# cad
FreeCAD 생성 스크립트(.py)와 모델(.FCStd), 도면 PDF. 담당: 서현. 모델은 스크립트로 만들고 치수는 design/의 설계 변수표에서 읽는다.

## D5e (현재 기준, 2026-11-01~02)
| 파일 | 무엇 |
|---|---|
| `D5e_전체조립도.png` | **한 장 조립도**: 등각·정면·측면·위·모듈 확대 + 2020 단면 + 부품 표 (`D5e_drawing_sheet.py`로 만듦) |
| `D5e_도1_전체_등각.png` ~ `D5e_도5_모듈_등각.png` | FreeCAD 정투영 렌더 5장 |
| `D5e_full_assembly.py` / `.FCStd` | 전체 조립: 2020 프로파일 프레임(T홈 단면, 기둥 610 × 4, 레일 320 × 21, L 브래킷 32) + 상용 트랩(실측표) + D5e 모듈 |
| `D5e_module_kinematic.py` / `.FCStd` | 움직이는 모듈 (스프레드시트 `Joints` 값을 바꾸면 움직임) |
| `D5e_check.py` / `D5e_check_result.json` | 이음부 86개·간섭 검사 |
| `D5e_animate.py`, `D5e_compose_video.py` → `D5e_동작_한마리처리.mp4`·`.gif` | 한 마리 처리 동영상 |

다시 만들기 (FreeCAD 1.x 파이썬 콘솔): `import sys; sys.path.insert(0, r"<repo>\cad"); import D5e_full_assembly as A; doc = A.make_full(); [A.render(doc, r"<repo>\cad", v) for v in A.VIEWS]` → `python3 cad/D5e_drawing_sheet.py cad`
