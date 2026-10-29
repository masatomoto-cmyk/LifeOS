# 仮の MIDI 出口「S-1 Spy」を作り、届いたメッセージを時刻つきで記録する
# 使い方: ~/.venvs/s1/bin/python bin/midispy.py 記録先.log（Logic の送り先を S-1 Spy にして使う）
import mido, time, sys
log = open(sys.argv[1], "a", buffering=1)
t0 = time.time()
with mido.open_input("S-1 Spy", virtual=True) as inp:
    log.write("ready\n")
    for m in inp:
        log.write(f"{time.time()-t0:8.3f} {m}\n")
