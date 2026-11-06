# -*- coding: utf-8 -*-
"""회로 설계 (서현, 2026-11-06, CAP-AI-23) — D5e + 11/02 결정 (빛 게이트 9쌍, 콘센트 + 배터리 상자)

한 곳(NETS)에 모든 연결을 적고, 여기서
  1) 넷리스트 표 out/netlist.csv (+ 선 굵기·색·커넥터)
  2) 구매 목록 out/bom.csv
  3) 검사: UNO 핀 중복 없음, 모든 넷에 끝이 2개 이상, 정해진 핀만 씀, 전원 넷에 GND 공통
  4) 회로도 3장 design/img/circuit/ (전원, UNO 1, UNO 2) — schemdraw
를 만든다.  실행: python design/circuit/circuit.py
근거: design/2026-11-02_전기계통_제어순서_서현.md (핀 4장, 전원 3·8장), Adafruit 2167 열린 컬렉터(끊기면 LOW)
"""
import csv
import re
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
IMG = os.path.join(HERE, "..", "img", "circuit")
os.makedirs(OUT, exist_ok=True)
os.makedirs(IMG, exist_ok=True)

GATES = ["G1", "G2", "G2b", "G3", "G3b", "G4", "G5", "G5b", "G6"]
GATE_PIN = dict(zip(GATES, ["A0", "A1", "A2", "A3", "A4", "A5", "D7", "D8", "D12"]))
GATE_WHERE = {"G1": "입구 세로관", "G2": "입구 문 바깥", "G2b": "입구 문 안", "G3": "격리 문 안", "G3b": "격리 문 바깥",
              "G4": "격리 통로 끝", "G5": "방생 문 안", "G5b": "방생 문 바깥", "G6": "방생 출구"}

# ---------------------------------------------------------------------------
# 넷: 이름 → [(부품.핀, 선 굵기 AWG, 비고)]
# ---------------------------------------------------------------------------
NETS = defaultdict(list)


def con(net, *nodes, awg=26, note=""):
    for n in nodes:
        NETS[net].append((n, awg, note))


# 전원 ② → 구동 레일
con("VIN_B", "J_B.+", "F1.1", awg=20, note="배럴 5.5×2.1 (+ 가운데)")
con("VF_B", "F1.2", "SW_E.1", awg=20, note="퓨즈 T2.5A 지연형")
con("+5V_B", "SW_E.2", "TB.+5V", "C1.+", "C2.1", "R_RS.1", awg=20, note="비상 정지 NC 뒤 = 구동 레일")
con("GND", "J_B.-", "TB.GND", "C1.-", "C2.2", awg=20, note="GND 한 점 (와고 GND 묶음)")
# 전원 ① → Pi
con("USB_PI", "PSU_A.USBC", "PI.USBC", awg=0, note="27 W USB-C (또는 배터리 상자 5.1 V 5 A)")
con("USB_U1", "PI.USB1", "U1.USB", awg=0, note="USB A-B 0.5 m, UNO 1 전원 + 115200")
con("USB_U2", "PI.USB2", "U2.USB", awg=0, note="USB A-B 0.5 m")
con("CSI", "PI.CAM0", "CAM.CSI", awg=0, note="Pi 5 22핀 ↔ 15핀 300 mm")
con("GND", "U1.GND", "U2.GND", awg=22, note="UNO GND를 단자대로 (USB GND와 같은 점)")
# 배터리 상자 I2C (배터리일 때만)
con("I2C_SDA", "PI.GPIO2", "J_I2C.SDA", awg=28, note="INA226 (배터리 상자)")
con("I2C_SCL", "PI.GPIO3", "J_I2C.SCL", awg=28)
con("PI_3V3", "PI.3V3", "J_I2C.VCC", awg=28)
con("PI_GND", "PI.GND", "J_I2C.GND", awg=28)

# UNO 1 — 스테핑 3개
for ax, pins in (("F", "D2 D3 D4 D5"), ("X", "D6 D7 D8 D9"), ("Y", "D10 D11 D12 D13")):
    for k, p in enumerate(pins.split(), 1):
        con("U1_%s_IN%d" % (ax, k), "U1.%s" % p, "ULN_%s.IN%d" % (ax, k), awg=26)
    con("+5V_B", "ULN_%s.VCC" % ax, awg=22)
    con("GND", "ULN_%s.GND" % ax, awg=22)
    con("M_%s" % ax, "ULN_%s.XH5" % ax, "M_%s.XH5" % ax, awg=26, note="28BYJ-48 기본 선 (JST-XH 5핀)")
# 펜 서보
con("U1_PEN", "U1.A0", "SG90.SIG", awg=26, note="주황")
con("+5V_B", "SG90.V+", awg=26, note="빨강 — 레일에서 (UNO 5V 아님)")
con("GND", "SG90.GND", awg=26, note="갈색")
# HX711
con("U1_5V", "U1.5V", "HX711.VCC", awg=26, note="HX711은 UNO 5 V (조용함)")
con("GND", "HX711.GND", awg=26)
con("U1_HX_DT", "U1.A1", "HX711.DT", awg=26)
con("U1_HX_SCK", "U1.A2", "HX711.SCK", awg=26)
for w, p in (("빨강", "E+"), ("검정", "E-"), ("흰", "A-"), ("초록", "A+")):
    con("LC_%s" % p, "HX711.%s" % p, "LC.%s" % w, awg=28, note="로드셀 148 (바닥과 움직임, 실리콘 선)")
con("HX_RATE", "HX711.RATE", "HX711.VCC_PAD", awg=0, note="RATE를 5 V로 → 80 Hz (모듈 납땜 다리)")
# 원점 스위치
for ax, p in (("F", "A3"), ("X", "A4"), ("Y", "A5")):
    con("U1_HOME_%s" % ax, "U1.%s" % p, "SW_H%s.NO" % ax, "C_H%s.1" % ax, awg=28, note="내부 풀업, 눌리면 LOW, 100 nF")
    con("GND", "SW_H%s.COM" % ax, "C_H%s.2" % ax, awg=28)

# UNO 2 — 문 서보
for d, p in (("IN", "D9"), ("CAP", "D10"), ("REL", "D11")):
    con("U2_DOOR_%s" % d, "U2.%s" % p, "MG_%s.SIG" % d, awg=26, note="주황")
    con("+5V_B", "MG_%s.V+" % d, awg=26)
    con("GND", "MG_%s.GND" % d, awg=26)
# 빛 게이트 9쌍
for g in GATES:
    con("U2_%s" % g, "U2.%s" % GATE_PIN[g], "RX_%s.OUT" % g, "R_%s.1" % g, awg=28, note="흰 선, 10 kΩ 풀업, 끊기면 LOW")
    con("+5V_B", "R_%s.2" % g, "RX_%s.V+" % g, "TX_%s.V+" % g, awg=28)
    con("GND", "RX_%s.GND" % g, awg=28)
    con("EMIT_LO", "TX_%s.GND" % g, awg=28, note="송신 검정 → MOSFET Q4 (낮은 쪽 스위치)")
con("EMIT_LO", "Q4.OUT-", awg=24)
con("GND", "Q4.GND", awg=24)
con("U2_EMIT", "U2.D4", "Q4.TRIG", awg=26, note="HIGH = 송신 켬 (자가 시험 때 끔)")
# 조명 MOSFET
# 출구 조명 L_EXIT·Q3 없앰 (승준 SJ-45 11/06: 방생 굴뚝 위 하늘빛, 밤 LED는 다른 벌레를 부름) → UNO 2 D6 예비
for q, p, lamp in (("Q1", "D3", "L_TOP"), ("Q2", "D5", "L_BOT")):
    con("U2_%s" % q, "U2.%s" % p, "%s.TRIG" % q, awg=26, note="PWM 되는 핀")
    con("+5V_B", "%s.V+" % lamp, awg=24)
    con("%s_LO" % lamp, "%s.V-" % lamp, "%s.OUT-" % q, awg=24)
    con("GND", "%s.GND" % q, awg=24)
# 레일 감지
con("U2_RAIL", "U2.D2", "R_RS.2", awg=28, note="10 kΩ 직렬, 레일 있으면 HIGH (INT0)")

# ---------------------------------------------------------------------------
# 구매 목록 (수량은 이 설계 기준, 보유분은 승준 구매장부와 대조)
# ---------------------------------------------------------------------------
BOM = [
    ("Arduino UNO R3", 2, "UNO 1 움직임, UNO 2 문·게이트·조명", "보유 4 (정품 1 + 호환)"),
    ("Raspberry Pi 5 + AI HAT+ + AI 카메라", 1, "판단", "보유"),
    ("Pi 5 카메라 케이블 22↔15핀 300 mm", 1, "Pi 위판 아래 (CSI 290 mm)", "확인 — AI 카메라 동봉 길이"),
    ("USB A-B 케이블 0.5 m", 2, "Pi → UNO", "보유 확인"),
    ("28BYJ-48 + ULN2003 세트", 3, "바닥 F, 마커 X, Y", "보유 1 → 살 것 2 (구매목록 B1)"),
    ("SG90", 1, "펜 들기 205", "보유 1 (학습 키트, 실물 확인)"),
    ("MG90S (혼 포함)", 3, "문 112·170·176", "보유 1 (혼 없음, 예비) → 살 것 3 (B2)"),
    ("HX711 + 막대형 로드셀 500 g~1 kg", 1, "누르는 힘 — 버튼형(145,200원) 대신 막대형(6,710원), 11/06 CAP-AI-31. 캐리지 아래 외팔보로 (승준 CAD)", "**살 것** (구매확정표 E11·E12)"),
    ("Pi 5 RTC 배터리 (공식 충전식 ML-2020, J5 BAT 단자)", 1, "전원이 끊겨도 날짜 유지 → 여왕벌 계절 규칙 (11/06)", "**추가**"),
    ("마이크로 스위치 KW11-3Z 레버형 (원점)", 3, "F, X, Y — 외형 20×10.2×6.4, 승준 라이브러리 SJ-38", "추가"),
    ("빛 게이트 Adafruit 2167 (3 mm)", 9, "G1·G2·G2b·G3·G3b·G4·G5·G5b·G6", "**살 것 9쌍** (보유 0, 국내 판매처 확인 — 11/06 고침)"),
    ("로직 레벨 MOSFET 모듈 (D4184 등)", 3, "조명 2 (위·아래) + 송신 켜기 1 — 출구 조명 없앰 (SJ-45)", "살 것 (시험 단계는 보유 릴레이 모듈로 대신 — 켜고 끄기만)"),
    ("저항 10 kΩ", 10, "게이트 풀업 9 + 레일 감지 1", "학습 키트 저항 세트에서 [실물 확인]"),
    ("커패시터 100 nF", 4, "원점 3 + 단자대 1", "키트 커패시터 세트에서 [실물 확인]"),
    ("전해 커패시터 1000 µF 10 V", 1, "서보 옆 단자대", "추가"),
    ("5 V 3 A 어댑터 + DC 잭 5.5×2.1", 1, "구동 레일", "구매 목록 G2"),
    ("퓨즈홀더 F-520 + 퓨즈 5×20 3 A", 1, "구동 레일 — 인라인 홀더·T2.5A를 국내 판매처에서 못 찾아 대신 (구매확정표 E3)", "살 것"),
    ("비상 정지 버튼 (NC)", 1, "구동 레일", "추가"),
    ("와고 레버 커넥터 221-415 (5구)", 5, "+5V_B 2개 이어 8구 (입력·ULN 3·서보 허브·게이트 허브·조명 2), GND 3개 이어 11구 (+ UNO 1·2 GND) — 단자대 대신 (승준 SJ-43 제안 채택) — 와고에는 20~22 AWG만 꽂음 (가는 선은 허브에서)", "살 것"),
    ("만능기판 소형 2장 + 핀 헤더", 1, "서보 허브 (서보 4 헤더 + 1000 µF + 100 nF), 게이트 허브 (수신 9 + 송신 9 헤더 + 풀업 10 kΩ × 9 + 송신 MOSFET)", "살 것 (헤더는 키트 확인)"),
    ("20·22 AWG 연선 (와고 꽂는 줄)", 1, "와고 221은 가는 26·28 AWG를 직접 물기 어려움 → 허브까지는 20~22 AWG", "살 것"),
    ("실리콘 연선 26·28 AWG 각 10~15 m, 20·22 AWG 각 2 m", 1, "배선 약 44 m (가닥 합)", "추가"),
    ("듀폰·JST-XH 연장 커넥터", 1, "게이트·서보 연장", "추가"),
    ("(선택) 배터리 상자: LiFePO4 12.8 V 20 Ah (2일, 11/06) + 충전기 + 강압 5.1 V 5 A·5 V 3 A + INA226 + 퓨즈 5 A", 1, "배터리 운용", "현장 시험 날짜 보고"),
]

UNO_PINS = ["D%d" % i for i in range(2, 14)] + ["A%d" % i for i in range(6)]
RESERVED = {"U1": set(UNO_PINS), "U2": set(UNO_PINS) - {"D13", "D6"}}


def check():
    errs, use = [], defaultdict(list)
    for net, nodes in NETS.items():
        if len({n for n, _, _ in nodes}) < 2 and net not in ("HX_RATE",):
            errs.append("넷 %s 끝이 하나뿐" % net)
        for n, _, _ in nodes:
            part, pin = n.split(".", 1)
            if part in ("U1", "U2") and pin in UNO_PINS:
                use[(part, pin)].append(net)
    for (u, p), nets in use.items():
        if len(set(nets)) > 1:
            errs.append("%s.%s가 넷 %s에 겹침" % (u, p, nets))
    for u in ("U1", "U2"):
        used = {p for (uu, p) in use if uu == u}
        if used != RESERVED[u]:
            errs.append("%s 쓴 핀 %s, 계획 %s" % (u, sorted(used), sorted(RESERVED[u])))
    # 서보·게이트 V+ 가 모두 구동 레일인지
    plus = {n for n, _, _ in NETS["+5V_B"]}
    for need in ["SG90.V+", "MG_IN.V+", "MG_CAP.V+", "MG_REL.V+"] + ["RX_%s.V+" % g for g in GATES] + ["R_%s.2" % g for g in GATES]:
        if need not in plus:
            errs.append("%s가 구동 레일에 없음" % need)
    if any(n.startswith("U1.5V") or n.startswith("U2.5V") for n, _, _ in NETS["+5V_B"]):
        errs.append("UNO 5V 핀이 구동 레일에 이어짐 (금지)")
    return errs, use


def write_tables():
    with open(os.path.join(OUT, "netlist.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["넷", "끝", "AWG", "비고"])
        for net in sorted(NETS):
            for n, awg, note in NETS[net]:
                w.writerow([net, n, awg or "", note])
    with open(os.path.join(OUT, "bom.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["부품", "수량", "쓰는 곳", "상태"])
        w.writerows(BOM)


# ---------------------------------------------------------------------------
# 회로도 (schemdraw)
# ---------------------------------------------------------------------------
def sheets():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "Noto Sans CJK JP"})
    import schemdraw
    import schemdraw.elements as elm
    schemdraw.config(font="Noto Sans CJK JP", fontsize=11)

    def P(name, side, anchor=None):
        return elm.IcPin(name=name, side=side, anchorname=anchor or re.sub(r"[^0-9A-Za-z]", "_", name.split()[0]))

    # --- 1장: 전원 ---
    with schemdraw.Drawing(file=os.path.join(IMG, "회로도_1_전원.png"), show=False, dpi=150) as d:
        d += elm.Label().label("회로도 1/3 — 전원 (콘센트 기본, 같은 플러그로 배터리 상자)", fontsize=14).at((0, 4.2))
        jb = elm.Ic(pins=[P("+", "right", "pin1"), P("−", "right", "pin2")], edgepadW=1.2, label="DC 잭\n5 V 3 A\n(또는 배터리\n상자 5 V 3 A)").at((0, 0))
        d += jb
        d += elm.Line().right(0.8).at(jb.pin1)
        d += (f := elm.Fuse().right().label("F1\nT2.5A", loc="top"))
        d += (sw := elm.Switch(nc=True).right().label("비상 정지\n(NC)", loc="top"))
        d += (n1 := elm.Dot())
        d += elm.Line().right(1.5)
        d += (tb := elm.Dot().label("+5V_B (와고 묶음)", loc="bottom"))
        d += elm.Capacitor(polar=True).down(2).at(n1.center).label("C1\n1000 µF", loc="bottom")
        d += (g1 := elm.Dot())
        d += elm.Capacitor().down(2).at((n1.center[0] + 1.5, n1.center[1])).label("C2 0.1 µF", loc="bottom")
        d += elm.Line().left(1.5)
        d += elm.Wire("-|").at(jb.pin2).to((g1.center[0] - 0.6, g1.center[1]))
        d += elm.Line().tox(g1.center)
        d += elm.Ground().at(g1.center)
        d += elm.Resistor().right(2.5).at(tb.center).label("R_RS 10 kΩ", loc="top")
        d += elm.Label().label("→ UNO 2 D2 (레일 감지)", loc="right")
        d += elm.Label().label("GND 한 점 (와고 GND 묶음) ← UNO 1 GND, UNO 2 GND, 서보·게이트·ULN2003 GND", fontsize=10, halign="left").at((-1, -3.8))
        d += elm.Label().label("+5V_B → ULN2003 ×3, SG90, MG90S ×3, 게이트 수신·송신 ×9, 풀업 10 kΩ ×9, 조명 ×2", fontsize=10, halign="left").at((-1, -4.4))
        d += elm.Label().label("UNO 5V 핀과 +5V_B는 잇지 않음 (UNO는 Pi USB에서)", fontsize=10, halign="left").at((-1, -5.0))
        d += elm.Label().label("Pi 레일 (따로)", fontsize=12, halign="left").at((-1, -6.6))
        pi = elm.Ic(pins=[P("USB-C", "left", "pin1"), P("USB1", "right", "pin2"), P("USB2", "right", "pin3"),
                          P("CAM0", "right", "pin4"), P("GPIO2 SDA", "left", "pin5"), P("GPIO3 SCL", "left", "pin6")],
                    edgepadW=3.6, label="Raspberry Pi 5 + AI HAT+", lblofst=-1.4).at((8, -10))
        d += pi
        d += elm.Line().left(1.5).at(pi.pin1)
        d += elm.Label().label("27 W USB-C 어댑터\n(또는 배터리 상자 5.1 V 5 A)", loc="left")
        d += elm.Line().right(1.2).at(pi.pin2)
        d += elm.Label().label("UNO 1 (USB 전원 + 시리얼)", loc="right")
        d += elm.Line().right(1.2).at(pi.pin3)
        d += elm.Label().label("UNO 2", loc="right")
        d += elm.Line().right(1.2).at(pi.pin4)
        d += elm.Label().label("AI 카메라 (CSI 300 mm)", loc="right")
        d += elm.Line().left(1.5).at(pi.pin5)
        d += elm.Label().label("INA226 SDA\n(배터리 상자)", loc="left")
        d += elm.Line().left(1.5).at(pi.pin6)
        d += elm.Label().label("INA226 SCL", loc="left")

    # --- 2장: UNO 1 ---
    with schemdraw.Drawing(file=os.path.join(IMG, "회로도_2_UNO1_움직임.png"), show=False, dpi=150) as d:
        d += elm.Label().label("회로도 2/3 — UNO 1 (움직임): 스테핑 3 · 펜 서보 · HX711 · 원점 3", fontsize=14).at((0, 9))
        right = ["D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9", "D10", "D11", "D12", "D13"]
        left = ["A0", "A1", "A2", "A3", "A4", "A5", "5V", "GND"]
        u = elm.Ic(pins=[P(p, "right") for p in right] + [P(p, "left", "p" + p) for p in left[::-1]],
                   edgepadH=0.5, pinspacing=0.6, edgepadW=2.0, label="UNO 1").at((0, 0))
        d += u
        for k, ax in enumerate("FXY"):
            ul = elm.Ic(pins=[P("IN%d" % i, "left") for i in range(4, 0, -1)] + [P("XH5", "right")],
                        pinspacing=0.6, edgepadW=1.2, label="ULN2003 %s" % ax).at((7.5, 4.6 - k * 2.9))
            d += ul
            for i in range(4):
                a = getattr(u, right[k * 4 + i])
                b = getattr(ul, "IN%d" % (i + 1))
                d += elm.Wire("-|").at(a).to(b).color("#2a78d6")
            d += elm.Line().right(1.2).at(ul.XH5)
            d += elm.Label().label("28BYJ-48 %s\n(+5V_B, GND)" % {"F": "바닥", "X": "마커 X", "Y": "마커 Y"}[ax], loc="right")
        for p, txt in (("A0", "SG90 펜 신호 (전원 +5V_B)"), ("A1", "HX711 DT"), ("A2", "HX711 SCK  — HX711 VCC는 UNO 5V, RATE→5V (80 Hz)"),
                       ("5V", "HX711 VCC"), ("GND", "와고 GND (한 점)")):
            d += elm.Line().left(1.0).at(getattr(u, "p" + p))
            d += elm.Label().label(txt, loc="left")
        for p, ax in (("A3", "F"), ("A4", "X"), ("A5", "Y")):
            d += elm.Line().left(1.0).at(getattr(u, "p" + p))
            d += elm.Label().label("원점 %s 스위치 → GND (+100 nF)" % ax, loc="left")
        d += elm.Label().label("원점은 내부 풀업 (눌리면 LOW) + 스위치 옆 100 nF", fontsize=10).at((-9, -6))

    # --- 3장: UNO 2 ---
    with schemdraw.Drawing(file=os.path.join(IMG, "회로도_3_UNO2_문게이트조명.png"), show=False, dpi=150) as d:
        d += elm.Label().label("회로도 3/3 — UNO 2: 문 서보 3 · 빛 게이트 9쌍 (풀업 10 kΩ, 송신 MOSFET) · 조명 2 · 레일 감지", fontsize=14).at((-6, 13.5))
        right = ["A0", "A1", "A2", "A3", "A4", "A5", "D7", "D8", "D12"]
        left = ["D2", "D3", "D4", "D5", "D6", "D9", "D10", "D11"]
        u = elm.Ic(pins=[P(p, "right") for p in right] + [P(p, "left", "p" + p) for p in left[::-1]],
                   pinspacing=1.3, edgepadW=2.0, label="UNO 2").at((0, 0))
        d += u
        # 게이트: 풀업 + 수신
        for g in GATES:
            a = getattr(u, GATE_PIN[g])
            d += elm.Line().right(1.0).at(a)
            d += (n := elm.Dot())
            d += elm.Label().label("10 kΩ → +5V_B", loc="top", fontsize=8).at((n.center[0], n.center[1] + 0.3))
            d += elm.Line().right(1.4).at(n.center)
            d += elm.Label().label("수신 %s 흰 선 (%s)" % (g, GATE_WHERE[g]), loc="right", fontsize=10)
        d += elm.Label().label("수신 빨강 +5V_B / 검정 GND, 송신 빨강 +5V_B / 검정 → Q4", fontsize=10).at((3.2, -1.2))
        for p, txt in (("D2", "R_RS 10 kΩ ← +5V_B (레일 감지)"), ("D3", "Q1 MOSFET → 위 링 조명 182"), ("D4", "Q4 MOSFET → 송신 9개 GND 쪽 (EMIT_EN)"),
                       ("D5", "Q2 MOSFET → 아래 조명"), ("D6", "예비 (출구 조명 없앰, SJ-45)"),
                       ("D9", "MG90S 입구 문 112 (주황)"), ("D10", "MG90S 격리 문 170"), ("D11", "MG90S 방생 문 176")):
            d += elm.Line().left(1.0).at(getattr(u, "p" + p))
            d += elm.Label().label(txt, loc="left", fontsize=10)
        d += elm.Label().label("D6·D13 예비 · 서보 전원 +5V_B · GND는 와고 한 점 · 끊기면 LOW", fontsize=10).at((-9, -4.4))


def main():
    errs, use = check()
    write_tables()
    print("넷 %d개, 끝 %d개" % (len(NETS), sum(len(v) for v in NETS.values())))
    print("UNO 1 핀 %d/18, UNO 2 핀 %d/16(D6·D13 예비)" % (len([1 for k in use if k[0] == "U1"]), len([1 for k in use if k[0] == "U2"])))
    print("검사:", "통과" if not errs else errs)
    try:
        sheets()
        print("회로도 3장 → design/img/circuit/")
    except Exception as e:  # 그림 실패해도 표는 남김
        print("회로도 실패:", repr(e))
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
