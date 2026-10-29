# S-1 用のベースラインを MIDI ファイルに書き出す（Logic に読み込んで再生する用）
# 使い方: ~/.venvs/s1/bin/python bin/s1bassmid.py 出力.mid [--bpm 128] [--bars 8] [--key C] [--seed 1]
# ノートに加えて、FREQ（CC74）と RESO（CC71）の動きも入れる。チャンネルは S-1 の 12
import mido, argparse, random

ap = argparse.ArgumentParser()
ap.add_argument("out")
ap.add_argument("--bpm", type=float, default=128)
ap.add_argument("--bars", type=int, default=8)
ap.add_argument("--key", default="C")
ap.add_argument("--seed", type=int, default=1)
a = ap.parse_args()

KEYS = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}
root = 36 + KEYS[a.key]  # C2 基準
CH = 11                  # S-1 の受信チャンネル 12
TPB = 480                # 1拍の分解能
S16 = TPB // 4           # 16分音符

# 基本の1小節（ルートからの半音の差。None は休み）。マイナー・ペンタ寄り
BASE = [0, 0, 12, 0, None, 3, 0, 10, 0, -2, 10, -2, 0, None, 7, 3]
ACCENT = {0, 3, 7, 10, 14}
rnd = random.Random(a.seed)

events = []  # (tick, message)
for bar in range(a.bars):
    pat = list(BASE)
    # 4小節ごとの後半で、少しだけ音を変える（毎回同じだと単調なため）
    if bar % 4 == 3:
        for i in (2, 6, 10, 14):
            pat[i] = rnd.choice([12, 15, 10, 7])
    for i, d in enumerate(pat):
        t = (bar * 16 + i) * S16
        if d is None:
            continue
        n = root + d
        vel = 120 if i in ACCENT else 85
        events.append((t, mido.Message("note_on", channel=CH, note=n, velocity=vel)))
        events.append((t + int(S16 * 0.55), mido.Message("note_off", channel=CH, note=n, velocity=0)))

# つまみの動き: FREQ は全体で 30 → 100 へ開き、最後の小節で 40 に戻す。RESO は後半で上げる
total = a.bars * 16
for s in range(total):
    t = s * S16
    if s < total - 16:
        f = 30 + 70 * s / max(1, total - 16)
    else:
        f = 100 - 60 * (s - (total - 16)) / 16
    events.append((t, mido.Message("control_change", channel=CH, control=74, value=int(f))))
events.append((0, mido.Message("control_change", channel=CH, control=71, value=30)))
events.append((total // 2 * S16, mido.Message("control_change", channel=CH, control=71, value=70)))
events.append((total * S16, mido.Message("control_change", channel=CH, control=71, value=30)))

mid = mido.MidiFile(ticks_per_beat=TPB)
tr = mido.MidiTrack()
mid.tracks.append(tr)
tr.append(mido.MetaMessage("track_name", name="S-1 Bass", time=0))
tr.append(mido.MetaMessage("set_tempo", tempo=mido.bpm2tempo(a.bpm), time=0))
tr.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
# 同じ時刻ではノートオフ → CC → ノートオンの順にする
order = {"note_off": 0, "control_change": 1, "note_on": 2}
now = 0
for t, m in sorted(events, key=lambda e: (e[0], order[e[1].type])):
    tr.append(m.copy(time=t - now))
    now = t
tr.append(mido.MetaMessage("end_of_track", time=0))
mid.save(a.out)
print(f"{a.out}: {a.bars}小節 {a.bpm}BPM キー{a.key} ノート{sum(1 for _, m in events if m.type == 'note_on')}個")
