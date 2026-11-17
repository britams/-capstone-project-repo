# -*- coding: utf-8 -*-
"""회로 설계 — 11/17 판 (서현, Claude CAP-AI-62). 처음: 2026-11-06 CAP-AI-23 (빛 게이트 9쌍, 5 V 어댑터, 만능기판 허브)

11/17에 바뀐 것 (design/2026-11-17_전원_12V하나_센서쉴드_서현.md, 인터페이스 정의서 11/14~17 이력)
  - 전원: 12 V 5 A 어댑터 하나 → 잭 변환 SZH-LC002 → 퓨즈 FHAM1 5 A → 비상 정지 NC → 와고 12 V
          → DRV8825 보드 · MOSFET(LED·펌프) · XL4015 ① 5.0 V (+5V_B → 센서 쉴드 2장) · XL4015 ② 7.4 V (mightyZAP)
  - 허브 만능기판 2장 → 센서 쉴드 V5 2장 (3핀 G·V·S, 납땜 없음). 쉴드 SEL 점퍼 뺌 = 쉴드 V는 나사 단자(+5V_B), UNO 5V와 안 이음
  - XY: 28BYJ-48 + ULN2003 → LM-NK1134 + DRV8825 (듀얼 보드 ARD200928). UNO 1 X STEP D6·DIR D7·EN D8, Y D9·D10·D11 (서현 11/17 13시)
  - 바닥: mightyZAP D7-6PT-3 PWM (UNO 1 D2) — 원점·누름 스위치 없음
  - 빛 게이트 3쌍 (Adafruit 2167): G2 A0 · G3b A3 · G5 A4, 내부 풀업 (trap_doors v0.3)
  - 조명: 12 V LED 3구 모듈 2개를 MOSFET Q1 하나로 (Q2·D5 비움), 펌프 Kamoer NKP 12 V (Q3)

한 곳(NETS)에 모든 연결을 적고, 여기서
  1) 넷리스트 표 out/netlist.csv   2) 전기 부품 목록 out/bom.csv
  3) 검사: UNO 핀 중복 없음, 넷마다 끝 2개 이상, 정해진 핀만 씀, 부하마다 맞는 전압 줄, 모든 구동 줄이 비상 정지 뒤, UNO 5V ↔ +5V_B 안 이음
  4) 회로도 3장 design/img/circuit/회로도_{1,2,3}_*_1117.png (11/06 그림은 그 회차 문서용으로 둠) — schemdraw
실행: python design/circuit/circuit.py
[가능성 높음 — 받으면 확인] 쉴드 SEL 점퍼 뜻, MOSFET 모듈 OUT+ = V+, DRV 보드 헤더 이름 (EN·STEP·DIR·GND), VLT-SM006 출력 (눌리면 LOW)
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

GATES = ["G2", "G3b", "G5"]
GATE_PIN = {"G2": "A0", "G3b": "A3", "G5": "A4"}
GATE_WHERE = {"G2": "입구 문 앞 (트랩 쪽) — 진입 신호 겸함", "G3b": "격리 문 뒤 (관 쪽)", "G5": "방생 문 뒤 (급이실 쪽)"}
EMIT_V_PIN = {"G2": "A1", "G3b": "A2", "G5": "A5"}   # 송신 빨강을 꽂는 쉴드 2 빈 줄의 V 핀 (+5V_B) — 신호 핀은 비움 (AI 판단)

# ---------------------------------------------------------------------------
# 넷: 이름 → [(부품.핀, 선 굵기 AWG, 비고)]   AWG 0 = 사서 쓰는 케이블·플러그
# ---------------------------------------------------------------------------
NETS = defaultdict(list)


def con(net, *nodes, awg=26, note=""):
    for n in nodes:
        NETS[net].append((n, awg, note))


# ---- 전원 (12 V 하나) ----
con("V12_RAW", "ADP.PLUG+", "JDC.+", awg=0, note="어댑터 5.5 × 2.1 플러그를 잭 변환 SZH-LC002에 꽂음")
con("V12_RAW", "F1.1", awg=20, note="잭 변환 + 나사 → FHAM1 (블레이드 퓨즈 5 A)")
con("V12_F", "F1.2", "SW_E.NC1", awg=20, note="퓨즈 → 비상 정지 KGE-J4R1R NC (나사 단자)")
con("+12V", "SW_E.NC2", "WG12.1", awg=20, note="비상 정지 뒤 = 구동 12 V (와고 12 V)")
con("+12V", "DRV.VMOT", awg=20, note="ARD200928 전원 단자 — DRV8825 2개. 드라이버 옆 VMOT–GND 100 µF (보드에 없으면) [받고 확인]")
con("+12V", "MOS.V+", awg=22, note="SZH-AT021 전원 단자 (Q1 LED · Q3 펌프)")
con("+12V", "MOS.Q1+", "L1.+", "L2.+", awg=24, note="LED 3구 모듈 12 V 2개 빨강 — 보드 OUT+ = V+ [가능성 높음]")
con("+12V", "MOS.Q3+", "PUMP.+", "D_P.K", awg=22, note="Kamoer NKP + · 1N5819 줄(K)을 같은 나사 단자에 (납땜 없음)")
con("+12V", "XL1.IN+", awg=20, note="강압 ① 입력")
con("+12V", "XL2.IN+", awg=22, note="강압 ② 입력")
con("+5V_B", "XL1.OUT+", "WG5.1", awg=20, note="XL4015 ① 5.0 V (표시 보며 손잡이 나사로) → 와고 5 V")
con("+5V_B", "SH1.VCC", "SH2.VCC", awg=22, note="센서 쉴드 1·2 나사 단자 V — SEL 점퍼 뺌 (쉴드 V 핀 = +5V_B, UNO 5V와 안 이음)")
con("+7V4", "XL2.OUT+", "MZ.V", awg=22, note="XL4015 ② 7.4 V → mightyZAP 빨강 (IR-EW06)")
con("GND", "JDC.-", "WGG.1", awg=20, note="와고 GND 2개 (다리 1개로 이음) — 한 점")
con("GND", "DRV.GND", "MOS.GND", "XL1.IN-", "XL1.OUT-", "XL2.IN-", "XL2.OUT-", awg=22)
con("GND", "SH1.GND", "SH2.GND", awg=22, note="쉴드 나사 단자 G = UNO GND (USB GND와 같은 점)")
con("GND", "MZ.GND", awg=22, note="mightyZAP 검정")
# ---- Pi 레일 (따로) ----
con("USB_PI", "PSU_A.USBC", "PI.USBC", awg=0, note="27 W 공식 USB-C (보유)")
con("USB_U1", "PI.USB1", "U1.USB", awg=0, note="USB A-B, UNO 1 전원 + 115200")
con("USB_U2", "PI.USB2", "U2.USB", awg=0, note="USB A-B, UNO 2")
con("CSI", "PI.CAM0", "CAM.CSI", awg=0, note="FPC 22P(0.5) ↔ 15P(1.0) 300 mm — 카메라 모듈 3")

# ---- UNO 1 (쉴드 1): 움직임 ----
con("U1_MZ", "U1.D2", "MZ.PWM", awg=26, note="쉴드 D2 줄 S — mightyZAP 흰(신호)만, V·G는 XL4015 ② (PWM 900~2100 µs)")
for ax, (st, dr, en) in (("X", ("D6", "D7", "D8")), ("Y", ("D9", "D10", "D11"))):
    con("U1_%s_STEP" % ax, "U1.%s" % st, "DRV.%s_STEP" % ax, awg=26, note="쉴드 S 핀 → 보드 헤더 (암-암 점퍼)")
    con("U1_%s_DIR" % ax, "U1.%s" % dr, "DRV.%s_DIR" % ax, awg=26)
    con("U1_%s_EN" % ax, "U1.%s" % en, "DRV.%s_EN" % ax, awg=26, note="LOW = 켬 (DRV8825), HIGH = 코일 끔 (HOLD 0)")
    for c in ("A1", "A2", "B1", "B2"):
        con("M_%s_%s" % (ax, c), "DRV.%s_%s" % (ax, c), "M_%s.%s" % (ax, c), awg=0, note="LM-NK1134 4선 (모터에 달린 선) → 보드 모터 단자")
con("GND", "DRV.LGND", awg=26, note="보드 신호 GND ↔ 쉴드 1 G 핀 (같은 점)")
con("U1_PEN", "U1.A0", "SG90.SIG", awg=0, note="쉴드 A0 줄에 서보 3핀 그대로 (주황 S)")
con("+5V_B", "SG90.V+", awg=0, note="빨강 → 쉴드 V (= +5V_B)")
con("GND", "SG90.GND", awg=0, note="갈색 → 쉴드 G")
for ax, p in (("X", "A4"), ("Y", "A5")):
    con("U1_HOME_%s" % ax, "U1.%s" % p, "SW%s.S" % ax, awg=26, note="VLT-SM006 3핀 → 쉴드 %s 줄 (암-암 점퍼), INPUT_PULLUP, 눌리면 LOW [받고 확인]" % p)
    con("+5V_B", "SW%s.V" % ax, awg=26)
    con("GND", "SW%s.G" % ax, awg=26)

# ---- UNO 2 (쉴드 2): 문·게이트·조명·펌프 ----
con("+5V_B", "R_RS.1", awg=0, note="쉴드 2 D2 줄 V 핀에 저항 다리를 듀폰 암에 꽂음")
con("U2_RAIL", "U2.D2", "R_RS.2", awg=0, note="10 kΩ 직렬 → D2 S: 비상 정지가 눌리면 +5V_B가 꺼져 LOW (INPUT)")
for d, p in (("IN", "D9"), ("CAP", "D10"), ("REL", "D11")):
    con("U2_DOOR_%s" % d, "U2.%s" % p, "MG_%s.SIG" % d, awg=0, note="쉴드 %s 줄에 서보 3핀 그대로" % p)
    con("+5V_B", "MG_%s.V+" % d, awg=0)
    con("GND", "MG_%s.GND" % d, awg=0)
for g in GATES:
    con("U2_%s" % g, "U2.%s" % GATE_PIN[g], "RX_%s.OUT" % g, awg=28, note="2167 수신 흰 → 쉴드 %s S, 내부 풀업, 끊기면 LOW" % GATE_PIN[g])
    con("+5V_B", "RX_%s.V+" % g, awg=28, note="수신 빨강 → 같은 줄 V")
    con("GND", "RX_%s.GND" % g, awg=28, note="수신 검정 → 같은 줄 G")
    con("+5V_B", "TX_%s.V+" % g, awg=28, note="송신 빨강 → 쉴드 %s 줄 V (빈 줄, 신호 핀은 안 씀)" % EMIT_V_PIN[g])
    con("EMIT_LO", "TX_%s.GND" % g, awg=28, note="송신 검정 → MOSFET Q4 OUT− (낮은 쪽 스위치)")
con("EMIT_LO", "MOS.Q4-", awg=24)
con("U2_EMIT", "U2.D4", "MOS.Q4_TRIG", awg=26, note="HIGH = 송신 켬 (자가 시험 때 끔)")
con("U2_LIGHT", "U2.D3", "MOS.Q1_TRIG", awg=26, note="PWM — LED 모듈 2개 같이")
con("L_TOP_LO", "MOS.Q1-", "L1.-", "L2.-", awg=24, note="LED 모듈 검정")
con("U2_PUMP", "U2.D6", "MOS.Q3_TRIG", awg=26, note="HIGH = 펌프 돎 (trap_doors PUMP <ms>, 최대 200)")
con("PUMP_LO", "MOS.Q3-", "PUMP.-", "D_P.A", awg=22, note="펌프 − · 1N5819 A")
con("GND", "MOS.SGND", awg=26, note="MOSFET 신호 쪽 GND ↔ 쉴드 2 G 핀 (TRIG 기준)")

# ---------------------------------------------------------------------------
# 전기 부품 목록 (이 회로 기준 수량) — 값·판매처는 purchase/부품정리_2026-11-17.xlsx (엑셀이 원본)
# ---------------------------------------------------------------------------
BOM = [
    ("Arduino UNO R3", 2, "UNO 1 움직임, UNO 2 문·게이트·조명·펌프", "보유"),
    ("아두이노 센서 쉴드 V5.0 SZH-EK049", 2, "UNO 위에 꽂음, SEL 점퍼 뺌", "엑셀"),
    ("Raspberry Pi 5 + AI HAT+ · 27 W USB-C", 1, "판단", "보유"),
    ("카메라 모듈 3 + FPC 22P↔15P 300 mm", 1, "Pi CAM0", "엑셀"),
    ("USB A-B 케이블", 2, "Pi → UNO 1·2", "보유 확인"),
    ("12 V 5 A 어댑터 (5.5 × 2.1)", 1, "모든 구동 전원", "엑셀"),
    ("DC 잭 → 단자 SZH-LC002", 1, "어댑터 플러그 → 나사 단자", "엑셀 (2 = 1 + 예비)"),
    ("퓨즈홀더 FHAM1 + 블레이드 퓨즈 5 A", 1, "12 V 줄, 비상 정지 앞", "엑셀 (퓨즈 3)"),
    ("비상 정지 KGE-J4R1R 25Φ (NC)", 1, "12 V 줄 — 끊으면 12 V·5 V·7.4 V 모두 꺼짐", "엑셀"),
    ("와고 221-415", 4, "12 V 1 · GND 2 · 5 V 1", "엑셀 (5 = 4 + 예비)"),
    ("XL4015 강압 (전압 표시) SZH-PWSDF-036", 2, "① 5.0 V +5V_B ② 7.4 V mightyZAP", "엑셀"),
    ("듀얼 스텝 드라이버 보드 ARD200928 + DRV8825", 1, "X·Y (DRV8825 2)", "엑셀 (해외, 자비)"),
    ("LM-NK1134 나사 일체형 스텝 모터", 2, "마커 X·Y", "엑셀"),
    ("mightyZAP D7-6PT-3 + 선 IR-EW06 PWM 200 mm", 1, "바닥 승강", "엑셀"),
    ("SG90", 1, "펜 들기 205", "보유"),
    ("MG90S", 3, "문 112·170·176", "엑셀"),
    ("리미트 스위치 모듈 VLT-SM006", 2, "원점 X·Y", "엑셀 (3 = 2 + 예비)"),
    ("빛 게이트 Adafruit 2167 3 mm", 3, "G2·G3b·G5", "엑셀 (4 = 3 + 예비)"),
    ("MOSFET 4채널 SZH-AT021", 1, "Q1 LED · Q3 펌프 · Q4 송신 (Q2 비움)", "엑셀"),
    ("LED 3구 모듈 백색 12 V", 2, "위 조명 (카메라 양옆)", "엑셀 (4 = 2 + 예비 2)"),
    ("연동 펌프 Kamoer NKP 12 V", 1, "급이 (Q3)", "엑셀"),
    ("저항 10 kΩ", 1, "레일 감지 R_RS (쉴드 2 D2 줄)", "보유 키트"),
    ("쇼트키 다이오드 1N5819", 1, "펌프 역기전력 D_P — MOSFET Q3 나사 단자에 같이 조임", "**엑셀에 없음**"),
    ("전해 커패시터 100 µF 25 V", 1, "DRV 보드 VMOT–GND (보드에 있으면 안 삼)", "**엑셀에 없음 — 보드 받고**"),
    ("연선 20·22 AWG (빨강·검정)", 1, "12 V·5 V·GND 와고 줄 — 길이는 harness.py", "**엑셀에 없음**"),
    ("듀폰 점퍼선 (암-암·암-수)", 1, "쉴드 ↔ DRV 보드·스위치·MOSFET TRIG, 짧은 선 연장", "보유"),
]

UNO_PINS = ["D%d" % i for i in range(2, 14)] + ["A%d" % i for i in range(6)]
RESERVED = {"U1": {"D2", "D6", "D7", "D8", "D9", "D10", "D11", "A0", "A4", "A5"},
            "U2": {"D2", "D3", "D4", "D6", "D9", "D10", "D11", "A0", "A3", "A4"}}
NEED_5V = ["SG90.V+", "MG_IN.V+", "MG_CAP.V+", "MG_REL.V+", "SWX.V", "SWY.V", "R_RS.1"] + \
          ["RX_%s.V+" % g for g in GATES] + ["TX_%s.V+" % g for g in GATES]
NEED_12V = ["SW_E.NC2", "DRV.VMOT", "MOS.V+", "XL1.IN+", "XL2.IN+", "L1.+", "L2.+", "PUMP.+"]


def check():
    errs, use = [], defaultdict(list)
    for net, nodes in NETS.items():
        if len({n for n, _, _ in nodes}) < 2:
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
    ends = {net: {n for n, _, _ in nodes} for net, nodes in NETS.items()}
    errs += ["%s가 +5V_B에 없음" % n for n in NEED_5V if n not in ends["+5V_B"]]
    errs += ["%s가 +12V(비상 정지 뒤)에 없음" % n for n in NEED_12V if n not in ends["+12V"]]
    if ends["+7V4"] != {"XL2.OUT+", "MZ.V"}:
        errs.append("7.4 V 줄에 mightyZAP 말고 다른 것: %s" % sorted(ends["+7V4"]))
    five = {"SG90", "MG_IN", "MG_CAP", "MG_REL", "SWX", "SWY", "SH1", "SH2", "MZ"} | {"RX_" + g for g in GATES} | {"TX_" + g for g in GATES}
    errs += ["%s가 12 V에 이어짐" % n for n in ends["+12V"] if n.split(".")[0] in five]
    if any(n.startswith(("U1.5V", "U2.5V")) for n in ends["+5V_B"]):
        errs.append("UNO 5V 핀이 +5V_B에 이어짐 (금지 — SEL 점퍼 뺌)")
    if not ({"JDC.+", "F1.1"} <= ends["V12_RAW"] and {"F1.2", "SW_E.NC1"} <= ends["V12_F"]):
        errs.append("잭 → 퓨즈 → 비상 정지 순서가 아님")
    return errs, use


def write_tables():
    with open(os.path.join(OUT, "netlist.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["넷", "끝", "AWG (0 = 산 케이블·플러그)", "비고"])
        for net in sorted(NETS):
            for n, awg, note in NETS[net]:
                w.writerow([net, n, awg or "", note])
    with open(os.path.join(OUT, "bom.csv"), "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["부품", "수량 (이 회로)", "쓰는 곳", "상태"])
        w.writerows(BOM)


# ---------------------------------------------------------------------------
# 회로도 (schemdraw)
# ---------------------------------------------------------------------------
def sheets():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FONT = "Noto Sans CJK JP" if any(f.name == "Noto Sans CJK JP" for f in matplotlib.font_manager.fontManager.ttflist) else "Malgun Gothic"  # Windows는 맑은 고딕
    plt.rcParams.update({"font.family": FONT})
    import schemdraw
    import schemdraw.elements as elm
    schemdraw.config(font=FONT, fontsize=11)

    def P(name, side, anchor=None):
        return elm.IcPin(name=name, side=side, anchorname=anchor or re.sub(r"[^0-9A-Za-z]", "_", name.split()[0]))

    # --- 1장: 전원 ---
    with schemdraw.Drawing(file=os.path.join(IMG, "회로도_1_전원_1117.png"), show=False, dpi=150) as d:
        d += elm.Label().label("회로도 1/3 — 전원 (11/17: 12 V 어댑터 하나, 비상 정지가 모든 구동을 끊음)", fontsize=14).at((0, 4.2))
        jb = elm.Ic(pins=[P("-", "right", "pin2"), P("+", "right", "pin1")], edgepadW=1.4, label="12 V 5 A\n어댑터 →\n잭 변환\nSZH-LC002").at((0, 0))
        d += jb
        d += elm.Line().right(0.8).at(jb.pin1)
        d += elm.Fuse().right().label("FHAM1\n5 A", loc="top")
        d += elm.Switch(nc=True).right().label("비상 정지\nKGE-J4R1R (NC)", loc="top")
        d += (n12 := elm.Dot())
        d += elm.Line().right(2.0)
        d += elm.Label().label("+12V (와고 12 V) → DRV8825 보드 ARD200928 VMOT → 마커 X·Y 모터", loc="right", fontsize=10)
        y0 = n12.center[1]
        for k, txt in enumerate(("MOSFET SZH-AT021 V+ → Q1 LED 모듈 2 (12 V) · Q3 펌프 Kamoer (12 V, 1N5819)",
                                 "XL4015 ① 5.0 V → +5V_B (와고 5 V) → 센서 쉴드 1·2 나사 단자",
                                 "XL4015 ② 7.4 V → mightyZAP (IR-EW06 빨강·검정)"), 1):
            d += elm.Line().down(1.1).at((n12.center[0], y0 - 1.1 * (k - 1)))
            d += elm.Dot()
            d += elm.Line().right(2.0)
            d += elm.Label().label(txt, loc="right", fontsize=10)
        d += elm.Wire("-|").at(jb.pin2).to((jb.pin2[0] + 1.2, -4.6))
        d += elm.Ground()
        d += elm.Label().label("GND 한 점 = 와고 GND 2개 (어댑터 −, DRV, MOSFET, XL4015 ①②, 쉴드 1·2 G, mightyZAP −) — UNO GND는 쉴드로 같은 점", fontsize=10, halign="left").at((-1, -5.6))
        d += elm.Label().label("+5V_B → 쉴드 V 핀: SG90 · MG90S 3 · 2167 수신 3·송신 3 · 원점 모듈 2 · 레일 감지 10 kΩ (UNO 2 D2)", fontsize=10, halign="left").at((-1, -6.2))
        d += elm.Label().label("쉴드 SEL 점퍼 뺌 → UNO 5V 핀과 +5V_B는 안 이음 (UNO는 Pi USB로) · 12 V 최대 약 2.5 A [추측] < 5 A", fontsize=10, halign="left").at((-1, -6.8))
        d += elm.Label().label("Pi 레일 (따로): 27 W USB-C 공식 어댑터 → Raspberry Pi 5 + AI HAT+ → USB1 UNO 1 · USB2 UNO 2 (USB A-B, 전원 + 시리얼) · CAM0 카메라 모듈 3 (FPC 300 mm)", fontsize=10, halign="left").at((-1, -7.8))

    # --- 2장: UNO 1 ---
    with schemdraw.Drawing(file=os.path.join(IMG, "회로도_2_UNO1_움직임_1117.png"), show=False, dpi=150) as d:
        d += elm.Label().label("회로도 2/3 — UNO 1 + 센서 쉴드 1 (움직임): mightyZAP · DRV8825 X·Y · 펜 서보 · 원점 X·Y", fontsize=14).at((-6, 7.5))
        right = ["D11", "D10", "D9", "D8", "D7", "D6", "D2"]
        left = ["A0", "A4", "A5", "G 단자", "V 단자"]
        u = elm.Ic(pins=[P(p, "right") for p in right] + [P(p, "left", "p" + p.split()[0]) for p in left[::-1]],
                   pinspacing=1.0, edgepadW=2.4, label="UNO 1\n+ 쉴드 1").at((0, 0))
        d += u
        for p, txt in (("D2", "mightyZAP 신호 (흰) — 전원 7.4 V는 XL4015 ②"),
                       ("D6", "X STEP → DRV 보드"), ("D7", "X DIR"), ("D8", "X EN (LOW = 켬)"),
                       ("D9", "Y STEP"), ("D10", "Y DIR"), ("D11", "Y EN (LOW = 켬)")):
            d += elm.Line().right(1.0).at(getattr(u, p)).color("#2a78d6")
            d += elm.Label().label(txt, loc="right", fontsize=10)
        for p, txt in (("A0", "SG90 펜 서보 3핀 그대로"), ("A4", "원점 X VLT-SM006 3핀 (눌리면 LOW)"), ("A5", "원점 Y VLT-SM006 3핀"),
                       ("G", "와고 GND"), ("V", "+5V_B (XL4015 ①), SEL 점퍼 뺌")):
            d += elm.Line().left(1.0).at(getattr(u, "p" + p))
            d += elm.Label().label(txt, loc="left", fontsize=10)
        d += elm.Label().label("DRV 보드: VMOT +12V · GND · 신호 GND ↔ 쉴드 G · 모터 X·Y 4선 · 전류 한도 0.5 A (Vref 0.25 V [가능성 높음]) · 빈 핀 D3 D4 D5 D12 D13 A1 A2 A3", fontsize=10, halign="left").at((-9, -4.2))

    # --- 3장: UNO 2 ---
    with schemdraw.Drawing(file=os.path.join(IMG, "회로도_3_UNO2_문게이트조명_1117.png"), show=False, dpi=150) as d:
        d += elm.Label().label("회로도 3/3 — UNO 2 + 센서 쉴드 2: 문 서보 3 · 빛 게이트 3쌍 · LED · 펌프 · 레일 감지", fontsize=14).at((-6, 9.5))
        right = ["A5", "A4", "A3", "A2", "A1", "A0"]
        left = ["D2", "D3", "D4", "D6", "D9", "D10", "D11"]
        u = elm.Ic(pins=[P(p, "right") for p in right] + [P(p, "left", "p" + p) for p in left[::-1]],
                   pinspacing=1.1, edgepadW=2.4, label="UNO 2\n+ 쉴드 2").at((0, 0))
        d += u
        for g in GATES:
            d += elm.Line().right(1.0).at(getattr(u, GATE_PIN[g])).color("#2a78d6")
            d += elm.Label().label("2167 수신 %s 3선 (%s)" % (g, GATE_WHERE[g]), loc="right", fontsize=10)
        for g, p in EMIT_V_PIN.items():
            d += elm.Line().right(1.0).at(getattr(u, p)).color("#c0392b")
            d += elm.Label().label("V 핀만: %s 송신 빨강 (+5V_B), 검정 → Q4 OUT−" % g, loc="right", fontsize=10)
        for p, txt in (("D2", "V 핀 → 10 kΩ → S (레일 감지)"), ("D3", "Q1 TRIG → LED 모듈 2 (12 V)"), ("D4", "Q4 TRIG → 송신 3개 GND 쪽"),
                       ("D6", "Q3 TRIG → 펌프 Kamoer (12 V)"), ("D9", "MG90S 입구 문 112"), ("D10", "MG90S 격리 문 170"), ("D11", "MG90S 방생 문 176")):
            d += elm.Line().left(1.0).at(getattr(u, "p" + p))
            d += elm.Label().label(txt, loc="left", fontsize=10)
        d += elm.Label().label("빈 핀 D5 (Q2 비움) D7 D8 D12 D13 · 수신은 INPUT_PULLUP, 끊기면 LOW · MOSFET 신호 GND ↔ 쉴드 G · 펌프 다이오드 1N5819는 Q3 나사 단자에", fontsize=10, halign="left").at((-9, -4.6))


def main():
    errs, use = check()
    write_tables()
    print("넷 %d개, 끝 %d개" % (len(NETS), sum(len(v) for v in NETS.values())))
    print("UNO 1 핀 %d/18, UNO 2 핀 %d/18" % (len([1 for k in use if k[0] == "U1"]), len([1 for k in use if k[0] == "U2"])))
    print("검사:", "통과" if not errs else errs)
    try:
        sheets()
        print("회로도 3장 → design/img/circuit/*_1117.png")
    except Exception as e:  # 그림 실패해도 표는 남김
        print("회로도 실패:", repr(e))
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
