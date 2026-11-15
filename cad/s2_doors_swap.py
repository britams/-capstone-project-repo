# -*- coding: utf-8 -*-
"""입구·격리 문 둘 다 −x 벽으로 → 격리 통로 다시 '일자' (서현 11/15 17:45 "일자로 벌이 움직이는 거리가 길지 않게 바꿔", CAP-AI-62)
  상자 300: −x 벽에 Ø13 구멍 2개 나란히 (입구 y +9 · 격리 y −9, 축 z 376.5), −y 격리 구멍 없앰 (lift_v2 BOXD mx_y)
  입구: 문 묶음 (112·G2·서보 나사) y +9. 세로 PVC 110은 깔때기 목 (0, 0)에서 4° 기울여 꺾임 110b로 — 110b는 문 축(x 방향) 둘레로 돌려 출구는 그대로 +x
  격리: 11/14 −y 길 (PVC 4토막 + 꺾임 3, y −135 · z 557)을 빼고 옛 D5e 길로: 문 묶음 (170·G3) y −9 · z −0.5,
        꺾임 172b (−x → 위) + 세로 PVC 172 (x 1.5)가 깔때기 173 (1.5, 0)까지 2.5° 기울어 곧게 (옛 길 그대로, 문 y −9만큼)
  ULN 받침 Y (S3, −x 갠트리 레일 y −18~34)가 새 세로 관과 겹침 → 같은 레일 y −150~−98로 (기판·기둥·나사 함께)
  입구 문 하우징은 y < 0, 격리 문 하우징은 y > 0 쪽을 0.5씩 깎음 (나란히 붙어서) — 문 하우징은 3단계에서 사는 것으로
한 번만 (다시는 split/*_before_swap.FCStd에서). freecad.exe cad/s2_doors_swap.py (cwd = cad) → split/S2·S3, split/_doors_swap.json"""
import json, os, sys, traceback, glob, time, math
HERE = os.getcwd(); OUT = os.path.join(HERE, "split"); sys.path.insert(0, HERE)
rep = dict(hits=[])


def _save(doc, path):
    try:
        doc.save(); App.closeDocument(doc.Name); return
    except OSError:
        pass
    App.closeDocument(doc.Name)
    tmp = sorted(glob.glob(path + ".*-*"), key=os.path.getmtime)[-1]
    for _ in range(60):
        try:
            os.replace(tmp, path); return
        except OSError:
            time.sleep(2)
    raise OSError("replace failed " + tmp)


try:
    import FreeCAD as App, Part
    import lift_v2 as L
    import lift_v3 as L3
    import D5e_module_kinematic as K
    V = App.Vector
    OY, ZD = 9.0, 376.5
    ex = V(1, 0, 0)

    def mv(sh, v):
        t = sh.copy(); t.translate(v); return t

    def rotx(sh, y0, z0, deg):
        t = sh.copy(); t.rotate(V(0, y0, z0), ex, deg); return t

    cur = App.openDocument(os.path.join(OUT, "S2_마킹부.FCStd"))
    old = App.openDocument(os.path.join(OUT, "S2_마킹부_before_v3.FCStd"), True)
    ob = lambda d, p: [o for o in d.Objects if o.TypeId.startswith("Part::") and o.Label.startswith(p)]
    # 1) 상자
    mw = App.Matrix(); mw.move(L3.WORLD)
    for o in ob(cur, "300_marking_box"):
        o.Shape = L.marking_box().transformed(mw)
    # 2) 입구
    for p in ("112_entry_gate", "196_gate_G2"):
        for o in ob(cur, p):
            o.Shape = mv(o.Shape, V(0, OY, 0))
    for o in ob(cur, "112s_gate_servo_screws"):
        if "[entry]" in o.Label:
            o.Shape = mv(o.Shape, V(0, OY, 0))
    for o in ob(cur, "112_entry_gate_housing"):
        o.Shape = o.Shape.cut(K.box(-50, 100, -100, 0.0, 300, 450))
    a = math.atan2(OY, ZD - 13.0 - 247.4)                          # 깔때기 목 (0, 0, 247.4) → 꺾임 입구
    s, c = math.sin(a), math.cos(a)
    for o in ob(cur, "110b"):
        o.Shape = rotx(mv(o.Shape, V(0, OY, 0)), OY, ZD, -math.degrees(a))
    F = V(0, 0, 248.5)                                             # 깔때기 목 위 1.1 (기울어서 목 안쪽에 안 박히게 — 이음은 열수축관 111h)
    Lp = (ZD - 13.0 - 247.4) / c - 0.0
    T = V(0, OY - 13.0 * s, ZD - 13.0 * c)
    for o in ob(cur, "110_entry_duct"):
        o.Shape = K.tube(9.0, 6.5, (T - F).Length, F, (T - F).normalize())
        o.Label = "110_entry_duct (수도용 PVC 13A — 바깥 18·안 13, %d mm 자름, 4° 기울어 깔때기 목 → 꺾임 110b, 11/15)" % round((T - F).Length)
    rep["entry"] = dict(deg=round(math.degrees(a), 2), L=round((T - F).Length, 1))
    # G1 빛 게이트 (관 둘레 안장 받침·센서·나사, z ~275)도 기운 관을 따라 y로
    def y_at(z):
        return F.y + (z - F.z) * math.tan(a)
    for o in ob(cur, "196_gate_G1") + ob(cur, "199d_gate_holder_G1") + ob(cur, "199e_gate_holder_G1"):
        o.Shape = mv(o.Shape, V(0, y_at(o.Shape.BoundBox.Center.z), 0))
    for o in ob(cur, "199s_gate_screws"):
        if "[iso" not in o.Label:
            o.Shape = Part.makeCompound([mv(x, V(0, y_at(x.BoundBox.Center.z), 0)) if abs(x.BoundBox.Center.x) < 30 and abs(x.BoundBox.Center.y) < 30 and x.BoundBox.Center.z < 330 else x.copy() for x in o.Shape.Solids])
    # 3) 격리: 11/14 −y 묶음 빼고 옛 −x 묶음
    for p in ("170_isolation_gate", "196_gate_G3", "172_isolation_duct", "172b_isolation", "196_gate_G4", "199b_gate_holder_G4"):
        for o in ob(cur, p):
            cur.removeObject(o.Name)
    for o in ob(cur, "112s_gate_servo_screws") + ob(cur, "199s_gate_screws"):
        if "[iso]" in o.Label or "[iso_duct]" in o.Label:
            cur.removeObject(o.Name)
    b = math.atan2(OY, 585.0 - ZD)
    sb, cb = math.sin(b), math.cos(b)
    ISO = V(0, -OY, -0.5)
    yG4 = -OY + (560.0 - ZD) * math.tan(b)
    add = []
    for o in old.Objects:
        if not o.TypeId.startswith("Part::"):
            continue
        lb = o.Label
        if lb.startswith(("170_isolation_gate", "196_gate_G3")):
            sh = mv(o.Shape, ISO)
            if lb.startswith("170_isolation_gate_housing"):
                sh = sh.cut(K.box(-50, 100, 0.0, 100, 300, 450))
            add.append((lb, sh))
        elif lb.startswith("172b_isolation_bend"):
            add.append((lb + " [11/15 문 y −9, 2.5° 돌림]", rotx(mv(o.Shape, ISO), -OY, ZD, -math.degrees(b))))
        elif lb.startswith(("196_gate_G4", "199b_gate_holder_G4")):
            add.append((lb, mv(o.Shape, V(0, yG4, -0.5))))
        elif lb.startswith("112s_gate_servo_screws"):
            ss = [x for x in o.Shape.Solids if x.BoundBox.Center.z > 365 and x.BoundBox.Center.x < 50]
            add.append((lb + " [iso]", mv(Part.makeCompound(ss), ISO)))
        elif lb.startswith("199s_gate_screws"):
            ss = [x for x in o.Shape.Solids if x.BoundBox.Center.z > 540]
            if ss:
                add.append((lb + " [iso_duct]", mv(Part.makeCompound(ss), V(0, yG4, -0.5))))
    T2 = V(1.5, -OY + 13.0 * sb, ZD + 13.0 * cb)
    G = V(1.5, 0, 584.0)                                           # 깔때기 173 목 아래 1 (같은 이유, 열수축관 173h)
    add.append(("172_isolation_duct (수도용 PVC 13A — 바깥 18·안 13, %d mm 자름, 꺾임 172b → 깔때기 173 곧게 2.5°, 11/15 옛 길로)" % round((G - T2).Length),
                K.tube(9.0, 6.5, (G - T2).Length, T2, (G - T2).normalize())))
    rep["iso"] = dict(deg=round(math.degrees(b), 2), L=round((G - T2).Length, 1), y_G4=round(yG4, 2))
    App.closeDocument(old.Name)
    for lb, sh in add:
        n = cur.addObject("Part::Feature", "SW_%d" % len(cur.Objects))
        n.Shape, n.Label = sh, lb
    _save(cur, os.path.join(OUT, "S2_마킹부.FCStd"))
    # 4) S3: ULN Y → −x 레일 y −150~−98
    s3 = App.openDocument(os.path.join(OUT, "S3_프레임회로.FCStd"))
    DY = V(0, -132, 0)
    for p in ("197_uln_bracket_Y", "195p_uln2003_Y", "198_uln_standoff_Y"):
        for o in ob(s3, p):
            o.Shape = mv(o.Shape, DY)
    for p in ("100h_bolt_M5x8_mounts", "100i_tnut_M5_mounts"):
        for o in ob(s3, p):
            o.Shape = Part.makeCompound([mv(x, DY) if x.BoundBox.Center.x < 0 else x.copy() for x in o.Shape.Solids])
    _save(s3, os.path.join(OUT, "S3_프레임회로.FCStd"))
    # 5) 정지 겹침: 바뀐 것 ↔ 전부 (같은 문 묶음 안은 뺌)
    every = []
    for f in ("S1_급이부", "S2_마킹부", "S3_프레임회로"):
        dd = App.openDocument(os.path.join(OUT, f + ".FCStd"), True)
        every += [(f[:2] + " " + o.Label, o.Shape.copy()) for o in dd.Objects if o.TypeId.startswith("Part::") and not o.Shape.isNull() and not o.Label.startswith("REF")]
        App.closeDocument(dd.Name)

    def grp(l):
        t = l.split(" ", 1)[1]
        if t.startswith(("112_", "196_gate_G2", "110", "196_gate_G1", "199d_gate_holder_G1", "199e_gate_holder_G1")) or (t.startswith("112s") and "[entry]" in t):
            return "entry"
        if t.startswith(("170_", "196_gate_G3", "172", "196_gate_G4", "199b_gate_holder_G4")) or "[iso" in t:
            return "iso"
        if t.startswith(("197_uln_bracket_Y", "195p_uln2003_Y", "198_uln_standoff_Y")):
            return "ulnY"
        if t.startswith("300_"):
            return "box"
        return None
    ok = (("110_entry_duct", "111h_"), ("199s", "199d"), ("199s", "199e"), ("199s", "196_gate_G1"), ("172_isolation_duct", "173h"), ("196_gate_G2_ir", "110b"), ("100h", "197"), ("100h", "100"), ("100i", "100"),
          ("300_", "300"), ("300_", "301"), ("300_", "304"), ("300_", "308"), ("300_", "307"), ("300_", "196_gate"), ("300_", "142"))
    probe = [(l, sh) for l, sh in every if grp(l) or l.split(" ", 1)[1].startswith(("100h", "100i"))]
    seen = set()
    for la, sa in probe:
        for lb, sb_ in every:
            if la == lb or (lb, la) in seen:
                continue
            if grp(la) and grp(la) == grp(lb):
                continue
            ta, tb = la.split(" ", 1)[1], lb.split(" ", 1)[1]
            if any(ta.startswith(p) and tb.startswith(q) or ta.startswith(q) and tb.startswith(p) for p, q in ok):
                continue
            if sa.BoundBox.intersect(sb_.BoundBox):
                try:
                    v = sa.common(sb_).Volume
                except Exception:
                    v = 0.0
                if v > 0.05:
                    rep["hits"].append([la[:45], lb[:45], round(v, 1)]); seen.add((la, lb))
    rep["ok"] = True
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(OUT, "_doors_swap.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
