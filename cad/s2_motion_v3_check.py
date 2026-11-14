# -*- coding: utf-8 -*-
"""전체 수정 4단계 검사: 마커가 움직일 때 새 마킹실·문·격리 관·컵 받침과 부딪히는지 (서현 11/14 21:06 "다음에 할거 해", CAP-AI-62)
  freecad.exe cad/s2_motion_v3_check.py (cwd = cad) → split/_motion_v3.json
마커 범위: X 원점 xm 37 ~ 대기 75, Y 대기 ym −40 ~ +16 (격자 끝 13.2 + 여유). 대기 자세(75, −40)에서도 이미 겹친 쌍은 '원래'로 따로 셈.
움직이는 것: XY 둘 다 = 펜·홀더·Z 서보·Y 캐리지·Y 베어링·안내 핀·Y 너트 / X만 = Y 봉·Y 리드·Y 모터·커플링·브래킷·빔 끝 블록·X 베어링·X 너트·Y 원점 스위치
"""
import json, os, sys, traceback
HERE = os.getcwd()
sys.path.insert(0, HERE)
OUT = os.path.join(HERE, "split")
XY = ("201_", "202_", "203_", "204_", "205", "206_", "221_", "223_", "224_")
XO = ("207_", "208_", "209", "210_", "211_", "212_", "222_", "225_", "227y", "153b_", "153n_")
PARK = (75.0, -40.0)
XS = (37.0, 46.0, 55.0, 64.0, 75.0)
YS = (-40.0, -28.0, -14.0, 0.0, 16.0)
rep = dict(ok=False)
try:
    import FreeCAD as App
    V = App.Vector
    objs = []
    for f in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        d = App.openDocument(os.path.join(OUT, f + ".FCStd"), True)
        for o in d.Objects:
            if o.TypeId.startswith("Part::"):
                try:
                    if o.Shape.isNull() or o.Shape.Volume <= 0 or o.Label.startswith("REF_"):
                        continue
                except Exception:
                    continue
                lab = o.Label
                kind = "xy" if lab.startswith(XY) else ("x" if lab.startswith(XO) and ("[marker]" in lab or not lab.startswith(("153b_", "153n_"))) else "fix")
                objs.append((f[:2] + " " + lab[:55], kind, o.Shape.copy()))
        App.closeDocument(d.Name)
    mov = [o for o in objs if o[1] != "fix"]
    fix = [o for o in objs if o[1] == "fix"]
    rep["n"] = dict(moving=len(mov), fixed=len(fix))

    def hits(dx, dy):
        out = {}
        for la, k, sa in mov:
            s = sa.copy()
            s.translate(V(dx, dy if k == "xy" else 0, 0))
            for lb, _, sb in fix:
                if s.BoundBox.intersect(sb.BoundBox):
                    v = s.common(sb).Volume
                    if v > 0.05:
                        out[(la, lb)] = round(v, 1)
        return out
    base = hits(0, 0)
    rep["park_overlaps"] = [list(k) + [v] for k, v in base.items()]
    new = {}
    for x in XS:
        for y in YS:
            for k, v in hits(x - PARK[0], y - PARK[1]).items():
                if v > base.get(k, 0) + 0.5 and (k not in new or v > new[k][0]):
                    new[k] = (v, x, y)
    rep["motion_new"] = [list(k) + list(v) for k, v in new.items()]
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
with open(os.path.join(OUT, "_motion_v3.json"), "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
