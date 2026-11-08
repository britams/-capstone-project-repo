// sim_doors.cpp — trap_doors.ino (UNO 2) PC 시험 (서현 CAP-AI-44)
// 빌드:  zig c++ -std=c++17 -Wall -I. sim_doors.cpp -o sim_doors.exe   (run_all.ps1 이 해 줌)
// 실제 .ino 를 그대로 #include 한다. 세계 = 빛 게이트 9개 + 레일 + 문 서보 기록.
#include "Arduino.h"
#include "Servo.h"
SIM_DEFINE_GLOBALS
SIM_DEFINE_SERVO
#include "../../design/circuit/firmware/trap_doors/trap_doors.ino"
#include "sim_common.h"
#include <map>

// ---- 세계 ----
static const char* GN[9] = {"G1", "G2", "G2b", "G3", "G3b", "G4", "G5", "G5b", "G6"};   // 스케치 gates[] 순서
static int gi(const char* n) { for (int i = 0; i < 9; i++) if (!strcmp(GN[i], n)) return i; return -1; }
static bool w_blocked[9], w_dead[9];     // dead = 송신부/수신부 고장 (빛이 안 옴, 수신부 선 빠짐 포함)
static bool w_rail = true;
static std::function<void()> w_script;   // 시험이 넣는 장면 (시간·서보 각도에 따라 빔을 막음)
static const int ANALOG_PIN_GATE[6] = {1, 2, 3, 4, 6, 7};        // A0..A5 → gates[] 번호
static int digital_gate(int pin) { return pin == 7 ? 0 : pin == 8 ? 5 : pin == 12 ? 8 : -1; }
static bool lit(int g) { return g_pins[4] && !w_blocked[g] && !w_dead[g]; }   // 송신(D4) 켬 + 안 막힘 + 안 고장

static void world_setup() {
  g_world = []() { if (w_script) w_script(); };
  g_dread = [](int p) -> int {
    if (p == 2) return w_rail ? 1 : 0;
    int g = digital_gate(p);
    if (g >= 0) { if (w_dead[g]) return 1;               // 수신부 선이 빠짐 → 풀업 때문에 늘 HIGH
                  return lit(g) ? 1 : 0; }
    return g_pins[p];
  };
  g_aread = [](int p) -> int {
    int k = p - 14; if (k < 0 || k > 5) return 0;
    int g = ANALOG_PIN_GATE[k];
    if (w_dead[g]) return 120;                           // 빛이 없을 때의 값
    return lit(g) ? 820 : 130;                           // 빛 받음 / 못 받음 — 값은 흉내 (실물 미검증)
  };
}
static void world_reset() {
  for (int i = 0; i < 9; i++) w_blocked[i] = w_dead[i] = false;
  w_rail = true; w_script = nullptr;
  g_us = 0; g_lines.clear(); g_servo_events.clear(); Serial.in.clear(); Serial.cur.clear();
  for (int i = 0; i < 24; i++) { g_servo_angle[i] = -1; g_servo_attached[i] = 0; g_pins[i] = 0; }
  // 스케치 전역 상태는 프로세스당 한 번이라 시험마다 새 프로세스를 쓰지 않고, 시험 순서를 짜서 쓴다 (아래 주석)
}

static int attached_max() {                       // 동시에 붙어 있던 서보 수의 최댓값
  int cnt = 0, mx = 0; std::map<int, bool> a;
  for (auto& e : g_servo_events) { if (e.kind == 'A') a[e.pin] = true; if (e.kind == 'D') a[e.pin] = false; cnt = 0; for (auto& kv : a) cnt += kv.second; if (cnt > mx) mx = cnt; }
  return mx;
}
static double min_attach_gap_s() {                // 서로 다른 서보를 붙이는 간격 최솟값
  double best = 1e9; unsigned long last = 0; bool have = false;
  for (auto& e : g_servo_events) if (e.kind == 'A') { if (have) best = std::min(best, (e.t_us - last) / 1e6); last = e.t_us; have = true; }
  return best;
}
static int last_write(int pin) { return g_servo_angle[pin]; }

// 스크립트: 문 IN(서보 D9)이 닫히는 중(각도 ≥ 100)에 빔 G2b 를 ms 동안 막음. times 번 반복
struct BlockWhileClosing {
  int pin, gate, minAngle, times, done = 0; unsigned long hold_ms; bool active = false; unsigned long until = 0;
  void operator()() {
    if (active) { if (g_us >= until) { w_blocked[gate] = false; active = false; } return; }
    if (done < times && g_servo_attached[pin] && g_servo_angle[pin] >= minAngle) {
      w_blocked[gate] = true; active = true; until = g_us + hold_ms * 1000UL; done++;
    }
  }
};

// 서버 모드:  sim_doors.exe --serve [--speed N] [--block G2b] [--dead G2b]
//   제어 줄: #BLOCK <게이트> 0|1, #DEAD <게이트> 0|1 (고장), #RAIL 0|1, #CLOSEBLOCK <문 IN|CAP|REL> <게이트> <횟수>
//   (#CLOSEBLOCK: 그 문이 닫히는 중 각도 ≥ 100 이 될 때마다 게이트를 600 ms 막음, 횟수만큼)
static BlockWhileClosing g_cb{9, 0, 100, 0, 0, 600};
static int serve(int argc, char** argv) {
  double speed = 1.0;
  world_setup(); world_reset();
  for (int i = 2; i < argc; i++) {
    if (!strcmp(argv[i], "--speed") && i + 1 < argc) speed = atof(argv[++i]);
    else if (!strcmp(argv[i], "--block") && i + 1 < argc) w_blocked[gi(argv[++i])] = true;
    else if (!strcmp(argv[i], "--dead") && i + 1 < argc) w_dead[gi(argv[++i])] = true;
  }
  w_script = []() { g_cb(); };
  return t_serve(speed, [](const std::string& l) {
    char g[8], d[8]; int v, n;
    if (sscanf(l.c_str(), "#BLOCK %7s %d", g, &v) == 2 && gi(g) >= 0) w_blocked[gi(g)] = v != 0;
    else if (sscanf(l.c_str(), "#DEAD %7s %d", g, &v) == 2 && gi(g) >= 0) w_dead[gi(g)] = v != 0;
    else if (sscanf(l.c_str(), "#RAIL %d", &v) == 1) w_rail = v != 0;
    else if (sscanf(l.c_str(), "#CLOSEBLOCK %7s %7s %d", d, g, &n) == 3 && gi(g) >= 0) {
      int pin = !strcmp(d, "IN") ? 9 : !strcmp(d, "CAP") ? 10 : 11;
      g_cb = BlockWhileClosing{pin, gi(g), 100, n, 0, 600};
    }
  });
}

int main(int argc, char** argv) {
  if (argc > 1 && !strcmp(argv[1], "--serve")) return serve(argc, argv);
  world_setup();
  world_reset();

  // ===== 0. 켜기 =====
  printf("[0] 켜기: READY 이름, 서보를 붙이지 않음 (V1), 자가 시험\n");
  setup();
  CHECK(t_has(0, "EVT READY trap_doors v0.2"), "READY 이름 trap_doors");
  CHECK(t_has(0, "EVT SELFTEST G1=OK G2=OK G2b=OK G3=OK G3b=OK G4=OK G5=OK G5b=OK G6=OK"), "켤 때 자가 시험 9쌍 OK");
  CHECK(g_servo_events.empty(), "켤 때 문 서보를 붙이지 않음 (V1)");
  t_run(100);
  size_t m = t_cmd("STATUS");
  CHECK(t_has(m, "OK STATUS IN=UNKNOWN CAP=UNKNOWN REL=UNKNOWN RAIL=1 EMIT=1 GATES=111111111"), "STATUS: 문 UNKNOWN, 게이트 9개 1");
  m = t_cmd("PING"); CHECK(t_has(m, "OK PONG"), "PING");
  m = t_cmd("foo"); CHECK(t_has(m, "ERR UNKNOWN"), "모르는 명령 → ERR UNKNOWN");

  // ===== 1. 서보 하나씩 + 0.3 s =====
  printf("[1] 문 열기 3개: 서보 한 번에 하나, 붙이는 간격 ≥ 0.3 s, 첫 펄스 각도 = 열림 각도\n");
  m = t_cmd("DOOR IN OPEN", 20);
  CHECK(t_has(m, "OK DOOR"), "DOOR IN OPEN 접수");
  m = t_cmd("DOOR CAP OPEN", 20);
  CHECK(t_has(m, "ERR BUSY"), "IN이 움직이는 동안 CAP 명령은 ERR BUSY (V2)");
  t_run(800);
  CHECK(t_has(0, "DONE DOOR IN OPEN"), "DONE DOOR IN OPEN");
  m = t_cmd("DOOR CAP OPEN", 50); t_wait(m, "DONE DOOR CAP OPEN", 2000);
  m = t_cmd("DOOR REL OPEN", 50); t_wait(m, "DONE DOOR REL OPEN", 2000);
  CHECK(attached_max() == 1, "동시에 붙은 서보 최대 1개");
  printf("      붙이는 간격 최솟값 %.3f s\n", min_attach_gap_s());
  CHECK(min_attach_gap_s() >= 0.3, "서보 붙이는 간격 ≥ 0.3 s");
  bool first_ok = true; for (auto& e : g_servo_events) if (e.kind == 'A' && e.angle != DOOR_OPEN_DEG) first_ok = false;
  CHECK(first_ok, "붙일 때 첫 펄스가 열림 각도 (튀지 않음)");
  t_run(1500);
  CHECK(g_servo_attached[9] == 0 && g_servo_attached[10] == 0 && g_servo_attached[11] == 0, "멈춘 뒤 서보 뗌 (HOLD 아님)");
  m = t_cmd("STATUS"); CHECK(t_has(m, "IN=OPEN CAP=OPEN REL=OPEN"), "STATUS 세 문 OPEN");

  // ===== 2. 정상 닫기 =====
  printf("[2] 빔이 비어 있으면 0.2 s 뒤 닫기 시작 → DONE DOOR IN CLOSED\n");
  m = t_cmd("DOOR IN CLOSE", 20);
  CHECK(t_has(m, "OK DOOR"), "DOOR IN CLOSE 접수");
  CHECK(t_wait(m, "DONE DOOR IN CLOSED", 3000), "DONE DOOR IN CLOSED");
  int idx = t_find(m, "DONE DOOR IN CLOSED");
  printf("      닫는 데 걸린 시간 %.2f s\n", idx >= 0 ? t_time(idx) - t_time((int)m) : -1.0);
  CHECK(last_write(9) == DOOR_CLOSED_DEG, "서보 마지막 각도 = 닫힘 각도");
  m = t_cmd("DOOR IN CLOSE"); CHECK(t_has(m, "DONE DOOR IN CLOSED") && t_has(m, "OK DOOR"), "이미 닫힌 문 → 바로 DONE");
  t_cmd("DOOR IN OPEN"); t_wait(0, "DONE DOOR IN OPEN", 100); t_run(1000);

  // ===== 3. 닫는 중 빔 끊김 → REOPEN → 다시 닫힘 =====
  printf("[3] 시험 ②: 닫는 중 빔 끊김 → REOPEN, 한 번만 끊기면 다음에 닫힘\n");
  static BlockWhileClosing S1{9, gi("G2b"), 100, 1, 0, 600};   // 1번만 600 ms 막음
  w_script = [&]() { S1(); };
  m = t_cmd("DOOR IN CLOSE", 20);
  CHECK(t_wait(m, "EVT DOOR IN REOPEN 1", 3000), "닫는 중 끊김 → EVT DOOR IN REOPEN 1");
  int ri = t_find(m, "EVT DOOR IN REOPEN 1");
  CHECK(last_write(9) == DOOR_OPEN_DEG, "끊기자 서보를 열림 각도로 (바로 엶)");
  CHECK(t_wait(m, "DONE DOOR IN CLOSED", 6000), "빔이 풀린 뒤 다시 시도해 DONE DOOR IN CLOSED");
  int ci = t_find(m, "DONE DOOR IN CLOSED");
  printf("      REOPEN → CLOSED 사이 %.2f s\n", (ci >= 0 && ri >= 0) ? t_time(ci) - t_time(ri) : -1.0);
  CHECK(!t_has(m, "BLOCKED"), "한 번만 끊겼으니 BLOCKED 아님");
  w_script = nullptr; w_blocked[gi("G2b")] = false;
  t_cmd("DOOR IN OPEN"); t_wait(0, "DONE DOOR IN OPEN", 100); t_run(1000);

  // ===== 4. 3번 끊김 → BLOCKED, 열어 둠 =====
  printf("[4] 시험 ②: 3번 모두 끊김 → EVT DOOR IN BLOCKED, 문은 열린 채\n");
  static BlockWhileClosing S3{9, gi("G2b"), 100, 99, 0, 600};
  w_script = [&]() { S3(); };
  m = t_cmd("DOOR IN CLOSE", 20);
  CHECK(t_wait(m, "EVT DOOR IN BLOCKED", 12000), "3번 실패 → EVT DOOR IN BLOCKED");
  CHECK(t_has(m, "EVT DOOR IN REOPEN 1") && t_has(m, "EVT DOOR IN REOPEN 2") && t_has(m, "EVT DOOR IN REOPEN 3"), "REOPEN 1·2·3 순서로 나옴");
  CHECK(!t_has(m, "DONE DOOR IN CLOSED"), "닫힘 보고 없음");
  t_run(1500);
  CHECK(last_write(9) == DOOR_OPEN_DEG, "마지막 각도 = 열림 (열어 둔 채)");
  m = t_cmd("STATUS"); CHECK(t_has(m, "IN=BLOCKED"), "STATUS IN=BLOCKED");
  w_script = nullptr; w_blocked[gi("G2b")] = false;
  m = t_cmd("DOOR IN OPEN"); CHECK(t_wait(m, "DONE DOOR IN OPEN", 1500), "BLOCKED 뒤 DOOR IN OPEN 으로 풀림");
  t_run(1000);

  // ===== 5. WAIT 시간 초과 =====
  printf("[5] 빔이 계속 막혀 있으면 2 s 뒤 ERR DOOR IN WAIT, 닫기 시작 안 함\n");
  w_blocked[gi("G2")] = true;
  m = t_cmd("DOOR IN CLOSE", 20);
  CHECK(t_wait(m, "ERR DOOR IN WAIT", 3000), "ERR DOOR IN WAIT");
  int wi = t_find(m, "ERR DOOR IN WAIT");
  printf("      WAIT 오류까지 %.2f s\n", wi >= 0 ? t_time(wi) - t_time((int)m) : -1.0);
  CHECK(last_write(9) == DOOR_OPEN_DEG, "서보는 열림 각도 그대로");
  w_blocked[gi("G2")] = false; t_run(1000);
  m = t_cmd("STATUS"); CHECK(t_has(m, "IN=OPEN"), "WAIT 끝나면 원래 상태(OPEN)로 돌아감, 안 굳음");
  m = t_cmd("DOOR IN CLOSE", 20); CHECK(t_wait(m, "DONE DOOR IN CLOSED", 3000), "빔이 풀리면 다시 닫을 수 있음");
  t_cmd("DOOR IN OPEN"); t_wait(0, "DONE DOOR IN OPEN", 100); t_run(1000);

  // ===== 6. RAIL 0 → 문 명령 거부 =====
  printf("[6] 시험 ④: RAIL 0 (비상 정지) → 문 명령 거부\n");
  w_rail = false; t_run(60);
  CHECK(t_has(0, "EVT RAIL 0"), "EVT RAIL 0 (20 ms 같은 값 뒤)");
  m = t_cmd("RAIL"); CHECK(t_has(m, "OK RAIL 0"), "RAIL → OK RAIL 0");
  m = t_cmd("DOOR IN CLOSE"); CHECK(t_has(m, "ERR RAIL") && !t_has(m, "OK DOOR"), "DOOR IN CLOSE → ERR RAIL");
  m = t_cmd("DOOR CAP OPEN"); CHECK(t_has(m, "ERR RAIL"), "DOOR CAP OPEN → ERR RAIL");
  m = t_cmd("SERVO IN 90"); CHECK(t_has(m, "ERR RAIL"), "SERVO IN 90 → ERR RAIL");
  w_rail = true; t_run(60);
  CHECK(t_has(0, "EVT RAIL 1"), "EVT RAIL 1 (풀림)");
  m = t_cmd("DOOR CAP OPEN"); CHECK(t_has(m, "OK DOOR"), "RAIL 1 이 되면 문 명령 다시 받음");
  t_run(800);

  // ===== 7. 레일이 닫는 도중 끊김 =====
  printf("[7] 닫는 도중 RAIL 0 → 문은 UNKNOWN, 서보 뗌, 오래 안 붙들림\n");
  m = t_cmd("DOOR IN CLOSE", 400);
  CHECK(g_servo_attached[9] == 1, "닫는 중 (서보 붙어 있음)");
  w_rail = false; t_run(100);
  CHECK(g_servo_attached[9] == 0 && g_servo_attached[10] == 0 && g_servo_attached[11] == 0, "RAIL 0 이 되면 서보를 모두 뗌");
  m = t_cmd("STATUS"); CHECK(t_has(m, "IN=UNKNOWN") && t_has(m, "RAIL=0"), "문 자리를 모름 → UNKNOWN (Pi가 HOME·OPEN부터 다시)");
  w_rail = true; t_run(100);
  m = t_cmd("DOOR IN OPEN"); t_wait(m, "DONE DOOR IN OPEN", 1500); t_run(1000);

  // ===== 8. 같은 문 OPENING 중 CLOSE (고친 버그) =====
  printf("[8] 열리는 중 같은 문에 CLOSE → ERR BUSY (prev=OPENING 로 굳는 버그를 고침)\n");
  t_cmd("DOOR CAP CLOSE"); t_wait(0, "DONE DOOR CAP CLOSED", 3000); t_run(600);
  m = t_cmd("DOOR CAP OPEN", 50);
  m = t_cmd("DOOR CAP CLOSE", 20);
  CHECK(t_has(m, "ERR BUSY"), "열리는 중 CLOSE → ERR BUSY");
  t_wait(0, "DONE DOOR CAP OPEN", 1500); t_run(1000);
  m = t_cmd("STATUS"); CHECK(t_has(m, "CAP=OPEN"), "문이 OPEN 으로 끝남 (안 굳음)");

  // ===== 9. 닫는 중 OPEN 으로 취소 =====
  printf("[9] 닫는 중 DOOR OPEN 으로 취소\n");
  m = t_cmd("DOOR IN CLOSE", 500);
  m = t_cmd("DOOR IN OPEN", 20); CHECK(t_has(m, "OK DOOR"), "닫는 중 같은 문 OPEN 접수");
  CHECK(t_wait(m, "DONE DOOR IN OPEN", 1500), "열림으로 끝남");
  CHECK(last_write(9) == DOOR_OPEN_DEG, "각도 = 열림");
  t_run(1000);

  // ===== 10. 빔 고장 = SELFTEST FAIL → 닫기 거부 =====
  printf("[10] 시험 ③: SELFTEST FAIL → 그 문의 닫기 거부 (G2b LED 고장)\n");
  w_dead[gi("G2b")] = true;
  m = t_cmd("SELFTEST", 100);
  CHECK(t_has(m, "OK SELFTEST") && t_has(m, "G2b=FAIL(0)"), "SELFTEST: G2b=FAIL(켬−끔 차이 0)");
  CHECK(t_has(m, "G2=OK") && t_has(m, "G3=OK"), "나머지 빔은 OK");
  m = t_cmd("DOOR IN CLOSE"); CHECK(t_has(m, "ERR DOOR IN BEAMFAIL") && !t_has(m, "OK DOOR"), "DOOR IN CLOSE → ERR DOOR IN BEAMFAIL");
  CHECK(last_write(9) == DOOR_OPEN_DEG, "서보 움직이지 않음");
  m = t_cmd("DOOR CAP CLOSE"); CHECK(t_wait(m, "DONE DOOR CAP CLOSED", 3000), "다른 문(CAP)은 정상으로 닫힘");
  t_cmd("DOOR CAP OPEN"); t_wait(0, "DONE DOOR CAP OPEN", 100); t_run(1000);
  m = t_cmd("GATES"); CHECK(t_has(m, "OK GATES G1=1 G2=1 G2b=? G3=1"), "GATES: 고장 빔은 ?");
  m = t_cmd("DOOR IN OPEN"); CHECK(t_has(m, "OK DOOR"), "고장 빔이 있어도 열기는 됨");
  t_run(800);
  // 고장난 빔은 사건도 안 보냄
  size_t mm = t_mark(); w_blocked[gi("G2b")] = true; t_run(100); w_blocked[gi("G2b")] = false; t_run(100);
  CHECK(!t_has(mm, "EVT GATE G2b"), "고장 빔은 EVT GATE 를 안 보냄");
  w_dead[gi("G2b")] = false; m = t_cmd("SELFTEST", 100);
  CHECK(t_has(m, "G2b=OK"), "고친 뒤 SELFTEST → OK");
  m = t_cmd("DOOR IN CLOSE"); CHECK(t_wait(m, "DONE DOOR IN CLOSED", 3000), "그 문 다시 닫힘");
  t_cmd("DOOR IN OPEN"); t_wait(0, "DONE DOOR IN OPEN", 100); t_run(1000);

  // ===== 11. 통로 게이트 고장 (수신 선 빠짐) =====
  printf("[11] 통로 게이트 G1 수신 선 빠짐 → 자가 시험 FAIL(H)\n");
  w_dead[gi("G1")] = true;
  m = t_cmd("SELFTEST", 100);
  CHECK(t_has(m, "G1=FAIL(H)"), "G1=FAIL(H) (송신을 꺼도 HIGH)");
  m = t_cmd("GATES"); CHECK(t_has(m, "G1=?"), "G1 = ?");
  w_dead[gi("G1")] = false; t_cmd("SELFTEST", 100);

  // ===== 12. EVT GATE 20 ms 거름 =====
  printf("[12] EVT GATE: 20 ms 미만 잡음은 안 보내고, 진짜 막힘은 BLOCK·CLEAR\n");
  mm = t_mark(); w_blocked[gi("G1")] = true; t_run(10); w_blocked[gi("G1")] = false; t_run(100);
  CHECK(!t_has(mm, "EVT GATE G1"), "10 ms 끊김 → 사건 없음");
  mm = t_mark(); w_blocked[gi("G1")] = true; t_run(100);
  CHECK(t_has(mm, "EVT GATE G1 BLOCK"), "100 ms 끊김 → EVT GATE G1 BLOCK (진입 신호)");
  w_blocked[gi("G1")] = false; t_run(100);
  CHECK(t_has(mm, "EVT GATE G1 CLEAR"), "풀리면 EVT GATE G1 CLEAR");
  mm = t_mark(); w_blocked[gi("G3b")] = true; t_run(100); w_blocked[gi("G3b")] = false; t_run(100);
  CHECK(t_has(mm, "EVT GATE G3b BLOCK") && t_has(mm, "EVT GATE G3b CLEAR"), "문 빔(아날로그)도 BLOCK·CLEAR");

  // ===== 13. EMIT 0 =====
  printf("[13] EMIT 0 (밤): 닫기 거부(EMIT_OFF), 게이트 사건 멈춤, EMIT 1 로 되돌려도 가짜 사건 없음\n");
  m = t_cmd("EMIT 0"); CHECK(t_has(m, "OK EMIT"), "EMIT 0");
  m = t_cmd("DOOR IN CLOSE"); CHECK(t_has(m, "ERR DOOR IN EMIT_OFF"), "송신 끄면 닫기 거부");
  m = t_cmd("DOOR IN OPEN"); CHECK(t_has(m, "OK DOOR"), "열기는 됨"); t_run(800);
  mm = t_mark(); t_run(300);
  CHECK(!t_has(mm, "EVT GATE"), "송신 끈 동안 EVT GATE 없음 (송신 꺼서 생기는 가짜 BLOCK 없음)");
  m = t_cmd("EMIT 1", 200); CHECK(t_has(m, "OK EMIT"), "EMIT 1");
  CHECK(!t_has(m, "EVT GATE"), "다시 켜도 가짜 사건 없음");

  // ===== 14. LIGHT =====
  printf("[14] LIGHT\n");
  m = t_cmd("LIGHT TOP 255"); CHECK(t_has(m, "OK LIGHT") && g_pins[3] == 255, "LIGHT TOP 255 → D3");
  m = t_cmd("LIGHT BOT 128"); CHECK(g_pins[5] == 128, "LIGHT BOT 128 → D5");
  m = t_cmd("LIGHT TOP 300"); CHECK(t_has(m, "ERR VALUE"), "범위 밖 → ERR VALUE");
  m = t_cmd("LIGHT SIDE 1"); CHECK(t_has(m, "ERR LIGHT"), "이름 틀림 → ERR LIGHT");

  // ===== 15. WATCHDOG =====
  printf("[15] WATCHDOG: Pi가 멈추면 닫던 문을 연다\n");
  m = t_cmd("WATCHDOG 1"); CHECK(t_has(m, "OK WATCHDOG"), "WATCHDOG 1");
  // 느리게 닫히도록 빔을 반쯤 열어 둔 채 닫기 시작
  m = t_cmd("DOOR REL CLOSE", 450);
  CHECK(g_servo_attached[11] == 1, "닫는 중");
  m = t_mark(); t_run(1500);
  CHECK(t_has(m, "EVT WATCHDOG_HOLD"), "EVT WATCHDOG_HOLD");
  m = t_cmd("WATCHDOG 0"); t_run(1500);
  CHECK(last_write(11) == DOOR_OPEN_DEG || g_servo_attached[11] == 0, "닫던 문을 열림으로 (또는 이미 닫혔으면 뗌)");

  printf("\n서보 이벤트 수 %zu, 시리얼 줄 %zu\n", g_servo_events.size(), g_lines.size());
  return t_summary("sim_doors");
}
