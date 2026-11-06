// 4단계 시험 — UNO 1 + ULN2003 F + 바닥 모터 + 원점 스위치 F (회로 시험용, 펌웨어 아님) — 서현 CAP-AI-33
// 연결: D2~D5 → ULN F IN1~IN4, ULN 전원 = 와고 +5V_B/GND, 원점 F: A3 ↔ 스위치 NO, COM → GND (+100 nF)
// 확인: 'h' 원점 찾기 (스위치까지 내려감 → "HOME OK 걸음수"), 'u' 1000 반걸음 올림, 'd' 1000 반걸음 내림, 'x' 코일 끔
// 주의: 반걸음 간격 1000 µs (1000 Hz). 686~928 Hz(약 1080~1460 µs)는 스프링 서지 근처라 쓰지 않음 (역학계산 2차)
const int IN_PINS[4] = {2, 3, 4, 5};
const int PIN_HOME = A3;
const unsigned int HALF_US = 1000;
const long HOME_MAX = 40L * 4096 / 8;      // 40 mm (리드 8 mm, 4096 반걸음/회전) 안에 못 찾으면 실패
const byte SEQ[8][4] = {{1,0,0,0},{1,1,0,0},{0,1,0,0},{0,1,1,0},{0,0,1,0},{0,0,1,1},{0,0,0,1},{1,0,0,1}};
int phase = 0;

void coils(const byte *s) { for (int i = 0; i < 4; i++) digitalWrite(IN_PINS[i], s[i]); }
void off() { for (int i = 0; i < 4; i++) digitalWrite(IN_PINS[i], LOW); }   // HOLD F 0: 멈추면 코일 끔

void stepOnce(int dir) {
  phase = (phase + (dir > 0 ? 1 : 7)) % 8;
  coils(SEQ[phase]);
  delayMicroseconds(HALF_US);
}

bool homed() {   // 눌리면 LOW (내부 풀업), 5번 연속 LOW면 눌림 (튐 막기)
  for (int i = 0; i < 5; i++) { if (digitalRead(PIN_HOME) == HIGH) return false; delayMicroseconds(200); }
  return true;
}

void home() {
  long n = 0;
  while (!homed()) {
    stepOnce(-1);
    if (++n > HOME_MAX) { off(); Serial.println(F("HOME FAIL")); return; }
  }
  for (int i = 0; i < 200; i++) stepOnce(+1);   // 스위치에서 살짝 떨어짐
  off();
  Serial.print(F("HOME OK ")); Serial.println(n);
}

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 4; i++) pinMode(IN_PINS[i], OUTPUT);
  pinMode(PIN_HOME, INPUT_PULLUP);
  off();
  Serial.println(F("b4_axis: h home, u up, d down, x off"));
}

void loop() {
  if (!Serial.available()) return;
  char c = Serial.read();
  if (c == 'h') home();
  if (c == 'u') { for (int i = 0; i < 1000; i++) stepOnce(+1); off(); Serial.println(F("UP 1000")); }
  if (c == 'd') { for (int i = 0; i < 1000; i++) { if (homed()) break; stepOnce(-1); } off(); Serial.println(F("DOWN")); }
  if (c == 'x') { off(); Serial.println(F("OFF")); }
}
