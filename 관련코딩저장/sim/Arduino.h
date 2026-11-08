// Arduino.h — PC 시뮬레이션용 흉내 헤더 (서현 CAP-AI-43, 2026-11-08)
// 목적: design/circuit/firmware/trap_motion·trap_doors 의 .ino 를 고치지 않고 그대로 PC에서 컴파일해 시험.
// 승준 control/firmware/sim/Arduino.h 는 UNO 1개 v0.1 핀에 묶여 있어서 새로 만듦 (핀·세계는 sim_*.cpp 가 정함).
// 한계: PC의 int는 32비트 (AVR은 16비트) → 16비트 넘침 버그는 못 잡음. 시간은 100 µs 단위로 흐름.
#pragma once
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <cmath>
#include <cctype>
#include <cstdio>
#include <string>
#include <vector>
#include <functional>

typedef uint8_t byte;
#define F(x) (x)
#define A0 14
#define A1 15
#define A2 16
#define A3 17
#define A4 18
#define A5 19
#define OUTPUT 1
#define INPUT 0
#define INPUT_PULLUP 2
#define HIGH 1
#define LOW 0

// ---- 시간 ----
extern unsigned long g_us;                 // Windows에서 unsigned long 32비트 = AVR과 같음 (약 71분마다 넘침)
extern std::function<void()> g_world;      // 세계 갱신 (시간이 흐르거나 핀이 바뀔 때)
inline unsigned long micros() { return g_us; }
inline unsigned long millis() { return g_us / 1000UL; }
inline void delayMicroseconds(unsigned int) {}
inline void delay(unsigned long ms) { for (unsigned long i = 0; i < ms; i++) { g_us += 1000; if (g_world) g_world(); } }
inline void noInterrupts() {}
inline void interrupts() {}

// ---- 핀 ----
extern int g_pins[24];                     // 스케치가 쓴 값 (digitalWrite / analogWrite)
extern int g_pinmode[24];
extern std::function<int(int)> g_dread;    // 세계가 정함
extern std::function<int(int)> g_aread;
inline void pinMode(int p, int m) { g_pinmode[p] = m; }
extern std::function<void(int, int)> g_dwrite_hook;   // 쓰기마다 불림 (HX711 SCK 클럭 세기 등)
inline void digitalWrite(int p, int v) { g_pins[p] = v ? 1 : 0; if (g_dwrite_hook) g_dwrite_hook(p, v ? 1 : 0); }
inline void analogWrite(int p, int v) { g_pins[p] = v; }
inline int digitalRead(int p) { return g_dread ? g_dread(p) : g_pins[p]; }
inline int analogRead(int p) { return g_aread ? g_aread(p) : 0; }

template <class T> T constrain(T v, T a, T b) { return v < a ? a : (v > b ? b : v); }

// ---- 시리얼 ----
struct SerialLine { unsigned long t_us; std::string text; };
extern std::vector<SerialLine> g_lines;    // 스케치가 보낸 줄 (시각 포함)
struct SerialT {
  std::string in, cur;
  void begin(long) {}
  int available() { return (int)in.size(); }
  char read() { char c = in[0]; in.erase(0, 1); return c; }
  void put(const std::string& s) { cur += s; }
  void print(const char* s) { cur += s; }
  void print(char c) { cur += c; }
  void print(unsigned char v) { cur += std::to_string((int)v); }
  void print(int v) { cur += std::to_string(v); }
  void print(unsigned int v) { cur += std::to_string(v); }
  void print(long v) { cur += std::to_string(v); }
  void print(unsigned long v) { cur += std::to_string(v); }
  void print(double v, int d = 2) { char b[40]; snprintf(b, sizeof b, "%.*f", d, v); cur += b; }
  void nl() { g_lines.push_back({g_us, cur}); cur.clear(); }
  void println() { nl(); }
  template <class T> void println(T v) { print(v); nl(); }
  void println(double v, int d) { print(v, d); nl(); }
  void println(float v, int d) { print((double)v, d); nl(); }
};
extern SerialT Serial;

// 공통 정의 (한 번만, 각 sim_*.cpp 맨 위에서 SIM_DEFINE_GLOBALS 를 부름)
#define SIM_DEFINE_GLOBALS \
  unsigned long g_us = 0; std::function<void()> g_world; int g_pins[24]; int g_pinmode[24]; \
  std::function<int(int)> g_dread; std::function<int(int)> g_aread; std::function<void(int, int)> g_dwrite_hook; \
  std::vector<SerialLine> g_lines; SerialT Serial;
