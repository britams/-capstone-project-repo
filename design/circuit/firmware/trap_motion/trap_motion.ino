// trap_motion.ino — UNO 1 (움직임): 바닥 F·마커 X·Y 스테핑, 펜 서보, 누름 스위치, 원점 스위치 3 — v0.2
// (11/10 밤, CAP-AI-60) 교수님 피드백 '로드셀은 과함' → HX711·로드셀 없앰. 스프링 146(k 103.6 N/m)이 4.8 mm 눌리면(0.5 N)
//   축 147의 걸쇠가 누름 스위치(KW11, NC 접점)를 누름 → 멈춤. 힘은 스위치 자리로 정함 (저울로 한 번 맞춤)
// 작성: 서현 (Claude, CAP-AI-40, 2026-11-08). 바탕: control/firmware/trap_controller/trap_controller.ino v0.1 (승준 SJ-19)
// 사양: design/2026-11-06_펌웨어_변경요청_서현.md 1장, 핀 원본: design/circuit/circuit.py (검사 통과)
// ※ 승준 control/ 은 고치지 않음. 승준이 동의하면 control/firmware/ 로 옮긴다.
//
// 핀 (UNO 1, 18/18)
//   F 바닥 승강 153 : D2  D3  D4  D5   (DRV8833 AIN1 AIN2 BIN1 BIN2 — 11/12 산 리니어 모듈 15BY25, 양극 2상)
//   X 마커 X   215 : D6  D7  D8  D9
//   Y 마커 Y   209 : D10 D11 D12 D13
//   PEN 펜 서보 205 : A0  (SG90, 전원 +5V_B)
//   누름 스위치 PSW : A1 (INPUT_PULLUP, NC 접점 → GND: 평소 LOW, 눌림·선 끊김 = HIGH → 멈춤 쪽으로 안전)   A2 예비
//   원점 F / X / Y : A3 / A4 / A5  (INPUT_PULLUP, 눌리면 LOW, 100 nF)
//
// 시리얼 115200, 한 줄 = 명령 하나 (대문자로 바꿔 읽음)
//   응답: OK ... (접수) / ERR <이유> / DONE ... (끝) / EVT ... (사건)
//   PING                         → OK PONG
//   STATUS                       → OK STATUS F=<mm> X=<mm> Y=<mm> MOVING=<FXY|-> HOMED=<FXY|-> PSW=<1|0> PEN=<UP|DOWN|MOVING|LIMP> SW=<FXY 눌림 1/0>
//   HOME <F|X|Y>                 → OK HOME <축>, 끝나면 DONE HOME <축> <찾을 때까지 반걸음> | ERR HOME <축> NOSWITCH | ERR HOME <축> STUCK
//   MOVE <F|X|Y> <mm>            → OK MOVE <축> <mm>, 끝나면 DONE MOVE <축> <mm>   (HOME/ZERO 전에는 ERR NOT_HOMED, 펜 DOWN이면 X·Y와 F 올리기는 ERR PEN_DOWN)
//   STOP                         → OK STOP (HOME 중이면 HOME도 멈춤 → ERR HOME <축> STOPPED)
//   ZERO <F|X|Y> <mm>            현재 위치를 <mm>로 (스위치 고장일 때 손으로) → OK ZERO, 그 축은 HOMED
//   SPEED <F|X|Y> <us>           반걸음 간격 (기본 1000, 최소 800, 1080~1460은 스프링 서지 띠라 거부)
//   LIMIT <F|X|Y> <min> <max>    소프트 한계 mm
//   HOLD <F|X|Y> <0|1>           멈춘 뒤 코일 전류 (기본 모두 0 — F도 0, 변경요청 1장)
//   PRESS <g> [<mm>]             → OK PRESS, DONE PRESS <mm> <g> | DONE PRESS LIMIT <mm> 0
//                                  (g는 기록용 — 힘은 스위치 자리가 정함). 누르기 전부터 스위치가 HIGH면 ERR PRESS_SW (눌림·선 끊김)
//   PEN <UP|DOWN>                → OK PEN, 끝나면 DONE PEN UP|DOWN. DOWN은 2단계(마지막 구간 ≤ 60 °/s). X·Y가 움직이면 ERR XY_MOVING
//   SERVO PEN <deg>              각도 직접 (보정용) → OK SERVO
//   SETDOOR PEN <위> <아래>       펜 각도 보정 (전원 끄면 사라짐) → OK SETDOOR
//   WATCHDOG <s>                 s초 명령 없으면 정지·펜 들기 (0 = 끔)
//
// 안전 규칙 (AI 판단, 서현 위임 — CAP-AI-40)
//   - X·Y는 펜이 UP일 때만 움직인다 (MOVE·HOME 모두). 펜이 캡 컵에 꽂힌 채 끌리지 않게. → ERR PEN_DOWN
//   - 켤 때 펜 서보를 붙이지 않는다 (LIMP). Pi가 PEN UP을 먼저 보낸다. 서보 1개뿐이라 켤 때 전류 문제 없음.
//   - R1 (검토 CAP-AI-42) → R1′ (CAP-AI-48): 펜이 DOWN이고 마킹실 위(Y > -20.5)면 F를 올리는 MOVE 거부 (ERR PEN_DOWN).
//     펜이 대기 자리 캡 컵에 꽂혀 있으면 F 올리기 허용 (재방문 말벌 급이 높이로). PRESS는 언제나 펜 UP일 때만. F 내리기·HOME F는 언제나.
//   - 스위치 쪽으로 MOVE 하다가 원점보다 0.5 mm 넘게 위에서 스위치가 눌리면 걸음을 잃은 것 → 그 축 정지, HOMED 지움, EVT SWITCH <축> <mm>
//   - 마지막 반걸음 뒤 코일은 COIL_OFF_DWELL_MS(20 ms) 뒤에 끈다 (CAP-AI-44, 시뮬레이터가 찾음): 이전 코드는 도착한 loop에서 걸음 코일을 켜자마자 꺼서
//     모터가 마지막 반걸음(약 2 µm)을 돌 시간이 없고, 이동마다 쌓여 위치가 틀어질 수 있음. v0.1(승준)에도 같은 구조. 실물 효과는 미검증.
//   - 원점 위치는 LIMIT와 따로 상수(HOME_*_MM)로 둔다 (LIMIT를 바꿔도 스위치 자리는 그대로)

#include <Servo.h>

// ---------------- 값 (미검증은 실물에서 맞춤) ----------------
#define STEPS_PER_MM      (4075.7728f / 8.0f)  // X·Y: 28BYJ-48 반걸음 4075.77/회전 [가능성 높음] ÷ T8 리드 8 mm
#define STEPS_PER_MM_F    (40.0f / 0.5f)       // F (11/12): 15BY25 18°/걸음 → 반걸음 40/회전 ÷ M3 리드 0.5 mm [확실 — Keshuo 치수도]
#define HALF_US_DEFAULT   1000UL   // 반걸음 간격 µs (≈ 1.96 mm/s) — v0.1 값
#define HALF_US_MIN       800UL
#define SURGE_LO_US       1080UL   // 686~928 Hz 스프링 서지 띠 (역학계산 2차, b4_axis 주석) — 이 사이 SPEED 거부
#define SURGE_HI_US       1460UL
#define HOME_SLOW_US      2000UL   // 원점 다시 닿을 때 반걸음 간격 — 미검증 (서지 띠 밖으로 고름)
#define HOME_BACKOFF_MM   1.0f     // 사양: 1 mm 물러났다 다시
#define HOME_MARGIN_MM    4.0f     // 찾는 최대 거리 = 행정 + 이 값 — (AI 판단) 아래 HOME_MAX 주석
#define HOME_F_MM         0.0f     // 스위치 자리 = 소프트 한계 아래 끝 (사양)
#define HOME_X_MM         (-18.0f)
#define HOME_Y_MM         (-40.0f)
#define SWITCH_SAMPLES    3        // 걸음마다 읽어 3번 연속 LOW면 눌림 (튐 막기) — 미검증
#define SWITCH_GUARD_MM   0.5f     // 원점보다 이만큼 넘게 위에서 눌리면 걸음 잃음
#define PEN_CHAMBER_Y_MM  (-20.5f)  // Y가 이보다 크면 펜이 마킹실 위 (trap_sim: Y > -20.5) — [가능성 높음] D5e 모델 값, R1′
#define COIL_OFF_DWELL_MS 20       // 마지막 반걸음 뒤 코일을 이만큼 더 켜 둔 다음 끔 (HOLD 0일 때) — 미검증, 아래 안전 규칙
#define PEN_UP_DEG        60       // v0.1 값 — 미검증 (SETDOOR PEN으로 맞춤)
#define PEN_DOWN_DEG      0        // v0.1 값 — 미검증
#define PEN_SLOW_DEG      12       // 여기부터 천천히 (팁 위 약 2 mm ≈ 60° × 2/10 mm) — [추측] 미검증
#define PEN_SLOW_MS_DEG   17       // 1°당 17 ms ≈ 59 °/s (인터페이스 정의서 구동기 4: 마지막 2 mm ≤ 60 °/s)
#define PEN_FAST_MS       150      // SG90 0.1 s/60° + 여유 (trap_sim pen_up_s)

// 28BYJ-48 반걸음 순서
const uint8_t HALF[8][4] = {{1,0,0,0},{1,1,0,0},{0,1,0,0},{0,1,1,0},{0,0,1,0},{0,0,1,1},{0,0,0,1},{1,0,0,1}};
// F (11/12): 양극 반걸음 — DRV8833 AIN1 AIN2 (코일 A) · BIN1 BIN2 (코일 B), 0 0 = 그 코일 끔
const uint8_t HALF_BI[8][4] = {{1,0,0,0},{1,0,1,0},{0,0,1,0},{0,1,1,0},{0,1,0,0},{0,1,0,1},{0,0,0,1},{1,0,0,1}};

enum HomePhase { H_NONE = 0, H_SEEK, H_BACK, H_SLOW };

struct Axis {
  char name;
  uint8_t pins[4];
  uint8_t sw;          // 원점 스위치 핀
  float homeMm;        // 스위치 자리
  long pos, target;    // 반걸음
  uint8_t phase;       // 0..7
  unsigned long intervalUs, lastUs;
  float minMm, maxMm;
  bool hold, moving, homed;
  uint8_t home;        // HomePhase
  long homeCount, homeLeg;
  uint8_t swLow;       // 연속 LOW 수
  bool offPending;     // HOLD 0: 마지막 걸음 뒤 코일 끄기 대기
  unsigned long offAt; // 그 시각 (ms)
};

Axis axes[3] = {
  {'F', {2, 3, 4, 5},     A3, HOME_F_MM, 0, 0, 0, HALF_US_DEFAULT, 0, 0.0f,   36.5f, false, false, false, H_NONE, 0, 0, 0, false, 0},
  {'X', {6, 7, 8, 9},     A4, HOME_X_MM, 0, 0, 0, HALF_US_DEFAULT, 0, -18.0f, 18.0f, false, false, false, H_NONE, 0, 0, 0, false, 0},
  {'Y', {10, 11, 12, 13}, A5, HOME_Y_MM, 0, 0, 0, HALF_US_DEFAULT, 0, -40.0f, 18.0f, false, false, false, H_NONE, 0, 0, 0, false, 0},
};

bool pressActive = false;
float pressGrams = 0;

// ---------------- 펜 ----------------
enum PenState { PEN_LIMP = 0, PEN_IS_UP, PEN_IS_DOWN, PEN_MOVING };
Servo pen;
const uint8_t PEN_PIN = A0;
int penUpDeg = PEN_UP_DEG, penDownDeg = PEN_DOWN_DEG;
uint8_t penState = PEN_LIMP;
bool penTargetUp = true;
int penCur = PEN_UP_DEG;          // 지금 쓴 각도
unsigned long penT = 0;           // 다음 일 시각 (ms)
uint8_t penStage = 0;             // 0 없음, 1 빠르게 가는 중, 2 천천히 내리는 중

// ---------------- 누름 스위치 (스프링 + KW11, CAP-AI-60) ----------------
const uint8_t PSW_PIN = A1;
#define PSW_SAMPLES 2           // 연속 2걸음 HIGH면 눌림 (잡음 거름)
uint8_t pswHigh = 0;

// ---------------- 기타 ----------------
char line[64];
uint8_t lineLen = 0;
unsigned long watchdogMs = 0, lastCmdMs = 0;

Axis* findAxis(const char* t) {
  if (!t || t[0] == '\0' || t[1] != '\0') return nullptr;
  for (int i = 0; i < 3; i++) if (axes[i].name == t[0]) return &axes[i];
  return nullptr;
}

void coils(Axis& a, bool on) {
  const uint8_t (*seq)[4] = (a.name == 'F') ? HALF_BI : HALF;
  for (int k = 0; k < 4; k++) digitalWrite(a.pins[k], on ? seq[a.phase][k] : 0);
}
float spm(const Axis& a) { return a.name == 'F' ? STEPS_PER_MM_F : STEPS_PER_MM; }
float posMm(const Axis& a) { return a.pos / spm(a); }
long mmToSteps(const Axis& a, float mm) { return lround(mm * spm(a)); }
bool swPressed(const Axis& a) { return digitalRead(a.sw) == LOW; }

bool pswPressed() { return digitalRead(PSW_PIN) == HIGH; }

void reply(const char* s) { Serial.println(s); }
void replyAxis(const char* head, const Axis& a, const char* tail) {
  Serial.print(head); Serial.print(a.name); Serial.println(tail);
}
void doneMove(const Axis& a) {
  Serial.print(F("DONE MOVE ")); Serial.print(a.name); Serial.print(' '); Serial.println(posMm(a), 3);
}

void startMove(Axis& a, float mm) {
  a.offPending = false;
  a.target = mmToSteps(a, mm);
  a.moving = (a.target != a.pos);
  a.lastUs = micros();
  if (!a.moving) doneMove(a);
}

void endAxis(Axis& a) {
  a.target = a.pos;
  a.moving = false;
  a.home = H_NONE;
  a.swLow = 0;
  // 마지막 반걸음 코일을 바로 끄면 모터가 그 걸음을 돌 시간이 없다 (같은 loop 안에서 켜자마자 끔) → 잠깐 두었다 끔
  if (!a.hold) { a.offPending = true; a.offAt = millis() + COIL_OFF_DWELL_MS; }
}

void homeFail(Axis& a, const char* why) {
  endAxis(a);
  Serial.print(F("ERR HOME ")); Serial.print(a.name); Serial.print(' '); Serial.println(why);
}

void stopAll() {
  for (int i = 0; i < 3; i++) {
    if (axes[i].home != H_NONE) homeFail(axes[i], "STOPPED");
    else endAxis(axes[i]);
  }
  pressActive = false;
}

bool xyMoving() { return axes[1].moving || axes[2].moving; }

// ---------------- 펜 (막지 않는 동작) ----------------
void penAttach() { if (!pen.attached()) pen.attach(PEN_PIN); }

void penStart(bool up) {
  penAttach();
  penTargetUp = up;
  penState = PEN_MOVING;
  if (up) {
    penCur = penUpDeg; pen.write(penCur);
    penStage = 1; penT = millis() + PEN_FAST_MS;
  } else {
    // 1단계: 천천히 내리기 시작할 각도까지 빠르게 (위 → 아래 방향 부호를 보정값에서 정함)
    int dir = (penDownDeg < penUpDeg) ? -1 : 1;
    int slowAt = penDownDeg - dir * PEN_SLOW_DEG;
    penCur = slowAt; pen.write(penCur);
    penStage = 1; penT = millis() + PEN_FAST_MS;
  }
}

void penPoll() {
  if (penState != PEN_MOVING) return;
  if ((long)(millis() - penT) < 0) return;
  if (penTargetUp) {
    penState = PEN_IS_UP; penStage = 0;
    reply("DONE PEN UP");
    return;
  }
  // 2단계: 1°씩 ≤ 60 °/s
  if (penCur == penDownDeg) {
    penState = PEN_IS_DOWN; penStage = 0;
    reply("DONE PEN DOWN");
    return;
  }
  penStage = 2;
  penCur += (penDownDeg > penCur) ? 1 : -1;
  pen.write(penCur);
  penT = millis() + PEN_SLOW_MS_DEG;
}

const char* penName() {
  switch (penState) {
    case PEN_IS_UP: return "UP";
    case PEN_IS_DOWN: return "DOWN";
    case PEN_MOVING: return "MOVING";
    default: return "LIMP";
  }
}

// ---------------- 원점 ----------------
long homeMaxSteps(const Axis& a) { return mmToSteps(a, a.maxMm - a.homeMm + HOME_MARGIN_MM); }
// HOME_MAX: 사양은 '반걸음 20480번'(b4의 40 mm = F 행정 기준). Y는 행정 58 mm라 +18에서 켜지면 20480으로는
//   스위치에 못 닿아 거짓 NOSWITCH가 남 → 축마다 (행정 + 4 mm): F 20,634 · X 20,379 · Y 31,587 반걸음 (AI 판단, CAP-AI-40)

void homeStart(Axis& a) {
  a.offPending = false;
  a.homeCount = 0; a.homeLeg = 0; a.swLow = 0;
  a.moving = true;
  a.homed = false;
  a.lastUs = micros();
  if (swPressed(a)) a.home = H_BACK;      // 이미 눌려 있으면 먼저 물러남
  else a.home = H_SEEK;
}

// 한 걸음 (dir = +1/-1)
void stepOnce(Axis& a, int dir) {
  a.phase = (a.phase + dir + 8) % 8;
  a.pos += dir;
  coils(a, true);
}

void homeStep(Axis& a) {
  // 스위치 읽기 (걸음마다 한 번, 연속 SWITCH_SAMPLES번 LOW면 눌림)
  if (swPressed(a)) { if (a.swLow < 255) a.swLow++; } else a.swLow = 0;
  bool hit = a.swLow >= SWITCH_SAMPLES;
  long back = mmToSteps(a, HOME_BACKOFF_MM);

  if (a.home == H_SEEK) {
    if (hit) { a.home = H_BACK; a.homeLeg = 0; a.swLow = 0; return; }
    if (a.homeCount >= homeMaxSteps(a)) { homeFail(a, "NOSWITCH"); return; }
    stepOnce(a, -1); a.homeCount++;
  } else if (a.home == H_BACK) {
    if (a.homeLeg >= back) {
      if (swPressed(a)) { homeFail(a, "STUCK"); return; }   // 1 mm 물러나도 눌림 = 스위치가 붙었거나 신호선이 GND에 닿음
      a.home = H_SLOW; a.homeLeg = 0; a.swLow = 0;
      return;
    }
    stepOnce(a, +1); a.homeLeg++;
  } else if (a.home == H_SLOW) {
    if (hit) {
      a.pos = a.target = mmToSteps(a, a.homeMm);
      a.homed = true;
      long n = a.homeCount;
      endAxis(a);
      Serial.print(F("DONE HOME ")); Serial.print(a.name); Serial.print(' '); Serial.println(n);
      return;
    }
    if (a.homeLeg >= 3 * back) { homeFail(a, "NOSWITCH"); return; }   // 물러난 거리의 3배 안에 다시 못 닿음
    stepOnce(a, -1); a.homeLeg++;
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
    Serial.print(F("OK STATUS F=")); Serial.print(posMm(axes[0]), 3);
    Serial.print(F(" X=")); Serial.print(posMm(axes[1]), 3);
    Serial.print(F(" Y=")); Serial.print(posMm(axes[2]), 3);
    Serial.print(F(" MOVING="));
    bool any = false;
    for (int i = 0; i < 3; i++) if (axes[i].moving) { Serial.print(axes[i].name); any = true; }
    if (!any) Serial.print('-');
    Serial.print(F(" HOMED="));
    any = false;
    for (int i = 0; i < 3; i++) if (axes[i].homed) { Serial.print(axes[i].name); any = true; }
    if (!any) Serial.print('-');
    Serial.print(F(" PSW=")); Serial.print(pswPressed() ? '1' : '0');
    Serial.print(F(" PEN=")); Serial.print(penName());
    Serial.print(F(" SW="));
    for (int i = 0; i < 3; i++) Serial.print(swPressed(axes[i]) ? '1' : '0');
    Serial.println();
    return;
  }

  if (!strcmp(tok[0], "HOME") && n == 2) {
    Axis* a = findAxis(tok[1]);
    if (!a) { reply("ERR AXIS"); return; }
    if (a->moving) { reply("ERR BUSY"); return; }
    if (a->name != 'F' && penState != PEN_IS_UP) { reply("ERR PEN_DOWN"); return; }
    if (a->name == 'F') pressActive = false;
    replyAxis("OK HOME ", *a, "");
    homeStart(*a);
    return;
  }

  if (!strcmp(tok[0], "MOVE") && n == 3) {
    Axis* a = findAxis(tok[1]);
    if (!a) { reply("ERR AXIS"); return; }
    if (a->home != H_NONE) { reply("ERR BUSY"); return; }
    if (!a->homed) { reply("ERR NOT_HOMED"); return; }
    if (a->name != 'F' && penState != PEN_IS_UP) { reply("ERR PEN_DOWN"); return; }
    float mm = atof(tok[2]);
    if (mm < a->minMm || mm > a->maxMm) { reply("ERR LIMIT"); return; }
    // R1 (검토 문서 CAP-AI-42): 바닥을 '올리는' MOVE는 펜 UP일 때만. 내리기는 언제나 허용 (말벌에서 멀어짐)
    // R1′ (CAP-AI-48): 펜이 내려가 있고 마킹실 위에 있으면 막음. 대기 자리(캡 컵, Y ≤ -20.5)에 꽂혀 있으면 허용 (재방문 급이)
    if (a->name == 'F' && mmToSteps(*a, mm) > a->pos && penState != PEN_IS_UP && posMm(axes[2]) > PEN_CHAMBER_Y_MM) { reply("ERR PEN_DOWN"); return; }
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
    a->pos = a->target = mmToSteps(*a, atof(tok[2]));
    a->homed = true;
    reply("OK ZERO");
    return;
  }

  if (!strcmp(tok[0], "SPEED") && n == 3) {
    Axis* a = findAxis(tok[1]);
    long us = atol(tok[2]);
    if (!a) { reply("ERR AXIS"); return; }
    if (us < (long)HALF_US_MIN) { reply("ERR SPEED_MIN_800"); return; }
    if (us >= (long)SURGE_LO_US && us <= (long)SURGE_HI_US) { reply("ERR SPEED_SURGE_BAND"); return; }
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
    if (!a->moving) { coils(*a, a->hold); a->offPending = false; }
    reply("OK HOLD");
    return;
  }

  if (!strcmp(tok[0], "PRESS") && (n == 2 || n == 3)) {
    Axis& f = axes[0];
    if (f.home != H_NONE || f.moving) { reply("ERR BUSY"); return; }
    if (!f.homed) { reply("ERR NOT_HOMED"); return; }
    if (penState != PEN_IS_UP) { reply("ERR PEN_DOWN"); return; }   // R1: 펜이 내려간 채 바닥을 올리면 말벌이 눌림
    float maxMm = (n == 3) ? atof(tok[2]) : f.maxMm;
    if (maxMm > f.maxMm) maxMm = f.maxMm;
    pressGrams = atof(tok[1]);
    if (pressGrams <= 0) { reply("ERR GRAMS"); return; }
    if (pswPressed()) { reply("ERR PRESS_SW"); return; }          // 누르기 전부터 HIGH = 눌린 채 걸림 또는 선 끊김 → 안 올림
    pswHigh = 0;
    pressActive = true;
    reply("OK PRESS");
    startMove(f, maxMm);
    if (!f.moving) pressActive = false;
    return;
  }

  if (!strcmp(tok[0], "PEN") && n == 2) {
    bool up;
    if (!strcmp(tok[1], "UP")) up = true;
    else if (!strcmp(tok[1], "DOWN")) up = false;
    else { reply("ERR STATE"); return; }
    if (!up && xyMoving()) { reply("ERR XY_MOVING"); return; }
    reply("OK PEN");
    penStart(up);
    return;
  }

  if (!strcmp(tok[0], "SERVO") && n == 3) {
    if (strcmp(tok[1], "PEN")) { reply("ERR DOOR"); return; }   // 문 서보는 UNO 2 (trap_doors)
    int deg = atoi(tok[2]);
    if (deg < 0 || deg > 180) { reply("ERR DEG"); return; }
    if (xyMoving()) { reply("ERR XY_MOVING"); return; }
    penAttach();
    pen.write(deg); penCur = deg;
    penState = (deg == penUpDeg) ? PEN_IS_UP : PEN_IS_DOWN;   // 위 각도가 아니면 X·Y 막음
    reply("OK SERVO");
    return;
  }

  if (!strcmp(tok[0], "SETDOOR") && n == 4) {
    if (strcmp(tok[1], "PEN")) { reply("ERR DOOR"); return; }
    penUpDeg = constrain(atoi(tok[2]), 0, 180);
    penDownDeg = constrain(atoi(tok[3]), 0, 180);
    reply("OK SETDOOR");
    return;
  }


  if (!strcmp(tok[0], "WATCHDOG") && n == 2) { watchdogMs = (unsigned long)(atof(tok[1]) * 1000); reply("OK WATCHDOG"); return; }

  reply("ERR UNKNOWN");
}

void stepAxes() {
  unsigned long now = micros();
  for (int i = 0; i < 3; i++) {
    Axis& a = axes[i];
    if (a.offPending && !a.moving && (long)(millis() - a.offAt) >= 0) { coils(a, false); a.offPending = false; }
    if (!a.moving) continue;
    unsigned long iv = (a.home == H_SLOW) ? HOME_SLOW_US : a.intervalUs;
    if (now - a.lastUs < iv) continue;
    a.lastUs = now;

    if (a.home != H_NONE) { homeStep(a); continue; }

    int dir = (a.target > a.pos) ? 1 : -1;
    // 스위치 쪽(-)으로 가는데 원점보다 한참 위에서 눌림 → 걸음 잃음
    if (dir < 0) {
      if (swPressed(a)) { if (a.swLow < 255) a.swLow++; } else a.swLow = 0;
      if (a.swLow >= SWITCH_SAMPLES && posMm(a) > a.homeMm + SWITCH_GUARD_MM) {
        float at = posMm(a);
        a.homed = false;
        bool wasPress = (i == 0 && pressActive);
        endAxis(a);
        if (wasPress) pressActive = false;
        Serial.print(F("EVT SWITCH ")); Serial.print(a.name); Serial.print(' '); Serial.println(at, 3);
        continue;
      }
    } else a.swLow = 0;

    stepOnce(a, dir);
    if (i == 0 && pressActive && dir > 0) {
      if (pswPressed()) { if (pswHigh < 255) pswHigh++; } else pswHigh = 0;
      if (pswHigh >= PSW_SAMPLES) {
        endAxis(a);
        pressActive = false;
        Serial.print(F("DONE PRESS ")); Serial.print(posMm(a), 3); Serial.print(' '); Serial.println(pressGrams, 1);
        continue;
      }
    }
    if (a.pos == a.target) {
      endAxis(a);
      if (i == 0 && pressActive) {
        pressActive = false;
        Serial.print(F("DONE PRESS LIMIT ")); Serial.print(posMm(a), 3); Serial.println(F(" 0"));
      } else {
        doneMove(a);
      }
    }
  }
}

void setup() {
  Serial.begin(115200);
  for (int i = 0; i < 3; i++) {
    for (int k = 0; k < 4; k++) pinMode(axes[i].pins[k], OUTPUT);
    coils(axes[i], false);                 // HOLD 기본 0 — 켤 때 코일 끔
    pinMode(axes[i].sw, INPUT_PULLUP);
  }
  pinMode(PSW_PIN, INPUT_PULLUP);
  // 펜 서보는 붙이지 않음 (LIMP) — Pi가 PEN UP을 먼저 보냄
  lastCmdMs = millis();
  reply("EVT READY trap_motion v0.2");
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
  stepAxes();
  penPoll();
  if (watchdogMs && millis() - lastCmdMs > watchdogMs) {
    stopAll();
    if (penState != PEN_LIMP && !(penState == PEN_IS_UP)) penStart(true);
    reply("EVT WATCHDOG_STOP");
    lastCmdMs = millis();
  }
}

