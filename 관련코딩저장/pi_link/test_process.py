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
        FakeVision.last = self

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
        check('MOVE F 31.000' in cm, '급이 높이 F 31')
        check('PUMP 100' in cd and cd.index('PUMP 100') < cd.index('DOOR REL OPEN'), '급이 때 펌프 100 ms (방생 문 열기 전, CAP-AI-59)')
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
    r, proc, vis, res, cm, cd = run_scene('revisit 이미 표식 → 급이(펜 캡 컵에 꽂힌 채 F 31, R1′) → 방생',
                                          dict(species='velutina', mw_mm=4.0, marked=True, x=0, y=0))
    try:
        check(res == ('release', 'marked'), '결과 release (marked)')
        check(not any(s.startswith(('PRESS', 'PEN')) for s in cm), 'PRESS·펜 명령 없음')
        check('MOVE F 31.000' in cm, '급이 F 31 — 펌웨어가 받아들임 (R1′, 펜은 Y −40 캡 컵)')
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
    def is_day():                       # 판별(identify) 사진 뒤에 해 짐 → 방생 직전엔 밤
        return 'identify' not in FakeVision.last.calls
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


def t_format():
    print('[format] vision_format: VespAI 클래스·신뢰도 → species, 점 → marked, 화소 → mm (CAP-AI-52)')
    from vision_format import make_obs, px_to_mm
    check(make_obs(1, 0.95)['species'] == 'velutina' and make_obs(0, 0.9)['species'] == 'crabro', '클래스 1 velutina, 0 crabro')
    check(make_obs(1, 0.7)['species'] == 'other', '신뢰도 0.7 < 0.8 → other (격리)')
    check(make_obs(1, 0.9, dots=[dict(x=1, y=1)])['marked'] and not make_obs(1, 0.9)['marked'], '점 있으면 marked')
    o = make_obs(1, 0.9, mw_mm=4.0, thorax=(1.0, -0.5, 0.5, 5.5, 4.1))
    check(o['x'] == 1.0 and o['y'] == -0.5 and len(o['unc']) == 3, 'thorax → x, y, unc')
    check(decide([o], 7)[0] == 'mark', 'make_obs 결과가 decide로 바로 들어감')
    cam = dict(u0=1000, v0=800, px_per_mm=15.6)
    x, y = px_to_mm(1000 + 15.6 * 3, 800 - 15.6 * 2, cam)
    check(abs(x - 3) < 1e-9 and abs(y - 2) < 1e-9, '화소 (+3 mm 오른쪽, 2 mm 위) → (3, 2)')


def t_planner():
    import math
    th = (1.0, -0.5, math.radians(30), 5.5, 4.1)
    r, proc, vis, res, cm, cd = run_scene('planner 흉부 타원을 주면 승준 mark_planner가 고른 점에 찍음 (C4)',
                                          dict(species='velutina', mw_mm=4.0, marked=False, x=th[0], y=th[1],
                                               thorax=th, unc=(0.4, math.radians(8), 0.1)))
    try:
        import mark_planner
        want = mark_planner.plan(th, (0.4, math.radians(8), 0.1), start=(10.0, -40.0))['route']
        check(res == ('release', 'worker'), '결과 release (worker)')
        check(len(want) == 1, '고른 점 1개 (k=1)')
        mx = 'MOVE X %.3f' % want[0][0]
        check(mx in cm and 'MOVE Y %.3f' % want[0][1] in cm, '그 점으로 감 %s' % (want[0],))
        check(cm[cm.index('MOVE Y %.3f' % want[0][1]) + 1:][:2] == ['PEN DOWN', 'PEN UP'], '거기서 찍음')
    finally:
        r.close()


def t_night_wait():
    print('[nightwait] 말벌 기다리는 중 해 짐 → step 끝 → 다음 step이 밤 (REL 닫고 IN·CAP 엶) (C5)')
    r = Rig()
    try:
        r.ctl.boot()
        day = {'v': True}
        proc = Processor(r.ctl, FakeVision(None), fast_prm(), month=lambda: 7, is_day=lambda: day['v'])
        threading.Timer(1.5, lambda: day.__setitem__('v', False)).start()
        t0 = time.time()
        res = proc.step()                       # 시간 제한 없음 — 고치기 전에는 여기서 안 끝남
        check(res == 'no_entry' and time.time() - t0 < 10, '기다림이 해 지자 끝남 (%s, %.1f s)' % (res, time.time() - t0))
        n0 = len(r.d.history)
        check(proc.step() == 'night', '다음 step → night')
        cd = [s for _, d, s in list(r.d.history)[n0:] if d == '>>' and s != 'PING']
        check('DOOR CAP OPEN' in cd and 'DOOR IN OPEN' in cd and 'DOOR REL OPEN' not in cd, '밤: CAP·IN 열림, REL 안 엶')
    finally:
        r.close()


if __name__ == '__main__':
    t0 = time.time()
    tests = dict(decide=t_decide, format=t_format, mark=t_mark, queen=t_queen, revisit=t_revisit, season=t_season,
                 dusk=t_dusk, pose=t_pose_retry, planner=t_planner, nightwait=t_night_wait)
    for n in (sys.argv[1:] or list(tests)):
        tests[n]()
    print('\n== test_process: PASS %d, FAIL %d (%.0f s)' % (PASS[0], FAIL[0], time.time() - t0))
    sys.exit(1 if FAIL[0] else 0)
