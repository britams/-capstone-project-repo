# -*- coding: utf-8 -*-
"""meviy 담당자 견적 6장 → 출하 12/02라 시연(12/2)에 못 맞춤 → 3D 프린트 3장 + 아크릴 레이저 3장 (승준 11/23 19시, CAP-AI-SJ-63)
  YA·YB·YM = 3D 프린트 PETG 3T (M4·M3 접시가 있어 아크릴은 깨짐 — 둥근머리로 바꾸면 6곳이 SC8UU·캐리지·모터에 닿음 [CAD])
  XN·CP·SV = 아크릴 3T 레이저 (접시·얇은 벽 없음)
  NEMA17 팬케이크 + T8 너트용으로 같이 고침: YM 옛 Ø3.0 × 4 메움 → Ø3.4 × 3 (31 간격) / XN M2 탭·옛 Ø3.4 메움, 가운데 Ø10.5, M3 탭 밑구멍 Ø2.5 × 2 / CP 옛 POM Ø3.4 × 3 메움 → Ø3.4 × 2
  프린트 구멍은 0.2 mm 크게 (FDM은 작게 나옴), 접시는 그대로. 판을 눕혀 (두께 = z) 원점에 놓음. 두께 3 mm 그대로라 다른 부품은 안 바뀜
  재료: meviy STEP (cad/print/meviy/, 11/18 승준 수정본 = meviy에 올린 것). FreeCAD 없이 OpenCascade (pip install cadquery-ocp ezdxf)
  실행: python3 cad/xy_plates_plastic_1123.py  → cad/print/2026-11-23_XY판_프린트_아크릴/"""
import os, math
from OCP.STEPControl import STEPControl_Reader
from OCP.IFSelect import IFSelect_RetDone
from OCP.TopExp import TopExp_Explorer
from OCP.TopAbs import TopAbs_FACE, TopAbs_EDGE
from OCP.BRepAdaptor import BRepAdaptor_Surface, BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_Cylinder, GeomAbs_Plane, GeomAbs_Line, GeomAbs_Circle
from OCP.TopoDS import TopoDS
from OCP.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Ax1, gp_Trsf, gp_Vec
from OCP.BRepPrimAPI import BRepPrimAPI_MakeCylinder
from OCP.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut
from OCP.BRepBuilderAPI import BRepBuilderAPI_Transform
from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
from OCP.BRepCheck import BRepCheck_Analyzer
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.StlAPI import StlAPI_Writer
from OCP.Bnd import Bnd_Box
from OCP.BRepBndLib import BRepBndLib
from OCP.GProp import GProp_GProps
from OCP.BRepGProp import BRepGProp
from OCP.BRepTools import BRepTools
import ezdxf

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "print", "meviy")
OUT = os.path.join(HERE, "print", "2026-11-23_XY판_프린트_아크릴")
os.makedirs(OUT, exist_ok=True)

def read(p):
    r = STEPControl_Reader(); assert r.ReadFile(p) == IFSelect_RetDone; r.TransferRoots(); return r.OneShape()
def bbox(s):
    b = Bnd_Box(); BRepBndLib.Add_s(s, b); p, q = b.CornerMin(), b.CornerMax(); return p.X(), p.Y(), p.Z(), q.X(), q.Y(), q.Z()
def vol(s):
    g = GProp_GProps(); BRepGProp.VolumeProperties_s(s, g); return g.Mass()
def faces(s):
    e = TopExp_Explorer(s, TopAbs_FACE)
    while e.More(): yield TopoDS.Face(e.Current()); e.Next()
def cyl(p, d, r, t0, t1):              # 판 두께 축 d (0 x, 1 y), p = 나머지 두 좌표
    q = list(p); q.insert(d, t0); D = [0, 0, 0]; D[d] = 1
    return BRepPrimAPI_MakeCylinder(gp_Ax2(gp_Pnt(*q), gp_Dir(*D)), r, t1 - t0).Shape()
def clean(s):
    u = ShapeUpgrade_UnifySameDomain(s, True, True, False); u.Build(); return u.Shape()
def edit(s, d, t0, t1, fill=(), new=()):
    for p, dia in fill: s = BRepAlgoAPI_Fuse(s, cyl(p, d, dia / 2 + 0.02, t0, t1)).Shape()   # +0.02: 좌표 끝수 틈 없게
    s = clean(s)
    for p, dia in new: s = BRepAlgoAPI_Cut(s, cyl(p, d, dia / 2, t0 - 1, t1 + 1)).Shape()
    return clean(s)
def through_holes(s, d):               # 두께 방향 원통 구멍 (중심 2좌표, 지름)
    out = set()
    for f in faces(s):
        a = BRepAdaptor_Surface(f)
        if a.GetType() == GeomAbs_Cylinder:
            c = a.Cylinder(); ax = c.Axis().Direction()
            if abs(abs([ax.X(), ax.Y(), ax.Z()][d]) - 1) < 1e-6:
                p = c.Location(); q = [p.X(), p.Y(), p.Z()]; q.pop(d)
                out.add((round(q[0], 3), round(q[1], 3), round(c.Radius() * 2, 3)))
    return sorted(out)

a = math.radians
XN_TAP = [(-65 + 8 * math.cos(a(t)), 425 + 8 * math.sin(a(t))) for t in (150, 240)]
# 이름, STEP, 두께 축, [t0, t1], 메울 구멍, 새 구멍, 방식, 위로 올 면 (+1/−1: 두께 축 + 쪽 면을 위로)
PL = [
 ("YA_빔판A", "YA_빔판A_A5052_3T.step", 1, -59.0, -56.0, [], [], "print", +1),
 ("YB_빔판B", "YB_빔판B_A5052_3T.step", 1, 58.0, 61.0, [], [], "print", -1),
 ("YM_Y모터판", "YM_Y모터판_A5052_3T.step", 1, -101.9, -98.9,
  [((89.9, 441.5), 3.0), ((89.9, 464.5), 3.0), ((112.9, 441.5), 3.0), ((112.9, 464.5), 3.0)],
  [((85.9, 437.5), 3.4), ((85.9, 468.5), 3.4), ((116.9, 468.5), 3.4)], "print", -1),
 ("XN_X너트판", "XN_X너트판_A5052_3T.step", 0, 87.4, 90.4,
  [((-70.5, 421.8), 1.6), ((-59.5, 421.8), 1.6), ((-65.0, 431.35), 3.4)],
  [((-65.0, 425.0), 10.5)] + [(p, 2.5) for p in XN_TAP], "laser", 0),
 ("CP_캐리지판", "CP_캐리지판_A5052_3T.step", 1, -47.0, -44.0,
  [((95.901, 456.175), 3.4), ((106.899, 456.175), 3.4), ((101.4, 446.65), 3.4)],
  [((93.4, 453.0), 3.4), ((109.4, 453.0), 3.4)], "laser", 0),
 ("SV_서보판", "SV_서보판_A5052_3T.step", 0, 100.15, 103.15, [], [], "laser", 0),
]
COMP = 0.2                              # 프린트 구멍 보정 (지름)

def to_print(s, d, up):                 # 두께 축 → +z, up 면이 위, 원점에
    t = gp_Trsf()
    if d == 1: t.SetRotation(gp_Ax1(gp_Pnt(0, 0, 0), gp_Dir(1, 0, 0)), math.radians(90 if up > 0 else -90))
    s = BRepBuilderAPI_Transform(s, t, True).Shape()
    x0, y0, z0, *_ = bbox(s); t2 = gp_Trsf(); t2.SetTranslation(gp_Vec(-x0, -y0, -z0))
    return BRepBuilderAPI_Transform(s, t2, True).Shape()

def to_dxf(s, d, path):                 # 두께 축 − 쪽 면 외곽·구멍 → 2D (u, v) = 나머지 두 좌표
    keep = [i for i in range(3) if i != d]
    best = None
    for f in faces(s):
        a_ = BRepAdaptor_Surface(f)
        if a_.GetType() == GeomAbs_Plane:
            n = a_.Plane().Axis().Direction(); n = [n.X(), n.Y(), n.Z()]
            if abs(abs(n[d]) - 1) < 1e-6:
                g = GProp_GProps(); BRepGProp.SurfaceProperties_s(f, g)
                if best is None or g.Mass() > best[0]: best = (g.Mass(), f)
    f = best[1]
    x0, y0, z0, *_ = bbox(s); org = [x0, y0, z0]
    P = lambda p: ((p.X(), p.Y(), p.Z())[keep[0]] - org[keep[0]], (p.X(), p.Y(), p.Z())[keep[1]] - org[keep[1]])
    doc = ezdxf.new("R2010", units=4); msp = doc.modelspace(); n = 0
    e = TopExp_Explorer(f, TopAbs_EDGE)
    while e.More():
        c = BRepAdaptor_Curve(TopoDS.Edge(e.Current())); t0, t1 = c.FirstParameter(), c.LastParameter()
        if c.GetType() == GeomAbs_Line:
            msp.add_line(P(c.Value(t0)), P(c.Value(t1)))
        elif c.GetType() == GeomAbs_Circle:
            ci = c.Circle(); cc = P(ci.Location()); r = ci.Radius()
            if abs(t1 - t0 - 2 * math.pi) < 1e-6: msp.add_circle(cc, r)
            else:
                ang = lambda p: math.degrees(math.atan2(P(p)[1] - cc[1], P(p)[0] - cc[0])) % 360
                s0, s1, sm = ang(c.Value(t0)), ang(c.Value(t1)), ang(c.Value((t0 + t1) / 2))
                ccw = (sm - s0) % 360 < (s1 - s0) % 360
                msp.add_arc(cc, r, s0, s1) if ccw else msp.add_arc(cc, r, s1, s0)
        else:
            k = 24; pts = [P(c.Value(t0 + (t1 - t0) * i / k)) for i in range(k + 1)]
            msp.add_lwpolyline(pts)
        n += 1; e.Next()
    doc.saveas(path); return n

if __name__ == "__main__":
    for name, step, d, t0, t1, fill, new, how, up in PL:
        s0 = read(os.path.join(SRC, step))
        s = edit(s0, d, t0, t1, fill, new) if (fill or new) else s0
        tag = "_NEMA17" if (fill or new) else ""
        if how == "print":
            for (u, v, dia) in through_holes(s, d):
                s = BRepAlgoAPI_Cut(s, cyl((u, v), d, (dia + COMP) / 2, t0 - 1, t1 + 1)).Shape()
            assert BRepCheck_Analyzer(s).IsValid(), name          # (접시와 만나는 곳은 면 합치기 안 함)
            m = to_print(s, d, up)
            BRepMesh_IncrementalMesh(m, 0.01, False, 0.1, True)
            out = os.path.join(OUT, "%s_PETG_3T%s.stl" % (name, tag))
            w = StlAPI_Writer(); w.ASCIIMode = False; w.Write(m, out)
            b = bbox(m)
            print("STL", os.path.basename(out), "%.1f × %.1f × %.1f mm" % (b[3] - b[0], b[4] - b[1], b[5] - b[2]), "부피 %.0f mm³" % vol(m))
        else:
            assert BRepCheck_Analyzer(s).IsValid(), name
            out = os.path.join(OUT, "%s_아크릴3T%s.dxf" % (name, tag))
            k = to_dxf(s, d, out)
            print("DXF", os.path.basename(out), "선 %d개" % k, "구멍", through_holes(s, d))
