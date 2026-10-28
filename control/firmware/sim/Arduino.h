#pragma once
#include <cstdint>
#include <cstring>
#include <cstdlib>
#include <cmath>
#include <cctype>
#include <string>
#include <cstdio>
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
#define HIGH 1
#define LOW 0
extern unsigned long g_us;
extern long g_raw; extern int g_bit;
extern int g_pins[20];
inline unsigned long micros(){ return g_us; }
inline unsigned long millis(){ return g_us/1000; }
inline void pinMode(int,int){}
inline void digitalWrite(int p,int v){ g_pins[p]=v; if(p==A5 && v==1){ g_bit++; } }
inline int digitalRead(int p){ if(p==A4){ if(g_bit==0) return LOW; int idx=g_bit-1; if(idx>=24) return 0; return (g_raw>>(23-idx))&1; } return 0; }
inline void delayMicroseconds(int){}
inline void noInterrupts(){}
inline void interrupts(){}
template<class T> T constrain(T v,T a,T b){ return v<a?a:(v>b?b:v); }
struct SerialT {
  std::string in; std::string out;
  void begin(long){}
  int available(){ return (int)in.size(); }
  char read(){ char c=in[0]; in.erase(0,1); return c; }
  void print(const char* s){ out+=s; }
  void print(char c){ out+=c; }
  void print(long v){ out+=std::to_string(v); }
  void print(float v,int d){ char b[32]; snprintf(b,32,"%.*f",d,v); out+=b; }
  void println(const char* s){ out+=s; out+="\n"; }
  void println(long v){ out+=std::to_string(v); out+="\n"; }
  void println(float v,int d){ print(v,d); out+="\n"; }
};
extern SerialT Serial;
