# midispy.py の記録を、同じ間隔で S-1 に送り直す（Logic を通さずに再現を試すため）
# 使い方: ~/.venvs/s1/bin/python bin/midireplay.py 記録.log [--only note,control_change,...] [--skip 種類,...] [--from 秒] [--to 秒] [--dry]
import mido, time, sys, argparse
ap = argparse.ArgumentParser()
ap.add_argument("log"); ap.add_argument("--only"); ap.add_argument("--skip")
ap.add_argument("--from", dest="t_from", type=float, default=0); ap.add_argument("--to", dest="t_to", type=float, default=1e9)
ap.add_argument("--port", default="S-1 MIDI IN"); ap.add_argument("--dry", action="store_true")
a = ap.parse_args()
only = set(a.only.split(",")) if a.only else None
skip = set(a.skip.split(",")) if a.skip else set()
msgs = []
for line in open(a.log):
    if "|" not in line: continue
    left, hx = line.rsplit("|", 1)
    t = float(left.split()[0])
    if not (a.t_from <= t <= a.t_to): continue
    m = mido.Message.from_hex(hx.strip())
    kind = "note" if m.type in ("note_on", "note_off") else m.type
    if (only and kind not in only) or kind in skip: continue
    msgs.append((t, m))
counts = {}
for _, m in msgs: counts[m.type] = counts.get(m.type, 0) + 1
print(f"{len(msgs)} 件:", counts)
if a.dry or not msgs: sys.exit()
with mido.open_output(a.port) as o:
    start, t_first = time.time(), msgs[0][0]
    for t, m in msgs:
        d = (t - t_first) - (time.time() - start)
        if d > 0: time.sleep(d)
        o.send(m)
