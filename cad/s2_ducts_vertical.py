# -*- coding: utf-8 -*-
"""통로 관 110·172 수직으로 (서현 11/17 10:26 "이거 수직 위로 되는거 맞아? 수직 아니면 수직으로", CAP-AI-62)
  [확실 — CAD] 지금 110 입구 관은 4.0°, 172 격리 관은 2.5° 기울어 있었음 (11/15 s2_doors_swap: 깔때기 목은 트랩 축 (0, 0), 문 묶음은 y ±9라서
  하우징 꺾임을 문 축 둘레로 돌려 관을 비스듬히 이음).
  → 하우징 112의 꺾임 2개를 그때 돌린 만큼 되돌려 (입구 +4.43° · 축 (y 9, z 376.5), 격리 +2.47° · 축 (y −9, z 376.5)) 소켓을 수직으로,
    관 110은 (0, 9), 172는 (1.5, −9)에 수직, 깔때기 111·173은 넓은 끝(데크·위판 쪽)은 그대로 두고 목만 9 mm 옮긴 비스듬한 깔때기
    (데크 구멍·위판 구멍·UNO 2를 안 건드리려고 — 깔때기를 통째로 옮기면 111이 UNO 2와 겹침)
한 번만 — 다시는 split/S2_마킹부_before_vert.FCStd에서. GUI FreeCAD에서 exec 가능 (os._exit 없음) → split/_ducts_vertical.json"""
import json, os, sys, shutil, traceback, glob, time, math
import FreeCAD as App, Part
HERE = r"C:\capstone\-capstone-project-repo\cad"; OUT = os.path.join(HERE, "split")
DESK = r"C:\Users\Seohyun_Lee\Desktop\capstone design\주문제작 파일\프린트_5개_최종"
V = App.Vector; ex = V(1, 0, 0)
A_E = math.degrees(math.atan2(9.0, 376.5 - 13.0 - 247.4))     # s2_doors_swap에서 입구 꺾임을 돌린 각
A_I = math.degrees(math.atan2(9.0, 585.0 - 376.5))            # 격리 꺾임
rep = dict(a_entry=round(A_E, 3), a_iso=round(A_I, 3))


def _save(doc, path):                               # 저장 잠김이면 임시 파일을 바꿔 넣음 (fix_screw_clash와 같음)
    try:
        doc.save(); return
    except OSError:
        pass
    tmp = sorted(glob.glob(path + ".*-*"), key=os.path.getmtime)[-1]
    for _ in range(60):
        try:
            os.replace(tmp, path); return
        except OSError:
            time.sleep(2)
    raise OSError("replace failed " + tmp)


def cyl(r, h, p, d=V(0, 0, 1)):
    return Part.makeCylinder(r, h, p, d)


def shear_y(sh, k, z0):                            # y' = y + k (z − z0): 가로 단면 원은 원 그대로 → 비스듬한 원뿔
    m = App.Matrix(); m.A23 = k; m.A24 = -k * z0
    return sh.transformGeometry(m)


def sockets(sh):
    return [f for f in sh.Faces if "Cylinder" in f.Surface.TypeId and abs(f.Surface.Radius - 9.15) < 0.05]


try:
    P, B = os.path.join(OUT, "S2_마킹부.FCStd"), os.path.join(OUT, "S2_마킹부_before_vert.FCStd")
    shutil.copy(B, P) if os.path.exists(B) else shutil.copy(P, B)
    d = App.openDocument(P, True)
    ob = lambda p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)][0]
    # 1) 하우징 꺾임 되돌리기
    h = ob("112_entry_iso_gate_housing"); H = h.Shape
    cut = Part.makeBox(30, 140, 100, V(-17, -70, 330))           # x −17~13 = 꺾임 두 개만 (몸은 x 13.5부터)
    left = sorted(H.common(cut).Solids, key=lambda s: s.BoundBox.ZMin)
    assert len(left) == 2, len(left)
    ent, iso = left[0].copy(), left[1].copy()
    ent.rotate(V(0, 9.0, 376.5), ex, A_E); iso.rotate(V(0, -9.0, 376.5), ex, A_I)
    Hn = H.cut(cut).fuse(ent).fuse(iso).removeSplitter()
    h.Shape = Hn
    soc = sockets(Hn)
    rep["sockets"] = [[round(f.Surface.Axis.x, 4), round(f.Surface.Axis.y, 4), round(f.Surface.Axis.z, 4), round(f.Surface.Center.x, 2), round(f.Surface.Center.y, 2),
                       round(f.BoundBox.ZMin, 2), round(f.BoundBox.ZMax, 2)] for f in soc]
    se = [f for f in soc if f.BoundBox.ZMax < 370][0]; si = [f for f in soc if f.BoundBox.ZMin > 380][0]
    assert abs(abs(se.Surface.Axis.z) - 1) < 1e-4 and abs(abs(si.Surface.Axis.z) - 1) < 1e-4
    ce = V(se.Surface.Center.x, se.Surface.Center.y, 0); ci = V(si.Surface.Center.x, si.Surface.Center.y, 0)
    z_top_e = se.BoundBox.ZMax; z_bot_i = si.BoundBox.ZMin
    h.Label = h.Label.split(" (11/17")[0] + " (11/17 꺾임 소켓 수직 — 관 110·172 수직)"
    # 2) 관
    Fz = 248.5; Gz = 584.4
    t = ob("110_entry_duct")
    Le = z_top_e - Fz
    t.Shape = cyl(9.0, Le, V(ce.x, ce.y, Fz)).cut(cyl(7.0, Le, V(ce.x, ce.y, Fz)))
    t.Label = "110_entry_duct (아크릴 파이프 바깥 18 · 안 14 — DKD아크릴 맞춤 절단 %.1f mm, 수직 (x %.1f, y %.1f) — 11/17 기울기 4° → 0)" % (Le, ce.x, ce.y)
    t = ob("172_isolation_duct")
    Li = Gz - z_bot_i
    t.Shape = cyl(9.0, Li, V(ci.x, ci.y, z_bot_i)).cut(cyl(7.0, Li, V(ci.x, ci.y, z_bot_i)))
    t.Label = "172_isolation_duct (아크릴 파이프 바깥 18 · 안 14 — DKD아크릴 맞춤 절단 %.1f mm, 수직 (x %.1f, y %.1f) — 11/17 기울기 2.5° → 0)" % (Li, ci.x, ci.y)
    rep["len"] = dict(d110=round(Le, 2), d172=round(Li, 2), c110=[round(ce.x, 2), round(ce.y, 2)], c172=[round(ci.x, 2), round(ci.y, 2)])
    # 3) 깔때기: 넓은 끝 그대로, 목만 관 축으로 (s2_gates_funnels_feed와 같은 소켓 꼴)
    f = ob("111_entry_funnel")
    cone = shear_y(f.Shape.common(Part.makeBox(80, 80, 36.2, V(-40, -40, 200))), ce.y / 31.2, 205.0)
    E = V(ce.x, ce.y, Fz)
    b = cone.fuse(cyl(11, E.z + 1.5 - 236.2, V(ce.x, ce.y, 236.2))).fuse(cyl(11, 11, V(ce.x, ce.y, E.z - 0.5)))
    f.Shape = b.cut(cyl(7, 30, V(ce.x, ce.y, 230))).cut(cyl(9.15, 20, E)).removeSplitter()
    f.Label = f.Label.split(" (11/17")[0] + " (11/17 목을 관 110 축 y %.1f로 — 아래 넓은 끝은 데크 구멍 위 그대로, 비스듬한 깔때기)" % ce.y
    f = ob("173_isolation_funnel")
    cone = f.Shape.common(Part.makeBox(80, 80, 40, V(-40, -40, 596.2)))
    cone = shear_y(cone, ci.y / (596.2 - 620.0), 620.0)           # z 596.2에서 y가 ci.y만큼 (−9)
    E = V(ci.x, ci.y, Gz)
    b = cone.fuse(cyl(11, 596.2 - (E.z + 0.5) + 0.01, V(ci.x, ci.y, E.z + 0.5))).fuse(cyl(11, 11, V(ci.x, ci.y, E.z + 0.5), V(0, 0, -1)))
    b = b.cut(cyl(7, 23, V(ci.x, ci.y, 575))).cut(cyl(9.15, 20, E, V(0, 0, -1)))
    f.Shape = b.cut(Part.makeBox(60, 60, 15.5, V(-28, -30, 560))).removeSplitter()
    f.Label = f.Label.split(" (11/17")[0] + " (11/17 목을 관 172 축 y %.1f로 — 위 넓은 끝은 위판 구멍 그대로, 비스듬한 깔때기)" % ci.y
    for p in ("111_entry_funnel", "173_isolation_funnel", "112_entry_iso_gate_housing"):
        rep[p[:3] + "_valid"] = [ob(p).Shape.isValid(), len(ob(p).Shape.Solids)]
    d.recompute(); _save(d, P)
    # 4) STL (레포 print/3d + 바탕화면)
    import MeshPart
    for p, nm in (("111_entry_funnel", "111_입구깔때기"), ("112_entry_iso_gate_housing", "112_입구격리문하우징"), ("173_isolation_funnel", "173_격리깔때기")):
        m = MeshPart.meshFromShape(Shape=ob(p).Shape, LinearDeflection=0.05, AngularDeflection=0.3)
        fn = os.path.join(HERE, "print", "3d", nm + ".stl"); m.write(fn)
        try:
            shutil.copy(fn, os.path.join(DESK, nm + ".stl"))
        except Exception as e:
            rep["desk_" + nm] = str(e)
        rep["stl_" + nm] = dict(solid=m.isSolid(), vol_cm3=round(ob(p).Shape.Volume / 1000, 2))
    # 5) 정지 겹침: 바뀐 것 ↔ 전부
    every = []
    for ff in ("S1_급이부", "S2a_바닥구동", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, ff + ".FCStd"), True)
        every += [(ff[:3] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(dd.Name)
    every += [("S2_ " + o.Label, o.Shape.copy()) for o in d.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
    CH = ("110_entry_duct", "172_isolation_duct", "111_entry_funnel", "173_isolation_funnel", "112_entry_iso_gate_housing")
    ok = (("110_entry_duct", "111_entry"), ("110_entry_duct", "112_entry_iso"), ("172_isolation_duct", "112_entry_iso"), ("172_isolation_duct", "173_iso"))
    hits = []
    for la, sa in every:
        ta = la.split(" ", 1)[1]
        if not ta.startswith(CH):
            continue
        for lb, sb in every:
            tb = lb.split(" ", 1)[1]
            if la == lb or (tb.startswith(CH) and lb < la):
                continue
            if any(ta.startswith(p) and tb.startswith(q) or ta.startswith(q) and tb.startswith(p) for p, q in ok):
                continue
            try:
                if sa.BoundBox.intersect(sb.BoundBox):
                    v = sa.common(sb).Volume
                    if v > 0.05:
                        hits.append([ta[:40], tb[:40], round(v, 1)])
            except Exception:
                pass
    rep["hits"] = hits
    # 관이 소켓에 맞는지: 관 ↔ 깔때기·하우징 겹침이 0이어야 (소켓 Ø18.3 > 관 Ø18)
    rep["fit"] = {k: round(ob(a).Shape.common(ob(b_).Shape).Volume, 3) for k, a, b_ in
                  (("110-111", "110_entry_duct", "111_entry_funnel"), ("110-112", "110_entry_duct", "112_entry_iso"),
                   ("172-112", "172_isolation_duct", "112_entry_iso"), ("172-173", "172_isolation_duct", "173_isolation_funnel"))}
    App.closeDocument(d.Name)
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_ducts_vertical.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps(rep, ensure_ascii=False)[:3000])
