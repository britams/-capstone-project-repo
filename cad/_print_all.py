# -*- coding: utf-8 -*-
import json, os, sys, re, traceback
HERE = os.getcwd()
OUT = os.path.join(HERE, "print", "all")
os.makedirs(OUT, exist_ok=True)
rep = dict(rows=[])
try:
    import FreeCAD as App, Mesh, MeshPart, Part
    d = App.openDocument(os.path.join(HERE, "D5g_full.FCStd"))
    for o in d.Objects:
        if not o.TypeId.startswith("Part::") or not App.GuiUp: continue
        try:
            c = o.ViewObject.ShapeColor
            sh = o.Shape
        except Exception:
            continue
        if not (c[1] > 0.6 and c[0] < 0.4 and c[2] < 0.5) or sh.isNull() or sh.Volume <= 0 or o.Label.startswith("300_"):
            continue
        code = o.Label.split(" ")[0]
        name = re.sub(r'[\\/:*?"<>|]', "_", code)
        bb = sh.BoundBox
        m = MeshPart.meshFromShape(Shape=sh, LinearDeflection=0.05, AngularDeflection=0.3)
        m.write(os.path.join(OUT, name + ".stl"))
        sh.exportStep(os.path.join(OUT, name + ".step"))
        ins = bool(re.search("인서트|insert", o.Label))
        rep["rows"].append(dict(code=code, label=o.Label, file=name, valid=sh.isValid(), solids=len(sh.Solids),
                                vol_cm3=round(sh.Volume / 1000, 2), size=[round(bb.XLength, 1), round(bb.YLength, 1), round(bb.ZLength, 1)],
                                mesh_solid=m.isSolid(), insert=ins))
except Exception:
    rep["error"] = traceback.format_exc()
json.dump(rep, open(os.path.join(HERE, "split", "_print_all.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
import FreeCAD as App
if App.GuiUp:
    os._exit(0)
