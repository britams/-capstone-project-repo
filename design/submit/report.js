const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, HeadingLevel, AlignmentType, Table, TableRow, TableCell,
  WidthType, ShadingType, ImageRun, LevelFormat, PageBreak, Footer, PageNumber, BorderStyle } = require('docx');

const FONT = '맑은 고딕';
const W = 9026; // A4 본문 폭 (DXA, 여백 1인치)
const p = (text, o = {}) => new Paragraph({ spacing: { after: 100, line: 300 }, ...o, children: [new TextRun({ text, font: FONT, size: 22, ...(o.run || {}) })] });
const b = (text) => new Paragraph({ numbering: { reference: 'bul', level: 0 }, spacing: { after: 60, line: 290 }, children: [new TextRun({ text, font: FONT, size: 22 })] });
const h1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun({ text: t, font: FONT })] });
const h2 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun({ text: t, font: FONT })] });
const cap = (t) => new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 200 }, children: [new TextRun({ text: t, font: FONT, size: 18, color: '555555' })] });
function img(file, wpx, ratio) {
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 120, after: 60 },
    children: [new ImageRun({ type: 'png', data: fs.readFileSync(file), transformation: { width: wpx, height: Math.round(wpx * ratio) } })] });
}
const border = { style: BorderStyle.SINGLE, size: 4, color: 'AAAAAA' };
function table(rows, widths) {
  const tw = widths.reduce((a, c) => a + c, 0);
  return new Table({ width: { size: tw, type: WidthType.DXA }, columnWidths: widths,
    rows: rows.map((r, i) => new TableRow({ tableHeader: i === 0, children: r.map((c, j) => new TableCell({
      width: { size: widths[j], type: WidthType.DXA }, borders: { top: border, bottom: border, left: border, right: border },
      shading: i === 0 ? { fill: 'E8F0FA', type: ShadingType.CLEAR, color: 'auto' } : undefined,
      margins: { top: 60, bottom: 60, left: 100, right: 100 },
      children: [new Paragraph({ children: [new TextRun({ text: c, font: FONT, size: 19, bold: i === 0 })] })] })) })) });
}
const sp = () => new Paragraph({ children: [] });

const cover = [
  new Paragraph({ spacing: { before: 2400 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: '창의적종합설계 최종보고서', font: FONT, size: 32, color: '555555' })] }),
  new Paragraph({ spacing: { before: 400, after: 200 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: 'YOLO 판별 기반 등검은말벌 자동 마킹·둥지 거리 추정 트랩', font: FONT, size: 40, bold: true, color: '1F2A44' })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: '— 시판 트랩 장착형 자동 표시 모듈 —', font: FONT, size: 28, color: '2B6CB0' })] }),
  new Paragraph({ spacing: { before: 2400 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: '팀 초벌 | 이서현 (팀장) · 이승준', font: FONT, size: 26 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: '국립공주대학교 기계자동차공학부 기계공학전공', font: FONT, size: 24 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ text: '지도교수 김성관', font: FONT, size: 24 })] }),
  new Paragraph({ spacing: { before: 400 }, alignment: AlignmentType.CENTER, children: [new TextRun({ text: '2026. 11. 30.', font: FONT, size: 24 })] }),
  new Paragraph({ children: [new PageBreak()] }),
];

const body = [
  h1('요약'),
  p('등검은말벌은 꿀벌을 잡아먹는 외래종으로, 피해를 줄이는 근본 대책은 둥지 제거임. 둥지를 찾는 첫 단계인 "말벌을 잡아 몸에 표시하고 돌아오는 시간을 재는 일"은 지금 사람이 손으로 하고 있어 쏘임 위험과 시간 부담이 큼. 본 과제는 이 단계를 사람 없이 하는 모듈을 설계함. 시판 말벌 트랩에 얹어, 들어온 말벌을 한 마리씩 가두고 → YOLO 모델로 종을 판별하고 크기를 재어 여왕벌을 가려낸 뒤 → 승강 바닥으로 말벌을 투명 격자판에 고정하고 → XY 펜으로 가슴에 점 마킹을 한 뒤 → 내보내며 시각을 기록함. 여왕벌·다른 종은 표시 없이 격리함.'),
  p('고정 방식은 양봉가의 여왕벌 마킹 통 원리를 기계화한 것이고, 판별은 공개 모델 VespAI의 가중치를 우리 표본과 격자 조건으로 파인 튜닝해 학습에 쓰지 않은 표본의 철망 너머 시험 영상 917/917 장면에서 말벌을 찾음. CAD 움직임·간섭 검사와 제어 시뮬레이션 (시험 274개 통과)을 수행했고, 실물은 부품 입고 후 조립해 표본 말벌로 시험할 예정임.'),

  h1('1. 서론'),
  h2('1.1 배경과 필요성'),
  b('등검은말벌은 2019년 생태계교란 생물로 지정됨. 먹이의 대부분이 꿀벌이라 양봉 피해가 큼.'),
  b('트랩으로 잡아도 둥지의 여왕벌이 일벌을 계속 생산해 피해가 계속됨. 둥지를 일찍 찾아 없애는 것이 핵심 대책으로 꼽힘 (Kennedy 2018, Rojas-Nossa 2022).'),
  b('둥지 찾기는 말벌을 잡아 표시한 뒤 왕복 시간으로 거리를 추정하는 방식이 쓰임. 거리 = (왕복 시간 − 둥지 체류 45초) ÷ 2 × 비행 속도 1.8~5.4 m/s (Rojas-Nossa 2022).'),
  b('지금은 이 표시를 사람이 손으로 함: 얼음 마취 10~12분 후 고정판에 묶어 표시 (Kennedy 2018), 마킹 통으로 눌러 표시 (Rojas-Nossa 2022). 쏘임 위험과 시간 부담이 있음.'),
  h2('1.2 선행 연구'),
  table([
    ['구분', '선행 연구', '한 일', '본 과제와의 관계'],
    ['판별', 'VespAI (O\'Shea-Wheller 외 2024)', '라즈베리파이 4 + YOLOv5s로 등검은말벌·유럽말벌 판별', '판별까지만 함 → 출발 가중치로 사용, 우리 조건으로 파인 튜닝'],
    ['고정·표시', '여왕벌 마킹 통 (양봉 표준 도구)', '플런저로 벌을 망에 눌러 망 너머로 표시', '원리를 승강 바닥 + 투명 격자로 기계화'],
    ['자동 표시', 'Martin 2006, Hagler 2011, Mikery-Pacheco 2013', '벌통 입구에서 지나가는 벌 모두에 가루·물감 자동 표시', '판별 없이 전부 표시 → 본 과제는 고른 한 마리에만 표시'],
    ['추적법', 'Wang 2024 리뷰, Kennedy 2018, Lioy 2021', '무선 발신기·하모닉 레이더 등 5가지 추적법', '모두 사람이 붙잡아 부착 → 자동 표시 없음'],
  ], [1100, 2300, 2900, 2726]),
  img('fig_idea.png', 560, 21.4 / 31.4),
  cap('그림 1. 마킹실 작동 원리 — 여왕벌 마킹 통의 "눌러 고정" + 펜 플로터의 "점 마킹"을 합친 본 과제의 착상'),
  h2('1.3 목표와 요구 조건'),
  table([
    ['번호', '요구 조건', '값·근거'],
    ['R1', '한 번에 한 마리만 처리', '"한 마리를 정확히" 원칙 (10/28)'],
    ['R2', '한 마리 처리 시간', '3분 이내'],
    ['R3', '여왕벌·다른 종은 표시하지 않음', '격리 (조사 모드)'],
    ['R4', '사람이 말벌을 만지지 않음', '가두기~내보내기 전 과정 자동'],
    ['R5', '시판 트랩에 얹는 모듈', '「야생 말벌 포획기」 레트로핏'],
    ['R6', '전원 하나, 저전압', '12 V 5 A 어댑터 1개'],
    ['R7', '재료비', '지원 50만 원 안에서 정산 (정산 보고서 별도)'],
  ], [1000, 3800, 4226]),

  h1('2. 설계 과정'),
  h2('2.1 방향 변천'),
  table([
    ['날짜', '방향', '바뀐 이유'],
    ['9/16', '형광 가루 자가 표시 + 비행 방향 추정', '계획서 제출안'],
    ['10/2', '피스톤 + 패드 + 왕복 시간', '가루는 양 조절이 어려움'],
    ['10/8', '비행 방향·거리 추정 삭제', '최문보 교수님 (경북대) 자문'],
    ['10/11', '수성 아크릴 마커, 여왕벌 격리', '표시가 오래 남고 말벌에 안전'],
    ['10/28', '시판 트랩 레트로핏, 바닥 승강형 마킹실', '"한 마리를 정확히", 새 트랩 제작 대신 모듈'],
    ['11/02~', 'XY 리드스크루 마킹부, 빛 게이트 3쌍, 12 V 단일 전원', '역학계산·제어 시뮬레이션 결과 반영'],
    ['11/14', '바닥 구동을 리니어 서보 하나로 단순화', '교수님 피드백 "로드셀은 과함", 부품 수 감소'],
    ['11/23', 'XY 모터를 NEMA17 + T8로 교체 검토, XY 판 PETG 프린트·아크릴로 변경', '기존 모터 납기 지연'],
  ], [1000, 4000, 4026]),
  h2('2.2 개념설계와 동작 순서'),
  b('운용 모드 2개: 방제 모드 (구별 없이 전부 가둠), 조사 모드 (일벌만 표시해 내보냄 — 퇴치 권한이 있는 공공기관 운용 전제).'),
  b('기능 분해: 들이기 → 가려내기 → 붙잡기 → 점 찍기 → 내보내고 기록.'),
  img('fig_goal_ai.png', 560, 21.4 / 31.4),
  cap('그림 2. 한 마리 처리 동작 순서와 ② 판별 — VespAI 원본 실행 화면, 우리 격자판 조건 파인 튜닝 학습 사진'),

  h1('3. 상세 설계'),
  img('fig_rep.png', 520, 21.4 / 31.4),
  cap('그림 3. 전체 조립 CAD (D5g, 2020 알루미늄 프레임 + 시판 트랩)'),
  table([
    ['단계', '기구', '원리와 근거'],
    ['① 들이기', '입구 서보 문 + 적외선 빛 게이트 G2', '벌통 입구 계수기의 적외선 통로 판정 (Struye 1994, Quiles-Latorre 2024)'],
    ['② 가려내기', '라즈베리파이 5 + 카메라 + YOLOv5s', 'VespAI 가중치에서 우리 표본·격자 조건으로 파인 튜닝 (4.4절), 크기 측정으로 여왕벌 구분 (중순판 폭 4.4 mm 이상)'],
    ['③ 붙잡기', '승강 바닥 (mightyZAP 직선 서보) + 투명 아크릴 격자판 (두께 2, 네모 구멍 3.0 mm, 간격 4.4)', '여왕벌 마킹 통 원리. 격자를 투명하게 해 카메라가 말벌 전체를 봄 (불투명 격자는 열린 면적 36.5 %)'],
    ['④ 점 찍기', 'XY 리드스크루 이송 × 2 (모터: LM-NK1134 납기 지연으로 NEMA17 + T8 교체 예정) + 볼 부싱 SC08UU + 펜 들기 서보 + 수성 아크릴 마커', '펜 플로터 구조 (Mani 외 2018). 펜 누름 힘 0.25~0.34 N, 마지막 2 mm는 60 °/s 이하로 천천히'],
    ['⑤ 내보내고 기록', '방생 문 + 빛 게이트 G5 + release_time·capture_time 기록', '왕복 시간으로 둥지 거리 계산 (Rojas-Nossa 2022)'],
  ], [1300, 3500, 4226]),
  sp(),
  h2('3.1 전기·제어'),
  b('전원: 12 V 5 A 하나 → 퓨즈 → 비상 정지 → 강압 컨버터 2개 (5.0 V, 7.4 V).'),
  b('제어: Arduino UNO 2대 (UNO 1 trap_motion: XY·펜·바닥, UNO 2 trap_doors: 문·빛 게이트·조명, 펌웨어 v0.3) + Raspberry Pi 5 (카메라 판별, pi_link).'),
  b('안전 규칙: 빛 게이트가 비어 있음을 확인한 뒤 문을 닫음 (끼임 방지), 켤 때 서보를 하나씩 켬 (돌입 전류 3.2 A 방지).'),

  h1('4. 해석과 검증'),
  h2('4.1 역학계산 (11/02 발표, D5e 기준)'),
  table([
    ['번호', '대상', '결과'],
    ['M1', '바닥 올리는 나사', '필요 토크의 약 10배 여유'],
    ['M3', '펜 누름 힘', '0.31 N, 한계로 잡은 0.5 N 안'],
    ['M4', '펜 드는 서보', '약 14배 여유'],
    ['M6', '봉 처짐', '약 0.01 mm'],
    ['M7', '문 닫기', '약 0.2초 → 빛 게이트 확인 뒤 닫도록 순서 변경'],
    ['M8', '펜 내리는 속도', '빠르면 충격 2~5배 → 마지막 2 mm 감속'],
    ['M10', '진동', '공진 회전수 (2~3 rpm)만 피하면 됨'],
  ], [1000, 3000, 5026]),
  p('교재 유제 (Riley 정역학, Meriam 동역학, Gere 재료역학)로 방법을 먼저 확인한 뒤 우리 값으로 풂. 그 뒤 바닥 구동이 리니어 서보로 바뀌었고 XY 모터도 28BYJ-48 → LM-NK1134 → NEMA17 + T8 (교체 예정)로 바뀌어, M1 (바닥 나사)·M2 (펜 옮기는 힘)·M9 (옮기는 시간)는 바뀐 부품으로 다시 계산할 항목임.', { run: { size: 21 } }),
  h2('4.2 CAD 검사'),
  b('FreeCAD + Python 스크립트로 모델을 만들고 검사를 자동화함 (cad/run_full.py).'),
  b('움직이는 부품 28개 × 고정 부품 139개 사이 새 겹침 0, 알루미늄 판 17장 구멍 ↔ 끝단 거리 ≥ 1.04 mm (가공 업체 규칙 1 mm), 판정 PASS (11/20). 11/23 Y축 끝에서 찾은 겹침은 판 모양을 고쳐 해결.'),
  h2('4.3 제어 시뮬레이션'),
  b('실제 아두이노 펌웨어를 PC에서 가상 센서·모터로 실행: 모터 92/92, 문 90/90. Python 가짜 카메라·가짜 말벌로: Pi 연동 37/37, 처리 순서 55/55. 합계 274개 통과 (11/17).'),
  h2('4.4 판별 YOLO 파인 튜닝'),
  p('원래 VespAI는 위에서 내려다본 미끼판 영상으로 학습되어, 격자를 겹친 화면에서는 말벌을 거의 찾지 못함 (11/02 시험). 우리 표본 (등검은말벌 6마리)을 흰 종이 위·격자 아래에서 찍은 사진 155장으로 VespAI 가중치에서 이어서 학습함 = 파인 튜닝 (YOLOv5s, 640, freeze 10). 시험은 신뢰도 50 % 이상만 검출로 인정.'),
  img('chart_v3.png', 480, 3.6 / 6.4),
  cap('그림 4. 파인 튜닝 단계별 격자 너머 검출 장면 비율 (v1·v2·v3 시험 영상은 서로 다름)'),
  b('v3: 학습에 쓰지 않은 표본 2마리 영상에서 917/917 장면 검출, 격자만 있는 화면의 헛것 2.1 % (17/797).'),
  b('한계: 시험 격자는 검은 철망 4 mm (실제 아크릴 격자판과 모양 다름), 장면 기준 집계 (한 장면에서 일부 개체를 놓친 경우는 셈하지 않음), 다른 곤충 시험 없음, 웹캠 조건 → 트랩 카메라 (Camera Module 3)로 다시 시험 예정.'),

  h1('5. 제작'),
  b('구매·정산: 재료비 지원 50만 원 안에서 정산, 초과분은 팀 자비 (정산 보고서 별도 제출).'),
  b('가공: 알루미늄 판 10장 레이저 가공 주문 (meviy), 아크릴 판 9종 주문 (11/18), 3D 프린트 부품은 충남앵커공유대학 Craft-Lab에서 출력 예정.'),
  b('11/23 기준: 프레임·리니어 부품·전원·아크릴 대부분 입고, XY 모터 대기 (NEMA17 + T8로 교체 예정), XY 판은 PETG 프린트·아크릴로 변경 (11/23) → 입고 후 조립·시험.'),

  h1('6. 결론과 향후 계획'),
  h2('6.1 결론'),
  b('말벌 표시의 위험한 손작업 단계를 기계로 바꾸는 모듈을 설계함: 판별 (YOLO 파인 튜닝 + 크기 측정) + 고정 (마킹 통 원리의 승강 바닥) + 표시 (XY 펜).'),
  b('CAD·역학계산·제어 시뮬레이션으로 만들기 전에 검증하고, 판별은 격자 조건에서 파인 튜닝으로 개선함.'),
  h2('6.2 기대효과'),
  img('fig_use.png', 520, 21.4 / 31.4),
  cap('그림 5. 공공기관 (B2G) 활용 흐름'),
  b('둥지 탐색 첫 단계의 사람 위험·시간 감소, 재포획 시각 기록으로 둥지 거리 범위 계산.'),
  h2('6.3 한계와 향후 계획'),
  b('실물 조립 후 표본 말벌로 판별·고정·표시 동작 시험 (확정). 표시 뒤 귀소 여부와 누르는 힘에 대한 살아 있는 말벌 안전은 방생 허가가 필요한 야외 시험 → 후속 연구로 제안.'),
  b('법: 생태계교란 생물의 방사는 금지 → 조사 모드는 공공기관 운용 전제, 관계 기관 확인 필요. 기본은 방제 모드.'),
  b('사양 확장: 시제품은 마커 한 색 (사람이 1시간마다 색 교체) → 여러 색 마커로 색 교체까지 완전 자동화 (Hagler 2011의 다중 표시 사례), 실외 방수·전원.'),

  h1('참고문헌'),
  ...[
    'Kennedy P.J. 외 (2018) Searching for nests of the invasive Asian hornet (Vespa velutina) using radio-telemetry. Communications Biology 1:88 (doi 10.1038/s42003-018-0092-9).',
    'Rojas-Nossa S.V. 외 (2022) Method for nest detection of the yellow-legged hornet in high density areas. Frontiers in Insect Science 2 (doi 10.3389/finsc.2022.851010).',
    'Lioy S. 외 (2021) Tracking the invasive hornet Vespa velutina in complex environments by means of a harmonic radar. Scientific Reports 11.',
    'Wang C. 외 (2024) A review of five existing hornet-tracking methods. Insects 15:601.',
    'O\'Shea-Wheller T.A. 외 (2024) VespAI: a deep learning-based system for the detection of invasive hornets. Communications Biology 7.',
    'Martin A.P. 외 (2006) A modular system for trapping and mass-marking bumblebees. Apidologie 37:341-350.',
    'Hagler J. 외 (2011) A method for distinctly marking honey bees originating from multiple apiary locations. Journal of Insect Science 11:143.',
    'Mikery-Pacheco O. 외 (2013) A method for mass marking honeybees. Acta Zoológica Mexicana 29(1):248-251.',
    'Struye M.H. 외 (1994) Microprocessor-controlled monitoring of honeybee flight activity at the hive entrance. Apidologie 25:384-395.',
    'Quiles-Latorre F.J. 외 (2024) FPGA-based bee counter system. IEEE Access 12.',
    'Mani S.R. 외 (2018) Design and implementation of low-cost 2D plotter CNC machine. IJERT 7(5).',
    'Riley W.F. 외, Engineering Mechanics: Statics / Meriam J.L. 외, Engineering Mechanics: Dynamics / Gere J.M., Mechanics of Materials.',
  ].map(t => new Paragraph({ numbering: { reference: 'num', level: 0 }, spacing: { after: 60 }, children: [new TextRun({ text: t, font: FONT, size: 19 })] })),
];

const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: 22 } } },
    paragraphStyles: [
      { id: 'Heading1', name: 'Heading 1', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: 32, bold: true, color: '1F2A44' }, paragraph: { spacing: { before: 360, after: 160 }, outlineLevel: 0, keepNext: true } },
      { id: 'Heading2', name: 'Heading 2', basedOn: 'Normal', next: 'Normal', quickFormat: true,
        run: { font: FONT, size: 26, bold: true, color: '2B6CB0' }, paragraph: { spacing: { before: 240, after: 120 }, outlineLevel: 1, keepNext: true } },
    ],
  },
  numbering: { config: [
    { reference: 'bul', levels: [{ level: 0, format: LevelFormat.BULLET, text: '•', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } }] },
    { reference: 'num', levels: [{ level: 0, format: LevelFormat.DECIMAL, text: '[%1]', alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 500, hanging: 500 } } } }] },
  ] },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1440, bottom: 1440, left: 1440, right: 1440 } } },
    footers: { default: new Footer({ children: [new Paragraph({ alignment: AlignmentType.CENTER, children: [new TextRun({ children: [PageNumber.CURRENT], font: FONT, size: 18 })] })] }) },
    children: [...cover, ...body],
  }],
});
Packer.toBuffer(doc).then(buf => { fs.writeFileSync('말벌트랩_최종보고서.docx', buf); console.log('ok'); });
