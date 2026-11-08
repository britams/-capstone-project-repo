// sim_common.h — 시험 보조 (서현 CAP-AI-43). 스케치와 이름이 겹치지 않게 t_ 로 시작.
#pragma once
#include <thread>
#include <mutex>
#include <deque>
#include <chrono>
#include <iostream>
static int t_pass = 0, t_fail = 0;
#define CHECK(cond, msg) do { bool _ok = (cond); if (_ok) t_pass++; else t_fail++; \
  printf("  [%s] %s\n", _ok ? "PASS" : "FAIL", msg); } while (0)

// ms 만큼 스케치 loop()를 돌린다 (100 µs 간격)
static void t_run(unsigned long ms) {
  for (unsigned long i = 0; i < ms * 10UL; i++) { g_us += 100; if (g_world) g_world(); loop(); if (g_world) g_world(); }
}
static size_t t_mark() { return g_lines.size(); }
static void t_send(const char* c) { Serial.in += c; Serial.in += "\n"; }
static int t_find(size_t from, const char* sub) {
  for (size_t i = from; i < g_lines.size(); i++) if (g_lines[i].text.find(sub) != std::string::npos) return (int)i;
  return -1;
}
static bool t_has(size_t from, const char* sub) { return t_find(from, sub) >= 0; }
// sub 가 담긴 줄이 나올 때까지 최대 max_ms 돌림 (10 ms 단위)
static bool t_wait(size_t from, const char* sub, unsigned long max_ms) {
  for (unsigned long t = 0; t <= max_ms; t += 10) { if (t_has(from, sub)) return true; t_run(10); }
  return t_has(from, sub);
}
// 명령을 보내고 반응 줄이 나올 때까지 (기본 500 ms)
static size_t t_cmd(const char* c, unsigned long ms = 100) { size_t m = t_mark(); t_send(c); t_run(ms); return m; }
static std::string t_dump(size_t from) {
  std::string s;
  for (size_t i = from; i < g_lines.size(); i++) { char b[32]; snprintf(b, sizeof b, "      %8.3f  ", g_lines[i].t_us / 1e6); s += b; s += g_lines[i].text; s += "\n"; }
  return s;
}
// prefix 로 시작하는 마지막 줄 뒤의 숫자 (예: "DONE MOVE F " → 19.999). 없으면 NAN
static double t_value(size_t from, const char* prefix) {
  for (size_t i = g_lines.size(); i > from; i--) {
    size_t p = g_lines[i - 1].text.find(prefix);
    if (p != std::string::npos) return atof(g_lines[i - 1].text.c_str() + p + strlen(prefix));
  }
  return NAN;
}
static bool t_near(double a, double b, double tol) { return std::fabs(a - b) <= tol; }
static double t_time(int idx) { return g_lines[idx].t_us / 1e6; }
static int t_summary(const char* name) {
  printf("\n== %s: PASS %d, FAIL %d\n", name, t_pass, t_fail);
  return t_fail ? 1 : 0;
}

// ---- 서버 모드: Pi 쪽 파이썬 코드가 실제 .ino 로직에 붙어 시험하도록 표준 입출력을 시리얼로 쓴다 ----
// 시간은 벽시계 × speed 로 흐른다. '#'로 시작하는 줄은 시리얼이 아니라 세계(고장 주입) 명령이다.
static int t_serve(double speed, std::function<void(const std::string&)> control) {
  std::deque<std::string> q; std::mutex mu; bool eof = false;
  std::thread rd([&]() { std::string l; while (std::getline(std::cin, l)) { if (!l.empty() && l.back() == '\r') l.pop_back(); std::lock_guard<std::mutex> g(mu); q.push_back(l); }
                         std::lock_guard<std::mutex> g(mu); eof = true; });
  rd.detach();
  setup();
  size_t printed = 0;
  auto flush = [&]() { while (printed < g_lines.size()) { std::string o = g_lines[printed++].text + "\n"; fwrite(o.data(), 1, o.size(), stdout); } fflush(stdout); };
  flush();
  const unsigned long base = g_us;
  auto t0 = std::chrono::steady_clock::now();
  for (;;) {
    { std::lock_guard<std::mutex> g(mu);
      while (!q.empty()) { std::string l = q.front(); q.pop_front();
        if (!l.empty() && l[0] == '#') control(l); else { Serial.in += l; Serial.in += "\n"; } }
      if (eof && q.empty()) break; }
    double us = std::chrono::duration<double, std::micro>(std::chrono::steady_clock::now() - t0).count() * speed;
    unsigned long target = base + (unsigned long)us;
    int guard = 0;
    while (g_us + 100 <= target && guard++ < 20000) { g_us += 100; if (g_world) g_world(); loop(); if (g_world) g_world(); }
    flush();
    std::this_thread::sleep_for(std::chrono::microseconds(300));
  }
  return 0;
}
