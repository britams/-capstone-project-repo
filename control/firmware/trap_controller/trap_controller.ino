// trap_controller.ino — 말벌 마킹 모듈 구동부 (Arduino UNO) · CAP-AI-SJ-19
// 담당: 이승준 (control/). 인터페이스: design/인터페이스_정의서.md (2차, D5 4차 안 B)
//
// 구동기 7개 + 하중 센서
//   스테핑 (28BYJ-48 + ULN2003, T8 리드스크루 리드 8 mm)
//     F = 바닥 승강 153   : D2  D3  D4  D5
//     X = 마커 X 215      : D6  D7  D8  D9
//     Y = 마커 Y 209      : D10 D11 D12 D13
//   서보 (SG90/MG90S)
//     IN  = 입구 문 112        : A0
//     CAP = 격리 문 170 (포획통) : A1
//     REL = 방생 문 176        : A2
//     PEN = 펜 들기 205        : A3
//   하중 센서 148 (로드셀 + HX711) : DT A4, SCK A5
//   ※ UNO는 D0·D1(시리얼)을 빼면 18핀 → 여기서 18핀 모두 사용. 적외선 진입 센서 114는 Pi GPIO로.
//
// 시리얼 115200, 한 줄 = 명령 하나 (대문자, 공백 구분, 줄 끝 \n)
//   응답:  OK ...   (명령 접수)   ERR <이유>   DONE <...> (이동 끝)   EVT <...> (사건)
//   PING                       → OK PONG
//   STATUS                     → OK STATUS F=<mm> X=<mm> Y=<mm> MOVING=<FXY> LOAD=<g> PEN=<UP|DOWN>
//   MOVE <F|X|Y> <mm>          절대 위치로 이동 → OK, 끝나면 DONE MOVE <축> <mm>
//   STOP                       모든 스테핑 즉시 정지 → OK STOP
//   ZERO <F|X|Y> <mm>          현재 위치를 <mm>로 정함 (원점 스위치가 없어서 필요 — 아래 주의)
//   SPEED <F|X|Y> <us>         반걸음 간격 µs (기본 1000 ≈ 1.96 mm/s, 최소 800)
//   LIMIT <F|X|Y> <min> <max>  소프트 한계 mm
//   HOLD <F|X|Y> <0|1>         멈춘 뒤 코일 전류 유지 (기본: F=1, X·Y=0)
//   PRESS <g> [<mm>]           바닥을 올리다 하중 ≥ g 이면 정지 (최대 <mm>까지) → DONE PRESS <mm> <g> | DONE PRESS LIMIT <mm> <g>
//   DOOR <IN|CAP|REL> <OPEN|CLOSE>
//   PEN <UP|DOWN>
//   SERVO <IN|CAP|REL|PEN> <deg>   각도 직접 (보정용)
//   SETDOOR <IN|CAP|REL|PEN> <열림·위 각도> <닫힘·아래 각도>   보정값 저장(전원 끄면 사라짐)
//   LOAD                       → OK LOAD <g> <raw>
//   TARE                       → 영점
//   CAL <g/raw 배율>            → 하중 배율 (예: CAL 0.00235)
//   WATCHDOG <s>               s초 동안 명령이 없으면 정지·펜 들기 (0 = 끔, 기본 0)
//
// 주의 (미검증·잠정)
//   - 원점(리밋) 스위치가 없음 → 켤 때 위치 = 0으로 가정. 바닥은 맨 아래, 마커는 대기 자리에 둔 채 켤 것.
//   - 28BYJ-48 반걸음 4075.77/회전 (기어비 63.68) [가능성 높음], 리드 8 mm → 약 509.5 반걸음/mm.
//   - 서보 4개 + 스테핑 3개 전류는 UNO 5V 핀으로 감당 못 함 → 별도 5V 전원 (GND는 공통).

#include <Servo.h>

// ---------------- 스테핑 ----------------
const float STEPS_PER_MM = 4075.7728f / 8.0f;
const uint8_t HALF[8][4] = {{1,0,0,0},{1,1,0,0},{0,1,0,0},{0,1,1,0},{0,0,1,0},{0,0,1,1},{0,0,0,1},{1,0,0,1}};

struct Axis {
  char name;
  uint8_t pins[4];
  long pos;          // 반걸음
  long target;
  int phase;         // 0..7
  unsigned long intervalUs;
  unsigned long lastUs;
  float minMm, maxMm;
  bool hold;
  bool moving;
};

Axis axes[3] = {
  {'F', {2, 3, 4, 5},     0, 0, 0, 1000, 0, 0.0f,   36.5f, true,  false},
  {'X', {6, 7, 8, 9},     0, 0, 0, 1000, 0, -18.0f, 18.0f, false, false},
  {'Y', {10, 11, 12, 13}, 0, 0, 0, 1000, 0, -40.0f, 18.0f, false, false},
};

// PRESS 모드 (바닥만)
bool pressActive = false;
float pressGrams = 0;

// ---------------- 서보 ----------------
struct Door { const char* name; uint8_t pin; int openDeg; int closeDeg; Servo s; };
// openDeg = 열림(PEN은 '들기'), closeDeg = 닫힘(PEN은 '놓기')
Door doors[4] = {
  {"IN",  A0, 90, 0, Servo()},
  {"CAP", A1, 90, 0, Servo()},
  {"REL", A2, 90, 0, Servo()},
  {"PEN", A3, 60, 0, Servo()},
};
bool penUp = true;

// ---------------- HX711 ----------------
const uint8_t HX_DT = A4, HX_SCK = A5;
long hxOffset = 0;
float hxScale = 1.0f;   // g / raw (CAL로 정함)
long hxLastRaw = 0;

// ---------------- 기타 ----------------
char line[64];
uint8_t lineLen = 0;
unsigned long watchdogMs = 0, lastCmdMs = 0;

Axis* findAxis(const char* t) {
  if (!t || t[1] != '\0') return nullptr;
  for (int i = 0; i < 3; i++) if (axes[i].name == t[0]) return &axes[i];
  return nullptr;
}
Door* findDoor(const char* t) {
  if (!t) return nullptr;
  for (int i = 0; i < 4; i++) if (strcmp(doors[i].name, t) == 0) return &doors[i];
  return nullptr;
}

void coils(Axis& a, bool on) {
  for (int k = 0; k < 4; k++) digitalWrite(a.pins[k], on ? HALF[a.phase][k] : 0);
}

float posMm(const Axis& a) { return a.pos / STEPS_PER_MM; }

bool hxReady() { return digitalRead(HX_DT) == LOW; }
long hxReadRaw() {               // 호출 전 hxReady() 확인. 128배 이득, A 채널
  long v = 0;
  noInterrupts();
  for (int i = 0; i < 24; i++) {
    digitalWrite(HX_SCK, HIGH); delayMicroseconds(1);
    v = (v << 1) | digitalRead(HX_DT);
    digitalWrite(HX_SCK, LOW); delayMicroseconds(1);
  }
  digitalWrite(HX_SCK, HIGH); delayMicroseconds(1); digitalWrite(HX_SCK, LOW);
  interrupts();
  if (v & 0x800000L) v |= 0xFF000000L;   // 24비트 부호 확장
  return v;
}
float grams() { return (hxLastRaw - hxOffset) * hxScale; }
void hxPoll() { if (hxReady()) hxLastRaw = hxReadRaw(); }

void reply(const char* s) { Serial.println(s); }

void startMove(Axis& a, float mm) {
  a.target = lround(mm * STEPS_PER_MM);
  a.moving = (a.target != a.pos);
  a.lastUs = micros();
  if (!a.moving) {
    Serial.print(F("DONE MOVE ")); Serial.print(a.name); Serial.print(' '); Serial.println(posMm(a), 3);
  }
}

void stopAll() {
  for (int i = 0; i < 3; i++) { axes[i].target = axes[i].pos; axes[i].moving = false; if (!axes[i].hold) coils(axes[i], false); }
  pressActive = false;
}

void setPen(bool up) {
  doors[3].s.write(up ? doors[3].openDeg : doors[3].closeDeg);
  penUp = up;
}

void handle(char* cmd) {
  char* tok[5] = {0};
  int n = 0;
  for (char* p = strtok(cmd, " "); p && n < 5; p = strtok(nullptr, " ")) tok[n++] = p;
  if (n == 0) return;
  lastCmdMs = millis();

  if (!strcmp(tok[0], "PING")) { reply("OK PONG"); return; }

  if (!strcmp(tok[0], "STATUS")) {
    Serial.print(F("OK STATUS F=")); Serial.print(posMm(axes[0]), 3);
    Serial.print(F(" X=")); Serial.print(posMm(axes[1]), 3);
    Serial.print(F(" Y=")); Serial.print(posMm(axes[2]), 3);
    Serial.print(F(" MOVING="));
    bool any = false;
    for (int i = 0; i < 3; i++) if (axes[i].moving) { Serial.print(axes[i].name); any = true; }
    if (!any) Serial.print('-');
    Serial.print(F(" LOAD=")); Serial.print(grams(), 1);
    Serial.print(F(" PEN=")); Serial.println(penUp ? F("UP") : F("DOWN"));
    return;
  }

  if (!strcmp(tok[0], "MOVE") && n == 3) {
    Axis* a = findAxis(tok[1]);
    if (!a) { reply("ERR AXIS"); return; }
    float mm = atof(tok[2]);
    if (mm < a->minMm || mm > a->maxMm) { reply("ERR LIMIT"); return; }
    if (a->name == 'F') pressActive = false;
    Serial.print(F("OK MOVE ")); Serial.print(a->name); Serial.print(' '); Serial.println(mm, 3);
    startMove(*a, mm);
    return;
  }

  if (!strcmp(tok[0], "STOP")) { stopAll(); reply("OK STOP"); return; }

  if (!strcmp(tok[0], "ZERO") && n == 3) {
    Axis* a = findAxis(tok[1]);
    if (!a) { reply("ERR AXIS"); return; }
    if (a->moving) { reply("ERR BUSY"); return; }
    a->pos = a->target = lround(atof(tok[2]) * STEPS_PER_MM);
    reply("OK ZERO");
    return;
  }

  if (!strcmp(tok[0], "SPEED") && n == 3) {
    Axis* a = findAxis(tok[1]);
    long us = atol(tok[2]);
    if (!a) { reply("ERR AXIS"); return; }
    if (us < 800) { reply("ERR SPEED_MIN_800"); return; }
    a->intervalUs = us;
    reply("OK SPEED");
    return;
  }

  if (!strcmp(tok[0], "LIMIT") && n == 4) {
    Axis* a = findAxis(tok[1]);
    if (!a) { reply("ERR AXIS"); return; }
    float lo = atof(tok[2]), hi = atof(tok[3]);
    if (lo >= hi) { reply("ERR RANGE"); return; }
    a->minMm = lo; a->maxMm = hi;
    reply("OK LIMIT");
    return;
  }

  if (!strcmp(tok[0], "HOLD") && n == 3) {
    Axis* a = findAxis(tok[1]);
    if (!a) { reply("ERR AXIS"); return; }
    a->hold = atoi(tok[2]) != 0;
    if (!a->moving) coils(*a, a->hold);
    reply("OK HOLD");
    return;
  }

  if (!strcmp(tok[0], "PRESS") && (n == 2 || n == 3)) {
    Axis& f = axes[0];
    float maxMm = (n == 3) ? atof(tok[2]) : f.maxMm;
    if (maxMm > f.maxMm) maxMm = f.maxMm;
    pressGrams = atof(tok[1]);
    if (pressGrams <= 0) { reply("ERR GRAMS"); return; }
    pressActive = true;
    reply("OK PRESS");
    startMove(f, maxMm);
    if (!f.moving) pressActive = false;
    return;
  }

  if (!strcmp(tok[0], "DOOR") && n == 3) {
    Door* d = findDoor(tok[1]);
    if (!d || d == &doors[3]) { reply("ERR DOOR"); return; }
    if (!strcmp(tok[2], "OPEN")) d->s.write(d->openDeg);
    else if (!strcmp(tok[2], "CLOSE")) d->s.write(d->closeDeg);
    else { reply("ERR STATE"); return; }
    reply("OK DOOR");
    return;
  }

  if (!strcmp(tok[0], "PEN") && n == 2) {
    if (!strcmp(tok[1], "UP")) setPen(true);
    else if (!strcmp(tok[1], "DOWN")) setPen(false);
    else { reply("ERR STATE"); return; }
    reply("OK PEN");
    return;
  }

  if (!strcmp(tok[0], "SERVO") && n == 3) {
    Door* d = findDoor(tok[1]);
    int deg = atoi(tok[2]);
    if (!d) { reply("ERR DOOR"); return; }
    if (deg < 0 || deg > 180) { reply("ERR DEG"); return; }
    d->s.write(deg);
    reply("OK SERVO");
    return;
  }

  if (!strcmp(tok[0], "SETDOOR") && n == 4) {
    Door* d = findDoor(tok[1]);
    if (!d) { reply("ERR DOOR"); return; }
    d->openDeg = constrain(atoi(tok[2]), 0, 180);
    d->closeDeg = constrain(atoi(tok[3]), 0, 180);
    reply("OK SETDOOR");
    return;
  }

  if (!strcmp(tok[0], "LOAD")) {
    Serial.print(F("OK LOAD ")); Serial.print(grams(), 1); Serial.print(' '); Serial.println(hxLastRaw);
    return;
  }
  if (!strcmp(tok[0], "TARE")) { hxOffset = hxLastRaw; reply("OK TARE"); return; }
  if (!strcmp(tok[0], "CAL") && n == 2) { hxScale = atof(tok[1]); reply("OK CAL"); return; }

  if (!strcmp(tok[0], "WATCHDOG") && n == 2) { watchdogMs = (unsigned long)(atof(tok[1]) * 1000); reply("OK WATCHDOG"); return; }

  reply("ERR UNKNOWN");
}

void stepAxes() {
  unsigned long now = micros();
  for (int i = 0; i < 3; i++) {
    Axis& a = axes[i];
    if (!a.moving) continue;
    if (now - a.lastUs < a.intervalUs) continue;
    a.lastUs = now;
    int dir = (a.target > a.pos) ? 1 : -1;
    a.phase = (a.phase + dir + 8) % 8;
    a.pos += dir;
    coils(a, true);
    if (i == 0 && pressActive && dir > 0 && grams() >= pressGrams) {
      a.target = a.pos;
      a.moving = false;
      pressActive = false;
      if (!a.hold) coils(a, false);
      Serial.print(F("DONE PRESS ")); Serial.print(posMm(a), 3); Serial.print(' '); Serial.println(grams(), 1);
      continue;
    }
    if (a.pos == a.target) {
      a.moving = false;
      if (!a.hold) coils(a, false);
      if (i == 0 && pressActive) {
        pressActive = false;
        Serial.print(F("DONE PRESS LIMIT ")); Serial.print(posMm(a), 3); Serial.print(' '); Serial.println(grams(), 1);
      } else {
        Serial.print(F("DONE MOVE ")); Serial.print(a.name); Serial.print(' '); Serial.println(posMm(a), 3);
      }
    }
  }
}

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 3; i++) for (int k = 0; k < 4; k++) pinMode(axes[i].pins[k], OUTPUT);
  for (int i = 0; i < 3; i++) coils(axes[i], axes[i].hold);
  for (int i = 0; i < 4; i++) doors[i].s.attach(doors[i].pin);
  // 켤 때 상태 = 상태 머신 1 '대기' : 입구 열림, 격리·방생 닫힘, 펜 들기 (마커는 캡 컵 위에서 놓기는 Pi가 지시)
  doors[0].s.write(doors[0].openDeg);
  doors[1].s.write(doors[1].closeDeg);
  doors[2].s.write(doors[2].closeDeg);
  setPen(true);
  pinMode(HX_DT, INPUT);
  pinMode(HX_SCK, OUTPUT);
  digitalWrite(HX_SCK, LOW);
  lastCmdMs = millis();
  reply("EVT READY trap_controller v0.1");
}

void loop() {
  while (Serial.available()) {
    char c = Serial.read();
    if (c == '\r') continue;
    if (c == '\n') {
      line[lineLen] = '\0';
      for (uint8_t i = 0; i < lineLen; i++) line[i] = toupper(line[i]);
      handle(line);
      lineLen = 0;
    } else if (lineLen < sizeof(line) - 1) {
      line[lineLen++] = c;
    } else {
      lineLen = 0;
      reply("ERR TOO_LONG");
    }
  }
  hxPoll();
  stepAxes();
  if (watchdogMs && millis() - lastCmdMs > watchdogMs) {
    stopAll();
    setPen(true);
    reply("EVT WATCHDOG_STOP");
    lastCmdMs = millis();
  }
}
