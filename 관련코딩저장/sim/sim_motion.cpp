// sim_motion.cpp — trap_motion.ino (UNO 1) PC 시험 (서현 CAP-AI-44)
// 빌드:  zig c++ -std=c++17 -Wall -I. sim_motion.cpp -o sim_motion.exe   (run_all.ps1 이 해 줌)
// 세계 = 스테핑 3축(코일 패턴을 읽어 기계 위치를 셈) + 원점 스위치 3 + HX711 + 펜 서보 기록.
#include "Arduino.h"
#include "Servo.h"
SIM_DEFINE_GLOBALS
SIM_DEFINE_SERVO
#include "../../design/circuit/firmware/trap_motion/trap_motion.ino"
#include "sim_common.h"
#include <algorithm>

// ---- 세계: 축 ----
struct AxisW {
  int pin0;            // 코일 핀 시작 (4개 연속)
  int swPin;           // 원점 스위치 핀
  long mech = 0;       // 기계 위치 (반걸음). 스위치가 눌리는 자리 = swPos
  long swPos = 0;
  bool swConnected = true;
  int lastIdx = 0;     // 스케치 phase 시작값 0
  long minMech = 0, maxMech = 0;
  long lost = 0;       // 순서 어긋난 걸음
  long steps = 0;      // 움직인 걸음 총수
};
static AxisW W[3] = {{2, A3}, {6, A4}, {10, A5}};
static const int HALF_T[8][4] = {{1,0,0,0},{1,1,0,0},{0,1,0,0},{0,1,1,0},{0,0,1,0},{0,0,1,1},{0,0,0,1},{1,0,0,1}};
static long w_hx_raw_base = 0;
static int hx_pulse = 0;          // HX711 클럭 수
static int last_sck = 0;
static long hx_latched = 0;
static std::function<void()> w_script;

static long hx_raw_now() {        // 바닥(F)이 스위치 위 10 mm 를 넘으면 1 mm당 1000
  double mm = (W[0].mech - W[0].swPos) / STEPS_PER_MM;
  return w_hx_raw_base + (mm > 10 ? (long)((mm - 10) * 1000) : 0);
}

static void sample_axes() {
  for (int a = 0; a < 3; a++) {
    AxisW& w = W[a];
    int v[4]; bool all0 = true;
    for (int k = 0; k < 4; k++) { v[k] = g_pins[w.pin0 + k]; if (v[k]) all0 = false; }
    if (all0) continue;                                    // 코일 꺼짐 (위치 유지)
    int idx = -1;
    for (int i = 0; i < 8; i++) if (v[0]==HALF_T[i][0] && v[1]==HALF_T[i][1] && v[2]==HALF_T[i][2] && v[3]==HALF_T[i][3]) { idx = i; break; }
    if (idx < 0 || idx == w.lastIdx) continue;
    int d = (idx - w.lastIdx + 8) % 8;
    if (d == 1) w.mech++; else if (d == 7) w.mech--; else w.lost++;
    w.steps++;
    w.lastIdx = idx;
    w.minMech = std::min(w.minMech, w.mech); w.maxMech = std::max(w.maxMech, w.mech);
  }
}

static void world_setup() {
  g_world = []() { sample_axes(); if (w_script) w_script(); };
  g_dwrite_hook = [](int p, int v) {                       // HX711 SCK(A2) 오름 가장자리마다 비트 하나
    if (p == A2) { if (v && !last_sck) { hx_pulse++; if (hx_pulse == 1) hx_latched = hx_raw_now() & 0xFFFFFF; if (hx_pulse >= 25) hx_pulse = 0; } last_sck = v; }
  };
  g_dread = [](int p) -> int {
    for (int a = 0; a < 3; a++) if (p == W[a].swPin) return (W[a].swConnected && W[a].mech <= W[a].swPos) ? 0 : 1;   // 눌리면 LOW (풀업)
    if (p == A1) {                                         // HX711 DT
      if (hx_pulse == 0) return 0;                         // 준비됨 (LOW)
      if (hx_pulse > 24) return 0;
      return (hx_latched >> (24 - hx_pulse)) & 1;
    }
    return g_pins[p];
  };
}

static void axes_reset() {
  for (int a = 0; a < 3; a++) { W[a].mech = 0; W[a].swPos = 0; W[a].swConnected = true; W[a].lastIdx = 0; W[a].minMech = W[a].maxMech = 0; W[a].lost = 0; W[a].steps = 0; }
}
static double mm_of(int a) { return (W[a].mech - W[a].swPos) / STEPS_PER_MM; }   // 스위치 자리 기준 mm
static int last_write(int pin) { return g_servo_angle[pin]; }
// 마지막 걸음 뒤 대기 시간(COIL_OFF_DWELL_MS)이 지난 다음 코일을 본다
static bool coils_off() {
  t_run(COIL_OFF_DWELL_MS + 20);
  for (int p = 2; p <= 13; p++) if (g_pins[p]) return false;
  return true;
}
static bool wait_home(const char* ax, unsigned long max_ms, size_t m) {
  char ok[32], bad[32]; snprintf(ok, sizeof ok, "DONE HOME %s", ax); snprintf(bad, sizeof bad, "ERR HOME %s", ax);
  for (unsigned long t = 0; t < max_ms; t += 10) { if (t_has(m, ok) || t_has(m, bad)) return true; t_run(10); }
  return false;
}
static void pen_up() { size_t m = t_cmd("PEN UP", 10); t_wait(m, "DONE PEN UP", 1000); }
static void pen_down() { size_t m = t_cmd("PEN DOWN", 10); t_wait(m, "DONE PEN DOWN", 3000); }

// 서버 모드:  sim_motion.exe --serve [--speed N] [--f-mm 2] [--x-mm 2] [--y-mm 2] [--no-switch X]
//   시작할 때 각 축이 스위치 위 몇 mm 에 있는지. 제어 줄: #SWITCH <축> 0|1 (스위치 연결), #SHIFT <축> <mm> (기계가 어긋남)
static int serve(int argc, char** argv) {
  double speed = 1.0, start[3] = {2.0, 2.0, 2.0};
  for (int i = 2; i < argc; i++) {
    if (!strcmp(argv[i], "--speed") && i + 1 < argc) speed = atof(argv[++i]);
    else if (!strcmp(argv[i], "--f-mm") && i + 1 < argc) start[0] = atof(argv[++i]);
    else if (!strcmp(argv[i], "--x-mm") && i + 1 < argc) start[1] = atof(argv[++i]);
    else if (!strcmp(argv[i], "--y-mm") && i + 1 < argc) start[2] = atof(argv[++i]);
    else if (!strcmp(argv[i], "--no-switch") && i + 1 < argc) { int a = argv[++i][0] - 'F'; a = (a == 0) ? 0 : (a == 'X' - 'F' ? 1 : 2); W[a].swConnected = false; }
  }
  world_setup(); axes_reset();
  for (int a = 0; a < 3; a++) W[a].mech = W[a].swPos + (long)(start[a] * STEPS_PER_MM);
  return t_serve(speed, [](const std::string& l) {
    char ax; int v; double mm;
    if (sscanf(l.c_str(), "#SWITCH %c %d", &ax, &v) == 2) { int a = ax == 'F' ? 0 : ax == 'X' ? 1 : 2; W[a].swConnected = v != 0; }
    else if (sscanf(l.c_str(), "#SHIFT %c %lf", &ax, &mm) == 2) { int a = ax == 'F' ? 0 : ax == 'X' ? 1 : 2; W[a].swPos += (long)(mm * STEPS_PER_MM); }
  });
}

int main(int argc, char** argv) {
  if (argc > 1 && !strcmp(argv[1], "--serve")) return serve(argc, argv);
  world_setup();
  axes_reset();

  printf("[0] 켜기: READY 이름, 코일 꺼짐(HOLD F 0), 펜 서보 안 붙임, 스위치 풀업\n");
  setup();
  CHECK(t_has(0, "EVT READY trap_motion v0.2"), "READY 이름 trap_motion");
  CHECK(coils_off(), "켠 직후 코일 전부 꺼짐 (F도)");
  CHECK(g_servo_events.empty(), "켤 때 펜 서보를 붙이지 않음 (LIMP)");
  CHECK(g_pinmode[A3] == INPUT_PULLUP && g_pinmode[A4] == INPUT_PULLUP && g_pinmode[A5] == INPUT_PULLUP, "원점 스위치 A3·A4·A5 INPUT_PULLUP");
  size_t m = t_cmd("STATUS"); CHECK(t_has(m, "HOMED=- ") && t_has(m, "PEN=LIMP"), "STATUS: 아무 축도 HOMED 아님, PEN=LIMP");
  m = t_cmd("MOVE F 5"); CHECK(t_has(m, "ERR NOT_HOMED"), "HOME 전 MOVE → ERR NOT_HOMED");

  printf("[1] HOME F: 스위치 7.8 mm 위에서 켜짐 → 찾고, 물러났다 천천히 다시 닿고, 0 으로 정함\n");
  W[0].mech = 4000;                                  // 스위치 위 약 7.85 mm
  m = t_cmd("HOME F", 10);
  CHECK(t_has(m, "OK HOME F"), "OK HOME F");
  CHECK(wait_home("F", 60000, m), "끝남 (60 s 안)");
  CHECK(t_has(m, "DONE HOME F"), "DONE HOME F <걸음수>");
  printf("      %s", t_dump(m).c_str());
  CHECK(std::labs(W[0].mech - W[0].swPos) <= 3, "기계 위치 = 스위치 자리 (±3 반걸음, 3번 연속 LOW 거름 때문에 2걸음 지나침)");
  CHECK(W[0].minMech > W[0].swPos - 200, "스위치를 지나 200 반걸음(0.4 mm) 넘게 밀어붙이지 않음");
  CHECK(coils_off(), "HOME 끝나면 코일 꺼짐");
  m = t_cmd("STATUS"); CHECK(t_has(m, "F=0.000") && t_has(m, "HOMED=F "), "STATUS F=0.000 HOMED=F");
  CHECK(W[0].lost == 0, "순서 어긋난 걸음 0");

  printf("[2] 시험 ①: HOME 스위치 못 찾음 → ERR HOME X NOSWITCH, 한도 안에서 멈춤\n");
  pen_up();
  W[1].mech = 3000; W[1].swConnected = false;       // 스위치 선이 빠짐
  m = t_cmd("HOME X", 10);
  CHECK(wait_home("X", 60000, m), "끝남");
  CHECK(t_has(m, "ERR HOME X NOSWITCH"), "ERR HOME X NOSWITCH");
  long moved = 3000 - W[1].mech;
  printf("      움직인 걸음 %ld (한도 = 행정 36 mm + 4 mm = %ld)\n", moved, homeMaxSteps(axes[1]));
  CHECK(moved <= homeMaxSteps(axes[1]) + 2 && moved >= homeMaxSteps(axes[1]) - 2, "한도(행정+4 mm)만큼 가다 멈춤");
  CHECK(coils_off(), "실패하면 코일 꺼짐");
  m = t_cmd("STATUS"); CHECK(t_has(m, "HOMED=F "), "X 는 HOMED 아님 (F 만)");
  m = t_cmd("MOVE X 0"); CHECK(t_has(m, "ERR NOT_HOMED"), "실패한 축은 MOVE 거부");
  W[1].swConnected = true; W[1].mech = 3000;

  printf("[3] HOME Y: 행정 58 mm 끝(+18)에서 켜도 스위치에 닿음 (V6 — 20480 반걸음이면 거짓 NOSWITCH)\n");
  W[2].mech = (long)(58 * STEPS_PER_MM);            // 스위치 위 58 mm
  m = t_cmd("HOME Y", 10);
  CHECK(wait_home("Y", 120000, m), "끝남");
  CHECK(t_has(m, "DONE HOME Y"), "DONE HOME Y");
  printf("      %s", t_dump(m).c_str());
  CHECK(std::labs(W[2].mech - W[2].swPos) <= 3, "스위치 자리에서 멈춤");
  CHECK((long)(58 * STEPS_PER_MM) > 20480, "58 mm = 29,5xx 반걸음 > 20480 (옛 한도로는 못 닿았음)");

  printf("[4] HOME X 정상 + 이미 눌려 있으면 먼저 물러남\n");
  W[1].mech = 0;                                     // 스위치 위에 앉아 있음 (눌림)
  m = t_cmd("HOME X", 10); CHECK(wait_home("X", 30000, m) && t_has(m, "DONE HOME X"), "눌린 채 시작해도 HOME X 성공");
  CHECK(std::labs(W[1].mech - W[1].swPos) <= 3, "스위치 자리");

  printf("[5] 스위치 붙음/GND 단락 → HOME STUCK\n");
  AxisW saved = W[1];
  W[1].swPos = 1000000;                              // 어디서나 눌림
  m = t_cmd("HOME X", 10); CHECK(wait_home("X", 30000, m), "끝남");
  CHECK(t_has(m, "ERR HOME X STUCK"), "ERR HOME X STUCK");
  W[1].swPos = saved.swPos; W[1].mech = saved.mech;

  printf("[6] X 는 정상 홈, 펜 DOWN 이면 X·Y 이동·홈 거부 (V4)\n");
  m = t_cmd("HOME X", 10); wait_home("X", 30000, m);
  m = t_cmd("MOVE X 0", 10); t_wait(m, "DONE MOVE X", 40000);
  pen_down();
  CHECK(t_has(0, "DONE PEN DOWN"), "PEN DOWN 끝남");
  m = t_cmd("MOVE X 5"); CHECK(t_has(m, "ERR PEN_DOWN"), "펜 DOWN: MOVE X → ERR PEN_DOWN");
  m = t_cmd("MOVE Y -30"); CHECK(t_has(m, "ERR PEN_DOWN"), "펜 DOWN: MOVE Y → ERR PEN_DOWN");
  m = t_cmd("HOME X"); CHECK(t_has(m, "ERR PEN_DOWN"), "펜 DOWN: HOME X → ERR PEN_DOWN");
  m = t_cmd("HOME F", 10); CHECK(t_has(m, "OK HOME F"), "펜 DOWN: HOME F 는 허용 (F 는 내려가기만)"); wait_home("F", 60000, m);

  printf("[7] R1 (검토 CAP-AI-42): 바닥 올리기는 펜 UP 일 때만, 내리기·HOME F 는 언제나\n");
  pen_up();
  m = t_cmd("MOVE Y 0", 10); t_wait(m, "DONE MOVE Y", 40000);          // 펜을 마킹실 위로 (R1′ 은 Y > -20.5 에서만 막음)
  m = t_cmd("MOVE F 20", 10); CHECK(t_has(m, "OK MOVE F"), "펜 UP: MOVE F 20 접수"); t_wait(m, "DONE MOVE F", 40000);
  CHECK(t_near(t_value(m, "DONE MOVE F "), 20.0, 0.01), "F 20 mm 도착");
  pen_down();
  m = t_cmd("MOVE F 30"); CHECK(t_has(m, "ERR PEN_DOWN") && !t_has(m, "OK MOVE"), "펜 DOWN: MOVE F 30 (올리기) → ERR PEN_DOWN");
  m = t_cmd("PRESS 50"); CHECK(t_has(m, "ERR PEN_DOWN") && !t_has(m, "OK PRESS"), "펜 DOWN: PRESS → ERR PEN_DOWN");
  m = t_cmd("MOVE F 20"); CHECK(t_has(m, "OK MOVE F") && t_near(t_value(m, "DONE MOVE F "), 20.0, 0.01), "펜 DOWN: 같은 높이 MOVE F 20 → OK (올리기 아님)");
  m = t_cmd("MOVE F 5", 10); CHECK(t_has(m, "OK MOVE F"), "펜 DOWN: MOVE F 5 (내리기) → OK"); t_wait(m, "DONE MOVE F", 40000);
  CHECK(t_near(t_value(m, "DONE MOVE F "), 5.0, 0.01), "F 5 mm 도착 (내려감)");
  m = t_cmd("MOVE F 0", 10); t_wait(m, "DONE MOVE F", 40000); CHECK(t_near(t_value(m, "DONE MOVE F "), 0.0, 0.01), "펜 DOWN: MOVE F 0 (내리기) → OK");
  printf("[7b] R1′: 펜이 대기 자리 캡 컵(Y −40)에 꽂혀 있으면 F 올리기 허용 (재방문 급이)\n");
  pen_up();
  m = t_cmd("MOVE Y -40", 10); t_wait(m, "DONE MOVE Y", 40000);
  pen_down();
  m = t_cmd("MOVE F 10", 10); CHECK(t_has(m, "OK MOVE F"), "펜 DOWN + Y −40: MOVE F 10 → OK"); t_wait(m, "DONE MOVE F", 40000);
  m = t_cmd("PRESS 50"); CHECK(t_has(m, "ERR PEN_DOWN"), "PRESS 는 그래도 펜 UP 일 때만");
  m = t_cmd("MOVE F 0", 10); t_wait(m, "DONE MOVE F", 40000);
  pen_up();

  printf("[8] 펜 내리기 2단계: 마지막 구간은 ≤ 60 °/s (S4 M8), 올리기는 빠르게\n");
  g_servo_events.erase(g_servo_events.begin(), g_servo_events.end());
  pen_down();
  { std::vector<ServoEvent> wr; for (auto& e : g_servo_events) if (e.kind == 'W' || e.kind == 'A') wr.push_back(e);
    double maxRate = 0; int slow_n = 0;
    for (size_t i = 1; i < wr.size(); i++) {
      double dt = (wr[i].t_us - wr[i - 1].t_us) / 1e6, da = std::abs(wr[i].angle - wr[i - 1].angle);
      if (wr[i - 1].angle <= PEN_SLOW_DEG + 1 && dt > 0) { maxRate = std::max(maxRate, da / dt); slow_n++; }
    }
    printf("      마지막 %d° 구간 최대 각속도 %.1f °/s (한도 60), 쓰기 %zu번\n", PEN_SLOW_DEG, maxRate, wr.size());
    CHECK(slow_n >= PEN_SLOW_DEG - 1, "천천히 구간이 1° 단위로 나뉘어 있음");
    CHECK(maxRate <= 60.0, "천천히 구간 각속도 ≤ 60 °/s"); }
  CHECK(last_write(A0) == PEN_DOWN_DEG, "마지막 각도 = 아래");
  m = t_cmd("STATUS"); CHECK(t_has(m, "PEN=DOWN"), "STATUS PEN=DOWN");
  m = t_cmd("PEN SIDE"); CHECK(t_has(m, "ERR STATE"), "PEN SIDE → ERR STATE");
  pen_up();
  CHECK(last_write(A0) == PEN_UP_DEG, "PEN UP → 위 각도");

  printf("[9] V5: 스위치 쪽으로 가다 원점보다 한참 위에서 눌리면(걸음 잃음) 정지 + EVT SWITCH\n");
  m = t_cmd("MOVE F 10", 10); t_wait(m, "DONE MOVE F", 40000);
  W[0].swPos += (long)(2 * STEPS_PER_MM);           // 기계가 2 mm 어긋남 → 스위치가 2 mm 일찍 눌림
  m = t_cmd("MOVE F 0", 10); t_wait(m, "EVT SWITCH F", 40000);
  CHECK(t_has(m, "EVT SWITCH F"), "EVT SWITCH F <mm>");
  CHECK(!t_has(m, "DONE MOVE F"), "도착 보고 없음");
  t_run(100); m = t_cmd("STATUS"); CHECK(!t_has(m, "HOMED=F") && t_has(m, "MOVING=-"), "F 는 HOMED 해제, 정지");
  CHECK(coils_off(), "코일 꺼짐");
  W[0].swPos -= (long)(2 * STEPS_PER_MM);
  m = t_cmd("HOME F", 10); CHECK(wait_home("F", 60000, m) && t_has(m, "DONE HOME F"), "HOME F 로 다시 맞춤");

  printf("[10] HOLD 기본 0 / HOLD F 1 / 이동 끝나면 코일 꺼짐\n");
  m = t_cmd("MOVE F 1", 10); t_wait(m, "DONE MOVE F", 20000);
  CHECK(coils_off(), "이동 뒤 코일 꺼짐 (HOLD F 0 기본)");
  m = t_cmd("HOLD F 1"); CHECK(t_has(m, "OK HOLD") && !coils_off(), "HOLD F 1 → 코일 켜짐");
  m = t_cmd("HOLD F 0"); CHECK(coils_off(), "HOLD F 0 → 코일 꺼짐");

  printf("[11] SPEED / LIMIT / ZERO\n");
  m = t_cmd("SPEED X 700"); CHECK(t_has(m, "ERR SPEED_MIN_800"), "700 µs → 거부 (최소 800)");
  m = t_cmd("SPEED X 1200"); CHECK(t_has(m, "ERR SPEED_SURGE_BAND"), "1200 µs → 거부 (스프링 서지 띠 1080~1460)");
  m = t_cmd("SPEED X 1000"); CHECK(t_has(m, "OK SPEED"), "1000 µs → OK");
  m = t_cmd("SPEED X 1600"); CHECK(t_has(m, "OK SPEED"), "1600 µs → OK (띠 밖)");
  t_cmd("SPEED X 1000");
  m = t_cmd("MOVE F 99"); CHECK(t_has(m, "ERR LIMIT"), "행정 밖 → ERR LIMIT");
  m = t_cmd("LIMIT F 5 1"); CHECK(t_has(m, "ERR RANGE"), "LIMIT 거꾸로 → ERR RANGE");
  m = t_cmd("MOVE Q 1"); CHECK(t_has(m, "ERR AXIS"), "축 이름 틀림 → ERR AXIS");
  m = t_cmd("ZERO Y 3"); CHECK(t_has(m, "OK ZERO"), "ZERO Y 3");
  m = t_cmd("STATUS"); CHECK(t_near(t_value(m, "Y="), 3.0, 0.01) && t_has(m, "HOMED=FXY"), "ZERO 한 축도 HOMED");

  printf("[12] PRESS: 하중이 g 에 닿으면 멈춤 (HX711 흉내), 펜 UP 일 때만\n");
  m = t_cmd("CAL 0.1"); m = t_cmd("TARE");
  hx_pulse = 0;
  m = t_cmd("PRESS 50 30", 10);
  CHECK(t_has(m, "OK PRESS"), "OK PRESS");
  CHECK(t_wait(m, "DONE PRESS", 40000), "DONE PRESS");
  printf("      %s", t_dump(m).c_str());
  CHECK(t_near(t_value(m, "DONE PRESS "), 10.5, 0.1), "10.5 mm 근처(스위치 위 10 mm + 0.5 mm = 50 g)에서 멈춤");
  CHECK(!t_has(m, "LIMIT"), "한계에 닿아서 멈춘 것이 아님");
  m = t_cmd("MOVE F 0", 10); t_wait(m, "DONE MOVE F 0.000", 40000);
  m = t_cmd("PRESS 99999 5", 10); t_wait(m, "DONE PRESS", 40000);
  CHECK(t_has(m, "DONE PRESS LIMIT"), "너무 큰 g → DONE PRESS LIMIT (5 mm 한계)");
  m = t_cmd("MOVE F 0", 10); t_wait(m, "DONE MOVE F 0.000", 40000);

  printf("[13] STOP: 움직이는 축 정지, HOME 중이면 HOME 도 멈춤\n");
  m = t_cmd("MOVE F 30", 500); CHECK(t_has(m, "OK MOVE F"), "이동 시작");
  m = t_cmd("STOP", 20); CHECK(t_has(m, "OK STOP"), "OK STOP");
  m = t_cmd("STATUS"); CHECK(t_has(m, "MOVING=-"), "멈춤"); CHECK(coils_off(), "코일 꺼짐");
  W[2].mech = (long)(20 * STEPS_PER_MM) + W[2].swPos;
  m = t_cmd("HOME Y", 500); m = t_cmd("STOP", 20);
  CHECK(t_has(m, "ERR HOME Y STOPPED") && t_has(m, "OK STOP"), "HOME 중 STOP → ERR HOME Y STOPPED");

  printf("[14] WATCHDOG: Pi가 멈추면 정지 + 펜 들기\n");
  pen_down();
  m = t_cmd("WATCHDOG 0.5"); CHECK(t_has(m, "OK WATCHDOG"), "OK WATCHDOG");
  m = t_mark(); t_run(900);
  CHECK(t_has(m, "EVT WATCHDOG_STOP"), "EVT WATCHDOG_STOP");
  t_run(500); CHECK(last_write(A0) == PEN_UP_DEG, "펜을 들어 올림");
  m = t_cmd("WATCHDOG 0");

  printf("[15] SERVO PEN / SETDOOR PEN / 문 서보 명령은 UNO 1에 없음\n");
  m = t_cmd("SERVO IN 90"); CHECK(t_has(m, "ERR DOOR"), "SERVO IN → ERR DOOR (문은 UNO 2)");
  m = t_cmd("SETDOOR PEN 70 5"); CHECK(t_has(m, "OK SETDOOR"), "SETDOOR PEN 70 5");
  pen_up(); CHECK(last_write(A0) == 70, "보정한 위 각도 70");
  m = t_cmd("DOOR IN OPEN"); CHECK(t_has(m, "ERR UNKNOWN"), "DOOR 명령 없음 → ERR UNKNOWN");

  printf("\n순서 어긋난 걸음: F %ld, X %ld, Y %ld (0 이어야 함)\n", W[0].lost, W[1].lost, W[2].lost);
  CHECK(W[0].lost == 0 && W[1].lost == 0 && W[2].lost == 0, "코일 순서 어긋남 없음 (걸음 건너뜀 없음)");
  return t_summary("sim_motion");
}



