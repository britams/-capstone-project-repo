# -*- coding: utf-8 -*-
"""test_process.py — 처리 순서를 실제 펌웨어 로직(sim --serve, 5배속) + 가짜 카메라·가짜 말벌로 시험 (서현 CAP-AI-48)

실행:  python 관련코딩저장/pi_link/test_process.py           (decide 표 + 장면 6개, 약 1~2분)
말벌은 '#BLOCK 게이트 1/0' 줄로 빔을 차례로 끊어 흉내 낸다 (G1 → G2 → G2b → 마킹실, 나갈 때 G5 → G5b → G6 또는 G3 → G3b → G4).
"""
import os
import sys
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test_pi_link import Rig, check, PASS, FAIL, SPEED          # noqa: E402
from process import Processor, Params, decide                     # noqa: E402

W = 0.08    # 빔 하나 지나는 벽시계 시간 (5배속 → 0.4 s 펌웨어 시간)


class FakeVision:
    def __init__(self, hornet, marks_ok=True, pose_seq=None):
        self.h = hornet                 # dict(species, mw_mm, marked, x, y) 또는 None
        self.present = 0                # 마킹실 안 수 (가짜 말벌이 바꿈)
        self.marks_ok = marks_ok
        self.pose_seq = list(pose_seq or ['dorsal'])
        self.calls = []

    def look(self, what):
        self.calls.append(what)
        if self.present <= 0 or not self.h:
            return []
        o = dict(self.h, pose='dorsal', p=0.9)
        if what == 'pose':
            o['pose'] = self.pose_seq.pop(0) if len(self.pose_seq) > 1 else self.pose_seq[0]
            o['p'] = 0.9 if o['pose'] == 'dorsal' else 0.1
        if what == 'verify' and self.marks_ok:
            self.h['marked'] = True
            o['marked'] = True
        return [o] * self.present


def cross(port, gates):
    for g in gates:
        port.control('#BLOCK %s 1' % g)
        time.sleep(W)
    for g in gates:
        port.control('#BLOCK %s 0' % g)
        time.sleep(W)


def enter(rig, vis, delay=0.5):
    def go():
        time.sleep(delay)
        cross(rig.pd, ['G1'])
        time.sleep(0.2)
        cross(rig.pd, ['G2', 'G2b'])
        vis.present += 1
    threading.Thread(target=go, daemon=True).start()


def leave_when_open(rig, vis, proc):
    def on_open(d):
        if d not in ('REL', 'CAP') or vis.present <= 0:
            return
        def go():
            time.sleep(0.3)
            beams, out = (['G5', 'G5b'], 'G6') if d == 'REL' else (['G3', 'G3b'], 'G4')
            cross(rig.pd, beams)
            vis.present -= 1
            time.sleep(0.2)
            cross(rig.pd, [out])
        threading.Thread(target=go, daemon=True).start()
    proc.on_door_opened = on_open


def fast_prm(**kw):
    p = Params(feed_s=2.0 / SPEED * 5, idle_look_s=1.0)
    for k, v in kw.items():
        setattr(p, k, v)
    return p


def sent(rig):
    return [s for s in rig.sent_m() + rig.sent_d() if s != 'PING']


def run_scene(name, hornet, month=7, is_day=lambda: True, marks_ok=True, pose_seq=None, prm=None):
    print('[%s]' % name)
    r = Rig()
    try:
        r.ctl.boot()
        vis = FakeVision(hornet, marks_ok, pose_seq)
        proc = Processor(r.ctl, vis, prm or fast_prm(), month=lambda: month, is_day=is_day)
        leave_when_open(r, vis, proc)
        n0m, n0d = len(r.m.history), len(r.d.history)
        enter(r, vis)
        t0 = time.time()
        res = proc.step(entry_timeout_s=20)
        print('      결과 %s (%.1f s)' % (res, time.time() - t0))
        cm = [s for _, d, s in list(r.m.history)[n0m:] if d == '>>' and s != 'PING']
        cd = [s for _, d, s in list(r.d.history)[n0d:] if d == '>>' and s != 'PING']
        return r, proc, vis, res, cm, cd
    except Exception:
        r.close()
        raise


def t_decide():
    print('[decide] 판정 표 (C1 여왕벌: 4.4 mm, 못 재면 계절)')
    w = dict(species='velutina', mw_mm=4.0, marked=False)
    cases = [
        ([w], 7, 'mark'), ([dict(w, marked=True)], 7, 'revisit'), ([w, w], 7, 'isolate'), ([], 7, 'isolate'),
        ([dict(w, species='crabro')], 7, 'isolate'), ([dict(w, species='other')], 7, 'isolate'),
        ([dict(w, mw_mm=4.4)], 7, 'isolate'), ([dict(w, mw_mm=4.39)], 7, 'mark'),
        ([dict(w, mw_mm=None)], 10, 'isolate'), ([dict(w, mw_mm=None)], 7, 'mark'), ([dict(w, mw_mm=None)], 3, 'isolate'),
    ]
    for obs, month, want in cases:
        got = decide(obs, month)[0]
        check(got == want, '%s 월 %d → %s (%s)' % ([(o['species'], o['mw_mm'], o['marked']) for o in obs], month, want, got))
    check(decide([w], 7, Params(control_mode=True))[0] == 'isolate', '방제 모드 → isolate')


def t_mark():
    r, proc, vis, res, cm, cd = run_scene('mark 일벌: 진입 → IN 닫기 → 판별 → PRESS → 자세 → 2번 찍기 → 확인 → 급이 → 방생',
                                          dict(species='velutina', mw_mm=4.0, marked=False, x=3.0, y=-5.0))
    try:
        check(res == ('release', 'worker'), '결과 release (worker)')
        check('DOOR IN CLOSE' in cd and cd.index('DOOR IN CLOSE') < cd.index('DOOR REL OPEN'), '진입 뒤 IN 닫고, 나중에 REL 엶')
        check(any(s.startswith('PRESS 51') for s in cm), 'PRESS 51 g')
        check('MOVE X 3.000' in cm and 'MOVE Y -5.000' in cm, '자세 사진의 흉부 좌표(3, −5)로 감 (C2)')
        i = cm.index('MOVE Y -5.000')
        check(cm[i + 1:i + 5] == ['PEN DOWN', 'PEN UP', 'PEN DOWN', 'PEN UP'], '2번 찍기 (DOWN·UP ×2)')
        check('MOVE F 10.000' in cm, '급이 높이 F 10')
        check(cd[-2:] == ['DOOR REL CLOSE', 'LIGHT TOP 0'] or 'DOOR REL CLOSE' in cd, 'REL 닫음')
        check(cm[-1] == 'MOVE F 0.000', '마지막에 바닥 0')
        check(proc.ledger.n['released'] == 1 and proc.ledger.n['chamber'] == 0, '장부: 방생 1, 마킹실 0')
        check(vis.calls[:3] == ['entry', 'after_close', 'identify'] or vis.calls[0] in ('entry', 'idle_check'), '카메라 순서 entry → after_close → identify')
        check('verify' in vis.calls and vis.h['marked'], '점 확인')
    finally:
        r.close()


def t_queen():
    r, proc, vis, res, cm, cd = run_scene('queen 여왕벌 4.7 mm → 격리: 바닥 0 → CAP 열기 → 지나감 → 닫기, PRESS 없음',
                                          dict(species='velutina', mw_mm=4.7, marked=False, x=0, y=0))
    try:
        check(res == ('isolate', 'queen'), '결과 isolate (queen)')
        check(not any(s.startswith('PRESS') for s in cm), 'PRESS 안 함')
        check('DOOR CAP OPEN' in cd and cd.index('DOOR CAP OPEN') < len(cd) - 1 and 'DOOR CAP CLOSE' in cd[cd.index('DOOR CAP OPEN'):], 'CAP 열고 나간 뒤 닫음')
        check(proc.ledger.n['captured'] == 1, '장부: 포획 1')
        check('DOOR REL OPEN' not in cd, '방생 문은 안 엶')
    finally:
        r.close()


def t_revisit():
    r, proc, vis, res, cm, cd = run_scene('revisit 이미 표식 → 급이(펜 캡 컵에 꽂힌 채 F 10, R1′) → 방생',
                                          dict(species='velutina', mw_mm=4.0, marked=True, x=0, y=0))
    try:
        check(res == ('release', 'marked'), '결과 release (marked)')
        check(not any(s.startswith(('PRESS', 'PEN')) for s in cm), 'PRESS·펜 명령 없음')
        check('MOVE F 10.000' in cm, '급이 F 10 — 펌웨어가 받아들임 (R1′, 펜은 Y −40 캡 컵)')
        check(not any('ERR' in n.get('why', '') for n in proc.log), '오류 없음')
    finally:
        r.close()


def t_season():
    r, proc, vis, res, cm, cd = run_scene('season 10월, 폭 못 잼 → 여왕으로 보고 격리',
                                          dict(species='velutina', mw_mm=None, marked=False, x=0, y=0), month=10)
    try:
        check(res == ('isolate', 'queen'), '결과 isolate (queen, 계절 규칙)')
    finally:
        r.close()


def t_dusk():
    state = {'n': 0}

    def is_day():
        state['n'] += 1
        return state['n'] <= 1          # step 시작 때만 낮, 방생 직전엔 해 짐
    r, proc, vis, res, cm, cd = run_scene('dusk 재방문인데 방생 직전 해 짐 → 격리',
                                          dict(species='velutina', mw_mm=4.0, marked=True, x=0, y=0), is_day=is_day)
    try:
        check(res == ('isolate', 'dusk'), '결과 isolate (dusk)')
        check(any(n.get('why') == 'dusk' for n in proc.log), '판단 dusk → isolate')
        check('DOOR CAP OPEN' in cd and 'DOOR REL OPEN' not in cd, 'CAP 으로 보냄, REL 안 엶')
    finally:
        r.close()


def t_pose_retry():
    r, proc, vis, res, cm, cd = run_scene('pose 첫 자세가 배가 위 → 10 mm 내렸다 다시 PRESS → 등이 위 → 마킹',
                                          dict(species='velutina', mw_mm=4.0, marked=False, x=1.0, y=2.0), pose_seq=['ventral', 'dorsal'])
    try:
        check(sum(1 for s in cm if s.startswith('PRESS')) == 2, 'PRESS 2번')
        check(any(n['kind'] == 'pose_retry' for n in proc.log), '알림 pose_retry')
        check(res == ('release', 'worker'), '결국 마킹 후 방생')
    finally:
        r.close()


if __name__ == '__main__':
    t0 = time.time()
    tests = dict(decide=t_decide, mark=t_mark, queen=t_queen, revisit=t_revisit, season=t_season, dusk=t_dusk, pose=t_pose_retry)
    for n in (sys.argv[1:] or list(tests)):
        tests[n]()
    print('\n== test_process: PASS %d, FAIL %d (%.0f s)' % (PASS[0], FAIL[0], time.time() - t0))
    sys.exit(1 if FAIL[0] else 0)
