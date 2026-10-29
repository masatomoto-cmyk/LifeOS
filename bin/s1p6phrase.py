# P-6 のベースに合わせて、S-1 のアシッドのフレーズを MIDI ファイルに書き出す
# 使い方: ~/.venvs/s1/bin/python bin/s1p6phrase.py P-6ベース.mid 出力.mid
# - P-6 ベースの各小節のいちばん低い音を「その小節のコードの根音」とみなし、S-1 のフレーズをそこへ移す
# - ベースが鳴っていない小節は S-1 も休む
# - 区切り（SECTIONS）ごとに、リフの種類と FREQ（CC74）・RESO（CC71）の動きを変える
# - S-1 は P-6 ベースより上の C3〜C4 あたりで弾く。チャンネルは S-1 の 12
import mido, sys

src, out = sys.argv[1], sys.argv[2]
CH = 11

bass = mido.MidiFile(src)
TPB = bass.ticks_per_beat
BAR, S16 = TPB * 4, TPB // 4
tempo, notes = mido.bpm2tempo(128), []
for tr in bass.tracks:
    t = 0
    for m in tr:
        t += m.time
        if m.type == "set_tempo":
            tempo = m.tempo
        elif m.type == "note_on" and m.velocity > 0:
            notes.append((t, m.note))
nbars = max(t for t, _ in notes) // BAR + 1
roots = [min((n for t, n in notes if b * BAR <= t < (b + 1) * BAR), default=None) for b in range(nbars)]

# リフ（16分×16。数字は根音からの半音、None は休み、"+" は前の音をのばす）
RIFF = {
    "pulse": [0, None, 0, None, 0, None, 0, None, 0, None, 0, None, 0, None, 0, None],
    "sparse": [0, None, None, None, None, None, 12, None, None, None, 0, None, None, None, None, None],
    "A": [0, 0, 12, 0, None, 7, 0, 10, 0, None, 12, 0, 3, None, 7, 0],
    "B": [0, 12, 0, 15, 0, 7, 12, None, 0, 10, 12, 0, 19, 12, 7, 3],
    "hold": [0, "+", "+", "+", "+", "+", "+", "+", 7, "+", "+", "+", 12, "+", "+", "+"],
}
ACCENT = {0, 3, 6, 10, 13}

# (開始小節, 終了小節, リフ, FREQ の始め, FREQ の終わり, RESO) ※小節は1から
SECTIONS = [
    (9, 16, "pulse", 25, 45, 40),     # ベースと一緒に入る。小さく刻む
    (17, 32, "A", 40, 80, 60),        # 本体。だんだん開く
    (33, 40, "hold", 30, 30, 50),     # ベースが C だけの所。のばして休ませる
    (41, 56, "B", 50, 95, 80),        # 2回目。音域を広げてクセを強く
    (57, 64, "sparse", 35, 35, 50),   # ドラムが引く所
    (65, 72, "A", 30, 70, 60),        # もう一度盛り上げる準備
    (73, 88, "B", 60, 100, 85),       # 3回目
    (89, 96, "B", 90, 110, 100),      # いちばん盛り上がる所（ビヨビヨ最大）
    (97, 112, "A", 70, 50, 70),       # 少しずつ落とす
    (113, 120, "pulse", 50, 30, 50),  # 終わりに向かって閉じる
]

def chord_shift(root, d):
    # A♭・B♭ の小節（根音が C 以外）は短3度を長3度にする（A♭→C、B♭→D）
    if root % 12 != 0 and d % 12 == 3:
        return d + 1
    return d

ev = []
def add(t, m):
    ev.append((t, m))

# 1小節目の頭に初期値を置く（Logic は読み込むとき頭の空白を詰めてしまうため、位置がずれないようにする）
add(0, mido.Message("control_change", channel=CH, control=74, value=SECTIONS[0][3]))
add(0, mido.Message("control_change", channel=CH, control=71, value=SECTIONS[0][5]))

for s, e, riff, f0, f1, reso in SECTIONS:
    add((s - 1) * BAR, mido.Message("control_change", channel=CH, control=71, value=reso))
    length = (e - s + 1) * 16
    for k in range(length):
        bar = s - 1 + k // 16
        if bar >= nbars:
            break
        t = bar * BAR + (k % 16) * S16
        add(t, mido.Message("control_change", channel=CH, control=74, value=int(f0 + (f1 - f0) * k / max(1, length - 1))))
        root = roots[bar]
        if root is None:
            continue
        pat = RIFF[riff]
        d = pat[k % 16]
        if d is None or d == "+":
            continue
        # のばす長さ: 次の音（"+" 以外）までの 16 分の数
        span = 1
        while (k % 16) + span < 16 and pat[(k % 16) + span] == "+":
            span += 1
        base = 48 + (root % 12) - (12 if root % 12 > 7 else 0)  # C3 付近に置く（A♭・B♭ は下の A♭2・B♭2）
        n = base + chord_shift(root, d)
        vel = 120 if (k % 16) in ACCENT else 88
        gate = S16 * span - S16 // 4 if span > 1 else int(S16 * 0.55)
        add(t, mido.Message("note_on", channel=CH, note=n, velocity=vel))
        add(t + gate, mido.Message("note_off", channel=CH, note=n, velocity=0))

# 最後は太いベースの値に戻す
end = SECTIONS[-1][1] * BAR
add(end, mido.Message("control_change", channel=CH, control=74, value=40))
add(end, mido.Message("control_change", channel=CH, control=71, value=30))

mid = mido.MidiFile(ticks_per_beat=TPB)
tr = mido.MidiTrack()
mid.tracks.append(tr)
tr.append(mido.MetaMessage("track_name", name="S-1 with P-6", time=0))
tr.append(mido.MetaMessage("set_tempo", tempo=tempo, time=0))
tr.append(mido.MetaMessage("time_signature", numerator=4, denominator=4, time=0))
order = {"note_off": 0, "control_change": 1, "note_on": 2}
now = 0
for t, m in sorted(ev, key=lambda x: (x[0], order[x[1].type])):
    tr.append(m.copy(time=t - now))
    now = t
tr.append(mido.MetaMessage("end_of_track", time=0))
mid.save(out)
print(f"{out}: {nbars}小節 {round(mido.tempo2bpm(tempo))}BPM ノート{sum(1 for _, m in ev if m.type == 'note_on')}個")
