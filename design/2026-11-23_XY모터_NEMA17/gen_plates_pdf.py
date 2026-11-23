# -*- coding: utf-8 -*-
"""XY 모터 NEMA17 팬케이크로 바꾸며 판 4장(217·211·XN·CP)을 손으로 고치는 것 — PDF 2개 (승준 11/23, CAP-AI-SJ-63)
  ① 판수정_비교.pdf : 원래 ↔ 수정 후 (1:1) + FreeCAD 그림 + 살 것
  ② 판구멍_1대1도안.pdf : 수정 후만, 십자 표시 — 실제 크기(100 %)로 인쇄해 판에 붙이고 펀치
판 모양·구멍 = plates_2d.json (승준 PC FreeCAD D5g_full_SJ1118에서 뽑음). 실행: python3 gen_plates_pdf.py (나눔고딕 필요 — NANUM_DIR)"""
import json, math, os, glob
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(os.path.join(HERE, "plates_2d.json"), encoding="utf-8"))

def font_path(name):
    for d in [os.environ.get("NANUM_DIR", ""), "/home/claude/fonts", "/usr/share/fonts/truetype/nanum",
              os.path.expanduser("~/.fonts"), r"C:\Windows\Fonts"]:
        f = glob.glob(os.path.join(d, name)) if d else []
        if f: return f[0]
    raise SystemExit("나눔고딕 " + name + " 을 못 찾음 — NANUM_DIR 지정")
pdfmetrics.registerFont(TTFont("NG", font_path("NanumGothic.ttf")))
pdfmetrics.registerFont(TTFont("NGB", font_path("NanumGothicBold.ttf")))

W, H = A4
RED = colors.HexColor("#d62728"); BLUE = colors.HexColor("#1f77b4"); GRAY = colors.HexColor("#9a9a9a")
PURPLE = colors.HexColor("#7b3fa0"); YEL = colors.HexColor("#f3d27a"); DARK = colors.HexColor("#222222")
CIRC = "①②③④⑤⑥"

def uv(pl, p):                      # 판 전체 좌표 (2성분) → 보는 방향 2D (u 오른쪽, v 위)
    su = pl["axes"]["u"][1]; return (su * p[0], p[1])

def bbox(pl):
    pts = [uv(pl, q) for q in pl["outer"]]
    return min(a for a, b in pts), max(a for a, b in pts), min(b for a, b in pts), max(b for a, b in pts)

def txt(c, x, y, s, size=9, bold=False, color=DARK, anchor="l"):
    s = s.replace("\u2212", "-")                # 나눔고딕에 − 글자가 없음
    c.setFillColor(color); c.setFont("NGB" if bold else "NG", size)
    {"l": c.drawString, "c": c.drawCentredString, "r": c.drawRightString}[anchor](x, y, s)

def para(c, x, y, lines, size=9, lead=1.45, bold_first=False, color=DARK):
    for i, s in enumerate(lines):
        txt(c, x, y - i * size * lead, s, size, bold=(bold_first and i == 0), color=color)
    return y - len(lines) * size * lead

def scale_bar(c, x, y):            # 50 mm 확인 선
    c.setStrokeColor(DARK); c.setLineWidth(0.8)
    c.line(x, y, x + 50 * mm, y)
    for k in range(6):
        t = 2.2 if k % 5 == 0 else 1.2
        c.line(x + k * 10 * mm, y, x + k * 10 * mm, y + t * mm)
    txt(c, x, y - 4 * mm, "↑ 이 선이 자로 50 mm인지 확인 (인쇄: 실제 크기 100 %, '페이지에 맞춤' 끄기)", 7.5)

def cross(c, x, y, r):
    c.line(x - r, y, x + r, y); c.line(x, y - r, x, y + r)

def draw_plate(c, key, state, ox, oy, number=True, template=False):
    """ox, oy = 판 bbox 왼쪽 아래가 놓일 쪽 좌표 (pt). 1:1."""
    pl = P[key]; u0, u1, v0, v1 = bbox(pl)
    T = lambda p: (ox + (uv(pl, p)[0] - u0) * mm, oy + (uv(pl, p)[1] - v0) * mm)
    cx, cy = T(pl["center"])
    # 217 수정 후: 뒷면 레일 닿는 띠 (z 440 ~ 판 위)
    if key == "217" and state == "after" and not template:
        a = T([-87.0, 440.0]); b = T([-43.0, 459.0])
        c.setFillColor(YEL); c.setStrokeColor(YEL); c.rect(min(a[0], b[0]), a[1], abs(b[0] - a[0]), b[1] - a[1], fill=1, stroke=0)
    # 외곽
    c.setStrokeColor(DARK); c.setLineWidth(0.9 if not template else 0.6)
    if template: c.setDash(3, 2)
    pth = c.beginPath(); q = [T(p) for p in pl["outer"]]; pth.moveTo(*q[0])
    for p in q[1:]: pth.lineTo(*p)
    c.drawPath(pth, stroke=1, fill=0); c.setDash()
    # 모터·너트 자리 (점선)
    if not template:
        c.setLineWidth(0.6); c.setDash(2, 1.5)
        if key in ("217", "211"):
            s = (28.0 if state == "before" else 42.0) / 2 * mm
            c.setStrokeColor(BLUE); c.rect(cx - s, cy - s, 2 * s, 2 * s, fill=0, stroke=1)
        else:
            r = (19.05 if state == "before" else 22.0) / 2 * mm
            c.setStrokeColor(PURPLE); c.circle(cx, cy, r, fill=0, stroke=1)
        c.setDash()
    # 원래 구멍
    for h in pl["holes"]:
        x, y = T(h["p"]); r = h["d"] / 2 * mm
        if state == "before":
            c.setStrokeColor(DARK); c.setLineWidth(0.5); c.circle(x, y, r, stroke=1, fill=0)
        elif h["after"] == "keep":
            c.setStrokeColor(DARK); c.setLineWidth(0.5); c.circle(x, y, r, stroke=1, fill=0)
        elif h["after"] == "unused":
            c.setStrokeColor(GRAY); c.setLineWidth(0.4); c.setDash(1, 1); c.circle(x, y, r, stroke=1, fill=0); c.setDash()
        elif h["after"] == "enlarge":
            c.setStrokeColor(GRAY); c.setLineWidth(0.4); c.setDash(1, 1); c.circle(x, y, r, stroke=1, fill=0); c.setDash()
            c.setStrokeColor(RED); c.setLineWidth(0.8); c.circle(x, y, h["to"] / 2 * mm, stroke=1, fill=0)
            c.setLineWidth(0.3); cross(c, x, y, h["to"] / 2 * mm + 2 * mm)
    if state == "before": return
    # 새 구멍
    for i, h in enumerate(pl["new"]):
        x, y = T(h["p"]); r = h["d"] / 2 * mm
        c.setStrokeColor(RED); c.setLineWidth(0.8); c.circle(x, y, r, stroke=1, fill=0)
        if h["kind"] in ("csk", "csk_opt"):
            c.setLineWidth(0.4); c.setDash(1.2, 1); c.circle(x, y, 3.3 * mm, stroke=1, fill=0); c.setDash()
        c.setLineWidth(0.3); cross(c, x, y, r + 2.2 * mm)
        if number:                                    # 번호: 판 중심에서 바깥쪽으로
            dx, dy = x - cx, y - cy; L = math.hypot(dx, dy) or 1
            nx, ny = x + dx / L * 5.2 * mm, y + dy / L * 5.2 * mm
            if key == "CP": nx, ny = x + (dx / L) * 7 * mm, y + 4.5 * mm
            txt(c, nx, ny - 1.2 * mm, CIRC[i], 8, bold=True, color=RED, anchor="c")

def legend(c, x, y, template=False):
    items = [(DARK, "solid", "원래 구멍 (그대로 씀)"), (GRAY, "dash", "원래 구멍 — 이제 안 씀"),
             (RED, "solid", "새로 뚫음 / 넓힘 (+ 십자)"), (RED, "dash", "접시 (뒷면, Ø6.6 정도)")]
    if not template:
        items += [(BLUE, "dash", "모터 몸 자리 (28각 → 42각)"), (PURPLE, "dash", "너트 플랜지 (Ø19.05 → Φ22)")]
    for i, (col, st, s) in enumerate(items):
        yy = y - i * 4.6 * mm
        c.setStrokeColor(col); c.setLineWidth(0.8)
        if st == "dash": c.setDash(1.5, 1)
        c.circle(x + 2 * mm, yy + 1.2 * mm, 1.6 * mm, stroke=1, fill=0); c.setDash()
        txt(c, x + 6 * mm, yy, s, 8)

def rel(pl, p):                     # 큰 구멍(가운데) 기준 가로·세로 (보는 방향)
    du = uv(pl, p)[0] - uv(pl, pl["center"])[0]; dv = p[1] - pl["center"][1]
    f = lambda a, pos, neg: ("%s %.1f" % (pos if a > 0 else neg, abs(a))) if abs(a) > 0.05 else "0"
    return "%s · %s" % (f(du, "오른쪽", "왼쪽"), f(dv, "위", "아래"))

KIND = {"drill": "Ø3.4 관통 (M3 나사)", "csk": "Ø3.4 + 접시 (뒷면) — M3 접시머리", "csk_opt": "Ø3.4 + 접시 (뒷면) 또는 안 뚫음",
        "tap": "Ø2.5 → M3 탭 (나사는 M3 × 6만)"}

NOTES = {
 "217": ["판을 +x 갠트리 레일의 '바깥(+x) 면'으로 23 mm 옮기기만 함 (판 모양·M5 구멍 그대로 — 같은 판, 뒤집지 않음).",
         "새 구멍 4개 = 31 mm 정사각 (NEMA17 앞 나사 M3). 원래 Ø2.9 4개(23 간격)는 안 씀.",
         "③④는 나사 머리가 레일 쪽 뒷면에 옴 → 냄비머리면 레일에 약 3 mm 걸림 → 접시 + M3 접시머리.",
         "①②는 레일보다 아래 → 냄비머리 M3 × 6도 됨 (같이 접시로 해도 됨).",
         "레일에 거는 나사: M5 둥근머리(머리 Ø9.5)는 모터 몸 윗면에 0.75 mm 걸림 → M4 둥근머리 × 8 + 2020 M4 T너트 (머리 Ø7.6, 여유 0.2).",
         "순서: 모터를 판에 먼저 조임 → 판을 레일 바깥 면에 M4 2개로."],
 "211": ["판 자리는 그대로 (Y 모터는 안 닿음 — FreeCAD 검사).",
         "새 구멍 4개 = 31 mm 정사각. 원래 Ø2.9 4개는 안 씀.",
         "④는 뒷면(+y)의 6각 기둥 바로 옆 (구멍 사이 벽 1.3 mm) → 냄비머리가 기둥에 닿음 → 접시 + 접시머리, 또는 안 뚫고 3개만.",
         "판 위쪽 끝까지 2.8 mm 남음 — 천천히 뚫기."],
 "XN": ["가운데 Ø8.5 → Ø10.5로 넓힘 (T8 너트 몸통 Φ10.2가 판을 지나감). 계단 드릴이 안전.",
        "너트 플랜지는 지금 POM 너트처럼 −x 면 (스위치 쪽). 4구멍 중 2개만 씀 — 위·+y 쪽은 Y 원점 스위치, 오른쪽은 판 끝·옛 M2 구멍.",
        "새 구멍 ①② = Ø2.5 뚫고 M3 탭. 뒤(+x)에는 YA 판·L 브래킷이라 너트 자리 없음. M3 × 8은 L 브래킷에 닿음 → × 6.",
        "구멍 자리는 너트 구멍 간격 PCD 16 [추측]으로 그림 → 너트를 받으면 판에 대 보고 맞으면 뚫기.",
        "플랜지 Φ22 가장자리가 Y 원점 스위치 기판에 1 mm 이하 걸림 → 기판을 살짝 올리거나 플랜지를 줄로."],
 "CP": ["가운데 Ø8.5 그대로 (스크류 Ø8이 지나감, 너트 몸통은 판 밖 +y).",
        "새 구멍 ①② (가로 2개, 가운데에서 8 mm) + 뒤(−y)에 M3 너트. 세로 2개는 뒤 너트가 LMK8UU 플랜지에 닿아 안 씀.",
        "새 구멍과 옛 POM 구멍(안 씀) 사이 벽 0.6 mm — 붙어도 괜찮음 (옛 구멍은 안 씀). 와셔를 받침.",
        "구멍 자리는 PCD 16 [추측] — 너트를 받으면 대 보고 뚫기.",
        "플랜지 가장자리가 LMK8UU 나사 너트 4개에 약 0.3 mm 걸림 → 그 나사를 뒤집거나 (냄비머리 쪽이 앞) 플랜지를 줄로."],
}

def plate_page(c, key, page):
    pl = P[key]; u0, u1, v0, v1 = bbox(pl); pw, ph = (u1 - u0) * mm, (v1 - v0) * mm
    txt(c, 15 * mm, H - 16 * mm, "%d. %s — 원래 ↔ 수정 후 (실제 크기 1:1)" % (page, pl["name"]), 13, bold=True)
    txt(c, 15 * mm, H - 22 * mm, pl["view"] + " · 위 = 위(z)", 9, color=colors.HexColor("#555555"))
    top = H - 30 * mm; gap = 85 * mm
    lx = 25 * mm + (60 * mm - pw) / 2; rx = lx + gap
    oy = top - ph - 8 * mm
    txt(c, lx + pw / 2, top - 2 * mm, "원래 (11/18 주문한 판)", 10, bold=True, anchor="c")
    txt(c, rx + pw / 2, top - 2 * mm, "수정 후 (NEMA17 팬케이크)", 10, bold=True, color=RED, anchor="c")
    draw_plate(c, key, "before", lx, oy, number=False)
    draw_plate(c, key, "after", rx, oy)
    if key == "217":
        txt(c, rx + pw / 2, top - 7 * mm, "노란 띠 = 뒷면이 레일에 닿는 자리 (z 440~)", 7.5, color=colors.HexColor("#8a6d00"), anchor="c")
    legend(c, 150 * mm, oy - 4 * mm)
    # 새 구멍 표
    y = oy - 8 * mm
    txt(c, 15 * mm, y, "새로 하는 것 (가운데 큰 구멍 중심 기준, 보는 방향 그대로)", 10, bold=True); y -= 6 * mm
    for i, h in enumerate(pl["new"]):
        txt(c, 17 * mm, y, CIRC[i], 9, bold=True, color=RED)
        txt(c, 23 * mm, y, rel(pl, h["p"]), 9); txt(c, 70 * mm, y, KIND[h["kind"]], 9); y -= 5.2 * mm
    for h in pl["holes"]:
        if h["after"] == "enlarge":
            txt(c, 17 * mm, y, "●", 9, color=RED); txt(c, 23 * mm, y, "가운데", 9)
            txt(c, 70 * mm, y, "Ø%.1f → Ø%.1f 넓힘" % (h["d"], h["to"]), 9); y -= 5.2 * mm
    y -= 3 * mm
    txt(c, 15 * mm, y, "왜 · 주의", 10, bold=True); y -= 6 * mm
    for s in NOTES[key]:
        y = para(c, 17 * mm, y, wrap("• " + s, 60), 8.6) - 1.2 * mm
    scale_bar(c, 15 * mm, 18 * mm)

def wrap(s, n):
    out, cur = [], ""
    for w in s.split(" "):
        if len(cur) + len(w) + 1 > n and cur: out.append(cur); cur = "  " + w
        else: cur = (cur + " " + w) if cur else w
    return out + [cur]

def cover(c):
    txt(c, 15 * mm, H - 18 * mm, "XY 모터 NEMA17 팬케이크로 바꿀 때 판 4장 고치기 — 원래 ↔ 수정 후", 14, bold=True)
    txt(c, 15 * mm, H - 24.5 * mm, "2026-11-23 이승준 (Claude, CAP-AI-SJ-63) · FreeCAD D5g_full_SJ1118로 부딪힘 검사 · 판 재주문 없음", 8.5, color=colors.HexColor("#555555"))
    y = H - 34 * mm
    y = para(c, 15 * mm, y, [
        "결론: 주문한 LM-NK1134(28각)가 12/4 이후에 와서 12/2 시연에 못 맞춤 → 내써팝 NEMA17 23 mm 팬케이크 + T8 리드 8로 바꿈.",
        "몸이 42각이라 사방 7 mm 커짐 → FreeCAD로 넣어 보니 X 모터만 +x 갠트리 레일 밑에 6 mm 겹침 (서현 11/16 기록과 같음).",
        "→ 217 판을 같은 레일의 바깥 면으로 옮기고 모터는 프레임 밖으로 (검사 통과). Y 모터는 그 자리 그대로.",
        "→ 판 4장은 드릴로 손 가공 (아래 2~5쪽). 스크류 절단: X 155 mm · Y 132 mm (모터 몸 앞면 기준)."], 9.3)
    y -= 4 * mm
    iw = 88 * mm; ih = 64 * mm
    imgs = [("X_수정전_레일겹침.png", "X 모터 — 지금 자리: 파란 몸 위쪽이 레일(노랑)과 6 mm 겹침"),
            ("X_수정후_레일바깥면.png", "X 모터 — 수정 후: 판을 레일 바깥 면에, 모터는 밖으로")]
    for k, (f, cap) in enumerate(imgs):
        x = 15 * mm + k * (iw + 4 * mm)
        c.drawImage(os.path.join(HERE, "img", f), x, y - ih, iw, ih, preserveAspectRatio=True)
        c.setStrokeColor(GRAY); c.setLineWidth(0.4); c.rect(x, y - ih, iw, ih)
        txt(c, x, y - ih - 4.5 * mm, cap, 8)
    y = y - ih - 12 * mm
    txt(c, 15 * mm, y, "FreeCAD 정면도 (−y에서 봄, 정투영). 팬케이크 몸 = 42 × 42 × 23 상자 (모서리 안 깎음 — 실제보다 조금 크게).", 7.5, color=colors.HexColor("#555555"))
    y -= 9 * mm
    txt(c, 15 * mm, y, "판마다 할 일 (한 줄 요약)", 11, bold=True); y -= 7 * mm
    rows = [("217 X 모터판", "레일 바깥 면으로 옮김 · Ø3.4 × 4 (31 간격) · 위 2개 뒷면 접시", "2쪽"),
            ("211 Y 모터판", "Ø3.4 × 4 (31 간격) · 기둥 옆 1개는 접시 또는 생략", "3쪽"),
            ("XN X 너트판", "가운데 Ø8.5 → Ø10.5 · M3 탭 2", "4쪽"),
            ("CP 캐리지판", "Ø3.4 × 2 (가로) + 뒤 너트", "5쪽")]
    for a, b, p in rows:
        txt(c, 17 * mm, y, a, 9.3, bold=True); txt(c, 50 * mm, y, b, 9.3); txt(c, 190 * mm, y, p, 9.3, anchor="r"); y -= 6 * mm
    y -= 4 * mm
    txt(c, 15 * mm, y, "검사 숫자 [확실 — CAD]", 11, bold=True); y -= 6.5 * mm
    for s in ["X 지금 자리: 레일 2020과 2,387 mm³ 겹침 (몸 위 z 446 > 레일 밑 z 440) · 217 M5 나사와 60 mm³",
              "X 수정 후: 판·몸·T8 스크류(Ø8 × 155)·M4 머리 모두 겹침 0 (M5 머리는 몸과 7 mm³ → M4로)",
              "Y: 그 자리 겹침 0 · +x 끝은 지금과 같음 · −x 원점: 판이 레버를 누른 뒤 1.4 mm에서 몸이 X 원점 팔 226p에 닿음 (지금 2.0 mm)",
              "새 나사 머리·너트: XN ①② · CP ①② · 211 ①②③ · 217 ①②(냄비)·③④(접시) 겹침 0"]:
        y = para(c, 17 * mm, y, wrap("• " + s, 78), 8.6) - 0.8 * mm
    txt(c, 15 * mm, 12 * mm, "검사 스크립트 cad/check_xy_nema17_pancake.py · 판 좌표 plates_2d.json · 이 PDF gen_plates_pdf.py", 7.5, color=colors.HexColor("#777777"))

def shopping(c, page):
    txt(c, 15 * mm, H - 18 * mm, "%d. 살 것 · 도구 · 순서 · 아직 모르는 것" % page, 13, bold=True)
    y = H - 30 * mm
    blocks = [
      ("모터 (내써팝 스마트스토어)", ["NEMA17 TM 스크류 일체형 23 mm + TM 200, 2개, 너트 포함",
        "주문 메모: '스크류 절단 — 모터 앞면(플랜지면)부터 끝까지 1개 155 mm, 1개 132 mm'",
        "결제 전 상세페이지 확인: 앞 나사 M3 간격 31 · 앞 돌기 Φ22 · T8 플랜지 너트 Φ22 (구멍 간격)",
        "정산 잔액 300원 → 자비 (약 2만 원 × 2 + 배송 3,500)"]),
      ("나사", ["M3 접시머리 × 6 — 217 ③④ (+ 211 ④) · M3 냄비머리 × 6 — 217 ①② · 211 ①②③ · XN ①② (탭)",
        "M3 × 8~10 냄비 + 너트 + 와셔 — CP ①② (플랜지 3.5 + 판 3 + 너트)",
        "M4 둥근머리 × 8 2개 + 2020용 M4 T너트(스프링너트) 2개 — 217을 레일에 (M5 대신)",
        "모터 앞 나사 깊이를 보고 M3 길이 확정 (판 3 mm + 2.5~4 mm)"]),
      ("도구", ["드릴 날 2 · 2.5 · 3.4 mm, 계단 드릴 (Ø10.5용), 접시 비트, M3 탭 + 핸들, 센터 펀치, 바이스·클램프, 보안경"]),
      ("순서", ["① '2026-11-23_승준_판구멍_1대1도안.pdf'를 실제 크기(100 %)로 인쇄 → 50 mm 선을 자로 확인",
        "② 도안을 판 모양대로 오려, 원래 구멍(검은 원)에 맞춰 붙임 (붙이는 면은 도안 제목)",
        "③ 십자 가운데 펀치 → 2 mm로 먼저 → 3.4 (탭 자리는 2.5) → 접시 · 탭 → 버 제거",
        "④ XN·CP는 너트를 받은 뒤 너트를 판에 대 보고 구멍이 맞는지 확인 후 뚫기"]),
      ("펌웨어 · 전기 (서현 담당 — 요청만)", ["1 mm = 25 풀스텝 (지금 100) — 1/4 스텝이면 100 걸음/mm (지금 400)",
        "원점 찾기는 천천히 (Y 여유 1.4 mm) · DRV8825 전류를 새 모터 정격에 · X 모터 선은 프레임 밖 → 길이·묶기"]),
      ("아직 모르는 것 [추측]", ["T8 너트 구멍 간격 (PCD 16으로 그림) · 모터 앞 나사 깊이 · 커넥터 방향 (Y 쪽만 다시 보면 됨)",
        "23 mm 팬케이크 힘 — 받으면 축을 손으로 밀어 보며 돌려 보기 (가벼운 캐리지라 될 가능성 높음)"]),
    ]
    for head, lines in blocks:
        txt(c, 15 * mm, y, head, 10.5, bold=True); y -= 6 * mm
        for s in lines:
            y = para(c, 18 * mm, y, wrap("• " + s, 76), 8.8) - 1 * mm
        y -= 3 * mm

def compare_pdf(path):
    c = canvas.Canvas(path, pagesize=A4); c.setTitle("XY 모터 NEMA17 — 판 수정 비교 (2026-11-23)")
    cover(c); c.showPage()
    for i, k in enumerate(["217", "211", "XN", "CP"]):
        plate_page(c, k, i + 2); c.showPage()
    shopping(c, 6); c.showPage(); c.save()

def template_pdf(path):
    c = canvas.Canvas(path, pagesize=A4); c.setTitle("판 구멍 1:1 도안 (2026-11-23)")
    face = {"217": "모터가 붙는 면 (+x, 프레임 바깥쪽)에 붙임", "211": "모터가 붙는 면 (−y)에 붙임",
            "XN": "너트 플랜지 면 (−x, Y 원점 스위치 쪽)에 붙임", "CP": "너트 플랜지 면 (+y)에 붙임"}
    for pg, keys in enumerate([["217", "211"], ["XN", "CP"]]):
        txt(c, 15 * mm, H - 16 * mm, "판 구멍 1:1 도안 %d/2 — 실제 크기(100 %%)로 인쇄, 판 모양대로 오려 붙이고 십자 가운데를 펀치" % (pg + 1), 11.5, bold=True)
        txt(c, 15 * mm, H - 22 * mm, "점선 = 판 바깥선(자르는 선) · 검은 원 = 원래 구멍 (여기에 맞춰 붙임) · 빨강 = 새 구멍 · 회색 점선 = 안 쓰는 옛 구멍", 8, color=colors.HexColor("#555555"))
        x = 22 * mm
        for k in keys:
            pl = P[k]; u0, u1, v0, v1 = bbox(pl); pw, ph = (u1 - u0) * mm, (v1 - v0) * mm
            oy = H - 40 * mm - ph
            txt(c, x, H - 31 * mm, pl["name"], 10, bold=True)
            txt(c, x, H - 35 * mm, face[k], 7.8, color=RED)
            draw_plate(c, k, "after", x, oy, template=True)
            y = oy - 7 * mm
            for i, h in enumerate(pl["new"]):
                txt(c, x, y, "%s %s" % (CIRC[i], KIND[h["kind"]]), 7.8); y -= 4.2 * mm
            for h in pl["holes"]:
                if h["after"] == "enlarge": txt(c, x, y, "● 가운데 Ø%.1f → Ø%.1f" % (h["d"], h["to"]), 7.8, color=RED); y -= 4.2 * mm
            if k in ("XN", "CP"): txt(c, x, y, "※ 너트를 받아 대 보고 맞으면 뚫기 (PCD 16 추측)", 7.8, color=RED)
            x += 95 * mm
        legend(c, 15 * mm, 60 * mm, template=True)
        scale_bar(c, 15 * mm, 25 * mm); c.showPage()
    c.save()

if __name__ == "__main__":
    compare_pdf(os.path.join(HERE, "2026-11-23_승준_XY판수정_비교.pdf"))
    template_pdf(os.path.join(HERE, "2026-11-23_승준_판구멍_1대1도안.pdf"))
    print("ok")
