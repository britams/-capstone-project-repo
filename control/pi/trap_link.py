"""trap_link.py — Pi(또는 PC) ↔ 아두이노 trap_controller 시리얼 연결 (CAP-AI-SJ-19)

명령 형식은 control/firmware/trap_controller/trap_controller.ino 맨 위 주석과 같다.

사용 (손으로 시험):
    pip install pyserial
    python trap_link.py COM3          # Windows (장치 관리자 → 포트에서 번호 확인)
    python trap_link.py /dev/ttyACM0  # Pi
    > PING
    > MOVE X 5
    > time X 10                       # X를 10 mm 움직이는 데 걸린 시간 → mm/s (J6 속도 측정)
    > quit

코드에서:
    link = TrapLink(serial.Serial('COM3', 115200, timeout=0.1))
    link.move('X', 5.0)               # 끝날 때까지 기다림
    mm, g = link.press(50, 30)        # 하중 50 g까지 바닥 올림
"""
import sys
import time


class TrapError(RuntimeError):
    pass


class TrapLink:
    def __init__(self, port, ready_timeout=3.0, log=None):
        """port: readline()/write() 가 있는 객체 (pyserial Serial, 시험용 가짜 포트)."""
        self.port = port
        self.log = log or (lambda s: None)
        self.events = []
        self._wait_ready(ready_timeout)

    # ---- 저수준 ----
    def _readline(self):
        raw = self.port.readline()
        if not raw:
            return None
        s = raw.decode('ascii', 'replace').strip() if isinstance(raw, bytes) else raw.strip()
        if s:
            self.log('<< ' + s)
        return s or None

    def _wait_ready(self, timeout):
        """아두이노는 시리얼을 열면 재부팅됨 → EVT READY를 기다리고, 안 오면 PING으로 확인."""
        end = time.time() + timeout
        while time.time() < end:
            s = self._readline()
            if s and s.startswith('EVT READY'):
                return
        self.command('PING')

    def command(self, cmd, timeout=2.0):
        """명령을 보내고 OK/ERR 한 줄을 받는다. 그 사이 온 EVT/DONE은 events에 쌓음."""
        self.log('>> ' + cmd)
        self.port.write((cmd + '\n').encode('ascii'))
        end = time.time() + timeout
        while time.time() < end:
            s = self._readline()
            if s is None:
                continue
            if s.startswith('OK'):
                return s
            if s.startswith('ERR'):
                raise TrapError(f'{cmd} → {s}')
            self.events.append(s)
        raise TrapError(f'{cmd} → 응답 없음 ({timeout}s)')

    def wait_for(self, prefix, timeout):
        """events 또는 새 줄에서 prefix로 시작하는 줄을 기다린다."""
        for i, e in enumerate(self.events):
            if e.startswith(prefix):
                return self.events.pop(i)
        end = time.time() + timeout
        while time.time() < end:
            s = self._readline()
            if s is None:
                continue
            if s.startswith(prefix):
                return s
            self.events.append(s)
        raise TrapError(f'{prefix} 기다리다 시간 초과 ({timeout}s)')

    # ---- 고수준 ----
    def move(self, axis, mm, wait=True, mm_per_s=1.8):
        self.command(f'MOVE {axis} {mm:.3f}')
        if not wait:
            return None
        st = self.status()
        dist = abs(mm - st.get(axis, 0.0)) if axis in st else 60.0
        s = self.wait_for(f'DONE MOVE {axis}', timeout=dist / mm_per_s + 60.0)
        return float(s.split()[-1])

    def press(self, grams, max_mm=None, timeout=60.0):
        self.command(f'PRESS {grams}' + (f' {max_mm}' if max_mm is not None else ''))
        s = self.wait_for('DONE PRESS', timeout=timeout).split()
        if s[2] == 'LIMIT':                       # DONE PRESS LIMIT <mm> <g>
            raise TrapError(f'하중 {grams} g에 닿기 전에 한계 {s[3]} mm 도달 (하중 {s[4]} g)')
        return float(s[2]), float(s[3])

    def door(self, name, state):
        self.command(f'DOOR {name} {state}')

    def pen(self, up):
        self.command('PEN UP' if up else 'PEN DOWN')

    def load(self):
        _, _, g, raw = self.command('LOAD').split()
        return float(g), int(raw)

    def status(self):
        s = self.command('STATUS').split()[2:]
        out = {}
        for kv in s:
            k, v = kv.split('=')
            try:
                out[k] = float(v)
            except ValueError:
                out[k] = v
        return out

    def stop(self):
        self.command('STOP')


def console(port_name):
    import serial  # pyserial
    link = TrapLink(serial.Serial(port_name, 115200, timeout=0.1), log=print)
    print('연결됨. 명령을 입력 (quit 끝, "time X 10" = X를 10 mm 움직인 시간 측정)')
    while True:
        try:
            cmd = input('> ').strip()
        except EOFError:
            break
        if not cmd:
            continue
        if cmd.lower() in ('quit', 'exit'):
            break
        parts = cmd.split()
        try:
            if parts[0].lower() == 'time' and len(parts) == 3:
                ax, d = parts[1].upper(), float(parts[2])
                start = link.status()[ax]
                t0 = time.time()
                link.move(ax, start + d)
                dt = time.time() - t0
                print(f'{ax} {d} mm: {dt:.2f} s → {abs(d) / dt:.2f} mm/s (명령 왕복 포함)')
            else:
                link.command(cmd.upper(), timeout=5.0)
                time.sleep(0.05)
                while link.events:
                    print(link.events.pop(0))
        except TrapError as e:
            print('!!', e)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    console(sys.argv[1])
