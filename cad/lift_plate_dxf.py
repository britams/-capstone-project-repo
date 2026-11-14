# -*- coding: utf-8 -*-
"""300p 투명 아크릴 격자판 → 레이저 가공용 DXF (R12, mm, 원점 = 판 가운데). FreeCAD 없이: python cad/lift_plate_dxf.py
치수는 lift_v2와 같은 값을 직접 씀 (lift_v2는 FreeCAD가 있어야 불러옴): 38 × 38, 모서리 R1, 네모 구멍 3.0 간격 4.4 (안 Ø33 안), 나사 구멍 Ø3.4 (±15, ±15)
"""
import math, os

D, R, HOLE, P, BORE, SCREW, INS = 38.0, 1.0, 3.0, 4.4, 33.0, 3.4, 15.0
GRID_R = BORE / 2 - HOLE / 2 * 2 ** 0.5


def centers():
    n = int(GRID_R / P) + 1
    return [(i * P, j * P) for i in range(-n, n + 1) for j in range(-n, n + 1) if math.hypot(i, j) * P <= GRID_R + 1e-9]


def disc_dxf(path, d=32.0, hole=3.4):
    """(11/14) 304 바닥 원판 — 같은 2T 판에서 같이 자름 (McMaster 원판 대신)"""
    e = ["0\nCIRCLE\n8\nCUT\n10\n0.0\n20\n0.0\n40\n%.4f" % (d / 2), "0\nCIRCLE\n8\nCUT\n10\n0.0\n20\n0.0\n40\n%.4f" % (hole / 2)]
    with open(path, "w", encoding="ascii") as f:
        f.write("0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(e) + "\n0\nENDSEC\n0\nEOF\n")


def dxf(path):
    e = []
    line = lambda a, b: e.append("0\nLINE\n8\nCUT\n10\n%.4f\n20\n%.4f\n11\n%.4f\n21\n%.4f" % (a[0], a[1], b[0], b[1]))
    arc = lambda c, r, a0, a1: e.append("0\nARC\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f\n50\n%.1f\n51\n%.1f" % (c[0], c[1], r, a0, a1))
    circ = lambda c, r: e.append("0\nCIRCLE\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f" % (c[0], c[1], r))
    h = D / 2
    line((-h + R, -h), (h - R, -h)); line((h, -h + R), (h, h - R)); line((h - R, h), (-h + R, h)); line((-h, h - R), (-h, -h + R))
    arc((h - R, -h + R), R, 270, 360); arc((h - R, h - R), R, 0, 90); arc((-h + R, h - R), R, 90, 180); arc((-h + R, -h + R), R, 180, 270)
    a = HOLE / 2
    for x, y in centers():
        c = [(x - a, y - a), (x + a, y - a), (x + a, y + a), (x - a, y + a)]
        for k in range(4):
            line(c[k], c[(k + 1) % 4])
    for sx in (-1, 1):
        for sy in (-1, 1):
            circ((sx * INS, sy * INS), SCREW / 2)
    with open(path, "w", encoding="ascii") as f:
        f.write("0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(e) + "\n0\nENDSEC\n0\nEOF\n")
    return len(centers())


def nest_dxf(path, W=100.0, H=90.0):
    """(11/15) 아크릴몰은 50 mm 밑은 못 자름 → 판 한 장(100 × 90, 2T 투명) 안에 격자판 2 + 바닥 원판 2를 같이 그림 (바깥 틀도 자름)"""
    import re
    def body(fn, dx, dy):
        tmp = path + ".tmp"
        fn(tmp)
        t = open(tmp, encoding="ascii").read()
        os.remove(tmp)
        ents = t.split("ENTITIES\n", 1)[1].rsplit("\n0\nENDSEC", 1)[0]
        out = []
        for e in ents.split("\n0\n"):
            e = e if e.startswith("0\n") else "0\n" + e
            ln = e.split("\n")
            for i in range(0, len(ln) - 1, 2):
                if ln[i] in ("10", "11"):
                    ln[i + 1] = "%.4f" % (float(ln[i + 1]) + dx)
                elif ln[i] in ("20", "21"):
                    ln[i + 1] = "%.4f" % (float(ln[i + 1]) + dy)
            out.append("\n".join(ln))
        return out
    e = []
    for dx in (-25.0, 25.0):
        e += body(dxf, dx, 21.0)
        e += body(disc_dxf, dx, -24.0)
    w, h = W / 2, H / 2
    for a_, b_ in (((-w, -h), (w, -h)), ((w, -h), (w, h)), ((w, h), (-w, h)), ((-w, h), (-w, -h))):
        e.append("0\nLINE\n8\nCUT\n10\n%.4f\n20\n%.4f\n11\n%.4f\n21\n%.4f" % (a_[0], a_[1], b_[0], b_[1]))
    with open(path, "w", encoding="ascii") as f:
        f.write("0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(e) + "\n0\nENDSEC\n0\nEOF\n")
    return len(e)


if __name__ == "__main__":
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "print", "lift", "300p_아크릴격자판.dxf")
    print(out, "구멍", dxf(out))
    disc_dxf(os.path.join(os.path.dirname(out), "300f_아크릴바닥원판.dxf"))
    print("묶음", nest_dxf(os.path.join(os.path.dirname(out), "300pf_아크릴_묶음_100x90_2T.dxf")))
