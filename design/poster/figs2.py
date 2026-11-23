import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.patches import FancyBboxPatch, Circle, Rectangle, Ellipse, FancyArrowPatch, Polygon
from PIL import Image, ImageChops
import numpy as np
for f in ['/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc', '/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc']:
    fm.fontManager.addfont(f)
plt.rcParams['font.family'] = 'Noto Sans CJK JP'
NAVY = '#1B2A4A'; BLUE = '#2563A8'; LIGHT = '#EAF1FA'; AMBER = '#E8A317'; GRAY = '#5B6472'; LINE = '#C9D3E0'
W, H = 31.4 / 2.54, 21.4 / 2.54   # 실제 크기 (인치) → 글자 pt가 포스터에서 그대로
DPI = 220

def canvas():
    f = plt.figure(figsize=(W, H), dpi=DPI); a = f.add_axes([0, 0, 1, 1]); a.set_xlim(0, 100); a.set_ylim(0, 68); a.axis('off'); return f, a

def card(a, x, y, w, h, fc='white', ec=LINE, lw=2.0, r=1.6):
    a.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f'round,pad=0,rounding_size={r}', fc=fc, ec=ec, lw=lw))

def arrow(a, x1, y1, x2, y2, c=GRAY, lw=3):
    a.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=34, lw=lw, color=c))

def trim(path, top=0, bottom=0):
    im = Image.open(path).convert('RGB'); im = im.crop((0, top, im.width, im.height - bottom))
    bg = Image.new('RGB', im.size, 'white'); bb = ImageChops.difference(im, bg).convert('L').point(lambda q: 255 if q > 12 else 0).getbbox()
    return im.crop(bb)

def put(a, im, x, y, w, h):   # (x,y,w,h) 안에 비율 유지해 가운데
    r = im.height / im.width; ax_r = (h / 68 * H) / (w / 100 * W)
    if r > ax_r: ww = h / 68 * H / r / W * 100; hh = h
    else: ww = w; hh = w / 100 * W * r / H * 68
    x0 = x + (w - ww) / 2; y0 = y + (h - hh) / 2
    a.imshow(np.asarray(im), extent=(x0, x0 + ww, y0, y0 + hh), zorder=2)

# ── A 대표 그림: 등각 CAD
f, a = canvas()
card(a, 0.5, 0.5, 99, 67, fc='white', ec=LINE, r=2.5)
put(a, trim('/home/claude/repo/cad/img/D5g_도1_전체_등각.png', 150, 90), 2, 2, 96, 64)
a.text(97.5, 2.2, 'CAD 모델', ha='right', va='bottom', fontsize=20, color=GRAY)
f.savefig('fig_rep.png'); plt.close(f)

# ── B 작동 순서
f, a = canvas()
steps = [('들어옴', '빛 센서 감지\n입구 문 닫힘'), ('판별', '카메라 AI\n일벌 확인'), ('고정', '바닥 상승\n격자에 고정'),
         ('표시', 'XY 펜\n가슴에 점'), ('내보냄', '방생 문 열림\n시각 기록')]
cx = [10, 30, 50, 70, 90]
for i, (t, s) in enumerate(steps):
    hl = i in (2, 3)
    a.add_patch(Circle((cx[i], 52), 6.2, fc=BLUE if hl else NAVY, ec='none', zorder=3))
    a.text(cx[i], 52, str(i + 1), ha='center', va='center', fontsize=40, color='white', weight='bold', zorder=4)
    a.text(cx[i], 40.5, t, ha='center', va='center', fontsize=36, color=NAVY, weight='bold')
    a.text(cx[i], 31.0, s, ha='center', va='center', fontsize=24, color=GRAY, linespacing=1.35)
    if i < 4: arrow(a, cx[i] + 7.2, 52, cx[i + 1] - 7.2, 52)
card(a, 4, 3, 44, 13, fc=LIGHT, ec=LIGHT)
a.text(26, 9.5, '일벌이 아니면 → 표시 없이 격리', ha='center', va='center', fontsize=25, color=NAVY, weight='bold')
card(a, 52, 3, 44, 13, fc='#FDF3DE', ec='#FDF3DE')
a.text(74, 9.5, '다시 잡히면 → 왕복 시간 기록', ha='center', va='center', fontsize=25, color=NAVY, weight='bold')
f.savefig('fig_goal.png'); plt.close(f)

# ── C 착상: VespAI + 마킹 통 = 우리
def wasp(a, x, y, s=1.0, z=5):
    a.add_patch(Ellipse((x + 1.6 * s, y), 7 * s, 3.0 * s, fc='#2E2E2E', ec='none', zorder=z))
    a.add_patch(Ellipse((x - 1.8 * s, y), 2.8 * s, 2.4 * s, fc='#C97A10', ec='none', zorder=z + 1))
def grid(a, x0, x1, y):
    a.plot([x0, x1], [y, y], color='#7FA7D6', lw=6, solid_capstyle='butt', zorder=6)
    for xx in np.arange(x0 + 1.2, x1, 2.4): a.plot([xx, xx], [y - 0.5, y + 0.5], color='white', lw=2.5, zorder=7)
f, a = canvas()
xs = [1, 35, 69]; cw = 30
heads = [('기존 ①  VespAI', '카메라 AI로 판별만'), ('기존 ②  여왕벌 마킹 통', '사람이 손으로 고정·표시'), ('우리 장치', '판별·고정·표시 자동')]
for i, x in enumerate(xs):
    card(a, x, 2, cw, 64, fc=LIGHT if i == 2 else 'white', ec=BLUE if i == 2 else LINE, lw=3 if i == 2 else 2)
    a.text(x + cw / 2, 60, heads[i][0], ha='center', va='center', fontsize=27, weight='bold', color=NAVY)
    a.text(x + cw / 2, 8, heads[i][1], ha='center', va='center', fontsize=22, color=BLUE if i == 2 else GRAY, weight='bold' if i == 2 else 'normal')
a.text(33.0, 34, '+', ha='center', va='center', fontsize=60, color=GRAY, weight='bold')
a.text(67.0, 34, '=', ha='center', va='center', fontsize=60, color=GRAY, weight='bold')
put(a, Image.open('vespai_v.jpg'), xs[0] + 2, 14, cw - 4, 40)
a.text(xs[0] + cw / 2, 3.6, "영상: O'Shea-Wheller 2024 (CC BY-NC-SA)", ha='center', fontsize=12, color=GRAY)
# 마킹 통 (사람 손)
c = xs[1] + cw / 2
a.add_patch(Rectangle((c - 7, 15), 14, 32, fill=False, ec=GRAY, lw=3))
grid(a, c - 7, c + 7, 47)
wasp(a, c, 45.2)
a.add_patch(Rectangle((c - 6.5, 41.5), 13, 1.6, fc='#B9C2CC', ec='none')); a.add_patch(Rectangle((c - 1, 15), 2, 26.5, fc='#B9C2CC', ec='none'))
arrow(a, c + 4, 22, c + 4, 38, c=BLUE, lw=3.5)
a.text(c, 11.6, '손으로 밀어 올림', ha='center', fontsize=18, color=GRAY)
a.add_patch(Polygon([[c - 1, 49], [c + 1, 49], [c + 1.6, 55], [c - 1.6, 55]], fc=AMBER, ec='none'))
a.text(c + 3, 53, '붓', fontsize=17, color=GRAY, va='center')
# 우리 장치
c = xs[2] + cw / 2
a.add_patch(Rectangle((c - 7, 15), 14, 32, fill=False, ec=NAVY, lw=3))
grid(a, c - 7, c + 7, 47)
wasp(a, c, 45.2)
a.add_patch(Rectangle((c - 6.5, 41.5), 13, 1.6, fc='#7FA7D6', ec='none')); a.add_patch(Rectangle((c - 1, 15), 2, 26.5, fc='#7FA7D6', ec='none'))
a.add_patch(Rectangle((c - 3.2, 15), 6.4, 5, fc=NAVY, ec='none')); a.text(c + 5, 17.5, '서보', fontsize=17, color=NAVY, va='center')
arrow(a, c + 4, 23, c + 4, 38, c=BLUE, lw=3.5)
a.add_patch(Polygon([[c + 2, 49], [c + 4, 49], [c + 4.6, 55], [c + 1.4, 55]], fc=AMBER, ec='none'))
a.text(c + 6, 53, 'XY 펜', fontsize=17, color=NAVY, va='center')
a.add_patch(Rectangle((c - 6, 51.5), 4.6, 3.2, fc=NAVY, ec='none')); a.add_patch(Circle((c - 3.7, 51.4), 0.9, fc='#9FC3F0', ec='none'))
a.text(c - 6.5, 53.1, '카메라', fontsize=17, color=NAVY, va='center', ha='right')
f.savefig('fig_idea.png'); plt.close(f)

# ── D 결과: 세 방향 그림
f, a = canvas()
views = [('정면', 'D5g_도2_정면.png'), ('측면', 'D5g_도3_측면.png'), ('위', 'D5g_도4_위.png')]
for i, (t, fn) in enumerate(views):
    x = 1 + i * 33
    card(a, x, 2, 32, 64, fc='white', ec=LINE, r=2)
    put(a, trim('/home/claude/repo/cad/img/' + fn, 150, 90), x + 1.5, 4, 29, 52)
    a.text(x + 16, 61, t, ha='center', va='center', fontsize=28, weight='bold', color=NAVY)
f.savefig('fig_result.png'); plt.close(f)

# ── E 활용: B2G 흐름
f, a = canvas()
flow = [('트랩 설치', '양봉장 주변\n여러 곳'), ('자동 표시', '일벌 표시 후\n내보냄'), ('시각 수집', '다시 잡힌\n시각 기록'), ('둥지 제거', '거리 범위로\n둥지 탐색')]
for i, (t, s) in enumerate(flow):
    x = 1.5 + i * 25
    hl = i == 3
    card(a, x, 22, 21, 40, fc=NAVY if hl else LIGHT, ec='none', r=2)
    a.text(x + 10.5, 51, t, ha='center', va='center', fontsize=31, weight='bold', color='white' if hl else NAVY)
    a.text(x + 10.5, 35, s, ha='center', va='center', fontsize=23, color='white' if hl else GRAY, linespacing=1.4)
    if i < 3: arrow(a, x + 21.4, 42, x + 25, 42)
a.text(50, 12.5, '지자체·방제 기관용 조사 장비 (B2G)', ha='center', va='center', fontsize=30, weight='bold', color=BLUE)
a.text(50, 4.5, '양봉농가는 표시 없이 모두 가두는 방제 모드로 사용', ha='center', va='center', fontsize=22, color=GRAY)
f.savefig('fig_use.png'); plt.close(f)
print('ok')

# ── D' 결과: 한 일 숫자 타일
f, a = canvas()
tiles = [('10', '역학계산 문제', '정역학·동역학·재료역학'), ('167', '부품 간섭 검사', '움직임 포함, 겹침 0'),
         ('180', '제어 모의 시험', '문·Pi·처리 순서 전부 통과'), ('917/917', 'AI 판별 장면', '격자 너머, 재학습 후'),
         ('3', '회로도', '12 V 단일 전원'), ('61', '구매 품목', '재료비 60만 원 정산'),
         ('16+9', '가공 판 + 3D 프린트', '레이저 가공·출력 부품'), ('30', '참고 문헌·자료', '논문·법령·통계')]
for i, (n, t, s) in enumerate(tiles):
    r, c = divmod(i, 4); x = 1 + c * 24.75; y = 35 - r * 33
    hl = i in (0, 1, 2, 3)
    card(a, x, y, 23.5, 31, fc=NAVY if i == 3 else (LIGHT if hl else 'white'), ec=LINE if not hl else 'none', r=2)
    col = 'white' if i == 3 else NAVY
    a.text(x + 11.75, y + 21, n, ha='center', va='center', fontsize=46 if len(n) < 5 else 36, weight='bold', color=AMBER if i == 3 else BLUE)
    a.text(x + 11.75, y + 11, t, ha='center', va='center', fontsize=24, weight='bold', color=col)
    a.text(x + 11.75, y + 5, s, ha='center', va='center', fontsize=17, color='#D6E2F2' if i == 3 else GRAY)
f.savefig('fig_result.png'); plt.close(f)
print('ok2')

# ══ 그림 3 (교체): 마킹실 단면 — 누르고 찍는 원리
f, a = canvas()
GL = '#BFD9F2'
# 카메라 + 조명
a.add_patch(FancyBboxPatch((24, 59), 12, 6, boxstyle='round,pad=0,rounding_size=0.8', fc=NAVY, ec='none'))
a.add_patch(Rectangle((19.5, 58.2), 4, 1.6, fc=AMBER, ec='none')); a.add_patch(Rectangle((36.5, 58.2), 4, 1.6, fc=AMBER, ec='none'))
a.add_patch(Rectangle((28.6, 57.9), 2.8, 1.1, fc=NAVY, ec='none'))
a.text(42, 62, '카메라 + LED 조명', fontsize=22, color=NAVY, weight='bold', va='center')
a.add_patch(Polygon([(30, 57.6), (17, 37.5), (43, 37.5)], closed=True, fc=GL, ec='none', alpha=0.45))
# XY 이송 장치
a.add_patch(Rectangle((6, 47.5), 52, 1.6, fc='#8C96A3', ec='none'))
a.add_patch(FancyBboxPatch((22, 45.2), 8, 6.4, boxstyle='round,pad=0,rounding_size=0.6', fc=BLUE, ec='none'))
a.add_patch(Polygon([(25.3, 45.2), (26.7, 45.2), (26.0, 40.6)], closed=True, fc=NAVY, ec='none'))
a.add_patch(FancyArrowPatch((32.5, 45), (32.5, 41.2), arrowstyle='-|>', mutation_scale=26, lw=3, color=BLUE))
a.text(36, 53.6, 'XY 이송 장치', fontsize=20, color=NAVY, weight='bold'); a.text(36, 50.6, '펜을 앞뒤·좌우로 옮김', fontsize=17, color=GRAY)
# 격자판
a.add_patch(Rectangle((8, 37.5), 44, 2.2, fc=GL, ec=BLUE, lw=2))
for gx in np.arange(10, 51, 3.0): a.add_patch(Rectangle((gx, 37.5), 1.1, 2.2, fc='white', ec='none'))
# 말벌 (격자에 눌린 모습)
a.add_patch(Ellipse((26.0, 35.6), 15, 3.6, fc=AMBER, ec=NAVY, lw=2))
for sx in (29, 31.5, 34): a.add_patch(Rectangle((sx - 0.5, 34.0), 1.0, 3.2, fc=NAVY, ec='none'))
a.add_patch(Circle((26.0, 37.2), 0.9, fc='#2563A8', ec='white', lw=1.5, zorder=5))
# 승강 바닥 + 구동
a.add_patch(Rectangle((8, 31.6), 44, 2.2, fc='#F7F8FA', ec=NAVY, lw=2))
a.add_patch(FancyArrowPatch((40, 22), (40, 30.8), arrowstyle='-|>', mutation_scale=30, lw=4, color=BLUE))
a.add_patch(Rectangle((29, 21), 2, 10.6, fc='#B9C2CC', ec='none'))
a.add_patch(FancyBboxPatch((25, 5), 10, 16, boxstyle='round,pad=0,rounding_size=0.6', fc=GRAY, ec='none'))
# 벽·문
a.add_patch(Rectangle((5.5, 31.6), 2.5, 10.2, fc='#D5DBE3', ec='none')); a.add_patch(Rectangle((52, 31.6), 2.5, 10.2, fc='#D5DBE3', ec='none'))
a.add_patch(Rectangle((5.5, 32.6), 2.5, 2.6, fc=AMBER, ec='none')); a.add_patch(Rectangle((52, 32.6), 2.5, 2.6, fc=AMBER, ec='none'))
a.text(4.5, 28.6, '입구 문', fontsize=17, color=GRAY); a.text(47.5, 28.6, '방생 문', fontsize=17, color=GRAY)
# 오른쪽 설명
R = 60
def note(y, n, t, s, c=NAVY):
    a.add_patch(Circle((R + 2, y), 1.9, fc=c, ec='none')); a.text(R + 2, y, n, ha='center', va='center', fontsize=22, color='white', weight='bold')
    a.text(R + 5.2, y + 1.6, t, fontsize=24, color=NAVY, weight='bold', va='center')
    a.text(R + 5.2, y - 2.6, s, fontsize=18, color=GRAY, va='center', linespacing=1.3)
note(58, '1', '찍기 전 촬영', '격자 위 153.5 mm 카메라로\n일벌 확인·가슴 위치 찾음')
note(42, '2', '바닥 상승 → 고정', '리니어 서보가 바닥을 밀어\n말벌을 격자판에 눌러 고정', BLUE)
note(26, '3', '정한 높이에서 멈춤', '위치 지정 서보라 격자 아래\n5 mm에서 바로 정지', BLUE)
note(10, '4', '격자 구멍으로 점', '펜 약 0.3 N, 마지막 2 mm는\n천천히 내려 가슴에 점', BLUE)
a.text(30, 15.2, '리니어', ha='center', va='center', fontsize=17, color='white', weight='bold'); a.text(30, 11.4, '서보', ha='center', va='center', fontsize=17, color='white', weight='bold')
a.text(37, 9, '행정 26 mm', fontsize=17, color=GRAY, va='center'); a.text(44.5, 34.7, '백색 바닥', fontsize=15, color=GRAY, va='center')
a.text(1, 42.6, '투명 격자판\n(네모 구멍 3 mm)', fontsize=17, color=BLUE, linespacing=1.2); a.plot([11.5, 11.5], [42.4, 39.8], color=BLUE, lw=1.5)
a.text(1.5, 65.2, '마킹실 작동 원리', fontsize=22, color=NAVY, weight='bold')
a.text(2, 1.2, '마킹실 단면 개념도 (실제 비율 아님)', fontsize=16, color=GRAY)
f.savefig('fig_idea.png'); plt.close(f)

# ══ 그림 4 (11/23 밤 다시): CAD 정면도에 번호 + 오른쪽 설명 (판넬 2번 칸 방식, 선 교차 없음)
f, a = canvas()
card(a, 0.5, 0.5, 40, 67, fc='white', ec=LINE, r=2.0)
fr = Image.open('/home/claude/repo/cad/img/D5g_도2_정면.png').convert('RGB').crop((835, 240, 1565, 1640))
put(a, fr, 2, 2, 38, 64)   # → 그림 x 4.3~37.7, y 2~66
a.text(39.5, 1.6, 'CAD 정면도', ha='right', va='bottom', fontsize=16, color=GRAY, zorder=7, bbox=dict(fc='white', ec='none', pad=2))
pts = [((21.9, 58.5), '포획통', '여왕벌·다른 종을 표시 없이 가둠'),
       ((26.3, 46.6), '카메라', '마킹실 위 153.5 mm, AI로 일벌 판별'),
       ((25.1, 32.2), '마킹실', '리니어 서보 바닥으로 고정, XY 펜으로 점'),
       ((14.6, 19.8), '제어·전원', 'Raspberry Pi 5·Arduino, 12 V 전원'),
       ((17.3, 10.7), '시판 트랩', '2020 알루미늄 프레임 아래에 그대로 씀')]
for i, ((px, py), t, sub) in enumerate(pts):
    c = BLUE if i == 2 else NAVY
    a.add_patch(Circle((px, py), 2.0, fc=c, ec='white', lw=3, zorder=5))
    a.text(px, py, str(i + 1), ha='center', va='center', fontsize=24, color='white', weight='bold', zorder=6)
    ty = 59 - i * 12.2
    a.add_patch(Circle((45.5, ty), 2.4, fc=c, ec='none'))
    a.text(45.5, ty, str(i + 1), ha='center', va='center', fontsize=26, color='white', weight='bold')
    a.text(49.5, ty + 1.7, t, fontsize=30, color=NAVY, weight='bold', va='center')
    a.text(49.5, ty - 2.9, sub, fontsize=20, color=GRAY, va='center')
f.savefig('fig_struct.png'); plt.close(f)

# ══ 판넬 2번 칸 (설계 및 모델링): CAD 등각 + 설계 요점 — 실제 크기 35.6 × 32 cm (11/23 서현 '판넬 정말 별로')
PW, PH = 35.6, 32.0
f = plt.figure(figsize=(PW / 2.54, PH / 2.54), dpi=DPI); a = f.add_axes([0, 0, 1, 1]); a.set_xlim(0, PW); a.set_ylim(0, PH); a.axis('off')
iso = trim('/home/claude/repo/cad/img/D5g_도1_전체_등각.png', 150, 90); ih = 30.4; iw = ih * iso.width / iso.height
a.add_patch(FancyBboxPatch((0.2, 0.2), iw + 1.0, PH - 0.4, boxstyle='round,pad=0,rounding_size=0.8', fc='white', ec=LINE, lw=2))
a.imshow(np.asarray(iso), extent=(0.7, 0.7 + iw, 0.8, 0.8 + ih), zorder=2)
a.text(iw + 0.6, 0.9, 'CAD 모델', ha='right', va='bottom', fontsize=18, color=GRAY, zorder=3)
pts = [('시판 트랩 장착형', '시판 트랩 위에 얹는\n2020 알루미늄 프레임'), ('입구 통로', '빛 센서·문으로\n한 마리씩 들여보냄'),
       ('마킹실', '투명 격자판 (네모 구멍 3 mm)\n리니어 서보 승강 바닥'), ('XY 펜', '수성 아크릴 마커, 약 0.3 N\n마지막 2 mm는 천천히'),
       ('설계 검토', '역학계산 10문제\n조립 움직임·간섭 검사')]
x0 = iw + 2.2
for i, (t, s) in enumerate(pts):
    y = PH - 3.4 - i * 6.15
    a.add_patch(Circle((x0 + 1.1, y), 1.05, fc=BLUE if i in (2, 3) else NAVY, ec='none'))
    a.text(x0 + 1.1, y, str(i + 1), ha='center', va='center', fontsize=26, color='white', weight='bold')
    a.text(x0 + 2.8, y + 0.15, t, fontsize=28, color=NAVY, weight='bold', va='center')
    a.text(x0 + 2.8, y - 1.35, s, fontsize=20, color=GRAY, va='top', linespacing=1.3)
f.savefig('fig_p_design.png'); plt.close(f)


# ══ 그림 4 (11/23 밤): AI 판별 시험 — 실제 사진 + 우리 재학습 결과 (VespAI 사진은 레포에 안 올림 → fig_ai.png는 .gitignore)
U = '/mnt/user-data/uploads/capstone design/'
f, a = canvas()
a.text(1, 64.6, 'AI 판별 시험 — 격자 너머에서도 등검은말벌 찾기', fontsize=26, color=NAVY, weight='bold', va='center')
v = Image.open(U + 'capstone_vespai/out/velutina-frame-1.jpeg').convert('RGB').crop((480, 180, 1560, 1080))
card(a, 0.5, 31.5, 46, 29.5, fc='white', ec=LINE, r=1.2); put(a, v, 1.3, 37.6, 44.4, 22.9)
a.text(1.8, 35.4, '① VespAI 원본 모델을 우리 PC에서 실행', fontsize=17, color=NAVY, weight='bold', va='center')
a.text(1.8, 33.0, '공개 예시 영상 (O\'Shea-Wheller 2024) · 검출 0.85~0.96', fontsize=13, color=GRAY, va='center')
g = Image.open('/tmp/grid_test_2x2.png').convert('RGB')   # 11/16 주간보고 슬라이드 13 (승준 v3 철망 시험 결과 4장)
card(a, 0.5, 0.5, 46, 29.5, fc='white', ec=LINE, r=1.2); put(a, g, 1.3, 6.6, 44.4, 22.9)
a.text(1.8, 4.4, '② 우리 시험: 철망 너머 표본 검출 (v3)', fontsize=17, color=NAVY, weight='bold', va='center')
a.text(1.8, 2.0, '학습에 안 쓴 표본 · 검은 철망 4 mm로 시험', fontsize=13, color=GRAY, va='center')
# 오른쪽: 우리 재학습 결과 (vision/2026-11-15, 승준)
card(a, 48.5, 0.5, 51, 60.5, fc='white', ec=LINE, r=1.2)
a.text(51, 58, '③ 우리 표본으로 다시 학습 (YOLOv5s)', fontsize=17, color=NAVY, weight='bold', va='center')
a.text(51, 55.6, '격자 + 말벌 장면 중 말벌을 찾은 비율', fontsize=13, color=GRAY, va='center')
bars = [('v1', 32.0, '312/975', '흰 종이만'), ('v2', 26.1, '472/1811', '떠 있는 격자 추가'), ('v3', 100.0, '917/917', '격자를 얹어 학습')]
base, top = 14, 49
a.plot([51, 97.5], [base, base], color=GRAY, lw=1.5)
for i, (n, p, fr_, d) in enumerate(bars):
    cx = 58.5 + i * 15.5; hgt = (top - base) * p / 100; c = BLUE if n == 'v3' else '#B9C2CC'
    a.add_patch(Rectangle((cx - 5, base), 10, hgt, fc=c, ec='none'))
    a.text(cx, base + hgt + 2.6, f'{p:.1f} %', ha='center', va='center', fontsize=20, color=NAVY if n == 'v3' else GRAY, weight='bold')
    a.text(cx, base + hgt + 0.9, fr_, ha='center', va='center', fontsize=12, color=GRAY)
    a.text(cx, base - 2.0, n, ha='center', va='center', fontsize=17, color=NAVY, weight='bold')
    a.text(cx, base - 4.3, d, ha='center', va='center', fontsize=12, color=GRAY)
a.text(51, 6.0, '표본 6마리 · 사진 155장, VespAI 가중치에서 이어 학습', fontsize=12.5, color=GRAY, va='center')
a.text(51, 3.6, '시험: 학습에 안 쓴 표본 2마리 · 격자만 장면 헛검출 2.1 % (17/797)', fontsize=12.5, color=GRAY, va='center')
f.savefig('fig_ai.png'); plt.close(f)


# ══ 그림 (오른쪽 4번) B2G 활용 — 자세히 (11/23 밤 서현 "현재 것에서 자세하게"). 근거: 당위성 워드 (Rojas-Nossa 2022 공식, 11-3 색 교체, 조사·방제 모드)
f, a = canvas()
a.text(1, 64.5, '활용 — 지자체·방제 기관용 둥지 조사 장비 (B2G)', fontsize=26, color=NAVY, weight='bold', va='center')
flow = [('트랩 설치', '양봉장 주변 여러 곳\n시판 트랩 위에 장착'), ('자동 표시', '일벌만 점 찍고 내보냄\n1시간마다 마커 색 교체'),
        ('시각 수집', '다시 잡히면 시각 기록\n→ 왕복 시간 계산'), ('둥지 제거', '거리 범위 안 수색\n허가 기관이 제거')]
for i, (t, sub) in enumerate(flow):
    x = 1 + i * 25; hl = i == 3
    card(a, x, 33, 22.5, 26, fc=NAVY if hl else LIGHT, ec='none', r=1.6)
    a.add_patch(Circle((x + 3.2, 55.3), 2.0, fc=BLUE if not hl else 'white', ec='none'))
    a.text(x + 3.2, 55.3, str(i + 1), ha='center', va='center', fontsize=20, weight='bold', color='white' if not hl else NAVY)
    a.text(x + 11.25, 48.5, t, ha='center', va='center', fontsize=27, weight='bold', color='white' if hl else NAVY)
    a.text(x + 11.25, 39.3, sub, ha='center', va='center', fontsize=17, color='white' if hl else GRAY, linespacing=1.45)
    if i < 3: arrow(a, x + 22.8, 46, x + 25.6, 46)
card(a, 1, 1, 57, 29, fc='white', ec=LINE, r=1.4)
a.text(3, 26.3, '둥지 거리 추정 (Rojas-Nossa 2022)', fontsize=20, color=NAVY, weight='bold', va='center')
a.text(3, 19.8, '거리 = (왕복 시간 − 45 s) ÷ 2 × 1.8~5.4 m/s', fontsize=19, color=BLUE, weight='bold', va='center')
a.text(3, 13.5, '둥지 195~1,331 m  ↔  왕복 약 2~25분', fontsize=18, color=NAVY, va='center')
a.text(3, 6.0, '45 s = 둥지에 머무는 시간, 1.8~5.4 m/s = 비행 속도', fontsize=14, color=GRAY, va='center')
card(a, 60, 16.5, 39, 13.5, fc=LIGHT, ec='none', r=1.4)
a.text(62, 26, '조사 모드  ·  지자체·방제 기관', fontsize=17, color=NAVY, weight='bold', va='center')
a.text(62, 20.3, '일벌 표시 후 내보내 둥지 추적', fontsize=16, color=GRAY, va='center')
card(a, 60, 1, 39, 13.5, fc='#FDF3DE', ec='none', r=1.4)
a.text(62, 10.5, '방제 모드  ·  양봉농가', fontsize=17, color=NAVY, weight='bold', va='center')
a.text(62, 4.8, '표시 없이 모두 가둬 피해 줄임', fontsize=16, color=GRAY, va='center')
f.savefig('fig_use.png'); plt.close(f)


# ══ 그림 1 (11/23 21:21 서현 "VespAI 사진하고 2개만"): VespAI 실행 화면 + 우리 재학습 사진 (11/16 주간보고 슬라이드 14, 격자 합성 v4 학습 사진)
U = '/mnt/user-data/uploads/capstone design/'
f, a = canvas()
a.text(1, 64.6, 'AI 판별 — 격자 너머 등검은말벌 찾기', fontsize=26, color=NAVY, weight='bold', va='center')
v = Image.open(U + 'capstone_vespai/out/velutina-frame-1.jpeg').convert('RGB').crop((420, 180, 1620, 1068))
sy = Image.open('/tmp/syn_3.png').convert('RGB'); sy = sy.crop((45, 0, 333, 213))
for i, (im, t, sub) in enumerate([(v, '① VespAI 원본 모델 (우리 PC에서 실행)', "공개 예시 영상 (O'Shea-Wheller 2024) · 검출 0.85~0.96"),
                                  (sy, '② 우리 재학습 사진 — 설계 격자판 합성', '우리 표본 + 아크릴 격자 (네모 3 mm), 빨간 네모 = 학습 라벨')]):
    x = 0.5 + i * 50
    card(a, x, 12.5, 49, 47.5, fc='white', ec=LINE, r=1.2)
    put(a, im, x + 1.2, 20.8, 46.6, 38.2)
    a.text(x + 2, 17.6, t, fontsize=18, color=NAVY, weight='bold', va='center')
    a.text(x + 2, 14.8, sub, fontsize=13, color=GRAY, va='center')
card(a, 0.5, 0.5, 99, 10, fc=LIGHT, ec='none', r=1.0)
a.text(50, 5.5, '재학습 결과 (v3): 학습에 안 쓴 표본, 철망 너머 917/917 장면 검출', ha='center', fontsize=21, color=NAVY, weight='bold', va='center')
f.savefig('fig_ai.png'); plt.close(f)
