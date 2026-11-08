# 허브 기판 핀 표 (자동 생성 — `전기회로/hub_boards.py`, 고치지 말고 스크립트를 고칠 것)

## 게이트 허브 (70 × 30 mm, 구멍 27 × 12)

| 구멍 (칸, 줄) | 표시 | 노드 (circuit.py) | 넷 |
|---|---|---|---|
| c2, r9 | G2 C | `PT_G2.C` | +5V_B |
| c2, r8 | G2 A | `LED_G2.A` | LEDA_G2 |
| c2, r7 | G2 E | `PT_G2.E` | U2_G2 |
| c2, r6 | G2 K | `LED_G2.K` | EMIT_LO |
| c3, r7 | →UNO2 A0 | `U2.A0` | U2_G2 |
| c4, r9 | G2b C | `PT_G2b.C` | +5V_B |
| c4, r8 | G2b A | `LED_G2b.A` | LEDA_G2b |
| c4, r7 | G2b E | `PT_G2b.E` | U2_G2b |
| c4, r6 | G2b K | `LED_G2b.K` | EMIT_LO |
| c5, r7 | →UNO2 A1 | `U2.A1` | U2_G2b |
| c6, r9 | G3 C | `PT_G3.C` | +5V_B |
| c6, r8 | G3 A | `LED_G3.A` | LEDA_G3 |
| c6, r7 | G3 E | `PT_G3.E` | U2_G3 |
| c6, r6 | G3 K | `LED_G3.K` | EMIT_LO |
| c7, r7 | →UNO2 A2 | `U2.A2` | U2_G3 |
| c8, r9 | G3b C | `PT_G3b.C` | +5V_B |
| c8, r8 | G3b A | `LED_G3b.A` | LEDA_G3b |
| c8, r7 | G3b E | `PT_G3b.E` | U2_G3b |
| c8, r6 | G3b K | `LED_G3b.K` | EMIT_LO |
| c9, r7 | →UNO2 A3 | `U2.A3` | U2_G3b |
| c10, r9 | G5 C | `PT_G5.C` | +5V_B |
| c10, r8 | G5 A | `LED_G5.A` | LEDA_G5 |
| c10, r7 | G5 E | `PT_G5.E` | U2_G5 |
| c10, r6 | G5 K | `LED_G5.K` | EMIT_LO |
| c11, r7 | →UNO2 A4 | `U2.A4` | U2_G5 |
| c12, r9 | G5b C | `PT_G5b.C` | +5V_B |
| c12, r8 | G5b A | `LED_G5b.A` | LEDA_G5b |
| c12, r7 | G5b E | `PT_G5b.E` | U2_G5b |
| c12, r6 | G5b K | `LED_G5b.K` | EMIT_LO |
| c13, r7 | →UNO2 A5 | `U2.A5` | U2_G5b |
| c14, r9 | G1 TX+ | `TX_G1.V+` | +5V_B |
| c14, r8 | G1 RX+ | `RX_G1.V+` | +5V_B |
| c14, r7 | G1 흰 | `RX_G1.OUT` | U2_G1 |
| c14, r6 | G1 RX− | `RX_G1.GND` | GND |
| c14, r5 | G1 TX− | `TX_G1.GND` | EMIT_LO |
| c15, r7 | →UNO2 D7 | `U2.D7` | U2_G1 |
| c16, r9 | G4 TX+ | `TX_G4.V+` | +5V_B |
| c16, r8 | G4 RX+ | `RX_G4.V+` | +5V_B |
| c16, r7 | G4 흰 | `RX_G4.OUT` | U2_G4 |
| c16, r6 | G4 RX− | `RX_G4.GND` | GND |
| c16, r5 | G4 TX− | `TX_G4.GND` | EMIT_LO |
| c17, r7 | →UNO2 D8 | `U2.D8` | U2_G4 |
| c18, r9 | G6 TX+ | `TX_G6.V+` | +5V_B |
| c18, r8 | G6 RX+ | `RX_G6.V+` | +5V_B |
| c18, r7 | G6 흰 | `RX_G6.OUT` | U2_G6 |
| c18, r6 | G6 RX− | `RX_G6.GND` | GND |
| c18, r5 | G6 TX− | `TX_G6.GND` | EMIT_LO |
| c19, r7 | →UNO2 D12 | `U2.D12` | U2_G6 |
| c20, r7 | →UNO2 D2 | `U2.D2` | U2_RAIL |
| c21, r10 | +5V 입력 | `TB.+5V` | +5V_B |
| c21, r1 | →Q4 OUT− | `Q4.OUT-` | EMIT_LO |
| c21, r0 | GND | `TB.GND` | GND |
| c24, r0 | →Q4 GND | `Q4.GND` | GND |

저항: RLED_G2 220 (c3 r9–r8), RL_G2 10k (c3 r6–r5), RLED_G2b 220 (c5 r9–r8), RL_G2b 10k (c5 r6–r5), RLED_G3 220 (c7 r9–r8), RL_G3 10k (c7 r6–r5), RLED_G3b 220 (c9 r9–r8), RL_G3b 10k (c9 r6–r5), RLED_G5 220 (c11 r9–r8), RL_G5 10k (c11 r6–r5), RLED_G5b 220 (c13 r9–r8), RL_G5b 10k (c13 r6–r5), R_G1 10k (c15 r9–r8), R_G4 10k (c17 r9–r8), R_G6 10k (c19 r9–r8), R_RS 10k (c20 r9–r8)

수: 헤더핀 49, 전선자리 4, 저항 16, 땜납다리 122, 버스 3, 점퍼 9, 구멍 27 × 12

판과 안 이어지는 부품: J_I2C (JST XH 4P) 가운데 (61.67, 16.27) mm, 12.40 × 5.75 — 판 왼쪽 아래 귀퉁이 기준, 긴 쪽이 x

## 서보 허브 (60 × 40 mm, 구멍 23 × 15)

| 구멍 (칸, 줄) | 표시 | 노드 (circuit.py) | 넷 |
|---|---|---|---|
| c3, r11 | 펜 갈 | `SG90.GND` | GND |
| c3, r10 | 빨 | `SG90.V+` | +5V_B |
| c3, r9 | 주 | `SG90.SIG` | U1_PEN |
| c3, r6 | →펜 (UNO1 A0) | `U1.A0` | U1_PEN |
| c7, r11 | 입구 갈 | `MG_IN.GND` | GND |
| c7, r10 | 빨 | `MG_IN.V+` | +5V_B |
| c7, r9 | 주 | `MG_IN.SIG` | U2_DOOR_IN |
| c7, r6 | →입구 (UNO2 D9) | `U2.D9` | U2_DOOR_IN |
| c11, r11 | 격리 갈 | `MG_CAP.GND` | GND |
| c11, r10 | 빨 | `MG_CAP.V+` | +5V_B |
| c11, r9 | 주 | `MG_CAP.SIG` | U2_DOOR_CAP |
| c11, r6 | →격리 (UNO2 D10) | `U2.D10` | U2_DOOR_CAP |
| c15, r11 | 방생 갈 | `MG_REL.GND` | GND |
| c15, r10 | 빨 | `MG_REL.V+` | +5V_B |
| c15, r9 | 주 | `MG_REL.SIG` | U2_DOOR_REL |
| c15, r6 | →방생 (UNO2 D11) | `U2.D11` | U2_DOOR_REL |
| c22, r12 | GND 입력 20AWG | `TB.GND` | GND |
| c22, r4 | +5V 입력 20AWG | `TB.+5V` | +5V_B |

저항: D_RP SB540 (c17 r5–r11), C1 1000µ (c19 r11–r13), C2 0.1µ (c20 r5–r6)

수: 헤더핀 16, 전선자리 2, 저항 3, 땜납다리 61, 버스 2, 점퍼 0, 구멍 23 × 15

**구멍 넓힘** (드릴): c17 r5 → Ø1.5 mm, c17 r11 → Ø1.5 mm
