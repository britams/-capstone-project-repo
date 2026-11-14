// zap_setup.ino — mightyZAP D7-6PT-3 최대 힘 줄이기 (한 번만 올려서 씀) · 서현 CAP-AI-62, 2026-11-15
// 왜: PWM으로는 힘을 정할 수 없음. 대신 TTL로 'Motor Operating Rate'(0~1023, 기본 1023)를 낮추면 최대 출력·정지력이 같이 줄어듦.
//     이 값은 액추에이터 안 비휘발 메모리에 저장됨 → 한 번 넣으면 끝 [확실 — 제조사 D7 설명서]. PWM에서도 적용되는지는 실물로 확인 [가능성 높음]
// 연결: UNO 1의 D2(평소 PWM 선 그대로) — 같은 데이터 핀이 PWM·TTL을 스스로 알아봄 [확실 — 설명서]. 쓰기만 하므로 TX 한 줄로 충분.
// 쓰는 법: 이 스케치를 UNO 1에 올림 → 시리얼 모니터 115200 → 숫자(400~1023) 입력 + 엔터 → 끝나면 trap_motion을 다시 올림.
//          저울 위에서 PRESS 힘을 재며 숫자를 낮춤 (400 밑은 안 움직일 수 있음 — 설명서)
// 패킷 (IR 프로토콜, Store Data 0xF3): FF FF FF ID SIZE F3 ADDR DATA_L DATA_H CHK, SIZE = 인수 수 + 2 = 5,
//   CHK = 0xFF − (ID + SIZE + F3 + ADDR + DATA…)의 아래 바이트. 기본 ID 0, 57600 bps [확실 — 설명서 예 FF FF FF 00 04 F3 80 00 88]
#include <SoftwareSerial.h>
const uint8_t ZAP_PIN = 2;
SoftwareSerial zap(10, ZAP_PIN);   // RX는 안 씀 (D10은 이 스케치에서 비어 있음)

void storeRate(uint16_t rate) {
  uint8_t p[] = {0xFF, 0xFF, 0xFF, 0x00, 0x05, 0xF3, 0x0E, (uint8_t)(rate & 0xFF), (uint8_t)(rate >> 8), 0};
  uint8_t sum = 0;
  for (uint8_t i = 3; i < 9; i++) sum += p[i];
  p[9] = 0xFF - sum;
  zap.write(p, sizeof p);
  Serial.print(F("SENT"));
  for (uint8_t i = 0; i < sizeof p; i++) { Serial.print(' '); if (p[i] < 16) Serial.print('0'); Serial.print(p[i], HEX); }
  Serial.println();
}

void setup() {
  Serial.begin(115200);
  zap.begin(57600);
  Serial.println(F("EVT READY zap_setup — 400~1023 입력 (기본 1023)"));
}

void loop() {
  if (!Serial.available()) return;
  long v = Serial.parseInt();
  while (Serial.available()) Serial.read();
  if (v < 400 || v > 1023) { Serial.println(F("ERR RANGE 400~1023")); return; }
  storeRate((uint16_t)v);
  Serial.print(F("OK RATE ")); Serial.println(v);
}
