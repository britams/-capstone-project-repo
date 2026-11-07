# -*- coding: utf-8 -*-
"""하네스 표 (선마다: 번호, 어디→어디, 핀, 색, 굵기, 자를 길이, 양 끝 커넥터) — 서현, 2026-11-06, CAP-AI-32

바탕: design/circuit/circuit.py (연결), design/control_sim/elec_budget.py (좌표 P, 길이 route_len, 전압 강하 drop)
11/06 바뀐 것 반영: 문 빔 6쌍은 낱개 LED·포토TR (21시, 승준 SJ-47), 단자대 → 와고 221-415 (+5 V 묶음 / GND 묶음), 서보 허브·게이트 허브 만능기판, 출구 조명 없음, MOSFET 3채널 보드
좌표는 D5g 실제 배치 (11/07 확정, CAP-AI-38) — HX711·DC 잭 자리만 [제안].
실행: python3 design/circuit/harness.py → design/circuit/out/harness.csv, 화면에 요약
"""
import csv
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "control_sim"))
import elec_budget as EB   # noqa: E402

# D5g 실제 자리 (승준 CAP-AI-SJ-49, Issue #7 2026-11-06 21:58 — 부품 가운데 점, 데크 윗면 z 205) [확실 — 승준 모델 값]
# 표시 [제안]은 D5g 모델에 없는 것 → 서현 제안 자리
P_EXTRA = {
    "WAGO": (-5, -67, 211), "SERVO_HUB": (0, 66, 214), "GATE_HUB": (-92, 1, 214), "MOSFET": (-92, 53, 212),
    "FUSE": (-184, 36, 225), "ESTOP": (-184, 0, 225), "J_I2C": (-67, 1, 215),
    "UNO1": (-94, -48, 212), "UNO2": (-94, -48, 229),          # x −131.5~−56.4, y −75~−21.7, 기판 z 207 / 223.6
    "PI_B": (-81, 32, 578),                                      # 190r 선반 199a 위: x −125.5~−36.9, y 3.4~61, z 568.5~587.5
    "ULN_F": (55, -50, 208), "ULN_X": (170, -30, 478), "ULN_Y": (170, 22, 478),
    "LC": (66.5, 77.5, 236),                                     # 막대 4540 +y 끝 (선이 나가는 곳), 바닥 내림 기준
    "HX711": (66, 95, 210),                                      # [제안] D5g 모델에 없음 — 로드셀 +y 끝 아래 데크 위
    "DCIN": (-184, -22, 225),                                    # [제안] D5g 모델에 없음 — 비상 정지 판 194b의 −y 쪽 (퓨즈 반대편)
}
P = dict(EB.P, **P_EXTRA)
EB.P = P                        # route_len이 이 표를 쓰게

# 커넥터 이름
DUP_F = "듀폰 암 1핀 (UNO 헤더)"
DUP_HDR = "듀폰 2.54 헤더 (허브 기판)"
WAGO = "와고 221-415 (선 끝 8 mm 벗김)"
SOLDER = "허브 기판 납땜"

# (번호 묶음, 이름, 시작, 끝, [(선 이름, 색, AWG, 시작 핀, 끝 핀)], 시작 커넥터, 끝 커넥터, 최대 전류 A, 기본 선 종류)
H = [
    ("P", "어댑터 DC 잭 → 퓨즈", "DCIN", "FUSE", [("+5V 들어옴", "빨강", 20, "잭 +", "퓨즈 1")],
     "DC 잭 단자 납땜/나사", "퓨즈홀더 납땜", 2.5, None),
    ("P", "어댑터 DC 잭 GND → 와고 GND", "DCIN", "WAGO", [("GND", "검정", 20, "잭 −", "와고 GND 1번")], "DC 잭 단자 납땜/나사", WAGO, 2.5, None),
    ("P", "퓨즈 → 비상 정지", "FUSE", "ESTOP", [("+5V 퓨즈 뒤", "빨강", 20, "퓨즈 2", "비상 정지 NC 1")], "퓨즈홀더 납땜", "비상 정지 나사 단자", 2.5, None),
    ("P", "비상 정지 → 와고 +5V", "ESTOP", "WAGO", [("+5V_B", "빨강", 20, "NC 2", "와고 +5V 1번")], "비상 정지 나사 단자", WAGO, 2.5, None),
    ("P", "와고 → ULN2003 F", "WAGO", "ULN_F", [("+5V_B", "빨강", 22, "와고 +5V", "ULN + (5-12V)"), ("GND", "검정", 22, "와고 GND", "ULN −")],
     WAGO, "듀폰 암 (ULN 전원 핀)", EB.I_STEP_PEAK, None),
    ("P", "와고 → ULN2003 X", "WAGO", "ULN_X", [("+5V_B", "빨강", 22, "와고 +5V", "ULN +"), ("GND", "검정", 22, "와고 GND", "ULN −")],
     WAGO, "듀폰 암 (ULN 전원 핀)", EB.I_STEP_PEAK, None),
    ("P", "와고 → ULN2003 Y", "WAGO", "ULN_Y", [("+5V_B", "빨강", 22, "와고 +5V", "ULN +"), ("GND", "검정", 22, "와고 GND", "ULN −")],
     WAGO, "듀폰 암 (ULN 전원 핀)", EB.I_STEP_PEAK, None),
    ("P", "와고 → 서보 허브", "WAGO", "SERVO_HUB", [("+5V_B", "빨강", 20, "와고 +5V", "허브 +"), ("GND", "검정", 20, "와고 GND", "허브 −")],
     WAGO, SOLDER, 2.0, None),
    ("P", "와고 → 게이트 허브", "WAGO", "GATE_HUB", [("+5V_B", "빨강", 22, "와고 +5V", "허브 +"), ("GND", "검정", 22, "와고 GND", "허브 −")],
     WAGO, SOLDER, 0.4, None),
    ("P", "와고 → MOSFET 보드 (조명 전원)", "WAGO", "MOSFET", [("+5V_B", "빨강", 22, "와고 +5V", "보드 V+"), ("GND", "검정", 22, "와고 GND", "보드 GND")],
     WAGO, "보드 나사 단자", 0.5, None),
    ("P", "UNO 1·2 GND → 와고 GND", "UNO1", "WAGO", [("GND U1", "검정", 22, "UNO 1 GND", "와고 GND"), ("GND U2", "검정", 22, "UNO 2 GND", "와고 GND")],
     DUP_F, WAGO, 0.1, None),
    ("P", "레일 감지 (+5V_B → 10 kΩ → UNO 2 D2)", "GATE_HUB", "UNO2", [("RAIL", "주황", 28, "허브 10 kΩ 끝", "UNO 2 D2")], SOLDER, DUP_F, 0.001, None),
    # UNO 1
    ("S", "UNO 1 → ULN2003 F (IN1~4)", "UNO1", "ULN_F", [("IN1", "파랑", 26, "D2", "IN1"), ("IN2", "초록", 26, "D3", "IN2"), ("IN3", "노랑", 26, "D4", "IN3"), ("IN4", "주황", 26, "D5", "IN4")],
     DUP_F, "듀폰 암 (ULN IN 핀)", 0.002, None),
    ("S", "UNO 1 → ULN2003 X (IN1~4)", "UNO1", "ULN_X", [("IN1", "파랑", 26, "D6", "IN1"), ("IN2", "초록", 26, "D7", "IN2"), ("IN3", "노랑", 26, "D8", "IN3"), ("IN4", "주황", 26, "D9", "IN4")],
     DUP_F, "듀폰 암 (ULN IN 핀)", 0.002, None),
    ("S", "UNO 1 → ULN2003 Y (IN1~4)", "UNO1", "ULN_Y", [("IN1", "파랑", 26, "D10", "IN1"), ("IN2", "초록", 26, "D11", "IN2"), ("IN3", "노랑", 26, "D12", "IN3"), ("IN4", "주황", 26, "D13", "IN4")],
     DUP_F, "듀폰 암 (ULN IN 핀)", 0.002, None),
    ("M", "ULN2003 F → 바닥 모터 153", "ULN_F", "M_F", [("모터 5선 (모터에 달린 선)", "파랑·분홍·노랑·주황·빨강", 26, "ULN JST-XH 5", "모터")],
     "JST-XH 5핀 (모터 기본)", "모터 (기본)", EB.I_STEP_PEAK, "stepper"),
    ("M", "ULN2003 X → X 모터 215", "ULN_X", "M_X", [("모터 5선", "파랑·분홍·노랑·주황·빨강", 26, "ULN JST-XH 5", "모터")],
     "JST-XH 5핀", "모터 (기본)", EB.I_STEP_PEAK, "stepper"),
    ("M", "ULN2003 Y → Y 모터 209 (X로 움직임)", "ULN_Y", "M_Y", [("모터 5선", "파랑·분홍·노랑·주황·빨강", 26, "ULN JST-XH 5", "모터")],
     "JST-XH 5핀", "모터 (기본)", EB.I_STEP_PEAK, "stepper"),
    ("V", "서보 허브 → 펜 서보 SG90 205 (X·Y로 움직임)", "SERVO_HUB", "PEN", [("서보 3선", "갈색 GND·빨강 +5V·주황 신호", 26, "허브 헤더 S1", "서보")],
     DUP_HDR, "서보 3핀 (기본)", 0.65, "servo"),
    ("S", "UNO 1 A0 → 서보 허브 S1 신호", "UNO1", "SERVO_HUB", [("PEN 신호", "주황", 26, "A0", "허브 S1 신호")], DUP_F, SOLDER, 0.001, None),
    ("S", "UNO 1 → HX711 (VCC, GND, DT, SCK)", "UNO1", "HX711", [("VCC", "빨강", 26, "5V", "VCC"), ("GND", "검정", 26, "GND", "GND"), ("DT", "흰색", 26, "A1", "DT"), ("SCK", "초록", 26, "A2", "SCK")],
     DUP_F, "듀폰 암 (HX711 헤더)", 0.01, None),
    ("S", "HX711 → 로드셀 (바닥과 함께 움직임)", "HX711", "LC", [("E+", "빨강", 28, "E+", "로드셀 빨강"), ("E−", "검정", 28, "E−", "로드셀 검정"), ("A−", "흰색", 28, "A−", "로드셀 흰색"), ("A+", "초록", 28, "A+", "로드셀 초록")],
     "HX711 납땜", "로드셀 선 (납땜 + 수축튜브)", 0.005, None),
    ("S", "UNO 1 → 원점 F", "UNO1", "SW_F", [("HOME_F", "노랑", 28, "A3", "스위치 NO"), ("GND", "검정", 28, "GND", "스위치 COM")], DUP_F, "스위치 납땜 + 100 nF", 0.001, None),
    ("S", "UNO 1 → 원점 X", "UNO1", "SW_X", [("HOME_X", "노랑", 28, "A4", "스위치 NO"), ("GND", "검정", 28, "GND", "스위치 COM")], DUP_F, "스위치 납땜 + 100 nF", 0.001, None),
    ("S", "UNO 1 → 원점 Y (빔과 함께 움직임)", "UNO1", "SW_Y", [("HOME_Y", "노랑", 28, "A5", "스위치 NO"), ("GND", "검정", 28, "GND", "스위치 COM")], DUP_F, "스위치 납땜 + 100 nF", 0.001, None),
    # UNO 2
    ("V", "서보 허브 → 입구 문 서보 112", "SERVO_HUB", "D_IN", [("서보 3선", "갈색·빨강·주황", 26, "허브 S2", "서보")], DUP_HDR, "서보 3핀 (기본)", 0.75, "servo"),
    ("V", "서보 허브 → 격리 문 서보 170", "SERVO_HUB", "D_CAP", [("서보 3선", "갈색·빨강·주황", 26, "허브 S3", "서보")], DUP_HDR, "서보 3핀 (기본)", 0.75, "servo"),
    ("V", "서보 허브 → 방생 문 서보 176", "SERVO_HUB", "D_REL", [("서보 3선", "갈색·빨강·주황", 26, "허브 S4", "서보")], DUP_HDR, "서보 3핀 (기본)", 0.75, "servo"),
    ("S", "UNO 2 D9·D10·D11 → 서보 허브 S2~S4 신호", "UNO2", "SERVO_HUB", [("DOOR_IN", "주황", 26, "D9", "허브 S2"), ("DOOR_CAP", "주황", 26, "D10", "허브 S3"), ("DOOR_REL", "주황", 26, "D11", "허브 S4")],
     DUP_F, SOLDER, 0.001, None),
    ("S", "UNO 2 → 게이트 허브 (수신 9 + 송신 켜기 1)", "UNO2", "GATE_HUB",
     [(g, "흰색", 28, p, "허브 " + g) for g, p in (("G2", "A0"), ("G2b", "A1"), ("G3", "A2"), ("G3b", "A3"), ("G5", "A4"), ("G5b", "A5"), ("G1", "D7"), ("G4", "D8"), ("G6", "D12"))]
     + [("EMIT_EN", "보라", 28, "D4", "허브 Q4 TRIG")], DUP_F, SOLDER, 0.001, None),
] + [
    ("G", "게이트 허브 → 통로 빛 게이트 %s (Adafruit 2167: 송신 2선 + 수신 3선)" % g, "GATE_HUB", g,
     [("송신 +5V", "빨강", 28, "허브 TX+", "송신 빨강"), ("송신 GND(켜기)", "검정", 28, "허브 Q4 OUT−", "송신 검정"),
      ("수신 +5V", "빨강", 28, "허브 RX+", "수신 빨강"), ("수신 GND", "검정", 28, "허브 GND", "수신 검정"), ("수신 신호", "흰색", 28, "허브 %s (10 kΩ 풀업)" % g, "수신 흰색")],
     DUP_HDR, "게이트 기본 선 + 연장 (납땜 + 수축튜브)", 0.02, "ir")
    for g in ("G1", "G4", "G6")
] + [
    ("G", "게이트 허브 → 문 빔 %s (낱개: IR LED 2선 + 포토TR 2선, 220 Ω·10 kΩ는 허브에)" % g, "GATE_HUB", g,
     [("LED +(220 Ω 뒤)", "빨강", 28, "허브 R220 끝", "LED 긴 다리 A"), ("LED −(켜기)", "검정", 28, "허브 Q4 OUT−", "LED 짧은 다리 K"),
      ("포토TR C", "빨강", 28, "허브 +5V", "포토TR 컬렉터"), ("포토TR E(신호)", "흰색", 28, "허브 %s (10 kΩ → GND)" % g, "포토TR 이미터")],
     DUP_HDR, "LED·포토TR 다리 납땜 + 수축튜브", 0.017, None)
    for g in ("G2", "G2b", "G3", "G3b", "G5", "G5b")
] + [
    ("S", "UNO 2 D3·D5 → MOSFET 보드 (조명 켜기)", "UNO2", "MOSFET", [("L_TOP", "노랑", 26, "D3", "Q1 TRIG"), ("L_BOT", "노랑", 26, "D5", "Q2 TRIG")], DUP_F, "보드 핀", 0.001, None),
    ("L", "MOSFET → 위 조명 182", "MOSFET", "L_TOP", [("+5V", "빨강", 24, "보드 V+", "조명 +"), ("Q1 OUT−", "검정", 24, "Q1 OUT−", "조명 −")], "보드 나사 단자", "조명 납땜", 0.20, None),
    ("L", "MOSFET → 아래 조명", "MOSFET", "L_BOT", [("+5V", "빨강", 24, "보드 V+", "조명 +"), ("Q2 OUT−", "검정", 24, "Q2 OUT−", "조명 −")], "보드 나사 단자", "조명 납땜", 0.10, None),
    # 11/07 (CAP-AI-38): 배터리 상자 INA226 → Pi I2C. 본체 J_I2C(게이트 허브 위, 승준 193j) → Pi 40핀 헤더
    ("S", "J_I2C → Pi I2C (배터리 상자 INA226, 콘센트일 때는 비어 있음)", "J_I2C", "PI_B",
     [("3.3V", "빨강", 28, "J_I2C 1 VS", "Pi 핀 1 (3V3)"), ("GND", "검정", 28, "J_I2C 2 GND", "Pi 핀 6 (GND)"),
      ("SDA", "파랑", 28, "J_I2C 3 SDA", "Pi 핀 3 (GPIO2)"), ("SCL", "노랑", 28, "J_I2C 4 SCL", "Pi 핀 5 (GPIO3)")],
     "JST XH 4P 하우징 (193j에 꽂음)", "듀폰 암 1핀 (Pi 헤더)", 0.001, None),
]

# 사서 쓰는 케이블 — 길이가 모자라지 않는지만 본다 (하네스에 안 넣음)
BOUGHT = [
    ("Pi USB → UNO 1 (USB A–B)", "PI_B", "UNO1", 1000),
    ("Pi USB → UNO 2 (USB A–B)", "PI_B", "UNO2", 1000),
    ("Pi CAM0 → AI 카메라 (22↔15핀 FFC)", "PI_B", "CAM", 300),
]


def cut_len(L):
    """자를 길이: 경로 길이 + 10 % 여유, 10 mm 단위로 올림"""
    return int(math.ceil(L * 1.1 / 10.0) * 10)


def build():
    rows, k = [], {}
    for grp, name, a, b, wires, ca, cb, amps, stock in H:
        L = EB.route_len(a, b)
        if stock:
            need_ext = max(0.0, L - EB.STOCK[stock])
            cut = cut_len(need_ext) if need_ext > 0 else 0
        else:
            cut = cut_len(L)
        k[grp] = k.get(grp, 0) + 1
        hid = "%s%02d" % (grp, k[grp])
        for (w, color, awg, pa, pb) in wires:
            rows.append(dict(id=hid, harness=name, wire=w, color=color, awg=awg, frm=a, frm_pin=pa, frm_conn=ca, to=b, to_pin=pb, to_conn=cb,
                             route_mm=round(L), cut_mm=cut, stock_mm=EB.STOCK.get(stock, 0) if stock else 0,
                             moving=(a in EB.MOVE or b in EB.MOVE),
                             drop_V=round(EB.drop(awg, L / 1000, amps), 3) if amps >= 0.1 else ""))
    return rows


def write_md(rows, tot):
    """묶음별 표 (사람이 보는 것) — design/2026-11-06_하네스표_서현.md 의 2장에 들어감"""
    out, seen = [], {}
    for r in rows:
        seen.setdefault(r["id"], []).append(r)
    out.append("| 번호 | 어디 → 어디 | 선 (색·굵기) | 시작 핀 → 끝 핀 | 자를 길이 | 양 끝 | 움직임 |")
    out.append("|---|---|---|---|---|---|---|")
    for hid, rs in seen.items():
        r0 = rs[0]
        wires = "<br>".join("%s (%s, %d AWG)" % (r["wire"], r["color"], r["awg"]) for r in rs)
        pins = "<br>".join("%s → %s" % (r["frm_pin"], r["to_pin"]) for r in rs)
        if r0["stock_mm"]:
            cut = "기본 %d + 연장 %d" % (r0["stock_mm"], r0["cut_mm"]) if r0["cut_mm"] else "기본 %d (연장 없음)" % r0["stock_mm"]
        else:
            cut = "%d mm" % r0["cut_mm"]
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
    tot = {}
    for r in rows:
        tot[r["awg"]] = tot.get(r["awg"], 0) + r["cut_mm"]
    ids = sorted(set(r["id"] for r in rows))
    print("하네스 %d묶음, 선 %d가닥, 자를 길이 합 %.1f m" % (len(ids), len(rows), sum(tot.values()) / 1000))
    for a in sorted(tot):
        print("  AWG %d: %.1f m" % (a, tot[a] / 1000))
    worst = max((r for r in rows if r["drop_V"] != ""), key=lambda r: r["drop_V"])
    print("가장 큰 전압 강하: %s %s V" % (worst["harness"], worst["drop_V"]))
    print("움직이는 선:", sorted(set(r["id"] for r in rows if r["moving"])))
    print(p)
    chk = []
    for nm, x, y, have in BOUGHT:
        need = cut_len(EB.route_len(x, y))
        chk.append("| %s | %d mm | %d mm | %s |" % (nm, need, have, "충분" if have >= need else "**모자람**"))
        print("  산 케이블 %s: 필요 %d / 있음 %d" % (nm, need, have))
    with open(os.path.join(HERE, "out", "harness_table.md"), "w", encoding="utf-8") as f:
        f.write(write_md(rows, tot))
        f.write("\n\n**사서 쓰는 케이블 길이 확인** (경로 + 10 %)\n\n| 케이블 | 필요 | 있음(산 것) | 판단 |\n|---|---|---|---|\n" + "\n".join(chk) + "\n")
    return rows, tot


if __name__ == "__main__":
    main()
