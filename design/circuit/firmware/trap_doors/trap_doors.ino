// trap_doors.ino — UNO 2 (문·빛 게이트·조명): 문 서보 3, 빛 게이트 9쌍, 조명 2, 송신 켜기, 레일 감지 — v0.2
// 작성: 서현 (Claude, CAP-AI-41, 2026-11-08). 바탕: trap_controller.ino v0.1 명령 형식 + bringup/b2_gate·b3_door
// 사양: design/2026-11-06_펌웨어_변경요청_서현.md 2장, 핀 원본: design/circuit/circuit.py (GATE_PIN, 검사 통과)
// ※ 승준 control/ 은 고치지 않음. 승준이 동의하면 control/firmware/ 로 옮긴다.
//
// 핀 (UNO 2, 17/18 — D13 예비)
//   D2  레일 감지 (+5V_B → 10 kΩ → D2, 레일 있으면 HIGH) — INPUT (내부 풀업 쓰면 레일이 꺼져도 HIGH라 안 됨)
//   D3  위 링 조명 Q1 (PWM)      D5  아래 조명 Q2 (PWM)
//   D4  송신 켜기 Q4 (EMIT_EN, HIGH = 9개 송신 켬)
//   D6  급이 펌프 Q3 (Adafruit 3910 5 V 0.5 A, HIGH = 돎) — 11/10 밤 CAP-AI-59 (예비였던 핀)
//   D7 / D8 / D12  통로 게이트 G1 / G4 / G6 (Adafruit 2167, 외부 10 kΩ 풀업, 끊기면 LOW)
//   D9 / D10 / D11 문 서보 IN 112 / CAP 170 / REL 176 (MG90S)
//   A0..A5 문 빔 G2 G2b G3 G3b G5 G5b (포토TR 이미터 팔로어, 빛 받으면 높음 → analogRead)
//
// 시리얼 115200, 한 줄 = 명령 하나
//   PING                        → OK PONG
//   STATUS                      → OK STATUS IN=<문> CAP=<문> REL=<문> RAIL=<1|0> EMIT=<1|0> GATES=<G1 G2 G2b G3 G3b G4 G5 G5b G6 순 1/0/?>
//                                  <문> = UNKNOWN OPEN CLOSED OPENING WAIT CLOSING REOPEN BLOCKED
//   SELFTEST                    → OK SELFTEST G1=OK G2=OK ... G2b=FAIL(87)   (켤 때 자동 1번 → EVT SELFTEST ...)
//                                  문 빔 FAIL(<켬−끔>), 통로 FAIL(H) = 송신 꺼도 HIGH / FAIL(L) = 송신 켜도 LOW
//   GATES                       → OK GATES G1=1 G2=1 ... (1 이어짐, 0 끊김, ? 자가 시험 FAIL)
//   (사건) EVT GATE <이름> BLOCK|CLEAR   같은 값 20 ms 뒤에만. G1 BLOCK = 진입 신호
//   DOOR <IN|CAP|REL> OPEN      → OK DOOR, 끝나면 DONE DOOR <이름> OPEN
//   DOOR <IN|CAP|REL> CLOSE     → OK DOOR, 그다음 하나:
//                                  DONE DOOR <이름> CLOSED / ERR DOOR <이름> WAIT (2 s 안에 빔 0.2 s 비지 않음, 문은 열린 채)
//                                  / EVT DOOR <이름> REOPEN <n> (닫다가 빔 끊김 → 바로 엶, 1 s 뒤 다시) / EVT DOOR <이름> BLOCKED (3번 실패, 열어 둠)
//                                  거부: ERR RAIL · ERR DOOR <이름> BEAMFAIL · ERR DOOR <이름> EMIT_OFF · ERR BUSY
//   SERVO <IN|CAP|REL> <deg>    각도 직접 (보정용, 빔 규칙 없음 — 사람이 볼 때만) → OK SERVO, 그 문은 UNKNOWN
//   SETDOOR <IN|CAP|REL> <열림> <닫힘>  보정값 (전원 끄면 사라짐) → OK SETDOOR
//   LIGHT <TOP|BOT> <0~255>     → OK LIGHT
//   EMIT <0|1>                  송신 끔/켬 (기본 켬). 끄면 게이트 사건 멈춤, 닫기 거부 → OK EMIT
//   RAIL                        → OK RAIL 1|0. 바뀌면 EVT RAIL 0|1 (20 ms 같은 값 뒤)
//   PUMP <ms>                   급이 펌프를 ms 동안 돌림 (1~PUMP_MAX_MS) → OK PUMP, 끝나면 DONE PUMP <ms>. PUMP 0 = 바로 멈춤 → OK PUMP 0
//                                  거부: ERR RAIL · ERR BUSY (문이 움직이는 중 — 서보 붙일 때 전류와 겹치지 않게) · ERR PUMP MAX (너무 김)
//                                  돌던 중 레일 끊김·WATCHDOG → 멈춤 + EVT PUMP STOP. 펌프가 도는 동안 DOOR·SERVO 명령은 ERR BUSY
//   WATCHDOG <s>                s초 명령 없으면 닫는 중인 문을 엶 → EVT WATCHDOG_HOLD (0 = 끔)
//
// 안전 규칙 (AI 판단, 서현 위임 — CAP-AI-41)
//   - 켤 때 문 서보를 붙이지 않는다 (문은 UNKNOWN). v0.1처럼 setup에서 문을 닫으면 빔 확인 없이 닫게 됨 → Pi가 DOOR CLOSE로 닫는다.
//   - 문 서보는 한 번에 하나만 붙인다 (다른 문은 떼고), 붙이는 사이는 0.3 s 이상 (켤 때 3.27 A > 퓨즈 3 A, 변경요청 0장).
//   - 움직임이 끝나고 0.5 s 뒤 뗀다 (MG90S 기어 마찰로 자리 유지 — trap_sim, b3_door).
//   - 문 하나가 움직이는(열기·기다림·닫기·다시 열기) 동안 다른 문 명령은 ERR BUSY. Pi가 순서를 정한다.
//   - (CAP-AI-59) 펌프 한 번 최대 PUMP_MAX_MS: 고장 나도 물길이 넘치지 않는 양 (cad/feeder_check.py 1번이 이 값을 읽어 검사). 펌프와 문은 같이 안 움직임.

#include <Servo.h>

// ---------------- 값 (미검증은 실물에서 맞춤) ----------------
#define DOOR_OPEN_DEG       30    // 혼 −60° 열림 (90 기준, 인터페이스 정의서 구동기 5~7) — 미검증 (붙이는 방향)
#define DOOR_CLOSED_DEG     150   // 혼 +60° 닫힘 — 미검증
#define CLOSE_STEP_DEG      2     // 닫는 속도 2°/20 ms ≈ 100 °/s (b3_door 값) — 미검증 (끼임 시험으로)
#define CLOSE_STEP_MS       20
#define DOOR_MOVE_MS        400   // 열기(한 번에 씀) 뒤 다 갔다고 보는 시간 (b3_door) — 미검증
#define CLEAR_BEFORE_MS     200   // 사양: 두 빔이 0.2 s 계속 이어져야 닫기 시작
#define WAIT_TIMEOUT_MS     2000  // 사양: 2 s 넘으면 ERR DOOR <이름> WAIT
#define REOPEN_WAIT_MS      1000  // 다시 열고 기다림 (b3_door) — 미검증
#define RETRY_MAX           3     // 사양: 3번 실패 → BLOCKED
#define DETACH_MS           500   // 멈추고 뗄 때까지
#define SERVO_GAP_MS        300   // 서보 붙이는 사이 (사양)
#define BLOCK_SAMPLES       2     // 닫는 중 연속 2번 끊김이면 끊김 (잡음 거르기) — 미검증
#define GATE_DEBOUNCE_MS    20    // 사양: 같은 값 20 ms
#define RAIL_DEBOUNCE_MS    20
#define BEAM_MIN_DIFF       200   // 사양: 켬−끔 < 200 이면 FAIL (약 1 V)
#define SETTLE_MS           20    // 송신 켜고 끈 뒤 기다림 (b2·b3)

const uint8_t PIN_RAIL = 2, PIN_TOP = 3, PIN_EMIT = 4, PIN_BOT = 5, PIN_PUMP = 6;
const unsigned int PUMP_MAX_MS = 2000;   // 100 mL/min × 2 s = 3.3 mL ≤ 물길 넘침까지 (feeder_check 1)
unsigned long pumpOffAt = 0, pumpMs = 0;  // 0 = 멈춤

// ---------------- 빛 게이트 ----------------
struct Gate {
  const char* name;
  uint8_t pin;
  bool analog;
  int thr;               // 문 빔 문턱값 (SELFTEST)
  bool ok;               // 자가 시험 통과
  int diff;              // 켬 − 끔 (문 빔)
  char failWhy;          // 통로: 'H' / 'L'
  bool raw;              // 지금 읽은 값 (true = 이어짐)
  bool stable;           // 20 ms 같은 값으로 인정한 것
  unsigned long tChange; // raw가 바뀐 시각
};
// 순서: STATUS GATES 문자열 순서와 같음
Gate gates[9] = {
  {"G1",  7,  false, 0,   false, 0, 0, true, true, 0},
  {"G2",  A0, true,  512, false, 0, 0, true, true, 0},
  {"G2b", A1, true,  512, false, 0, 0, true, true, 0},
  {"G3",  A2, true,  512, false, 0, 0, true, true, 0},
  {"G3b", A3, true,  512, false, 0, 0, true, true, 0},
  {"G4",  8,  false, 0,   false, 0, 0, true, true, 0},
  {"G5",  A4, true,  512, false, 0, 0, true, true, 0},
  {"G5b", A5, true,  512, false, 0, 0, true, true, 0},
  {"G6",  12, false, 0,   false, 0, 0, true, true, 0},
};
bool emitOn = true;
bool selftestDone = false;
// ※ 함수는 구조체(Gate·Door)를 다 선언한 뒤에 둔다 — Arduino가 자동 원형을 첫 함수 앞에 넣기 때문

// ---------------- 문 ----------------
enum DoorState { D_UNKNOWN = 0, D_OPEN, D_CLOSED, D_OPENING, D_WAIT, D_CLOSING, D_REOPEN, D_BLOCKED };
const char* const DOOR_STATE_NAME[] = {"UNKNOWN", "OPEN", "CLOSED", "OPENING", "WAIT", "CLOSING", "REOPEN", "BLOCKED"};

struct Door {
  const char* name;
  uint8_t pin;
  uint8_t beamA, beamB;  // gates[] 번호
  int openDeg, closeDeg;
  Servo s;
  uint8_t state;
  uint8_t prev;          // WAIT가 끝났을 때 돌아갈 상태
  int cur;               // 지금 쓴 각도
  uint8_t tries;
  bool started;          // 서보를 붙이고 움직이기 시작했나 (붙이는 사이 0.3 s 기다림)
  unsigned long t;       // 상태 시각
  unsigned long tStep;
  unsigned long clearSince;
  uint8_t blockN;
  unsigned long detachAt;  // 0 = 없음
};
Door doors[3] = {
  {"IN",  9,  1, 2, DOOR_OPEN_DEG, DOOR_CLOSED_DEG, Servo(), D_UNKNOWN, D_UNKNOWN, DOOR_OPEN_DEG, 0, false, 0, 0, 0, 0, 0},
  {"CAP", 10, 3, 4, DOOR_OPEN_DEG, DOOR_CLOSED_DEG, Servo(), D_UNKNOWN, D_UNKNOWN, DOOR_OPEN_DEG, 0, false, 0, 0, 0, 0, 0},
  {"REL", 11, 6, 7, DOOR_OPEN_DEG, DOOR_CLOSED_DEG, Servo(), D_UNKNOWN, D_UNKNOWN, DOOR_OPEN_DEG, 0, false, 0, 0, 0, 0, 0},
};
unsigned long lastAttachMs = 0;
bool everAttached = false;

// ---------------- 레일 ----------------
bool railStable = true, railRaw = true;
unsigned long railT = 0;

// ---------------- 기타 ----------------
char line[64];
uint8_t lineLen = 0;
unsigned long watchdogMs = 0, lastCmdMs = 0;

bool readClear(const Gate& g) {
  if (g.analog) return analogRead(g.pin) > g.thr;
  return digitalRead(g.pin) == HIGH;
}

void reply(const char* s) { Serial.println(s); }
void doorMsg(const char* head, const Door& d, const char* tail) {
  Serial.print(head); Serial.print(d.name); Serial.println(tail);
}

Door* findDoor(const char* t) {
  if (!t) return nullptr;
  for (int i = 0; i < 3; i++) if (!strcmp(doors[i].name, t)) return &doors[i];
  return nullptr;
}
bool doorBusy(const Door& d) { return d.state == D_OPENING || d.state == D_WAIT || d.state == D_CLOSING || d.state == D_REOPEN; }
Door* busyDoor() { for (int i = 0; i < 3; i++) if (doorBusy(doors[i])) return &doors[i]; return nullptr; }
bool beamsOk(const Door& d) { return gates[d.beamA].ok && gates[d.beamB].ok; }

// 한 번에 하나만 붙임 + 붙이는 사이 0.3 s. 붙였으면 true, 아직 기다려야 하면 false
bool servoAttach(Door& d) {
  if (d.s.attached()) { d.detachAt = 0; return true; }
  unsigned long now = millis();
  if (everAttached && now - lastAttachMs < SERVO_GAP_MS) return false;
  for (int i = 0; i < 3; i++) if (&doors[i] != &d && doors[i].s.attached()) { doors[i].s.detach(); doors[i].detachAt = 0; }
  d.s.write(d.cur);            // 붙일 때 첫 펄스 각도
  d.s.attach(d.pin);
  lastAttachMs = now; everAttached = true;
  d.detachAt = 0;
  return true;
}
void detachLater(Door& d) { d.detachAt = millis() + DETACH_MS; if (d.detachAt == 0) d.detachAt = 1; }
void detachAll() { for (int i = 0; i < 3; i++) { if (doors[i].s.attached()) doors[i].s.detach(); doors[i].detachAt = 0; } }

void startOpen(Door& d) {
  d.state = D_OPENING; d.started = false; d.t = millis();
}
void startClose(Door& d) {
  d.prev = (d.state == D_OPEN || d.state == D_BLOCKED) ? (uint8_t)D_OPEN : d.state;
  if (d.prev == D_CLOSED || d.prev == D_WAIT || d.prev == D_CLOSING || d.prev == D_REOPEN) d.prev = D_UNKNOWN;
  d.state = D_WAIT; d.tries = 0; d.t = millis(); d.clearSince = 0; d.blockN = 0;
}

void doorPoll(Door& d) {
  unsigned long now = millis();
  if (d.detachAt && (long)(now - d.detachAt) >= 0 && !doorBusy(d)) { d.s.detach(); d.detachAt = 0; }

  switch (d.state) {
    case D_OPENING:
      if (!d.started) {
        d.cur = d.openDeg;
        if (!servoAttach(d)) return;
        d.s.write(d.openDeg);
        d.started = true; d.t = now;
        return;
      }
      if (now - d.t >= DOOR_MOVE_MS) {
        d.state = D_OPEN;
        detachLater(d);
        doorMsg("DONE DOOR ", d, " OPEN");
      }
      return;

    case D_WAIT: {
      bool clr = gates[d.beamA].raw && gates[d.beamB].raw;
      if (clr) {
        if (!d.clearSince) d.clearSince = now ? now : 1;
        if (now - d.clearSince >= CLEAR_BEFORE_MS) {
          d.cur = d.openDeg;               // 열린 쪽(안전한 쪽)에서 시작
          if (!servoAttach(d)) return;
          d.s.write(d.cur);
          d.state = D_CLOSING; d.tStep = now; d.blockN = 0;
          return;
        }
      } else d.clearSince = 0;
      if (now - d.t > WAIT_TIMEOUT_MS) {
        d.state = d.prev;
        if (d.s.attached()) detachLater(d);
        doorMsg("ERR DOOR ", d, " WAIT");
      }
      return;
    }

    case D_CLOSING: {
      bool clr = gates[d.beamA].raw && gates[d.beamB].raw;
      if (!clr) { if (d.blockN < 255) d.blockN++; } else d.blockN = 0;
      if (d.blockN >= BLOCK_SAMPLES) {     // 닫는 중 끊김 → 바로 엶
        d.cur = d.openDeg; d.s.write(d.cur);
        d.tries++;
        Serial.print(F("EVT DOOR ")); Serial.print(d.name); Serial.print(F(" REOPEN ")); Serial.println(d.tries);
        if (d.tries >= RETRY_MAX) {
          d.state = D_BLOCKED;
          detachLater(d);
          doorMsg("EVT DOOR ", d, " BLOCKED");
        } else {
          d.state = D_REOPEN; d.t = now;
        }
        return;
      }
      if (now - d.tStep < CLOSE_STEP_MS) return;
      d.tStep = now;
      int dir = (d.closeDeg > d.cur) ? 1 : -1;
      int nxt = d.cur + dir * CLOSE_STEP_DEG;
      if ((dir > 0 && nxt >= d.closeDeg) || (dir < 0 && nxt <= d.closeDeg)) nxt = d.closeDeg;
      d.cur = nxt; d.s.write(d.cur);
      if (d.cur == d.closeDeg) {
        d.state = D_CLOSED;
        detachLater(d);
        doorMsg("DONE DOOR ", d, " CLOSED");
      }
      return;
    }

    case D_REOPEN:
      if (now - d.t >= DOOR_MOVE_MS + REOPEN_WAIT_MS) {
        d.state = D_WAIT; d.prev = D_OPEN; d.t = now; d.clearSince = 0;
      }
      return;

    default:
      return;
  }
}

// ---------------- 자가 시험 ----------------
void selftest(bool asEvent) {
  int offV[9], onV[9];
  digitalWrite(PIN_EMIT, LOW); delay(SETTLE_MS);
  for (int i = 0; i < 9; i++) offV[i] = gates[i].analog ? analogRead(gates[i].pin) : digitalRead(gates[i].pin);
  digitalWrite(PIN_EMIT, HIGH); delay(SETTLE_MS);
  for (int i = 0; i < 9; i++) onV[i] = gates[i].analog ? analogRead(gates[i].pin) : digitalRead(gates[i].pin);
  if (!emitOn) digitalWrite(PIN_EMIT, LOW);

  Serial.print(asEvent ? F("EVT SELFTEST") : F("OK SELFTEST"));
  for (int i = 0; i < 9; i++) {
    Gate& g = gates[i];
    if (g.analog) {
      g.diff = onV[i] - offV[i];
      g.ok = g.diff >= BEAM_MIN_DIFF;
      if (g.ok) g.thr = (onV[i] + offV[i]) / 2;
    } else {
      g.failWhy = (offV[i] != LOW) ? 'H' : ((onV[i] != HIGH) ? 'L' : 0);
      g.ok = (g.failWhy == 0);
    }
    Serial.print(' '); Serial.print(g.name); Serial.print('=');
    if (g.ok) Serial.print(F("OK"));
    else {
      Serial.print(F("FAIL("));
      if (g.analog) Serial.print(g.diff); else Serial.print(g.failWhy);
      Serial.print(')');
    }
  }
  Serial.println();
  // 사건 기준을 지금 값으로 다시 잡음 (송신 끈 동안의 끊김을 사건으로 보내지 않음)
  unsigned long now = millis();
  for (int i = 0; i < 9; i++) { gates[i].raw = gates[i].stable = readClear(gates[i]); gates[i].tChange = now; }
  selftestDone = true;
}

void gatesPoll() {
  unsigned long now = millis();
  for (int i = 0; i < 9; i++) {
    Gate& g = gates[i];
    bool r = readClear(g);
    if (r != g.raw) { g.raw = r; g.tChange = now; }
    if (!emitOn || !g.ok) continue;       // 송신 꺼짐·고장 빔은 사건 안 보냄
    if (g.raw != g.stable && now - g.tChange >= GATE_DEBOUNCE_MS) {
      g.stable = g.raw;
      Serial.print(F("EVT GATE ")); Serial.print(g.name); Serial.println(g.stable ? F(" CLEAR") : F(" BLOCK"));
    }
  }
}

void pumpStop(bool evt) {
  bool was = pumpOffAt != 0;
  digitalWrite(PIN_PUMP, LOW); pumpOffAt = 0;
  if (was && evt) reply("EVT PUMP STOP");
}

void pumpPoll() {
  if (pumpOffAt && (long)(millis() - pumpOffAt) >= 0) {
    digitalWrite(PIN_PUMP, LOW); pumpOffAt = 0;
    Serial.print(F("DONE PUMP ")); Serial.println(pumpMs);
  }
}

void railPoll() {
  unsigned long now = millis();
  bool r = digitalRead(PIN_RAIL) == HIGH;
  if (r != railRaw) { railRaw = r; railT = now; }
  if (railRaw != railStable && now - railT >= RAIL_DEBOUNCE_MS) {
    railStable = railRaw;
    if (!railStable) {                     // 구동 전원 끊김: 움직이던 문은 자리를 모름
      for (int i = 0; i < 3; i++) if (doorBusy(doors[i])) doors[i].state = D_UNKNOWN;
      detachAll();
      pumpStop(true);
    }
    reply(railStable ? "EVT RAIL 1" : "EVT RAIL 0");
  }
}

void printGateBits(bool withNames) {
  for (int i = 0; i < 9; i++) {
    if (withNames) { Serial.print(' '); Serial.print(gates[i].name); Serial.print('='); }
    Serial.print(!gates[i].ok ? '?' : (gates[i].stable ? '1' : '0'));
  }
}

// ---------------- 명령 ----------------
void handle(char* cmd) {
  char* tok[5] = {0};
  int n = 0;
  for (char* p = strtok(cmd, " "); p && n < 5; p = strtok(nullptr, " ")) tok[n++] = p;
  if (n == 0) return;
  lastCmdMs = millis();

  if (!strcmp(tok[0], "PING")) { reply("OK PONG"); return; }

  if (!strcmp(tok[0], "STATUS")) {
    Serial.print(F("OK STATUS"));
    for (int i = 0; i < 3; i++) { Serial.print(' '); Serial.print(doors[i].name); Serial.print('='); Serial.print(DOOR_STATE_NAME[doors[i].state]); }
    Serial.print(F(" RAIL=")); Serial.print(railStable ? '1' : '0');
    Serial.print(F(" EMIT=")); Serial.print(emitOn ? '1' : '0');
    Serial.print(F(" PUMP=")); Serial.print(pumpOffAt ? '1' : '0');
    Serial.print(F(" GATES=")); printGateBits(false);
    Serial.println();
    return;
  }

  if (!strcmp(tok[0], "SELFTEST")) {
    if (busyDoor()) { reply("ERR BUSY"); return; }
    selftest(false);
    return;
  }

  if (!strcmp(tok[0], "GATES")) { Serial.print(F("OK GATES")); printGateBits(true); Serial.println(); return; }

  if (!strcmp(tok[0], "RAIL")) { reply(railStable ? "OK RAIL 1" : "OK RAIL 0"); return; }

  if (!strcmp(tok[0], "DOOR") && n == 3) {
    Door* d = findDoor(tok[1]);
    if (!d) { reply("ERR DOOR"); return; }
    bool open;
    if (!strcmp(tok[2], "OPEN")) open = true;
    else if (!strcmp(tok[2], "CLOSE")) open = false;
    else { reply("ERR STATE"); return; }
    if (!railStable) { reply("ERR RAIL"); return; }
    if (pumpOffAt) { reply("ERR BUSY"); return; }
    Door* b = busyDoor();
    // 움직이는 문이 있으면 거부. 단 같은 문에 OPEN은 허용 (닫는 중 Pi가 취소하고 열기). 같은 문 CLOSE 겹치기는 거부.
    if (b && (b != d || !open)) { reply("ERR BUSY"); return; }
    if (open) {
      reply("OK DOOR");
      if (d->state == D_OPEN) { doorMsg("DONE DOOR ", *d, " OPEN"); return; }
      startOpen(*d);
      return;
    }
    if (!emitOn) { doorMsg("ERR DOOR ", *d, " EMIT_OFF"); return; }
    if (!selftestDone || !beamsOk(*d)) { doorMsg("ERR DOOR ", *d, " BEAMFAIL"); return; }
    reply("OK DOOR");
    if (d->state == D_CLOSED) { doorMsg("DONE DOOR ", *d, " CLOSED"); return; }
    startClose(*d);
    return;
  }

  if (!strcmp(tok[0], "SERVO") && n == 3) {
    Door* d = findDoor(tok[1]);
    int deg = atoi(tok[2]);
    if (!d) { reply("ERR DOOR"); return; }
    if (deg < 0 || deg > 180) { reply("ERR DEG"); return; }
    if (!railStable) { reply("ERR RAIL"); return; }
    if (pumpOffAt) { reply("ERR BUSY"); return; }
    if (busyDoor()) { reply("ERR BUSY"); return; }
    d->cur = deg;
    if (!servoAttach(*d)) { reply("ERR BUSY"); return; }   // 0.3 s 안에 다른 서보를 붙였음 — 조금 뒤 다시
    d->s.write(deg);
    d->state = D_UNKNOWN;
    detachLater(*d);
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

  if (!strcmp(tok[0], "LIGHT") && n == 3) {
    int v = atoi(tok[2]);
    if (v < 0 || v > 255) { reply("ERR VALUE"); return; }
    if (!strcmp(tok[1], "TOP")) analogWrite(PIN_TOP, v);
    else if (!strcmp(tok[1], "BOT")) analogWrite(PIN_BOT, v);
    else { reply("ERR LIGHT"); return; }
    reply("OK LIGHT");
    return;
  }

  if (!strcmp(tok[0], "EMIT") && n == 2) {
    bool on = atoi(tok[1]) != 0;
    if (!on && busyDoor()) { reply("ERR BUSY"); return; }
    emitOn = on;
    digitalWrite(PIN_EMIT, on ? HIGH : LOW);
    if (on) {                              // 다시 켜면 사건 기준을 다시 잡음
      delay(SETTLE_MS);
      unsigned long now = millis();
      for (int i = 0; i < 9; i++) { gates[i].raw = gates[i].stable = readClear(gates[i]); gates[i].tChange = now; }
    }
    reply("OK EMIT");
    return;
  }

  if (!strcmp(tok[0], "PUMP") && n == 2) {
    long ms = atol(tok[1]);
    if (ms <= 0) { pumpStop(false); reply("OK PUMP 0"); return; }
    if (ms > (long)PUMP_MAX_MS) { reply("ERR PUMP MAX"); return; }
    if (!railStable) { reply("ERR RAIL"); return; }
    for (int i = 0; i < 3; i++) if (doorBusy(doors[i])) { reply("ERR BUSY"); return; }
    pumpMs = ms; pumpOffAt = millis() + ms; if (pumpOffAt == 0) pumpOffAt = 1;
    digitalWrite(PIN_PUMP, HIGH);
    reply("OK PUMP");
    return;
  }

  if (!strcmp(tok[0], "WATCHDOG") && n == 2) { watchdogMs = (unsigned long)(atof(tok[1]) * 1000); reply("OK WATCHDOG"); return; }

  reply("ERR UNKNOWN");
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_RAIL, INPUT);
  pinMode(PIN_TOP, OUTPUT); analogWrite(PIN_TOP, 0);
  pinMode(PIN_BOT, OUTPUT); analogWrite(PIN_BOT, 0);
  pinMode(PIN_EMIT, OUTPUT); digitalWrite(PIN_EMIT, HIGH);
  pinMode(PIN_PUMP, OUTPUT); digitalWrite(PIN_PUMP, LOW);
  for (int i = 0; i < 9; i++) if (!gates[i].analog) pinMode(gates[i].pin, INPUT);   // 풀업은 허브 10 kΩ
  // 문 서보는 붙이지 않음 (UNKNOWN) — 위 '안전 규칙'
  railRaw = railStable = digitalRead(PIN_RAIL) == HIGH;
  lastCmdMs = millis();
  reply("EVT READY trap_doors v0.2");
  delay(SETTLE_MS);
  selftest(true);
  if (!railStable) reply("EVT RAIL 0");
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
  railPoll();
  gatesPoll();
  for (int i = 0; i < 3; i++) doorPoll(doors[i]);
  pumpPoll();
  if (watchdogMs && millis() - lastCmdMs > watchdogMs) {
    for (int i = 0; i < 3; i++) {
      Door& d = doors[i];
      if (d.state == D_WAIT || d.state == D_CLOSING || d.state == D_REOPEN) startOpen(d);
    }
    pumpStop(true);
    reply("EVT WATCHDOG_HOLD");
    lastCmdMs = millis();
  }
}
