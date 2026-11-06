// 2단계 시험 — UNO 2 + 빛 게이트 1쌍 (회로 시험용, 펌웨어 아님) — 서현 CAP-AI-33, 2026-11-06
// 연결: 게이트 허브 → 수신 흰 선(+10k 풀업) → A0 (G1),  송신 검정 → MOSFET Q4 OUT-, Q4 TRIG ← D4,  레일 감지 D2 (10k 직렬)
// 확인: ① 손으로 빛을 가리면 "BLOCK" ② 's' 입력 → 자가 시험: 송신 끔 → LOW여야, 켬 → HIGH여야 ③ 비상 정지 누르면 RAIL=0
const int PIN_GATE = A0;   // G1
const int PIN_EMIT = 4;    // EMIT_EN (HIGH = 송신 켬)
const int PIN_RAIL = 2;    // 힘 전기 감지

void setup() {
  Serial.begin(115200);
  pinMode(PIN_GATE, INPUT);          // 풀업은 허브의 10 kΩ (내부 풀업 안 씀)
  pinMode(PIN_RAIL, INPUT);
  pinMode(PIN_EMIT, OUTPUT);
  digitalWrite(PIN_EMIT, HIGH);
  Serial.println(F("b2_gate: 's' = self-test"));
}

bool selfTest() {
  digitalWrite(PIN_EMIT, LOW);  delay(20);
  bool offOk = (digitalRead(PIN_GATE) == LOW);    // 송신 끔 → 빛 없음 → 수신 LOW
  digitalWrite(PIN_EMIT, HIGH); delay(20);
  bool onOk = (digitalRead(PIN_GATE) == HIGH);    // 송신 켬 → 빛 받음 → HIGH
  Serial.print(F("SELFTEST off=")); Serial.print(offOk ? F("OK") : F("FAIL"));
  Serial.print(F(" on="));          Serial.println(onOk ? F("OK") : F("FAIL"));
  return offOk && onOk;
}

int last = -1;
unsigned long tPrint = 0;
void loop() {
  if (Serial.available() && Serial.read() == 's') selfTest();
  int g = digitalRead(PIN_GATE);
  if (g != last) { Serial.println(g == LOW ? F("BLOCK") : F("CLEAR")); last = g; }
  if (millis() - tPrint > 2000) { tPrint = millis(); Serial.print(F("RAIL=")); Serial.println(digitalRead(PIN_RAIL)); }
}
