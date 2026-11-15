# -*- coding: utf-8 -*-
"""XY '전부 사는 것' 알루미늄 판 → 레이저 가공용 DXF (R12, mm). FreeCAD 없이: python cad/xy_plate_dxf.py (11/15, CAP-AI-62)
치수는 s23_gantry_buy1b.py와 같은 값을 직접 씀.
  217 X 모터판 3 mm: 44 × 59 (가로 = y −87 ~ −43, 세로 = z 400 ~ 459), 원점 = 판 왼쪽 아래
      축 Ø10 (22, 25) · 28BYJ 귀 Ø4.2 (22 ± 17.5, 17) · 레일 M5 Ø5.5 (22 ± 9, 50)
"""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "print", "xy")


def write(path, rect, holes):
    e = []
    w, h = rect
    pts = [(0, 0), (w, 0), (w, h), (0, h)]
    for k in range(4):
        a, b = pts[k], pts[(k + 1) % 4]
        e.append("0\nLINE\n8\nCUT\n10\n%.4f\n20\n%.4f\n11\n%.4f\n21\n%.4f" % (a[0], a[1], b[0], b[1]))
    for x, y, d in holes:
        e.append("0\nCIRCLE\n8\nCUT\n10\n%.4f\n20\n%.4f\n40\n%.4f" % (x, y, d / 2))
    with open(path, "w", encoding="ascii") as f:
        f.write("0\nSECTION\n2\nHEADER\n9\n$INSUNITS\n70\n4\n0\nENDSEC\n0\nSECTION\n2\nENTITIES\n" + "\n".join(e) + "\n0\nENDSEC\n0\nEOF\n")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    write(os.path.join(OUT, "217_X모터판_알루미늄3T_44x59.dxf"), (44.0, 59.0),
          [(22, 25, 10.0), (22 - 17.5, 17, 4.2), (22 + 17.5, 17, 4.2), (22 - 9, 50, 5.5), (22 + 9, 50, 5.5)])
    print("ok", OUT)
