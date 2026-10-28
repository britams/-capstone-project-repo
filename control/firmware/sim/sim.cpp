#include "Arduino.h"
unsigned long g_us=0; long g_raw=0; int g_bit=0; int g_pins[20]; int g_servo[20]; SerialT Serial;
#include "../trap_controller/trap_controller.ino"
// HX711 simulation: each read consumes 25 SCK pulses; reset bit counter when g_bit reaches 25
void tick(unsigned long us){ for(unsigned long t=0;t<us;t+=100){ g_us+=100; if(g_bit>=25) g_bit=0; loop(); } }
std::string cmd(const char* c, unsigned long run_us=20000){ Serial.out.clear(); Serial.in+=c; Serial.in+="\n"; tick(run_us); return Serial.out; }
int main(){
  setup(); printf("%s", Serial.out.c_str());
  printf("%s", cmd("ping").c_str());
  printf("%s", cmd("MOVE X 1.0", 1200000).c_str());   // ~510 steps at 1000us -> 0.51 s
  printf("%s", cmd("STATUS").c_str());
  printf("%s", cmd("MOVE X 30").c_str());              // limit
  printf("%s", cmd("MOVE Q 1").c_str());
  // parallel X & Y
  Serial.out.clear(); Serial.in+="MOVE X -1\nMOVE Y -0.5\n"; tick(1500000); printf("%s", Serial.out.c_str());
  // press: raw rises with floor position: simulate load = 0 until 2mm then 1000 raw per mm
  printf("%s", cmd("CAL 0.1").c_str());
  printf("%s", cmd("TARE").c_str());
  Serial.out.clear(); Serial.in+="PRESS 50 10\n";
  for(int k=0;k<200000;k++){ double mm=axes[0].pos/STEPS_PER_MM; g_raw = (long)(mm>2? (mm-2)*1000:0); g_us+=100; if(g_bit>=25) g_bit=0; loop(); if(Serial.out.find("DONE PRESS")!=std::string::npos) break; }
  printf("%s", Serial.out.c_str());
  printf("%s", cmd("DOOR CAP OPEN").c_str()); printf("servo CAP(A1)=%d\n", g_servo[A1]);
  printf("%s", cmd("PEN DOWN").c_str()); printf("servo PEN(A3)=%d\n", g_servo[A3]);
  printf("%s", cmd("SETDOOR PEN 70 5").c_str()); printf("%s", cmd("PEN UP").c_str()); printf("servo PEN=%d\n", g_servo[A3]);
  printf("%s", cmd("WATCHDOG 0.5").c_str()); Serial.out.clear(); tick(700000); printf("%s", Serial.out.c_str());
  printf("%s", cmd("FOO").c_str());
  printf("%s", cmd("STATUS").c_str());
}
