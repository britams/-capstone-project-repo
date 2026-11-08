# -*- coding: utf-8 -*-
"""uno_link.py — UNO 한 대와의 시리얼 연결 (서현 CAP-AI-45, 2026-11-08)

펌웨어 v0.2 (design/circuit/firmware/trap_motion, trap_doors)의 한 줄 텍스트 규칙을 그대로 쓴다.
  - 명령에는 먼저 'OK <명령어>' 또는 'ERR ...' 한 줄이 온다 (PING → 'OK PONG').
  - 그다음 일이 끝나면 'DONE ...' / 'EVT ...' / 비동기 'ERR HOME <축> <이유>' · 'ERR DOOR <문> WAIT' 가 따로 온다.
  - 그래서 command() 는 OK/ERR 한 줄만 받고, 나머지는 events 에 쌓아 wait_for() 로 기다린다.

port 는 readline() → bytes (없으면 b'') 와 write(bytes) 가 있는 객체 (pyserial Serial, 시험용 SimPort).
"""
import re
import time
from collections import deque

# 명령의 '답'이 아니라 일이 끝난 뒤 따로 오는 ERR (펌웨어 머리말 참고)
ASYNC_ERR = re.compile(r'^ERR (HOME \w+ (NOSWITCH|STUCK|STOPPED)|DOOR \w+ WAIT)$')
READY_RE = re.compile(r'^EVT READY (\w+) (\S+)')


class LinkError(RuntimeError):
    pass


class CommandError(LinkError):
    """UNO 가 명령을 거부했다 (ERR ...). reply 에 줄 전체."""

    def __init__(self, cmd, reply):
        super().__init__('%s -> %s' % (cmd, reply))
        self.cmd, self.reply = cmd, reply


class UnoLink:
    def __init__(self, port, label='?', clock=time.monotonic, history_max=2000):
        self.port, self.label, self.clock = port, label, clock
        self.name = None            # 'trap_motion' / 'trap_doors' (READY 에서)
        self.version = None
        self.events = deque(maxlen=400)
        self.history = deque(maxlen=history_max)    # (시각, '>>'|'<<', 줄) — 순서 시험용
        self.last_tx = clock()

    # ---- 저수준 ----
    def _readline(self):
        raw = self.port.readline()
        if not raw:
            return None
        s = raw.decode('utf-8', 'replace').strip() if isinstance(raw, bytes) else str(raw).strip()
        if not s:
            return None
        self.history.append((self.clock(), '<<', s))
        return s

    def send(self, cmd):
        self.history.append((self.clock(), '>>', cmd))
        self.port.write((cmd + '\n').encode('ascii'))
        self.last_tx = self.clock()

    def sent(self):
        """보낸 명령만 순서대로."""
        return [s for _, d, s in self.history if d == '>>']

    # ---- 시작 ----
    def wait_ready(self, timeout=6.0):
        """UNO 는 시리얼을 열면 재부팅한다 → EVT READY <이름> <버전>. 이름을 알면 True."""
        end = self.clock() + timeout
        while self.clock() < end:
            s = self._readline()
            if s is None:
                continue
            m = READY_RE.match(s)
            if m:
                self.name, self.version = m.group(1), m.group(2)
                return True
            self.events.append(s)
        return False

    def identify_by_status(self):
        """READY 를 놓쳤을 때(이미 켜져 있었음): STATUS 모양으로 이름을 가린다."""
        r = self.command('STATUS', timeout=2.0)
        if 'GATES=' in r:
            self.name = 'trap_doors'
        elif 'HOMED=' in r and 'PEN=' in r:
            self.name = 'trap_motion'
        return self.name

    # ---- 명령 ----
    def command(self, cmd, timeout=2.0):
        """명령을 보내고 OK 한 줄을 받는다. ERR 이면 CommandError. 그 사이 온 DONE/EVT 는 events 에."""
        self.send(cmd)
        word = cmd.split()[0]
        want = 'OK PONG' if word == 'PING' else 'OK ' + word
        end = self.clock() + timeout
        while self.clock() < end:
            s = self._readline()
            if s is None:
                continue
            if s.startswith(want):
                return s
            if s.startswith('OK '):
                continue                      # 다른 명령의 늦은 OK (예: 심장박동 PONG)
            if s.startswith('ERR') and not ASYNC_ERR.match(s):
                raise CommandError(cmd, s)
            self.events.append(s)
        raise LinkError('%s: 응답 없음 (%.1f s, %s)' % (cmd, timeout, self.label))

    def poll(self, prefixes, slice_s=0.05):
        """prefixes 중 하나로 시작하는 줄이 events 나 새 줄에 있으면 돌려주고, 없으면 None (slice_s 안에서)."""
        if isinstance(prefixes, str):
            prefixes = (prefixes,)
        for i, e in enumerate(self.events):
            if e.startswith(tuple(prefixes)):
                del self.events[i]
                return e
        end = self.clock() + slice_s
        while True:
            s = self._readline()
            if s is not None:
                if s.startswith(tuple(prefixes)):
                    return s
                if not s.startswith('OK '):
                    self.events.append(s)
            if self.clock() >= end:
                return None

    def wait_for(self, prefixes, timeout):
        end = self.clock() + timeout
        while self.clock() < end:
            s = self.poll(prefixes, min(0.05, max(0.0, end - self.clock())))
            if s:
                return s
        raise LinkError('%s 기다리다 시간 초과 (%.1f s, %s)' % (prefixes, timeout, self.label))

    def take(self, prefix):
        """events 에서 prefix 로 시작하는 줄을 모두 꺼냄 (기다리지 않음)."""
        out = [e for e in self.events if e.startswith(prefix)]
        for e in out:
            self.events.remove(e)
        return out

    def ping_if_idle(self, max_idle_s):
        """WATCHDOG 을 막으려면 명령이 5 s 안에 와야 한다 → 한가하면 PING (답은 나중에 PONG 으로 걸러짐)."""
        if self.clock() - self.last_tx >= max_idle_s:
            self.send('PING')
