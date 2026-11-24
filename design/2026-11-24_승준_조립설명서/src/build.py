# -*- coding: utf-8 -*-
"""조립 설명서 HTML 만들기 → Chrome으로 PDF."""
import json, math, os, html
import spec as SP
import svgparts as SV

BASE = os.path.dirname(os.path.abspath(__file__))
R = os.path.join(BASE, "r")
KB = json.load(open(os.path.join(BASE, "data", "keys_bb.json")))
steps, ctxkeys = SP.compute()
STEP_BY_ID = {s["id"]: s for s in steps}

SEC = {
    "A": ("프레임", "#d84315", "2020 알루미늄 막대로 장치의 뼈대 (360 × 360 × 610 mm)를 만든다.", "5-①"),
    "B": ("데크 판과 전기 부품", "#6a1b9a", "아래에서 두 번째 층에 흰 데크 판을 얹고, 전기 부품을 붙인다.", "5-① · 5-②"),
    "C": ("마킹실 (말벌 방과 문)", "#00838f", "작업대에서 말벌이 지나가는 방·문·센서를 한 덩어리로 만들어 데크에 세운다.", "2-① · 1"),
    "D": ("XY 펜 장치", "#1565c0", "펜을 말벌 위로 옮기는 장치. 작업대에서 거의 다 만들고 프레임에 얹는다.", "2-② · 1"),
    "E": ("위판 · 카메라 · 라즈베리 파이", "#2e7d32", "맨 위 층에 카메라를 매달고 파이 선반을 단다.", "3 · 5-①"),
    "F": ("선 연결", "#ef6c00", "전원 줄과 아두이노 핀. 서현 배선표 (11/17)를 그림으로 옮긴 것.", "5-②"),
    "G": ("나중 부품 (12/2 시연엔 없어도 됨)", "#757575", "상용 트랩, 통로 관, 깔때기, 포획통. 급이부 (설탕물 — 상자 4)는 이 설명서에 없다 (시연 뒤 서현 설계대로).", "2-① · 5-①"),
    "H": ("마지막 점검", "#37474f", "전원을 넣기 전과 처음 켤 때 볼 것.", ""),
}


# ---------------------------------------------------------------- 투영
def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def load_cam(name):
    return json.load(open(os.path.join(R, name + ".json"), encoding="utf-8"))["cam"]


def proj(cv, p):
    rel = [p[i] - cv["c"][i] for i in range(3)]
    s = cv["H"] / cv["height"]
    return (cv["W"] / 2 + dot(rel, cv["r"]) * s, cv["H"] / 2 - dot(rel, cv["u"]) * s)


def sol_centers(k):
    if k not in KB:
        return []
    sols = KB[k]["sol"] or [KB[k]["bb"]]
    return [((b[0] + b[3]) / 2, (b[1] + b[4]) / 2, (b[2] + b[5]) / 2) for b in sols]


def bb_of(keys, off):
    xs = []
    for k in keys:
        if k not in KB:
            continue
        b = KB[k]["bb"]; o = off.get(k, (0, 0, 0))
        xs.append([b[0] + o[0], b[1] + o[1], b[2] + o[2], b[3] + o[0], b[4] + o[1], b[5] + o[2]])
    if not xs:
        return None
    return [min(x[0] for x in xs), min(x[1] for x in xs), min(x[2] for x in xs), max(x[3] for x in xs), max(x[4] for x in xs), max(x[5] for x in xs)]


def overlay(step, cv):
    W, H = cv["W"], cv["H"]
    off = step["off"]
    el = []
    # 화살표 (같은 offset 묶음마다 하나)
    groups = {}
    for k, v in off.items():
        if tuple(v) == (0, 0, 0):
            continue
        groups.setdefault(tuple(v), []).append(k)
    for v, keys in groups.items():
        bb = bb_of(keys, {})
        if not bb:
            continue
        c0 = ((bb[0] + bb[3]) / 2, (bb[1] + bb[4]) / 2, (bb[2] + bb[5]) / 2)
        c1 = (c0[0] + v[0], c0[1] + v[1], c0[2] + v[2])
        p0 = proj(cv, c0); p1 = proj(cv, c1)
        dx, dy = p0[0] - p1[0], p0[1] - p1[1]
        L = math.hypot(dx, dy)
        if L < 40:
            continue
        a = (p1[0] + dx * 0.28, p1[1] + dy * 0.28)
        b = (p1[0] + dx * 0.80, p1[1] + dy * 0.80)
        el.append(arrow(a, b))
    # 번호 동그라미
    placed = []
    for i, (pid, qty, keys) in enumerate(step["parts"]):
        if not keys:
            continue
        best = None
        for k in keys:
            o = off.get(k, (0, 0, 0))
            for c in sol_centers(k):
                cc = (c[0] + o[0], c[1] + o[1], c[2] + o[2])
                dep = dot(cc, cv["d"])
                if best is None or dep < best[0]:
                    best = (dep, cc)
        if best is None:
            continue
        p = proj(cv, best[1])
        if not (0 <= p[0] <= W and 0 <= p[1] <= H):
            continue
        q = place_badge(p, placed, W, H)
        placed.append(q)
        el.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#1a237e" stroke-width="3"/>' % (p[0], p[1], q[0], q[1]))
        el.append('<circle cx="%.1f" cy="%.1f" r="6" fill="#1a237e"/>' % p)
        el.append('<circle cx="%.1f" cy="%.1f" r="25" fill="#1a237e" stroke="white" stroke-width="4"/>' % q)
        el.append('<text x="%.1f" y="%.1f" font-size="30" font-weight="700" fill="white" text-anchor="middle" dominant-baseline="central">%d</text>' % (q[0], q[1] + 1, i + 1))
    # 방향 표시
    el.append(compass(cv))
    if step["id"] == "A1":
        el.append(dims_A1(cv))
    return '<svg class="ov" viewBox="0 0 %d %d">%s</svg>' % (W, H, "".join(el))


def place_badge(p, placed, W, H):
    cands = []
    for ang in (225, 315, 135, 45, 270, 180, 0, 90):
        for dist in (70, 110, 150):
            q = (p[0] + dist * math.cos(math.radians(ang)), p[1] + dist * math.sin(math.radians(ang)))
            if not (40 < q[0] < W - 40 and 40 < q[1] < H - 40):
                continue
            if q[0] < 230 and q[1] > H - 230:   # 방향 표시 자리
                continue
            dmin = min([math.hypot(q[0] - r[0], q[1] - r[1]) for r in placed] + [999])
            cands.append((-(min(dmin, 160)) + dist * 0.15, q))
    if not cands:
        return (min(max(p[0], 40), W - 40), min(max(p[1] - 60, 40), H - 40))
    cands.sort(key=lambda t: t[0])
    return cands[0][1]


def arrow(a, b, col="#e53935", w=12):
    dx, dy = b[0] - a[0], b[1] - a[1]
    L = math.hypot(dx, dy)
    ux, uy = dx / L, dy / L
    hl = min(34, L * 0.45); hw = 20
    bx, by = b[0] - ux * hl, b[1] - uy * hl
    pts = "%.1f,%.1f %.1f,%.1f %.1f,%.1f" % (b[0], b[1], bx - uy * hw, by + ux * hw, bx + uy * hw, by - ux * hw)
    return ('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="white" stroke-width="%d" stroke-linecap="round"/>'
            '<polygon points="%s" fill="white" stroke="white" stroke-width="8" stroke-linejoin="round"/>'
            '<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="%s" stroke-width="%d" stroke-linecap="round"/>'
            '<polygon points="%s" fill="%s"/>') % (a[0], a[1], bx, by, w + 8, pts, a[0], a[1], bx, by, col, w, pts, col)


def compass(cv):
    ox, oy = 105, cv["H"] - 95
    out = ['<rect x="%d" y="%d" width="196" height="176" rx="14" fill="white" fill-opacity="0.88" stroke="#90a4ae" stroke-width="2"/>' % (ox - 95, oy - 85)]
    for vec, lab, col in (((0, -1, 0), "앞", "#c62828"), ((1, 0, 0), "오른쪽", "#1565c0"), ((0, 0, 1), "위", "#2e7d32")):
        x, y = dot(vec, cv["r"]), -dot(vec, cv["u"])
        L = math.hypot(x, y)
        if L < 0.25:
            continue
        x, y = x / L * 62, y / L * 62
        out.append(arrow((ox, oy), (ox + x, oy + y), col, 6))
        tx, ty = ox + x * 1.32, oy + y * 1.32
        out.append('<text x="%.1f" y="%.1f" font-size="25" font-weight="700" fill="%s" text-anchor="middle" dominant-baseline="central">%s</text>' % (tx, ty, col, lab))
    return "".join(out)


def dims_A1(cv):
    out = []
    pts = []
    for z, lab in ((0, "0"), (180, "180"), (440, "440"), (590, "590")):
        p = proj(cv, (-180, -180, z))
        pts.append((p, lab))
    xline = min(p[0] for p, _ in pts) - 70
    out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#263238" stroke-width="3"/>' % (xline, pts[0][0][1], xline, pts[-1][0][1]))
    for p, lab in pts:
        out.append('<line x1="%.1f" y1="%.1f" x2="%.1f" y2="%.1f" stroke="#263238" stroke-width="2" stroke-dasharray="6,5"/>' % (p[0], p[1], xline, p[1]))
        out.append('<text x="%.1f" y="%.1f" font-size="30" font-weight="700" fill="#263238" text-anchor="end" dominant-baseline="central">%s</text>' % (xline - 10, p[1], lab))
    out.append('<text x="%.1f" y="%.1f" font-size="24" fill="#263238" text-anchor="end">레일 아랫면 높이 (mm)</text>' % (xline - 6, pts[-1][0][1] - 40))
    return "".join(out)


# ---------------------------------------------------------------- 부품 그림
def part_img(pid, big=False):
    p = SP.P[pid]
    if p["kind"] == "cad":
        return '<img src="r/T_%s.png">' % pid
    if p["kind"] == "icon":
        return SV.tape_svg()
    return SV.icon_svg(p["spec"])


def esc(t):
    return t  # 본문에 <b> 허용


# ---------------------------------------------------------------- 쪽 틀
PAGES = []
PAGE_NO = [0]


def page(body, cls="", sec=None):
    PAGE_NO[0] += 1
    foot = '<div class="foot"><span>말벌 자동 마킹 트랩 · 조립 설명서 · 팀 초벌</span><span>%d</span></div>' % PAGE_NO[0]
    PAGES.append('<section class="page %s">%s%s</section>' % (cls, body, foot))


def header(num, title, place, col, sub=""):
    return ('<div class="hdr" style="--c:%s"><div class="num">%s</div><div class="ttl">%s%s</div><div class="place">%s</div></div>'
            % (col, num, title, ('<span class="sub">%s</span>' % sub) if sub else "", place))


def step_page(s):
    col = SEC[s["sec"]][1]
    cv = load_cam("S_" + s["id"])
    ov = overlay(s, cv)
    parts = []
    for i, (pid, qty, keys) in enumerate(s["parts"]):
        p = SP.P[pid]
        badge = '<span class="pb">%d</span>' % (i + 1) if keys else '<span class="pb nob">%d</span>' % (i + 1)
        parts.append('<div class="pc">%s<div class="pimg">%s</div><div class="pq">×%d</div><div class="pn">%s</div></div>' % (badge, part_img(pid), qty, p["name"]))
    txt = "".join("<li>%s</li>" % t for t in s["text"])
    notes = "".join('<div class="warn"><b>조심</b> %s</div>' % w for w in s["warns"]) + "".join('<div class="tip"><b>팁</b> %s</div>' % t for t in s["tips"])
    later = '<div class="later">나중 — 12/2 시연엔 없어도 됨</div>' if s["later"] else ""
    ncol = 4 if len(parts) > 9 else 3
    body = (header(s["id"], s["title"], s["place"], col, SEC[s["sec"]][0]) +
            '<div class="sgrid"><div class="sleft"><div class="simg"><img src="r/S_%s.png">%s%s</div><div class="notes">%s</div></div>'
            '<div class="sside"><div class="pbox"><div class="pbt">이번에 필요한 것</div><div class="pgrid c%d">%s</div></div>'
            '<ol class="stxt">%s</ol></div></div>') % (s["id"], ov, later, notes, ncol, "".join(parts), txt)
    page(body, "step")


def section_page(sec):
    name, col, desc, boxes = SEC[sec]
    ss = [s for s in steps if s["sec"] == sec]
    lst = "".join('<li><b>%s</b> %s <span class="pl">%s</span></li>' % (s["id"], s["title"], s["place"]) for s in ss)
    img = '<img src="r/X_sec_%s.png">' % sec if os.path.exists(os.path.join(R, "X_sec_%s.png" % sec)) else ""
    body = ('<div class="secp" style="--c:%s"><div class="secl"><div class="secn">%s</div><div class="secname">%s</div><p class="secd">%s</p>'
            '%s<div class="secsteps"><div class="h">단계</div><ol>%s</ol></div></div><div class="secimg">%s<div class="cap">주황 = 이 장에서 붙일 부품</div></div></div>') % (
        col, sec, name, desc, ('<p class="secbox">꺼낼 상자: <b>%s</b> (부품 분류표 상자 번호)</p>' % boxes) if boxes else "", lst, img)
    page(body, "secpage")


# ---------------------------------------------------------------- 특별 쪽
def cover():
    body = ('<div class="cover"><div class="cl"><div class="ctag">창의적종합설계 · 팀 초벌</div><h1>말벌 자동 마킹 트랩<br>조립 설명서</h1>'
            '<p class="csub">레고처럼 한 단계씩 — 그림의 <span class="or">주황색</span> 부품을 붙이면 된다.</p>'
            '<div class="cbox"><div class="h">순서</div><ol class="corder">'
            '<li><b>준비</b> 보는 법 · 방향 · 공구 · 나사 1:1 · 기본 기술 · 부품 · 손볼 것</li>'
            '<li><b>A</b> 프레임</li><li><b>B</b> 데크 판과 전기 부품</li><li><b>C</b> 마킹실</li><li><b>D</b> XY 펜 장치</li>'
            '<li><b>E</b> 위판 · 카메라 · 파이</li><li><b>F</b> 선 연결</li><li><b>G</b> 나중 부품</li><li><b>H</b> 마지막 점검</li>'
            '<li><b>부록</b> 217 판 구멍 1:1 도안</li></ol></div>'
            '<p class="cmeta">2026-11-24 · 이승준 (Claude와 정리)<br>기준 설계: 승준 PC FreeCAD <code>D5g_full_SJ1123_플라스틱판_NEMA17</code> — XY 모터 NEMA17 팬케이크, 판 6장 플라스틱 (11/23 최종). '
            '그림은 모두 이 CAD에서 그대로 찍었다. 부품 수는 「부품 분류표」 (11/23)와 맞춤.</p></div>'
            '<div class="cr"><img src="r/X_cover.png"></div></div>')
    page(body, "coverpage")


def howto():
    cv = load_cam("X_top")
    # 방향 글씨
    lab = []
    for p3, t, col in (((0, -185, 0), "앞", "#c62828"), ((0, 185, 0), "뒤", "#455a64"), ((-200, 0, 0), "", "#455a64"), ((205, 0, 0), "", "#455a64")):
        pass
    W, H = cv["W"], cv["H"]
    pf = proj(cv, (0, -190, 600)); pb = proj(cv, (0, 190, 600)); pl = (34, H / 2); pr = (W - 30, H / 2)
    svg = ('<svg class="ov" viewBox="0 0 %d %d">' % (W, H) +
           '<text x="%.0f" y="%.0f" font-size="46" font-weight="800" fill="#c62828" text-anchor="middle">앞 (Y 모터 · 드라이버 보드 쪽)</text>' % (pf[0], pf[1] + 52) +
           '<text x="%.0f" y="%.0f" font-size="46" font-weight="800" fill="#455a64" text-anchor="middle">뒤</text>' % (pb[0], pb[1] - 18) +
           '<text x="%.0f" y="%.0f" font-size="40" font-weight="800" fill="#455a64" text-anchor="middle" transform="rotate(-90 %.0f %.0f)">왼쪽 (비상 정지 버튼)</text>' % (pl[0], pl[1], pl[0], pl[1]) +
           '<text x="%.0f" y="%.0f" font-size="40" font-weight="800" fill="#1565c0" text-anchor="middle" transform="rotate(90 %.0f %.0f)">오른쪽 (X 모터)</text>' % (pr[0], pr[1], pr[0], pr[1]) +
           '</svg>')
    legend = ('<div class="lg"><div class="lgi"><span class="sw or2"></span><div><b>주황</b> = 이번 단계에 붙이는 부품</div></div>'
              '<div class="lgi"><span class="sw gr"></span><div><b>회색</b> = 이미 붙인 부품</div></div>'
              '<div class="lgi"><svg viewBox="0 0 120 40" width="70" height="24">%s</svg><div><b>빨간 화살표</b> = 부품이 들어가는 방향 (그림에서는 조금 떨어뜨려 그림)</div></div>'
              '<div class="lgi"><span class="pb" style="position:static">3</span><div><b>번호</b> = 오른쪽 "이번에 필요한 것" 칸의 같은 번호 부품</div></div>'
              '<div class="lgi"><b class="big">×4</b><div>그 부품을 4개 쓴다</div></div>'
              '<div class="lgi"><span class="placeeg">작업대</span><div>장치 밖 책상에서 따로 만든다 / <span class="placeeg">프레임</span> 장치에 바로 붙인다</div></div>'
              '<div class="lgi"><div class="warn mini"><b>조심</b></div><div>틀리면 부서지거나 다시 풀어야 하는 것</div></div>'
              '<div class="lgi"><div class="tip mini"><b>팁</b></div><div>알면 쉬워지는 것</div></div>'
              '<div class="lgi"><div class="later mini">나중</div><div>12/2 시연엔 없어도 되는 단계 (G장)</div></div></div>') % arrow((10, 20), (110, 20), "#e53935", 8)
    body = (header("준비", "이 설명서 보는 법 · 방향 약속", "", "#37474f") +
            '<div class="two"><div><h3>그림 읽는 법</h3>%s'
            '<h3>단계마다 하는 일</h3><ol class="stxt"><li>오른쪽 칸의 부품과 나사를 <b>먼저 다 꺼내</b> 개수를 센다.</li><li>그림과 같은 방향으로 장치를 돌려 놓는다 (그림 왼쪽 아래 방향 표시).</li><li>번호 순서대로 한다. 볼트는 처음엔 손으로만, 모양이 다 맞으면 꽉.</li><li>끝나면 그림과 같은지 본다 → 다음 쪽.</li></ol></div>'
            '<div><h3>방향 약속 — 위에서 내려다본 모습</h3><div class="simg small"><img src="r/X_top.png">%s</div>'
            '<p class="note">프레임을 세우면 바로 기둥에 마스킹테이프로 <b>앞 · 뒤 · 왼 · 오른</b>을 써 붙인다. 모든 그림 왼쪽 아래에 <span style="color:#c62828"><b>앞</b></span> · <span style="color:#1565c0"><b>오른쪽</b></span> · <span style="color:#2e7d32"><b>위</b></span> 화살표가 있다.</p></div></div>') % (legend, svg)
    page(body)


def tools():
    body = (header("준비", "준비물 — 공구와 약속", "", "#37474f") +
            '<div class="two"><div><h3>공구</h3><table class="tb">'
            '<tr><th>공구</th><th>어디에</th></tr>'
            '<tr><td>육각렌치 세트 (1.5 ~ 5 mm)</td><td>렌치볼트·무두볼트 — 나사 구멍에 꼭 맞는 크기를 골라 씀</td></tr>'
            '<tr><td>십자 드라이버 작은 것 (#0 · #1) · 보통 (#2)</td><td>서보·카메라·태핑·둥근머리 나사</td></tr>'
            '<tr><td>롱노즈 플라이어 · 작은 스패너</td><td>너트 잡기 (M2 · M2.5 · M3 · M5)</td></tr>'
            '<tr><td>전동 드릴 + 날 Ø2 · Ø3.4 · 접시 날 (또는 Ø8 날을 손으로)</td><td>217 판 구멍 4개 (준비 작업 1)</td></tr>'
            '<tr><td>센터펀치 (또는 못) · 망치 · 클램프 · 보안경</td><td>217 판 구멍 자리 찍기·잡기</td></tr>'
            '<tr><td>평줄 (쇠줄)</td><td>T8 너트 플랜지 갈기 (준비 작업 2)</td></tr>'
            '<tr><td>줄자 · 쇠자 · 삼각자</td><td>레일 높이·자리, 직각</td></tr>'
            '<tr><td>멀티미터</td><td>강압 모듈 전압 5.0 / 7.4 V (F장)</td></tr>'
            '<tr><td>마스킹테이프 · 네임펜</td><td>방향·이름표 (앞·오른쪽·UNO ①② 등)</td></tr>'
            '<tr><td>알코올 · 휴지 · 가위</td><td>폼 양면테이프 붙이기 전 닦기</td></tr>'
            '<tr><td>케이블타이 · 작은 그릇 여러 개</td><td>선 묶기 · 나사 종류별로 나눠 담기</td></tr></table></div>'
            '<div><h3>시작 전에 약속</h3><ol class="stxt">'
            '<li><b>전원은 맨 마지막.</b> F장 끝 \'처음 켜기\' 전까지 어댑터를 꽂지 않는다.</li>'
            '<li>부품은 「부품 분류표」 상자 번호대로 나눠 두고, 각 장 첫 쪽에 적힌 상자를 꺼낸다.</li>'
            '<li>나사는 종류별로 그릇에 — 헷갈리면 다음 쪽 <b>1:1 자</b>에 대 본다.</li>'
            '<li>볼트는 처음엔 손으로, 다 맞은 뒤에 꽉. 아크릴·3D 프린트 판은 <b>세게 조이지 않기</b>, 와셔 받치기, 록타이트 쓰지 않기 (아크릴이 금 감).</li>'
            '<li>모터·서보 축을 억지로 돌리지 않는다 (살살).</li>'
            '<li>드릴·줄질할 때 보안경. 줄질 가루는 털어 내고 조립.</li>'
            '<li>모르는 것은 멈추고 서현에게 — 특히 전기 (F장).</li></ol>'
            '<h3>시간 어림</h3><p class="note">A 프레임 1~1.5시간 · B 데크 1시간 · C 마킹실 1.5시간 · D XY 2~3시간 · E 1시간 · F 선 2~3시간 (두 사람 기준 어림 — 처음이면 더 걸림).</p></div></div>')
    page(body)


ONE = [("m5x8", "M5 × 8"), ("m5x10", "M5 × 10"), ("m5x12", "M5 × 12"), ("m4x8", "M4 × 8"), ("m4x10c", "M4 × 10 접시"),
       ("m3x6", "M3 × 6"), ("m3x8", "M3 × 8"), ("m3x10", "M3 × 10"), ("m3x12", "M3 × 12"), ("m3x16", "M3 × 16"), ("m3x20", "M3 × 20"),
       ("m3x8c", "M3 × 8 접시"), ("m3x12c", "M3 × 12 접시"), ("m3x8t", "M3 × 8 태핑"), ("m3x6set", "M3 × 6 무두"), ("m3x8set", "M3 × 8 무두"),
       ("m2x8", "M2 × 8"), ("m25x5", "M2.5 × 5")]


def onetoone():
    cells = []
    for pid, lab in ONE:
        cells.append('<div class="oc"><div class="osvg">%s</div><div class="ol">%s</div></div>' % (SV.onetoone_svg(SP.P[pid]["spec"], lab), lab))
    nuts = "".join('<div class="oc"><div class="osvg">%s</div><div class="ol">%s</div></div>' % (SV.onetoone_svg(("nut", d, 0), ""), "M%s 너트" % d) for d in (2, 2.5, 3, 5))
    nuts += '<div class="oc"><div class="osvg">%s</div><div class="ol">M3 와셔</div></div>' % SV.onetoone_svg(("washer", 3, 0), "")
    nuts += '<div class="oc"><div class="osvg">%s</div><div class="ol">스프링너트 M5</div></div>' % SV.onetoone_svg(("springnut", 5, 0), "")
    gauge = ('<svg style="width:30mm;height:16mm" viewBox="0 0 30 16"><circle cx="8" cy="8" r="4.2" fill="none" stroke="#c62828" stroke-width="0.25"/>'
             '<circle cx="8" cy="8" r="0.3" fill="#c62828"/><text x="15" y="7" font-size="2.6" fill="#c62828">Ø8.4</text><text x="15" y="10.5" font-size="2.1" fill="#333">이 원보다</text><text x="15" y="13.2" font-size="2.1" fill="#333">크면 X</text></svg>')
    ruler = ['<svg style="width:102mm;height:9mm" viewBox="-1 0 102 9"><line x1="0" y1="2" x2="100" y2="2" stroke="#000" stroke-width="0.3"/>']
    for i in range(0, 101):
        h = 4 if i % 10 == 0 else (3 if i % 5 == 0 else 1.8)
        ruler.append('<line x1="%d" y1="2" x2="%d" y2="%.1f" stroke="#000" stroke-width="0.15"/>' % (i, i, 2 + h))
        if i % 10 == 0:
            ruler.append('<text x="%d" y="8.6" font-size="2.2" text-anchor="middle">%d</text>' % (i, i))
    ruler.append('</svg>')
    body = (header("준비", "나사 찾기 자 — 실제 크기 1:1", "", "#37474f",
                   "인쇄: '실제 크기 (100 %)', '페이지에 맞춤' 끄기") +
            '<div class="ruler">%s<span>← 이 자가 쇠자로 <b>100 mm</b>인지 먼저 확인</span></div>' % "".join(ruler) +
            '<p class="note">나사를 그림 위에 눕혀 대 본다 — 길이 = 머리 밑에서 끝까지 (접시머리는 머리 꼭대기부터). 굵기 M3 = 지름 3 mm.</p>'
            '<div class="ogrid">%s</div><div class="ogrid">%s<div class="oc gauge"><div class="osvg">%s</div><div class="ol">M4 접시머리 머리 재기 (YB 혀 쪽 2개)</div></div></div>' % ("".join(cells), nuts, gauge))
    page(body, "onepage")


def skills():
    items = [
        ("스프링너트 넣기", '2020 막대 홈에 너트를 비스듬히 넣고 렌치 끝으로 눌러 <b>90° 돌리면</b> 스프링이 홈 안에서 너트를 잡는다. 볼트 넣기 전에 너트를 구멍 밑으로 밀어 맞춘다.', "sn"),
        ("L 브래킷", '브래킷 구멍 ↔ 스프링너트를 맞추고 볼트를 손으로 2~3바퀴 → 막대 위치를 맞춘 뒤 조인다. 브래킷은 두 막대가 만나는 <b>안쪽 모서리</b>.', "lb"),
        ("손으로 먼저, 마지막에 꽉", '볼트는 처음엔 손으로만. 한 덩어리 모양이 다 맞으면 <b>대각선 순서</b>로 조금씩 꽉.', ""),
        ("태핑 나사 (3D 프린트)", '구멍 (Ø2.5)에 똑바로 세워 천천히. 멈추면 끝 — 더 돌리면 플라스틱 나사산이 뭉개진다.', ""),
        ("접시머리", '머리가 판 속으로 쏙 들어가 평평해지는 나사. 판에서 <b>오목하게 파인 (접시) 구멍 쪽</b>에서 넣는다.', ""),
        ("너트 잡기", '롱노즈나 스패너로 너트를 잡고 반대쪽 나사를 돌린다. 좁은 곳은 너트를 마스킹테이프로 렌치 끝에 붙여서 넣는다.', ""),
        ("폼 양면테이프", '붙일 곳을 알코올로 닦고 → 붙이고 → 10초 꾹 누른다. 나중에 떼기 쉽게 한쪽 끝을 접어 둔다.', ""),
        ("아크릴 · 프린트 판", '와셔 받치기, 세게 조이지 않기, 나사 고정제 (록타이트) 쓰지 않기. 플라스틱은 시간이 지나면 조금 눌리니 <b>시연 전날 한 번 더 조이기</b>.', ""),
    ]
    snsvg = ('<svg viewBox="0 0 60 34" style="width:62mm;height:35mm"><path d="M5,4 h50 v26 h-50 z" fill="#d6d9de" stroke="#555" stroke-width="0.5"/>'
             '<path d="M22,4 h16 v6 h5 v10 h-26 v-10 h5 z" fill="white" stroke="#555" stroke-width="0.5"/>'
             '<rect x="21" y="12" width="18" height="5" rx="1" fill="#9aa1ab" stroke="#333" stroke-width="0.4"/>'
             '<circle cx="30" cy="20" r="1.6" fill="#555"/><text x="30" y="32.5" font-size="3.2" text-anchor="middle">2020 홈 자른 면 — 너트가 홈 안에서 돌아 걸림</text>'
             '<path d="M44,9 a6,6 0 1 1 -2,-4" fill="none" stroke="#e53935" stroke-width="0.9"/><polygon points="42,3 45.5,6 41,7" fill="#e53935"/></svg>')
    cards = []
    for t, d, k in items:
        extra = snsvg if k == "sn" else (('<img class="sk" src="r/T_lbr.png">') if k == "lb" else "")
        cards.append('<div class="skc"><div class="skt">%s</div><div class="skd">%s</div>%s</div>' % (t, d, extra))
    body = header("준비", "기본 기술 8가지", "", "#37474f") + '<div class="skgrid">%s</div>' % "".join(cards)
    page(body)


BOXORDER = [("5-①", "상자 5-① 프레임 · 데크"), ("5-②", "상자 5-② 전원 · 배선 · 두뇌"), ("1", "상자 1 액추부 (모터 · 서보 · 드라이버 · 스위치)"),
            ("2-①", "상자 2-① 말벌 길 · 마킹실"), ("2-②", "상자 2-② XY · 펜"), ("3", "상자 3 카메라부"), ("5-③", "상자 5-③ 나사 · 기둥 · 소모품")]


def totals():
    tot = {}; tot_l = {}
    for s in steps:
        for pid, q, _ in s["parts"]:
            if s["later"]:
                tot_l[pid] = tot_l.get(pid, 0) + q
            else:
                tot[pid] = tot.get(pid, 0) + q
    return tot, tot_l


def parts_pages():
    tot, tot_l = totals()
    blocks = []
    for box, title in BOXORDER:
        cards = []
        for pid, p in SP.P.items():
            if p["box"] != box:
                continue
            n = tot.get(pid, 0); nl = tot_l.get(pid, 0)
            if n == 0 and nl == 0:
                continue
            cnt = ("×%d" % n if n else "") + (' <span class="lt">나중 ×%d</span>' % nl if nl else "")
            if pid == "foam":
                cnt = "1 롤"
            cards.append('<div class="pcard"><div class="pimg">%s</div><div class="pcn">%s</div><div class="pcd">%s</div><div class="pcq">%s</div></div>' % (part_img(pid), p["name"], p["desc"], cnt))
        blocks.append((title, cards))
    # 3쪽으로 나눔
    groups = [blocks[0:2], blocks[2:4], blocks[4:5], blocks[5:7]]
    for gi, g in enumerate(groups):
        html_b = "".join('<div class="pbk"><div class="pbkt">%s</div><div class="pcards">%s</div></div>' % (t, "".join(c)) for t, c in g)
        body = header("준비", "부품 한눈에 (%d/%d)" % (gi + 1, len(groups)), "", "#37474f", "개수 = 이 설명서 전체에서 쓰는 수 (산 것은 예비가 더 있음)") + html_b
        page(body, "partspage")


def nut_file_svg():
    def flange(cx, cy, mode):
        out = ['<circle cx="%d" cy="%d" r="22" fill="#e3c47a" stroke="#6d5a2a" stroke-width="1"/>' % (cx, cy),
               '<circle cx="%d" cy="%d" r="10.2" fill="#caa75a" stroke="#6d5a2a" stroke-width="1"/>' % (cx, cy),
               '<circle cx="%d" cy="%d" r="4" fill="white" stroke="#6d5a2a" stroke-width="1"/>' % (cx, cy)]
        for a in (45, 135, 225, 315):
            out.append('<circle cx="%.1f" cy="%.1f" r="1.8" fill="white" stroke="#6d5a2a" stroke-width="0.8"/>' % (cx + 16 * math.cos(math.radians(a)), cy + 16 * math.sin(math.radians(a))))
        if mode == "X":
            out.append('<path d="M%.1f,%.1f A22,22 0 0 1 %.1f,%.1f Z" fill="#e53935" fill-opacity="0.75"/>' % (cx - 12.5, cy - 18.1, cx + 12.5, cy - 18.1))
            out.append('<text x="%d" y="%d" font-size="7" text-anchor="middle" fill="#c62828">위 1.5 mm 평평하게</text>' % (cx, cy - 27))
        else:
            for a in (-52, -128, 52, 128):
                x = cx + 21 * math.cos(math.radians(a)); y = cy + 21 * math.sin(math.radians(a))
                out.append('<circle cx="%.1f" cy="%.1f" r="3.2" fill="#e53935" fill-opacity="0.8"/>' % (x, y))
            out.append('<text x="%d" y="%d" font-size="7" text-anchor="middle" fill="#c62828">가장자리 4곳 0.5 mm</text>' % (cx, cy - 27))
        return "".join(out)
    return ('<svg viewBox="0 0 160 70" style="width:100%%;height:auto">%s%s<text x="40" y="66" font-size="7" text-anchor="middle">X 너트 (XN 판)</text>'
            '<text x="120" y="66" font-size="7" text-anchor="middle">Y 너트 (CP 판)</text></svg>') % (flange(40, 36, "X"), flange(120, 36, "Y"))


def prep():
    body = (header("준비", "조립 전에 손볼 것 (준비 작업)", "작업대", "#37474f", "D장 전까지 끝내면 됨") +
            '<div class="prep">'
            '<div class="pp"><div class="ppt">1 · 217 판 (X 모터판) 구멍 4개</div><ol>'
            '<li>맨 뒤 <b>부록 1:1 도안</b>을 실제 크기 (100 %%)로 인쇄 → 50 mm 선을 자로 확인.</li>'
            '<li>점선대로 오려 판의 <b>모터가 붙는 면 (바깥 면)</b>에 원래 구멍 (검은 원)에 맞춰 붙인다.</li>'
            '<li>빨간 십자 4곳을 센터펀치로 찍고 Ø2로 먼저 → Ø3.4로 뚫는다 (판은 클램프로 꽉).</li>'
            '<li><b>뒷면 (레일 쪽)</b>에서 위 2개 (③④)만 접시 (Ø6.6쯤) — M3 접시머리가 판과 평평하게.</li>'
            '<li>구멍 가장자리 거스러미를 큰 날로 살짝 돌려 없앤다.</li></ol></div>'
            '<div class="pp"><div class="ppt">2 · T8 황동 너트 2개 줄질</div>%s<ol>'
            '<li>모터와 같이 온 너트 2개. 바이스·펜치로 잡고 평줄로 문지른다 (황동이라 몇 분).</li>'
            '<li><b>X 너트</b>: 플랜지 위를 1.5 mm 평평하게 (Y 원점 스위치 기판과 닿음).</li>'
            '<li><b>Y 너트</b>: 플랜지 가장자리 4곳을 0.5 mm (LMK8UU 나사와 닿음).</li>'
            '<li>가루를 털고 나사 막대에 끼워 잘 도는지 본다.</li></ol></div>'
            '<div class="pp"><div class="ppt">3 · 3D 프린트 부품 다듬기</div><ol>'
            '<li>실 같은 찌꺼기·받침 자국을 칼로 정리.</li>'
            '<li>구멍이 빡빡하면 같은 지름 드릴 날을 <b>손으로</b> 한 번 훑는다.</li>'
            '<li><b>Ø2.5 구멍은 넓히지 않는다</b> — 태핑·M3 나사가 나사산을 만들어야 함 (XN 판 2개, 마킹실 상자 300의 나사 구멍 8개).</li>'
            '<li>YM 판은 모터 열 때문에 ABS·ASA가 좋다 (PLA뿐이면 2장 뽑아 예비).</li></ol></div>'
            '<div class="pp"><div class="ppt">4 · 받으면 바로 잴 것</div><ol>'
            '<li><b>M4 접시머리 머리 지름</b> ≤ 8.4 mm — 앞쪽 1:1 원에 대 보기 (YB 혀 쪽 2개에 씀).</li>'
            '<li><b>모터 나사 길이</b>: 모터 앞면부터 끝까지 X 155 · Y 132 mm. Y가 <b>131 mm보다 짧으면</b> 서현에게 (펌웨어 Y 끝을 +17로). 길면 괜찮음.</li>'
            '<li><b>T8 너트 구멍 간격</b>: XN · CP 판 구멍에 대 보고 맞는지.</li>'
            '<li><b>모터 앞 나사 구멍 깊이</b>: M3 나사가 바닥에 닿지 않는 길이 (판 3 mm + 구멍 깊이보다 짧게).</li></ol></div>'
            '</div>') % nut_file_svg()
    page(body)


# ---------------------------------------------------------------- 선 연결 (F)
def wiring():
    col = SEC["F"][1]
    chain = ('<div class="chain">'
             '<div class="cb">12 V 5 A 어댑터</div><div class="ca">→</div><div class="cb">DC 잭 변환<br><small>SZH-LC002</small></div><div class="ca">→ P01 →</div>'
             '<div class="cb">퓨즈 5 A<br><small>FHAM1</small></div><div class="ca">→ P02 →</div><div class="cb red">비상 정지<br><small>NC 단자</small></div><div class="ca">→ P03 →</div>'
             '<div class="cb">와고 12 V<br><small>5구 꽉 참</small></div></div>')
    rows = [("P05", "와고 12 V · GND", "DRV8825 보드 VMOT · GND", "빨강·검정 22 AWG", "520"),
            ("P06", "와고 12 V · GND", "MOSFET 보드 V+ · GND", "빨강·검정", "350"),
            ("P07", "와고 12 V · GND", "XL4015 ① IN+ · IN−", "빨강·검정", "280"),
            ("P08", "와고 12 V · GND", "XL4015 ② IN+ · IN−", "빨강·검정", "330"),
            ("P04", "DC 잭 −", "와고 GND", "검정", "180"),
            ("P09", "XL4015 ① OUT+ · OUT− (5.0 V)", "와고 5 V · GND", "빨강·검정", "280"),
            ("P10", "와고 5 V · GND", "센서 쉴드 ① 나사 단자 V · G", "빨강·검정", "230"),
            ("P11", "와고 5 V · GND", "센서 쉴드 ② 나사 단자 V · G", "빨강·검정", "280"),
            ("P12", "XL4015 ② OUT+ · OUT− (7.4 V)", "mightyZAP 선 IR-EW06 빨강 · 검정", "빨강·검정 (+연장)", "200+90")]
    t = "".join("<tr><td><b>%s</b></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % r for r in rows)
    body = (header("F1", "전원 줄 — 12 V 하나로 전부", "데크 위", col, SEC["F"][0]) +
            '<div class="warn big"><b>먼저</b> XL4015 두 개의 전압부터: 어댑터 → 잭 → 퓨즈 → 비상 정지 → 와고 12 V까지만 잇고, XL4015 <b>입력만</b> 연결 → 전원 켜고 멀티미터로 보며 작은 나사를 돌려 ① <b>5.0 V</b>, ② <b>7.4 V</b> → 전원 끄고 그다음에 출력 선을 잇는다. 7.4 V를 5 V 부품에 잇거나 12 V를 서보에 이으면 바로 탄다.</div>'
            + chain +
            '<table class="tb wt"><tr><th>번호</th><th>어디서</th><th>어디로</th><th>선</th><th>길이 mm</th></tr>%s</table>'
            '<div class="two small2"><div><h3>약속 (서현 회로 검사 통과한 규칙)</h3><ul class="stxt">'
            '<li>12 V를 쓰는 것은 모두 <b>비상 정지 뒤</b>에 — 비상 정지를 누르면 다 꺼짐.</li>'
            '<li>7.4 V는 mightyZAP <b>만</b>. 5 V (+5V_B)는 서보·게이트·스위치.</li>'
            '<li>UNO의 5V 핀과 +5V_B (와고 5 V)는 <b>잇지 않는다</b>. GND만 서로 잇는다.</li>'
            '<li>와고: 선을 8 mm 벗겨 레버 올리고 끝까지 넣고 레버 내림 → 살짝 당겨 안 빠지면 OK.</li>'
            '<li>나사 단자: 선을 벗겨 꼬은 뒤 넣고 조임. 잔 가닥이 옆 단자에 닿지 않게.</li></ul></div>'
            '<div><h3>파이 (라즈베리 파이 5)</h3><ul class="stxt"><li>전원은 따로 — 공식 27 W USB-C 어댑터.</li><li>USB A–B 선 2개: 파이 ↔ UNO ①, 파이 ↔ UNO ②.</li>'
            '<li>카메라 FPC (500 mm, 12/01쯤 옴 — 그 전엔 300 mm 예비): 파이 CAM 단자 ↔ 카메라.</li></ul>'
            '<p class="note">근거: 레포 <code>design/2026-11-17_회로_배선표_서현.md</code> (11/17 판). 길이 = 자를 길이 (어림 + 10 %%). 받고 확인할 것 (쉴드 SEL 점퍼, MOSFET 단자 이름, 드라이버 보드 핀 이름)은 서현 문서 4장.</p></div></div>') % t
    page(body, "wpage")
    u1 = [("D2", "mightyZAP 신호 (IR-EW06 흰 선)", "S01"), ("D6 · D7 · D8", "X 모터 STEP · DIR · EN → 드라이버 보드", "S02"),
          ("D9 · D10 · D11", "Y 모터 STEP · DIR · EN → 드라이버 보드 (+ GND 1가닥)", "S02"), ("A0", "펜 서보 SG-90 (3핀 그대로)", "V01"),
          ("A4", "X 원점 스위치 (G · V · S)", "S03"), ("A5", "Y 원점 스위치 (G · V · S)", "S04")]
    u2 = [("D2", "레일 감지 — 같은 줄 V → 10 kΩ → S (비상 정지 누르면 LOW)", ""), ("D3 · D4 · D6", "MOSFET TRIG: Q1 LED 2 · Q4 게이트 송신 3 · Q3 펌프 (+ GND)", "S05"),
          ("D9 · D10 · D11", "문 서보: 입구 112 · 격리 170 · 방생 176", "V02~V04"), ("A0 · A3 · A4", "빛 게이트 수신 G2 · G3b · G5 (3선: 흰 S · 빨강 V · 검정 G)", "G01~G03"),
          ("A1 · A2 · A5 의 V 핀만", "빛 게이트 송신 빨강 G2 · G3b · G5", "G01~G03"), ("—", "송신 검정 3가닥 → MOSFET Q4 OUT− (함께 조임)", "G04~G06")]
    t1 = "".join("<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>" % r for r in u1)
    t2 = "".join("<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>" % r for r in u2)
    body = (header("F2", "아두이노 핀 — 무엇을 어디에 꽂나", "데크 위", col, SEC["F"][0]) +
            '<p class="note">센서 쉴드의 3핀 줄 = <b>G (검정·갈색) · V (빨강) · S (신호)</b>. 서보 선은 갈색이 G 쪽. 꽂기 전에 UNO에 붙인 이름표 (① 움직임 / ② 문)를 다시 본다.</p>'
            '<div class="two"><div><h3>UNO ① — 움직임 (펌웨어 trap_motion v0.4)</h3><table class="tb"><tr><th>핀</th><th>꽂는 것</th><th>선 번호</th></tr>%s</table>'
            '<h3>드라이버 보드 → 모터</h3><table class="tb"><tr><td><b>X A1 A2 B1 B2</b></td><td>X 모터 4선 (M01)</td></tr><tr><td><b>Y A1 A2 B1 B2</b></td><td>Y 모터 4선 (M02, 빔과 같이 움직임 — 휨 고리)</td></tr></table>'
            '<div class="warn"><b>조심</b> 모터 선은 전원을 끈 상태에서만 꽂고 뺀다. 드라이버 전류 (Vref)는 NEMA17 정격에 맞춰 서현 튜닝표대로.</div></div>'
            '<div><h3>UNO ② — 문 · 센서 · 조명 (trap_doors)</h3><table class="tb"><tr><th>핀</th><th>꽂는 것</th><th>선 번호</th></tr>%s</table>'
            '<h3>MOSFET 출력</h3><table class="tb"><tr><td><b>Q1</b></td><td>LED 모듈 2개 (카메라 판 양옆) — L01</td></tr><tr><td><b>Q3</b></td><td>펌프 (나중, 급이부) — L02</td></tr><tr><td><b>Q4</b></td><td>빛 게이트 송신 검정 3가닥 — G04~G06</td></tr></table>'
            '<div class="tip"><b>팁</b> 움직이는 선 (펜 서보 · Y 모터 · Y 원점)은 넉넉히 늘어뜨려 케이블타이로 고정점만 잡는다 — 빔을 끝에서 끝까지 밀어 보며 당기지 않는지 확인.</div></div></div>') % (t1, t2)
    page(body, "wpage")


def final_check():
    col = SEC["H"][1]
    body = (header("H", "마지막 점검 · 처음 켜기", "", col) +
            '<div class="two"><div><h3>전원 넣기 전 (손으로)</h3><ul class="chk">'
            '<li>프레임 대각선 두 길이가 같다 (2 mm 안) · 네 기둥이 바닥에 다 닿는다.</li>'
            '<li>빔 (X)을 왼쪽 끝 ↔ 오른쪽 끝까지 밀면 같은 힘으로 간다.</li>'
            '<li>캐리지 (Y)를 앞 끝 ↔ 뒤 끝까지 — 걸림 없음.</li>'
            '<li>펜 홀더를 들었다 놓으면 스르륵 내려온다.</li>'
            '<li>원점 스위치 X · Y가 손으로 밀었을 때 \'딸깍\'.</li>'
            '<li>문 3개를 손으로 살살 열고 닫아 걸림 없음 · mightyZAP 막대 위로 걸림 없음.</li>'
            '<li>마커 끝이 격자판 위, 뚜껑 컵 자리 확인.</li>'
            '<li>모든 볼트 조임 · 플라스틱 판은 시연 전날 다시.</li></ul>'
            '<h3>전기 확인 (어댑터 빼고)</h3><ul class="chk"><li>퓨즈 5 A가 꽂혀 있다.</li><li>비상 정지를 누르면 와고 12 V가 끊긴다 (멀티미터 통전).</li>'
            '<li>XL4015 ① 5.0 V · ② 7.4 V로 맞춰 놓았다 (F1).</li><li>DRV8825 방향 · 모터 선 4가닥 확인 (사진 → 서현).</li></ul></div>'
            '<div><h3>처음 켜기 (서현과 같이)</h3><ol class="stxt"><li>한 사람은 <b>비상 정지 위에 손</b>.</li>'
            '<li>파이 → UNO 두 개 USB, 펌웨어 trap_motion <b>v0.4</b> (100 걸음/mm) · trap_doors 올리기 (서현).</li>'
            '<li>12 V를 넣고 냄새·소리 이상하면 바로 비상 정지.</li><li>원점 찾기 → 1 mm 명령으로 실제 이동 재기 (서현 튜닝표).</li>'
            '<li>문 닫힘 각도에 맞춰 혼 다시 끼우기 (C8), 펜 들 각도 60° 넘지 않기 (D6).</li><li>표본 말벌로: 입구 문 닫힘 → 바닥 올림 → 점 → 방생 문 열림.</li></ol>'
            '<h3>이럴 땐</h3><table class="tb"><tr><th>증상</th><th>해볼 것</th></tr>'
            '<tr><td>빔이 빡빡함</td><td>SK08 볼트·조임 나사를 풀고 빔을 몇 번 왕복 → 부드러운 자리에서 다시 조임</td></tr>'
            '<tr><td>캐리지가 빡빡함</td><td>Y 봉 끝 나사 4개를 살짝 풀고 왕복 → 다시 조임 · T8 너트 나사를 살짝 풀어 너트가 스스로 맞게</td></tr>'
            '<tr><td>펜이 안 내려옴</td><td>어깨 볼트 너트가 너무 조였나 · 접시머리가 튀어나왔나 (D3 · D5)</td></tr>'
            '<tr><td>모터가 윙 소리만</td><td>모터 선 쌍 (A · B) 바뀜 · 전류 · 너트가 걸림 — 서현</td></tr>'
            '<tr><td>문이 덜 닫힘</td><td>혼을 한 톱니씩 돌려 다시 끼움 (C8)</td></tr>'
            '<tr><td>게이트가 늘 막힘</td><td>송신·수신이 빔 구멍에 마주 보나 (C9)</td></tr></table></div></div>')
    page(body)


def sources():
    body = (header("—", "어디서 확인했나 (근거)", "", "#37474f") +
            '<ul class="stxt src">'
            '<li>그림 · 자리 · 나사 크기: 승준 PC FreeCAD <code>FreeCAD_2026-11-18\\D5g_full_SJ1123_플라스틱판_NEMA17.FCStd</code> (11/23 최종 — 플라스틱 판 6장 · NEMA17 · T8). 이 파일을 열어 사본 문서에서 단계마다 찍었고, 원본은 바꾸지 않음. 203p 마커 클립은 <code>docs/2026-11-18_승준_FreeCAD_파일_기록.md</code> 3-2 코드로 그려 넣음 (CAD의 P 클립 대신).</li>'
            '<li>부품 이름 · 개수 · 상자: <code>design/2026-11-23_승준_부품분류표_조립파트별.pdf</code>, 「내가 뭐한거지???」 11/24판 A · C장.</li>'
            '<li>XY 변경 (217 판 바깥 면, 접시머리, YB 혀, 줄질 2곳, 나사 M4 · M3): <code>design/2026-11-23_승준_XY마킹부_설계변경_설명.pdf</code>, <code>docs/2026-11-23_승준_XY모터_NEMA17_팬케이크_변경.md</code>.</li>'
            '<li>선 연결: <code>design/2026-11-17_회로_배선표_서현.md</code> (11/17 판 — 모터만 NEMA17로 바뀜, 핀은 같음).</li>'
            '<li>CAD에 없는 것 (실물 보고 정함): UNO 기둥 아래 고정 방식 (암-암/수-암), 게이트 송·수신 위아래, 혼 각도, 모터 앞 나사 길이, M4 접시 머리 지름, T8 너트 구멍 간격.</li>'
            '<li>시간 어림 · 조립 순서는 Claude 판단 (CAD에서 나사 머리·드라이버가 닿는 순서를 보고 정함) — 실물에서 더 쉬운 순서가 있으면 바꿔도 됨.</li></ul>')
    page(body)


CSS = open(os.path.join(BASE, "style.css"), encoding="utf-8").read()


def build():
    cover(); howto(); tools(); onetoone(); skills(); parts_pages(); prep()
    for sec in "ABCDE":
        section_page(sec)
        for s in steps:
            if s["sec"] == sec:
                step_page(s)
    # F 선 연결
    page('<div class="secp" style="--c:%s"><div class="secl"><div class="secn">F</div><div class="secname">%s</div><p class="secd">%s</p>'
         '<p class="secbox">꺼낼 상자: <b>5-②</b> · 전선 빨강·검정 10 m · 멀티미터</p><div class="secsteps"><div class="h">쪽</div><ol><li><b>F1</b> 전원 줄</li><li><b>F2</b> 아두이노 핀</li></ol></div></div>'
         '<div class="secimg"><img src="r/X_demo.png"><div class="cap">12/2 시연 모양 (G장 빼고)</div></div></div>' % (SEC["F"][1], SEC["F"][0], SEC["F"][2]), "secpage")
    wiring()
    section_page("G")
    for s in steps:
        if s["sec"] == "G":
            step_page(s)
    final_check()
    sources()
    doc = '<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><title>말벌 자동 마킹 트랩 조립 설명서</title><style>%s</style></head><body>%s</body></html>' % (CSS, "".join(PAGES))
    open(os.path.join(BASE, "manual.html"), "w", encoding="utf-8").write(doc)
    print("pages", PAGE_NO[0])


if __name__ == "__main__":
    build()
