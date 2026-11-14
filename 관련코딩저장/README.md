# 관련코딩저장 — 펌웨어 시뮬레이터 + Pi 연결 코드 (서현, 2026-11-08)

VS Code Claude가 만든 코드 파일 (CAP-AI-44·45). 규칙(언제 무엇을 막는지)은 웹 채팅 Claude가 검토한다:
`design/2026-11-08_펌웨어v0.2_제어규칙_검토_서현.md`.

펌웨어(UNO에 올릴 것)는 원래 자리에 그대로 있다. Arduino는 스케치 폴더 이름이 파일 이름과 같아야 하고, 다른 문서가 이 경로를 가리킨다.
- `design/circuit/firmware/trap_motion/trap_motion.ino` — UNO 1
- `design/circuit/firmware/trap_doors/trap_doors.ino` — UNO 2

## 폴더
| 폴더 | 내용 |
|---|---|
| `sim/` | PC 시뮬레이터. **실제 .ino를 고치지 않고 그대로 `#include`** 해서 PC에서 컴파일한다. 흉내 헤더(`Arduino.h`, `Servo.h`)와 세계(코일 패턴 → 기계 위치, 원점 스위치, HX711 클럭, 빛 게이트 9개, 레일)로 구성된다 |
| `pi_link/` | Pi 쪽 코드: `uno_link.py`(UNO 한 대), `ports.py`(READY 이름으로 두 포트 가리기), `controller.py`(켤 때 순서·P1~P7). 시험 `test_pi_link.py`는 `sim/`의 서버 모드에 붙어 **실제 펌웨어 로직과 대화한다** |

## 돌리는 법 (서현 PC)
```powershell
# 한 번만: winget install zig.zig  (PC용 C++ 컴파일러, 11/08 설치함)
cd C:\capstone\-capstone-project-repo\관련코딩저장\sim
.\run_all.ps1                       # 빌드 + sim_motion 82개 + sim_doors 77개 시험
cd ..\pi_link
python test_pi_link.py              # 36개, 약 1분 (5배속)
```
- UNO 컴파일: `arduino-cli compile --fqbn arduino:avr:uno design\circuit\firmware\trap_motion` (trap_doors도 같다)
- 실물 Pi: `pip install pyserial` 뒤 `ports.open_serial_ports()` → `ports.identify()` → `controller.TrapController(...).boot()`

## 결과 (2026-11-08)
| 무엇 | 결과 |
|---|---|
| arduino-cli 컴파일 (경고 모두 켬) | trap_motion 11,968 B (37 %) / RAM 972 B (47 %) · trap_doors 10,956 B (33 %) / RAM 1,006 B (49 %) · 경고 0 |
| sim_motion | 82/82 — HOME 찾기·**스위치 못 찾음 NOSWITCH**·Y 58 mm(V6)·STUCK·펜 DOWN이면 X·Y 거부(V4)·**R1**·펜 2단계 ≤ 60 °/s(58.8)·걸음 잃음 EVT SWITCH(V5)·HOLD·SPEED 서지 띠·PRESS·STOP·WATCHDOG |
| sim_doors | 77/77 — 서보 하나씩·0.3 s·첫 펄스 = 열림 각도·**닫는 중 빔 끊김 REOPEN → BLOCKED**·WAIT 2 s·**SELFTEST FAIL → 닫기 거부**·**RAIL 0 → 문 명령 거부**·닫는 중 레일 끊김·EVT GATE 20 ms·EMIT 0·LIGHT·WATCHDOG |
| test_pi_link | 36/36 — 포트 순서를 바꿔도 READY로 가림·켤 때 순서·P1 G1 FAIL·P2 다시 시험(풀림/고장)·P3 밤/낮 순서·P4 레일 복귀·P5 PING으로 WATCHDOG 막기·P6 9번 뒤 STUCK·STATUS로 가림 |

## 시뮬레이터가 찾아서 고친 펌웨어 버그 2개 (웹 채팅 검토 필요)
1. **trap_doors: 문이 열리는 중(OPENING)에 같은 문 `DOOR CLOSE`를 보내면 그 문이 영영 busy로 굳음.** WAIT가 끝나면 `prev`인 OPENING으로 돌아가기 때문이다. → 같은 문의 CLOSE 겹치기는 `ERR BUSY` (OPEN으로 닫기 취소는 허용). 고치기 전 코드로 같은 시험을 돌리면 2개 FAIL → 버그가 실제로 있었다 [확실].
2. **trap_motion: 마지막 반걸음 코일을 같은 loop 안에서 켜자마자 끔.** 모터가 그 걸음을 돌 시간이 없다. → `COIL_OFF_DWELL_MS` 20 ms 뒤에 끈다. 승준 v0.1에도 같은 구조가 있다. 실물에서 위치가 쌓여 틀어지는지는 **미검증**이다 (반걸음 = 약 2 µm).

## Pi 코드가 스스로 정한 것 (웹 채팅 검토 필요)
- A1. `EVT RAIL 0`이면 UNO 1에 `STOP`. UNO 1은 레일을 못 보고, 모터 전원이 끊기면 걸음을 잃기 때문이다.
- A2. 대기 자리 X = +20 mm (펌웨어 좌표, 11/14 CAP-AI-62). CAD PARK (75, −40)에서 55를 뺀 값이다 (예전 65 → +10). 펌웨어 X 위 한계도 +18 → +20. **미검증**
- (11/14) 바닥 F = mightyZAP PWM: sim_motion 91/91 · sim_doors 89/89 · test_pi_link 36/36 · test_process 53/53 (Linux g++). **AVR 컴파일은 이번에 못 함 — PC에서 arduino-cli로 확인할 것**

## 한계
- PC의 `int`는 32비트이고 AVR은 16비트다 → 16비트 넘침은 못 잡는다. 시간은 100 µs 단위로 흐른다.
- 빛 세기(켬 820 / 끔 130), 서보 각도, 말벌 행동은 흉내 값이다. 실물 값은 브링업 B2~B5에서 잰다.
- 판정·촬영·마킹 순서(trap_sim `process()`)는 카메라 코드가 필요해서 넣지 않았다. 승준 비전 코드와 붙일 때 `controller.py` 위에 얹는다.
