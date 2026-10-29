#!/usr/bin/env python3
"""Roland S-1 を USB MIDI で操作する道具。

CC 番号は Roland 公式マニュアル（S-1 v1.02 の Control change list）と
「Roland S-1 Control」プラグイン（Dennis Schauw 作）の中身で照らし合わせたもの。

使い方の例:
  s1 ports                      MIDI ポートの一覧
  s1 list                       操作できるパラメータの一覧
  s1 set cutoff=40 reso=90      つまみを動かす（名前=値、複数可）
  s1 cc 74 40                   CC 番号で直接送る
  s1 note C4 --dur 1            1音鳴らす
  s1 play "C4 E4 G4 C5" --dur 0.25 --gap 0.05
  s1 chord "C4 E4 G4" --dur 1   和音（Poly モードで）
  s1 pc 3                       パターン（音色）を 4 番に切り替え（0 始まり）
  s1 panic                      鳴りっぱなしを止める
  s1 test                       音を鳴らしながら S-1 の USB 音声を録音し、音量と音程を測る
"""
import argparse
import os
import re
import subprocess
import sys
import tempfile
import time

import mido

PORT_HINT = "S-1"

# 名前: (CC 番号, 説明, 値の範囲)
PARAMS = {
    "modwheel":     (1,   "モジュレーションホイール", "0-127"),
    "lforate":      (3,   "LFO RATE", "0-127"),
    "portatime":    (5,   "ポルタメント時間", "0-127"),
    "pan":          (10,  "パン（64=中央）", "0-127"),
    "expression":   (11,  "エクスプレッション（音量）", "0-127"),
    "lfowave":      (12,  "LFO 波形", "0-5（三角/のこぎり上/下/矩形/S&H/ランダム）"),
    "osclfo":       (13,  "OSC への LFO（ビブラート）", "0-127"),
    "range":        (14,  "OSC RANGE（音域。1 上げると 1 オクターブ上）", "0-5（3=標準 8'）"),
    "pw":           (15,  "パルス幅", "0-127"),
    "pwmsource":    (16,  "PWM ソース", "0=手動 1=LFO 2=エンベロープ"),
    "lfodepth":     (17,  "LFO モジュレーション深さ", "0-127"),
    "oscbend":      (18,  "OSC ベンド感度", "0-127"),
    "square":       (19,  "矩形波の音量", "0-127"),
    "saw":          (20,  "のこぎり波の音量", "0-127"),
    "sub":          (21,  "サブオシレーター音量", "0-127"),
    "subtype":      (22,  "サブ OSC の種類", "0=-2oct非対称 1=-2oct 2=-1oct"),
    "noise":        (23,  "ノイズ音量", "0-127"),
    "filterenv":    (24,  "フィルターへのエンベロープ量", "0-127"),
    "filterlfo":    (25,  "フィルターへの LFO 量", "0-127"),
    "keyfollow":    (26,  "フィルターのキーボード追従", "0-127"),
    "filterbend":   (27,  "フィルターのベンド感度", "0-127"),
    "ampmode":      (28,  "アンプのモード", "0=ゲート 127=エンベロープ"),
    "envtrig":      (29,  "エンベロープのトリガー", "0=Gate 1=Trig1 2=Trig2"),
    "sustain":      (30,  "ENV サスティン", "0-127"),
    "portamode":    (31,  "ポルタメントのモード", "0=Off 1=On 2=Auto"),
    "damper":       (64,  "ダンパー（ホールド）", "0/127"),
    "portamento":   (65,  "ポルタメント スイッチ", "0/127"),
    "reso":         (71,  "フィルター レゾナンス", "0-127"),
    "release":      (72,  "ENV リリース", "0-127"),
    "attack":       (73,  "ENV アタック", "0-127"),
    "cutoff":       (74,  "フィルター カットオフ", "0-127"),
    "decay":        (75,  "ENV ディケイ", "0-127"),
    "finetune":     (76,  "ファインチューン（64=0）", "0-127"),
    "transpose":    (77,  "トランスポーズ（64=0、±半音）", "0-127"),
    "noisemode":    (78,  "ノイズの種類", "0=White 127=Pink"),
    "lfomode":      (79,  "LFO モード", "0=Normal 127=Fast"),
    "polymode":     (80,  "発音モード", "0=Mono 1=Uni 2=Poly 3=Chord"),
    "chord2":       (81,  "コード 2声目 ON/OFF", "0/127"),
    "chord3":       (82,  "コード 3声目 ON/OFF", "0/127"),
    "chord4":       (83,  "コード 4声目 ON/OFF", "0/127"),
    "chord2key":    (85,  "コード 2声目の音程（12=0、±12半音）", "0-24"),
    "chord3key":    (86,  "コード 3声目の音程", "0-24"),
    "chord4key":    (87,  "コード 4声目の音程", "0-24"),
    "reverbtime":   (89,  "リバーブ時間", "0-127"),
    "delaytime":    (90,  "ディレイ時間", "0-127"),
    "reverb":       (91,  "リバーブ量", "0-127"),
    "delay":        (92,  "ディレイ量", "0-127"),
    "chorus":       (93,  "コーラス", "0=Off 1-4"),
    "drawmult":     (102, "OSC DRAW MULTIPLY", "0-127"),
    "chopover":     (103, "OSC CHOP OVERTONE", "0-127"),
    "chopcomb":     (104, "OSC CHOP COMB", "0-127"),
    "lfokeytrig":   (105, "LFO キートリガー", "0/127"),
    "lfosync":      (106, "LFO テンポ同期", "0/127"),
    "drawsw":       (107, "OSC DRAW スイッチ", "0=Off 1=Step 2=Slope"),
}

NOTE_RE = re.compile(r"^([A-Ga-g])([#b]?)(-?\d)$")
NOTE_BASE = {"C": 0, "D": 2, "E": 4, "F": 5, "G": 7, "A": 9, "B": 11}


def note_num(s):
    """'C4' → 60、数字ならそのまま。"""
    if s.isdigit():
        return int(s)
    m = NOTE_RE.match(s)
    if not m:
        sys.exit(f"音名が読めません: {s}（例: C4, F#3, Bb2, 60）")
    n = NOTE_BASE[m.group(1).upper()] + {"#": 1, "b": -1, "": 0}[m.group(2)]
    return (int(m.group(3)) + 1) * 12 + n


def find_port(names, hint):
    for n in names:
        if hint in n:
            return n
    sys.exit(f"'{hint}' を含む MIDI ポートがありません。S-1 の USB 接続と電源を確認してください。\n今あるポート: {names}")


def open_out(args):
    return mido.open_output(find_port(mido.get_output_names(), args.port))


def ch(args):
    return args.channel - 1


def send_cc(out, args, cc, val):
    if not 0 <= val <= 127:
        sys.exit(f"値は 0〜127 です: {val}")
    out.send(mido.Message("control_change", channel=ch(args), control=cc, value=val))


def resolve(name):
    if name.isdigit():
        return int(name)
    key = name.lower()
    if key not in PARAMS:
        sys.exit(f"知らないパラメータ名です: {name}（s1 list で一覧）")
    return PARAMS[key][0]


def play_notes(out, args, notes, dur, gap=0.0, together=False):
    msgs = [note_num(n) for n in notes]
    try:
        if together:
            for n in msgs:
                out.send(mido.Message("note_on", channel=ch(args), note=n, velocity=args.vel))
            time.sleep(dur)
            for n in msgs:
                out.send(mido.Message("note_off", channel=ch(args), note=n))
        else:
            for n in msgs:
                out.send(mido.Message("note_on", channel=ch(args), note=n, velocity=args.vel))
                time.sleep(dur)
                out.send(mido.Message("note_off", channel=ch(args), note=n))
                time.sleep(gap)
    except KeyboardInterrupt:
        panic(out, args)
        raise


def panic(out, args):
    """全チャンネルでペダルを離し、全音を止める（チャンネル違いの鳴りっぱなしにも効くように）。
    S-1 は CC123/120 を無視するので、128 音すべてにノートオフも送る（2026-10-29 実測）。"""
    for c in range(16):
        out.send(mido.Message("control_change", channel=c, control=64, value=0))
        out.send(mido.Message("control_change", channel=c, control=123, value=0))
        out.send(mido.Message("control_change", channel=c, control=120, value=0))
        for n in range(128):
            out.send(mido.Message("note_off", channel=c, note=n, velocity=0))


def audio_device_index(hint):
    """ffmpeg（avfoundation）の音声入力から S-1 の番号を探す。"""
    r = subprocess.run(["ffmpeg", "-hide_banner", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
                       capture_output=True, text=True)
    audio = False
    for line in r.stderr.splitlines():
        if "audio devices" in line:
            audio = True
            continue
        m = re.search(r"\[(\d+)\] (.+)$", line)
        if audio and m and hint in m.group(2):
            return m.group(1)
    return None


def measure(wav):
    """WAV の最大音量（dBFS）と、ゼロ交差から求めたおおよその音程（Hz）。"""
    import array
    import math
    import wave
    with wave.open(wav) as w:
        nch, rate = w.getnchannels(), w.getframerate()
        data = array.array("h", w.readframes(w.getnframes()))
    mono = data[::nch]
    peak = max((abs(x) for x in mono), default=0)
    db = 20 * math.log10(peak / 32768) if peak else float("-inf")
    if peak == 0:
        return db, None
    # 最大音量のあたり 0.1 秒の自己相関で基本周波数を求める（30〜2000 Hz）
    i = max(range(len(mono)), key=lambda k: abs(mono[k]))
    n = int(rate * 0.1)
    start = max(0, min(i - n // 2, len(mono) - n))
    seg = [x / 32768 for x in mono[start:start + n]]
    if len(seg) < n:
        return db, None
    lags = range(int(rate / 2000), int(rate / 30))
    corr = [sum(seg[k] * seg[k + lag] for k in range(n - lag)) / (n - lag) for lag in lags]
    best = max(corr)
    # 最初に最大値の 90% を超える山を採る（倍音の取り違えを防ぐ）
    lag = next(l for l, c in zip(lags, corr) if c >= 0.9 * best)
    return db, rate / lag


def record_while(args, seconds, action):
    idx = audio_device_index(args.audio)
    if idx is None:
        sys.exit("S-1 の USB 音声入力が見つかりません（ffmpeg -f avfoundation -list_devices true -i '' で確認）")
    wav = args.out or tempfile.mktemp(suffix=".wav", prefix="s1_")
    rec = subprocess.Popen(["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-f", "avfoundation",
                            "-i", f":{idx}", "-t", str(seconds), "-ac", "2", "-ar", "44100", wav])
    time.sleep(0.8)  # 録音が始まるのを待つ
    action()
    rec.wait()
    return wav


def main():
    p = argparse.ArgumentParser(description="Roland S-1 を USB MIDI で操作する")
    p.add_argument("--port", default=PORT_HINT, help="MIDI ポート名の一部（既定: S-1）")
    p.add_argument("--channel", type=int, default=int(os.environ.get("S1_CHANNEL", 12)),
                   help="MIDI チャンネル 1-16（既定: 12。本体の MENU → CH と合わせる。環境変数 S1_CHANNEL でも変更可）")
    p.add_argument("--vel", type=int, default=100, help="ベロシティ（既定: 100）")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("ports")
    sub.add_parser("list")
    s = sub.add_parser("set"); s.add_argument("pairs", nargs="+")
    s = sub.add_parser("cc"); s.add_argument("num"); s.add_argument("val", type=int)
    s = sub.add_parser("note"); s.add_argument("note"); s.add_argument("--dur", type=float, default=0.5)
    s = sub.add_parser("play"); s.add_argument("notes"); s.add_argument("--dur", type=float, default=0.25)
    s.add_argument("--gap", type=float, default=0.0)
    s = sub.add_parser("chord"); s.add_argument("notes"); s.add_argument("--dur", type=float, default=1.0)
    s = sub.add_parser("pc"); s.add_argument("num", type=int)
    s = sub.add_parser("bend"); s.add_argument("val", type=int, help="-8192〜8191（0=中央）")
    sub.add_parser("panic")
    s = sub.add_parser("test"); s.add_argument("--note", default="A3"); s.add_argument("--audio", default="S-1")
    s.add_argument("--out", help="録音を残す WAV のパス")
    args = p.parse_args()

    if args.cmd == "ports":
        print("出力:", mido.get_output_names())
        print("入力:", mido.get_input_names())
        return
    if args.cmd == "list":
        for name, (cc, desc, rng) in PARAMS.items():
            print(f"{name:12s} CC{cc:<4d} {desc}（{rng}）")
        return

    with open_out(args) as out:
        if args.cmd == "set":
            for pair in args.pairs:
                name, _, val = pair.partition("=")
                send_cc(out, args, resolve(name), int(val))
        elif args.cmd == "cc":
            send_cc(out, args, resolve(args.num), args.val)
        elif args.cmd == "note":
            play_notes(out, args, [args.note], args.dur)
        elif args.cmd == "play":
            play_notes(out, args, args.notes.split(), args.dur, args.gap)
        elif args.cmd == "chord":
            play_notes(out, args, args.notes.split(), args.dur, together=True)
        elif args.cmd == "pc":
            out.send(mido.Message("program_change", channel=ch(args), program=args.num))
        elif args.cmd == "bend":
            out.send(mido.Message("pitchwheel", channel=ch(args), pitch=args.val))
        elif args.cmd == "panic":
            panic(out, args)
        elif args.cmd == "test":
            wav = record_while(args, 2.5, lambda: play_notes(out, args, [args.note], 1.0))
            db, hz = measure(wav)
            print(f"録音: {wav}")
            print(f"最大音量: {db:.1f} dBFS" + ("（無音）" if db == float('-inf') or db < -60 else ""))
            if hz:
                print(f"おおよその音程: {hz:.1f} Hz")
            if not args.out:
                os.remove(wav)


if __name__ == "__main__":
    main()
