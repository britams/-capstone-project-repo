#pragma once
extern int g_servo[20];
struct Servo { int pin=-1; void attach(int p){pin=p;} void write(int d){ if(pin>=0) g_servo[pin]=d; } };
