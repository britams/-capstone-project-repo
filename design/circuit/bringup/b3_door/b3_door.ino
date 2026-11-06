// 3단계 시험 — UNO 2 + 입구 문 서보 1개 + 문 빔 2개 (회로 시험용, 펌웨어 아님) — 서현 CAP-AI-33
// 연결: 서보 허브 S2 신호 ← D9, 서보 전원은 허브(+5V_B), G2 → A1, G2b → A2, EMIT_EN D4
// 규칙 (A2 문닫기): 두 빔 모두 0.2 s 비어야 닫기 시작 / 닫는 중 하나라도 막히면 바로 다시 열기 / 3번 실패 → BLOCKED
// 확인: 'c' 닫기, 'o' 열기. ① 빔을 막은 채 'c' → "WAIT" (안 닫힘) ② 닫는 중 손가락으로 빔을 끊으면 "REOPEN"
#include <Servo.h>
const int PIN_SERVO = 9, PIN_G2 = A1, PIN_G2B = A2, PIN_EMIT = 4;
const int ANG_OPEN = 90, ANG_CLOSED = 0;   // [실물에서 맞춤] 문 열림·닫힘 각도
const int STEP_DEG = 2, STEP_MS = 20;      // 닫는 속도 약 100 °/s
Servo door;
int pos = ANG_OPEN;

bool beamsClear() { return digitalRead(PIN_G2) == HIGH && digitalRead(PIN_G2B) == HIGH; }

bool clearFor(unsigned long ms) {
  unsigned long t0 = millis();
  while (millis() - t0 < ms) { if (!beamsClear()) return false; }
  return true;
}

void openDoor() {
  door.attach(PIN_SERVO);
  door.write(ANG_OPEN); pos = ANG_OPEN;
  delay(400);
  door.detach();                            // 열려 있을 때는 힘 빼기 (전류·떨림 줄임)
  Serial.println(F("OPEN"));
}

bool closeDoor() {
  for (int tries = 1; tries <= 3; tries++) {
    unsigned long t0 = millis();
    while (!clearFor(200)) {                // 두 빔 모두 0.2 s 빌 때까지
      if (millis() - t0 > 10000) { Serial.println(F("WAIT timeout")); return false; }
      Serial.println(F("WAIT"));
      delay(100);
    }
    door.attach(PIN_SERVO);
    bool ok = true;
    for (int a = pos; a >= ANG_CLOSED; a -= STEP_DEG) {
      if (!beamsClear()) { ok = false; break; }   // 닫는 중 막힘 → 다시 열기
      door.write(a); pos = a;
      delay(STEP_MS);
    }
    if (ok) { Serial.println(F("CLOSED")); return true; }
    door.write(ANG_OPEN); pos = ANG_OPEN;
    Serial.print(F("REOPEN try=")); Serial.println(tries);
    delay(1000);
  }
  Serial.println(F("BLOCKED"));
  return false;
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_G2, INPUT); pinMode(PIN_G2B, INPUT);
  pinMode(PIN_EMIT, OUTPUT); digitalWrite(PIN_EMIT, HIGH);
  openDoor();
  Serial.println(F("b3_door: 'c' close, 'o' open"));
}

void loop() {
  if (!Serial.available()) return;
  char c = Serial.read();
  if (c == 'c') closeDoor();
  if (c == 'o') openDoor();
}
