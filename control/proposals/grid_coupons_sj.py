"""grid_coupons_sj.py — 격자 시험 조각 4종 (3D 프린트용) · 이승준 제안, CAP-AI-SJ-24

목적: 신뢰성 시뮬레이션(control/analysis/reliability_mc.py)이 '격자 모양 + 팁 굵기'가 마킹 성공을 좌우한다고 봄 →
      실물로 ① 마커 팁이 구멍을 지나 아래 면에 닿는지 ② 말벌 더미(표본)가 눌렸을 때 빠지거나 다리가 걸리는지 ③ 살이 휘는지 확인.
서현 설계 파일(cad/)이 아니라 시험용 조각. 채택되면 서현이 cad/ 모델에 반영.

조각 (모두 바깥 50 × 50 mm, 두께 1.5 mm = D6 g_t, 무늬 영역 40 × 40 = 마킹실)
  A  사각 구멍 3.0 / 피치 4.4 (살 1.4)  — 지금 D6 값
  B  사각 구멍 3.5 / 피치 4.3 (살 0.8)  — 제안 D6
  C  슬롯 틈 3.0 / 피치 4.0 (살 1.0), 가로 리브 12 mm마다 폭 1.0
  D  슬롯 틈 3.5 / 피치 4.5 (살 1.0), 가로 리브 12 mm마다 폭 1.0 — 제안 D5
가장자리 홈 개수(1~4)로 A~D 구분.

FreeCAD에서 실행 (FreeCAD 1.x): exec(open(이 파일).read()) 또는 MCP execute_code. OUT_DIR에 STL 4개 저장.
"""
import os

import FreeCAD as App
import Part

OUT_DIR = globals().get('OUT_DIR', os.path.join(os.path.expanduser('~'), 'grid_coupons'))
SIZE, T, AREA = 50.0, 1.5, 40.0

COUPONS = {
    'A_square_3p0_pitch4p4': dict(kind='square', opening=3.0, pitch=4.4, notches=1),
    'B_square_3p5_pitch4p3': dict(kind='square', opening=3.5, pitch=4.3, notches=2),
    'C_slot_3p0_pitch4p0':   dict(kind='slot', opening=3.0, pitch=4.0, rib_pitch=12.0, rib_w=1.0, notches=3),
    'D_slot_3p5_pitch4p5':   dict(kind='slot', opening=3.5, pitch=4.5, rib_pitch=12.0, rib_w=1.0, notches=4),
}


def centers(pitch, half):
    n = int((half - 0.5) // pitch)
    return [i * pitch for i in range(-n, n + 1)]


def make_coupon(c):
    plate = Part.makeBox(SIZE, SIZE, T, App.Vector(-SIZE / 2, -SIZE / 2, 0))
    cutters = []
    h = AREA / 2
    if c['kind'] == 'square':
        o = c['opening']
        for x in centers(c['pitch'], h - o / 2 + 0.5):
            for y in centers(c['pitch'], h - o / 2 + 0.5):
                cutters.append(Part.makeBox(o, o, T + 2, App.Vector(x - o / 2, y - o / 2, -1)))
    else:
        o, rp, rw = c['opening'], c['rib_pitch'], c['rib_w']
        ribs = [i * rp for i in range(-int(h // rp), int(h // rp) + 1)]
        xs = [-h] + sorted(sum([[r - rw / 2, r + rw / 2] for r in ribs], [])) + [h]
        for y in centers(c['pitch'], h - o / 2 + 0.5):
            for x0, x1 in zip(xs[0::2], xs[1::2]):
                if x1 - x0 > 0.5:
                    cutters.append(Part.makeBox(x1 - x0, o, T + 2, App.Vector(x0, y - o / 2, -1)))
    for k in range(c['notches']):            # 구분 홈: 아래 가장자리 1×1 mm
        cutters.append(Part.makeBox(1.0, 1.2, T + 2, App.Vector(-SIZE / 2 + 3 + 3 * k, -SIZE / 2 - 0.2, -1)))
    return plate.cut(Part.makeCompound(cutters))


def build(doc_name='GridCoupons_SJ'):
    os.makedirs(OUT_DIR, exist_ok=True)
    doc = App.newDocument(doc_name)
    report = {}
    for i, (name, c) in enumerate(COUPONS.items()):
        shp = make_coupon(c)
        obj = doc.addObject('Part::Feature', name)
        obj.Shape = shp
        obj.Placement.Base = App.Vector((i % 2) * 60, -(i // 2) * 60, 0)
        path = os.path.join(OUT_DIR, name + '.stl')
        shp.exportStl(path)
        open_ratio = 1 - shp.Volume / (SIZE * SIZE * T)
        report[name] = dict(volume_mm3=round(shp.Volume, 1), open_ratio_total=round(open_ratio, 3), valid=shp.isValid(), stl=path)
    doc.recompute()
    return report


if __name__ == '__main__' or 'FreeCAD' in globals() or True:
    REPORT = build()
    print(REPORT)
