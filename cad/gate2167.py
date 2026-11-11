# -*- coding: utf-8 -*-
"""빛 게이트 송수신기 Adafruit 2167 — 실제 치수로 다시 + 둥근 통로에 맞는 안장 받침 (서현 11/12 02:31, CAP-AI-62)

서현: "여기 회색 무슨 부품이야. 이거 수정해. 이것도 찾아서 제대로 만들어" (G4 — 격리 통로 위, 둥근 관 옆 네모 두 개)
찾은 것 [확실 — 모델]:
  - 회색 네모 = 빛 게이트 송신기·수신기 (Adafruit 2167 IR Break Beam 3 mm, 2개 1조)
  - 지금 모양은 10 × 10 × 20 상자 — 실제는 20 × 10 × 8 (두께 8) [확실 — Adafruit 제품 페이지·치수도 2167diagram.jpg]
  - G4(172)·G1(110 입구)의 통로는 둥근 관 Ø16인데 송수신기 평평한 면이 관에 '선 하나'로만 닿아 양옆이 떠 있음.
    받침(gate_holders_fix)은 가장 가까운 점 사이만 채워서 0.4 mm 조각이 됨. G1은 송수신기가 관 속으로 2 mm 들어가 있었음
실제 2167 (치수도): 몸통 20 × 10 × 8, 앞면(20 × 10)에 LED 렌즈 링 Ø8 · LED Ø3 — 한 끝에서 5 mm,
  나사 구멍 Ø2.4 (앞→뒤 관통) — LED에서 10 mm (다른 끝에서 5 mm), 선 230 mm [확실 — 치수도·제품 페이지]
  렌즈 링 깊이·선 나오는 자리 [추측 — 치수도에 없음]: 링 0.5 mm 오목, 선은 구멍 쪽 끝에서 Ø3
고침:
  - 송수신기 = 실제 치수. LED 가운데가 빔 선 위
  - 둥근 관(G1·G4): 앞면을 관 축에서 12 mm에 두고, 앞면 ↔ 관 사이를 '안장 받침'으로 채움(관 둘레 모양으로 파냄, 가운데 두께 4).
    빔 구멍 Ø3.2. 송수신기는 M2 × 12 (뒤에서 구멍 Ø2.4로 받침에 셀프 탭), 받침은 관에 순간접착 (작고 단순한 프린트)
  - G6(174 방생 목, 네모): 받침판 그대로 (목 위아래 2 mm), 송수신기만 실제 치수·LED 자리
"""
import FreeCAD as App
import Part

V = App.Vector
A = dict(L=20.0, W=10.0, T=8.0, led_end=5.0, led_d=3.0, ring_d=8.0, ring_t=0.5, hole_d=2.4, pitch=10.0, cable_d=3.0, cable_L=10.0)
SCREW = dict(d=2.0, L=12.0, head_d=3.8, head_t=1.3)
# 게이트: (송수신기 라벨, 빔 가운데, 빔 방향 n, 몸 길이 방향 u(LED 끝 쪽), 앞면 거리(빔 가운데 → 앞면), 통로 라벨, 관 반지름(둥근 관) 또는 None, 받침 라벨, 빔 라벨)
GATES = (
    (("114_entry_sensor_tx", "114_entry_sensor_rx"), V(0, 0, 275), V(1, 0, 0), V(0, 0, 1), 12.0, "110_", 8.0,
     ("199d_gate_holder_G1_tx", "199e_gate_holder_G1_rx"), None),
    (("196_gate_G4_tx_rx",), V(0, 0, 570), V(1, 0, 0), V(0, 0, 1), 12.0, "172_", 8.0, ("199b_gate_holder_G4",), "196_gate_G4_beam"),
    # G6: 몸 길이를 y로 (11/12 — x로 두면 LED 끝 5 때문에 몸이 x 93~113 → 문 하우징 176·G5b와 겹침, x 103~123 → 굴뚝 175와 겹침. y −15~5는 비어 있음)
    (("196_gate_G6_tx_rx",), V(108, 0, 377), V(0, 0, 1), V(0, 1, 0), 10.0, "174_", None, ("199c_gate_holder_G6",), "196_gate_G6_beam"),
)


def _frame_box(c, n, u, w, n0, n1, u0, u1, w0, w1):
    """국부(n, u, w) 상자 → 세상 (축은 세상 축과 나란함)"""
    pts = [c + n * a + u * b + w * e for a in (n0, n1) for b in (u0, u1) for e in (w0, w1)]
    x0, x1 = min(p.x for p in pts), max(p.x for p in pts)
    y0, y1 = min(p.y for p in pts), max(p.y for p in pts)
    z0, z1 = min(p.z for p in pts), max(p.z for p in pts)
    return Part.makeBox(x1 - x0, y1 - y0, z1 - z0, V(x0, y0, z0))


def sensor(face_c, n_in, u):
    """face_c = 앞면의 LED 가운데, n_in = 빔이 나가는 방향(앞면 바깥), u = LED 끝 쪽. 반환 (몸통, 나사 구멍 가운데)"""
    a = A
    w = n_in.cross(u)
    body = _frame_box(face_c, n_in, u, w, -a["T"], 0, -(a["L"] - a["led_end"]), a["led_end"], -a["W"] / 2, a["W"] / 2)
    body = body.cut(Part.makeCylinder(a["ring_d"] / 2, a["ring_t"], face_c - n_in * a["ring_t"], n_in))       # 렌즈 링 [추측 깊이]
    body = body.fuse(Part.makeCylinder(a["led_d"] / 2, a["ring_t"], face_c - n_in * a["ring_t"], n_in))       # LED 머리 (앞면과 같은 높이)
    hc = face_c - u * a["pitch"]
    body = body.cut(Part.makeCylinder(a["hole_d"] / 2, a["T"] + 2, hc - n_in * (a["T"] + 1), n_in))
    cab = face_c - u * (a["L"] - a["led_end"]) - n_in * (a["T"] / 2)
    body = body.fuse(Part.makeCylinder(a["cable_d"] / 2, a["cable_L"], cab, -u))                              # 선 [추측 자리]
    return body.removeSplitter(), hc


def screw(hc, n_in):
    """M2 × 12 십자 냄비머리: 머리는 뒷면 바깥, 몸은 앞쪽(n_in)으로 — 송수신기 8 + 받침 4"""
    back = hc - n_in * A["T"]
    head = Part.makeCylinder(SCREW["head_d"] / 2, SCREW["head_t"], back - n_in * SCREW["head_t"], n_in)
    return head.fuse(Part.makeCylinder(SCREW["d"] / 2, SCREW["L"], back, n_in))


def build(doc):
    """반환: dict(라벨 → 모양), 보고"""
    out, rep = {}, []
    for labels, c, n, u, face, duct_pre, r_tube, holders, beam_lab in GATES:
        duct = [o for o in doc.Objects if o.Label.startswith(duct_pre)]
        w = n.cross(u)
        bodies, screws, saddles = [], [], []
        for side in (-1, 1):
            n_in = n * (-side)                        # 앞면이 빔 가운데를 봄
            fc = c + n * (side * face)
            b, hc = sensor(fc, n_in, u)
            bodies.append(b)
            # 받침: 앞면 → 빔 가운데 쪽으로, 몸통 크기
            if r_tube is not None:
                depth = face - r_tube + 1.0                                     # 관 속 1 mm까지 → 관 모양으로 파냄
                blk = _frame_box(fc, n_in, u, w, 0, depth, -(A["L"] - A["led_end"]), A["led_end"], -A["W"] / 2, A["W"] / 2)
                blk = blk.cut(Part.makeCylinder(r_tube, 400, V(c.x, c.y, c.z) - u * 200, u))     # 관 둘레 (관 축 = u)
            else:
                gap = face - 8.0                                                # 네모 목: 바깥 면이 빔 가운데에서 8
                blk = _frame_box(fc, n_in, u, w, 0, gap, -(A["L"] - A["led_end"]), A["led_end"], -A["W"] / 2, A["W"] / 2)
            blk = blk.cut(Part.makeCylinder(1.6, 2 * face + 2, c - n * (face + 1), n))                # 빔 구멍 Ø3.2
            blk = blk.cut(Part.makeCylinder(0.8, 6.0, hc, n_in))                                    # M2 셀프 탭 구멍 Ø1.6
            if duct:
                try:
                    blk = blk.cut(duct[0].Shape)
                except Exception:
                    pass
            saddles.append(blk.removeSplitter())
            if r_tube is not None:
                screws.append(screw(hc, n_in))
        if len(labels) == 2:                          # 114: 송신 tx는 +x 쪽 (예전 자리 그대로), 수신 rx는 −x
            out[labels[0]] = bodies[1]
            out[labels[1]] = bodies[0]
            out[holders[0]] = saddles[1]
            out[holders[1]] = saddles[0]
        else:
            out[labels[0]] = Part.makeCompound(bodies)
            out[holders[0]] = Part.makeCompound(saddles)
        if screws:
            out.setdefault("199s_gate_screws", []).extend(screws)
        if beam_lab:
            out[beam_lab] = Part.makeCylinder(0.6, 2 * face, c - n * face, n)
        rep.append(dict(gate=labels[0], face_from_center=face, tube_r=r_tube,
                        saddle_min=round(face - r_tube, 1) if r_tube else round(face - 8.0, 1)))
    out["199s_gate_screws"] = Part.makeCompound(out.get("199s_gate_screws", []))
    return out, rep


NAMES = {
    "114_entry_sensor_tx": "114_entry_sensor_tx (Adafruit 2167 송신 — 20 × 10 × 8, LED 끝에서 5, 실제 치수)",
    "114_entry_sensor_rx": "114_entry_sensor_rx (Adafruit 2167 수신 — 20 × 10 × 8, LED 끝에서 5, 실제 치수)",
    "196_gate_G4_tx_rx": "196_gate_G4_tx_rx (Adafruit 2167 송·수신 — 20 × 10 × 8, 실제 치수)",
    "196_gate_G6_tx_rx": "196_gate_G6_tx_rx (Adafruit 2167 송·수신 — 20 × 10 × 8, 실제 치수)",
    "199b_gate_holder_G4": "199b_gate_holder_G4 (안장 받침 2 — 관 Ø16 둘레로 파냄, 가운데 4 mm, 관에 순간접착, 작은 3D 프린트)",
    "199c_gate_holder_G6": "199c_gate_holder_G6 (받침판 2 — 목 위아래 2 mm, 순간접착, 작은 3D 프린트)",
    "199d_gate_holder_G1_tx": "199d_gate_holder_G1_tx (안장 받침 — 관 Ø16 둘레로 파냄, 가운데 4 mm, 작은 3D 프린트)",
    "199e_gate_holder_G1_rx": "199e_gate_holder_G1_rx (안장 받침 — 관 Ø16 둘레로 파냄, 가운데 4 mm, 작은 3D 프린트)",
    "199s_gate_screws": "199s_gate_screws (M2 × 12 십자 냄비머리 4 — 2167 구멍 Ø2.4 → 안장 받침에 셀프 탭, 구매)",
    "196_gate_G4_beam": "196_gate_G4_beam",
    "196_gate_G6_beam": "196_gate_G6_beam",
}


def apply(doc):
    out, rep = build(doc)
    made = []
    for key, shp in out.items():
        old = [o for o in doc.Objects if o.Label.split(" ")[0] == key]
        if old:
            o = old[0]
            for extra in old[1:]:
                doc.removeObject(extra.Name)
        else:
            o = doc.addObject("Part::Feature", "GT_" + key.split("_")[0])
        o.Shape = shp
        o.Label = NAMES.get(key, key)
        made.append(o)
    doc.recompute()
    return made, rep


def check(doc, made):
    """새 부품 ↔ 문서 전부 (고체 하나씩). 허용: 나사 ↔ 송수신기·받침 (셀프 탭), 받침 ↔ 통로 (순간접착 면)"""
    allow = (("199s", "114_"), ("199s", "196_gate"), ("199s", "199"), ("199", "110_"), ("199", "172_"), ("199", "174_"))
    hits = []
    for a in made:
        if "beam" in a.Label:
            continue
        for o in doc.Objects:
            if o is a or o.TypeId != "Part::Feature" or o.Shape.isNull() or "beam" in o.Label:
                continue
            if not a.Shape.BoundBox.intersect(o.Shape.BoundBox) or (o in made and o.Name < a.Name):
                continue
            ka, kb = a.Label.split(" ")[0], o.Label.split(" ")[0]
            try:
                v = sum(s.common(o.Shape).Volume for s in a.Shape.Solids if s.BoundBox.intersect(o.Shape.BoundBox))
            except Exception as e:
                hits.append((ka, kb, "ERR %s" % e, "확인"))
                continue
            if v > 0.05:
                ok = any((ka.startswith(p) and kb.startswith(q)) or (kb.startswith(p) and ka.startswith(q)) for p, q in allow)
                hits.append((ka, kb, round(v, 2), "허용" if ok else "문제"))
    # 받침이 관에 닿는지 (붙는 면)
    touch = []
    for a in made:
        if a.Label.startswith(("199b", "199d", "199e", "199c")):
            for lab, pre in (("199b", "172_"), ("199d", "110_"), ("199e", "110_"), ("199c", "174_")):
                if a.Label.startswith(lab):
                    du = [o for o in doc.Objects if o.Label.startswith(pre)]
                    if du:
                        touch.append((lab, [round(s.distToShape(du[0].Shape)[0], 2) for s in a.Shape.Solids]))
    return hits, touch
