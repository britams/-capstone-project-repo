# -*- coding: utf-8 -*-
"""통로 관 110·172 → 산 PVC 관 + 작은 꺾임 조각 (서현 11/12 02:48·02:5x, CAP-AI-62)

서현: "관을 투명하게 하는 것을 추천하지 않는다면 투명하게 하지 말고. 부품 사" → 수도용 PVC 13A 선택
      엘보가 안 들어감 → "꺾이는 부분도 최대한 사는 쪽으로 찾아봐 안되면 프린트"
찾은 것:
  - PVC 13A (VG1): 바깥 18, 최소 두께 2.2, 안 약 13 [확실 — sudo.info KS 표]
  - 수도용 엘보 13 (KS M 3402 TS): 바깥 24, 가운데→끝 H 36, 끼움 깊이 26 [확실 — 삼진프라코 표 (kkpla.co.kr)]
  - 지금 꺾이는 곳: 세로 관 축(x 0)에서 문 하우징(112·170, x 9.5부터)까지 9.5 mm → 가운데→끝 36인 엘보는 하우징 속으로 들어감 [확실 — 모델]
  - 공압 유니언 엘보(16 mm)도 끼움 깊이 때문에 비슷하게 길다 [추측 — 치수표 못 읽음]
  → 곧은 구간 = PVC 13A 자름 (구매), 꺾임 2곳 = 지금 꺾임 모양(R 12, 안 12) + PVC 끼움 소켓(안 18.4, 깊이 12)의 작은 프린트
꺾임 시작: 110은 z 337 (가로 축 z 349, R 12), 172는 z 389 (가로 축 z 377, R 12) [확실 — 모델 단면]
빔 구멍 Ø3.2 (x 방향): G1 z 275 (110), G4 z 570 (172) — PVC에 드릴
"""
import FreeCAD as App
import Part

V = App.Vector
PVC = dict(od=18.0, id=13.0)
SOCK = dict(id=18.4, od=22.0, depth=12.0, shoulder=1.0, bore=12.0)
# (11/12) 172 세로 관 축을 x +1.5: 바깥 18이면 갠트리 레일 100d(면 x −8)에 1 mm 묻힘 (77 mm³) → 틈 0.5. 꺾임 조각 소켓이 1.5 어긋남을 받음
DUCTS = (  # (라벨 머리, 관 z0, 관 z1, 꺾임 쪽 'up'/'down', 꺾임 경계 z, 빔 z, 세로 관 축 x)
    ("110_entry_duct", 235.0, None, "up", 337.0, 275.0, 0.0),
    ("172_isolation_duct", None, 585.0, "down", 389.0, 570.0, 1.5),
)
LABEL = {
    "110_entry_duct": "110_entry_duct (수도용 PVC 13A — 바깥 18·안 13, %d mm 자름, 빔 구멍 Ø3.2 2, 구매)",
    "172_isolation_duct": "172_isolation_duct (수도용 PVC 13A — 바깥 18·안 13, %d mm 자름, 빔 구멍 Ø3.2 2, 구매)",
    "110b": "110b_entry_bend (꺾임 조각 — R 12·안 12 + PVC 끼움 소켓 깊이 12, 작은 3D 프린트)",
    "172b": "172b_isolation_bend (꺾임 조각 — R 12·안 12 + PVC 끼움 소켓 깊이 12, 작은 3D 프린트)",
}


def build(old_shape, z0, z1, side, zb, zbeam, ax=0.0):
    s = SOCK
    big = 2000.0
    if side == "up":                   # 꺾임이 위 (110)
        bend = old_shape.common(Part.makeBox(big, big, big, V(-big / 2, -big / 2, zb)))
        zs0, zs1 = zb - s["depth"] - s["shoulder"], zb
        sock = Part.makeCylinder(s["od"] / 2, zs1 - zs0, V(ax, 0, zs0))
        sock = sock.cut(Part.makeCylinder(s["id"] / 2, s["depth"], V(ax, 0, zs0)))
        sock = sock.cut(Part.makeCylinder(s["bore"] / 2, 50, V(ax, 0, zs0)))
        p0, p1 = z0, zb - s["shoulder"]
    else:                              # 꺾임이 아래 (172)
        bend = old_shape.common(Part.makeBox(big, big, big, V(-big / 2, -big / 2, zb - big)))
        zs0, zs1 = zb, zb + s["depth"] + s["shoulder"]
        sock = Part.makeCylinder(s["od"] / 2, zs1 - zs0, V(ax, 0, zs0))
        sock = sock.cut(Part.makeCylinder(s["id"] / 2, s["depth"], V(ax, 0, zs0 + s["shoulder"])))
        sock = sock.cut(Part.makeCylinder(s["bore"] / 2, 50, V(ax, 0, zs0 - 1)))
        sock = sock.cut(Part.makeCylinder(s["bore"] / 2, 50, V(0, 0, zs0 - 1)))       # 꺾임 쪽 구멍 (축 x 0)과도 통하게
        p0, p1 = zb + s["shoulder"], z1
    bendp = bend.fuse(sock).removeSplitter()
    pipe = Part.makeCylinder(PVC["od"] / 2, p1 - p0, V(ax, 0, p0)).cut(Part.makeCylinder(PVC["id"] / 2, p1 - p0 + 2, V(ax, 0, p0 - 1)))
    pipe = pipe.cut(Part.makeCylinder(1.6, 40, V(-20, 0, zbeam), V(1, 0, 0)))
    return pipe, bendp, round(p1 - p0)


def apply(doc):
    rep, made = {}, []
    for head, z0, z1, side, zb, zbeam, ax in DUCTS:
        o = [x for x in doc.Objects if x.Label.startswith(head)][0]
        if "PVC 13A" in o.Label:
            rep[head] = "이미 PVC"
            continue
        pipe, bendp, L = build(o.Shape, z0, z1, side, zb, zbeam, ax)
        o.Shape = pipe
        o.Label = LABEL[head] % L
        bh = head[:3] + "b"
        for x in [x for x in doc.Objects if x.Label.startswith(bh + "_")]:
            doc.removeObject(x.Name)
        b = doc.addObject("Part::Feature", "DB_" + bh)
        b.Label, b.Shape = LABEL[bh], bendp
        made += [o, b]
        rep[head] = dict(pipe_L=L, bend_vol=round(bendp.Volume))
    doc.recompute()
    return made, rep


def check(doc, made):
    allow = (("110_", "110b"), ("172_", "172b"), ("110b", "112_"), ("172b", "170_"), ("199s", "110_"), ("199s", "172_"))
    hits = []
    for a in made:
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
    return hits
