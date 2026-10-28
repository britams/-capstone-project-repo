# 펌웨어 PC 시뮬레이션 (CAP-AI-SJ-19)
아두이노 없이 `trap_controller.ino`의 명령 처리를 PC에서 시험하기 위한 흉내 헤더(`Arduino.h`, `Servo.h`).
Linux/WSL/macOS: `g++ -std=c++17 -I. sim.cpp -o sim && ./sim` (명령 묶음 시험), `g++ -std=c++17 -I. sim2.cpp -o sim2 && python3 test_link.py` (실시간 + 파이썬 클라이언트).
하중 센서는 "바닥 2 mm부터 1 mm당 raw 1000 증가"로 흉내 냄. 실물 동작을 보장하지 않음.
