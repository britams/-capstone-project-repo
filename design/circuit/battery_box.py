# -*- coding: utf-8 -*-
"""배터리 상자 회로 (서현, 2026-11-06, CAP-AI-35 — 제어·회로 서현 위임, AI 판단)

본체는 바꾸지 않는다: 본체 입력 2개(Pi USB-C, 구동 레일 DC 5.5×2.1)에 콘센트 어댑터 대신 이 상자의 플러그 2개를 꽂는다.
  LiFePO4 12.8 V 20 Ah (BMS) → 퓨즈 5 A → INA226 (0.01 Ω) → [충전 단자] → 주 스위치 → 강압 A (5.15 V → USB-C → Pi)
                                                                               → 강압 B (5.0 V → 배럴 → 본체 퓨즈 3 A → 비상 정지)
하는 일
  1) 넷(연결) 한 곳에 적기 + 검사 (퓨즈가 맨 앞, 충전 단자가 분류 저항 뒤, 강압 출력끼리 안 이어짐 …)
  2) 전류·퓨즈·전압 강하·INA226 설정값 계산
  3) GND 고리(배터리일 때만 생김) 전류 나눔 계산 → 대책
  4) 회로도 4장 design/img/circuit/회로도_4_배터리상자.png, 결과 out/battery_box.json
실행: python design/circuit/battery_box.py
표기: [확실] 사양·계산 / [가능성 높음] / [추측]
"""
import json
import os
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
IMG = os.path.join(HERE, "..", "img", "circuit")
sys.path.insert(0, os.path.join(HERE, "..", "control_sim"))
import elec_budget as eb  # noqa: E402

# ---------------------------------------------------------------------------
# 0) 값
# ---------------------------------------------------------------------------
V_NOM, V_FULL, V_LOW, V_BMS = 12.8, 14.6, 12.0, 10.0   # LiFePO4 4셀: 공칭 / 충전 끝 / '부족' 판단(부하 중) / BMS 차단 [가능성 높음 — 셀 3.2/3.65/3.0/2.5 V]
AH = 20.0                                               # 11/06 결정 (2일)
ETA = eb.ETA_BUCK                                       # 0.90 [가능성 높음]
V_PI_SET = 5.15                                         # 강압 A 출력 (Pi 5 저전압 경고 약 4.63 V보다 여유) [가능성 높음]
V_DRV_SET = 5.00
I_FUSE_BOX = 5.0                                        # 상자 퓨즈 5×20 5 A (본체 E3와 같은 F-520 홀더)
I_FUSE_BODY = 3.0                                       # 본체 구동 레일 퓨즈 (바뀌지 않음)

OHM_PER_M = {18: 0.0210, 20: 0.0333, 22: 0.0530, 24: 0.0842, 28: 0.2129}   # 구리 20 °C [확실 — AWG 표]
R_CONTACT = 0.010                                       # 커넥터 접점 하나 [추측 — 실측 필요]

# Pi 레일 (W) — elec_budget LOADS에서
L = eb.LOADS
P_PI_TYP = 5.7                                          # 대기 (elec_budget state_table) [가능성 높음]
P_PI_PEAK = L["pi5"]["peak"] + L["ai_camera"]["run"] + L["ai_hat"]["run"] + 2 * L["uno"]["on"] + L["hx711"]["on"]
# 구동 레일 (A @5 V)
I_DRV_TYP = 0.344                                       # 대기 (아래 조명 켬)
I_DRV_RULE = 1.80                                       # 규칙 지킬 때 최대 (worst_cases)
I_DRV_FUSE = I_FUSE_BODY                                # 본체 퓨즈가 끊기기 직전 = 설계 최악


def bat_current(p_pi, i_drv, v_bat):
    return (p_pi / ETA + i_drv * V_DRV_SET / ETA) / v_bat


# ---------------------------------------------------------------------------
# 1) 넷
# ---------------------------------------------------------------------------
NETS = defaultdict(list)


def con(net, *nodes, awg=18, note=""):
    for n in nodes:
        NETS[net].append((n, awg, note))


con("BAT+", "BAT.+", "F2.1", awg=18, note="XT60 (배터리 ↔ 상자), 퓨즈는 배터리 + 단자에서 10 cm 안")
con("VF2", "F2.2", "INA.IN+", awg=18, note="5×20 5 A")
con("VBOX", "INA.IN-", "INA.VBUS", "J_CHG.+", "SW_M.1", awg=18, note="충전 단자는 분류 저항 뒤 → 충전 전류도 INA226이 셈")
con("VSW", "SW_M.2", "BK_A.VIN+", "BK_B.VIN+", awg=18, note="주 스위치 (DC 12 V 10 A 이상)")
con("GND_BOX", "BAT.-", "J_CHG.-", "BK_A.VIN-", "BK_B.VIN-", "BK_A.OUT-", "BK_B.OUT-", "J_PI.GND", "J_DRV.-", "INA.GND",
    awg=18, note="GND 한 점 = 배터리 − 단자 옆 (별 모양으로 모음)")
con("5V1_PI", "BK_A.OUT+", "J_PI.VBUS", awg=20, note="USB-C 수 플러그 전원 전용 꼬리선 0.5 m, 강압 A 5.15 V · 전류 제한 4 A")
con("5V_DRV", "BK_B.OUT+", "J_DRV.+", awg=18, note="DC 5.5×2.1 수 플러그 1.0 m, 강압 B 5.0 V · 전류 제한 3.2 A")
con("I2C_SDA", "INA.SDA", "J_I2C.SDA", awg=28, note="4심 1 m → 본체 J_I2C → Pi GPIO2 (100 kHz)")
con("I2C_SCL", "INA.SCL", "J_I2C.SCL", awg=28, note="→ Pi GPIO3")
con("I2C_VCC", "INA.VS", "J_I2C.VCC", awg=28, note="Pi 3.3 V (Pi가 꺼지면 INA226도 꺼짐)")
con("I2C_GND", "INA.GND", "J_I2C.GND", awg=28, note="")

PARTS = {
    "BAT": "LiFePO4 12.8 V 20 Ah (BMS 들어 있음, 연속 10 A 이상)",
    "F2": "퓨즈홀더 F-520 + 5×20 5 A",
    "INA": "INA226 모듈 — 분류 저항 R010 (0.01 Ω)",
    "J_CHG": "충전 단자 XT60 암 (LiFePO4 전용 충전기 14.6 V)",
    "SW_M": "주 스위치 (로커/토글, DC 12 V 10 A 이상)",
    "BK_A": "강압 모듈 A (입력 8~36 V, 출력 조정 CV/CC, 5 A급) → 5.15 V",
    "BK_B": "강압 모듈 B (같은 것) → 5.0 V",
    "J_PI": "USB-C 수 플러그 꼬리선 (전원 전용, 20 AWG)",
    "J_DRV": "DC 5.5×2.1 수 플러그 꼬리선 (18 AWG)",
    "J_I2C": "4핀 커넥터 + 4심 선 1 m (본체 J_I2C와 짝)",
}


def check():
    errs = []
    for net, nodes in NETS.items():
        if len({n for n, _, _ in nodes}) < 2:
            errs.append("넷 %s 끝이 하나뿐" % net)
    ends = {n for v in NETS.values() for n, _, _ in v}
    for p in PARTS:
        if not any(e.startswith(p + ".") for e in ends):
            errs.append("부품 %s가 아무 데도 안 이어짐" % p)
    where = {n: net for net, v in NETS.items() for n, _, _ in v}
    # (1) 배터리 +는 퓨즈에만
    if {n for n, _, _ in NETS["BAT+"]} != {"BAT.+", "F2.1"}:
        errs.append("배터리 +가 퓨즈 말고 다른 데로 감")
    # (2) 충전 단자는 분류 저항 뒤(IN−) — 그래야 충전·방전을 같은 저항으로 셈
    if where.get("J_CHG.+") != where.get("INA.IN-"):
        errs.append("충전 단자가 INA226 IN− 쪽이 아님")
    # (3) 강압 입력은 스위치 뒤
    for b in ("BK_A.VIN+", "BK_B.VIN+"):
        if where.get(b) != where.get("SW_M.2"):
            errs.append("%s가 스위치 뒤가 아님" % b)
    # (4) 강압 출력 +끼리 안 이어짐, 출력이 배터리 쪽과 안 이어짐
    if where.get("BK_A.OUT+") == where.get("BK_B.OUT+"):
        errs.append("강압 A·B 출력이 이어짐 (금지)")
    for o in ("BK_A.OUT+", "BK_B.OUT+"):
        if where.get(o) in ("BAT+", "VF2", "VBOX", "VSW"):
            errs.append("%s가 12 V 쪽에 이어짐" % o)
    # (5) INA226 버스 전압은 IN− 쪽, GND는 상자 GND (I2C GND와 같은 점)
    if where.get("INA.VBUS") != "VBOX":
        errs.append("INA226 VBUS가 IN− 쪽이 아님")
    # (6) 선 굵기: 12 V 쪽 18 AWG 이상
    for net in ("BAT+", "VF2", "VBOX", "VSW"):
        if any(awg > 18 for _, awg, _ in NETS[net]):
            errs.append("넷 %s 선이 18 AWG보다 가늚" % net)
    return errs


# ---------------------------------------------------------------------------
# 2) 계산
# ---------------------------------------------------------------------------
def calc():
    r = {}
    r["P_pi_typ_W"], r["P_pi_peak_W"] = P_PI_TYP, round(P_PI_PEAK, 2)
    r["I_pi_peak_A"] = round(P_PI_PEAK / V_PI_SET, 2)
    cases = {
        "대기 (공칭 12.8 V)": (P_PI_TYP, I_DRV_TYP, V_NOM),
        "규칙 최대 (12.0 V, 부족 직전)": (P_PI_PEAK, I_DRV_RULE, V_LOW),
        "설계 최악 (10.0 V BMS 직전, 본체 퓨즈 3 A 직전)": (P_PI_PEAK, I_DRV_FUSE, V_BMS),
    }
    r["I_bat"] = {k: round(bat_current(*v), 2) for k, v in cases.items()}
    worst = r["I_bat"]["설계 최악 (10.0 V BMS 직전, 본체 퓨즈 3 A 직전)"]
    r["fuse_ok"] = worst < 0.8 * I_FUSE_BOX          # 퓨즈 정격의 80 % 아래로 쓰기 [가능성 높음 — 흔한 경감 규칙]
    r["fuse_margin"] = round(I_FUSE_BOX / worst, 2)

    # INA226 [확실 — TI 데이터시트: 분류 전압 최대 81.92 mV, LSB 2.5 µV, CAL = 0.00512 / (Current_LSB × R)]
    ina = {}
    for name, R in (("R100 (흔한 모듈 0.1 Ω)", 0.1), ("R010 (0.01 Ω, 고름)", 0.01)):
        fs = 0.08192 / R
        ina[name] = dict(full_scale_A=round(fs, 2), ok=fs > 1.25 * worst, shunt_W_at_worst=round(worst ** 2 * R, 3),
                         drop_mV_at_worst=round(worst * R * 1000, 1), resolution_mA=round(2.5e-6 / R * 1000, 3))
    i_lsb = 0.0002                                       # 0.2 mA (최소 = 5 A / 32768 = 0.153 mA보다 크게, 깔끔한 수)
    ina["설정"] = dict(R_shunt=0.01, current_LSB_A=i_lsb, CAL=round(0.00512 / (i_lsb * 0.01)), power_LSB_W=25 * i_lsb,
                     config="평균 16회, 변환 1.1 ms (0x4527) → 약 35 ms마다 새 값, Pi는 0.5 s마다 읽음",
                     addr="0x40 (A0·A1 = GND)", i2c="100 kHz, 선 1 m — 모듈 풀업 10 kΩ + Pi 1.8 kΩ [가능성 높음]")
    r["ina226"] = ina

    # 전압 강하 — Pi 꼬리선 (20 AWG 0.5 m 왕복 + USB-C 접점 2) / 구동 꼬리선 (18 AWG 1.0 m 왕복 + 배럴 접점 2)
    i_pi = P_PI_PEAK / V_PI_SET
    drop_pi = i_pi * (2 * 0.5 * OHM_PER_M[20] + 2 * R_CONTACT * 1.5)
    drop_drv = I_DRV_RULE * (2 * 1.0 * OHM_PER_M[18] + 2 * R_CONTACT)
    r["drop"] = dict(pi_V=round(drop_pi, 3), pi_at_board_V=round(V_PI_SET - drop_pi, 2), pi_undervolt_V=4.63,
                     drv_V=round(drop_drv, 3), drv_at_jack_V=round(V_DRV_SET - drop_drv, 2))

    # 밤 (Pi 꺼짐 → INA226도 꺼짐 → 셀 수 없음): 밤 전력 × 시간을 Pi가 아침에 더함
    night_W = (0.034 * V_DRV_SET + L["pi5"]["halt"]) / ETA + eb.BUCK_IQ_W
    r["night"] = dict(W=round(night_W, 3), Wh_15h=round(night_W * 15, 2), mA_bat=round(night_W / V_NOM * 1000, 1),
                      note="INA226은 적산을 안 함(INA228은 함). Pi가 켜져 있는 동안 P를 더하고, 밤 몫은 '밤 W × 꺼진 시간'으로 더함")
    r["days"] = eb.battery_days(eb.daily(20, 9.0, False, True, True)["load_Wh"], 0, 9.0, AH)
    return r


# ---------------------------------------------------------------------------
# 3) GND 고리 — 콘센트일 때는 어댑터 2개가 서로 떨어져(절연) 있어 고리가 없다.
#    배터리 상자는 강압 2개의 GND가 배터리 −에서 만난다 → 본체 안에서도 UNO GND(와고) ↔ UNO USB ↔ Pi GND로 이어져 있으므로
#    구동 레일 되돌이 전류가 (a) 배럴 GND 선, (b) UNO GND 선 → UNO USB 케이블 → Pi → USB-C 꼬리선 두 길로 나뉜다.
# ---------------------------------------------------------------------------
def ground_loop():
    out = {}
    r_uno_path = (0.5 * OHM_PER_M[22] + 0.5 * OHM_PER_M[28] + 3 * R_CONTACT)   # UNO GND 선 22 AWG 0.5 m + USB A-B GND 28 AWG 0.5 m + 접점 3
    r_b = r_uno_path / 2 + 0.5 * OHM_PER_M[20] + 2 * R_CONTACT                   # UNO 2개 나란히 + Pi USB-C 꼬리선 GND
    for name, awg, m in (("배럴 꼬리선 20 AWG 1.5 m (흔한 어댑터 선)", 20, 1.5), ("배럴 꼬리선 18 AWG 1.0 m (고름)", 18, 1.0)):
        r_a = m * OHM_PER_M[awg] + 0.3 * OHM_PER_M[20] + 2 * R_CONTACT       # 꼬리선 + 본체 잭→와고 20 AWG 0.3 m + 접점 2
        share = r_a / (r_a + r_b)
        i_usb = I_DRV_RULE * share
        out[name] = dict(R_barrel_mOhm=round(r_a * 1000), R_usb_path_mOhm=round(r_b * 1000), share_usb=round(share, 2),
                         I_through_usb_A=round(i_usb, 2), I_per_uno_cable_A=round(i_usb / 2, 2),
                         offset_mV=round(i_usb / 2 * (0.5 * OHM_PER_M[28] + R_CONTACT) * 1000))
    out["판단"] = ("UNO USB는 풀 스피드(12 Mbps)라 GND가 수십 mV 어긋나도 신호 문턱(0.8/2.0 V)에 한참 못 미친다 [가능성 높음]. "
                 "그래도 스테핑 전류가 펄스로 흘러 잡음이 될 수 있어 ① 배럴 꼬리선 18 AWG 1.0 m ② GND는 배터리 −에서 별 모양 ③ 브링업 B6에서 "
                 "'UNO GND ↔ Pi GND 전압 < 50 mV, 1시간 시리얼 오류 0'을 확인. 넘으면 강압 B를 절연형 Mean Well SD-15A-5 (9.2~18 V → 5 V 3 A, 절연 2 kV)로 바꾼다")
    # 절연형으로 바꿀 때 손해 (효율 68 % — RS 페이지)
    e_day = I_DRV_TYP * V_DRV_SET * 9
    out["SD-15A-5로 바꾸면"] = dict(extra_Wh_day=round(e_day / 0.68 - e_day / ETA, 1),
                                 note="무부하 전류는 공개값 못 찾음 → 밤 손실은 실측 [추측]")
    return out


# ---------------------------------------------------------------------------
# 4) 회로도 4장
# ---------------------------------------------------------------------------
def sheet():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.family": "Noto Sans CJK JP"})
    import schemdraw
    import schemdraw.elements as elm
    schemdraw.config(font="Noto Sans CJK JP", fontsize=11)
    with schemdraw.Drawing(file=os.path.join(IMG, "회로도_4_배터리상자.png"), show=False, dpi=150) as d:
        d += elm.Label().label("회로도 4/4 — 배터리 상자 (본체는 그대로, 플러그 2개만 바꿔 꽂음)", fontsize=14).at((0, 4.0))
        d += (bat := elm.BatteryCell().up(3).at((0, -1.5)))
        d += elm.Label().label("LiFePO4\n12.8 V 20 Ah\n(BMS)", halign="right").at((-0.8, 0))
        d += elm.Line().right(0.8).at(bat.end)
        d += elm.Fuse().right().label("F2\n5×20 5 A", loc="top")
        d += elm.ResistorIEC().right().label("INA226 분류\n0.01 Ω", loc="top")
        d += (nv := elm.Dot().label("VBOX", loc="bottom"))
        d += elm.Switch().right().label("주 스위치", loc="top")
        d += (ns := elm.Dot())
        d += elm.Line().right(1.0)
        d += (bka := elm.Ic(pins=[elm.IcPin(name="IN", side="left", anchorname="pin1"), elm.IcPin(name="OUT", side="right", anchorname="pin2")],
                            edgepadW=1.6, label="강압 A\n5.15 V\n제한 4 A").anchor("pin1"))
        d += elm.Line().right(1.2).at(bka.pin2)
        d += elm.Label().label("USB-C → Pi 5 (20 AWG 0.5 m)", loc="right")
        d += elm.Line().down(3.0).at(ns.center)
        d += elm.Line().right(1.0)
        d += (bkb := elm.Ic(pins=[elm.IcPin(name="IN", side="left", anchorname="pin1"), elm.IcPin(name="OUT", side="right", anchorname="pin2")],
                            edgepadW=1.6, label="강압 B\n5.0 V\n제한 3.2 A").anchor("pin1"))
        d += elm.Line().right(1.2).at(bkb.pin2)
        d += elm.Label().label("DC 5.5×2.1 → 본체 퓨즈 3 A → 비상 정지 (18 AWG 1.0 m)", loc="right")
        d += elm.Line().up(1.6).at(nv.center)
        d += elm.Label().label("충전 단자 XT60 (14.6 V 전용 충전기, 0 °C 아래 충전 금지)", loc="top")
        d += elm.Line().down(1.5).at(bat.start)
        d += (g := elm.Ground().label("GND 한 점 (배터리 −) — 강압 A·B 입력·출력 −, 충전 −, INA226 GND", loc="right"))
        d += elm.Label().label("INA226: VS·GND·SDA·SCL 4심 1 m → 본체 J_I2C → Pi 3.3 V·GND·GPIO2·GPIO3 (주소 0x40, CAL 2560, 0.2 mA/LSB)", fontsize=10, halign="left").at((-1.5, -5.8))
        d += elm.Label().label("Pi가 0.5 s마다 읽음 → 남은 에너지 15 % 또는 부하 중 12.0 V 아래 = '부족' → 처리 끝내고 문 열고 Pi 끔", fontsize=10, halign="left").at((-1.5, -6.4))
        d += elm.Label().label("배터리일 때만 GND 고리가 생김 (강압 2개 GND가 만남) → 배럴 선 18 AWG, 별 모양 GND, B6에서 < 50 mV 확인", fontsize=10, halign="left").at((-1.5, -7.0))


def main():
    errs = check()
    res = dict(parts=PARTS, nets={k: [n for n, _, _ in v] for k, v in NETS.items()}, check=errs or "통과",
               calc=calc(), ground_loop=ground_loop())
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "battery_box.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print("넷 %d개, 끝 %d개, 검사: %s" % (len(NETS), sum(len(v) for v in NETS.values()), res["check"]))
    print(json.dumps(res["calc"], ensure_ascii=False, indent=1))
    print(json.dumps(res["ground_loop"], ensure_ascii=False, indent=1))
    try:
        sheet()
        print("회로도 4장 → design/img/circuit/회로도_4_배터리상자.png")
    except Exception as e:
        print("회로도 실패:", repr(e))
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
