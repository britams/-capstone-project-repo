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
         ('표시', 'XY 펜\n가슴에 점'), ('내보냄', '출구 문 열림\n시각 기록')]
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
a.add_patch(Rectangle((26.5, 57.6), 7, 1.4, fc=AMBER, ec='none'))
a.text(38, 62, '카메라 + 링 조명', fontsize=22, color=NAVY, weight='bold', va='center')
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
a.add_patch(Rectangle((8, 31.6), 44, 2.2, fc='#7FA7D6', ec=NAVY, lw=2))
a.add_patch(FancyArrowPatch((40, 22), (40, 30.8), arrowstyle='-|>', mutation_scale=30, lw=4, color=BLUE))
a.add_patch(Rectangle((28.5, 12), 3, 19.6, fc='#B9C2CC', ec='none'))
for k in range(6): a.plot([27.2, 32.8], [21.5 + k * 1.3, 22.1 + k * 1.3], color=NAVY, lw=2)
a.add_patch(Rectangle((24.5, 16.5), 11, 3.4, fc='#C77D3A', ec='none'))
a.add_patch(Rectangle((25, 5), 10, 7, fc=GRAY, ec='none'))
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
note(42, '2', '바닥 상승 → 고정', '모터·나사가 바닥을 밀어\n말벌을 격자판에 눌러 고정', BLUE)
note(26, '3', '힘을 재며 멈춤', '스프링 밑 로드셀이 누르는 힘\n측정, 0.5 N이면 정지', BLUE)
note(10, '4', '격자 구멍으로 점', '펜 약 0.3 N, 마지막 2 mm는\n천천히 내려 가슴에 점', BLUE)
a.text(30, 8.5, '모터', ha='center', va='center', fontsize=17, color='white', weight='bold')
a.text(36.5, 18.2, '로드셀', fontsize=17, color=GRAY, va='center'); a.text(34, 23.5, '스프링', fontsize=17, color=GRAY, va='center')
a.text(1, 42.6, '투명 격자판\n(구멍 Ø3)', fontsize=17, color=BLUE, linespacing=1.2); a.plot([11.5, 11.5], [42.4, 39.8], color=BLUE, lw=1.5)
a.text(1.5, 65.2, '마킹실 작동 원리', fontsize=22, color=NAVY, weight='bold')
a.text(2, 1.2, '마킹실 단면 개념도 (실제 비율 아님)', fontsize=16, color=GRAY)
f.savefig('fig_idea.png'); plt.close(f)

# ══ 그림 4 (교체): 장치 구조 + 말벌 이동 경로
f, a = canvas()
card(a, 0.5, 0.5, 41, 67, fc='white', ec=LINE, r=2.0)
fr = Image.open('/home/claude/repo/cad/img/D5g_도2_정면.png').convert('RGB').crop((835, 240, 1565, 1640))
put(a, fr, 2, 2, 38, 64)
def lab(y, t, s=None, yp=None, xp=31):
    yp = y if yp is None else yp
    a.plot([xp, 40, 44.5], [yp, y, y], color=BLUE, lw=2); a.add_patch(Circle((xp, yp), 0.7, fc=BLUE, ec='none'))
    a.text(45.3, y + (1.4 if s else 0), t, fontsize=22, color=NAVY, weight='bold', va='center')
    if s: a.text(45.3, y - 2.3, s, fontsize=17, color=GRAY, va='center')
lab(61, '포획통', '격리된 말벌', 60, 26)
lab(48, '카메라', '마킹실 위 153.5 mm', 44.8, 27)
lab(35, '마킹실', 'XY 펜·승강 바닥', 32.8, 27)
lab(21.5, '제어·전원', 'Pi 5·Arduino', 20.5, 30)
lab(8.5, '시판 트랩', '처음 잡히는 곳', 9.4, 30)
# 경로도
X = 72
def box(y, t, fc=LIGHT, tc=NAVY, w=22):
    card(a, X - w / 2, y - 3, w, 6, fc=fc, ec=fc, r=1.2); a.text(X, y, t, ha='center', va='center', fontsize=20, color=tc, weight='bold')
box(8, '시판 트랩 몸통'); box(22, '입구 통로 (센서 2개)'); box(38, '마킹실', NAVY, 'white')
arrow(a, X, 11.2, X, 18.6); arrow(a, X, 25.2, X, 34.6)
card(a, 58, 52, 20, 9, fc='#FDF3DE', ec='#FDF3DE', r=1.2); a.text(68, 58.4, '밖으로 (귀소)', ha='center', va='center', fontsize=18, color=NAVY, weight='bold'); a.text(68, 54.6, '일벌 · 표시 후', ha='center', va='center', fontsize=16, color='#9A6A0A', weight='bold')
card(a, 80, 52, 19, 9, fc='#E9ECEF', ec='#E9ECEF', r=1.2); a.text(89.5, 58.4, '포획통 (격리)', ha='center', va='center', fontsize=18, color=NAVY, weight='bold'); a.text(89.5, 54.6, '여왕벌 · 다른 종', ha='center', va='center', fontsize=16, color=GRAY, weight='bold')
arrow(a, 69, 41.4, 68, 51.4, c=AMBER, lw=4); arrow(a, 79, 41.4, 88, 51.4)
a.text(X + 6, 64.2, '말벌이 지나가는 길', ha='center', fontsize=22, color=NAVY, weight='bold')
f.savefig('fig_result.png'); plt.close(f)

# ══ 판넬 2번 칸 (설계 및 모델링): CAD 등각 + 설계 요점 — 실제 크기 35.6 × 32 cm (11/23 서현 '판넬 정말 별로')
PW, PH = 35.6, 32.0
f = plt.figure(figsize=(PW / 2.54, PH / 2.54), dpi=DPI); a = f.add_axes([0, 0, 1, 1]); a.set_xlim(0, PW); a.set_ylim(0, PH); a.axis('off')
iso = trim('/home/claude/repo/cad/img/D5g_도1_전체_등각.png', 150, 90); ih = 30.4; iw = ih * iso.width / iso.height
a.add_patch(FancyBboxPatch((0.2, 0.2), iw + 1.0, PH - 0.4, boxstyle='round,pad=0,rounding_size=0.8', fc='white', ec=LINE, lw=2))
a.imshow(np.asarray(iso), extent=(0.7, 0.7 + iw, 0.8, 0.8 + ih), zorder=2)
a.text(iw + 0.6, 0.9, 'CAD 모델', ha='right', va='bottom', fontsize=18, color=GRAY, zorder=3)
pts = [('시판 트랩 장착형', '시판 트랩 위에 얹는\n2020 알루미늄 프레임'), ('입구 통로', '센서 2개·문으로\n한 마리씩 들여보냄'),
       ('마킹실', '투명 격자판 (구멍 Ø3)\n승강 바닥·로드셀'), ('XY 펜', '수성 마커, 약 0.3 N\n마지막 2 mm는 천천히'),
       ('설계 검토', '역학계산 10문제\n부품 167개 간섭 검사')]
x0 = iw + 2.2
for i, (t, s) in enumerate(pts):
    y = PH - 3.4 - i * 6.15
    a.add_patch(Circle((x0 + 1.1, y), 1.05, fc=BLUE if i in (2, 3) else NAVY, ec='none'))
    a.text(x0 + 1.1, y, str(i + 1), ha='center', va='center', fontsize=26, color='white', weight='bold')
    a.text(x0 + 2.8, y + 0.15, t, fontsize=28, color=NAVY, weight='bold', va='center')
    a.text(x0 + 2.8, y - 1.35, s, fontsize=20, color=GRAY, va='top', linespacing=1.3)
f.savefig('fig_p_design.png'); plt.close(f)
