import subprocess, sys, threading, queue, time
sys.path.insert(0, '../../pi')
from trap_link import TrapLink, TrapError
p = subprocess.Popen(['./sim2'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, bufsize=0)
q = queue.Queue()
threading.Thread(target=lambda: [q.put(l) for l in iter(p.stdout.readline, b'')], daemon=True).start()
class Port:
    def readline(self):
        try: return q.get(timeout=0.1)
        except queue.Empty: return b''
    def write(self, b): p.stdin.write(b); p.stdin.flush()
link = TrapLink(Port())
print('status', link.status())
t=time.time(); print('move X ->', link.move('X', 2.0), f'{time.time()-t:.2f}s (~{2/(time.time()-t):.2f} mm/s)')
link.command('CAL 0.1'); link.command('TARE')
print('press ->', link.press(50, 10))
try: link.command('MOVE X 99')
except TrapError as e: print('expected error:', e)
link.door('IN', 'CLOSE'); link.pen(False); print('status', link.status())
p.stdin.close(); p.wait(timeout=5)
