# VS Code에서 Claude Code로 실제 코드까지 — 시작 정리 (서현 PC)

정리: 2026-11-07 · 이서현 (Claude, **CAP-AI-39**)
목표: 지금까지 설계(회로·핀·제어 순서)를 **실제로 UNO에 올릴 펌웨어와 Pi 코드**로 만들고, 서현 PC에서 컴파일까지 확인한다.

## 0. 먼저 알아야 할 것 3가지
1. **[확실] PC의 `capstone design_이서현\repo\`는 git이 아니라 복사본이다.** 그래서 Claude Code는 거기서 commit·push를 할 수 없다.
   - → git 레포를 **새로 받는다**: `C:\capstone\-capstone-project-repo`
   - 영어·공백 없는 경로를 쓴다. Arduino 빌드는 한글·공백 경로에서 실패하는 일이 있다 [가능성 높음].
2. **[확실] `CLAUDE.md` 규칙상 `control/`(승준 펌웨어·Pi 코드)은 서현 세션이 고치지 않는다.** VS Code의 Claude도 이 파일을 읽고 같은 규칙을 따른다.
   - → 새 코드는 **서현 폴더 `design/circuit/firmware/`**에 만든다:
     - `trap_motion/` (UNO 1)
     - `trap_doors/` (UNO 2)
     - `pi_link/` (Pi)
   - 승준이 돌아와 동의하면 `control/`로 옮긴다.
   - 서현이 분업계획을 바꿔 펌웨어를 맡겠다고 정하면 `control/`를 바로 고쳐도 된다. 그때는 분업계획에 한 줄 적는다.
3. **실물 부품이 아직 없다.** 그래서 이번에 할 수 있는 것은 **컴파일 통과 + 시뮬레이션 통과**까지다.
   - UNO에 올리는 것(업로드)과 브링업 B1~B6 시험은 부품이 오면 한다.
   - 보유한 UNO·28BYJ-48·SG90으로 일부는 먼저 할 수 있다 (`design/2026-11-06_브레드보드_단계별_배선_서현.md` 7장).

## 1. 설치 (한 번만, PowerShell)
시작 메뉴에서 'PowerShell'을 열고 한 줄씩 붙여 넣는다. 이미 깔린 것은 건너뛴다.

```powershell
winget install Git.Git
winget install Microsoft.VisualStudioCode
winget install ArduinoSA.CLI
winget install Python.Python.3.12
irm https://claude.ai/install.ps1 | iex
```

- **설치가 끝나면 PowerShell을 닫고 새로 연다.** 그다음 아래 4개가 버전을 보여 주면 된다:
  - `git --version`
  - `code --version`
  - `arduino-cli version`
  - `claude --version`
- 마지막 줄은 Claude Code 프로그램(터미널용)이다. VS Code 확장만 쓸 거면 없어도 되지만, 문제가 생겼을 때 `claude doctor`로 원인을 볼 수 있어서 같이 깐다.
- Claude Code는 **유료 Claude 계정**(Pro·Max·Team·Enterprise)이 필요하다. 무료 계정은 안 된다.

## 2. 레포 받기
```powershell
mkdir C:\capstone
cd C:\capstone
git clone https://github.com/britams/-capstone-project-repo.git
cd -capstone-project-repo
git config user.name "이서현"
git config user.email "<GitHub에 등록한 메일>"
```
- 처음 `git push`를 하면 GitHub 로그인 창이 뜬다. britams 계정으로 로그인한다 (Git Credential Manager).

## 3. 아두이노 준비 (한 번만)
```powershell
arduino-cli core update-index
arduino-cli core install arduino:avr
arduino-cli lib install Servo
```
- 시험 컴파일: `arduino-cli compile --fqbn arduino:avr:uno design\circuit\bringup\b4_axis`
  - "Sketch uses … bytes"가 나오면 준비가 끝난 것이다.
- UNO를 USB로 꽂았을 때 포트 찾기: `arduino-cli board list` (예: COM3)
- 올리기: `arduino-cli upload -p COM3 --fqbn arduino:avr:uno <스케치 폴더>`

## 4. VS Code에서 Claude Code 열기
1. VS Code를 켠다 → **파일 > 폴더 열기** → `C:\capstone\-capstone-project-repo`. '이 폴더를 신뢰하시겠습니까'가 나오면 **예**.
2. `Ctrl+Shift+X` (확장) → **"Claude Code"** 검색 → Anthropic 것 **설치**.
3. 아무 파일이나 하나 연다 (예: `CLAUDE.md`). 오른쪽 위의 **Spark 아이콘(✻)**을 누른다.
   - 왼쪽 막대의 Spark 아이콘이나 `Ctrl+Shift+P` → "Claude Code"로도 열 수 있다.
4. 처음이면 **Sign in** → 브라우저에서 로그인.
5. 아래 5장 첫 메시지를 붙여 넣는다.

- 안 보이면 `Ctrl+Shift+P` → **Developer: Reload Window**.
- 터미널이 편하면 VS Code 아래 터미널(`` Ctrl+` ``)에서 `claude`를 쳐도 같다.

## 5. 첫 메시지 (그대로 붙여 넣기)

```
나는 이서현이야. CLAUDE.md 규칙대로 시작해 (읽는 순서 → 지금 상태·할 일·정할 것 짧게).

이번 세션 목표: 지금까지 설계를 실제로 쓸 코드로 만든다. 승준은 내가 말할 때까지 쉬고, control/는 승준 파일이니 고치지 말고 내 폴더 design/circuit/firmware/ 에 새로 만든다.

근거 문서 (이 순서로 읽어):
1. design/2026-11-06_펌웨어_변경요청_서현.md  ← 만들 것의 사양 (핀표, 명령, 문 닫기 안전 규칙)
2. design/2026-11-06_회로설계_서현.md, design/circuit/circuit.py  ← 핀의 원본 (검사 통과)
3. control/firmware/trap_controller/trap_controller.ino (v0.1)  ← 명령 형식·스테핑 코드는 이것을 바탕으로
4. design/circuit/bringup/b2~b5  ← 게이트·문 닫기·원점·HX711 시험 코드
5. design/control_sim/trap_sim.py  ← Pi 쪽 순서의 참고 구현 (24/24 PASS)
6. control/pi/trap_link.py, control/pi/daynight.py  ← Pi 쪽 기존 코드 (읽기만)
7. design/인터페이스_정의서.md 5차

할 일 (순서대로, 하나 끝날 때마다 컴파일·시험하고 commit·push):
A. design/circuit/firmware/trap_motion/trap_motion.ino — UNO 1: F·X·Y 스테핑(D2~D13), PEN A0, HX711 A1/A2, 원점 A3~A5 + HOME, HOLD F 기본 0, 서보 attach는 하나씩 0.3 s 간격, READY 이름 trap_motion
B. design/circuit/firmware/trap_doors/trap_doors.ino — UNO 2: 레일 감지 D2, 조명 D3·D5, 송신 D4, 문 서보 D9~D11, 통로 게이트 D7·D8·D12, 문 빔 A0~A5 아날로그, SELFTEST·GATES·EVT GATE·DOOR CLOSE 안전 규칙·LIGHT·EMIT·RAIL, READY 이름 trap_doors
C. 두 스케치 모두 arduino-cli compile --fqbn arduino:avr:uno 통과 (경고도 확인, 메모리 사용량 기록). 시뮬레이터(control/firmware/sim 방식)를 design/circuit/firmware/sim/에 복사해 시험 4개: HOME 스위치 못 찾음, 닫는 중 빔 끊김 → REOPEN·BLOCKED, SELFTEST FAIL → 닫기 거부, RAIL 0 → 문 명령 거부
D. design/circuit/firmware/pi_link/ — 두 포트를 READY 이름으로 구분하는 Pi 쪽 연결 코드 + 켤 때 순서(SELFTEST → RAIL → HOME F·X·Y), trap_sim의 순서를 실제 명령으로. 가짜 포트로 시험
E. 각 단계 끝에 ai-log/AI_명령사항_로그.md에 CAP-AI-40부터 항목, 커밋은 "[서현] …". 바뀐 파일은 PC 사본 C:\Users\Seohyun_Lee\Desktop\capstone design_이서현\repo\ 와 제어\ 폴더에도 복사 (제어\에는 20번부터 번호, 00_읽는순서.md에 추가)

모르는 값(서보 각도, 문턱값 등)은 지어내지 말고 #define으로 빼서 '미검증'이라고 적어. 확실하지 않으면 나한테 물어봐.
```

## 6. 일하는 방식 (VS Code Claude)
- Claude가 파일을 고치기 전에 **바뀐 부분(diff)을 보여 준다.** 처음에는 하나씩 'Accept'로 본다. 익숙해지면 자동 수락을 켠다.
- 명령(컴파일·git)을 실행할 때 허락을 묻는다. `arduino-cli`, `git`, `python`은 '항상 허용'으로 해도 된다.
- 사용량 90 %가 되면 `CLAUDE.md` 규칙대로 저장·push부터 한다.

## 7. 막힐 때
| 증상 | 할 것 |
|---|---|
| `claude`·`arduino-cli`가 없다고 나옴 | PowerShell을 닫고 새로 열기 (PATH 반영) |
| 컴파일 오류 `Servo.h: No such file` | `arduino-cli lib install Servo` |
| 업로드 `can't open device "COM3"` | 시리얼 모니터·다른 프로그램을 닫기, `arduino-cli board list`로 포트 다시 확인 |
| push 403 | GitHub 로그인 창에서 britams로 다시 로그인 |
| push rejected | `git pull --rebase` 뒤 다시 push (승준이 올린 것이 있을 때) |
| 확장이 안 보임 | `Ctrl+Shift+P` → Developer: Reload Window |

참고: Claude Code 설치 [code.claude.com/docs/en/setup](https://code.claude.com/docs/en/setup), VS Code 확장 [code.claude.com/docs/en/vs-code](https://code.claude.com/docs/en/vs-code)
