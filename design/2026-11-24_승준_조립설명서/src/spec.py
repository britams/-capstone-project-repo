# -*- coding: utf-8 -*-
"""조립 설명서 스펙 — 단계, 부품, 렌더 작업.
CAD 키 = 승준 PC FreeCAD 'ASM_manual' 문서의 객체 이름 (D5g_full_SJ1123_플라스틱판_NEMA17 사본 + 나눈 키).
"""
import json

# ---------------------------------------------------------------- 보기 방향
FR = (-1, 1, -0.8)    # 앞-오른쪽-위에서
FL = (1, 1, -0.8)     # 앞-왼쪽-위에서
BR = (-1, -1, -0.8)   # 뒤-오른쪽-위에서
BL = (1, -1, -0.8)    # 뒤-왼쪽-위에서
TOPV = (0, 0, -1)

# ---------------------------------------------------------------- 키 묶음
POSTS_F = ["P100a_post_1", "P100a_post_2"]
POSTS_B = ["P100a_post_3", "P100a_post_4"]
RAILS_F = ["P100b_rail_0_xm170", "P100b_rail_deck_xm170", "P100b_rail_gantry_xm170", "P100b_rail_top_xm170"]
RAILS_B = ["P100b_rail_0_xp170", "P100b_rail_deck_xp170", "P100b_rail_gantry_xp170", "P100b_rail_top_xp170"]
RAILS_L = ["P100b_rail_0_ym170", "P100b_rail_deck_ym170", "P100b_rail_gantry_ym170", "P100b_rail_top_ym170"]
RAILS_R = ["P100b_rail_0_yp170", "P100b_rail_deck_yp170", "P100b_rail_gantry_yp170", "P100b_rail_top_yp170"]
DECK_X = ["P100c_cross_deck_ym80", "P100c_cross_deck_yp80"]
TOP_X = ["P100c_cross_top_ym80", "P100c_cross_top_yp80"]
GANTRY = ["P100d_gantry_rail_xm18"]
FRAME_ALL = POSTS_F + POSTS_B + RAILS_F + RAILS_B + RAILS_L + RAILS_R + DECK_X + GANTRY + \
    ["brk_front", "brk_back", "brk_left", "brk_right", "tb_deck", "tb_gantry"]

UNO = ["uno1_st", "uno2_st", "P191_arduino_uno", "SH1", "E01", "SH2"]
MOS = ["SJX04", "SJ53C_mosfet_parts", "SJX05", "SJ53C_board_spacers", "SJ53C_board_screws"]
PWR = ["XL1", "XL2", "JK1", "FU1", "SJW1", "SJW2"]
ESTOP = ["SJ_estop_plate", "E03", "estop_bolts"]

MK1 = ["V3_P07", "V3_P09", "bar_bolts_bar"]
MK2 = ["V3_P03", "V3_P04", "V3_P11"]
MK3 = ["V3_P00", "V3_P08"]
MK4 = ["V3_P06", "V3_P05"]
MK5 = ["V3_P01", "V3_P02"]
MK6 = ["B1_housing", "P176_release_gate_housing", "ear_112", "ear_176"]
MK7 = ["P112_entry_gate_servo_MG90S", "P112_entry_gate_servo_spline", "SW_104", "SW_105",
       "P176_release_gate_servo_MG90S", "P176_release_gate_servo_spline",
       "SJ53_servo_screws_entry", "SW_116", "SJ53_servo_screws_rel"]
MK8 = ["P112_entry_gate_horn", "P112_entry_gate_flap", "SW_106", "SW_103",
       "P176_release_gate_horn", "P176_release_gate_flap"]
MK9 = ["GM_G2", "GM_G3b", "GM_G5"]
MK_ALL = MK1 + MK2 + MK3 + MK4 + MK5 + MK6 + MK7 + MK8 + MK9
CUP = ["CupBracket", "P219_cap_cup"]

CAR1 = ["PL_CP_acryl", "B2_116", "XYn99"]
CAR2 = ["PL_Ynut_T8", "PL_CP_M3_nut"]
CAR3 = ["falcs", "falcs_screws", "PL_SP_metal"]
CAR4 = ["sp_set", "spsv_standoffs", "sv_pan", "PL_SV_PETG", "P205_z_servo_SG90", "P205s_z_servo_spline", "XYn100"]
HV = ["B3_115", "C203p", "clip_screws"]
CAR6 = ["shoulder_set", "S202s_spacer", "P205h_z_servo_horn"]
CAR_ALL = CAR1 + CAR2 + CAR3 + CAR4 + HV + CAR6
BEAM_A = ["PL_YA_PETG", "sc8uu_A", "sc_csk_A"]
BEAM_B = ["PL_YB_PETG", "sc8uu_B", "sc_csk_B"]
XN = ["PL_XN_PETG", "PL_Xnut_T8", "PL_XN_M3x6", "HS_227y_home_switch_Y", "XYn114", "HS_227ys_switch_screws_Y"]
XNL = ["beamL", "beamL_bolts"]
YRODS = ["B2_113", "rodend_A", "rodend_B"]
YM1 = ["PL_YM_PETG", "ym_standoffs", "ym_csk", "PL_Ymotor_N17", "PL_Ymotor_M3"]
YM2 = ["PL_Yscrew_T8", "ym_pan"]
XRODS = ["P213_x_rods", "B1_111"]
XY_ALL = CAR_ALL + BEAM_A + BEAM_B + XN + XNL + YRODS + YM1 + YM2 + XRODS
SKB = ["B1_112"]
XMOT = ["PL_217_moved", "PL_Xmotor_N17", "PL_Xmotor_M3low", "PL_217_M4", "PL_Xscrew_T8"]
XHOME = ["XH_arm", "XH_bolts", "HS_227x_home_switch_X", "XYn113", "HS_227xs_switch_screws_X"]
DRV = ["DRV_br", "SJ10", "SJ11", "DRV_so", "drv_board", "drv_modules"]
MARKER = ["P201_marker"]

TOPX = TOP_X + ["tb_top"]
CAMU = ["CAM_PLATE", "P180_camera", "SJ53_cam_m2", "CAM_LED", "B2_96"]
TOPP = ["P105_top_plate", "top_bolts"]
PIU = ["pi_PV", "pi_PB", "B2_97", "SJR_pi5_st", "SJR_pi5"]
PIB = ["pi_bolts"]

TRAP = ["PREF_trap_bait_cup", "PREF_trap_body", "PREF_trap_funnels", "PREF_trap_awning", "PREF_trap_ring"]
COLLAR = ["P102_collar", "P100m_bolt_M3x10_deck"]
ENTRY = ["P111_entry_funnel", "P110_entry_duct"]
ISO = ["SW_117", "P173_isolation_funnel", "P104_dome_coupling", "PREF_trap_container", "PREF_trap_cap", "PREF_trap_silicone_star"]

# ---------------------------------------------------------------- 재질 색 (표지·부품 사진)
ALU = (0.80, 0.82, 0.85); WHITE = (0.97, 0.97, 0.96); CLEAR = (0.72, 0.88, 0.97)
PRINT = (1.00, 0.70, 0.36); DARK = (0.28, 0.29, 0.31); STEEL = (0.70, 0.71, 0.74)
PCB_B = (0.10, 0.42, 0.62); PCB_G = (0.12, 0.48, 0.28); PCB_R = (0.80, 0.18, 0.15)
YEL = (1.0, 0.84, 0.10); BRASS = (0.85, 0.70, 0.35); TRAPC = (0.62, 0.80, 0.62); BLK = (0.16, 0.16, 0.18)
SERVO_B = (0.22, 0.36, 0.80); RED = (0.85, 0.12, 0.12)


def mat(k):
    if k.startswith(("P100", "brk_", "tb_", "V3_P07", "V3_P09")):
        return ALU
    if k in ("P101_deck", "P105_top_plate", "CAM_PLATE", "pi_PB", "CupBracket", "P102_collar",
             "P104_dome_coupling", "V3_P05", "PL_CP_acryl", "CAM_LED", "SJ53C_board_spacers"):
        return WHITE
    if k in ("V3_P01", "P110_entry_duct", "SW_117"):
        return CLEAR
    if k in ("V3_P00", "B1_housing", "P176_release_gate_housing", "P111_entry_funnel", "P173_isolation_funnel",
             "PL_YA_PETG", "PL_YB_PETG", "PL_XN_PETG", "PL_YM_PETG", "PL_SV_PETG", "C203p", "S202s_spacer"):
        return PRINT
    if k in ("PL_Xmotor_N17", "PL_Ymotor_N17", "V3_P03", "E03"):
        return DARK
    if k in ("P201_marker", "P219_cap_cup"):
        return YEL
    if k.startswith("PREF_trap"):
        return TRAPC
    if k in ("P191_arduino_uno", "E01", "XL1", "XL2", "drv_board"):
        return PCB_B
    if k in ("SH1", "SH2", "JK1", "FU1"):
        return BLK
    if k in ("SJX04", "SJ53C_mosfet_parts", "drv_modules"):
        return PCB_R
    if k in ("SJR_pi5", "P180_camera", "XYn113", "XYn114"):
        return PCB_G
    if k in ("P112_entry_gate_servo_MG90S", "SW_104", "P176_release_gate_servo_MG90S", "GM_G2", "GM_G3b", "GM_G5"):
        return BLK
    if k in ("P205_z_servo_SG90",):
        return SERVO_B
    if k in ("PL_Xnut_T8", "PL_Ynut_T8", "uno1_st", "uno2_st", "SJX05", "spsv_standoffs", "DRV_so", "SJR_pi5_st", "B2_96"):
        return BRASS
    if k in ("SJW1",):
        return (0.85, 0.85, 0.85)
    if k in ("SJW2",):
        return (0.95, 0.55, 0.10)
    return STEEL


# ---------------------------------------------------------------- 부품 목록 (사진 = CAD 키 또는 나사 그림)
# kind: cad → thumb = (키 목록) 또는 [(키, [고체 번호])]
P = {}


def part(pid, name, desc, thumb=None, box="", kind="cad", spec=None, later=False):
    P[pid] = dict(id=pid, name=name, desc=desc, thumb=thumb, box=box, kind=kind, spec=spec, later=later)


# 프레임
part("post610", "기둥 610", "2020 알루미늄 막대 610 mm — 네 모서리 기둥 (빨강 칠한 것)", [("P100a_post_1", None)], "5-①")
part("rail320", "레일 320", "2020 알루미늄 막대 320 mm — 층마다 테두리·가로대 (파랑 칠한 것)", [("P100b_rail_0_xm170", None)], "5-①")
part("bar156", "세운 막대 156", "2020 알루미늄 막대 156 mm — 마킹실을 받침 (초록 칠한 것)", [("V3_P07", None)], "5-①")
part("lbr", "L 브래킷 DCB 2025", "막대 두 개를 직각으로 잇는 알루미늄 ㄱ자 조각", [("P100e_bracket_2020_L", [0])], "5-①")
# 데크·전기
part("deck101", "데크 판 101", "흰 아크릴 5T, 230 × 180 — 가운데 큰 구멍", [("P101_deck", None)], "5-①")
part("uno", "아두이노 UNO", "작은 컴퓨터. ① = 움직임 (XY·펜·바닥), ② = 문·빛 게이트·조명", [("P191_arduino_uno", None)], "5-②")
part("shield", "센서 쉴드 V5.0", "UNO 위에 꽂는 판 — 3핀 선을 납땜 없이 꽂음", [("SH1", None)], "5-②")
part("mosfet", "MOSFET 4채널 모듈", "빨간 판 — LED·빛 게이트 송신·펌프의 12 V를 켜고 끔", [("SJX04", None), ("SJ53C_mosfet_parts", None)], "5-②")
part("xl4015", "강압 모듈 XL4015", "12 V를 낮춤 — ① 5.0 V (서보·센서), ② 7.4 V (mightyZAP)", [("XL1", None)], "5-②")
part("dcjack", "DC 잭 → 나사 단자", "12 V 5 A 어댑터 플러그를 꽂는 곳", [("JK1", None)], "5-②")
part("fuse", "퓨즈 홀더 + 5 A 퓨즈", "전기가 너무 세게 흐르면 퓨즈가 끊어져 보호", [("FU1", None)], "5-②")
part("wago", "와고 221-415", "주황 레버를 올리고 선을 넣고 내리면 이어짐 (5구)", [("SJW1", [0])], "5-②")
part("estopplate", "비상 정지 판 194b", "알루미늄 4T, 둥근 구멍 Ø25.5", [("SJ_estop_plate", None)], "5-②")
part("estop", "비상 정지 버튼", "빨간 버섯 버튼 — 누르면 12 V 전체가 꺼짐", [("E03", None)], "5-②")
# 마킹실
part("mzap", "mightyZAP 직선 서보", "막대가 위아래로 움직이는 모터 — 바닥을 밀어 올림", [("V3_P03", None), ("V3_P04", None)], "1")
part("box300", "마킹실 상자 300", "3D 프린트 — 말벌 한 마리가 들어가는 둥근 방 (안 Ø33)", [("V3_P00", None)], "2-①")
part("floor304", "바닥 원판 304", "흰 아크릴 Ø32 × 2T — 말벌을 위로 살짝 밀어 올림 (2장 중 1장, 1장 예비)", [("V3_P05", None)], "2-①")
part("grid300p", "격자판 300p", "투명 아크릴 38 × 38 × 2T — 네모 구멍으로 펜이 들어가 점을 찍음 (2장 중 1장)", [("V3_P01", None)], "2-①")
part("housing112", "입구·격리 문 하우징 112", "3D 프린트 — 문 2개 (입구·격리) 집", [("B1_housing", None)], "2-①")
part("housing176", "방생 문 하우징 176", "3D 프린트 — 방생 문 집", [("P176_release_gate_housing", None)], "2-①")
part("mg90s", "MG90S 서보", "검은 작은 모터 — 문을 돌려 여닫음 (3개: 입구·격리·방생)", [("P112_entry_gate_servo_MG90S", None), ("P112_entry_gate_servo_spline", None)], "1")
part("horn", "서보 혼", "서보 봉지에 든 날개 — 서보 축에 끼움", [("P112_entry_gate_horn", None)], "1")
part("flap", "문판 112f · 170f · 176f", "알루미늄 1.5T 작은 판 — 혼에 붙어 문이 됨", [("P112_entry_gate_flap", None)], "2-①")
part("gate", "빛 게이트 Adafruit 2167", "송신·수신 한 쌍 — 빛이 끊기면 말벌이 지나간 것", [("GM_G2", None)], "2-①")
part("cup220", "컵 받침 220", "흰 아크릴 5T 작은 띠 — 마커 뚜껑을 얹음", [("CupBracket", None)], "2-②")
part("cap219", "마커 뚜껑", "여분 샤피 마커의 뚜껑 — 펜 끝이 마르지 않게", [("P219_cap_cup", None)], "2-②")
# XY
part("cp", "캐리지판 CP", "흰 아크릴 3T — 펜 장치의 몸통 (아크릴몰)", [("PL_CP_acryl", None)], "2-②")
part("lmk8uu", "LMK8UU 베어링", "네모 날개 달린 베어링 — Y 봉 위를 미끄러짐", [("B2_116", [0])], "2-②")
part("t8nut", "T8 황동 너트", "모터 나사를 따라 움직이며 판을 밂 (모터와 같이 옴)", [("PL_Ynut_T8", None)], "1")
part("falcs", "L형 판금 브래킷 FALCS", "얇은 스테인리스 ㄱ자 (미스미)", [("falcs", [0])], "2-②")
part("sp", "안내판 SP", "알루미늄 3T — 세로 홈 2개 (펜 홀더 길)", [("PL_SP_metal", None)], "2-②")
part("sv", "서보판 SV", "3D 프린트 3T — 펜 서보를 잡음", [("PL_SV_PETG", None)], "2-②")
part("sg90", "SG-90 서보", "파란 작은 모터 — 펜 홀더를 들어 올림", [("P205_z_servo_SG90", None), ("P205s_z_servo_spline", None)], "1")
part("sg90horn", "SG-90 혼", "SG-90 봉지의 날개 하나", [("P205h_z_servo_horn", None)], "1")
part("hv", "홀더판 HV", "알루미늄 3T — 마커를 잡고 위아래로 미끄러짐", [("B3_115", None)], "2-②")
part("clip203", "마커 클립 203p", "3D 프린트 링 — 마커를 꽉 잡음 (2개)", [("C203p", [0])], "2-②")
part("shoulder", "어깨 볼트 SHMSB4-10", "매끈한 원통 + 작은 나사 끝 — 홀더가 미끄러지는 핀", [("shoulder_set", [0])], "2-②")
part("spacer202", "스페이서 202s", "3D 프린트 작은 링 Ø7 × 3.8", [("S202s_spacer", [0])], "2-②")
part("ya", "빔판 YA", "3D 프린트 3T, 30 × 110.5 — 빔 앞쪽 판 (가장 긴 판)", [("PL_YA_PETG", None)], "2-②")
part("yb", "빔판 YB", "3D 프린트 3T, 28 × 73.5 — 빔 뒤쪽 판", [("PL_YB_PETG", None)], "2-②")
part("xn", "X 너트판 XN", "3D 프린트 3T, 28 × 68 — 가운데 Ø10.5 구멍", [("PL_XN_PETG", None)], "2-②")
part("ym", "Y 모터판 YM", "3D 프린트 3T, 43 × 86.5 — 가운데 Ø22.5 구멍", [("PL_YM_PETG", None)], "2-②")
part("sc8uu", "SC08UU 베어링 블록", "알루미늄 블록 안에 베어링 — X 봉 위를 미끄러짐", [("sc8uu_A", None)], "2-②")
part("yrod", "Y 봉 Ø8 × 114", "양 끝에 M4 암나사 (미스미)", [("B2_113", [0])], "2-②")
part("xrod", "X 봉 Ø8 × 200", "매끈한 쇠막대 (미스미)", [("P213_x_rods", [0])], "2-②")
part("sk08", "SK08 봉 받침", "X 봉 끝을 레일 위에 잡아 줌 (조임 나사 달림)", [("B1_111", [0])], "2-②")
part("nemaY", "NEMA17 모터 (Y, 나사 132)", "네모 모터 + 나사 막대 132 mm — 캐리지를 앞뒤로", [("PL_Ymotor_N17", None), ("PL_Yscrew_T8", None)], "1")
part("nemaX", "NEMA17 모터 (X, 나사 155)", "네모 모터 + 나사 막대 155 mm — 빔을 좌우로", [("PL_Xmotor_N17", None), ("PL_Xscrew_T8", None)], "1")
part("p217", "X 모터판 217", "알루미늄 3T — 구멍 4개를 직접 뚫음 (준비 작업 1)", [("PL_217_moved", None)], "2-②")
part("vlt", "원점 스위치 VLT-SM006", "작은 레버 스위치 — 눌리면 '여기가 0'", [("XYn113", None), ("HS_227x_home_switch_X", None)], "1")
part("arm226", "X 원점 팔 226p", "알루미늄 3T 긴 판 — 원점 스위치를 받침", [("XH_arm", None)], "2-②")
part("p197", "드라이버 받침 197", "알루미늄 3T 판", [("DRV_br", None)], "1")
part("drvboard", "드라이버 보드 ARD200928", "DRV8825 두 개를 꽂는 판", [("drv_board", None)], "1")
part("drv8825", "DRV8825 드라이버", "작은 빨간 판 + 방열판 — 모터에 전기를 나눠 줌 (2개)", [("drv_modules", None)], "1")
part("marker", "샤피 마커 (노랑)", "말벌 등에 노란 점을 찍는 펜", [("P201_marker", None)], "2-②")
# 위
part("top105", "위판 105", "흰 아크릴 5T, 140 × 180", [("P105_top_plate", None)], "5-①")
part("campl", "카메라 판 181", "흰 아크릴 3T, 58 × 80", [("CAM_PLATE", None)], "3")
part("cam", "카메라 모듈 3", "라즈베리 파이 카메라 — 위에서 말벌을 봄", [("P180_camera", None)], "3")
part("led", "LED 3구 모듈 (12 V)", "흰 불빛 — 마킹실을 비춤 (2개)", [("CAM_LED", [0])], "3")
part("pipb", "Pi 선반 바닥 199a", "흰 아크릴 3T", [("pi_PB", None)], "3")
part("pipv", "Pi 선반 벽 199a", "알루미늄 3T", [("pi_PV", None)], "3")
part("pi5", "라즈베리 파이 5", "AI로 말벌을 판단하는 컴퓨터 (팀에 있음)", [("SJR_pi5", None)], "3")
# 나중
part("trap", "상용 트랩 「야생 말벌 포획기」", "먹이로 말벌을 꾀어 위로 보냄 (있음)", [(k, None) for k in TRAP], "5-①", later=True)
part("collar102", "칼라 102", "흰 아크릴 5T × 3장 — 트랩 링 ↔ 데크", [("P102_collar", None)], "5-①", later=True)
part("funnel111", "입구 깔때기 111", "3D 프린트", [("P111_entry_funnel", None)], "2-①", later=True)
part("tube110", "입구 관 110", "아크릴 관 바깥 18 · 안 14, 115 mm", [("P110_entry_duct", None)], "2-①", later=True)
part("tube172", "격리 관 172", "아크릴 관 바깥 18 · 안 14, 195 mm", [("SW_117", None)], "2-①", later=True)
part("funnel173", "격리 깔때기 173", "3D 프린트", [("P173_isolation_funnel", None)], "2-①", later=True)
part("dome104", "돔 연결부 104", "흰 아크릴 5T × 2장", [("P104_dome_coupling", None)], "5-①", later=True)
part("container", "상용 트랩 포획통", "잡힌 말벌이 모이는 통 (있음)", [("PREF_trap_container", None), ("PREF_trap_cap", None), ("PREF_trap_silicone_star", None)], "5-①", later=True)
# 기둥류 (CAD 사진)
part("so_uno", "M3 기둥 5 mm", "황동 육각 기둥 (키트 C)", [("uno1_st", [0])], "5-③")
part("so_mos", "M3 × 6 암-암 기둥", "황동 육각 기둥", [("SJX05", [0])], "5-③")
part("nylon", "나일론 스페이서", "흰 플라스틱 통 (키트 A)", [("SJ53C_board_spacers", [0])], "5-③")
part("so_spsv", "M3 × 10 암-암 기둥", "황동 육각 기둥 (키트 C)", [("spsv_standoffs", [0])], "5-③")
part("so_ym", "기둥 40 mm (M-15 + F-25)", "M-15(수-암)를 F-25(암-암)에 돌려 이어 40 mm", [("ym_standoffs", [0])], "2-②")
part("so_drv", "M3 × 8 암-암 기둥", "육각 기둥", [("DRV_so", [0])], "5-③")
part("so_cam", "카메라 기둥 (M-30 + M-15)", "두 개를 이어 45 mm", [("B2_96", [0])], "3")
part("so_pi", "M2.5 기둥 F-6", "황동 기둥 (파이 밑)", [("SJR_pi5_st", [0])], "3")
part("foam", "3M 폼 양면테이프 18 mm", "두께 있는 양면테이프 — 작은 부품 붙이기", None, "5-②", kind="icon", spec=("tape",))
# 나사 (그림) — spec = (모양, 지름, 길이)
for pid, name, desc, spec in [
    ("m5x8", "M5 × 8 렌치볼트", "프레임 볼트 (가장 많이 씀)", ("button", 5, 8)),
    ("m5x10", "M5 × 10 렌치볼트 (검정)", "데크·위판·SK08·상자 혀", ("button", 5, 10)),
    ("m5x12", "M5 × 12 볼트", "스텐 키트 — 너트와 같이", ("socket", 5, 12)),
    ("sn5", "스프링너트 M5", "2020 홈에 넣는 너트 (20 시리즈)", ("springnut", 5, 0)),
    ("n5", "M5 너트", "6각 너트", ("nut", 5, 0)),
    ("sn4", "스프링너트 M4", "2020 홈에 넣는 너트 (20 시리즈)", ("springnut", 4, 0)),
    ("m4x8", "M4 × 8 둥근머리", "217 판 → 레일", ("pan", 4, 8)),
    ("m4x10c", "M4 × 10 접시머리", "머리가 판 속으로 쏙 — 빔 판", ("csk", 4, 10)),
    ("m3x6", "M3 × 6 둥근머리", "짧은 M3 — 기둥 고정", ("pan", 3, 6)),
    ("m3x6s", "M3 × 6 렌치볼트", "XN 판 T8 너트", ("socket", 3, 6)),
    ("m3x8", "M3 × 8 둥근머리", "브래킷·선반", ("pan", 3, 8)),
    ("m3x8c", "M3 × 8 접시머리", "머리가 판 속으로", ("csk", 3, 8)),
    ("m3x8t", "M3 × 8 태핑 (PT2-3X8)", "3D 프린트에 바로 돌려 박는 뾰족 나사", ("tap", 3, 8)),
    ("m3x10", "M3 × 10 둥근머리", "스위치·CP 너트", ("pan", 3, 10)),
    ("m3x12", "M3 × 12 둥근머리", "LMK8UU 베어링", ("pan", 3, 12)),
    ("m3x12c", "M3 × 12 접시머리", "마커 클립", ("csk", 3, 12)),
    ("m3x16", "M3 × 16 둥근머리", "MOSFET 긴 나사", ("pan", 3, 16)),
    ("m3x20", "M3 × 20 둥근머리", "mightyZAP 경첩", ("pan", 3, 20)),
    ("m3x6set", "M3 × 6 무두볼트", "머리 없는 나사 (육각 구멍)", ("set", 3, 6)),
    ("m3x8set", "M3 × 8 무두볼트", "머리 없는 나사 (이노공구 세트)", ("set", 3, 8)),
    ("n3", "M3 너트", "6각 너트", ("nut", 3, 0)),
    ("w3", "M3 와셔", "얇은 둥근 판", ("washer", 3, 0)),
    ("nsp3", "나일론 스페이서 M3 × 3", "3 mm 짧은 통", ("spacer", 3, 3)),
    ("m2x8", "M2 × 8 둥근머리 + M2 너트", "카메라·SG-90 (키트 A)", ("pan", 2, 8)),
    ("m2self", "서보 나사 (봉지에 든 것)", "MG90S 봉지의 작은 셀프탭 나사", ("tap", 2, 8)),
    ("hornscrew", "혼 나사 (봉지에 든 것)", "서보 봉지의 가장 작은 나사", ("tap", 2, 5)),
    ("m25x5", "M2.5 × 5 둥근머리", "파이·모터 앞", ("pan", 2.5, 5)),
    ("n25", "M2.5 와셔 + 너트", "어깨 볼트 끝", ("nut", 2.5, 0)),
    ("m3mot", "M3 둥근머리 (모터용)", "M3 × 6~8 — 모터 구멍 깊이에 맞게", ("pan", 3, 6)),
    ("m3motc", "M3 접시머리 (모터용)", "M3 × 8 — 217 판 위 2개", ("csk", 3, 8)),
]:
    part(pid, name, desc, None, "5-③", kind="screw", spec=spec)

# ---------------------------------------------------------------- 단계
S = []


def step(**kw):
    kw.setdefault("ctx", "main")
    kw.setdefault("off", {})
    kw.setdefault("d", FR)
    kw.setdefault("up", (0, 0, 1))
    kw.setdefault("hide", [])
    kw.setdefault("tips", [])
    kw.setdefault("warns", [])
    kw.setdefault("later", False)
    kw.setdefault("merge", [])
    kw.setdefault("focus", None)
    kw.setdefault("margin", 1.12)
    kw.setdefault("extra_done", [])
    S.append(kw)


def offs(keys, v):
    return {k: v for k in keys}


# ===== A 프레임
step(id="A1", sec="A", title="앞 사다리 만들기", place="바닥 (넓은 곳)",
     new=POSTS_F + RAILS_F + ["brk_front"], focus=FRAME_ALL,
     parts=[("post610", 2, POSTS_F), ("rail320", 4, RAILS_F), ("lbr", 8, ["brk_front"]), ("m5x8", 16, None), ("sn5", 16, None)],
     text=["기둥 610 두 개를 바닥에 나란히 눕힌다 (사이 320 mm).",
           "레일 320 네 개를 기둥 사이에 끼운다. 레일 <b>아랫면</b> 높이 (기둥 아래 끝부터): <b>0 · 180 · 440 · 590 mm</b>. 맨 아래 레일은 기둥 끝과, 맨 위 레일 윗면은 기둥 위 끝(610)과 딱 맞는다.",
           "레일 끝마다 L 브래킷 1개 (모두 8개)를 안쪽 모서리에 대고, 스프링너트를 홈에 넣어 M5 × 8로 조인다. 브래킷은 맨 아래 층만 레일 <b>위</b>, 나머지 세 층은 레일 <b>아래</b>에 둔다.",
           "레일이 기둥과 직각인지 (삼각자·책 모서리) 본 뒤 꽉 조인다."],
     tips=["높이 맞추기 쉬운 법: 골판지를 160 · 240 · 130 mm로 잘라 레일 사이에 끼우면 저절로 맞는다 (아래에서부터 레일 사이 빈칸 높이).",
           "이 면이 장치의 <b>앞</b>이다. 기둥에 마스킹테이프로 '앞' 이라고 써 두자."],
     labels="dims_A1")
step(id="A2", sec="A", title="뒤 사다리 만들기", place="바닥",
     new=POSTS_B + RAILS_B + ["brk_back"], focus=FRAME_ALL,
     parts=[("post610", 2, POSTS_B), ("rail320", 4, RAILS_B), ("lbr", 8, ["brk_back"]), ("m5x8", 16, None), ("sn5", 16, None)],
     text=["1단계와 <b>똑같이</b> 하나 더 만든다 — 높이 0 · 180 · 440 · 590 mm.",
           "두 사다리를 나란히 놓고 레일 높이가 서로 같은지 맞대어 본다."],
     tips=["그림에서 회색 = 이미 만든 것, 주황 = 이번에 붙이는 것."])
step(id="A3", sec="A", title="옆 레일 8개로 두 사다리 잇기", place="바닥 (두 사람이면 좋음)",
     new=RAILS_L + RAILS_R + ["brk_left", "brk_right"], focus=FRAME_ALL,
     parts=[("rail320", 8, RAILS_L + RAILS_R), ("lbr", 16, ["brk_left", "brk_right"]), ("m5x8", 32, None), ("sn5", 32, None)],
     text=["두 사다리를 세워 마주 보게 놓는다 (사이 320 mm).",
           "왼쪽 옆에 레일 4개, 오른쪽 옆에 레일 4개를 같은 높이 (0 · 180 · 440 · 590)로 끼운다.",
           "레일 끝마다 L 브래킷 1개 (16개) — 1단계처럼 맨 아래 층은 레일 위, 나머지는 레일 아래.",
           "다 끼우면 상자 모양. 평평한 바닥에서 네 기둥이 모두 바닥에 닿게 (흔들리지 않게) 한 뒤 모든 볼트를 꽉 조인다."],
     tips=["<b>왼쪽</b> = 나중에 빨간 비상 정지 버튼이 붙는 쪽, <b>오른쪽</b> = X 모터가 튀어나오는 쪽. 테이프로 표시."],
     warns=["대각선 두 길이를 줄자로 재서 같으면 직각이다 (차이 2 mm 안)."])
step(id="A4", sec="A", title="데크 가로대 2개", place="프레임",
     new=DECK_X + ["tb_deck"], focus=FRAME_ALL,
     parts=[("rail320", 2, DECK_X), ("lbr", 8, ["tb_deck"]), ("m5x8", 16, None), ("sn5", 16, None)],
     text=["아래에서 두 번째 층 (데크 층, 높이 180) 의 왼쪽·오른쪽 레일 사이에 가로대 2개를 앞뒤 방향이 아닌 <b>좌우 방향</b>으로 끼운다.",
           "자리: 앞 가로대의 앞면이 앞 레일 안쪽 면에서 <b>70 mm</b>, 뒤 가로대의 뒷면이 뒤 레일 안쪽 면에서 <b>70 mm</b> (두 가로대 사이 빈칸 140 mm).",
           "가로대 끝마다 L 브래킷 <b>2개</b> (가로대 양옆에 하나씩, 모두 8개)로 옆 레일 안쪽 면에 조인다. 가로대 윗면이 옆 레일 윗면과 같은 높이."],
     tips=["가로대 윗면 홈에는 나중에 데크 판 볼트용 스프링너트가 들어간다 — 홈이 위를 보게."])
step(id="A5", sec="A", title="갠트리 레일 (가운데 레일 100d)", place="프레임",
     new=GANTRY + ["tb_gantry"], focus=FRAME_ALL,
     parts=[("rail320", 1, GANTRY), ("lbr", 4, ["tb_gantry"]), ("m5x8", 8, None), ("sn5", 8, None)],
     text=["위에서 두 번째 층 (갠트리 층, 높이 440)의 앞 레일과 뒤 레일 사이에 레일 1개를 <b>앞뒤 방향</b>으로 끼운다.",
           "자리: 레일 왼쪽 면이 왼쪽 옆 레일 안쪽 면에서 <b>132 mm</b> (오른쪽 옆 레일 안쪽 면에서 168 mm).",
           "끝마다 L 브래킷 2개 (양옆, 모두 4개)."],
     tips=["이 레일 위에 X 봉 받침 2개와 드라이버 받침이 올라간다 — 윗면이 앞·뒤 레일 윗면과 같은 높이여야 X 봉이 수평."])
# ===== B 데크
HB = ["P100a_post_2"]  # 앞-오른쪽 기둥 숨김 (잘 보이게)
BRK = ["brk_front", "brk_back", "brk_left", "brk_right"]
UPPER = RAILS_F[2:] + RAILS_B[2:] + RAILS_L[2:] + RAILS_R[2:] + GANTRY + ["tb_gantry"] + BRK
TOPR = [RAILS_F[3], RAILS_B[3], RAILS_L[3], RAILS_R[3]] + BRK
HDECK = HB + UPPER
step(id="B1", sec="B", title="데크 판 올리기", place="프레임",
     new=["P101_deck", "deck_bolts"], off={"P101_deck": (0, 0, 70), "deck_bolts": (0, 0, 120)},
     d=(-1, 1, -1.1), focus=["P101_deck"] + DECK_X + ["P100b_rail_deck_xm170", "P100b_rail_deck_xp170"], hide=HDECK,
     parts=[("deck101", 1, ["P101_deck"]), ("m5x10", 4, ["deck_bolts"]), ("sn5", 4, None)],
     text=["데크 가로대 2개의 <b>윗면 홈</b>에 스프링너트를 2개씩 (모두 4개) 넣어 둔다.",
           "데크 판을 가로대 위에 얹는다: 큰 둥근 구멍이 장치 한가운데, 판의 앞·뒤 끝이 가로대 바깥 면과 딱 맞고, 왼쪽 끝은 왼쪽 레일 안쪽에서 약 30 mm.",
           "판 구멍 4개 밑으로 스프링너트를 밀어 맞추고 M5 × 10 (검정) 4개로 조인다."],
     warns=["아크릴은 세게 조이면 금이 간다 — 판이 안 움직일 만큼만."],
     tips=["그림에서는 안이 잘 보이게 앞-오른쪽 기둥을 숨겼다."])
step(id="B2", sec="B", title="아두이노 UNO 2개 + 센서 쉴드", place="데크 위",
     new=UNO, off={"uno1_st": (0, 0, 25), "uno2_st": (0, 0, 25), "P191_arduino_uno": (0, 0, 55), "E01": (0, 0, 55), "SH1": (0, 0, 95), "SH2": (0, 0, 95)},
     d=(-1, 1, -1.1), focus=["P101_deck"], hide=HDECK,
     parts=[("uno", 2, ["P191_arduino_uno", "E01"]), ("shield", 2, ["SH1", "SH2"]), ("so_uno", 6, ["uno1_st", "uno2_st"]), ("m3x6", 12, None)],
     text=["UNO ① (움직임 담당) 자리 = 데크 <b>왼쪽 앞</b>, UNO ② (문·센서 담당) 자리 = 데크 <b>뒤 가운데</b>. 그림의 위치를 보고 데크 구멍을 찾는다.",
           "UNO 하나에 M3 기둥 5 mm 3개: 데크 밑에서 M3 × 6으로 기둥을 고정 (기둥이 수-암이면 수나사를 구멍에 넣고 밑에서 M3 너트).",
           "UNO를 기둥 위에 얹고 위에서 M3 × 6으로 조인다.",
           "센서 쉴드를 UNO 위에 핀을 맞춰 꾹 꽂는다 (핀이 휘지 않게 똑바로)."],
     tips=["UNO에 마스킹테이프로 '① 움직임', '② 문' 이라고 써 두면 선 꽂을 때 헷갈리지 않는다."])
step(id="B3", sec="B", title="MOSFET 모듈 (빨간 판)", place="데크 위",
     new=MOS, off={"SJX05": (0, 0, 25), "SJ53C_board_spacers": (0, 0, 25), "SJX04": (0, 0, 55), "SJ53C_mosfet_parts": (0, 0, 55), "SJ53C_board_screws": (0, 0, 95)},
     d=(-1, 1, -1.1), focus=["P101_deck"], hide=HDECK,
     parts=[("mosfet", 1, ["SJX04"]), ("so_mos", 2, ["SJX05"]), ("nylon", 2, ["SJ53C_board_spacers"]), ("m3x6", 4, None), ("m3x16", 2, None), ("n3", 2, None)],
     text=["자리 = 데크 <b>왼쪽 뒤</b> (UNO ① 뒤).",
           "앞쪽 두 구멍: M3 × 6 암-암 기둥 2개를 데크 밑에서 M3 × 6으로 고정 → 모듈을 얹고 위에서 M3 × 6.",
           "뒤쪽 두 구멍: 모듈 → 나일론 스페이서 → 데크를 M3 × 16이 한 번에 지나가게 넣고 데크 밑에서 M3 너트."],
     tips=["나사 단자 (초록 블록) 쪽이 바깥을 보게 — 선을 넣기 쉽다."])
step(id="B4", sec="B", title="전원 부품 — 강압 모듈 2 · DC 잭 · 퓨즈 · 와고 5", place="데크 위",
     new=PWR, off=offs(PWR, (0, 0, 45)),
     d=(-1, 1, -1.1), focus=["P101_deck"], hide=HDECK,
     parts=[("xl4015", 2, ["XL1", "XL2"]), ("dcjack", 1, ["JK1"]), ("fuse", 1, ["FU1"]), ("wago", 5, ["SJW1"]), ("foam", 1, None)],
     text=["모두 나사 없이 <b>폼 양면테이프</b>로 붙인다. 붙이기 전에 데크를 알코올로 닦는다.",
           "XL4015 ① (5.0 V) = 왼쪽 가운데 (UNO ① 뒤), XL4015 ② (7.4 V) = 오른쪽 뒤.",
           "DC 잭과 퓨즈 홀더 = 오른쪽 앞 (세운 막대 자리 앞). 와고 5개 = 앞 가장자리에 한 줄.",
           "퓨즈 홀더에 5 A 퓨즈를 꽂아 둔다."],
     warns=["XL4015 두 개는 <b>선을 잇기 전에</b> 전압을 맞춰야 한다 (5.0 V / 7.4 V) — F장 '선 연결' 1번. 7.4 V 짜리에 '7.4' 라고 써 두기."])
step(id="B5", sec="B", title="비상 정지 버튼", place="프레임 왼쪽 바깥",
     new=ESTOP, off={"SJ_estop_plate": (-45, 0, 0), "E03": (-110, 0, 0), "estop_bolts": (-80, 0, 0)},
     d=(1, 1, -0.6), focus=["SJ_estop_plate", "E03", "P100b_rail_deck_ym170", "P101_deck"], hide=UPPER,
     parts=[("estopplate", 1, ["SJ_estop_plate"]), ("estop", 1, ["E03"]), ("m5x8", 2, ["estop_bolts"]), ("sn5", 2, None)],
     text=["비상 정지 버튼을 판의 둥근 구멍 (Ø25.5)에 넣고 버튼에 달린 링 너트로 조인다. 버섯 머리가 바깥을 보게.",
           "<b>왼쪽</b> 데크 층 레일 (높이 180)의 <b>바깥 면</b> 홈에 스프링너트 2개 → 판을 대고 M5 × 8 2개.",
           "판은 레일 가운데에 (앞뒤 대칭)."],
     tips=["누구나 바로 누를 수 있게 바깥을 본다. 선은 F장에서."])
# ===== C 마킹실 (작업대)
step(id="C1", sec="C", title="세운 막대 + L 브래킷", place="작업대", ctx="mk",
     new=MK1, off={"V3_P09": (0, -30, 0), "bar_bolts_bar": (0, -60, 0)}, d=FL, focus=MK1,
     parts=[("bar156", 1, ["V3_P07"]), ("lbr", 1, ["V3_P09"]), ("m5x8", 1, ["bar_bolts_bar"]), ("sn5", 1, None)],
     text=["세운 막대 156의 아래 끝에 L 브래킷을 댄다 — 브래킷의 한 다리는 막대 <b>앞면</b>에, 다른 다리는 막대 아래 끝과 같은 높이에서 앞으로 (나중에 데크에 놓이는 다리).",
           "막대 앞면 홈에 스프링너트 1개 → M5 × 8 1개로 조인다.",
           "데크 쪽 다리 구멍은 9단계 (C9)에서 쓴다."],
     tips=["C장 1~8단계는 <b>작업대 위</b>에서 마킹실 덩어리를 따로 만든다. 다 만든 뒤 9단계에서 데크에 세운다."])
step(id="C2", sec="C", title="mightyZAP (바닥 올리는 모터) 달기", place="작업대", ctx="mk",
     new=MK2, off={"V3_P03": (-45, 0, 0), "V3_P04": (-45, 0, 0), "V3_P11": (-95, 0, 0)}, d=FL, focus=MK1 + MK2,
     parts=[("mzap", 1, ["V3_P03"]), ("m3x20", 1, ["V3_P11"]), ("w3", 3, None), ("n3", 2, None)],
     text=["세운 막대의 <b>왼쪽 면</b> 홈에 M3 너트 1개를 위 끝에서 밀어 넣어 경첩 높이 (막대 아래 끝에서 약 86 mm)까지 내린다.",
           "M3 × 20 → mightyZAP 아래 끝 구멍 → (틈 4 mm 채우기: M3 너트 1 + M3 와셔 3) → 막대 홈 속 너트 순서로 끼워 조인다.",
           "mightyZAP 막대(로드)가 <b>위</b>를 보게 세운다. 경첩이라 살짝 흔들리는 게 정상."],
     warns=["홈 속 너트는 상자를 달기 전에 (막대 위 끝이 열려 있을 때) 넣어야 한다."])
step(id="C3", sec="C", title="마킹실 상자 300", place="작업대", ctx="mk",
     new=MK3, off={"V3_P00": (0, 0, 55), "V3_P08": (0, 55, 0)}, d=FL, focus=MK1 + MK2 + MK3,
     parts=[("box300", 1, ["V3_P00"]), ("m5x10", 2, ["V3_P08"]), ("sn5", 2, None)],
     text=["세운 막대 <b>뒷면</b> 홈에 스프링너트 2개를 위쪽에 넣어 둔다.",
           "상자를 위에서 내려 씌운다: mightyZAP 로드가 상자 밑구멍으로 들어가고, 상자의 '혀'가 막대 뒷면에 붙는다.",
           "혀 구멍 2개에 M5 × 10 2개."],
     tips=["상자 둥근 방이 막대 왼쪽, 혀가 막대 뒤에 오는 방향은 하나뿐 — 그림과 같게."])
step(id="C4", sec="C", title="바닥 원판", place="작업대", ctx="mk",
     new=MK4, off={"V3_P06": (0, 0, 45), "V3_P05": (0, 0, 80)}, d=FL, focus=MK1 + MK2 + MK3 + MK4,
     parts=[("m3x8set", 1, ["V3_P06"]), ("n3", 1, None), ("floor304", 1, ["V3_P05"])],
     text=["M3 × 8 무두볼트를 로드 끝 나사 구멍에 반쯤 돌려 넣고, M3 너트를 끼워 로드 끝에 붙여 잠근다.",
           "흰 바닥 원판의 가운데 구멍을 무두볼트에 끼워 너트 위에 얹는다 (상자 위로 넣음)."],
     tips=["원판은 너트 위에 얹히기만 한다. 말벌 뒤 배경이 흰색이 되어 카메라가 잘 본다."])
step(id="C5", sec="C", title="격자판 (투명)", place="작업대", ctx="mk",
     new=MK5, off={"V3_P01": (0, 0, 35), "V3_P02": (0, 0, 70)}, d=FL, focus=MK1 + MK3 + MK5,
     parts=[("grid300p", 1, ["V3_P01"]), ("m3x8t", 4, ["V3_P02"]), ("w3", 4, None)],
     text=["투명 격자판을 상자 윗면에 얹고 네 모서리 구멍을 맞춘다.",
           "M3 와셔 + M3 × 8 태핑 4개를 상자 구멍(Ø2.5)에 천천히 돌려 박는다."],
     warns=["태핑 나사는 프린트 플라스틱에 나사산을 만들며 들어간다 — 끝까지 들어간 뒤 더 돌리면 구멍이 망가진다. 손힘으로만."],
     tips=["격자판 보호 비닐이 있으면 떼고 붙인다. 카메라가 이 판을 통해 말벌을 본다."])
step(id="C6", sec="C", title="문 하우징 2개", place="작업대", ctx="mk",
     new=MK6, off={"B1_housing": (-45, 0, 0), "P176_release_gate_housing": (45, 0, 0)}, d=FL, focus=MK1 + MK3 + MK6,
     parts=[("housing112", 1, ["B1_housing"]), ("housing176", 1, ["P176_release_gate_housing"]), ("m3x8t", 4, ["ear_112", "ear_176"])],
     text=["입구·격리 문 하우징 112를 상자 <b>왼쪽</b>, 방생 문 하우징 176을 상자 <b>오른쪽</b>에 대어 문 구멍끼리 맞춘다.",
           "하우징의 '귀' 4곳 (상자 앞·뒤 면)에 M3 × 8 태핑을 돌려 박는다."],
     tips=["112의 꺾인 관 소켓 2개가 아래를 본다 (입구 관·격리 관이 꽂힐 곳)."])
step(id="C7", sec="C", title="문 서보 3개 (MG90S)", place="작업대", ctx="mk",
     new=MK7, off={k: (0, 0, 40) for k in MK7}, d=FL, focus=MK3 + MK6 + MK7,
     parts=[("mg90s", 3, ["P112_entry_gate_servo_MG90S", "SW_104", "P176_release_gate_servo_MG90S"]), ("m2self", 6, None)],
     text=["서보 3개: 입구 문 (112 뒤쪽 칸), 격리 문 (112 앞쪽 칸), 방생 문 (176 칸).",
           "서보를 칸에 넣고 서보 봉지의 작은 나사로 서보 귀 2곳을 조인다 (서보 하나에 2개).",
           "서보 축 (톱니)이 문 구멍 쪽을 보게 넣는다."],
     tips=["서보 선에 '입구 · 격리 · 방생' 테이프를 붙여 두면 선 연결 때 편하다."])
step(id="C8", sec="C", title="혼 + 문판", place="작업대", ctx="mk",
     new=MK8, off={"P112_entry_gate_horn": (0, 0, 25), "SW_106": (0, 0, 25), "P176_release_gate_horn": (0, 0, 25),
                   "P112_entry_gate_flap": (0, 0, 50), "SW_103": (0, 0, 50), "P176_release_gate_flap": (0, 0, 50)},
     d=FL, focus=MK3 + MK6 + MK7 + MK8,
     parts=[("horn", 3, ["P112_entry_gate_horn", "SW_106", "P176_release_gate_horn"]), ("flap", 3, ["P112_entry_gate_flap", "SW_103", "P176_release_gate_flap"]), ("hornscrew", 6, None)],
     text=["문판 (알루미늄 작은 판)의 긴 구멍을 혼 날개에 맞추고, 혼 봉지의 가장 작은 나사 2개로 붙인다 (문판 3개).",
           "문판 붙은 혼을 서보 축에 끼운다. 문판이 문 구멍을 막는 자리 (닫힘)에서 끼운다.",
           "손으로 혼을 살살 돌려 문판이 걸리지 않고 열리고 닫히는지 본다."],
     warns=["정확한 닫힘 각도는 전원을 켠 뒤 서현 펌웨어 '닫힘' 명령에 맞춰 혼을 다시 끼운다. 혼 가운데 나사는 그때 조인다."])
step(id="C9", sec="C", title="빛 게이트 3쌍", place="작업대", ctx="mk",
     new=MK9, d=FL, focus=MK3 + MK6 + MK9,
     parts=[("gate", 3, MK9), ("foam", 1, None)],
     text=["게이트 한 쌍 = 송신 1 + 수신 1. 하우징 <b>윗면과 아랫면</b>의 작은 빔 구멍 (Ø3.2)에 서로 마주 보게 폼테이프로 붙인다.",
           "G2 = 입구 문 앞 (112), G3b = 격리 문 뒤 (112), G5 = 방생 문 뒤 (176).",
           "LED 렌즈가 빔 구멍 바로 위에 오도록 — 빛이 구멍으로 지나가야 한다."],
     tips=["어느 쪽이 위든 괜찮다. 선에 G2 · G3b · G5 이름표."])
step(id="C10", sec="C", title="마킹실 덩어리를 데크에 세우기", place="프레임 (데크 위)",
     new=MK_ALL + ["bar_bolts_deck"], merge=["mk"], off=dict(offs(MK_ALL, (0, 0, 90)), bar_bolts_deck=(0, 0, -45)),
     d=(-1, 1, -0.9), focus=["P101_deck"] + MK_ALL, hide=HDECK,
     parts=[("m5x12", 1, ["bar_bolts_deck"]), ("n5", 1, None)],
     text=["마킹실 덩어리를 데크 위에 세운다: 세운 막대가 데크 오른쪽 (DC 잭 뒤), L 브래킷 다리 구멍이 데크의 Ø5.5 구멍 위에 오게.",
           "위에서 M5 × 12를 브래킷과 데크에 넣고, 데크 밑에서 M5 너트로 조인다 (옆 빈칸으로 손을 넣음).",
           "막대가 데크에 수직인지 본다."],
     tips=["격자판이 위 (카메라 쪽)를 보고, 입구 문 하우징 112가 데크 가운데 큰 구멍 쪽 (왼쪽)을 본다."])
step(id="C11", sec="C", title="컵 받침 + 마커 뚜껑", place="데크 위 (마킹실 옆)",
     new=CUP, off={"CupBracket": (0, 0, 30), "P219_cap_cup": (0, 0, 60)},
     d=(-1, 1, -0.9), focus=MK3 + MK6 + CUP, hide=HDECK,
     parts=[("cup220", 1, ["CupBracket"]), ("cap219", 1, ["P219_cap_cup"]), ("foam", 1, None)],
     text=["컵 받침 220을 방생 문 하우징 176의 <b>앞쪽 선반</b> 위에 폼테이프로 붙인다.",
           "여분 마커의 뚜껑을 컵 받침 위에 입구가 위를 보게 붙인다 — 펜이 쉴 때 이 뚜껑 속으로 들어간다."],
     tips=["뚜껑 자리는 나중에 펜 위치 (대기 자리)를 보고 조금 옮겨도 된다."])
# ===== D XY (작업대 → 프레임)
CARD = (1, 1, -0.45)   # 앞-왼쪽에서 (CP 앞면·HV 보임)
CARB = (-1, -1, -0.45)  # 뒤-오른쪽에서 (CP 뒷면·SV 보임)
step(id="D1", sec="D", title="캐리지판 + 베어링 2개", place="작업대", ctx="car",
     new=CAR1, off={"B2_116": (0, -35, 0), "XYn99": (0, -65, 0)}, d=CARD, focus=CAR1,
     parts=[("cp", 1, ["PL_CP_acryl"]), ("lmk8uu", 2, ["B2_116"]), ("m3x12", 8, ["XYn99"]), ("n3", 8, None)],
     text=["흰 아크릴 캐리지판 CP의 큰 구멍 2개에 LMK8UU 베어링을 <b>같은 면</b>에서 끼운다 (네모 날개가 판에 붙게).",
           "날개 구멍 4개마다 M3 × 12를 날개 쪽에서 넣고 반대쪽에서 M3 너트 — 베어링 2개 × 4 = 8개.",
           "날개 있는 면이 <b>앞 (YA 쪽)</b>이 된다."],
     warns=["아크릴 — 대각선 순서로 조금씩, 세게 조이지 않기."])
step(id="D2", sec="D", title="Y 너트 (T8) 달기", place="작업대", ctx="car",
     new=CAR2, off={"PL_Ynut_T8": (0, 40, 0), "PL_CP_M3_nut": (0, -40, 0)}, d=CARB, focus=CAR1 + CAR2,
     parts=[("t8nut", 1, ["PL_Ynut_T8"]), ("m3x10", 2, ["PL_CP_M3_nut"]), ("n3", 2, None)],
     text=["준비 작업 2에서 가장자리 4곳을 0.5 mm 갈아 둔 T8 너트를 쓴다.",
           "너트의 둥근 플랜지를 CP <b>뒷면</b> (베어링 날개 반대쪽) 가운데 구멍에 대고, 몸통이 뒤로 튀어나오게 한다.",
           "플랜지 구멍 중 <b>가로 (좌우) 2개</b>만 쓴다: CP 앞에서 M3 × 10 → 플랜지 → 뒤에서 M3 너트."],
     tips=["세로 2개 구멍은 비워 둔다 (너트가 베어링 날개에 닿음)."])
step(id="D3", sec="D", title="ㄱ자 브래킷 2개 + 안내판 SP", place="작업대", ctx="car",
     new=CAR3, off={"falcs": (0, 25, 0), "falcs_screws": (0, 0, 0), "PL_SP_metal": (-35, 0, 0)}, d=CARB, focus=CAR1 + CAR3,
     parts=[("falcs", 2, ["falcs"]), ("sp", 1, ["PL_SP_metal"]), ("m3x8", 3, ["falcs_screws"]), ("m3x8c", 1, None), ("n3", 4, None)],
     text=["FALCS ㄱ자 2개를 CP 뒷면 <b>맨 위</b>와 <b>맨 아래</b>에 댄다 (긴 다리 20 mm가 CP에).",
           "CP 쪽: CP 앞에서 M3 × 8 둥근머리 → 브래킷 → M3 너트 (2곳).",
           "안내판 SP를 브래킷의 짧은 다리에 대고 (세로 홈 2개가 위아래로), SP 바깥 (왼쪽)에서 나사: 위 = M3 × 8 둥근머리, <b>아래 = M3 × 8 접시머리</b> + 너트."],
     warns=["아래 나사는 꼭 접시머리 — 펜 홀더 HV가 그 위를 미끄러진다."])
step(id="D4", sec="D", title="서보판 SV + 펜 서보 SG-90", place="작업대", ctx="car",
     new=CAR4, off={"sp_set": (0, 0, 0), "spsv_standoffs": (25, 0, 0), "sv_pan": (75, 0, 0), "PL_SV_PETG": (50, 0, 0),
                    "P205_z_servo_SG90": (0, 0, -45), "P205s_z_servo_spline": (0, 0, -45), "XYn100": (75, 0, -45)},
     d=CARB, focus=CAR1 + CAR3 + CAR4,
     parts=[("m3x6set", 3, ["sp_set"]), ("so_spsv", 3, ["spsv_standoffs"]), ("sv", 1, ["PL_SV_PETG"]), ("m3x6", 3, ["sv_pan"]),
            ("sg90", 1, ["P205_z_servo_SG90"]), ("m2x8", 2, ["XYn100"])],
     text=["SP의 나사 구멍 3개에 M3 × 6 무두볼트를 육각렌치로 돌려 넣는다 — 무두볼트 끝이 SP <b>왼쪽 면과 딱 같은 높이</b> (튀어나오면 HV가 걸림).",
           "오른쪽으로 나온 무두볼트에 M3 × 10 암-암 기둥 3개를 돌려 끼운다.",
           "SG-90을 SV 판 칸에 끼우고 (축이 왼쪽, SP 창문 쪽), SV 오른쪽에서 M2 × 8 → 서보 귀 → M2 너트 2곳.",
           "SV를 기둥 3개에 대고 M3 × 6 둥근머리 3개."],
     tips=["SG-90 축이 SP의 네모 창으로 나와 왼쪽에서 보여야 한다."])
step(id="D5", sec="D", title="홀더판 HV + 마커 클립 2개", place="작업대", ctx="hv",
     new=HV, off={"C203p": (-30, 0, 0), "clip_screws": (0, 0, 0)}, d=CARD, focus=HV,
     parts=[("hv", 1, ["B3_115"]), ("clip203", 2, ["C203p"]), ("m3x12c", 2, ["clip_screws"]), ("n3", 2, None)],
     text=["HV 판에서 접시 구멍 2개 (오목하게 파인 쪽)가 있는 면이 <b>오른쪽 (SP 쪽)</b>이다.",
           "그 면에서 M3 × 12 접시머리 → HV → 클립 다리 구멍 → M3 너트. 클립 2개, 링이 왼쪽 앞을 보게.",
           "두 클립 링이 위아래로 한 줄 (같은 축)이 되게 맞춘 뒤 조인다."],
     warns=["접시머리가 판 면보다 튀어나오면 HV가 SP 위를 못 미끄러진다 — 손톱으로 쓸어 평평한지 확인."])
step(id="D6", sec="D", title="HV를 SP에 — 어깨 볼트", place="작업대", ctx="car",
     new=HV + CAR6, merge=["hv"], off=dict(offs(HV, (-35, 0, 0)), shoulder_set=(-75, 0, 0), S202s_spacer=(-55, 0, 0), P205h_z_servo_horn=(-20, 0, 0)),
     d=CARD, focus=CAR1 + CAR3 + HV + CAR6,
     parts=[("shoulder", 2, ["shoulder_set"]), ("spacer202", 2, ["S202s_spacer"]), ("n25", 2, None), ("sg90horn", 1, ["P205h_z_servo_horn"])],
     text=["어깨 볼트에 스페이서 202s를 끼운다 → HV의 둥근 구멍 (Ø4.1) → SP의 세로 홈 → SP 오른쪽에서 M2.5 와셔 + 너트 (2개).",
           "너트는 손으로 끝까지 — 어깨 끝이 SP에 닿으면 멈춘다. HV를 손가락으로 올렸다 놓아 <b>스르륵 내려오는지</b> 본다.",
           "HV를 맨 아래로 내린 채, SG-90 축에 혼을 끼운다 — 혼이 HV 밑 모서리 바로 아래에 오는 각도."],
     warns=["펜을 드는 각도는 60° 넘게 하지 않는다 (마커 끝이 카메라 렌즈에 닿음 — 틈 9.5 mm). 각도는 서현 펌웨어로 맞춤."])
step(id="D7", sec="D", title="빔판 YA · YB + 베어링 블록 SC08UU", place="작업대", ctx="beam",
     new=BEAM_A + BEAM_B, off={"sc8uu_A": (0, -35, 0), "sc_csk_A": (0, 30, 0), "sc8uu_B": (0, 35, 0), "sc_csk_B": (0, -30, 0)},
     d=(-1, 0.55, -0.45), focus=BEAM_A + BEAM_B,
     parts=[("ya", 1, ["PL_YA_PETG"]), ("yb", 1, ["PL_YB_PETG"]), ("sc8uu", 2, ["sc8uu_A", "sc8uu_B"]), ("m4x10c", 8, ["sc_csk_A", "sc_csk_B"])],
     text=["SC08UU 블록을 YA 판 <b>바깥 (앞)</b>, 다른 하나를 YB 판 <b>바깥 (뒤)</b> 위쪽에 대어 구멍 4개를 맞춘다.",
           "판 <b>안쪽 면</b> (접시 구멍이 오목한 쪽)에서 M4 × 10 접시머리 4개씩 블록 나사 구멍에 조인다 (모두 8개).",
           "YB에서 혀를 깎은 쪽 (왼쪽, SP가 지나가는 쪽) 2개는 <b>머리 지름 8.4 mm 이하</b>인 것만 (준비 작업 4의 1:1 원)."],
     warns=["접시머리가 판 안쪽 면보다 튀어나오면 캐리지가 걸린다."])
step(id="D8", sec="D", title="X 너트판 XN — T8 너트 · Y 원점 스위치 · YA에 잇기", place="작업대", ctx="beam",
     new=XN + XNL, off={"PL_Xnut_T8": (-30, 0, 0), "PL_XN_M3x6": (-55, 0, 0), "HS_227y_home_switch_Y": (-30, 0, 15), "XYn114": (-30, 0, 15),
                        "HS_227ys_switch_screws_Y": (-30, 0, 15), "beamL": (0, 0, -30), "beamL_bolts": (0, 0, -30)},
     d=(1, 0.8, -0.45), focus=BEAM_A + XN + XNL,
     parts=[("xn", 1, ["PL_XN_PETG"]), ("t8nut", 1, ["PL_Xnut_T8"]), ("m3x6s", 2, ["PL_XN_M3x6"]), ("vlt", 1, ["XYn114"]),
            ("m3x10", 1, None), ("nsp3", 1, None), ("n3", 1, None), ("lbr", 1, ["beamL"]), ("m5x12", 2, ["beamL_bolts"]), ("n5", 2, None)],
     text=["X T8 너트 (준비 작업 2에서 위를 1.5 mm 평평하게 간 것): 몸통을 XN 가운데 구멍 (Ø10.5)에 왼쪽에서 넣고, 플랜지 구멍 2개로 XN의 Ø2.5 구멍에 <b>M3 × 6 렌치볼트</b>를 바로 돌려 넣는다 (플라스틱에 나사산이 생김). 갈아 낸 평평한 면이 <b>위</b>.",
           "Y 원점 스위치: XN 오른쪽에서 M3 × 10 → XN → 나일론 스페이서 3 mm → 스위치 기판 → M3 너트. 레버가 뒤쪽을 본다.",
           "L 브래킷으로 XN 아래 끝과 YA 아래 끝을 직각으로: M5 × 12 + M5 너트 2개."],
     warns=["XN의 Ø2.5 구멍은 드릴로 넓히지 않는다 — 나사가 헛돈다."])
step(id="D9", sec="D", title="Y 봉 2개 + 캐리지 → YA · YB 사이에", place="작업대", ctx="beam",
     new=YRODS + CAR_ALL, merge=["car"], off={"rodend_A": (0, -45, 0), "rodend_B": (0, 45, 0)},
     d=(-1, 0.55, -0.45), focus=BEAM_A + BEAM_B + YRODS + CAR_ALL + XN,
     parts=[("yrod", 2, ["B2_113"]), ("m4x10c", 4, ["rodend_A", "rodend_B"])],
     text=["캐리지의 베어링 2개에 Y 봉 2개를 끼운다 (봉이 베어링 속을 스르륵).",
           "방향: 베어링 날개 면이 YA 쪽 (앞), 펜 홀더 HV가 왼쪽.",
           "봉 앞 끝을 YA 아래쪽 구멍 2개에, 뒤 끝을 YB 구멍 2개에 대고 판 <b>바깥</b>에서 M4 × 10 접시머리 (4개)를 봉 끝 암나사에 조인다.",
           "캐리지를 손으로 끝에서 끝까지 밀어 본다 — 같은 힘으로 걸림 없이."],
     tips=["빡빡하면 봉 끝 나사 4개를 살짝 풀고 캐리지를 몇 번 왕복한 뒤 다시 조인다."])
step(id="D10", sec="D", title="Y 모터판 YM + Y 모터", place="작업대", ctx="ym",
     new=YM1, off={"ym_csk": (0, -60, 0), "PL_Ymotor_N17": (0, -50, 0), "PL_Ymotor_M3": (0, 25, 0)},
     d=(-1, -0.25, -0.35), focus=YM1,
     parts=[("ym", 1, ["PL_YM_PETG"]), ("so_ym", 3, ["ym_standoffs"]), ("m3x8c", 3, ["ym_csk"]), ("nemaY", 1, ["PL_Ymotor_N17"]), ("m3mot", 3, ["PL_Ymotor_M3"])],
     text=["기둥 3개 만들기: M-15 (수-암)의 수나사를 F-25 (암-암)에 돌려 이어 40 mm.",
           "YM 판 <b>앞면</b> (모터 붙는 면, 접시 구멍이 오목한 면)에서 M3 × 8 접시머리 3개로 기둥 3개를 YM에 단다 — 모터 밑에 깔리므로 <b>먼저</b>.",
           "NEMA17 (Y, 나사 132)의 둥근 턱을 YM 가운데 구멍 (Ø22.5)에 앞에서 끼우고, YM 뒤 (기둥 쪽)에서 M3 3개 (4번째 구멍은 없음)."],
     warns=["모터 나사가 모터 구멍 바닥에 닿으면 판이 덜 조여진다 — 판이 흔들리면 한 치수 짧은 나사."])
step(id="D11", sec="D", title="Y 나사를 캐리지 너트에 감고 YA에 고정", place="작업대", ctx="beam",
     new=YM2 + YM1, merge=["ym"], off=dict(offs(YM1, (0, -60, 0)), PL_Yscrew_T8=(0, -60, 0), ym_pan=(0, 35, 0)),
     d=(-1, -0.25, -0.35), focus=YM1 + BEAM_A + CAR_ALL,
     parts=[("m3x6", 3, ["ym_pan"])],
     text=["캐리지를 YA 쪽으로 당겨 둔다.",
           "모터 나사 끝을 YA 판 구멍에 넣어 캐리지 Y 너트 구멍에 댄다.",
           "모터를 통째로 손으로 돌려 나사를 너트에 감아 들어가게 한다 (8 mm에 한 바퀴). 기둥 끝이 YA에 닿을 때까지.",
           "YA 안쪽에서 M3 × 6 둥근머리 3개로 기둥 끝을 조인다. 캐리지를 밀어 봐서 나사가 따라 도는지 확인."],
     tips=["나사 끝 (뒤)은 아무 데도 안 붙는다 — 그게 정상."])
step(id="D12", sec="D", title="X 봉 2개 + 봉 받침 SK08 4개", place="작업대", ctx="beam",
     new=XRODS, off={"P213_x_rods": (-60, 0, 0), "B1_111": (0, 0, 0)}, d=(-1, 0.9, -0.6),
     focus=XRODS + BEAM_A + BEAM_B,
     parts=[("xrod", 2, ["P213_x_rods"]), ("sk08", 4, ["B1_111"])],
     text=["X 봉 2개를 SC08UU 블록 2개에 하나씩 끼운다 (앞 봉 = YA 쪽 블록, 뒤 봉 = YB 쪽 블록).",
           "봉 양 끝에 SK08 받침을 끼운다 — 받침 바닥 (구멍 2개)이 아래.",
           "봉 끝이 받침 밖으로 나온 길이를 양쪽 같게 하고, SK08 조임 나사는 <b>아직 살짝만</b>."],
     tips=["이제 XY 덩어리 완성! 빔을 봉 위에서 밀어 봐서 부드러운지 본다."])
step(id="D13", sec="D", title="XY 덩어리를 갠트리 레일 위에", place="프레임",
     new=XY_ALL + SKB, merge=["beam"], off=dict(offs(XY_ALL, (0, 0, 110)), B1_112=(0, 0, 160)),
     d=(-1, 1, -0.75), focus=XY_ALL + ["P100b_rail_gantry_yp170", "P100d_gantry_rail_xm18"], hide=TOPR + HB,
     parts=[("m5x10", 8, ["B1_112"]), ("sn5", 8, None)],
     text=["가운데 갠트리 레일 (100d)과 <b>오른쪽</b> 갠트리 레일의 윗면 홈에 스프링너트를 4개씩 (모두 8개) 넣는다.",
           "XY 덩어리를 위에서 내려 SK08 4개를 두 레일 위에 얹는다 (Y 모터가 앞).",
           "자리: 앞 봉 중심이 앞 레일 안쪽 면에서 <b>90 mm</b>, 뒤 봉 중심이 뒤 레일 안쪽 면에서 <b>88 mm</b>.",
           "M5 × 10 8개를 살짝 → 빔을 왼쪽 끝 ↔ 오른쪽 끝까지 밀어 보며 가장 부드러운 자리에서 꽉 → SK08 조임 나사도 조인다."],
     warns=["위 가로대 (E1)를 달기 전에 해야 위로 넣을 수 있다."])
step(id="D14", sec="D", title="X 모터 + 모터판 217", place="프레임 오른쪽 바깥",
     new=XMOT, off={"PL_217_moved": (60, 0, 0), "PL_Xmotor_N17": (60, 0, 0), "PL_Xmotor_M3low": (60, 0, 0), "PL_Xscrew_T8": (60, 0, 0), "PL_217_M4": (100, 0, 0)},
     d=(-1, 0.6, -0.4), focus=XMOT + ["P100b_rail_gantry_yp170", "PL_XN_PETG", "PL_Xnut_T8"], hide=TOPR + HB,
     parts=[("p217", 1, ["PL_217_moved"]), ("nemaX", 1, ["PL_Xmotor_N17"]), ("m3motc", 2, None), ("m3mot", 2, ["PL_Xmotor_M3low"]), ("m4x8", 2, ["PL_217_M4"]), ("sn4", 2, None)],
     text=["217 판 (준비 작업 1에서 구멍 4개 뚫은 것)의 <b>바깥 면</b>에 NEMA17 (X, 나사 155)을 대고, <b>안쪽 면</b>에서 M3 4개: 위 2개 = 접시머리 (접시 구멍), 아래 2개 = 둥근머리.",
           "오른쪽 갠트리 레일의 <b>바깥 면</b> 홈에 스프링너트 M4 2개.",
           "모터 나사 끝을 빔의 X 너트에 대고 모터를 통째로 돌려 감아 넣는다 (약 10바퀴).",
           "판이 레일 바깥 면에 닿으면 판 구멍 (Ø5.5)에 M4 × 8 둥근머리 2개."],
     warns=["모터가 프레임 <b>밖</b>에 달린다 (안쪽이면 레일에 6 mm 부딪힘)."])
step(id="D15", sec="D", title="X 원점 팔 + 원점 스위치", place="프레임",
     new=XHOME, off={"XH_arm": (0, 0, 30), "XH_bolts": (0, 0, 60), "HS_227x_home_switch_X": (0, 0, 55), "XYn113": (0, 0, 55), "HS_227xs_switch_screws_X": (0, 0, 55)},
     d=(-1, 1, -0.9), focus=XHOME + ["PL_YM_PETG", "PL_Ymotor_N17", "P100d_gantry_rail_xm18"], hide=TOPR + HB,
     parts=[("arm226", 1, ["XH_arm"]), ("m5x8", 2, ["XH_bolts"]), ("sn5", 2, None), ("vlt", 1, ["XYn113"]), ("m3x10", 1, None), ("nsp3", 1, None), ("n3", 1, None)],
     text=["앞 갠트리 레일 윗면 홈에 스프링너트 2개 → 226p 팔을 얹어 M5 × 8 2개. 팔은 뒤로 (안쪽으로) 뻗는다.",
           "자리: 팔 왼쪽 끝이 가운데 갠트리 레일 (100d) 오른쪽 면에서 약 29 mm.",
           "원점 스위치를 팔 끝 위에: 팔 밑에서 M3 × 10 → 팔 → 나일론 스페이서 → 기판 → M3 너트.",
           "빔을 손으로 왼쪽 끝까지 밀어 YM 판이 레버를 '딸깍' 누르는지 확인 → 안 누르면 팔을 앞뒤로 밀어 맞춤."],
     tips=["레버가 눌린 뒤 판이 1 mm 안에 팔에 닿는다 — 원점 찾기는 펌웨어가 천천히 한다."])
step(id="D16", sec="D", title="드라이버 받침 + 드라이버 보드", place="프레임",
     new=DRV, off={"DRV_br": (0, 0, 30), "SJ10": (0, 0, 60), "SJ11": (0, 0, 0), "DRV_so": (0, 0, 50), "drv_board": (0, 0, 75), "drv_modules": (0, 0, 110)},
     d=(-1, 1, -0.9), focus=DRV + ["P100d_gantry_rail_xm18", "XH_arm"], hide=TOPR + HB,
     parts=[("p197", 1, ["DRV_br"]), ("m5x8", 2, ["SJ10"]), ("sn5", 2, None), ("so_drv", 4, ["DRV_so"]), ("m3x6", 8, None), ("drvboard", 1, ["drv_board"]), ("drv8825", 2, ["drv_modules"])],
     text=["가운데 갠트리 레일 (100d) 윗면, <b>앞쪽 끝</b>에 스프링너트 2개 → 197 판 앞 끝을 앞 레일 안쪽 면에 붙이고 M5 × 8 2개.",
           "판 위에 M3 × 8 암-암 기둥 4개 (판 밑에서 M3 × 6).",
           "드라이버 보드를 얹고 위에서 M3 × 6 4개.",
           "DRV8825 2개를 보드 소켓에 꽂는다 — 방향을 보드 그림 · 핀 이름 (EN · GND)에 맞춘다."],
     warns=["DRV8825를 거꾸로 꽂고 전원을 넣으면 바로 탄다. 꽂은 뒤 사진을 찍어 서현에게 확인받기.",
            "모터 선은 전원이 꺼진 상태에서만 꽂고 뺀다."])
step(id="D17", sec="D", title="마커 끼우기", place="프레임",
     new=MARKER, off={"P201_marker": (0, 0, 120)}, d=(1, 1, -0.5),
     focus=MARKER + HV + CAR3 + MK3 + MK5, hide=TOPR + ["P100a_post_1", "P100a_post_4"] + [RAILS_L[2]],
     parts=[("marker", 1, ["P201_marker"])],
     text=["마커 뚜껑을 빼고 펜 끝이 아래로 오게 클립 2개 링에 위에서 밀어 넣는다.",
           "펜 홀더를 맨 아래로 내렸을 때 펜 끝이 격자판 윗면보다 약 3 mm 아래까지 내려오면 된다 (CAD 자리).",
           "처음엔 조금 높게 끼우고, 표본으로 시험하며 내린다."],
     tips=["펜을 쉬게 할 때는 뚜껑 컵 위로 — 시연 전날 펜이 마르지 않게."])
# ===== E 위
step(id="E1", sec="E", title="위 가로대 2개", place="프레임",
     new=TOPX, focus=FRAME_ALL + TOP_X,
     parts=[("rail320", 2, TOP_X), ("lbr", 8, ["tb_top"]), ("m5x8", 16, None), ("sn5", 16, None)],
     text=["A4 단계와 같은 방법으로 <b>맨 위 층</b> (높이 590)에 가로대 2개를 좌우 방향으로.",
           "자리: 앞·뒤 위 레일 안쪽 면에서 각각 70 mm (가로대 사이 140 mm).",
           "끝마다 L 브래킷 2개 (모두 8개). 홈은 위를 보게."])
step(id="E2", sec="E", title="카메라 판 만들기", place="작업대", ctx="cam",
     new=CAMU, off={"P180_camera": (0, 0, -30), "SJ53_cam_m2": (0, 0, -55), "CAM_LED": (0, 0, -35), "B2_96": (0, 0, 40)},
     d=(-1, 1, 0.55), focus=CAMU,
     parts=[("campl", 1, ["CAM_PLATE"]), ("cam", 1, ["P180_camera"]), ("m2x8", 4, ["SJ53_cam_m2"]), ("led", 2, ["CAM_LED"]), ("foam", 1, None),
            ("so_cam", 2, ["B2_96"]), ("n3", 2, None)],
     text=["카메라 선 (FPC)을 먼저 카메라에 꽂아 둔다 (파란 면 방향 — 카메라 설명서).",
           "카메라를 판 <b>아래</b>에 렌즈가 아래를 보게 대고 M2 × 8 + M2 너트 4개.",
           "LED 모듈 2개를 판 아래 양옆에 폼테이프로 (불빛이 아래로).",
           "기둥 2개: M-30과 M-15를 이어 45 mm → 아래 수나사를 판 구멍에 넣고 M3 너트."],
     tips=["그림은 아래에서 올려다본 모습."])
step(id="E3", sec="E", title="위판 + 카메라 달기", place="프레임 위",
     new=TOPP + CAMU, merge=["cam"], off=dict(offs(CAMU + ["P105_top_plate"], (0, 0, 120)), top_bolts=(0, 0, 160)),
     d=(-1, 1, -0.75), focus=TOPP + CAMU + TOP_X + ["P100b_rail_top_xm170"],
     parts=[("top105", 1, ["P105_top_plate"]), ("m3x8", 2, None), ("m5x10", 4, ["top_bolts"]), ("sn5", 4, None)],
     text=["카메라 기둥 2개 위 끝을 위판 구멍에 맞추고, 위판 위에서 M3 × 8 2개로 매단다.",
           "위 가로대 윗면 홈에 스프링너트 4개 → 위판을 얹고 (카메라가 아래로 매달림) M5 × 10 4개.",
           "카메라 렌즈가 격자판 바로 위에 오는지 위에서 내려다본다 (렌즈 ↔ 격자 약 153 mm)."],
     warns=["카메라를 5 mm 넘게 내리지 않는다 — 든 펜에 닿는다."])
step(id="E4", sec="E", title="파이 선반 만들기", place="작업대", ctx="pi",
     new=PIU, off={"pi_PB": (0, -35, 0), "B2_97": (0, -20, 0), "SJR_pi5_st": (0, -35, 25), "SJR_pi5": (0, -35, 60)},
     d=(1, -1, -0.6), focus=PIU,
     parts=[("pipv", 1, ["pi_PV"]), ("pipb", 1, ["pi_PB"]), ("falcs", 2, ["B2_97"]), ("m3x8", 4, None), ("n3", 4, None),
            ("so_pi", 4, ["SJR_pi5_st"]), ("m25x5", 8, None), ("pi5", 1, ["SJR_pi5"])],
     text=["알루미늄 벽판 (PV)과 흰 아크릴 바닥판 (PB)을 FALCS ㄱ자 2개로 'ㄴ' 모양으로 잇는다: M3 × 8 + 너트 4개.",
           "바닥판 위에 M2.5 기둥 4개 (밑에서 M2.5 × 5).",
           "파이 5를 그림 방향대로 얹고 위에서 M2.5 × 5 4개."],
     tips=["파이 쿨러·AI HAT+는 먼저 파이에 끼워 둔다. USB · 카메라 선을 꽂을 쪽이 벽에 막히지 않는지 미리 본다."])
step(id="E5", sec="E", title="파이 선반 달기", place="프레임 위 (왼쪽 뒤)",
     new=PIU + PIB, merge=["pi"], off=dict(offs(PIU, (0, -70, 0)), pi_bolts=(0, -110, 0)),
     d=(0.55, 1, 0.3), focus=PIU + ["P100c_cross_top_yp80"], hide=TOPP + CAMU + ["P100a_post_1"],
     parts=[("m5x8", 2, ["pi_bolts"]), ("sn5", 2, None)],
     text=["<b>뒤</b> 위 가로대의 <b>앞면</b> 홈에 스프링너트 2개.",
           "벽판을 대고 M5 × 8 2개 — 선반이 가로대 아래로 매달려 왼쪽 위에 온다.",
           "카메라 선을 파이 CAM 단자에 꽂는다 (500 mm 선은 12/01쯤 옴 — 그 전엔 300 mm 예비 선)."])
# ===== G 나중
step(id="G1", sec="G", title="(나중) 상용 트랩 위에 씌우기 + 칼라", place="바닥", later=True,
     new=TRAP + COLLAR, off=dict(offs(TRAP, (0, 0, -60)), P102_collar=(0, 0, -30), P100m_bolt_M3x10_deck=(0, 0, -45)),
     d=(-1, 1, -0.45), focus=FRAME_ALL,
     parts=[("trap", 1, TRAP), ("collar102", 1, ["P102_collar"])],
     text=["트랩 (먹이 컵 + 몸통 + 차양)을 바닥에 놓고, 장치를 들어 트랩 위에 씌운다 — 트랩이 바닥 사각형 한가운데.",
           "칼라 102 (아크릴 3장)로 트랩 위 링과 데크 아래를 잇는다 (데크 밑에서 M3 × 10 4개 + 데크 위 M3 너트).",
           "12/2 시연에는 없어도 된다 (표본을 손으로 넣음)."])
step(id="G2", sec="G", title="(나중) 입구 깔때기 + 입구 관", place="데크", later=True,
     new=ENTRY, off={"P111_entry_funnel": (0, 0, 0), "P110_entry_duct": (0, 0, 60)}, d=(-1, 1, -0.6),
     focus=ENTRY + MK6 + ["P101_deck"], hide=HDECK + TOP_X + ["tb_top", "P105_top_plate", "top_bolts"],
     parts=[("funnel111", 1, ["P111_entry_funnel"]), ("tube110", 1, ["P110_entry_duct"])],
     text=["입구 깔때기 111을 데크 가운데 구멍 위에 세운다 (넓은 쪽 아래).",
           "아크릴 관 110 (115 mm)을 깔때기 위 소켓과 입구 문 하우징 112의 아래 소켓 사이에 끼운다.",
           "방생 관 174 (아크릴, 맞춤 주문)는 방생 문 하우징 176의 출구 소켓에 끼워 장치 밖으로 — 그림에는 없음."])
step(id="G3", sec="G", title="(나중) 격리 관 + 포획통", place="위판", later=True,
     new=ISO, off={"SW_117": (0, 0, 0), "P173_isolation_funnel": (0, 0, 40), "P104_dome_coupling": (0, 0, 70), "PREF_trap_container": (0, 0, 110), "PREF_trap_cap": (0, 0, 110), "PREF_trap_silicone_star": (0, 0, 110)},
     d=(-1, 1, -0.45), focus=FRAME_ALL + ISO,
     parts=[("tube172", 1, ["SW_117"]), ("funnel173", 1, ["P173_isolation_funnel"]), ("dome104", 1, ["P104_dome_coupling"]), ("container", 1, ["PREF_trap_container"])],
     text=["격리 관 172 (195 mm)를 112 하우징 격리 쪽 소켓에 꽂아 위로 세운다.",
           "격리 깔때기 173을 위판 가운데 구멍 위에서 관 끝에 끼운다.",
           "돔 연결부 104 (아크릴 2장)로 상용 포획통을 위판 위에 얹는다."])

STEP_IDS = [s["id"] for s in S]


# ---------------------------------------------------------------- done 목록 계산
def compute():
    ctxkeys = {"main": []}
    out = []
    for s in S:
        c = s["ctx"]
        ctxkeys.setdefault(c, [])
        done = [k for k in ctxkeys[c] if k not in s["new"]]
        if s["later"]:
            done = done  # 나중 단계도 지금까지 모양 위에
        done = [k for k in done if k not in s["hide"]]
        s2 = dict(s)
        s2["done"] = done
        out.append(s2)
        # 합치기
        for m in s["merge"]:
            for k in ctxkeys.get(m, []):
                if k not in ctxkeys[c]:
                    ctxkeys[c].append(k)
        for k in s["new"]:
            if k not in ctxkeys[c]:
                ctxkeys[c].append(k)
    return out, ctxkeys


if __name__ == "__main__":
    st, ck = compute()
    print(len(st), "steps")
    allp = set()
    for s in st:
        for p in s["parts"]:
            assert p[0] in P, p[0]
    print({k: len(v) for k, v in ck.items()})
