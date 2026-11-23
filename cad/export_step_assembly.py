# 전체 조립 STEP 내보내기 (SolidWorks 제출용) — FreeCAD 1.1 매크로/파이썬 콘솔에서 실행
# 사용: FreeCAD에서 이 파일 실행 → 바탕화면 'capstone design\2026 창의융합 경진대회\말벌트랩_D5g_전체조립.step'
import os, FreeCAD as App, Import
SRC = os.path.expanduser(r'~\Desktop\capstone design\D5g_full_no.FCStd')
OUT = os.path.expanduser(r'~\Desktop\capstone design\2026 창의융합 경진대회\말벌트랩_D5g_전체조립.step')
doc = App.openDocument(SRC)
objs = [o for o in doc.Objects if hasattr(o, 'Shape') and not o.Shape.isNull() and o.TypeId.startswith('Part::')
        and getattr(o, 'Visibility', True) and not o.InList]  # 맨 위(다른 것에 안 쓰인) 보이는 몸체만
Import.export(objs, OUT)
print('STEP', len(objs), '개 →', OUT)
