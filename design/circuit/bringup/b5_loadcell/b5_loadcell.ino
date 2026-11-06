// 5단계 시험 — UNO 1 + HX711 + 막대 로드셀 (회로 시험용, 펌웨어 아님) — 서현 CAP-AI-33
// 연결: HX711 VCC ← UNO 5V (조용한 전원), GND, DT → A1, SCK → A2, RATE 다리 → 5V (80 Hz)
//       로드셀 빨강 E+, 검정 E−, 흰색 A−, 초록 A+ (선 색은 제품마다 다를 수 있음 — 무게를 올렸을 때 숫자가 줄면 A+·A− 바꿈)
// 확인: 't' 0점, 'k' 아는 무게(예: 100 g 추)를 올리고 눌러 눈금 맞춤 → 이후 g 단위 출력. 흔들림(표준편차) 0.1 g 이하 목표 [가능성 높음]
#include <limits.h>
const int PIN_DT = A1, PIN_SCK = A2;
long offset = 0;
float gramsPerCount = 0;              // 'k'로 정함
const float CAL_G = 100.0;            // 눈금 맞출 추 무게 [실물]

bool ready() { return digitalRead(PIN_DT) == LOW; }

long readRaw() {                      // 24비트, 채널 A 게인 128 (펄스 25개)
  unsigned long t0 = millis();
  while (!ready()) { if (millis() - t0 > 200) return LONG_MIN; }
  long v = 0;
  noInterrupts();
  for (int i = 0; i < 24; i++) {
    digitalWrite(PIN_SCK, HIGH); delayMicroseconds(1);
    v = (v << 1) | digitalRead(PIN_DT);
    digitalWrite(PIN_SCK, LOW); delayMicroseconds(1);
  }
  digitalWrite(PIN_SCK, HIGH); delayMicroseconds(1); digitalWrite(PIN_SCK, LOW);   // 25번째: 다음도 A·128
  interrupts();
  if (v & 0x800000) v |= 0xFF000000;  // 부호 확장
  return v;
}

long avgRaw(int n) { long s = 0; int k = 0; for (int i = 0; i < n; i++) { long r = readRaw(); if (r != LONG_MIN) { s += r; k++; } } return k ? s / k : LONG_MIN; }

void setup() {
  Serial.begin(115200);
  pinMode(PIN_SCK, OUTPUT); digitalWrite(PIN_SCK, LOW);
  pinMode(PIN_DT, INPUT);
  delay(500);
  offset = avgRaw(40);
  Serial.println(F("b5_loadcell: t tare, k calibrate (100 g)"));
}

unsigned long tPrint = 0;
float buf[16]; int bi = 0;
void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 't') { offset = avgRaw(40); Serial.println(F("TARE")); }
    if (c == 'k') { long r = avgRaw(40) - offset; if (r != 0) gramsPerCount = CAL_G / r; Serial.print(F("CAL g/count=")); Serial.println(gramsPerCount, 8); }
  }
  long r = readRaw();
  if (r == LONG_MIN) { Serial.println(F("HX711 no data")); delay(500); return; }
  float g = gramsPerCount ? (r - offset) * gramsPerCount : (float)(r - offset);
  buf[bi] = g; bi = (bi + 1) % 16;
  if (millis() - tPrint > 500) {
    tPrint = millis();
    float m = 0, s = 0; for (int i = 0; i < 16; i++) m += buf[i]; m /= 16;
    for (int i = 0; i < 16; i++) s += (buf[i] - m) * (buf[i] - m); s = sqrt(s / 16);
    Serial.print(gramsPerCount ? F("g=") : F("raw=")); Serial.print(m, 2); Serial.print(F("  sd=")); Serial.println(s, 3);
  }
}
