#include "Arduino.h"
#include <unistd.h>
#include <fcntl.h>
#include <chrono>
unsigned long g_us=0; long g_raw=0; int g_bit=0; int g_pins[20]; int g_servo[20]; SerialT Serial;
#include "../trap_controller/trap_controller.ino"
int main(){
  fcntl(0, F_SETFL, O_NONBLOCK);
  auto t0=std::chrono::steady_clock::now();
  setup();
  for(;;){
    char buf[256]; ssize_t n=read(0,buf,sizeof buf);
    if(n==0) break;
    if(n>0) Serial.in.append(buf,n);
    g_us=(unsigned long)std::chrono::duration_cast<std::chrono::microseconds>(std::chrono::steady_clock::now()-t0).count();
    if(g_bit>=25) g_bit=0;
    double mm=axes[0].pos/STEPS_PER_MM; g_raw=(long)(mm>2?(mm-2)*1000:0);
    loop();
    if(!Serial.out.empty()){ fwrite(Serial.out.data(),1,Serial.out.size(),stdout); fflush(stdout); Serial.out.clear(); }
    usleep(50);
  }
}
