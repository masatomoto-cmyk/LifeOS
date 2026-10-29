# S-1 で短いアシッド風ベースラインを弾く（つまみを動かしながら）
# 使い方: ~/.venvs/s1/bin/python bin/s1jam.py [--bpm 120] [--bars 4]
import mido, time, argparse, math

ap = argparse.ArgumentParser()
ap.add_argument("--bpm", type=float, default=120)
ap.add_argument("--bars", type=int, default=4)
a = ap.parse_args()

CH = 11  # S-1 の受信チャンネル 12
step = 60 / a.bpm / 4  # 16分音符の長さ
# Cマイナーのフレーズ（None は休み）。1小節 = 16 ステップ
PATTERN = [36, 36, 48, 36, None, 39, 36, 46,
           36, 34, 46, 34, 36, None, 43, 39]
ACCENT = {0, 3, 7, 10, 14}

with mido.open_output("S-1 MIDI IN") as o:
    cc = lambda n, v: o.send(mido.Message("control_change", channel=CH, control=n, value=int(v)))
    cc(71, 30)  # RESO
    total = 16 * a.bars
    t0 = time.time()
    for i in range(total):
        # FREQ: 30 → 100 へ開き、最後の小節で閉じる
        x = i / (total - 16) if i < total - 16 else 1 - (i - (total - 16)) / 16
        cc(74, 30 + 70 * min(1, x))
        if i == total // 2:
            cc(71, 70)  # 後半は RESO を上げてクセを出す
        n = PATTERN[i % 16]
        if n is not None:
            # 最後の小節は1オクターブ上に飛ぶ音を混ぜる
            if i >= total - 16 and i % 4 == 2:
                n += 12
            o.send(mido.Message("note_on", channel=CH, note=n, velocity=120 if i % 16 in ACCENT else 85))
            time.sleep(step * 0.55)
            o.send(mido.Message("note_off", channel=CH, note=n))
        d = t0 + (i + 1) * step - time.time()
        if d > 0:
            time.sleep(d)
    # 元の音色（太いベース）に戻す
    cc(74, 40)
    cc(71, 30)
