# -*- coding: utf-8 -*-
"""제어 순서 시뮬레이션 (서현, 2026-11-02, CAP-AI-22) — D5e 기준

Pi 상태 머신의 '참고 구현'을, 가짜 UNO 1·UNO 2·카메라·말벌로 시험한다. 실제 하드웨어 코드가 아니다.
- Pi 쪽 코드(PiFSM)는 실제로 쓸 순서 그대로 썼다: 명령 줄을 보내고, OK·DONE·EVT 줄을 기다린다.
  시리얼 대신 가짜 장치에 붙여 시간을 빨리 돌린다 (이벤트 시뮬레이션, 실제 시간 아님).
- 가짜 UNO 1은 지금 펌웨어(trap_controller.ino) 명령 + 제안 명령(HOME, DONE PEN, X·Y는 펜 들었을 때만)을 흉내 낸다.
- 가짜 UNO 2는 제안 프로토콜(문틈 규칙, 게이트 이벤트, SELFTEST, STATUS, 감시)을 흉내 낸다.
- 말벌은 정해진 행동표(시나리오)대로 움직인다.

실행:  python design/control_sim/trap_sim.py          → 시나리오 15개, 안전 규칙 검사, out/sim_results.json, out/S1_timeline.json
       python design/control_sim/trap_sim.py S1_nominal → 하나만, 메시지 기록 출력
값의 근거는 design/2026-11-02_전기계통_제어순서_서현.md 표를 본다. 시간값 대부분은 [추측]이고 J6·행동 시험에서 고친다.
"""
import heapq
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import elec_budget as EB  # noqa: E402

OUT = os.path.join(HERE, "out")
os.makedirs(OUT, exist_ok=True)

# ---------------------------------------------------------------------------
# 값 (근거)
# ---------------------------------------------------------------------------
PRM = dict(
    v_mm_s=1.96,          # 28BYJ-48 + T8, 반걸음 1000 µs (지금 펌웨어 기본값) [확실 — 펌웨어]
    door_s=0.2,           # MG90S 0.1 s/60°, 120° [확실 — 사양·S4 M7]
    gap_clear_s=0.2,      # 문틈 게이트가 이만큼 비어야 닫기 시작 [가능성 높음 — 제어 통합 정리 4장]
    retry_wait_s=1.0, retry_max=3,
    debounce_s=0.003,     # 1 ms마다 읽고 3번 같으면 인정 [가능성 높음]
    pen_up_s=0.15, pen_down_s=0.27,   # SG90 0.1 s/60°, 내리기 2단계 (마지막 2 mm ≤ 60 °/s) [가능성 높음]
    dwell_s=0.3,          # 펜이 닿아 있는 시간 [추측 — 마킹 시험 전]
    look_s=0.6,           # 촬영 + 추론 (5장) [추측]
    feed_s=60.0,          # 급이·건조 (샤피 건조 시간 시험 전) [추측]
    press_g=51.0,         # F_p 0.5 N = 51 g [확실 — D6]
    F_max=36.5, F_feed=10.0, F_retract=10.0,
    hornet_h=7.5,         # 말벌 등 높이 [가능성 높음 — D6]
    park=(65.0, -40.0), X_lim=(37.0, 73.0), Y_lim=(-40.0, 18.0),   # D5e 마커 범위 (cad/D5e_check.py) [확실 — 모델]
    thorax_p_min=0.6, pose_retry_max=3, mark_retry_max=1,
    T_enter_s=60.0, T_light_s=60.0, T_alert_s=120.0, T_fallback_s=300.0,
    clock_start_h=12.0,   # 시뮬레이션 시작 시각 (정오)
    sunrise_h=7.0, sunset_h=17.5,   # 공주 11월 초 해 뜸·짐 근사 [가능성 높음] — Pi는 날짜로 계산
    hb_period_s=0.5, hb_timeout_s=1.5, uno_watchdog_s=2.0,
    door_beams=2,         # 문틈 빔 수 (비교용: 1이면 옛 설계 — 통로 쪽 빔 하나만 봄)
    classes=("velutina", "crabro"),   # 분류는 등검은말벌·유럽말벌 2종만 (서현 11/02 09:25) — VespAI와 같은 2종
    crabro_action="isolate",   # 유럽말벌 → 격리 (서현 결정 11/06 17:05)
    other_action="isolate",    # 2종 아님·신뢰도 낮음 → 격리 (서현 결정 11/06 17:05)
    gyne_mw_mm=4.4,            # 중순판 폭(날개 뿌리 사이) ≥ 4.4 mm → 여왕벌(gyne)로 보고 격리. 논문 경계 4.5, 불확실 띠 4.4~4.58의 아래 끝
                               #   (Pérez-de-Heredia et al. 2017, J Hymenopt Res 60:119) — (AI 판단, 서현 위임) CAP-AI-24
    month=7,                   # 오늘 달 (Pi 시계). 폭을 못 재면 계절 규칙 (서현 결정 11/06 18:32)
    season_queen_months=(3, 4, 5, 9, 10, 11),   # 3~5월 창업 여왕만 다님, 9~11월 신여왕 나옴 → 못 재면 여왕으로 봄. 6~8월 → 일벌
    control_mode=False,        # 방제 모드 (등검은말벌 일벌도 격리)
)
CONTACT_F = PRM["F_max"] - PRM["hornet_h"]      # 바닥이 말벌 등에 닿는 높이 29.0 mm (격자 아래 면 기준)
GAP = {"IN": ("G2", "G2b"), "CAP": ("G3", "G3b"), "REL": ("G5", "G5b")}   # 문마다 빔 2개 (지나가는 방향 순서: 앞, 뒤) — 서현 11/02 결정
GATES = ("G1", "G2", "G2b", "G3", "G3b", "G4", "G5", "G5b", "G6")
PAIR = {g: (d, i) for d, pr in GAP.items() for i, g in enumerate(pr)}
WALK = dict(gate=1.4, tube_in=5.0, tube_cap=10.0, tube_rel=4.0)   # 몸길이 25 mm + 빔 3 mm ÷ 20 mm/s, 통로 걷기 [추측]


class Fault(Exception):
    pass


# ---------------------------------------------------------------------------
# 이벤트 시뮬레이터 + 발생기 프로세스
# ---------------------------------------------------------------------------
class Sim:
    def __init__(self):
        self.t, self.q, self.n = 0.0, [], 0

    def at(self, dt, fn, *a):
        heapq.heappush(self.q, (self.t + max(dt, 0.0), self.n, fn, a))
        self.n += 1

    def run(self, until):
        while self.q and self.q[0][0] <= until:
            t, _, fn, a = heapq.heappop(self.q)
            self.t = t
            fn(*a)
        self.t = until


class Proc:
    """('sleep', dt) 또는 ('wait', pred, timeout)을 yield. wait는 offer(msg)로 깨움, 시간 넘으면 None."""

    def __init__(self, sim, gen, on_fault=None):
        self.sim, self.gen, self.on_fault = sim, gen, on_fault
        self.tok, self.wait, self.alive = 0, None, True
        sim.at(0, self._resume, 0, None)

    def kill(self):
        self.alive, self.wait = False, None
        self.tok += 1
        try:
            self.gen.close()
        except Exception:
            pass

    def _resume(self, tok, val):
        if not self.alive or tok != self.tok:
            return
        self.wait = None
        try:
            req = self.gen.send(val)
        except StopIteration:
            self.alive = False
            return
        except Fault as e:
            self.alive = False
            if self.on_fault:
                self.on_fault(str(e))
            return
        self.tok += 1
        tok = self.tok
        if req[0] == "sleep":
            self.sim.at(req[1], self._resume, tok, None)
        else:
            self.wait = (req[1], tok)
            if req[2] is not None:
                self.sim.at(req[2], self._resume, tok, None)

    def offer(self, msg):
        if self.alive and self.wait and self.wait[0](msg):
            tok = self.wait[1]
            self.wait = None
            self.sim.at(0, self._resume, tok, msg)
            return True
        return False


class Rec:
    """상태 바뀜 기록 (그림·전력·안전 규칙 검사용)."""

    def __init__(self, sim):
        self.sim, self.ch, self.now, self.events = sim, [], {}, []

    hooks = None

    def set(self, k, v):
        if self.now.get(k) != v:
            self.now[k] = v
            self.ch.append((round(self.sim.t, 4), k, v))
            for hk in list(self.hooks or []):        # (키, 값, 지연, 함수) — 한 번만
                if hk[0] == k and hk[1] == v:
                    self.hooks.remove(hk)
                    self.sim.at(hk[2], hk[3])

    def ev(self, kind, **kw):
        self.events.append(dict(t=round(self.sim.t, 3), kind=kind, **kw))


# ---------------------------------------------------------------------------
# 세상 (말벌·게이트)
# ---------------------------------------------------------------------------
class Hornet:
    def __init__(self, hid, t=60.0, species="velutina", caste="worker", marked=False, poses=("dorsal",), dots=(True,),
                 gap_dwell=0.3, gap_returns=(), turn_back=False, leave_s=20.0, cam_miss_s=0.0, mw_mm=None):
        self.id, self.t_arrive, self.species, self.caste, self.marked = hid, t, species, caste, marked
        self.mw_mm = 4.0 if mw_mm == "fail" else mw_mm if mw_mm is not None else (4.7 if caste == "queen" else 4.0)   # 중순판 폭 (카메라가 잼)
        self.mw_measurable = mw_mm != "fail"                                                # False면 격자에 가려 못 잼
        self.poses, self.dots, self.gap_dwell, self.gap_returns, self.turn_back = list(poses), list(dots), gap_dwell, list(gap_returns), turn_back
        self.leave_s, self.cam_miss_s = leave_s, cam_miss_s
        self.zone, self.press_n, self.mark_n, self.t_chamber = "trap", 0, 0, None
        self.pinned = False
        self.marked_now = False


class World:
    def __init__(self, sim, rec, gate_fault=None):
        self.sim, self.rec = sim, rec
        self.blk = {g: set() for g in GATES}
        self.gap_occ = {d: set() for d in GAP}      # 문판 평면에 몸이 걸쳐 있는 말벌 (끼임 판정)
        self.batt_low = False
        self.gate_fault = gate_fault or {}
        self.hornets, self.uno1, self.uno2, self.pi = [], None, None, None
        for g in self.blk:
            rec.set("gate_" + g, 0)

    def pi_msg(self, src, line):
        if self.pi is not None and self.pi.alive:
            self.pi.on_msg(src, line)

    def raw(self, g, emit_on=True):
        """수신부 출력: True = 끊김(LOW). 수신부가 죽으면 풀업 때문에 늘 '안 끊김'으로 읽힘."""
        f = self.gate_fault.get(g)
        if f == "stuck_clear":
            return False
        if not emit_on or f == "stuck_blocked":
            return True
        return bool(self.blk[g])

    def block(self, g, h, on):
        before = self.raw(g)
        (self.blk[g].add if on else self.blk[g].discard)(h.id)
        after = self.raw(g)
        self.rec.set("gate_" + g, 1 if self.blk[g] else 0)
        if before != after and self.uno2:
            self.sim.at(PRM["debounce_s"], self.uno2.gate_change, g, after)

    def in_chamber(self):
        return [h for h in self.hornets if h.zone == "chamber"]

    def cross(self, h, g, dwell=None):
        self.block(g, h, True)
        yield ("sleep", WALK["gate"] if dwell is None else dwell)
        self.block(g, h, False)

    def cross_door(self, h, d, forward=True, both=0.3):
        """문 빔 두 개를 차례로 지남: 앞 빔 → (둘 다) → 뒤 빔. 문판 평면은 두 빔 사이 (각 2 mm)."""
        a, b = GAP[d] if forward else GAP[d][::-1]
        self.block(a, h, True)
        yield ("sleep", 0.15)
        self.gap_occ[d].add(h.id)
        yield ("sleep", 0.2)
        self.block(b, h, True)
        yield ("sleep", 0.7 + both)
        self.block(a, h, False)
        yield ("sleep", 0.15)
        self.gap_occ[d].discard(h.id)
        yield ("sleep", 0.2)
        self.block(b, h, False)

    def hornet_proc(self, h):
        u2 = self.uno2
        yield ("sleep", h.t_arrive)
        yield from self.cross(h, "G1")
        h.zone = "tube_in"
        yield ("sleep", WALK["tube_in"])
        if h.turn_back:
            yield from self.cross(h, "G1")
            h.zone = "trap"
            self.rec.ev("hornet", id=h.id, what="turned_back")
            return
        h.zone = "at_G2"
        self.block("G2", h, True)                  # 닫힌 입구 문 앞에서는 바깥 빔 G2를 막고 기다림
        while u2.door["IN"]["pos"] != "open":
            yield ("sleep", 0.1)
        yield ("sleep", 0.15)
        self.gap_occ["IN"].add(h.id)
        yield ("sleep", 0.2)
        self.block("G2b", h, True)
        yield ("sleep", 0.7 + h.gap_dwell)
        self.block("G2", h, False)
        yield ("sleep", 0.15)
        self.gap_occ["IN"].discard(h.id)
        yield ("sleep", 0.2)
        self.block("G2b", h, False)
        h.zone, h.t_chamber = "chamber", self.sim.t
        for dur in h.gap_returns:      # 문이 닫히기 시작할 때마다 마킹실 쪽에서 머리만 문틈에 넣음 (안쪽 빔 G2b만 막힘)
            t0 = self.sim.t
            while u2.door["IN"]["pos"] != "closing" and self.sim.t - t0 < 60:
                yield ("sleep", 0.01)
            h.zone = "at_G2"
            self.gap_occ["IN"].add(h.id)
            self.block("G2b", h, True)
            yield ("sleep", dur)
            self.block("G2b", h, False)
            self.gap_occ["IN"].discard(h.id)
            h.zone = "chamber"
        # 마킹실: 나갈 길을 기다림
        while True:
            yield ("sleep", 0.1)
            if h.pinned:
                continue
            rel, cap = u2.door["REL"], u2.door["CAP"]
            if rel["pos"] == "open" and self.sim.t - rel["t_open"] >= h.leave_s:
                yield from self.cross_door(h, "REL")
                h.zone = "tube_rel"
                yield ("sleep", WALK["tube_rel"])
                yield from self.cross(h, "G6")
                h.zone = "outside"
                return
            if cap["pos"] == "open" and self.sim.t - cap["t_open"] >= min(h.leave_s, 15.0) + 5.0 * self.order(h):
                yield from self.cross_door(h, "CAP")
                h.zone = "tube_cap"
                yield ("sleep", WALK["tube_cap"])
                yield from self.cross(h, "G4")
                h.zone = "captured"
                return

    def order(self, h):
        ids = [x.id for x in self.in_chamber()]
        return ids.index(h.id) if h.id in ids else 0

    # 카메라 (Pi가 직접 부름)
    def observe(self):
        seen = [h for h in self.in_chamber() if self.sim.t - (h.t_chamber or 0) >= h.cam_miss_s]
        out = []
        for h in seen:
            pose = h.poses[min(max(h.press_n - 1, 0), len(h.poses) - 1)] if h.pinned else "free"
            sp = h.species if h.species in PRM["classes"] else "uncertain"     # 2종 분류기: 다른 곤충은 낮은 신뢰도
            if not h.mw_measurable:                                          # 못 잼 → 계절 규칙 (서현 11/06)
                caste = "queen" if PRM["month"] in PRM["season_queen_months"] else "worker"
            else:
                caste = "queen" if h.mw_mm >= PRM["gyne_mw_mm"] else "worker"   # 카메라는 크기로만 가름
            out.append(dict(id=h.id, species=sp, caste=caste, mw_mm=h.mw_mm, marked=h.marked or h.marked_now,
                            pose=pose, p=0.9 if pose in ("dorsal", "free") else 0.1))
        return out


# ---------------------------------------------------------------------------
# 가짜 UNO 1 (움직임) — 지금 펌웨어 + 제안 (HOME, DONE PEN, 펜 내림 중 X·Y 금지, HOLD F 0)
# ---------------------------------------------------------------------------
class Uno1:
    def __init__(self, sim, world, rec):
        self.sim, self.w, self.rec = sim, world, rec
        self.pos = dict(F=0.0, X=PRM["park"][0], Y=PRM["park"][1])
        self.power_on(first=True)

    def power_on(self, first=False):
        self.alive, self.homed, self.hold = True, False, dict(F=False, X=False, Y=False)
        self.mv = {}            # 축 → (목표, 끝 시각, 토큰)
        self.tok, self.wd, self.last = 0, 0.0, self.sim.t
        self.pen = "limp" if not first else "down"   # 켤 때 서보를 붙이지 않음 (제안) — 펜은 무게로 내려앉아 있음
        self.pen_busy_until = 0.0
        self.press = None
        for a in "FXY":
            self.rec.set("ax_" + a, "off")
        self.rec.set("pen", "detached")
        self.rec.set("pen_pos", "down")
        self.rec.set("u1_power", 1)
        self.sim.at(0.3, self.send, "EVT READY uno1 v0.2-sim")
        if first:
            self.sim.at(0.1, self.tick)

    def power_off(self):
        self.alive = False
        self.tok += 1
        self.mv.clear()
        self.press = None
        for a in "FXY":
            self.rec.set("ax_" + a, "off")
        if self.pen == "up":
            self.rec.ev("pen_drop", over_chamber=self.pos["Y"] > -20.5, pinned=any(h.pinned for h in self.w.hornets))
        self.pen = "limp"
        self.rec.set("pen", "detached")
        self.rec.set("pen_pos", "down")
        self.rec.set("u1_power", 0)

    def send(self, line):
        if self.alive:
            self.sim.at(0.002, self.w.pi_msg, "U1", line)

    def recv(self, line):
        if not self.alive:
            return
        self.last = self.sim.t
        tk = line.split()
        c = tk[0]
        if c == "PING":
            return self.send("OK PONG")
        if c == "WATCHDOG":
            self.wd = float(tk[1])
            return self.send("OK WATCHDOG")
        if c == "HOLD":
            self.hold[tk[1]] = tk[2] == "1"
            self._coil(tk[1])
            return self.send("OK HOLD")
        if c in ("LIMIT", "SPEED", "TARE", "CAL"):
            return self.send("OK " + c)
        if c == "STOP":
            self._stop_all()
            return self.send("OK STOP")
        if c == "PEN":
            return self._pen(tk[1])
        if c == "HOME":
            return self._home(tk[1])
        if c == "MOVE":
            a, mm = tk[1], float(tk[2])
            if not self.homed:
                return self.send("ERR NOT_HOMED")
            if a in "XY" and self.pen != "up":
                return self.send("ERR PEN_DOWN")
            self.send("OK MOVE %s %.3f" % (a, mm))
            return self._move(a, mm, "MOVE")
        if c == "PRESS":
            if not self.homed:
                return self.send("ERR NOT_HOMED")
            self.press = float(tk[1])
            self.send("OK PRESS")
            hs = self.w.in_chamber()
            stop = CONTACT_F + 0.3 if hs else PRM["F_max"]
            return self._move("F", stop, "PRESS", hornets=hs)
        self.send("ERR UNKNOWN")

    def _coil(self, a):
        self.rec.set("ax_" + a, "move" if a in self.mv else ("hold" if self.hold[a] else "off"))

    def _move(self, a, mm, kind, hornets=()):
        if a in "XY" and self.pen_busy_until > self.sim.t:
            self.rec.ev("violation", what="XY while pen moving")
        d = abs(mm - self.pos[a])
        dt = d / PRM["v_mm_s"]
        self.tok += 1
        self.mv[a] = (mm, self.sim.t + dt, self.tok, self.pos[a])
        self._coil(a)
        if a == "F":
            for h in self.w.hornets:
                h.pinned = False
        self.sim.at(dt, self._arrive, a, self.tok, kind, list(hornets))

    def _arrive(self, a, tok, kind, hornets):
        if not self.alive or a not in self.mv or self.mv[a][2] != tok:
            return
        self.pos[a] = self.mv.pop(a)[0]
        self._coil(a)
        if kind == "PRESS":
            if hornets:
                for h in hornets:
                    h.pinned, h.press_n = True, h.press_n + 1
                self.send("DONE PRESS %.3f %.1f" % (self.pos["F"], self.press + 2.0))
            else:
                self.send("DONE PRESS LIMIT %.3f 0.0" % self.pos["F"])
            self.press = None
        elif kind.startswith("HOME"):
            self.sim.at(0, self._home_next, kind)
        elif kind == "WD":
            pass
        else:
            self.send("DONE MOVE %s %.3f" % (a, self.pos[a]))

    def _stop_all(self):
        for a in list(self.mv):
            m = self.mv.pop(a)
            frac = 1.0 - max(0.0, m[1] - self.sim.t) / max(1e-9, m[1] - (m[1] - abs(m[0] - m[3]) / PRM["v_mm_s"]))
            self.pos[a] = m[3] + (m[0] - m[3]) * min(1.0, max(0.0, frac))
            self._coil(a)
        self.press = None

    def _pen(self, s):
        if s == "DOWN" and any(a in self.mv for a in "XY"):
            return self.send("ERR XY_MOVING")
        self.send("OK PEN")
        dt = PRM["pen_up_s"] if s == "UP" else PRM["pen_down_s"]
        self.pen = "moving"
        self.pen_busy_until = self.sim.t + dt
        self.rec.set("pen", "move")
        self.sim.at(dt, self._pen_done, s, self.tok)

    def _pen_done(self, s, tok):
        if not self.alive:
            return
        self.pen = s.lower()
        self.rec.set("pen", "idle")
        self.rec.set("pen_pos", self.pen)
        if self.pen == "down":
            for h in self.w.hornets:
                if h.pinned and self.pos["Y"] > -20.5:
                    h.mark_n += 1
                    ok = h.dots[min(h.mark_n - 1, len(h.dots) - 1)]
                    if ok:
                        h.marked_now = True
        self.send("DONE PEN " + s)

    def _home(self, which):
        if self.pen != "up":
            return self.send("ERR PEN_DOWN")
        self.send("OK HOME")
        self._home_queue = ["F", "XY"] if which == "ALL" else [which]
        self.sim.at(0, self._home_next, "HOME")

    def _home_next(self, kind):
        if not self.alive:
            return
        if kind == "HOME_XY" and any(a in self.mv for a in "XY"):
            return
        if not self._home_queue:
            self.homed = True
            return self.send("DONE HOME ALL")
        step = self._home_queue.pop(0)
        if step == "F":
            self._home_axis("F", 0.0, "HOME_F")
        else:
            self._home_axis("X", PRM["X_lim"][0], "HOME_XY")
            self._home_axis("Y", PRM["Y_lim"][0], "HOME_XY")

    def _home_axis(self, a, sw, kind):
        d = abs(self.pos[a] - sw) + 2.0 + 2.0 * 2      # 스위치까지 + 2 mm 물러났다 반 속도로 다시 [가능성 높음]
        self.tok += 1
        self.mv[a] = (sw, self.sim.t + d / PRM["v_mm_s"], self.tok, self.pos[a])
        self._coil(a)
        if a == "F":
            for h in self.w.hornets:
                h.pinned = False
        self.sim.at(d / PRM["v_mm_s"], self._arrive, a, self.tok, kind, [])

    def tick(self):
        if self.alive and self.wd and self.sim.t - self.last > self.wd:
            self._stop_all()
            if self.pen != "up":
                self._pen("UP")
            if self.homed and self.pos["F"] > PRM["F_retract"] and "F" not in self.mv:     # 누르던 힘을 풂 (제안)
                self.sim.at(PRM["pen_up_s"] + 0.05, self._move, "F", self.pos["F"] - PRM["F_retract"], "WD")
            self.send("EVT WATCHDOG_STOP")
            self.rec.ev("uno1_watchdog")
            self.last = self.sim.t
        self.sim.at(0.1, self.tick)


# ---------------------------------------------------------------------------
# 가짜 UNO 2 (문·게이트·조명) — 제안 프로토콜
# ---------------------------------------------------------------------------
class Uno2:
    def __init__(self, sim, world, rec, init=None):
        self.sim, self.w, self.rec = sim, world, rec
        init = init or dict(IN="open", CAP="closed", REL="closed")
        self.door = {d: dict(pos=init[d], att=False, tok=0, retry=0, want=None, t_open=-1e9) for d in GAP}
        self.clear_since = {g: 0.0 for g in self.w.blk}
        self.emit = True
        self.power_on()

    def power_on(self):
        self.alive, self.wd, self.last = True, 0.0, self.sim.t
        for d in GAP:
            self.door[d]["att"] = False
            self.rec.set("srv_" + d, "detached")
            self.rec.set("door_" + d, self.door[d]["pos"])
        for k in ("TOP", "BOT", "EXIT"):
            self.rec.set("L_" + k, 0)
        self.rec.set("emit", 1)
        self.sim.at(0.3, self.send, "EVT READY uno2 v0.1-sim")
        self.sim.at(0.1, self.tick)

    def send(self, line):
        if self.alive:
            self.sim.at(0.002, self.w.pi_msg, "U2", line)

    def ms(self):
        return int(self.sim.t * 1000)

    def gate_change(self, g, blocked):
        if not blocked:
            self.clear_since[g] = self.sim.t
        self.send("EVT GATE %s %s %d" % (g[1:], "BLOCK" if blocked else "CLEAR", self.ms()))
        for d, pr in GAP.items():
            st = self.door[d]
            if g in pr[:PRM["door_beams"]] and blocked and st["pos"] == "closing":      # 닫는 중 두 빔 중 하나라도 막힘 → 바로 다시 열기
                self.rec.ev("door_reverse", door=d)
                self._go(d, "open", reason="reverse")
                st["retry"] += 1
                if st["retry"] >= PRM["retry_max"]:
                    st["want"] = None
                    self.send("EVT DOOR %s BLOCKED" % d)
                else:
                    self.send("EVT DOOR %s RETRY %d" % (d, st["retry"]))
                    self.sim.at(PRM["door_s"] + PRM["retry_wait_s"], self._try_close, d, st["tok"])

    def recv(self, line):
        if not self.alive:
            return
        self.last = self.sim.t
        tk = line.split()
        c = tk[0]
        if c == "PING":
            return self.send("OK PONG")
        if c == "WATCHDOG":
            self.wd = float(tk[1])
            return self.send("OK WATCHDOG")
        if c == "LIGHT":
            self.rec.set("L_" + tk[1], int(tk[2]))
            return self.send("OK LIGHT")
        if c == "STATUS":
            s = " ".join("%s=%s" % (d, self.door[d]["pos"].upper() if self.door[d]["att"] else "UNKNOWN") for d in GAP)
            bits = "".join("1" if self.w.raw(g, self.emit) else "0" for g in sorted(self.w.blk))
            return self.send("OK STATUS %s GATES=%s RAIL=1" % (s, bits))
        if c == "SELFTEST":
            off = [g for g in sorted(self.w.blk) if not self.w.raw(g, emit_on=False)]   # 송신을 끄면 모두 끊겨야 함
            on = [g for g in sorted(self.w.blk) if self.w.raw(g, emit_on=True)]          # 켜면 모두 이어져야 함
            if off:
                return self.send("ERR SELFTEST %s STUCK_CLEAR" % ",".join(off))
            if on:
                return self.send("ERR SELFTEST %s BLOCKED" % ",".join(on))
            return self.send("OK SELFTEST")
        if c == "DOOR":
            d, s = tk[1], tk[2]
            st = self.door[d]
            self.send("OK DOOR")
            if s == "OPEN":
                st["want"], st["retry"] = None, 0
                return self._go(d, "open")
            st["want"], st["retry"] = "closed", 0
            if st["pos"] == "closed" and st["att"]:
                return self.send("EVT DOOR %s CLOSED %d" % (d, self.ms()))
            return self._try_close(d, st["tok"])
        self.send("ERR UNKNOWN")

    def _try_close(self, d, tok):
        st = self.door[d]
        if not self.alive or st["want"] != "closed" or tok != st["tok"]:
            return
        if any(self.w.raw(g) or self.sim.t - self.clear_since[g] < PRM["gap_clear_s"] for g in GAP[d][:PRM["door_beams"]]) or self._busy(d):
            self.sim.at(0.01, self._try_close, d, tok)
            return
        self._go(d, "closed")

    def _busy(self, d):
        """다른 문 서보가 움직이는 중인가 — 서보는 한 번에 하나 (전류 규칙, UNO 2가 스스로 지킴)."""
        return any(st["pos"] in ("opening", "closing") for dd, st in self.door.items() if dd != d)

    def _go(self, d, target, reason=""):
        if self._busy(d):
            self.sim.at(0.01, self._go, d, target, reason)
            return
        st = self.door[d]
        st["tok"] += 1
        st["att"] = True
        st["pos"] = "closing" if target == "closed" else "opening"
        self.rec.set("door_" + d, st["pos"])
        self.rec.set("srv_" + d, "move")
        self.sim.at(PRM["door_s"], self._arrive, d, target, st["tok"])

    def _arrive(self, d, target, tok):
        st = self.door[d]
        if not self.alive or tok != st["tok"]:
            return
        st["pos"] = target
        self.rec.set("door_" + d, target)
        self.rec.set("srv_" + d, "idle")
        self.sim.at(0.5, self._detach, d, tok)
        if target == "closed":
            if self.w.gap_occ[d]:
                self.rec.ev("crush", door=d)
            st["want"] = None
            self.send("EVT DOOR %s CLOSED %d" % (d, self.ms()))
        else:
            st["t_open"] = self.sim.t
            self.send("EVT DOOR %s OPEN %d" % (d, self.ms()))

    def power_off(self):
        """Pi가 꺼지면 USB 전원이 끊겨 UNO 2도 꺼짐: 서보 신호 없음(문은 그 자리), 송신·조명 꺼짐."""
        self.alive = False
        for d in GAP:
            self.rec.set("srv_" + d, "detached")
        for k in ("TOP", "BOT", "EXIT"):
            self.rec.set("L_" + k, 0)
        self.rec.set("emit", 0)

    def _detach(self, d, tok):
        if self.alive and self.door[d]["tok"] == tok:
            self.rec.set("srv_" + d, "detached")      # 멈춘 뒤 0.5 s 신호 끊기 (기어 마찰로 자리 유지)

    def tick(self):
        if self.alive and self.wd and self.sim.t - self.last > self.wd:
            for d, st in self.door.items():
                st["want"] = None
                if st["pos"] == "closing":
                    self._go(d, "open", reason="watchdog")
            self.send("EVT WATCHDOG_HOLD")
            self.rec.ev("uno2_watchdog")
            self.last = self.sim.t
        self.sim.at(0.1, self.tick)


# ---------------------------------------------------------------------------
# Pi 상태 머신 (참고 구현)
# ---------------------------------------------------------------------------
class Ledger:
    """통로마다 들어감 − 나감. 문은 빔 2개의 순서로 방향을 앎 (앞 → 뒤 = 정방향, 뒤 → 앞 = 역방향, 같은 빔으로 빠지면 되돌아감)."""

    def __init__(self):
        self.n = dict(tube_in=0, chamber=0, tube_cap=0, tube_rel=0, captured=0, released=0)
        self.on = set()
        self.pair = {d: dict(on=set(), first=None) for d in GAP}
        self.out_pending = 0

    def gate(self, g, blocked):
        """빔 사건 하나 → 장부가 바뀌었으면 True."""
        if g in PAIR:
            d, i = PAIR[g]
            st = self.pair[d]
            if blocked:
                if not st["on"]:
                    st["first"] = i
                st["on"].add(i)
                return False
            st["on"].discard(i)
            if st["on"] or st["first"] is None:
                return False
            first, st["first"] = st["first"], None
            if first == i:
                return False                       # 같은 쪽으로 빠짐 = 문틈에 들어왔다 되돌아감
            return self.door_pass(d, forward=(first == 0))
        if blocked:
            self.on.add(g)
            return False
        if g not in self.on:
            return False
        self.on.discard(g)
        n = self.n
        if g == "G1":
            if self.out_pending > 0 and n["tube_in"] > 0:
                n["tube_in"] -= 1
                self.out_pending -= 1
            else:
                n["tube_in"] += 1
        elif g == "G4" and n["tube_cap"] > 0:
            n["tube_cap"] -= 1
            n["captured"] += 1
        elif g == "G6" and n["tube_rel"] > 0:
            n["tube_rel"] -= 1
            n["released"] += 1
        else:
            return False
        return True

    def door_pass(self, d, forward):
        n = self.n
        src, dst = {"IN": ("tube_in", "chamber"), "CAP": ("chamber", "tube_cap"), "REL": ("chamber", "tube_rel")}[d]
        if not forward:
            src, dst = dst, src
        n[src] = max(0, n[src] - 1)
        n[dst] += 1
        if d == "IN" and not forward:
            self.out_pending += 1
        return True


class PiFSM:
    def __init__(self, sim, world, rec, log):
        self.sim, self.w, self.rec, self.log = sim, world, rec, log
        self.alive = True
        self.ledger = Ledger()
        self.inbox = []
        self.last_pong = dict(U1=sim.t, U2=sim.t)
        self.ready = dict(U1=False, U2=False)
        self.notes = []
        self.main = None
        self.hb = Proc(sim, self.heartbeat())
        self.state("BOOT")

    # ---- 바탕 ----
    def state(self, s):
        self.rec.set("fsm", s)
        busy = s not in ("IDLE", "FEED", "FAULT_WAIT", "OFF")
        self.rec.set("pi", "active" if busy else "idle")

    def note(self, kind, **kw):
        self.notes.append(dict(t=round(self.sim.t, 2), kind=kind, **kw))

    def start(self, gen):
        if self.main:
            self.main.kill()
        self.main = Proc(self.sim, gen, on_fault=self.fault)

    def send(self, u, line):
        if not self.alive:
            return
        self.log.append((round(self.sim.t, 3), "PI", u, line))
        dev = self.w.uno1 if u == "U1" else self.w.uno2
        self.sim.at(0.002, dev.recv, line)

    def on_msg(self, src, line):
        if not self.alive:
            return
        self.log.append((round(self.sim.t, 3), src, "PI", line))
        tk = line.split()
        if line == "OK PONG":
            self.last_pong[src] = self.sim.t
            return
        if tk[0] == "EVT" and tk[1] == "READY":
            self.ready[src] = True
            self.last_pong[src] = self.sim.t
        if tk[0] == "EVT" and tk[1] == "GATE":
            g = "G" + tk[2]
            if self.ledger.gate(g, tk[3] == "BLOCK"):
                self._deliver(("PI", "LEDGER %s" % g))
        self._deliver((src, line))

    def _deliver(self, msg):
        if self.main and self.main.offer(msg):
            return
        self.inbox.append(msg)
        del self.inbox[:-40]

    def flush(self):
        self.inbox.clear()

    def wait(self, pred, timeout):
        for i, m in enumerate(self.inbox):
            if pred(m):
                del self.inbox[i]
                return m
        m = yield ("wait", lambda x: x[1].startswith("FAULT") or pred(x), timeout)
        if m and m[1].startswith("FAULT"):
            raise Fault(m[1])
        return m

    def cmd(self, u, line, timeout=1.0):
        word = line.split()[0]
        self.send(u, line)
        m = yield from self.wait(lambda x: x[0] == u and (x[1].startswith("OK " + word) or x[1].startswith("ERR")), timeout)
        if m is None:
            raise Fault("NO_REPLY %s %s" % (u, line))
        if m[1].startswith("ERR"):
            raise Fault("%s %s -> %s" % (u, line, m[1]))
        return m[1]

    def done(self, pats, timeout):
        """pats: 'DONE MOVE X' 같은 앞부분 목록 — 모두 올 때까지."""
        got, left, t_end = {}, list(pats), self.sim.t + timeout
        while left:
            m = yield from self.wait(lambda x: any(x[1].startswith(p) for p in left), max(0.0, t_end - self.sim.t))
            if m is None:
                raise Fault("TIMEOUT %s" % ",".join(left))
            p = next(p for p in left if m[1].startswith(p))
            got[p] = m[1]
            left.remove(p)
        return got

    def look(self, what):
        self.rec.set("hat", "run")
        yield ("sleep", PRM["look_s"])
        self.rec.set("hat", "idle")
        obs = self.w.observe()
        self.rec.ev("look", what=what, n=len(obs))
        return obs

    def move_t(self, d):
        return d / PRM["v_mm_s"] + 5.0

    def heartbeat(self):
        self.batt_low = False
        while self.alive:
            if self.w.batt_low and not self.batt_low:     # INA226 (배터리 상자) — 남은 에너지가 기준 아래
                self.batt_low = True
                self.note("battery_low")
            for u in ("U1", "U2"):
                self.send(u, "PING")
            yield ("sleep", PRM["hb_period_s"])
            for u in ("U1", "U2"):
                if self.ready[u] and self.sim.t - self.last_pong[u] > PRM["hb_timeout_s"]:
                    self.ready[u] = False
                    self.fault("HEARTBEAT %s" % u)

    def fault(self, reason):
        if not self.alive:
            return
        self.note("fault", reason=reason)
        self.state("FAULT")
        if self.main:
            self.main.kill()
        self.start(self.recover(reason))

    # ---- 순서 ----
    def boot(self):
        self.state("BOOT")
        t_end = self.sim.t + 5.0
        while not (self.ready["U1"] and self.ready["U2"]):
            m = yield from self.wait(lambda x: x[1].startswith("EVT READY"), max(0.0, t_end - self.sim.t))
            if m is None:
                raise Fault("NO_READY")
        yield from self.init_uno2()
        for d in ("IN", "CAP", "REL"):            # 켤 때 문 상태를 모름 → 먼저 모두 닫음 (문틈 규칙) — 원점 찾는 동안 못 들어오게
            yield from self.close_door(d)
        yield from self.init_uno1()
        yield from self.resume()

    def init_uno2(self):
        yield from self.cmd("U2", "WATCHDOG %g" % PRM["uno_watchdog_s"])
        r = yield from self.cmd("U2", "SELFTEST")
        self.note("selftest", reply=r)

    def init_uno1(self):
        self.state("HOME")
        yield from self.cmd("U1", "WATCHDOG %g" % PRM["uno_watchdog_s"])
        yield from self.cmd("U1", "HOLD F 0")
        self.flush()
        yield from self.cmd("U1", "PEN UP")
        yield from self.done(["DONE PEN UP"], 2)
        yield from self.cmd("U1", "HOME ALL")
        yield from self.done(["DONE HOME ALL"], 120)
        yield from self.cmd("U1", "LIMIT X %g %g" % PRM["X_lim"])
        yield from self.cmd("U1", "LIMIT Y %g %g" % PRM["Y_lim"])
        yield from self.park(pen_down=True)

    def park(self, pen_down):
        self.flush()
        yield from self.cmd("U1", "MOVE X %g" % PRM["park"][0])
        yield from self.cmd("U1", "MOVE Y %g" % PRM["park"][1])
        yield from self.done(["DONE MOVE X", "DONE MOVE Y"], self.move_t(70))
        if pen_down:
            yield from self.cmd("U1", "PEN DOWN")      # 캡 컵 안으로
            yield from self.done(["DONE PEN DOWN"], 2)

    def resume(self):
        """켤 때·고장 뒤: 마킹실에 말벌이 있으면 이어서 처리, 없으면 대기."""
        obs = yield from self.look("resume")
        self.ledger.n["chamber"] = len(obs)
        if obs:
            self.note("resume_with_hornet", n=len(obs))
            yield from self.close_door("IN")
            yield from self.close_door("CAP")
            yield from self.close_door("REL")
            yield from self.process(len(obs))
        yield from self.loop()

    def loop(self):
        while True:
            if self.batt_low:
                return (yield from self.shutdown_safe())
            yield from self.to_idle()
            n = yield from self.wait_entry()
            if n:
                yield from self.process(n)

    def to_idle(self):
        self.state("IDLE")
        yield from self.cmd("U2", "LIGHT TOP 0")
        yield from self.cmd("U2", "LIGHT BOT 255")
        yield from self.close_door("CAP")
        yield from self.close_door("REL")
        yield from self.cmd("U2", "DOOR IN OPEN")
        yield from self.done(["EVT DOOR IN OPEN"], 2)

    def close_door(self, d, tries=3):
        for k in range(tries):
            self.flush()
            yield from self.cmd("U2", "DOOR %s CLOSE" % d)
            m = yield from self.wait(lambda x: x[0] == "U2" and (x[1].startswith("EVT DOOR %s CLOSED" % d) or x[1].startswith("EVT DOOR %s BLOCKED" % d)), 30)
            if m and "CLOSED" in m[1]:
                return
            self.note("door_blocked", door=d, try_=k + 1)
            yield ("sleep", 5.0)
        raise Fault("DOOR_%s_STUCK" % d)

    def wait_entry(self):
        """G2를 지나 마킹실에 들어온 것(장부) 또는 카메라로 확인."""
        t_check = self.sim.t
        while True:
            if self.ledger.n["chamber"] > 0:
                break
            m = yield from self.wait(lambda x: x[1].startswith("LEDGER"), 5.0)
            if m is None and self.batt_low and self.ledger.n["chamber"] == 0:
                return 0
            if m is None:
                obs = yield from self.look("idle_check")
                if self.ledger.n["chamber"] > 0:
                    break
                if obs:
                    self.note("mismatch", what="camera sees hornet, ledger 0")
                    self.ledger.n["chamber"] = len(obs)
                    break
        self.state("ENTRY")
        for k in range(10):                       # 카메라로 확인 (구석에 있으면 못 볼 수 있음)
            obs = yield from self.look("entry")
            if obs or self.ledger.n["chamber"] == 0:
                break
            yield ("sleep", 1.0)
        if not obs:
            self.note("mismatch", what="ledger %d, camera 0 → 문 열어 둠" % self.ledger.n["chamber"])
            self.ledger.n["chamber"] = 0
            return 0
        yield from self.close_door("IN")
        obs = yield from self.look("after_close")
        if len(obs) != self.ledger.n["chamber"]:
            self.note("mismatch", what="ledger %d, camera %d" % (self.ledger.n["chamber"], len(obs)))
            if len(obs) > self.ledger.n["chamber"] and self.ledger.out_pending:
                self.ledger.out_pending -= 1
                self.ledger.n["tube_in"] = max(0, self.ledger.n["tube_in"] - 1)
            self.ledger.n["chamber"] = len(obs)
        return len(obs)

    def process(self, n):
        if n >= 2:
            self.note("decision", what="two_or_more → isolate")
            return (yield from self.isolate())
        self.state("IDENTIFY")
        yield from self.cmd("U2", "LIGHT BOT 0")
        yield from self.cmd("U2", "LIGHT TOP 255")
        obs = yield from self.look("identify")
        if not obs:
            return (yield from self.isolate())
        h = obs[0]
        if h["species"] == "uncertain":            # 2종 분류기가 둘 다 아니라고 봄 (다른 곤충) → 안전한 쪽
            self.note("decision", what="isolate (2종 아님·불확실)")
            return (yield from self.isolate())
        if PRM["control_mode"] or h["caste"] == "queen" or (h["species"] == "crabro" and PRM["crabro_action"] == "isolate"):
            self.note("decision", what="isolate (%s %s)" % (h["species"], h["caste"]))
            return (yield from self.isolate())
        if h["species"] == "crabro":
            self.note("decision", what="release crabro")
            return (yield from self.release())
        if h["marked"]:
            self.note("decision", what="revisit (already marked)")
            yield from self.feed()
            return (yield from self.release())
        ok = yield from self.press_mark()
        self.note("mark_result", ok=ok)
        yield from self.feed()
        yield from self.release()

    def press_mark(self):
        tx, ty = 55.0, 0.0                         # 판별 사진의 흉부 추정 (가짜: 마킹실 가운데)
        for attempt in range(1, PRM["pose_retry_max"] + 1):
            self.state("PRESS")
            self.flush()
            yield from self.cmd("U1", "PEN UP")
            yield from self.done(["DONE PEN UP"], 2)
            yield from self.cmd("U2", "LIGHT TOP 0")
            yield from self.cmd("U2", "LIGHT BOT 255")
            yield from self.cmd("U1", "MOVE X %g" % tx)
            yield from self.cmd("U1", "MOVE Y %g" % ty)
            yield from self.cmd("U1", "PRESS %g" % PRM["press_g"])
            r = yield from self.done(["DONE MOVE X", "DONE MOVE Y", "DONE PRESS"], self.move_t(60))
            if "LIMIT" in r["DONE PRESS"]:
                self.note("press_limit", attempt=attempt)
                yield from self.cmd("U1", "MOVE F 0")
                yield from self.done(["DONE MOVE F"], self.move_t(40))
                continue
            F_now = float(r["DONE PRESS"].split()[2])
            self.state("POSE")
            yield from self.cmd("U2", "LIGHT BOT 0")
            yield from self.cmd("U2", "LIGHT TOP 255")
            obs = yield from self.look("pose")
            if not obs or obs[0]["pose"] != "dorsal" or obs[0]["p"] < PRM["thorax_p_min"]:
                self.note("pose_retry", attempt=attempt, pose=obs[0]["pose"] if obs else None)
                yield from self.cmd("U1", "MOVE F %g" % max(0.0, F_now - PRM["F_retract"]))
                yield from self.done(["DONE MOVE F"], self.move_t(15))
                yield ("sleep", 2.0)
                continue
            for k in range(PRM["mark_retry_max"] + 1):
                self.state("MARK")
                self.flush()
                yield from self.cmd("U1", "MOVE X %g" % tx)
                yield from self.cmd("U1", "MOVE Y %g" % ty)
                yield from self.done(["DONE MOVE X", "DONE MOVE Y"], self.move_t(60))
                for stamp in range(2):             # 같은 점 두 번
                    yield from self.cmd("U1", "PEN DOWN")
                    yield from self.done(["DONE PEN DOWN"], 2)
                    yield ("sleep", PRM["dwell_s"])
                    yield from self.cmd("U1", "PEN UP")
                    yield from self.done(["DONE PEN UP"], 2)
                self.state("VERIFY")
                yield from self.park(pen_down=False)
                obs = yield from self.look("verify")
                if obs and obs[0]["marked"]:
                    yield from self.cmd("U1", "PEN DOWN")
                    yield from self.done(["DONE PEN DOWN"], 2)
                    return True
                self.note("mark_unverified", try_=k + 1)
            yield from self.cmd("U1", "PEN DOWN")
            yield from self.done(["DONE PEN DOWN"], 2)
            return False
        self.note("pose_fail")
        self.flush()
        yield from self.cmd("U1", "MOVE F 0")
        yield from self.done(["DONE MOVE F"], self.move_t(40))
        yield from self.park(pen_down=True)
        return False

    def feed(self):
        self.state("FEED")
        yield from self.cmd("U2", "LIGHT TOP 0")
        yield from self.cmd("U2", "LIGHT BOT 255")
        self.flush()
        yield from self.cmd("U1", "MOVE F %g" % PRM["F_feed"])
        yield from self.done(["DONE MOVE F"], self.move_t(40))
        yield ("sleep", PRM["feed_s"])

    def floor_down(self):
        self.flush()
        yield from self.cmd("U1", "MOVE F 0")
        yield from self.done(["DONE MOVE F"], self.move_t(40))

    def leave(self, d, gates, name):
        """문 d를 열고, 마킹실이 빌 때까지 (장부 + 카메라) 기다린 뒤 닫음."""
        self.state(name)
        self.flush()
        yield from self.cmd("U2", "DOOR %s OPEN" % d)
        yield from self.done(["EVT DOOR %s OPEN" % d], 2)
        t0, nudged, alerted, fallback = self.sim.t, False, False, False
        while True:
            m = yield from self.wait(lambda x: x[1].startswith("LEDGER"), 5.0)
            el = self.sim.t - t0
            n = self.ledger.n
            if n["chamber"] == 0 and n["tube_cap"] == 0 and n["tube_rel"] == 0:
                obs = yield from self.look("empty_check")
                if not obs:
                    break
                self.note("mismatch", what="ledger 0, camera %d" % len(obs))
                n["chamber"] = len(obs)
            if el > PRM["T_light_s"] and not nudged:          # 출구 조명 없음 (SJ-45) → 기록만, 마킹실은 이미 어두움
                nudged = True
                self.note("nudge", t_wait=round(el), what="방생 60 s — 굴뚝 빛 쪽으로 가길 기다림")
            if el > PRM["T_alert_s"] and not alerted:
                alerted = True
                self.note("alert", what="%s 120 s" % name)
            if el > PRM["T_fallback_s"] and not fallback and d == "REL":
                fallback = True
                self.note("fallback", what="REL 300 s → CAP도 엶")
                yield from self.cmd("U2", "DOOR CAP OPEN")
        yield from self.close_door(d)
        if fallback:
            yield from self.close_door("CAP")

    def daylight(self):
        """낮인가 (CAP-AI-30, 제어 위임): 해 뜬 뒤 30분 ~ 해 지기 30분 전. Pi는 날짜·위치(공주 36.45 N, 127.12 E)로
        해 뜨고 지는 시각을 계산 (NOAA 식, 인터넷 없이 RTC 시계로). 시뮬레이션은 PRM 시각을 씀."""
        h = (PRM["clock_start_h"] + self.sim.t / 3600.0) % 24
        return PRM["sunrise_h"] + 0.5 <= h <= PRM["sunset_h"] - 0.5

    def night_hold(self):
        """밤: 굴뚝이 어두워 말벌이 안 나감 → 300 s 뒤 격리 문 규칙에 걸려 찍은 말벌을 잃음 (SJ-45 질문 3).
        그래서 급이 자리 그대로(먹이 있음, 불 끔) 아침까지 마킹실에서 기다림. 입구 문은 닫힌 채."""
        self.state("NIGHT_HOLD")
        self.note("night_hold", what="해 진 뒤 → 아침까지 마킹실")
        yield from self.cmd("U2", "LIGHT TOP 0")
        yield from self.cmd("U2", "LIGHT BOT 0")
        while not self.daylight():
            yield ("sleep", 600.0)
        self.note("morning", what="해 뜬 뒤 30분 → 방생")

    def release(self):
        if not self.daylight():
            yield from self.night_hold()
        yield from self.cmd("U2", "LIGHT TOP 0")
        yield from self.cmd("U2", "LIGHT BOT 0")
        yield from self.leave("REL", ("G5", "G6"), "RELEASE")
        yield from self.floor_down()

    def isolate(self):
        self.state("ISOLATE")
        yield from self.floor_down()
        yield from self.cmd("U2", "LIGHT TOP 0")
        yield from self.cmd("U2", "LIGHT BOT 0")
        yield from self.leave("CAP", ("G3", "G4"), "ISOLATE")

    def shutdown_safe(self):
        """배터리 부족: 처리 중이던 말벌은 끝낸 뒤, 상용 트랩처럼 지나가게 열어 두고 Pi를 끔."""
        self.state("SHUTDOWN")
        yield from self.cmd("U2", "LIGHT TOP 0")
        yield from self.cmd("U2", "LIGHT BOT 0")
        self.flush()
        yield from self.cmd("U2", "DOOR CAP OPEN")
        yield from self.done(["EVT DOOR CAP OPEN"], 3)
        yield from self.cmd("U2", "DOOR IN OPEN")
        yield from self.done(["EVT DOOR IN OPEN"], 3)
        self.note("shutdown", what="passthrough 후 Pi 끔")
        yield ("sleep", 1.0)
        self.alive = False
        self.hb.kill()
        self.rec.set("fsm", "OFF")
        self.rec.set("pi", "halt")
        self.rec.set("cam", "off")
        self.w.uno1.power_off()
        self.w.uno2.power_off()

    def passthrough(self):
        """멈출 때: 격리 문·입구 문을 열어 상용 트랩처럼 지나가게 함 (마킹실에 갇혀 죽지 않게). UNO 2가 살아 있을 때만."""
        if self.ready["U2"]:
            try:
                yield from self.cmd("U2", "LIGHT TOP 0")
                yield from self.cmd("U2", "LIGHT BOT 0")
                self.flush()
                yield from self.cmd("U2", "DOOR CAP OPEN")
                yield from self.done(["EVT DOOR CAP OPEN"], 3)
                yield from self.cmd("U2", "DOOR IN OPEN")
                yield from self.done(["EVT DOOR IN OPEN"], 3)
                self.note("passthrough")
            except Fault:
                pass
        self.state("FAULT_WAIT")
        while True:
            yield ("sleep", 3600)

    def recover(self, reason):
        """고장 뒤: 문은 그대로 둠 → 장치가 돌아오면 다시 초기화 → 마킹실 확인 후 이어서."""
        self.state("FAULT_WAIT")
        if "SELFTEST" in reason:
            self.note("halt", what="게이트 자가 시험 실패 — 사람 점검 전까지 멈춤")
            yield from self.passthrough()
        if reason.startswith("HEARTBEAT"):
            u = reason.split()[1]
            m = yield from self.wait(lambda x: x[0] == u and x[1].startswith("EVT READY"), 120)
            if m is None:
                self.note("halt", what="%s 안 돌아옴" % u)
                yield from self.passthrough()
            self.note("recovered", dev=u)
            if u == "U1":
                yield from self.init_uno1()
            else:
                yield from self.init_uno2()
        yield from self.resume()


# ---------------------------------------------------------------------------
# 시나리오
# ---------------------------------------------------------------------------
def build(sc):
    sim = Sim()
    rec = Rec(sim)
    w = World(sim, rec, gate_fault=sc.get("gate_fault"))
    w.uno1 = Uno1(sim, w, rec)
    w.uno2 = Uno2(sim, w, rec)
    log = []
    rec.set("cam", "run")
    rec.set("hat", "idle")
    w.pi = PiFSM(sim, w, rec, log)
    w.pi.start(w.pi.boot())
    for h in sc["hornets"]:
        w.hornets.append(h)
        Proc(sim, w.hornet_proc(h))
    rec.hooks = []
    for ev in sc.get("events", []):
        if ev[0] == "on":                          # ("on", 상태, 지연, 무엇)
            rec.hooks.append(("fsm", ev[1], ev[2], (lambda what=ev[3]: inject(w, what, log))))
        else:
            sim.at(ev[0], inject, w, ev[1], log)
    return sim, rec, w, log


def inject(w, what, log):
    sim = w.sim
    if what == "battery_low":
        w.batt_low = True
        return
    if what == "uno1_off":
        w.uno1.power_off()
        sim.at(8.0, inject, w, "uno1_on", log)              # 8 s 뒤 전원 돌아옴
    elif what == "uno1_on":
        w.uno1.power_on()
    elif what == "pi_crash":
        w.pi.alive = False
        w.pi.hb.kill()
        if w.pi.main:
            w.pi.main.kill()
        w.rec.set("fsm", "OFF")
        w.rec.set("pi", "halt")
        w.rec.ev("pi_crash")
        sim.at(20.0, inject, w, "pi_restart", log)          # 20 s 뒤 다시 켜짐 (systemd 재시작 가정)
    elif what == "pi_restart":
        old = w.pi
        w.pi = PiFSM(sim, w, w.rec, log)
        w.pi.notes = old.notes + [dict(t=round(sim.t, 2), kind="pi_restart")]
        # 시리얼을 다시 열면 UNO가 재부팅된다 (DTR) — 보수적으로 봄
        w.uno1.power_off()
        w.uno1.power_on()
        w.uno2.alive = False
        w.uno2.power_on()
        w.pi.start(w.pi.boot())


def H(i, **kw):
    return Hornet("h%d" % i, **kw)


def scenarios():
    return {
        "S0_turn_back":        dict(desc="입구 통로에 들어왔다 되돌아감", hornets=[H(0, turn_back=True)], until=200,
                                    expect=dict(h0="trap", doors_end="IN 열림")),
        "S1_nominal":          dict(desc="등검은말벌 일벌 1마리 → 찍고 급이 후 방생", hornets=[H(0)], until=400,
                                    expect=dict(h0="outside", h0_marked=True)),
        "S2_two_in_sequence":  dict(desc="두 번째가 처리 중에 도착 → 입구 문 앞에서 기다렸다 차례로", hornets=[H(0), H(1, t=90)], until=800,
                                    expect=dict(h0="outside", h1="outside", h0_marked=True, h1_marked=True)),
        "S3_two_together":     dict(desc="두 마리가 문 닫기 전에 함께 들어옴 → 카메라 2마리 → 둘 다 격리", hornets=[H(0), H(1, t=60.6)], until=400,
                                    expect=dict(h0="captured", h1="captured")),
        "S4_queen":            dict(desc="여왕벌 → 격리", hornets=[H(0, caste="queen")], until=300, expect=dict(h0="captured")),
        "S4b_gyne_border":     dict(desc="중순판 폭 4.45 mm (경계 띠) → 여왕벌 쪽으로 보고 격리, 4.35 mm → 일벌로 찍고 방생",
                                    hornets=[H(0, mw_mm=4.45), H(1, t=400, mw_mm=4.35)], until=900,
                                    expect=dict(h0="captured", h1="outside", h1_marked=True)),
        "S4c_mw_fail_summer":  dict(desc="폭 못 잼, 7월 → 일벌로 보고 찍고 방생 (계절 규칙)", hornets=[H(0, mw_mm="fail")], until=400,
                                    expect=dict(h0="outside", h0_marked=True), prm=dict(month=7)),
        "S4d_mw_fail_autumn":  dict(desc="폭 못 잼, 10월 → 여왕으로 보고 격리 (계절 규칙)", hornets=[H(0, mw_mm="fail")], until=300,
                                    expect=dict(h0="captured"), prm=dict(month=10)),
"S15_night_hold":      dict(desc="해 진 뒤(17:10 도착) 찍은 말벌 → 아침까지 마킹실, 7:30 지나 방생 (출구 조명 없음, SJ-45)",
                                    hornets=[H(0, t=18600.0)], until=80000, expect=dict(h0="outside", h0_marked=True)),
                "S5_crabro":           dict(desc="유럽말벌 → 격리 (서현 결정 11/06)", hornets=[H(0, species="crabro")], until=300, expect=dict(h0="captured")),
        "S5b_other_insect":    dict(desc="2종이 아닌 곤충(장수말벌·꿀벌 등) → 분류기 불확실 → 격리", hornets=[H(0, species="other")], until=300,
                                    expect=dict(h0="captured")),
        "S6_already_marked":   dict(desc="이미 표식 있음 → 재방문 기록, 급이 후 방생", hornets=[H(0, marked=True)], until=300,
                                    expect=dict(h0="outside", notes=["decision"])),
        "S7_wont_leave":       dict(desc="방생 문을 열어도 150 s 안 나감 → 60 s 조명 바꿈, 120 s 알림", hornets=[H(0, leave_s=150)], until=700,
                                    expect=dict(h0="outside", h0_marked=True, notes=["nudge", "alert"])),
        "S8a_gap_return":      dict(desc="입구 문이 닫히기 시작할 때 마킹실 쪽에서 머리만 문틈에 넣음(2 s, 안쪽 빔만 막힘) → 바로 다시 열고, 비면 닫기", hornets=[H(0, gap_returns=(2.0,))], until=400,
                                    expect=dict(h0="outside", h0_marked=True, events=["door_reverse"])),
        "S8b_gap_dart":        dict(desc="닫힐 때마다 문틈으로 들어옴 3번 → BLOCKED → Pi가 5 s 뒤 다시 명령", hornets=[H(0, gap_returns=(0.5, 0.5, 0.5))], until=400,
                                    expect=dict(h0="outside", h0_marked=True, notes=["door_blocked"], events=["door_reverse"])),
        "S9_flip_retry":       dict(desc="처음 누르니 뒤집힘 → 10 mm 내렸다 다시 → 등 위", hornets=[H(0, poses=("ventral", "dorsal"))], until=400,
                                    expect=dict(h0="outside", h0_marked=True, notes=["pose_retry"])),
        "S10_mark_fail":       dict(desc="찍은 점이 두 번 다 안 보임 → 표식 없이 방생, 기록", hornets=[H(0, dots=(False, False))], until=500,
                                    expect=dict(h0="outside", h0_marked=False, notes=["mark_unverified"])),
        "S11a_camera_miss":    dict(desc="들어왔는데 카메라가 4 s 동안 못 봄 → 기다렸다 확인 후 닫기", hornets=[H(0, cam_miss_s=4.0)], until=400,
                                    expect=dict(h0="outside", h0_marked=True)),
        "S11b_gate_dead":      dict(desc="격리 문 G3 수신부 고장(늘 '안 끊김') → 켤 때 자가 시험에서 잡음 → 격리·입구 문 열어 상용 트랩처럼", hornets=[H(0)], until=300,
                                    gate_fault=dict(G3="stuck_clear"), expect=dict(h0="captured", notes=["halt", "passthrough"])),
        "S12a_uno1_power_loss": dict(desc="누르는 중 UNO 1 전원 끊김 8 s → 하트비트로 잡고, 돌아오면 원점부터 다시", hornets=[H(0)], until=600,
                                     events=[("on", "PRESS", 6.0, "uno1_off")], expect=dict(h0="outside", h0_marked=True, notes=["fault", "recovered"])),
        "S12b_pi_crash":       dict(desc="찍는 중 Pi 멈춤 20 s → UNO 감시가 멈춤·펜 들기, Pi 재시작 후 이어서", hornets=[H(0)], until=600,
                                    events=[("on", "MARK", 0.05, "pi_crash")], expect=dict(h0="outside", h0_marked=True, events=["uno1_watchdog"])),
        "S14_battery_low":     dict(desc="배터리로 운용 중 누르는 동안 배터리 부족 → 이 말벌은 끝까지 처리 → 격리·입구 문 열고 Pi 끔 → 뒤에 온 말벌은 포획통으로",
                                    hornets=[H(0), H(1, t=300)], until=500, events=[("on", "PRESS", 3.0, "battery_low")],
                                    expect=dict(h0="outside", h0_marked=True, h1="captured", notes=["battery_low", "shutdown"])),
        "S13_arrive_at_boot":  dict(desc="켜는 중(원점 찾기 35 s)에 도착 → 닫힌 입구 문 앞에서 기다림 → 준비 뒤 처리", hornets=[H(0, t=5.0)], until=400,
                                    expect=dict(h0="outside", h0_marked=True)),
    }


# ---------------------------------------------------------------------------
# 검사·전력
# ---------------------------------------------------------------------------
def segments(rec, t_end):
    """상태 기록 → (t0, t1, 상태 사전) 구간."""
    st, segs, last = {}, [], 0.0
    for t, k, v in rec.ch:
        if t > last:
            segs.append((last, t, dict(st)))
            last = t
        st[k] = v
    segs.append((last, t_end, dict(st)))
    return [s for s in segs if s[1] > s[0]]


def loads_of(st):
    ax = [st.get("ax_" + a, "off") for a in "FXY"]
    pen = {"detached": "detached", "idle": "idle", "move": "move"}.get(st.get("pen", "detached"), "detached")
    doors = tuple({"detached": "detached", "idle": "idle", "move": "move"}[st.get("srv_" + d, "detached")] for d in GAP)
    lv = lambda k: st.get("L_" + k, 0) / 255.0
    nb = sum(st.get("gate_G%d" % i, 0) for i in range(1, 7))
    kw = dict(stepper_move=ax.count("move"), stepper_hold=ax.count("hold"), pen=pen, doors=doors,
              emit=6 if st.get("emit", 1) else 0, rx=6, blocked=nb, top=lv("TOP"), bot=lv("BOT"), exit_=lv("EXIT"))
    iB = EB.rail_b(**kw)
    iBp = EB.rail_b(peak=True, **kw)
    pi = st.get("pi", "idle")
    pA = EB.LOADS["pi5"]["halt"] if pi == "halt" else EB.rail_a(pi=pi, cam=st.get("cam", "run"), hat=st.get("hat", "idle"))
    return iB, iBp, pA


def check(rec, t_end):
    segs = segments(rec, t_end)
    v = dict(max_servo_moving=0, xy_move_pen_not_up=0.0, mark_door_open=0.0, peak_iB=0.0, crush=0)
    E_A = E_B = 0.0
    for t0, t1, st in segs:
        dt = t1 - t0
        nmov = sum(1 for d in GAP if st.get("srv_" + d) == "move") + (1 if st.get("pen") == "move" else 0)
        v["max_servo_moving"] = max(v["max_servo_moving"], nmov)
        if any(st.get("ax_" + a) == "move" for a in "XY") and st.get("pen_pos") != "up":
            v["xy_move_pen_not_up"] += dt
        if st.get("fsm") in ("PRESS", "POSE", "MARK", "VERIFY") and st.get("door_IN") != "closed":
            v["mark_door_open"] += dt
        iB, iBp, pA = loads_of(st)
        v["peak_iB"] = max(v["peak_iB"], iBp)
        E_A += pA * dt / 3600
        E_B += iB * EB.V_B * dt / 3600
    v["crush"] = sum(1 for e in rec.events if e["kind"] == "crush")
    v["xy_move_pen_not_up"] = round(v["xy_move_pen_not_up"], 3)
    v["mark_door_open"] = round(v["mark_door_open"], 3)
    v["peak_iB"] = round(v["peak_iB"], 3)
    ok = (v["max_servo_moving"] <= 1 and v["xy_move_pen_not_up"] == 0 and v["mark_door_open"] == 0
          and v["peak_iB"] < EB.FUSE["rating_A"] and v["crush"] == 0)
    return ok, v, round(E_A, 4), round(E_B, 4), segs


def run_one(name, sc, verbose=False):
    saved = {k: PRM[k] for k in sc.get("prm", {})}
    PRM.update(sc.get("prm", {}))                     # 시나리오별 값 (예: 달)
    try:
        sim, rec, w, log = build(sc)
        sim.run(sc["until"])
    finally:
        PRM.update(saved)
    pi = w.pi
    ok_inv, inv, E_A, E_B, segs = check(rec, sc["until"])
    res = dict(name=name, desc=sc["desc"], hornets={h.id: dict(zone=h.zone, marked=h.marked_now) for h in w.hornets},
               notes=pi.notes, events=[e for e in rec.events if e["kind"] not in ("look",)], invariants=inv,
               E_A_Wh=E_A, E_B_Wh=E_B, final_doors={d: w.uno2.door[d]["pos"] for d in GAP}, fsm_end=rec.now.get("fsm"))
    exp, fails = sc["expect"], []
    for k, val in exp.items():
        if k.endswith("_marked"):
            if res["hornets"][k[:-7]]["marked"] != val:
                fails.append("%s=%s" % (k, res["hornets"][k[:-7]]["marked"]))
        elif k in ("notes",):
            kinds = {n["kind"] for n in pi.notes}
            fails += ["note %s 없음" % x for x in val if x not in kinds]
        elif k == "events":
            kinds = {e["kind"] for e in rec.events}
            fails += ["event %s 없음" % x for x in val if x not in kinds]
        elif k == "doors_end":
            if res["final_doors"]["IN"] != "open":
                fails.append("IN not open")
        elif k == "no_close":
            if any(c[1] == "door_IN" and c[2] == "closing" for c in rec.ch):
                fails.append("IN closed despite fault")
        elif k.startswith("h"):
            if res["hornets"][k]["zone"] not in val.split("|"):
                fails.append("%s zone=%s" % (k, res["hornets"][k]["zone"]))
    # 한 마리 처리 시간 (G1 → 입구 문 다시 열림)
    t_g1 = next((c[0] for c in rec.ch if c[1] == "gate_G1" and c[2] == 1), None)
    res["cycle_s"] = None
    if t_g1 is not None:
        t_out = next((c[0] for c in rec.ch if c[1] == "fsm" and c[2] in ("RELEASE", "ISOLATE") and c[0] > t_g1), None)
        t_idle = next((c[0] for c in rec.ch if c[1] == "fsm" and c[2] == "IDLE" and t_out and c[0] > t_out), None)
        t_open = next((c[0] for c in rec.ch if c[1] == "door_IN" and c[2] == "open" and t_idle and c[0] >= t_idle), None)
        if t_open:
            res["cycle_s"] = round(t_open - t_g1, 1)
    res["pass"] = ok_inv and not fails
    res["fails"] = fails
    if verbose:
        for t, a, b, line in log:
            if "PING" in line or "PONG" in line:
                continue
            print("%8.3f %-2s→%-2s %s" % (t, a, b, line))
    return res, rec, log, segs


def main(argv):
    scs = scenarios()
    names = argv[1:] or list(scs)
    allres = []
    for n in names:
        res, rec, log, segs = run_one(n, scs[n], verbose=len(names) == 1)
        allres.append(res)
        print("%-22s %s  cycle %-6s E_A %.3f Wh E_B %.3f Wh  inv %s %s" % (
            n, "PASS" if res["pass"] else "FAIL", res["cycle_s"], res["E_A_Wh"], res["E_B_Wh"], res["invariants"],
            ("  " + "; ".join(res["fails"])) if res["fails"] else ""))
        if res["notes"] and len(names) > 1 and not n.startswith(("S1_", "S2_")):
            print("      notes:", [(x["t"], x["kind"]) + tuple(v for k, v in x.items() if k not in ("t", "kind")) for x in res["notes"]][:8])
            evs = [(e["t"], e["kind"]) for e in res["events"] if e["kind"] != "hornet"]
            if evs:
                print("      events:", evs[:8])
        if n == "S1_nominal":
            # 타이밍 그림·순서도용
            t_g1 = next(c[0] for c in rec.ch if c[1] == "gate_G1" and c[2] == 1)
            per = [loads_of(st) + (t0, t1) for t0, t1, st in segs]
            base_A = EB.rail_a(pi="idle", cam="run", hat="idle")
            base_B = EB.rail_b(bot=1) * EB.V_B
            t_end = t_g1 + res["cycle_s"]
            E_cyc = sum((pA + iB * EB.V_B) * (min(t1, t_end) - max(t0, t_g1)) for iB, iBp, pA, t0, t1 in per if t1 > t_g1 and t0 < t_end) / 3600
            extra = E_cyc - (base_A + base_B) * res["cycle_s"] / 3600
            res["per_hornet"] = dict(cycle_s=res["cycle_s"], E_cycle_Wh=round(E_cyc, 4), E_extra_Wh=round(extra, 4),
                                     idle_W=round(base_A + base_B, 2))
            with open(os.path.join(OUT, "S1_timeline.json"), "w", encoding="utf-8") as f:
                json.dump(dict(changes=rec.ch, events=rec.events, log=[l for l in log if "PING" not in l[3] and "PONG" not in l[3]],
                               t_g1=t_g1, t_end=t_end, power=[(t0, t1, iB, pA) for iB, iBp, pA, t0, t1 in per]), f, ensure_ascii=False)
    if len(names) > 1:
        # 비교: 옛 설계(문틈 빔 하나, 통로 쪽)로 S8a·S8b를 돌리면?
        PRM["door_beams"] = 1
        cmp_ = {}
        for n in ("S8a_gap_return", "S8b_gap_dart"):
            r1 = run_one(n, scs[n])[0]
            cmp_[n] = dict(crush=r1["invariants"]["crush"], pass_=r1["pass"])
            print("  [빔 하나 비교] %-16s 끼임 %d  %s" % (n, r1["invariants"]["crush"], "통과" if r1["pass"] else "실패"))
        PRM["door_beams"] = 2
        s1 = next(r for r in allres if r["name"] == "S1_nominal")
        ph = s1["per_hornet"]
        daily = [EB.daily(v, 9.0, False, True, True, per_visit_Wh=ph["E_extra_Wh"]) for v in (0, 20, 100)]
        daily += [EB.daily(20, 24.0, True, True, True, per_visit_Wh=ph["E_extra_Wh"]),
                  EB.daily(20, 9.0, False, False, False, per_visit_Wh=ph["E_extra_Wh"])]
        with open(os.path.join(OUT, "sim_results.json"), "w", encoding="utf-8") as f:
            json.dump(dict(params=PRM, results=allres, per_hornet=ph, daily=daily, single_beam_compare=cmp_), f, ensure_ascii=False, indent=1)
        print("\n한 마리:", ph)
        for d in daily:
            print("하루:", d)
        print("\n%d/%d PASS" % (sum(r["pass"] for r in allres), len(allres)))


if __name__ == "__main__":
    main(sys.argv)
