# -*- coding: utf-8 -*-
"""전기 계통·제어 순서 그림 (서현, 2026-11-02, CAP-AI-22) → design/img/control/

먼저 elec_budget.py, trap_sim.py를 돌려 out/*.json을 만든 뒤 실행한다.
  1) 전기_배선도_상세.png       — 전원·퓨즈·단자대·UNO 1/2 핀·부품 (D5e + 제안)
  2) 제어순서_타이밍_S1.png     — 한 마리 처리 (S1) 시간표 + 전력
  3) 제어_상태도.png            — Pi 상태 머신 (graphviz)
  4) 제어_메시지순서_S1.png     — Pi ↔ UNO 1 ↔ UNO 2 메시지 (mermaid)
색: dataviz 기본 범주 순서 (파랑, 주황, 청록, 노랑, 자홍, 초록, 보라, 빨강), 글자는 검정·회색
"""
import json
import os
import subprocess

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
IMG = os.path.join(HERE, "..", "img", "control")
os.makedirs(IMG, exist_ok=True)
plt.rcParams.update({"font.family": "Noto Sans CJK JP", "axes.unicode_minus": False})
C = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#6250d6", "#e34948"]
SURF, INK, INK2, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#d9d8d4"
RED, BLK = "#c0392b", "#222222"


# ---------------------------------------------------------------------------
# 1) 배선도
# ---------------------------------------------------------------------------
def blk(ax, x, y, w, h, title, lines=(), fc="#f1f4fa", ec="#2f5597", tfs=11, fs=8.6, lh=0.33):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.12", fc=fc, ec=ec, lw=1.4, zorder=3))
    ax.text(x + 0.12, y + h - 0.12, title, fontsize=tfs, fontweight="bold", va="top", color=INK, zorder=4)
    for i, t in enumerate(lines):
        ax.text(x + 0.12, y + h - 0.5 - i * lh, t, fontsize=fs, va="top", color=INK2 if t.startswith("·") else INK, zorder=4)


def ln(ax, pts, c, lw=1.4, ls="-", z=1):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=c, lw=lw, ls=ls, zorder=z, solid_capstyle="round")


def tag(ax, x, y, t, c=INK2, fs=8, ha="center", va="center", rot=0):
    ax.text(x, y, t, fontsize=fs, ha=ha, va=va, color=c, rotation=rot, zorder=5,
            bbox=dict(fc=SURF, ec="none", pad=0.6, alpha=0.95))


def wiring():
    fig, ax = plt.subplots(figsize=(17, 11.5), dpi=130)
    fig.patch.set_facecolor(SURF)
    ax.set_facecolor(SURF)
    ax.set_xlim(0, 17)
    ax.set_ylim(0, 11.5)
    ax.axis("off")
    ax.text(0.2, 11.3, "전기 배선도 (D5e + 11/02 결정) — 구동 레일 5 V는 Pi 전원과 따로, GND만 한 점에서 묶음", fontsize=14, fontweight="bold", va="top")
    ax.text(0.2, 10.9, "굵은 빨강 = 구동 레일 +5 V (단자대에서 나눔)  ·  굵은 검정 = GND  ·  파랑 = UNO 1 신호  ·  초록 = UNO 2 신호  ·  보라 = USB / CSI",
            fontsize=9.5, color=INK2, va="top")
    U1C, U2C, USBC = C[0], C[5], C[6]

    # 전원 ①: Pi
    blk(ax, 0.2, 8.2, 2.5, 1.9, "전원 ① 27 W USB-C", ["5.1 V 5 A (보유) — 콘센트", "· Pi 5 + AI HAT+ + AI 카메라", "· 대기 약 5.7 W, 판별 약 8.4 W", "· 밤: 꺼짐 0.01 W (EEPROM 설정)"], fc="#fbf3ec", ec=C[1])
    blk(ax, 3.3, 6.55, 3.0, 3.15, "Raspberry Pi 5 (+ AI HAT+)", ["판단·AI·상태 머신·기록", "· USB-A ×2 → UNO 1, UNO 2", "  (/dev/serial/by-id 로 구분,", "   EVT READY uno1/uno2 확인)", "· CSI → AI 카메라 IMX500", "· 0.5 s마다 PING (하트비트)", "· 자리: 위판 아래 (CSI 300 mm)", "· I2C ← INA226 (배터리일 때)"], fc="#f3f0fb", ec=USBC, lh=0.31)
    ln(ax, [(2.7, 9.2), (3.3, 9.2)], C[1], lw=3)
    blk(ax, 3.3, 10.0, 3.0, 0.5, "AI 카메라 IMX500 (격자 위 200 mm)", [], fc="#f3f0fb", ec=USBC, tfs=9.5)
    ln(ax, [(4.8, 9.7), (4.8, 10.0)], USBC, lw=2.2)
    tag(ax, 6.5, 10.25, "CSI 리본: 데크 위 Pi면 약 680 mm(1 m 필요) / 위판 아래면 약 290 mm(300 mm)", c=USBC, fs=8, ha="left")

    # UNO 1
    u1 = (7.2, 5.6, 3.1, 4.5)
    blk(ax, *u1, "UNO 1 — 움직임", [
        "D2~D5   ULN2003 F (IN1~4)", "D6~D9   ULN2003 X", "D10~D13 ULN2003 Y", "A0      SG90 펜 신호",
        "A1/A2   HX711 DT/SCK", "A3/A4/A5 원점 F/X/Y", "        (내부 풀업 + 100 nF)", "5V/GND  HX711만 (UNO 5 V)",
        "· 하드웨어 WDT 1 s (제안)", "· Pi 2 s 침묵 → 멈춤·펜 들기·", "  바닥 10 mm 내림 (제안)"], fc="#eef4fc", ec=U1C, fs=8.4, lh=0.34)
    # UNO 2
    u2 = (7.2, 0.5, 3.1, 4.7)
    blk(ax, *u2, "UNO 2 — 문·게이트·조명", [
        "D9/D10/D11 MG90S 입구/격리/방생", "A0~A5   G1 G2 G2b G3 G3b G4 수신", "D7 D8 D12  G5 G5b G6 수신 (10 kΩ)",
        "D2      레일 감지 (10 kΩ, INT0)", "D3/D5/D6 MOSFET 위/아래/출구 조명", "        (PWM 되는 핀)", "D4      MOSFET 송신 켜기 EMIT_EN",
        "D13     예비", "· 문틈 규칙(빔 2개)·서보 하나씩", "· 켤 때 서보 안 붙임 (문 그대로)", "· Pi 2 s 침묵 → 닫던 문 다시 엶"], fc="#eef8ef", ec=U2C, fs=8.4, lh=0.34)
    ln(ax, [(6.3, 8.4), (7.2, 8.4)], USBC, lw=2.2)
    tag(ax, 6.75, 8.6, "USB", c=USBC)
    ln(ax, [(6.0, 6.55), (6.0, 3.0), (7.2, 3.0)], USBC, lw=2.2)
    tag(ax, 6.0, 5.0, "USB (전원 + 115200)", c=USBC, rot=90)

    # 전원 ②
    blk(ax, 0.2, 4.3, 2.5, 1.5, "전원 ② 5 V 3 A 어댑터", ["구동 레일 전용 — 콘센트", "· 정상 최대 약 1.9 A", "· 켤 때 서보 4개 동시면 3.3 A"], fc="#fbeeee", ec=RED)
    # 배터리 상자 (선택) — 같은 플러그로 전원 ①·② 자리를 대신함
    ax.add_patch(FancyBboxPatch((0.2, 6.05), 2.5, 1.9, boxstyle="round,pad=0.02,rounding_size=0.12", fc="#f4f4f1", ec=INK2, lw=1.4, ls=(0, (4, 2)), zorder=3))
    ax.text(0.32, 7.83, "배터리 상자 (선택)", fontsize=11, fontweight="bold", va="top", zorder=4)
    for i, t in enumerate(["LiFePO4 12.8 V 12 Ah (약 1.7일)", "· 강압 5.1 V 5 A → USB-C (①)", "· 강압 5 V 3 A → 배럴 (②)", "· 퓨즈 5 A + INA226 → Pi I2C", "· 부족하면 처리 끝내고 Pi 끔"]):
        ax.text(0.32, 7.45 - i * 0.3, t, fontsize=8.2, va="top", color=INK if i == 0 else INK2, zorder=4)
    ln(ax, [(2.7, 7.6), (2.95, 7.6), (2.95, 8.6), (2.7, 8.6)], INK2, lw=1.3, ls=(0, (4, 2)))
    ln(ax, [(2.7, 6.4), (2.95, 6.4), (2.95, 5.3), (2.7, 5.3)], INK2, lw=1.3, ls=(0, (4, 2)))
    ln(ax, [(2.95, 7.0), (3.3, 7.0)], USBC, lw=1.3, ls=(0, (4, 2)))
    tag(ax, 2.95, 8.05, "또는", c=INK2, fs=7.5)
    tag(ax, 2.95, 5.85, "또는", c=INK2, fs=7.5)
    blk(ax, 0.2, 2.6, 2.5, 1.2, "퓨즈 T2.5A (지연형)", ["3 A 어댑터는 스스로 전류를", "묶어 3 A 퓨즈는 거의 안 끊김"], fc="#fbeeee", ec=RED, fs=8)
    blk(ax, 0.2, 1.0, 2.5, 1.1, "비상 정지 (NC 버섯)", ["레일만 끊음 → UNO 2 D2가 감지", "→ 다시 켜면 원점부터"], fc="#fbeeee", ec=RED, fs=8)
    blk(ax, 3.3, 0.5, 3.0, 2.3, "단자대 (데크 위)", ["+5 V 줄 / GND 줄", "· 1000 µF + 0.1 µF (서보 옆)", "· GND 한 점 → UNO 1·2 GND", "· UNO 5V 핀과 레일 +5 V는", "  잇지 않음 (USB 역류 방지)"], fc="#fbeeee", ec=RED, fs=8.4)
    ln(ax, [(1.45, 4.3), (1.45, 3.8)], RED, lw=3)
    ln(ax, [(1.45, 2.6), (1.45, 2.1)], RED, lw=3)
    ln(ax, [(1.45, 1.0), (1.45, 0.7), (3.3, 0.7)], RED, lw=3)
    tag(ax, 2.3, 0.7, "20 AWG", c=RED)

    # 레일 줄 (단자대 → 오른쪽 부품)
    YR, YG = 0.25, 0.12
    ln(ax, [(6.3, 2.2), (6.7, 2.2), (6.7, YR), (16.8, YR)], RED, lw=3)
    ln(ax, [(6.3, 1.9), (6.55, 1.9), (6.55, YG), (16.8, YG)], BLK, lw=3)
    ln(ax, [(6.55, 1.9), (6.55, 5.4), (7.2, 5.4)], BLK, lw=1.6, ls=(0, (4, 2)))
    tag(ax, 6.85, 5.4, "GND", c=BLK, fs=7.5)
    tag(ax, 11.0, YR + 0.12, "+5 V 구동 레일 (22 AWG 가지, 서보 26 AWG)", c=RED, fs=8)

    # 오른쪽 부품 — UNO 1 쪽
    x0 = 11.0
    devs1 = [
        (9.3, "ULN2003 ×3 → 28BYJ-48 F·X·Y", "상당 82 mA, 반걸음 평균 0.12 A·대 · HOLD F 0 권장", "IN1~4 ×3"),
        (8.3, "SG90 펜 들기 205 (캐리지 위)", "움직일 때 0.25 A, 막힘 0.65 A · 휨 고리 약 180 mm", "A0"),
        (7.3, "HX711 + 로드셀 148 (바닥과 움직임)", "약 6 mA, UNO 1 5 V에서 · RATE 80 Hz 권장", "A1/A2"),
        (6.3, "원점 스위치 F·X·Y (마이크로)", "누르면 GND, 내부 풀업 · Y는 빔과 움직임", "A3~A5"),
    ]
    for y, t1, t2, pin in devs1:
        blk(ax, x0, y - 0.35, 5.8, 0.8, t1, [t2], fc="#eef4fc", ec=U1C, tfs=9.5, fs=8)
        ln(ax, [(10.3, y), (x0, y)], U1C, lw=1.6)
        tag(ax, 10.65, y + 0.14, pin, c=U1C, fs=7.5)
    for y in (9.3, 8.3):
        ln(ax, [(16.95, y), (16.95, YR)], RED, lw=1.8)
    for y in (9.3, 8.3):
        ln(ax, [(16.8, y), (16.95, y)], RED, lw=1.8)
    # UNO 2 쪽
    devs2 = [
        (4.8, "MG90S ×3 문 112·170·176", "이동 0.2 A, 막힘 0.75 A · 한 번에 하나 · 멈추고 0.5 s 뒤 신호 끊기", "D9~D11"),
        (3.8, "빛 게이트 수신 ×9 (문마다 2개 + G1·G4·G6)", "열린 컬렉터: 끊기면 LOW · 10 kΩ 풀업은 레일 +5 V로", "A0~5 +3"),
        (2.8, "빛 게이트 송신 ×9 (20 mA씩)", "EMIT_EN MOSFET 하나로 180 mA · 켤 때 끄고 켜서 자가 시험", "D4"),
        (1.8, "조명 3 (위 링 182 · 아래 · 출구)", "로직 레벨 MOSFET 모듈 · 0.2/0.1/0.06 A [추측]", "D3 D5 D6"),
        (0.85, "레일 감지 (10 kΩ 직렬)", "레일 끊김 → EVT RAIL OFF → Pi는 원점부터", "D2"),
    ]
    for y, t1, t2, pin in devs2:
        blk(ax, x0, y - 0.4 if y < 1 else y - 0.35, 5.8, 0.8, t1, [t2], fc="#eef8ef", ec=U2C, tfs=9.5, fs=8)
        ln(ax, [(10.3, y), (x0, y)], U2C, lw=1.6)
        tag(ax, 10.65, y + 0.14, pin, c=U2C, fs=7.5)
    for y in (4.8, 3.8, 2.8, 1.8):
        ln(ax, [(16.8, y), (16.95, y), (16.95, YR)], RED, lw=1.8)
    ax.text(11.0, 5.62, "풀업을 레일 +5 V에 다는 까닭: 레일이 꺼지면 풀업도 0 V → 모든 게이트가 '끊김'으로 읽힘\n→ 문이 안 닫힘 (안전 쪽). 수신부만 죽으면 '안 끊김'으로 읽혀 위험 → 켤 때 자가 시험으로 잡음",
            fontsize=8, color=INK2, va="center", linespacing=1.5)
    fig.savefig(os.path.join(IMG, "전기_배선도_상세.png"), facecolor=SURF, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2) 타이밍 (S1)
# ---------------------------------------------------------------------------
def intervals(ch, key, pred, t0, t1):
    out, cur, start = [], None, None
    for t, k, v in ch:
        if k != key:
            continue
        on = pred(v)
        if on and start is None:
            start = t
        elif not on and start is not None:
            out.append((start, t))
            start = None
        cur = v
    if start is not None:
        out.append((start, t1))
    return [(max(a, t0), min(b, t1)) for a, b in out if b > t0 and a < t1]


def timing():
    d = json.load(open(os.path.join(OUT, "S1_timeline.json"), encoding="utf-8"))
    ch, ev = d["changes"], d["events"]
    t0, t1 = d["t_g1"] - 3, d["t_end"] + 3
    T = lambda t: t - d["t_g1"]
    rows = [
        ("상태", None), ("G1 입구 세로관", ("gate_G1", 1)), ("G2 입구 문 바깥", ("gate_G2", 1)), ("G2b 입구 문 안", ("gate_G2b", 1)),
        ("G5 방생 문 안", ("gate_G5", 1)), ("G5b 방생 문 바깥", ("gate_G5b", 1)), ("G6 방생 출구", ("gate_G6", 1)),
        ("입구 문 열림", ("door_IN", "open")), ("방생 문 열림", ("door_REL", "open")),
        ("바닥 F 움직임", ("ax_F", "move")), ("마커 X 움직임", ("ax_X", "move")), ("마커 Y 움직임", ("ax_Y", "move")),
        ("펜 내림", ("pen_pos", "down")), ("위 조명", ("L_TOP", "on")), ("아래 조명", ("L_BOT", "on")), ("출구 조명", ("L_EXIT", "on")),
        ("촬영·판별", ("hat", "run")),
    ]
    colr = {"gate": INK2, "door": C[0], "ax_": C[2], "pen": C[1], "L_": C[3], "hat": C[6]}
    fig = plt.figure(figsize=(16, 9.6), dpi=130)
    fig.patch.set_facecolor(SURF)
    ax = fig.add_axes([0.13, 0.36, 0.85, 0.57])
    axp = fig.add_axes([0.13, 0.07, 0.85, 0.22], sharex=ax)
    for a in (ax, axp):
        a.set_facecolor(SURF)
        for s in ("top", "right"):
            a.spines[s].set_visible(False)
        a.spines["left"].set_color(GRID)
        a.spines["bottom"].set_color(GRID)
        a.tick_params(colors=INK2, labelsize=9)
    n = len(rows)
    for i, (name, spec) in enumerate(rows):
        y = n - 1 - i
        if spec is None:
            fs = [(t, v) for t, k, v in ch if k == "fsm"]
            short = 0
            for j, (ta, v) in enumerate(fs):
                tb = fs[j + 1][0] if j + 1 < len(fs) else t1
                a, b = max(ta, t0), min(tb, t1)
                if b <= a:
                    continue
                ax.add_patch(Rectangle((T(a), y - 0.38), T(b) - T(a), 0.76, fc="#e9e8e4" if j % 2 else "#d6d5d0", ec=SURF, lw=2))
                if T(b) - T(a) > 4:
                    ax.text((T(a) + T(b)) / 2, y, v, ha="center", va="center", fontsize=8.5, color=INK)
                elif T(a) >= T(t0) + 0.5:          # 짧은 상태는 띠 위에 엇갈려 적음
                    ax.plot([T(a), T(a)], [y + 0.4, y + 0.55 + 0.32 * (short % 3)], color=INK2, lw=0.6)
                    ax.text(T(a), y + 0.6 + 0.32 * (short % 3), v, ha="left", va="center", fontsize=7.5, color=INK2)
                    short += 1
            continue
        key, val = spec
        if val == "on":
            pred = lambda v: (v or 0) > 0
        else:
            pred = lambda v, val=val: v == val
        col = next(c for p, c in colr.items() if key.startswith(p))
        for a, b in intervals(ch, key, pred, t0, t1):
            w = max(T(b) - T(a), 0.35)
            ax.add_patch(Rectangle((T(a), y - 0.3), w, 0.6, fc=col, ec=SURF, lw=2))
    ax.set_yticks(range(n))
    ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=9.5, color=INK)
    ax.set_ylim(-0.95, n + 0.55)
    ax.set_xlim(T(t0), T(t1))
    ax.grid(axis="x", color=GRID, lw=0.6)
    ax.set_axisbelow(True)
    plt.setp(ax.get_xticklabels(), visible=False)
    # 주석
    looks = [e for e in ev if e["kind"] == "look" and t0 <= e["t"] <= t1]
    KO = dict(idle_check="대기 점검", entry="진입 확인", after_close="닫은 뒤", identify="판별", pose="자세·흉부",
              verify="점 확인", empty_check="빈방 확인", resume="재개")
    groups = []
    for e in looks:                       # 3 s 안에 붙은 촬영은 한 이름표로
        x = T(e["t"])
        if groups and x - groups[-1][1] < 3:
            groups[-1][1] = x
            groups[-1][2].append(KO.get(e["what"], e["what"]))
        else:
            groups.append([x, x, [KO.get(e["what"], e["what"])]])
    for x0_, x1_, names in groups:
        ax.text(x0_ - 0.3, -0.62, "·".join(names), fontsize=7.5, color=C[6], ha="left" if len(names) > 1 else "center")
    fig.text(0.13, 0.965, "제어 순서 시간표 — 시나리오 S1 (등검은말벌 일벌 1마리: 들어옴 → 판별 → 누르기 → 찍기 → 확인 → 급이 60 s → 방생)",
             fontsize=13, fontweight="bold", color=INK)
    fig.text(0.13, 0.94, "가로 = G1을 지난 뒤 초. 모터 1.96 mm/s(지금 펌웨어 기본값) 기준이라 Y 40 mm 이동이 약 20 s. 시간 대부분이 [추측] 값 (look 0.6 s, 급이 60 s, 나가는 데 20 s)",
             fontsize=9.5, color=INK2)
    # 전력
    pw = d["power"]
    xs, ya, yb = [], [], []
    for a, b, iB, pA in pw:
        if b < t0 or a > t1:
            continue
        a, b = max(a, t0), min(b, t1)
        xs += [T(a), T(b)]
        ya += [pA, pA]
        yb += [iB * 5.0, iB * 5.0]
    axp.plot(xs, ya, color=C[0], lw=2, label="Pi 레일 (Pi 5 + 카메라 + HAT + UNO)")
    axp.plot(xs, yb, color=C[1], lw=2, label="구동 레일 5 V (모터·서보·게이트·조명)")
    axp.set_ylabel("W", color=INK2)
    axp.set_xlabel("G1 통과 뒤 시간 (s)", color=INK2)
    axp.grid(axis="y", color=GRID, lw=0.6)
    axp.set_ylim(0, max(ya) * 1.25)
    axp.legend(loc="upper right", fontsize=9, frameon=False, ncol=2)
    axp.text(T(t0) + 1, max(ya) * 1.12, "평균 전력은 대기 때와 거의 같음 → 하루 에너지는 '켜 둔 시간'이 정함", fontsize=9, color=INK2)
    fig.savefig(os.path.join(IMG, "제어순서_타이밍_S1.png"), facecolor=SURF)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 3) 상태도 (graphviz)
# ---------------------------------------------------------------------------
DOT = r'''
digraph fsm {
  graph [rankdir=TB, fontname="Noto Sans CJK JP", bgcolor="#fcfcfb", pad=0.3, nodesep=0.45, ranksep=0.42,
         label="Pi 상태 머신 (참고 구현 trap_sim.py, D5e) — 굵은 선 = 보통 순서, 점선 = 예외", labelloc=t, fontsize=17];
  node  [shape=box, style="rounded,filled", fontname="Noto Sans CJK JP", fontsize=12, fillcolor="#eef4fc", color="#2a78d6", penwidth=1.4];
  edge  [fontname="Noto Sans CJK JP", fontsize=10, color="#52514e"];
  BOOT  [label="BOOT\nUNO 2 감시·SELFTEST\n문 3개 닫기(문틈 규칙)"];
  HOME  [label="HOME\n펜 들기 → 원점 F → X·Y\n한계·대기 자리·펜 캡 컵"];
  RESUME[label="마킹실 확인\n(카메라)", fillcolor="#f3f0fb", color="#6250d6"];
  IDLE  [label="IDLE 대기\n입구 열림·격리/방생 닫힘\n아래 조명"];
  ENTRY [label="ENTRY\nG2 통과(장부) + 카메라 1마리\n→ 입구 닫기(문틈 규칙)"];
  IDENT [label="IDENTIFY\n위 조명·촬영\n종·여왕벌·표식"];
  PRESS [label="PRESS\n펜 들기·X·Y 미리 이동\n바닥 51 g까지"];
  POSE  [label="POSE\n등 위? 흉부 확률 ≥ 0.6"];
  MARK  [label="MARK\n펜 2단계 내리기 ×2"];
  VERIFY[label="VERIFY\n대기 자리에서 점 확인"];
  FEED  [label="FEED 급이·건조\n바닥 31 mm, 60 s"];
  REL   [label="RELEASE\n출구 조명·방생 문 열기\nG5 → G6 + 카메라 0 → 닫기", fillcolor="#eef8ef", color="#008300"];
  ISO   [label="ISOLATE\n바닥 내림·격리 문 열기\nG3 → G4 + 카메라 0 → 닫기", fillcolor="#fbeeee", color="#e34948"];
  FAULT [label="FAULT_WAIT\n문은 그대로 · 장치 READY 기다림\n안 돌아오면 격리·입구 문 열어\n상용 트랩처럼 (passthrough)", fillcolor="#fff6e0", color="#eda100"];

  BOOT -> HOME -> RESUME [penwidth=2.2];
  RESUME -> IDLE [label=" 비었음", penwidth=2.2];
  RESUME -> IDENT [label=" 말벌 있음", style=dashed];
  IDLE -> ENTRY [label=" G2 통과\n 또는 카메라", penwidth=2.2];
  ENTRY -> IDLE [label=" 카메라 0 (10 s)\n 되돌아감", style=dashed];
  ENTRY -> IDENT [label=" 1마리", penwidth=2.2];
  ENTRY -> ISO [label=" 2마리 이상", style=dashed];
  IDENT -> PRESS [label=" 일벌·표식 없음", penwidth=2.2];
  IDENT -> FEED [label=" 이미 표식\n (재방문 기록)", style=dashed];
  IDENT -> ISO [label=" 여왕벌·다른 종\n 방제 모드·불확실", style=dashed];
  PRESS -> POSE [label=" DONE PRESS", penwidth=2.2];
  PRESS -> PRESS [label=" LIMIT(하중 없음)\n 바닥 내렸다 다시", style=dashed];
  POSE -> MARK [label=" 등 위", penwidth=2.2];
  POSE -> PRESS [label=" 뒤집힘: 10 mm 내리고\n 2 s 뒤 다시 (≤ 3번)", style=dashed];
  POSE -> FEED [label=" 3번 실패\n (표식 없이)", style=dashed];
  MARK -> VERIFY [penwidth=2.2];
  VERIFY -> MARK [label=" 점 안 보임\n (1번 더)", style=dashed];
  VERIFY -> FEED [label=" 점 확인\n (또는 기록)", penwidth=2.2];
  FEED -> REL [penwidth=2.2];
  REL -> IDLE [label=" 닫힘·바닥 내림", penwidth=2.2];
  ISO -> IDLE [label=" 닫힘", style=dashed];
  REL -> REL [label=" 60 s 조명 바꿈\n 120 s 알림\n 300 s 격리 문도 엶", style=dashed];
  FAULT -> HOME [label=" UNO 1 READY", style=dashed];
  FAULT -> RESUME [label=" UNO 2 READY", style=dashed];
  {rank=same; IDENT; ISO;}
  {rank=same; FEED; FAULT;}
  ANY [shape=plaintext, style="", label="어느 상태에서나:\n하트비트 1.5 s 끊김 · 명령 무응답·ERR\n문 3번 막힘 · 자가 시험 실패", fontsize=10, fontcolor="#52514e"];
  ANY -> FAULT [style=dotted, color="#eda100", penwidth=1.6];
}
'''


def state_diagram():
    p = os.path.join(OUT, "fsm.dot")
    open(p, "w", encoding="utf-8").write(DOT)
    subprocess.run(["dot", "-Tpng", "-Gdpi=130", p, "-o", os.path.join(IMG, "제어_상태도.png")], check=True)


# ---------------------------------------------------------------------------
# 4) 메시지 순서 (mermaid)
# ---------------------------------------------------------------------------
def sequence():
    d = json.load(open(os.path.join(OUT, "S1_timeline.json"), encoding="utf-8"))
    t0, t1 = d["t_g1"] - 0.5, d["t_end"] + 0.5
    T = lambda t: t - d["t_g1"]
    KO = dict(idle_check="대기 점검", entry="진입 확인", after_close="닫은 뒤 마릿수", identify="판별: 종·여왕벌·표식", pose="자세·흉부",
              verify="찍은 점 확인", empty_check="빈방 확인", resume="재개")
    looks = [(e["t"] - 0.6 + 1e-4, KO.get(e["what"], e["what"])) for e in d["events"] if e["kind"] == "look" and t0 <= e["t"] <= t1]
    items = []
    for t, a, b, line in d["log"]:
        if not (t0 <= t <= t1) or line.startswith("OK ") or "LEDGER" in line:
            continue
        items.append((t, a, b, line))
    for t, w in looks:
        items.append((t, "LOOK", "", w))
    items.sort(key=lambda x: x[0])
    name = {"PI": "Pi", "U1": "U1", "U2": "U2"}
    lines = ["sequenceDiagram", "  participant U1 as UNO 1 (움직임)", "  participant Pi as Pi 5 (상태 머신)", "  participant U2 as UNO 2 (문·게이트·조명)"]
    merged = []
    for it in items:      # 같은 방향 LIGHT 명령은 한 줄로
        if merged and it[3].startswith("LIGHT") and merged[-1][3].startswith("LIGHT") and it[1:3] == merged[-1][1:3]:
            merged[-1] = (merged[-1][0], it[1], it[2], merged[-1][3] + " · " + it[3][6:])
        else:
            merged.append(it)
    for t, a, b, line in merged:
        s = "%.1f s  %s" % (T(t), line.replace(";", ","))
        if a == "LOOK":
            lines.append("  Note over Pi: %.1f s 촬영 0.6 s — %s" % (T(t), line))
        elif a == "PI":
            lines.append("  Pi->>%s: %s" % (name[b], s))
        else:
            lines.append("  %s-->>Pi: %s" % (name[a], s))
    p = os.path.join(OUT, "seq_S1.mmd")
    open(p, "w", encoding="utf-8").write("\n".join(lines))
    cfg = os.path.join(OUT, "mmd_cfg.json")
    json.dump({"theme": "neutral", "themeVariables": {"fontFamily": "Noto Sans CJK JP", "fontSize": "13px"},
               "sequence": {"messageFontSize": 13, "noteFontSize": 12, "actorFontSize": 14, "messageMargin": 22}}, open(cfg, "w"))
    subprocess.run(["mmdc", "-i", p, "-o", os.path.join(IMG, "제어_메시지순서_S1.png"), "-c", cfg, "-b", "#fcfcfb", "-s", "1.6", "-w", "1100"],
                   check=True, capture_output=True)
    return len(merged)


if __name__ == "__main__":
    wiring()
    timing()
    state_diagram()
    n = sequence()
    print("ok, sequence lines", n)
