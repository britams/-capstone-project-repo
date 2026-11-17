# -*- coding: utf-8 -*-
"""하네스 표 — 11/17 판 (서현, Claude CAP-AI-62). 처음: 2026-11-06 CAP-AI-32 (허브 만능기판·5 V 어댑터)

선마다: 번호, 어디 → 어디, 핀, 색, 굵기, 길이, 양 끝. 연결은 design/circuit/circuit.py (11/17)와 같다.
11/17: 납땜 없음 — 신호는 센서 쉴드 3핀에 꽂는 선(서보·2167·스위치 모듈 기본 선 + 듀폰 점퍼로 늘림), 전원은 UL1007 22 AWG 연선을 와고·나사 단자에 조임 (11/17 15시: 20 AWG는 30 m 롤뿐 → 22, 가장 센 줄 약 3 A).
좌표 P = D5g_full 부품 가운데 (11/17 13시 PC FreeCAD에서 읽음) [확실 — 모델 값], LED 모듈·선 기본 길이 일부는 [추측].
길이 = 1.2 × 맨해튼 + 60 (elec_budget.route_len) + 움직이는 끝은 1.5 × 움직임 + 40.
실행: python3 design/circuit/harness.py → design/circuit/out/harness.csv · harness_table.md, 화면에 요약
"""
import csv
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "control_sim"))
import elec_budget as EB   # noqa: E402

P = {
    "UNO1": (-84, -48, 237), "UNO2": (2, 64, 237),          # 센서 쉴드 위 꽂힌 점퍼 자리 193kj (UNO 2는 11/17 데크로)
    "WAGO": (-5, -67, 215), "MOSFET": (-92, 53, 216), "DRV": (-18, -126, 482),   # 193w, 196m, 195p (갠트리 −x 레일 위 받침 197)
    "XL1": (-94, -1, 216), "XL2": (65, 56, 216), "JDC": (66, -79, 212), "FUSE": (69, -59, 211), "ESTOP": (-177, 0, 225),
    "M_X": (176, -62, 425), "M_Y": (101, -118, 450), "SW_X": (34, -84, 468), "SW_Y": (83, -60, 454),
    "PEN": (100, -19, 413), "MZ": (55, -7, 321),
    "D_IN": (10, 34, 376), "D_CAP": (10, -34, 376), "D_REL": (100, 25, 377),
    "G2": (20, 14, 374), "G3b": (20, -14, 375), "G5": (91, -5, 377),
    "LED": (55, 0, 556),                                    # 카메라 판 181 양옆 [추측 — 모델에 아직 없음]
    "PUMP": (112, 202, 128), "PI_B": (-81, 32, 578), "CAM": (55, -2, 547),
}
MOVE = {"PEN": 36.0 + 58.0, "M_Y": 36.0, "SW_Y": 36.0}     # X 36 · Y 58 (Y 모터·Y 원점은 X 캐리지와 같이)
STOCK = {"servo": 250, "ir": 230, "mz": 200, "stepper": 300, "dupont": 200, "led": 150, "pump": 100}
# 기본 선 길이 mm: 서보 [가능성 높음], 2167 230 [확실], IR-EW06 200 [확실 — 상품 이름], LM-NK1134 [추측], 듀폰 점퍼 20 cm [추측 — 보유품], LED·펌프 [추측]
EB.P, EB.MOVE = P, MOVE           # route_len이 이 표를 쓰게

DUP = "듀폰 암 (쉴드 핀)"
WAGO = "와고 221-415 (8 mm 벗김)"
SCREW = "나사 단자 (벗겨 조임)"

# (번호 묶음, 이름, 시작, 끝, [(선 이름, 색, AWG, 시작 핀, 끝 핀)], 시작 커넥터, 끝 커넥터, 최대 전류 A, 기본 선 종류)
H = [
    ("P", "잭 변환 + → 퓨즈 FHAM1", "JDC", "FUSE", [("12 V", "빨강", 22, "SZH-LC002 +", "FHAM1 1")], SCREW, SCREW + " (선 달린 꼴이면 그 선)", 3.0, None),
    ("P", "퓨즈 → 비상 정지 NC", "FUSE", "ESTOP", [("12 V 퓨즈 뒤", "빨강", 22, "FHAM1 2", "NC 1")], SCREW, "비상 정지 나사 단자", 3.0, None),
    ("P", "비상 정지 → 와고 12 V", "ESTOP", "WAGO", [("+12V", "빨강", 22, "NC 2", "와고 12 V")], "비상 정지 나사 단자", WAGO, 3.0, None),
    ("P", "잭 변환 − → 와고 GND", "JDC", "WAGO", [("GND", "검정", 22, "SZH-LC002 −", "와고 GND")], SCREW, WAGO, 3.0, None),
    ("P", "와고 → DRV8825 보드 VMOT (갠트리 위로)", "WAGO", "DRV", [("+12V", "빨강", 22, "와고 12 V", "VMOT"), ("GND", "검정", 22, "와고 GND", "GND")], WAGO, SCREW, 1.0, None),
    ("P", "와고 → MOSFET 보드 V+", "WAGO", "MOSFET", [("+12V", "빨강", 22, "와고 12 V", "V+"), ("GND", "검정", 22, "와고 GND", "GND")], WAGO, SCREW, 0.6, None),
    ("P", "와고 → XL4015 ① 입력", "WAGO", "XL1", [("+12V", "빨강", 22, "와고 12 V", "IN+"), ("GND", "검정", 22, "와고 GND", "IN−")], WAGO, SCREW, 1.0, None),
    ("P", "와고 → XL4015 ② 입력", "WAGO", "XL2", [("+12V", "빨강", 22, "와고 12 V", "IN+"), ("GND", "검정", 22, "와고 GND", "IN−")], WAGO, SCREW, 0.7, None),
    ("P", "XL4015 ① 출력 → 와고 5 V", "XL1", "WAGO", [("+5V_B", "빨강", 22, "OUT+", "와고 5 V"), ("GND", "검정", 22, "OUT−", "와고 GND")], SCREW, WAGO, 2.0, None),
    ("P", "와고 5 V → 센서 쉴드 1 나사 단자", "WAGO", "UNO1", [("+5V_B", "빨강", 22, "와고 5 V", "쉴드 1 V"), ("GND", "검정", 22, "와고 GND", "쉴드 1 G")], WAGO, SCREW, 1.0, None),
    ("P", "와고 5 V → 센서 쉴드 2 나사 단자", "WAGO", "UNO2", [("+5V_B", "빨강", 22, "와고 5 V", "쉴드 2 V"), ("GND", "검정", 22, "와고 GND", "쉴드 2 G")], WAGO, SCREW, 1.5, None),
    ("P", "XL4015 ② 출력 → mightyZAP 전원 (IR-EW06 빨강·검정 + 연장)", "XL2", "MZ", [("+7V4", "빨강", 22, "OUT+", "IR-EW06 빨강"), ("GND", "검정", 22, "OUT−", "IR-EW06 검정")], SCREW, "IR-EW06 (mightyZAP에 꽂음)", 0.6, "mz"),
    # UNO 1
    ("S", "쉴드 1 D2 → mightyZAP 신호 (IR-EW06 흰 + 연장)", "UNO1", "MZ", [("PWM", "흰", 26, "D2 S", "IR-EW06 흰")], DUP, "IR-EW06", 0.001, "mz"),
    ("S", "쉴드 1 → DRV 보드 (STEP·DIR·EN ×2 + GND)", "UNO1", "DRV",
     [("X STEP", "파랑", 26, "D6 S", "X STEP"), ("X DIR", "초록", 26, "D7 S", "X DIR"), ("X EN", "노랑", 26, "D8 S", "X EN"),
      ("Y STEP", "파랑", 26, "D9 S", "Y STEP"), ("Y DIR", "초록", 26, "D10 S", "Y DIR"), ("Y EN", "노랑", 26, "D11 S", "Y EN"), ("GND", "검정", 26, "아무 G", "보드 GND")],
     DUP, "듀폰 암 (보드 헤더) [받고 확인]", 0.002, "dupont"),
    ("M", "DRV 보드 → X 모터 215 (모터 4선)", "DRV", "M_X", [("모터 4선", "모터 선 색", 26, "X A1 A2 B1 B2", "모터")], SCREW + " / 헤더 [받고 확인]", "모터 (기본)", 0.75, "stepper"),
    ("M", "DRV 보드 → Y 모터 209 (X 캐리지와 움직임)", "DRV", "M_Y", [("모터 4선", "모터 선 색", 26, "Y A1 A2 B1 B2", "모터")], SCREW + " / 헤더 [받고 확인]", "모터 (기본)", 0.75, "stepper"),
    ("V", "쉴드 1 A0 → 펜 서보 SG90 205 (X·Y로 움직임)", "UNO1", "PEN", [("서보 3선", "갈색 G·빨강 V·주황 S", 26, "A0 줄", "서보")], "서보 3핀 그대로", "서보 (기본)", 0.65, "servo"),
    ("S", "쉴드 1 A4 → 원점 X 모듈 VLT-SM006", "UNO1", "SW_X", [("3선", "검정 G·빨강 V·노랑 S", 26, "A4 줄", "모듈 G V S")], DUP, "듀폰 암 (모듈 헤더)", 0.005, "dupont"),
    ("S", "쉴드 1 A5 → 원점 Y 모듈 (X 캐리지와 움직임)", "UNO1", "SW_Y", [("3선", "검정 G·빨강 V·노랑 S", 26, "A5 줄", "모듈 G V S")], DUP, "듀폰 암 (모듈 헤더)", 0.005, "dupont"),
    # UNO 2
    ("V", "쉴드 2 D9 → 입구 문 서보 112", "UNO2", "D_IN", [("서보 3선", "갈색·빨강·주황", 26, "D9 줄", "서보")], "서보 3핀 그대로", "서보 (기본)", 0.75, "servo"),
    ("V", "쉴드 2 D10 → 격리 문 서보 170", "UNO2", "D_CAP", [("서보 3선", "갈색·빨강·주황", 26, "D10 줄", "서보")], "서보 3핀 그대로", "서보 (기본)", 0.75, "servo"),
    ("V", "쉴드 2 D11 → 방생 문 서보 176", "UNO2", "D_REL", [("서보 3선", "갈색·빨강·주황", 26, "D11 줄", "서보")], "서보 3핀 그대로", "서보 (기본)", 0.75, "servo"),
] + [
    ("G", "쉴드 2 → 빛 게이트 %s (수신 3선 → %s 줄, 송신 빨강 → %s V)" % (g, a, v), "UNO2", g,
     [("수신 신호", "흰", 28, "%s S" % a, "수신 흰"), ("수신 +5V", "빨강", 28, "%s V" % a, "수신 빨강"), ("수신 GND", "검정", 28, "%s G" % a, "수신 검정"),
      ("송신 +5V", "빨강", 28, "%s V" % v, "송신 빨강")], DUP, "2167 선 끝 헤더 + 듀폰 연장", 0.02, "ir")
    for g, a, v in (("G2", "A0", "A1"), ("G3b", "A3", "A2"), ("G5", "A4", "A5"))
] + [
    ("G", "빛 게이트 %s 송신 검정 → MOSFET Q4 OUT−" % g, g, "MOSFET", [("송신 GND(켜기)", "검정", 28, "송신 검정", "Q4 OUT−")], "2167 선 끝 헤더 + 듀폰 연장", SCREW + " (수 핀 3개 함께) [AI 판단]", 0.02, "ir")
    for g in ("G2", "G3b", "G5")
] + [
    ("S", "쉴드 2 D3·D4·D6 → MOSFET TRIG (Q1 LED·Q4 송신·Q3 펌프) + GND", "UNO2", "MOSFET",
     [("Q1", "노랑", 26, "D3 S", "Q1 TRIG"), ("Q4", "보라", 26, "D4 S", "Q4 TRIG"), ("Q3", "주황", 26, "D6 S", "Q3 TRIG"), ("GND", "검정", 26, "아무 G", "신호 GND")],
     DUP, "듀폰 암 (보드 핀)", 0.001, "dupont"),
    ("L", "MOSFET Q1 → LED 3구 모듈 2개 (카메라 판 양옆)", "MOSFET", "LED", [("+12V", "빨강", 24, "Q1 OUT+", "모듈 빨강 ×2"), ("Q1 OUT−", "검정", 24, "Q1 OUT−", "모듈 검정 ×2")], SCREW + " (모듈 2개 선을 2가닥씩 함께)", "모듈 선 + 연장 — 이음은 모듈 선 끝을 보고 정함 [받고 확인]", 0.15, "led"),
    ("L", "MOSFET Q3 → 펌프 Kamoer 144p (프레임 +y 밖, 1N5819는 Q3 단자에)", "MOSFET", "PUMP", [("+12V", "빨강", 22, "Q3 OUT+", "펌프 +"), ("Q3 OUT−", "검정", 22, "Q3 OUT−", "펌프 −")], SCREW, "펌프 단자 [받고 확인]", 0.4, "pump"),
]

# 사서 쓰는 케이블 — 길이가 모자라지 않는지만 본다
BOUGHT = [
    ("Pi USB → UNO 1 (USB A–B)", "PI_B", "UNO1", 1000),
    ("Pi USB → UNO 2 (USB A–B)", "PI_B", "UNO2", 1000),
    ("Pi CAM0 → 카메라 모듈 3 (FPC 22P↔15P)", "PI_B", "CAM", 300),
]


def cut_len(L):
    """자를 길이: 경로 길이 + 10 % 여유, 10 mm 단위로 올림"""
    return int(math.ceil(L * 1.1 / 10.0) * 10)


def build():
    rows, k = [], {}
    for grp, name, a, b, wires, ca, cb, amps, stock in H:
        L = EB.route_len(a, b)
        if stock:
            need_ext = max(0.0, L - STOCK[stock])
            cut = cut_len(need_ext) if need_ext > 0 else 0
        else:
            cut = cut_len(L)
        k[grp] = k.get(grp, 0) + 1
        hid = "%s%02d" % (grp, k[grp])
        for (w, color, awg, pa, pb) in wires:
            rows.append(dict(id=hid, harness=name, wire=w, color=color, awg=awg, frm=a, frm_pin=pa, frm_conn=ca, to=b, to_pin=pb, to_conn=cb,
                             route_mm=round(L), cut_mm=cut, stock_mm=STOCK.get(stock, 0) if stock else 0,
                             moving=(a in MOVE or b in MOVE),
                             drop_V=round(EB.drop(awg, L / 1000, amps), 3) if amps >= 0.1 else ""))
    return rows


def write_md(rows):
    """묶음별 표 (사람이 보는 것) — design/2026-11-17_회로_배선표_서현.md 에 들어감"""
    out, seen = [], {}
    for r in rows:
        seen.setdefault(r["id"], []).append(r)
    out.append("| 번호 | 어디 → 어디 | 선 (색·굵기) | 시작 핀 → 끝 핀 | 길이 | 양 끝 | 움직임 |")
    out.append("|---|---|---|---|---|---|---|")
    for hid, rs in seen.items():
        r0 = rs[0]
        wires = "<br>".join("%s (%s, %d AWG)" % (r["wire"], r["color"], r["awg"]) for r in rs)
        pins = "<br>".join("%s → %s" % (r["frm_pin"], r["to_pin"]) for r in rs)
        if r0["stock_mm"]:
            cut = "기본 %d + 연장 %d" % (r0["stock_mm"], r0["cut_mm"]) if r0["cut_mm"] else "기본 %d (연장 없음)" % r0["stock_mm"]
        else:
            cut = "자름 %d mm" % r0["cut_mm"]
        out.append("| %s | %s | %s | %s | %s | %s / %s | %s |" % (hid, r0["harness"], wires, pins, cut, r0["frm_conn"], r0["to_conn"], "휨 고리" if r0["moving"] else ""))
    return "\n".join(out)


def main():
    rows = build()
    os.makedirs(os.path.join(HERE, "out"), exist_ok=True)
    p = os.path.join(HERE, "out", "harness.csv")
    with open(p, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    ids = sorted(set(r["id"] for r in rows))
    cut = {}
    for r in rows:
        if not r["stock_mm"]:
            cut[r["awg"]] = cut.get(r["awg"], 0) + r["cut_mm"]
    ext = [(r["id"], r["harness"], r["cut_mm"]) for r in rows if r["stock_mm"] and r["cut_mm"]]
    print("하네스 %d묶음, 선 %d가닥" % (len(ids), len(rows)))
    for a in sorted(cut):
        print("  자를 연선 AWG %d: %.1f m" % (a, cut[a] / 1000))
    print("  기본 선이 모자라 늘릴 묶음 %d개 (듀폰 점퍼·서보 연장):" % len({e[0] for e in ext}), sorted({(e[0], e[2]) for e in ext}))
    worst = max((r for r in rows if r["drop_V"] != ""), key=lambda r: r["drop_V"])
    print("가장 큰 전압 강하: %s %s V" % (worst["harness"], worst["drop_V"]))
    print("움직이는 선:", sorted(set(r["id"] for r in rows if r["moving"])))
    chk = []
    for nm, x, y, have in BOUGHT:
        need = cut_len(EB.route_len(x, y))
        judge = "충분" if have >= need else ("빠듯 (곧게 두르면 됨)" if have >= EB.manhattan(x, y) + 40 else "**모자람**")
        chk.append("| %s | %d mm | %d mm | %s |" % (nm, need, have, judge))
        print("  산 케이블 %s: 필요 %d / 있음 %d → %s" % (nm, need, have, judge))
    with open(os.path.join(HERE, "out", "harness_table.md"), "w", encoding="utf-8") as f:
        f.write(write_md(rows))
        f.write("\n\n**사서 쓰는 케이블 길이 확인** (경로 1.2 × 맨해튼 + 60, + 10 %)\n\n| 케이블 | 필요 | 있음(산 것) | 판단 |\n|---|---|---|---|\n" + "\n".join(chk) + "\n")
    print(p)
    return rows


if __name__ == "__main__":
    main()
