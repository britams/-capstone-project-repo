# -*- coding: utf-8 -*-
"""test_pi_link.py — pi_link 를 실제 펌웨어 로직(sim --serve, 5배속)에 붙여 시험 (서현 CAP-AI-45)

실행:  관련코딩저장/sim/run_all.ps1 로 exe 를 만든 뒤
       python 관련코딩저장/pi_link/test_pi_link.py           (전부, 약 1분)
       python 관련코딩저장/pi_link/test_pi_link.py boot      (하나만)
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from sim_port import SimPort            # noqa: E402
from ports import identify              # noqa: E402
from controller import TrapController, Config, TrapFault, parse_status   # noqa: E402

SPEED = 5.0
PASS, FAIL = [0], [0]


def check(cond, msg):
    (PASS if cond else FAIL)[0] += 1
    print('  [%s] %s' % ('PASS' if cond else 'FAIL', msg))


def fast_cfg(**kw):
    # 5배속: Pi 쪽 시간(벽시계)을 1/5 로 → 펌웨어 시간으로는 원래 값
    c = Config(keepalive_s=0.4, retest_wait_s=10.0 / SPEED, door_pause_s=5.0 / SPEED)
    for k, v in kw.items():
        setattr(c, k, v)
    return c


class Rig:
    def __init__(self, motion_args=(), doors_args=(), cfg=None, swap=True):
        self.pm = SimPort('sim_motion.exe', *motion_args, speed=SPEED)
        self.pd = SimPort('sim_doors.exe', *doors_args, speed=SPEED)
        ports = [('COM_B', self.pd), ('COM_A', self.pm)] if swap else [('COM_A', self.pm), ('COM_B', self.pd)]
        self.links = identify(ports, ready_timeout=3.0)
        self.m, self.d = self.links['trap_motion'], self.links['trap_doors']
        self.ctl = TrapController(self.m, self.d, cfg or fast_cfg(), log=lambda s: None)

    def sent_d(self):
        return self.d.sent()

    def sent_m(self):
        return self.m.sent()

    def close(self):
        self.pm.close()
        self.pd.close()


def order_ok(seq, items):
    """items 가 seq 안에서 이 순서로 (앞부분 일치) 나오나."""
    i = 0
    for s in seq:
        if i < len(items) and s.startswith(items[i]):
            i += 1
    return i == len(items)


# ------------------------------------------------------------------
def t_boot():
    print('[boot] 정상 켜기: 포트 순서를 바꿔 넘겨도 READY 이름으로 가림, 순서 SELFTEST → RAIL → 문 닫기 → HOME F·X·Y → 대기 자리')
    r = Rig()
    try:
        check(r.m.label == 'COM_A' and r.d.label == 'COM_B', 'trap_motion=COM_A, trap_doors=COM_B (넘긴 순서와 반대여도)')
        t0 = time.time()
        rep = r.ctl.boot()
        print('      켜기 %.1f s (벽시계, 5배속)' % (time.time() - t0))
        check(rep['unusable'] == [], '쓰지 못하는 문 없음')
        d = [s for s in r.sent_d() if s != 'PING']
        m = [s for s in r.sent_m() if s != 'PING']
        check(order_ok(d, ['WATCHDOG 5', 'SELFTEST', 'RAIL', 'DOOR IN CLOSE', 'DOOR CAP CLOSE', 'DOOR REL CLOSE']), 'UNO 2 순서: WATCHDOG → SELFTEST → RAIL → 문 3개 닫기')
        check(order_ok(m, ['WATCHDOG 5', 'HOLD F 0', 'PEN UP', 'HOME F', 'HOME X', 'HOME Y', 'MOVE X', 'MOVE Y', 'PEN DOWN']), 'UNO 1 순서: WATCHDOG → HOLD F 0 → PEN UP → HOME F·X·Y → 대기 자리 → PEN DOWN')
        # 문 닫기가 HOME 보다 먼저였나 (두 UNO 사이 순서 — 시각으로)
        t_close = max(t for t, dr, s in r.d.history if dr == '>>' and s == 'DOOR REL CLOSE')
        t_home = min(t for t, dr, s in r.m.history if dr == '>>' and s == 'HOME F')
        check(t_close < t_home, '문 3개를 닫은 뒤 HOME 시작')
        st = parse_status(r.m.command('STATUS'))
        check(st.get('HOMED') == 'FXY' and st.get('PEN') == 'DOWN', 'UNO 1: HOMED=FXY, PEN=DOWN (캡 컵)')
        check(abs(float(st['X']) - 10.0) < 0.01 and abs(float(st['Y']) + 40.0) < 0.01, '대기 자리 X 10, Y −40')
        sd = parse_status(r.d.command('STATUS'))
        check(sd.get('IN') == sd.get('CAP') == sd.get('REL') == 'CLOSED', 'UNO 2: 문 3개 CLOSED')
        # 심장박동: 오래 쉬어도 WATCHDOG 이 안 터짐
        r.ctl.idle(2.0)          # 펌웨어 시간 10 s > WATCHDOG 5 s
        ev = list(r.m.events) + list(r.d.events)
        check(not any('WATCHDOG' in e for e in ev), '10 s(펌웨어 시간) 쉬어도 PING 으로 WATCHDOG 안 터짐')
    finally:
        r.close()


def t_g1_fail():
    print('[g1] P1: G1 이 자가 시험 FAIL → 시작 안 함, 문·축 명령 안 보냄')
    r = Rig(doors_args=('--dead', 'G1'))
    try:
        try:
            r.ctl.boot()
            check(False, 'TrapFault 가 나야 함')
        except TrapFault as e:
            check(e.code == 'G1_SELFTEST_FAIL', 'TrapFault G1_SELFTEST_FAIL')
        check(not any(s.startswith('DOOR') for s in r.sent_d()), '문 명령 없음')
        check(not any(s.startswith(('HOME', 'MOVE', 'PEN')) for s in r.sent_m()), '축·펜 명령 없음')
        check(any(n['kind'] == 'g1_fail' for n in r.ctl.notes), '알림 g1_fail')
    finally:
        r.close()


def t_beam_retest_ok():
    print('[retest] P2: 켤 때 G2b 가 막혀 FAIL → 10 s(펌웨어 시간) 뒤 다시 시험 → 풀려서 OK, 정상 켜기')
    r = Rig(doors_args=('--block', 'G2b'))
    try:
        import threading
        threading.Timer(0.8, lambda: r.pd.control('#BLOCK G2b 0')).start()   # 4 s(펌웨어 시간) 뒤 말벌이 빠짐
        rep = r.ctl.boot()
        check(sum(1 for s in r.sent_d() if s == 'SELFTEST') == 2, 'SELFTEST 2번')
        check(rep['unusable'] == [], '두 번째에 OK → 쓰지 못하는 문 없음')
        check(any(n['kind'] == 'beam_fail_retest' for n in r.ctl.notes), '알림 beam_fail_retest')
    finally:
        r.close()


def t_beam_dead():
    print('[dead] P2: G2b 고장 → 다시 시험해도 FAIL → IN 은 쓰지 않음, 나머지는 켬, IN 닫기는 거부')
    r = Rig(doors_args=('--dead', 'G2b'))
    try:
        rep = r.ctl.boot()
        check(rep['unusable'] == ['IN'], '쓰지 못하는 문 = IN')
        check('DOOR IN CLOSE' not in r.sent_d(), 'IN 에는 닫기 명령을 보내지 않음')
        check('DOOR CAP CLOSE' in r.sent_d() and 'DOOR REL CLOSE' in r.sent_d(), 'CAP·REL 은 닫음')
        try:
            r.ctl.close_door('IN')
            check(False, 'TrapFault 가 나야 함')
        except TrapFault as e:
            check(e.code == 'DOOR_IN_UNUSABLE', 'close_door(IN) → DOOR_IN_UNUSABLE')
    finally:
        r.close()


def t_door_retry():
    print('[retry] P6: 펌웨어 BLOCKED(3번 다시 엶) → 5 s 쉬고 다시 → 닫힘')
    r = Rig()
    try:
        r.ctl.boot()
        r.ctl.open_door('IN')
        r.ctl.idle(0.3)
        r.pd.control('#CLOSEBLOCK IN G2b 3')      # 닫는 중 3번 끊김 → 펌웨어 한 번 시도 = BLOCKED
        k = r.ctl.close_door('IN')
        check(k == 2, 'Pi 두 번째 시도에서 닫힘 (첫 번째는 BLOCKED)')
        ev = [n for n in r.ctl.notes if n['kind'] == 'door_not_closed']
        check(len(ev) == 1 and 'BLOCKED' in ev[0]['why'], '알림 door_not_closed 1번 (EVT DOOR IN BLOCKED)')
        d = r.sent_d()
        check(d.count('DOOR IN CLOSE') >= 2, 'DOOR IN CLOSE 2번 보냄')
    finally:
        r.close()


def t_door_stuck():
    print('[stuck] P6: 계속 막힘 → Pi 3번 × 펌웨어 3번 = 9번 뒤 DOOR_IN_STUCK')
    r = Rig()
    try:
        r.ctl.boot()
        r.ctl.open_door('IN')
        r.ctl.idle(0.3)
        r.pd.control('#CLOSEBLOCK IN G2b 99')
        try:
            r.ctl.close_door('IN')
            check(False, 'TrapFault 가 나야 함')
        except TrapFault as e:
            check(e.code == 'DOOR_IN_STUCK', 'TrapFault DOOR_IN_STUCK')
        reopen = [s for _, dr, s in r.d.history if dr == '<<' and s.startswith('EVT DOOR IN REOPEN')]
        check(len(reopen) == 9, '다시 열기 9번 (펌웨어 3 × Pi 3) — 실제 %d' % len(reopen))
        sd = parse_status(r.d.command('STATUS'))
        check(sd.get('IN') == 'BLOCKED', '문은 열린 채 (BLOCKED)')
    finally:
        r.close()


def t_night_day():
    print('[night] P3: 밤 = 펜 UP·F 0 → REL CLOSE → IN·CAP OPEN → 조명 0 → EMIT 0, 아침은 EMIT 1 부터')
    r = Rig()
    try:
        r.ctl.boot()
        n0 = len(r.d.history)
        r.ctl.night_mode()
        d = [s for _, dr, s in list(r.d.history)[n0:] if dr == '>>' and s != 'PING']
        check(d == ['DOOR REL CLOSE', 'DOOR IN OPEN', 'DOOR CAP OPEN', 'LIGHT TOP 0', 'LIGHT BOT 0', 'EMIT 0'], 'UNO 2 순서 그대로: %s' % d)
        sd = parse_status(r.d.command('STATUS'))
        check(sd.get('IN') == 'OPEN' and sd.get('CAP') == 'OPEN' and sd.get('REL') == 'CLOSED' and sd.get('EMIT') == '0', '밤 상태: IN·CAP 열림, REL 닫힘, 송신 꺼짐')
        n1 = len(r.d.history)
        r.ctl.day_mode()
        d = [s for _, dr, s in list(r.d.history)[n1:] if dr == '>>' and s != 'PING']
        check(d[0] == 'EMIT 1' and d[1:] == ['DOOR CAP CLOSE', 'DOOR REL CLOSE', 'DOOR IN OPEN'], '아침 순서: EMIT 1 → CAP·REL 닫기 → IN 열기')
    finally:
        r.close()


def t_rail():
    print('[rail] P4: 비상 정지 → EVT RAIL 0 → UNO 1 STOP, 풀림 → PEN UP → HOME F·X·Y → 문 OPEN → 대기 자리')
    r = Rig()
    try:
        r.ctl.boot()
        r.pd.control('#RAIL 0')
        end = time.time() + 2
        while time.time() < end and r.ctl.rail:
            r.ctl.service()
        check(not r.ctl.rail, 'EVT RAIL 0 받음')
        check('STOP' in r.sent_m(), 'UNO 1 에 STOP (A1)')
        try:
            r.ctl.open_door('IN')
            check(False, '거부돼야 함')
        except Exception as e:
            check('ERR RAIL' in str(e), 'RAIL 0 동안 문 명령 → ERR RAIL')
        n0 = len(r.m.history)
        r.pd.control('#RAIL 1')
        res, end = None, time.time() + 30
        while time.time() < end and res is None:
            res = r.ctl.service()
        check(res == 'recovered', '복귀 순서 끝남')
        m = [s for _, dr, s in list(r.m.history)[n0:] if dr == '>>' and s not in ('PING',)]
        check(order_ok(m, ['HOLD F 0', 'PEN UP', 'HOME F', 'HOME X', 'HOME Y', 'MOVE X', 'MOVE Y', 'PEN DOWN']), 'UNO 1 복귀 순서')
        sd = parse_status(r.d.command('STATUS'))
        check(sd.get('IN') == sd.get('CAP') == sd.get('REL') == 'OPEN', '문은 OPEN 부터 (3개 열림)')
    finally:
        r.close()


def t_status_fallback():
    print('[fallback] READY 를 놓쳐도(이미 켜진 UNO) STATUS 모양으로 이름을 가림')
    pm, pd = SimPort('sim_motion.exe', speed=SPEED), SimPort('sim_doors.exe', speed=SPEED)
    try:
        time.sleep(0.5)
        while pm.readline() or pd.readline():   # READY·SELFTEST 줄을 먼저 버림
            pass
        links = identify([('A', pd), ('B', pm)], ready_timeout=0.5)
        check(links['trap_motion'].label == 'B' and links['trap_doors'].label == 'A', 'STATUS 로 가림')
    finally:
        pm.close()
        pd.close()


TESTS = dict(boot=t_boot, g1=t_g1_fail, retest=t_beam_retest_ok, dead=t_beam_dead, retry=t_door_retry,
             stuck=t_door_stuck, night=t_night_day, rail=t_rail, fallback=t_status_fallback)

if __name__ == '__main__':
    names = sys.argv[1:] or list(TESTS)
    t0 = time.time()
    for n in names:
        TESTS[n]()
    print('\n== test_pi_link: PASS %d, FAIL %d (%.0f s)' % (PASS[0], FAIL[0], time.time() - t0))
    sys.exit(1 if FAIL[0] else 0)
