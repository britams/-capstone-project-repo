# -*- coding: utf-8 -*-
"""process.py — 말벌 한 마리 처리 순서 + 주 루프 (서현 CAP-AI-48, 2026-11-08)

trap_sim.py (PiFSM wait_entry·process·press_mark·feed·release·isolate·leave·night·shutdown_safe)를
실제 펌웨어 v0.2 명령으로 옮긴 것. 판정 기준은 서현 결정(11/06)과 인터페이스 정의서 '여왕벌 판정' 줄.

순서 (한 마리)
  대기: 조명 위 0·아래 255, CAP·REL 닫힘, IN 열림
  진입: 장부(빛 게이트 순서)로 마킹실 1마리 이상 → 카메라로 확인 → IN 닫기 → 다시 셈
  판별: 위 조명 → 카메라 → decide()
    격리  : 2마리 이상 / 안 보임 / 2종 아님·불확실 / 유럽말벌 / 여왕벌 / 방제 모드
    재방문: 이미 표식 → 급이 → 방생
    마킹  : PRESS(51 g) → 자세 확인(등이 위, p ≥ 0.6) → 흉부 위 펜 2번 찍기 → 대기 자리 → 점 확인 → 급이 → 방생
  급이: 바닥 10 mm, feed_s 동안 (샤피 건조 시간 시험 전 [추측])
  방생: (해 지면 격리로) REL 열기 → 장부·카메라로 빌 때까지 → 60 s 기록, 120 s 알림, 300 s CAP도 엶 → 닫기 → 바닥 0
  격리: 바닥 0 → CAP 열기 → 빌 때까지 → 닫기
  고장(TrapFault): 통과 모드 — CAP·IN 열고 조명 끔 (마킹실에 갇혀 죽지 않게), 알리고 멈춤

이 파일이 정한 규칙 (AI 판단, 서현 위임 — CAP-AI-48)
  C1. 여왕벌 판정은 Pi가 한다: 중순판 폭 mw_mm ≥ 4.4 → 여왕, 못 쟀으면(None) 3~5·9~11월 여왕 / 6~8월 일벌
      (trap_sim은 카메라 흉내 안에서 했음 → 비전은 숫자만 주고 판단은 한 곳에서)
  C2. 흉부 좌표는 '자세 확인' 사진(PRESS 뒤)의 x·y를 쓴다 (trap_sim은 고정 55, 0) — 눌린 뒤 자리가 정확함
  C3. 비전 좌표 = 펌웨어 좌표 (원점 격자 가운데, 인터페이스 정의서 좌표계). 범위 밖이면 마킹 안 하고 급이·방생
  C4. (CAP-AI-52) 비전이 흉부 타원 thorax(x, y, θ, L, w)·unc를 주면 승준 mark_planner.plan()으로 찍을 점을 고른다
      (격자 구멍 안 + 흉부 안전영역 확률 ≥ 0.5). 고를 점이 없으면 자세 다시 잡기. thorax가 없으면 C2대로 x, y 한 점.
      결과 형식은 vision_format.py
  C5. (CAP-AI-52) 낮밤은 서현 결정: 밤에는 처리하지 않고 전부 포획통 (daynight.py와 같은 순서). 기다리는 중에 해가 지면
      wait_entry가 0으로 돌아와 다음 step이 night_mode로 간다
"""
import os
import sys
import time
from dataclasses import dataclass

from controller import TrapFault

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'vision', 'scripts'))


def plan_stamps(h, start):
    """C4: 승준 mark_planner로 찍을 점들. thorax 없으면 [(x, y)], 확률 낮으면 []."""
    if 'thorax' not in h:
        return [(h['x'], h['y'])]
    import mark_planner                                  # numpy 필요 — thorax를 줄 때만 부름
    r = mark_planner.plan(h['thorax'], h['unc'], start=start)
    return [tuple(p) for p in r['route']]

GAP = {'IN': ('G2', 'G2b'), 'CAP': ('G3', 'G3b'), 'REL': ('G5', 'G5b')}
PAIR = {g: (d, i) for d, pr in GAP.items() for i, g in enumerate(pr)}
QUEEN_MONTHS = (3, 4, 5, 9, 10, 11)


@dataclass
class Params:                   # 값 근거는 trap_sim PRM — [추측]은 시험으로 고칠 것
    press_g: float = 51.0       # F_p 0.5 N [확실 — D6]
    F_feed: float = 31.0
    F_retract: float = 10.0
    feed_s: float = 60.0        # [추측]
    dwell_s: float = 0.3        # 펜이 닿아 있는 시간 [추측]
    stamps: int = 2
    pose_retry_max: int = 3
    mark_retry_max: int = 1
    thorax_p_min: float = 0.6
    gyne_mw_mm: float = 4.4     # Pérez-de-Heredia 2017 (CAP-AI-24)
    control_mode: bool = False  # 방제 모드: 모두 격리
    T_light_s: float = 60.0
    T_alert_s: float = 120.0
    T_fallback_s: float = 300.0
    entry_looks: int = 10
    idle_look_s: float = 5.0
    x_range: tuple = (-18.0, 18.0)
    y_range: tuple = (-20.5, 18.0)   # 마킹실 위 (Y > -20.5)


def is_queen(obs, month, prm=Params()):
    """C1: 폭을 쟀으면 4.4 mm, 못 쟀으면 계절."""
    mw = obs.get('mw_mm')
    if mw is None:
        return month in QUEEN_MONTHS
    return mw >= prm.gyne_mw_mm


def decide(obs_list, month, prm=Params()):
    """판별 사진 → ('isolate'|'revisit'|'mark', 이유). 하드웨어와 떨어진 순수 함수."""
    if len(obs_list) >= 2:
        return 'isolate', 'two_or_more'
    if not obs_list:
        return 'isolate', 'not_seen'
    h = obs_list[0]
    if h.get('species') not in ('velutina', 'crabro'):
        return 'isolate', 'uncertain'
    if prm.control_mode:
        return 'isolate', 'control_mode'
    if h['species'] == 'crabro':
        return 'isolate', 'crabro'
    if is_queen(h, month, prm):
        return 'isolate', 'queen'
    if h.get('marked'):
        return 'revisit', 'marked'
    return 'mark', 'worker'


class Ledger:
    """통로마다 들어감 − 나감 (trap_sim Ledger를 펌웨어 'EVT GATE G2b BLOCK' 형식으로).
    문은 빔 2개 순서로 방향을 안다: 앞 → 뒤 = 정방향, 뒤 → 앞 = 역방향, 같은 빔으로 빠지면 되돌아감."""

    def __init__(self):
        self.n = dict(tube_in=0, chamber=0, tube_cap=0, tube_rel=0, captured=0, released=0)
        self.on = set()
        self.pair = {d: dict(on=set(), first=None) for d in GAP}
        self.out_pending = 0
        self.changed = 0

    def on_event(self, line):
        t = line.split()                      # EVT GATE <이름> BLOCK|CLEAR
        if len(t) >= 4 and self.gate(t[2], t[3] == 'BLOCK'):
            self.changed += 1

    def gate(self, g, blocked):
        if g in PAIR:
            d, i = PAIR[g]
            st = self.pair[d]
            if blocked:
                if not st['on']:
                    st['first'] = i
                st['on'].add(i)
                return False
            st['on'].discard(i)
            if st['on'] or st['first'] is None:
                return False
            first, st['first'] = st['first'], None
            if first == i:
                return False
            return self.door_pass(d, forward=(first == 0))
        if blocked:
            self.on.add(g)
            return False
        if g not in self.on:
            return False
        self.on.discard(g)
        n = self.n
        if g == 'G1':
            if self.out_pending > 0 and n['tube_in'] > 0:
                n['tube_in'] -= 1
                self.out_pending -= 1
            else:
                n['tube_in'] += 1
        elif g == 'G4' and n['tube_cap'] > 0:
            n['tube_cap'] -= 1
            n['captured'] += 1
        elif g == 'G6' and n['tube_rel'] > 0:
            n['tube_rel'] -= 1
            n['released'] += 1
        else:
            return False
        return True

    def door_pass(self, d, forward):
        n = self.n
        src, dst = {'IN': ('tube_in', 'chamber'), 'CAP': ('chamber', 'tube_cap'), 'REL': ('chamber', 'tube_rel')}[d]
        if not forward:
            src, dst = dst, src
        n[src] = max(0, n[src] - 1)
        n[dst] += 1
        if d == 'IN' and not forward:
            self.out_pending += 1
        return True


class Processor:
    """ctl = controller.TrapController, vision.look(what) → [dict(species, mw_mm, marked, pose, p, x, y)]
    month() → 오늘 달, is_day() → 처리해도 되는 시간인가, battery_low() → INA226 부족인가"""

    def __init__(self, ctl, vision, prm=None, month=lambda: time.localtime().tm_mon,
                 is_day=lambda: True, battery_low=lambda: False):
        self.ctl, self.vision = ctl, vision
        self.prm = prm or Params()
        self.month, self.is_day, self.battery_low = month, is_day, battery_low
        self.ledger = Ledger()
        ctl.gate_listeners.append(self.ledger.on_event)
        self.on_door_opened = None            # 시험용 갈고리 (문 이름)
        self.night = False
        self.log = []                         # (무엇, 내용) — 결과 기록

    def note(self, kind, **kw):
        self.log.append(dict(kind=kind, **kw))
        self.ctl.notify(kind, **kw)

    def look(self, what):
        return self.vision.look(what)

    def _open(self, d):
        self.ctl.open_door(d)
        if self.on_door_opened:
            self.on_door_opened(d)

    # ---------------- 대기·진입 ----------------
    def to_idle(self):
        self.ctl.lights(0, 255)
        self.ctl.close_door('CAP')
        self.ctl.close_door('REL')
        self._open('IN')

    def wait_entry(self, timeout_s=None):
        """마킹실에 들어온 수 (0 = 없었음/잘못 셈). timeout_s 없으면 들어올 때까지."""
        p, L = self.prm, self.ledger
        t0 = time.monotonic()
        while L.n['chamber'] <= 0:
            c0 = L.changed
            end = time.monotonic() + p.idle_look_s
            while time.monotonic() < end and L.changed == c0 and L.n['chamber'] <= 0:
                self.ctl.idle(0.05)
            if L.n['chamber'] > 0:
                break
            if L.changed == c0:                # 5 s 조용함 → 카메라로 한 번 (장부가 놓쳤을 수 있음)
                obs = self.look('idle_check')
                if obs:
                    self.note('mismatch', what='camera %d, ledger 0' % len(obs))
                    L.n['chamber'] = len(obs)
                    break
            if timeout_s is not None and time.monotonic() - t0 > timeout_s:
                return 0
            if not self.is_day():              # C5: 기다리다 해 짐 → 다음 step이 밤으로
                return 0
        obs = []
        for _ in range(p.entry_looks):        # 구석에 있으면 못 볼 수 있음
            obs = self.look('entry')
            if obs:
                break
            self.ctl.idle(1.0)
        if not obs:
            self.note('mismatch', what='ledger %d, camera 0 → 문 열어 둠' % L.n['chamber'])
            L.n['chamber'] = 0
            return 0
        self.ctl.close_door('IN')
        obs = self.look('after_close')
        if len(obs) != L.n['chamber']:
            self.note('mismatch', what='ledger %d, camera %d' % (L.n['chamber'], len(obs)))
            L.n['chamber'] = len(obs)
        return len(obs)

    # ---------------- 처리 ----------------
    def process(self, n):
        if n >= 2:
            return self._finish('isolate', 'two_or_more')
        self.ctl.lights(255, 0)
        obs = self.look('identify')
        action, why = decide(obs, self.month(), self.prm)
        self.note('decision', action=action, why=why)
        if action == 'isolate':
            return self._finish('isolate', why)
        if action == 'mark':
            ok = self.press_mark()
            self.note('mark_result', ok=ok)
        self.feed()
        return self._finish('release', why)

    def _finish(self, action, why):
        if action == 'release' and not self.release():     # 해가 져서 격리로 바뀜
            return 'isolate', 'dusk'
        if action != 'release':
            self.isolate()
        return action, why

    def _in_range(self, h):
        p = self.prm
        return p.x_range[0] <= h.get('x', 99) <= p.x_range[1] and p.y_range[0] < h.get('y', 99) <= p.y_range[1]

    def press_mark(self):
        c, p = self.ctl, self.prm
        for attempt in range(1, p.pose_retry_max + 1):
            c.pen(True)
            c.lights(0, 255)
            r = c.move_xy_press(0.0, 0.0, p.press_g)       # 격자 가운데 위에서 누름 (아직 흉부 자리를 모름)
            if r is None:                                  # 바닥이 한계까지 — 말벌이 안 눌림
                self.note('press_limit', attempt=attempt)
                c.move('F', 0.0)
                continue
            F_now = r[0]
            c.lights(255, 0)
            obs = self.look('pose')
            h = obs[0] if obs else None
            if not h or h.get('pose') != 'dorsal' or h.get('p', 0) < p.thorax_p_min or not self._in_range(h):
                self.note('pose_retry', attempt=attempt, pose=h.get('pose') if h else None)
                c.move('F', max(0.0, F_now - p.F_retract))
                c.idle(2.0)
                continue
            route = plan_stamps(h, (c.cfg.park['X'], c.cfg.park['Y']))
            if not route:                                  # C4: 안전하게 찍을 점 없음 → 자세 다시
                self.note('pose_retry', attempt=attempt, pose='no_safe_point')
                c.move('F', max(0.0, F_now - p.F_retract))
                c.idle(2.0)
                continue
            for k in range(p.mark_retry_max + 1):
                for x, y in route:
                    c.move_xy(x, y)                        # C2 / C4
                    for _ in range(p.stamps):
                        c.pen(False)
                        c.idle(p.dwell_s)
                        c.pen(True)
                c.move_xy(c.cfg.park['X'], c.cfg.park['Y'])
                v = self.look('verify')
                if v and v[0].get('marked'):
                    c.pen(False)                            # 캡 컵 안으로
                    return True
                self.note('mark_unverified', try_=k + 1)
            c.pen(False)
            return False
        self.note('pose_fail')
        c.move('F', 0.0)
        c.park()
        return False

    def feed(self):
        self.ctl.lights(0, 255)
        self.ctl.move('F', self.prm.F_feed)               # R1′: 펜이 캡 컵(Y −40)이면 펜 DOWN이어도 올림 허용
        self.ctl.idle(self.prm.feed_s)

    def floor_down(self):
        self.ctl.move('F', 0.0)

    def release(self):
        """방생했으면 True, 해가 져서 격리했으면 False."""
        if not self.is_day():
            self.note('decision', action='isolate', why='dusk')
            self.isolate()
            return False
        self.ctl.lights(0, 0)
        self.leave('REL')
        self.floor_down()
        return True

    def isolate(self):
        self.floor_down()
        self.ctl.lights(0, 0)
        self.leave('CAP')

    def leave(self, d):
        """문을 열고 마킹실이 빌 때까지 (장부 + 카메라) 기다린 뒤 닫음."""
        p, L = self.prm, self.ledger
        self._open(d)
        t0 = time.monotonic()
        nudged = alerted = fallback = False
        while True:
            self.ctl.idle(0.2)
            n = L.n
            if n['chamber'] == 0 and n['tube_cap'] == 0 and n['tube_rel'] == 0:
                obs = self.look('empty_check')
                if not obs:
                    break
                self.note('mismatch', what='ledger 0, camera %d' % len(obs))
                n['chamber'] = len(obs)
            el = time.monotonic() - t0
            if el > p.T_light_s and not nudged:
                nudged = True
                self.note('nudge', door=d)
            if el > p.T_alert_s and not alerted:
                alerted = True
                self.note('alert', door=d, wait_s=round(el))
            if el > p.T_fallback_s and not fallback and d == 'REL':
                fallback = True
                self.note('fallback', what='REL 300 s → CAP도 엶')
                self._open('CAP')
        self.ctl.close_door(d)
        if fallback:
            self.ctl.close_door('CAP')

    def passthrough(self, why):
        """고장: 상용 트랩처럼 지나가게 CAP·IN 열고 조명 끔."""
        self.note('passthrough', why=why)
        for cmd in (lambda: self.ctl.lights(0, 0), lambda: self.ctl.open_door('CAP'), lambda: self.ctl.open_door('IN')):
            try:
                cmd()
            except Exception as e:          # 레일이 꺼졌으면 문도 못 움직임 — 할 수 있는 만큼
                self.note('passthrough_partial', error=str(e))

    # ---------------- 주 루프 ----------------
    def step(self, entry_timeout_s=None):
        """한 바퀴: 배터리·낮밤 확인 → 대기 → 진입 → 처리. 돌려주는 값: 무엇을 했는지."""
        try:
            if self.battery_low():
                self.passthrough('battery_low')
                return 'shutdown'
            if not self.is_day():
                if not self.night:
                    self.ctl.night_mode()
                    self.night = True
                self.ctl.idle(1.0)
                return 'night'
            if self.night:
                self.ctl.day_mode()
                self.night = False
            self.to_idle()
            n = self.wait_entry(entry_timeout_s)
            if n <= 0:
                return 'no_entry'
            return self.process(n)
        except TrapFault as e:
            self.passthrough(e.code)
            raise
