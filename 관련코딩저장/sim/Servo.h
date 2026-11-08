// Servo.h — PC 시뮬레이션용 서보 흉내 (서현 CAP-AI-43)
// attach 시점과 '붙일 때 첫 펄스 각도'를 기록한다 → 서보 하나씩·0.3 s 간격·첫 펄스 규칙을 시험.
#pragma once
extern unsigned long g_us;
struct ServoEvent { unsigned long t_us; int pin; char kind; int angle; };   // kind: 'A' attach, 'D' detach, 'W' write
extern std::vector<ServoEvent> g_servo_events;
extern int g_servo_angle[24];     // 핀별 마지막으로 내보낸 각도 (-1 = 없음)
extern int g_servo_attached[24];

struct Servo {
  int pin = -1;
  int ang = -1;          // write()로 저장한 값 (AVR Servo도 attach 전 write는 값을 저장해 둠)
  bool att = false;
  void attach(int p) {
    pin = p; att = true;
    g_servo_attached[p] = 1;
    g_servo_angle[p] = ang;
    g_servo_events.push_back({g_us, p, 'A', ang});
  }
  void detach() {
    if (!att) return;
    att = false;
    g_servo_attached[pin] = 0;
    g_servo_events.push_back({g_us, pin, 'D', ang});
  }
  bool attached() const { return att; }
  void write(int d) {
    ang = d;
    if (att) { g_servo_angle[pin] = d; g_servo_events.push_back({g_us, pin, 'W', d}); }
  }
};
#define SIM_DEFINE_SERVO int g_servo_angle[24]; int g_servo_attached[24]; std::vector<ServoEvent> g_servo_events;
