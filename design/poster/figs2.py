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
