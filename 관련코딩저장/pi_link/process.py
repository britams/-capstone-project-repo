# -*- coding: utf-8 -*-
"""process.py — 말벌 한 마리 처리 순서 + 주 루프 (서현 CAP-AI-48, 2026-11-08)

trap_sim.py (PiFSM wait_entry·process·press_mark·feed·release·isolate·leave·night·shutdown_safe)를
실제 펌웨어 v0.2 명령으로 옮긴 것. 판정 기준은 서현 결정(11/06)과 인터페이스 정의서 '여왕벌 판정' 줄.

순서 (한 마리)
  대기: 조명 위 0·아래 255, CAP·REL 닫힘, IN 열림
  진입: (11/17) G2가 끊겼다 이어지면(또는 5 s 조용하면) 카메라로 셈 → 1마리 이상이면 IN 닫기 → 다시 셈
        빔이 문마다 1개라 방향을 모름 → 수는 카메라가 셈 (예전 장부의 빔 2개 순서 셈은 없앰)
  판별: 위 조명 → 카메라 → decide()
    격리  : 2마리 이상 / 안 보임 / 2종 아님·불확실 / 유럽말벌 / 여왕벌 / 방제 모드
    재방문: 이미 표식 → 급이 → 방생
    마킹  : PRESS(51 g) → 자세 확인(등이 위, p ≥ 0.6) → 흉부 위 펜 2번 찍기 → 대기 자리 → 점 확인 → 급이 → 방생
  급이: (11/17) 펌프 feed_pump_ms로 급이실 177 접시에 설탕물 → feed_s(10 s — 서현 관찰 약 7 s + 여유) 동안 마킹실에서 잉크 건조
  방생: (해 지면 격리로) REL(안쪽 문 176) 열기 → 카메라에 안 보이고 G5가 비면 REL 닫기 + 로그 release_time (방생 시각) → 바닥 0
        60 s 기록, 120 s 알림, 300 s CAP도 엶. 급이실은 밖 문이 없어 말벌이 먹고 스스로 나감
  격리: 바닥 0 → CAP 열기 → 카메라에 안 보이고 G3b가 비면 닫기 + 로그 capture_time
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
import subprocess
import sys
import time
from dataclasses import dataclass

from controller import TrapFault, DOOR_BEAM, ENTRY

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'vision', 'scripts'))


def plan_stamps(h, start):
    """C4: 승준 mark_planner로 찍을 점들. thorax 없으면 [(x, y)], 확률 낮으면 []."""
    if 'thorax' not in h:
        return [(h['x'], h['y'])]
    import mark_planner                                  # numpy 필요 — thorax를 줄 때만 부름
    r = mark_planner.plan(h['thorax'], h['unc'], start=start)
    return [tuple(p) for p in r['route']]

QUEEN_MONTHS = (3, 4, 5, 9, 10, 11)


@dataclass
class Params:                   # 값 근거는 trap_sim PRM — [추측]은 시험으로 고칠 것
    always_day: bool = False    # (11/17 서현) 시연용 스위치 — 시계·해 뜸·짐을 안 보고 늘 처리
    press_g: float = 51.0       # F_p 0.5 N [확실 — D6]
    F_retract: float = 10.0
    feed_s: float = 10.0        # (11/15 서현 "잉크 거의 7초면 마름") 7 s + 여유 3 s [AI 판단] — 말벌 몸(털) 위에서 다시 잼
    feed_pump_ms: float = 100.0  # (CAP-AI-59) 한 번 먹일 때 펌프 시간 — 약 0.14 mL [추측 — 실측으로 맞춤]. 펌웨어 PUMP_MAX_MS(200) 이하, 접시 0.34 mL
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


def clock_synced():
    """(11/17 서현) Pi 시계가 인터넷 시간으로 맞춰졌는가. RTC 배터리가 없어 전원을 끄면 시계가 틀어지고,
    그러면 낮·밤 판단·여왕벌 철·방생 시각이 다 틀림 → 켤 때 폰 핫스팟으로 맞춤. timedatectl을 물을 수 없으면 False."""
    try:
        r = subprocess.run(['timedatectl', 'show', '-p', 'NTPSynchronized', '--value'], capture_output=True, text=True, timeout=3)
        return r.stdout.strip() == 'yes'
    except Exception:
        return False


class Ledger:
    """(11/17) 빛 게이트 사건 기록 — 문마다 빔 1개라 방향을 모름. on = 지금 끊긴 빔, crossed[g] = 끊겼다 이어진 수."""

    def __init__(self):
        self.on = set()
        self.crossed = {}

    def on_event(self, line):
        t = line.split()                      # EVT GATE <이름> BLOCK|CLEAR
        if len(t) < 4:
            return
        if t[3] == 'BLOCK':
            self.on.add(t[2])
        elif t[2] in self.on:
            self.on.discard(t[2])
            self.crossed[t[2]] = self.crossed.get(t[2], 0) + 1


class Processor:
    """ctl = controller.TrapController, vision.look(what) → [dict(species, mw_mm, marked, pose, p, x, y)]
    month() → 오늘 달, is_day() → 처리해도 되는 시간인가, battery_low() → INA226 부족인가"""

    def __init__(self, ctl, vision, prm=None, month=lambda: time.localtime().tm_mon if time.localtime().tm_year >= 2026 else 4,   # (11/14) RTC 배터리 없음: 시계가 안 맞으면(2026년 전) 4월 = 여왕벌 철로 봄 → 격리 쪽 (안전)
                 is_day=lambda: True, battery_low=lambda: False, clock_ok=clock_synced):
        self.ctl, self.vision = ctl, vision
        self.prm = prm or Params()
        self.month, self.is_day, self.battery_low = month, is_day, battery_low
        self.ledger = Ledger()
        ctl.gate_listeners.append(self.ledger.on_event)
        self.on_door_opened = None            # 시험용 갈고리 (문 이름)
        self.night = False
        self.log = []                         # (무엇, 내용) — 결과 기록
        self.clock_ok = clock_ok()
        if not self.clock_ok:                 # (11/17) 알림: 폰 핫스팟에 이어 인터넷 시간을 받을 것
            self.note('clock_unsynced')
        if self.prm.always_day:
            self.is_day = lambda: True

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
        """마킹실에 들어온 수 (0 = 없었음). timeout_s 없으면 들어올 때까지.
        (11/17) G2가 끊겼다 이어지면 카메라로 셈 (빔 1개라 들어왔는지 되돌아갔는지 모름), 5 s 조용하면 한 번 봄."""
        p, L = self.prm, self.ledger
        t0 = time.monotonic()
        while True:
            c0 = L.crossed.get(ENTRY, 0)
            end = time.monotonic() + p.idle_look_s
            while time.monotonic() < end and L.crossed.get(ENTRY, 0) == c0:
                self.ctl.idle(0.05)
            obs = []
            if L.crossed.get(ENTRY, 0) != c0:
                for _ in range(p.entry_looks):    # 구석에 있으면 못 볼 수 있음
                    obs = self.look('entry')
                    if obs:
                        break
                    self.ctl.idle(1.0)
                if not obs:
                    self.note('mismatch', what='G2 지나감, camera 0 → 문 열어 둠')
            else:                                  # 5 s 조용함 → 카메라로 한 번 (G2가 놓쳤을 수 있음)
                obs = self.look('idle_check')
                if obs:
                    self.note('mismatch', what='camera %d, G2 사건 없음' % len(obs))
            if obs:
                break
            if timeout_s is not None and time.monotonic() - t0 > timeout_s:
                return 0
            if not self.is_day():              # C5: 기다리다 해 짐 → 다음 step이 밤으로
                return 0
        self.ctl.close_door('IN')
        n = len(self.look('after_close'))
        if n != len(obs):
            self.note('mismatch', what='entry %d, after_close %d' % (len(obs), n))
        return n

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
        if not self.ctl.pump(self.prm.feed_pump_ms):    # (CAP-AI-59) 먹일 때만 접시에 떨어뜨림 — 평소 접시는 마름 (다른 벌레가 덜 먹음)
            self.note('pump_stop')
        # (11/17 서현) 접시는 REL 뒤 급이실 177 → 바닥은 그대로, feed_s = 마킹실에서 잉크 마를 때까지 기다림. 먹는 것은 REL이 열린 뒤
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
        """문을 열고 그 문 빔이 비고 카메라에 안 보일 때까지 기다린 뒤 닫음 + 닫은 시각 기록 (11/17 서현: REL = '방생 시각')."""
        p, L = self.prm, self.ledger
        self._open(d)
        t0 = time.monotonic()
        nudged = alerted = fallback = False
        while True:
            self.ctl.idle(0.2)
            if DOOR_BEAM[d] not in L.on and not self.look('empty_check'):
                break
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
        self.note('release_time' if d == 'REL' else 'capture_time', at=time.strftime('%Y-%m-%d %H:%M:%S'), clock_ok=self.clock_ok)   # clock_ok False면 시각을 믿지 말 것
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
