# -*- coding: utf-8 -*-
"""controller.py — Pi 쪽 순서: 켤 때 · 문 닫기 재시도 · 밤/낮 · 비상 정지 복귀 (서현 CAP-AI-45, 2026-11-08)

근거
  - 켤 때 순서: design/2026-11-06_펌웨어_변경요청_서현.md 3장 + design/control_sim/trap_sim.py boot()
      READY → WATCHDOG → SELFTEST → RAIL → 문 3개 닫기 → HOLD F 0 → PEN UP → HOME F·X·Y → 대기 자리 + PEN DOWN
  - 규칙 P1~P7: design/2026-11-08_펌웨어v0.2_제어규칙_검토_서현.md 4장 (웹 채팅 CAP-AI-42)
  - 응답 이름은 펌웨어 v0.2 (P7): DONE DOOR <문> CLOSED/OPEN, EVT DOOR <문> REOPEN n/BLOCKED, ERR DOOR <문> WAIT
판정·촬영·마킹(trap_sim process())은 카메라 코드가 필요해서 여기 없다 — 승준 비전 코드와 붙일 때 이 위에 얹는다.

이 코드가 스스로 정한 것 (AI 판단, 서현 위임 — 웹 채팅 검토 대상)
  A1. EVT RAIL 0 을 받으면 UNO 1 에 STOP (UNO 1 은 레일을 못 봄 — 모터 전원이 끊겨 걸음을 잃음)
  A2. 대기 자리 X = +10 mm (펌웨어 좌표) — trap_sim park X 65 (CAD 좌표, X 범위 37~73) 에서 55 를 뺌. 미검증
"""
import time
from dataclasses import dataclass, field

from uno_link import LinkError, CommandError

DOORS = ('IN', 'CAP', 'REL')
DOOR_BEAMS = {'IN': ('G2', 'G2b'), 'CAP': ('G3', 'G3b'), 'REL': ('G5', 'G5b')}


class TrapFault(RuntimeError):
    """운용을 멈추고 사람에게 알려야 하는 고장. code 는 짧은 이름 (예: DOOR_IN_STUCK)."""

    def __init__(self, code, detail=''):
        super().__init__(code + (': ' + detail if detail else ''))
        self.code = code


class RailLost(TrapFault):
    pass


@dataclass
class Config:
    watchdog_s: float = 5.0        # P5
    keepalive_s: float = 1.0       # 이만큼 한가하면 PING (watchdog_s 보다 충분히 작게)
    retest_wait_s: float = 10.0    # P2
    door_pause_s: float = 5.0      # P6 BLOCKED 뒤 쉬는 시간
    door_retries: int = 3          # P6 Pi 쪽 시도 수 (펌웨어 안 3번 × 3 = 9번)
    door_timeout_s: float = 30.0   # 문 하나 닫기 기다림 (3번 다시 열기 포함)
    home_timeout_s: float = 60.0   # Y 행정 58 + 4 mm ≈ 32 s + 물러남·다시 닿기
    move_timeout_s: float = 60.0
    rail_wait_s: float = 30.0      # 켤 때 RAIL 0 이면 이만큼 기다림
    park: dict = field(default_factory=lambda: {'X': 10.0, 'Y': -40.0})   # A2 — 미검증
    emit_off_at_night: bool = True


def parse_selftest(line):
    """'OK SELFTEST G1=OK G2b=FAIL(87) …' → {'G1': 'OK', 'G2b': 'FAIL(87)', …}"""
    out = {}
    for tok in line.split()[2:]:
        if '=' in tok:
            k, v = tok.split('=', 1)
            out[k] = v
    return out


def parse_status(line):
    out = {}
    for tok in line.split()[2:]:
        if '=' in tok:
            k, v = tok.split('=', 1)
            out[k] = v
    return out


class TrapController:
    def __init__(self, motion, doors, cfg=None, log=print, clock=time.monotonic, sleep=time.sleep):
        self.m, self.d = motion, doors
        self.cfg = cfg or Config()
        self.log, self.clock, self._sleep = log, clock, sleep
        self.rail = True
        self.rail_restored = False
        self.unusable = set()      # P2: 빔 고장으로 쓰지 않는 문
        self.notes = []            # 사람에게 알릴 것
        self.gate_listeners = []   # EVT GATE 줄을 받을 함수 (process.Ledger)

    # ---------------- 바탕 ----------------
    def notify(self, kind, **kw):
        self.notes.append(dict(kind=kind, **kw))
        self.log('NOTE %s %s' % (kind, kw if kw else ''))

    def keepalive(self):
        for lk in (self.m, self.d):
            lk.ping_if_idle(self.cfg.keepalive_s)

    def _scan_rail(self):
        for e in self.d.take('EVT GATE'):          # 순서대로 넘김 (장부는 빔 순서로 방향을 앎)
            for cb in self.gate_listeners:
                cb(e)
        for e in self.d.take('EVT RAIL'):
            if e == 'EVT RAIL 0' and self.rail:
                self.rail = False
                self.notify('rail_off')
                try:
                    self.m.command('STOP')          # A1
                except LinkError:
                    pass
            elif e == 'EVT RAIL 1' and not self.rail:
                self.rail = True
                self.rail_restored = True
                self.notify('rail_on')

    def _await(self, link, prefixes, timeout, rail_matters=True):
        """link 에서 prefixes 줄을 기다리며 심장박동·레일을 본다."""
        end = self.clock() + timeout
        while self.clock() < end:
            s = link.poll(prefixes, 0.03)
            if s:
                return s
            if link is not self.d:
                self.d.poll((), 0.0)               # 문 쪽 사건(레일)도 읽어 둠
            self._scan_rail()
            if rail_matters and not self.rail:
                raise RailLost('RAIL_OFF', 'waiting %s' % (prefixes,))
            self.keepalive()
        raise TrapFault('TIMEOUT', '%s %s (%.0f s)' % (link.label, prefixes, timeout))

    def idle(self, seconds):
        """쉬는 동안에도 심장박동·사건 읽기 (time.sleep 대신)."""
        end = self.clock() + seconds
        while self.clock() < end:
            self.m.poll((), 0.02)
            self.d.poll((), 0.02)
            self._scan_rail()
            self.keepalive()

    # ---------------- UNO 1 ----------------
    def pen(self, up):
        w = 'UP' if up else 'DOWN'
        self.m.command('PEN ' + w)
        self._await(self.m, 'DONE PEN ' + w, 5.0)

    def home(self, ax):
        self.m.command('HOME ' + ax)
        s = self._await(self.m, ('DONE HOME ' + ax, 'ERR HOME ' + ax), self.cfg.home_timeout_s)
        if s.startswith('ERR'):
            raise TrapFault('HOME_%s_%s' % (ax, s.split()[-1]), s)
        return int(s.split()[-1])

    def move(self, ax, mm):
        self.m.command('MOVE %s %.3f' % (ax, mm))
        s = self._await(self.m, ('DONE MOVE ' + ax, 'EVT SWITCH ' + ax), self.cfg.move_timeout_s)
        if s.startswith('EVT SWITCH'):
            raise TrapFault('LOST_STEPS_%s' % ax, s)     # 펌웨어 V5: 걸음 잃음 → 다시 HOME 필요
        return float(s.split()[-1])

    def move_xy_press(self, x, y, grams):
        """X·Y를 흉부 위로 보내면서 바닥을 PRESS (trap_sim press_mark — 세 축 같이). (F mm, g) 또는 한계면 None."""
        self.m.command('MOVE X %.3f' % x)
        self.m.command('MOVE Y %.3f' % y)
        self.m.command('PRESS %g' % grams)
        got = {}
        for p in ('DONE MOVE X', 'DONE MOVE Y', 'DONE PRESS'):
            got[p] = self._await(self.m, (p, 'EVT SWITCH'), self.cfg.move_timeout_s)
            if got[p].startswith('EVT SWITCH'):
                raise TrapFault('LOST_STEPS', got[p])
        t = got['DONE PRESS'].split()
        if t[2] == 'LIMIT':
            return None
        return float(t[2]), float(t[3])

    def move_xy(self, x, y):
        self.m.command('MOVE X %.3f' % x)
        self.m.command('MOVE Y %.3f' % y)
        for ax in ('X', 'Y'):
            s = self._await(self.m, ('DONE MOVE ' + ax, 'EVT SWITCH ' + ax), self.cfg.move_timeout_s)
            if s.startswith('EVT SWITCH'):
                raise TrapFault('LOST_STEPS_%s' % ax, s)

    def pump(self, ms):
        """급이 펌프를 ms 동안 (UNO 2 D6, CAP-AI-59). 끝나면 True, 레일 끊김 등으로 멈추면 False."""
        self.d.command('PUMP %d' % ms)
        s = self._await(self.d, ('DONE PUMP', 'EVT PUMP STOP'), ms / 1000.0 + 2.0, rail_matters=False)
        return s.startswith('DONE PUMP')

    def lights(self, top, bot):
        self.d.command('LIGHT TOP %d' % top)
        self.d.command('LIGHT BOT %d' % bot)

    def park(self):
        """대기 자리로 가서 펜을 캡 컵에 놓음 (trap_sim park(pen_down=True))."""
        for ax in ('X', 'Y'):
            self.m.command('MOVE %s %.3f' % (ax, self.cfg.park[ax]))
        for ax in ('X', 'Y'):
            s = self._await(self.m, ('DONE MOVE ' + ax, 'EVT SWITCH ' + ax), self.cfg.move_timeout_s)
            if s.startswith('EVT SWITCH'):
                raise TrapFault('LOST_STEPS_%s' % ax, s)
        self.pen(False)

    def home_all(self):
        self.m.command('HOLD F 0')
        self.pen(True)                     # 펌웨어 V4: X·Y 는 펜 UP 일 때만
        for ax in ('F', 'X', 'Y'):
            self.home(ax)

    # ---------------- UNO 2 ----------------
    def selftest(self):
        return parse_selftest(self.d.command('SELFTEST', timeout=3.0))

    def _bad_doors(self, rep):
        return [d for d, beams in DOOR_BEAMS.items() if any(rep.get(b) != 'OK' for b in beams)]

    def open_door(self, d):
        self.d.command('DOOR %s OPEN' % d)
        self._await(self.d, 'DONE DOOR %s OPEN' % d, 5.0)

    def close_door(self, d):
        """P6: 펌웨어가 3번 다시 열고 BLOCKED 를 주면 쉬었다가 다시 — Pi 쪽 최대 door_retries 번."""
        if d in self.unusable:
            raise TrapFault('DOOR_%s_UNUSABLE' % d, '자가 시험에서 빔 고장')
        for k in range(1, self.cfg.door_retries + 1):
            try:
                self.d.command('DOOR %s CLOSE' % d)
            except CommandError as e:
                if 'BEAMFAIL' in e.reply:
                    self.unusable.add(d)
                    raise TrapFault('DOOR_%s_UNUSABLE' % d, e.reply)
                if e.reply == 'ERR RAIL':
                    raise RailLost('RAIL_OFF', e.reply)
                raise
            s = self._await(self.d, ('DONE DOOR %s CLOSED' % d, 'EVT DOOR %s BLOCKED' % d, 'ERR DOOR %s WAIT' % d),
                            self.cfg.door_timeout_s)
            if s.startswith('DONE'):
                return k
            self.notify('door_not_closed', door=d, attempt=k, why=s)
            self.idle(self.cfg.door_pause_s)
        self.notify('door_stuck', door=d)
        raise TrapFault('DOOR_%s_STUCK' % d)

    # ---------------- 순서 ----------------
    def boot(self):
        """켤 때. 성공하면 보고(dict), 시작하면 안 되면 TrapFault."""
        c = self.cfg
        for lk in (self.m, self.d):
            lk.command('WATCHDOG %g' % c.watchdog_s)            # P5
        rep = self.selftest()
        if rep.get('G1') != 'OK':                               # P1: 진입 신호가 고장이면 시작 안 함
            self.notify('g1_fail', value=rep.get('G1'))
            raise TrapFault('G1_SELFTEST_FAIL', rep.get('G1', '?'))
        bad = self._bad_doors(rep)
        if bad:                                                 # P2: 빔 사이에 말벌이 있었을 수 있음 → 한 번 더
            self.notify('beam_fail_retest', doors=bad, report=rep)
            self.idle(c.retest_wait_s)
            rep = self.selftest()
            if rep.get('G1') != 'OK':
                raise TrapFault('G1_SELFTEST_FAIL', rep.get('G1', '?'))
            for d in self._bad_doors(rep):
                self.unusable.add(d)
                self.notify('door_unusable', door=d, report=rep)
        r = self.d.command('RAIL')                              # 비상 정지가 눌려 있으면 풀릴 때까지
        if r.endswith(' 0'):
            self.rail = False
            self.notify('rail_off_at_boot')
            try:
                self._await(self.d, 'EVT RAIL 1', c.rail_wait_s, rail_matters=False)
            except TrapFault:
                raise TrapFault('RAIL_OFF', '켤 때 비상 정지가 눌려 있음')
            self.rail = True
        for d in DOORS:                                          # trap_sim: 원점 찾는 동안 못 들어오게 먼저 닫음
            if d not in self.unusable:
                self.close_door(d)
        self.home_all()
        self.park()
        return dict(selftest=rep, unusable=sorted(self.unusable))

    def night_mode(self):
        """P3: REL CLOSE → IN·CAP OPEN → 조명 0 → (원하면) EMIT 0. 앞에 펜 들기·바닥 내리기 (daynight.night_mode)."""
        self.pen(True)
        self.move('F', 0.0)
        self.close_door('REL')
        self.open_door('IN')
        self.open_door('CAP')
        self.d.command('LIGHT TOP 0')
        self.d.command('LIGHT BOT 0')
        if self.cfg.emit_off_at_night:
            self.d.command('EMIT 0')

    def day_mode(self):
        """아침: 송신부터 켬 (EMIT 0 이면 닫기가 거부됨) → CAP·REL 닫고 IN 엶."""
        self.d.command('EMIT 1')
        self.close_door('CAP')
        self.close_door('REL')
        self.open_door('IN')

    def recover_after_rail(self):
        """P4: EVT RAIL 1 → PEN UP → HOME F·X·Y → 문은 OPEN 부터 → 대기 자리."""
        self.rail_restored = False
        self.home_all()
        for d in DOORS:
            self.open_door(d)
        self.park()

    def service(self, auto_recover=True):
        """주 루프에서 자주 부름: 사건 읽기, 심장박동, 레일 복귀."""
        self.m.poll((), 0.01)
        self.d.poll((), 0.01)
        self._scan_rail()
        self.keepalive()
        if auto_recover and self.rail_restored and self.rail:
            self.recover_after_rail()
            return 'recovered'
        return None
