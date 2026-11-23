from pptx import Presentation
from pptx.util import Cm, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from PIL import Image

INK = RGBColor(0x1F, 0x2A, 0x44); ACC = RGBColor(0x2B, 0x6C, 0xB0); GRY = RGBColor(0x55, 0x55, 0x55)
F = '맑은 고딕'
prs = Presentation(); prs.slide_width = Cm(33.867); prs.slide_height = Cm(19.05)
BL = prs.slide_layouts[6]

def text(s, x, y, w, h, lines, size=20, color=INK, bold=False, bullet=False, align=None):
    tb = s.shapes.add_textbox(Cm(x), Cm(y), Cm(w), Cm(h)); tf = tb.text_frame; tf.word_wrap = True
    for i, l in enumerate(lines):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        r = p.add_run(); r.text = ('• ' if bullet else '') + l
        r.font.size = Pt(size); r.font.name = F; r.font.color.rgb = color; r.font.bold = bold
        p.space_after = Pt(8)
        if align: p.alignment = align
    return tb

def slide(title, num):
    s = prs.slides.add_slide(BL)
    bar = s.shapes.add_shape(1, 0, 0, prs.slide_width, Cm(2.3)); bar.fill.solid(); bar.fill.fore_color.rgb = INK; bar.line.fill.background()
    text(s, 1.2, 0.35, 28, 1.8, [title], 28, RGBColor(255, 255, 255), True)
    text(s, 30.5, 17.6, 3, 1, [f'{num}'], 12, GRY, align=PP_ALIGN.RIGHT)
    return s

def pic(s, f, x, y, w=None, h=None):
    im = Image.open(f); r = im.height / im.width
    if w is None: w = h / r
    s.shapes.add_picture(f, Cm(x), Cm(y), Cm(w), Cm(w * r))

# 1 표지
s = prs.slides.add_slide(BL)
bg = s.shapes.add_shape(1, 0, 0, prs.slide_width, prs.slide_height); bg.fill.solid(); bg.fill.fore_color.rgb = INK; bg.line.fill.background()
text(s, 2, 4.2, 30, 4.5, ['YOLO 판별 기반 등검은말벌', '자동 마킹·둥지 거리 추정 트랩'], 36, RGBColor(255, 255, 255), True)
text(s, 2, 9.3, 30, 1.5, ['시판 트랩에 얹는 자동 표시 모듈'], 24, RGBColor(0xF0, 0xC0, 0x40))
text(s, 2, 12.0, 30, 3, ['팀 초벌 | 이서현 (팀장) · 이승준', '국립공주대학교 기계자동차공학부 기계공학전공 | 지도교수 김성관'], 18, RGBColor(255, 255, 255))

# 2 문제
s = slide('문제: 둥지를 찾는 첫 단계가 사람 손작업임', 2)
text(s, 1.5, 3.2, 31, 12, [
    '등검은말벌: 꿀벌을 잡아먹는 외래종, 2019년 생태계교란 생물 지정',
    '트랩으로 잡아도 둥지의 여왕벌이 일벌을 계속 만듦 → 근본 대책은 둥지 제거 (Kennedy 2018)',
    '둥지 찾기: 말벌을 잡아 표시 → 돌아오는 시간으로 거리 계산 (Rojas-Nossa 2022)',
    '지금은 사람이 손으로 표시함: 얼음 마취 10~12분 + 고정판 → 쏘임 위험, 시간 부담',
    '목표: 가두기 → 판별 → 고정 → 점 마킹 → 내보내기를 사람 없이 수행'], 22, bullet=True)

# 3 착상
s = slide('원리: 마킹 통의 "눌러 고정" + 펜 플로터의 "점 마킹"', 3)
pic(s, 'fig_idea.png', 5.2, 2.6, w=23.4)

# 4 동작
s = slide('동작: 한 마리를 사람 손 없이', 4)
pic(s, 'fig_goal_ai.png', 1.0, 2.7, w=21.5)
text(s, 23.0, 3.4, 10, 13, ['입구 서보 문 + 적외선 빛 게이트', 'Pi 5 카메라 + YOLO 판별, 크기 측정으로 여왕벌 구분', '승강 바닥 → 말벌을 투명 격자판에 고정 (마킹 통 원리)', 'XY 리드스크루 + 서보 펜 → 가슴에 점 마킹', '여왕벌·다른 종·2마리 이상은 격리', '내보내며 시각 기록 → 재포획 시 왕복 시간'], 16, bullet=True)

# 5 설계
s = slide('설계: 2020 프레임 + 시판 트랩 레트로핏', 5)
pic(s, 'fig_rep.png', 1.0, 2.7, w=20.5)
text(s, 22.0, 3.4, 11, 13, ['역학계산 10문제 (정역학·동역학·재료역학)', '펜 누름 힘 0.31 N, 마지막 2 mm 감속', 'CAD 검사: 움직이는 28 × 고정 139 새 겹침 0', '제어 시뮬레이션 274개 통과 (92·90·37·55)', '12 V 전원 하나, 재료비 60만 원 안에서 정산'], 16, bullet=True)

# 6 판별
s = slide('판별: VespAI 가중치를 우리 격자 조건으로 YOLO 파인 튜닝', 6)
pic(s, 'chart_v3.png', 1.0, 2.8, w=19.5)
text(s, 21.5, 3.4, 11.5, 13, ['원래 VespAI: 격자 너머 말벌을 거의 못 찾음 (11/02 시험)', '표본 6마리 · 사진 155장으로 파인 튜닝', 'v3: 학습에 안 쓴 표본 2마리 917/917 장면 검출 (철망 시험, 신뢰도 50 % 이상)', '격자만 화면 헛것 2.1 %', '다음: 트랩 카메라 (CM3)로 다시 시험'], 16, bullet=True)

# 7 기대효과
s = slide('기대효과와 향후 계획', 7)
pic(s, 'fig_use.png', 1.0, 2.7, w=19.5)
text(s, 21.0, 3.4, 12, 13, ['둥지 탐색 첫 단계의 사람 위험·시간 감소', '공공기관 (B2G) 조사 장비, 양봉농가는 방제 모드', '실물 조립 후 표본 말벌 동작 시험 (확정), 야외 귀소 시험은 후속 연구', '조사 모드는 관계 기관 확인 후 운용', '시제품 한 색 → 여러 색 마커로 완전 자동화, 특허 검토'], 16, bullet=True)

prs.save('말벌트랩_발표.pptx'); print('ok')
