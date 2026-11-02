# control_sim — 전기 계산과 제어 순서 시뮬레이션 (서현, 2026-11-02, CAP-AI-22)

설명 문서: `design/2026-11-02_전기계통_제어순서_서현.md`

| 파일 | 하는 일 |
|---|---|
| `elec_budget.py` | 부품 전류표(근거 표시), 상태별 전류·전력, 최대 전류·퓨즈, 전선 강하, D5e 좌표로 배선 길이, 하루 에너지, `HOLD F` 검토 → `out/elec_results.json` |
| `trap_sim.py` | Pi 상태 머신 참고 구현(`PiFSM`) + 가짜 UNO 1·UNO 2·카메라·말벌. 시나리오 19개와 안전 규칙 5개 검사 + 빔 하나 비교 → `out/sim_results.json`, `out/S1_timeline.json` |
| `make_figs.py` | 그림 4장 → `design/img/control/` (배선도, S1 시간표, 상태도, 메시지 순서) |

실행 순서 (Python 3.10 이상, matplotlib; 상태도는 graphviz `dot`, 메시지 순서는 `mmdc`가 있어야 함):

```
python design/control_sim/elec_budget.py
python design/control_sim/trap_sim.py            # 19개 모두 + 빔 하나 비교
python design/control_sim/trap_sim.py S1_nominal # 하나만 + 메시지 기록
python design/control_sim/make_figs.py
```

- 실제 하드웨어 코드가 아니다. Pi 코드를 짤 때 `PiFSM`의 순서·시간 제한·고장 처리를 옮겨 쓰고, 시리얼 부분만 pyserial(승준 `control/pi/trap_link.py`)로 바꾼다.
- 가짜 UNO 2의 명령은 **제안**이다. 승준 펌웨어는 고치지 않았다 (GitHub Issue 참고).
- 시간값 대부분은 [추측]이다 (`PRM` 맨 위). J6·행동 시험 뒤 바꾸고 다시 돌린다.
