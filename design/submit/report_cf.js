// 2026 창의융합 경진대회 과제보고서 ([첨부 4] 양식 순서 그대로, CAP-AI-62)
// 학번은 레포에 안 넣음: SID1=… SID2=… node report_cf.js out.docx → soffice --convert-to pdf. 그림은 design/poster/*.png를 1800 px jpg(*_s.jpg)로 줄여 같은 폴더에 둠 (fig_goal_ai는 VespAI 사진 포함 — 레포에 없음)
const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, AlignmentType,
  ShadingType, ImageRun, BorderStyle, VerticalAlign, PageBreak } = require('docx');

const FONT = 'Noto Sans CJK KR';
const W = 10206;               // 본문 폭 (DXA) = A4 210 mm − 좌우 여백 각 15 mm
const GRAY = 'D9D9D9', LIGHT = 'F2F2F2';
const bd = { style: BorderStyle.SINGLE, size: 6, color: '000000' };
const borders = { top: bd, bottom: bd, left: bd, right: bd };

const r = (t, o = {}) => new TextRun({ text: t, font: FONT, size: o.size || 19, bold: o.bold, color: o.color, italics: o.it });
const P = (runs, o = {}) => new Paragraph({ children: Array.isArray(runs) ? runs : [r(runs, o)], alignment: o.align,
  spacing: { before: o.before ?? 30, after: o.after ?? 30, line: o.line ?? 290 }, indent: o.indent });
const head = t => P([r('▪ ' + t, { bold: true, size: 20 })], { before: 120, after: 60 });
const li = (t, lvl = 0) => P([r((lvl ? '· ' : '- ') + t)], { indent: { left: 240 + lvl * 300, hanging: 200 } });
const cap = t => P([r(t, { size: 17, color: '333333' })], { align: AlignmentType.CENTER, before: 40, after: 120 });
function img(file, wcm) {
  const { execSync } = require('child_process');
  const [pw, ph] = execSync(`python3 -c "from PIL import Image;i=Image.open('${file}');print(i.width,i.height)"`).toString().trim().split(' ').map(Number);
  const w = Math.round(wcm / 2.54 * 96), h = Math.round(w * ph / pw);
  return new Paragraph({ alignment: AlignmentType.CENTER, spacing: { before: 80, after: 20 }, keepNext: true, keepLines: true,
    children: [new ImageRun({ type: 'jpg', data: fs.readFileSync(file), transformation: { width: w, height: h } })] });
}
const cell = (children, o = {}) => new TableCell({ borders, width: { size: o.w, type: WidthType.DXA }, columnSpan: o.span, rowSpan: o.rows,
  verticalAlign: o.va || VerticalAlign.CENTER, shading: o.fill ? { fill: o.fill, type: ShadingType.CLEAR, color: 'auto' } : undefined,
  margins: { top: 60, bottom: 60, left: 100, right: 100 },
  children: (Array.isArray(children) ? children : [children]).map(c => typeof c === 'string' ? P(c, { align: o.align ?? AlignmentType.CENTER, size: o.size }) : c) });
function table(widths, rows, o = {}) {      // rows: [[text|{t,fill,bold}...]]
  return new Table({ width: { size: widths.reduce((a, b) => a + b), type: WidthType.DXA }, columnWidths: widths,
    rows: rows.map((row, ri) => new TableRow({ children: row.map((c, ci) => {
      const t = typeof c === 'string' ? { t: c } : c;
      const hdr = o.header && ri === 0;
      return cell(P([r(t.t, { bold: hdr || t.bold, size: o.size || 17 })], { align: t.align ?? (ci === 0 || hdr || o.center ? AlignmentType.CENTER : AlignmentType.LEFT), line: 260 }),
        { w: widths[ci], fill: hdr ? LIGHT : t.fill });
    }) })) });
}
const bar = t => new TableRow({ children: [cell(P([r(t, { bold: true, size: 21 })], { align: AlignmentType.CENTER }), { w: W, fill: GRAY })] });
const body = ch => new TableRow({ children: [cell(ch, { w: W, va: VerticalAlign.TOP })] });

// ── 1쪽: 표지 표
const C = [1500, 1150, 2500, 1350, 650, 650, 2406];   // 합 = W
const info = new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: C, rows: [
  new TableRow({ children: [cell(P([r('작품(과제)명', { bold: true })], { align: AlignmentType.CENTER }), { w: C[0], fill: LIGHT }),
    cell(P([r('YOLO 판별 기반 등검은말벌 자동 마킹·둥지 거리 추정 트랩', { bold: true, size: 21 })], { align: AlignmentType.CENTER }), { w: W - C[0], span: 6 })] }),
  new TableRow({ children: [cell(P([r('팀명', { bold: true })], { align: AlignmentType.CENTER }), { w: C[0], fill: LIGHT }),
    cell(P([r('초벌', { size: 21 })], { align: AlignmentType.CENTER }), { w: W - C[0], span: 6 })] }),
  new TableRow({ children: [cell(P([r('과제수행팀', { bold: true })], { align: AlignmentType.CENTER }), { w: C[0], rows: 3, fill: LIGHT }),
    ...['역할', '학과(전공)', '학번', '학년', '성별', '성명'].map((t, i) => cell(P([r(t, { bold: true, size: 18 })], { align: AlignmentType.CENTER }), { w: C[i + 1], fill: LIGHT }))] }),
  new TableRow({ children: ['팀장', '기계자동차공학부\n(기계공학전공)', process.env.SID1 || '(학번)', '4', '남', '이서현'].map((t, i) =>
    cell(t.split('\n').map(s => P([r(s, { size: 18 })], { align: AlignmentType.CENTER, before: 0, after: 0 })), { w: C[i + 1] })) }),
  new TableRow({ children: ['팀원', '기계자동차공학부\n(기계공학전공)', process.env.SID2 || '(학번)', '3', '남', '이승준'].map((t, i) =>
    cell(t.split('\n').map(s => P([r(s, { size: 18 })], { align: AlignmentType.CENTER, before: 0, after: 0 })), { w: C[i + 1] })) }),
  new TableRow({ children: [cell(P([r('지적재산권', { bold: true })], { align: AlignmentType.CENTER }), { w: C[0], fill: LIGHT }),
    cell([P([r('□ 해당 (특허(출원번호 기입), 실용신안(등록번호 기입), 기타(지재권유형기입))', { size: 18 })], { align: AlignmentType.LEFT }),
          P([r('■ 해당없음  (표본 시험 결과로 자동 고정·표시 기구 특허 출원 검토 예정)', { size: 18 })], { align: AlignmentType.LEFT })], { w: W - C[0], span: 6 })] }),
] });

const main = [];
main.push(bar('작품사진'));
main.push(body([
  img('fig_rep_s.jpg', 14), cap('그림 1. 작품 전체 모습 — FreeCAD 3D 설계 모델 (2020 알루미늄 프레임 + 시판 트랩 + 마킹 모듈)'),
  li('실물은 부품 입고 중이며 입고 후 조립 예정 (XY 구동부 모터 입고 대기) → 최종 결과물 대신 3D 설계 모델 사진 수록, 실물 사진은 조립 후 추가 예정'),
  li('설계 모델은 FreeCAD + Python 생성 스크립트로 만들고, 같은 모델로 움직임·간섭 검사 수행'),
]));

main.push(bar('과제필요성, 개발동기 및 목적'));
main.push(body([
  head('과제 필요성 및 개발 동기'),
  li('등검은말벌: 2003년 부산에서 처음 확인, 2019년 생태계교란 생물 지정, 현재 전국 분포 [1][3]'),
  li('꿀벌 포식으로 양봉 피해 확산 — 한 마리가 하루 꿀벌 약 10마리 사냥, 봉군 80 % 이상 폐사 사례 [2]'),
  li('트랩 방제의 한계: 트랩으로 잡아도 둥지의 여왕벌이 일벌을 계속 생산하고, 트랩에 잡힌 곤충의 96 % 이상은 등검은말벌이 아닌 다른 곤충 [8]'),
  li('둥지 하나가 최대 13,000마리와 새 여왕벌 수백 마리를 생산 → 방제의 핵심은 둥지 제거 [6]'),
  li('둥지는 높은 나무 위에 있어 여름에 찾기 어려움 [2]'),
  li('현재 둥지 탐색법: 말벌을 잡아 몸에 표시한 뒤 놓아주고, 다시 돌아오는 시간으로 거리를, 날아가는 방향으로 둥지 쪽을 추정 [9][12]'),
  li('문제: 표시 작업을 사람이 손으로 수행 — 얼음으로 마취한 뒤 고정판에 묶어 표시 [9], 마킹 통으로 눌러 표시 [12] → 쏘임 위험과 긴 작업 시간'),
  li('둥지 하나를 찾는 데 사람 시간 약 21시간이 든 사례 [11]'),
  head('개발목적'),
  li('말벌 포획부터 판별·고정·점 마킹·내보냄까지 사람 손 없이 자동화'),
  li('YOLO 판별·크기 측정으로 등검은말벌 일벌만 골라 점 마킹'),
  li('지정한 개체만 선택 격리 (현재 여왕벌·다른 종·2마리 이상) — 격리 대상은 설정으로 변경 가능'),
  li('마킹 색과 재포획 시각으로 내보낸 시간대를 대략 파악 → 말벌집까지 거리 범위 추정'),
  li('새 트랩 제작이 아닌 시판 트랩 위에 얹는 모듈 → 지자체·방제 기관용 조사 장비(B2G)로 보급'),
]));

main.push(bar('선행연구 및 기술현황'));
main.push(body([
  head('선행연구 및 기술현황'),
  table([2300, 3200, 2400, 2306], [
    ['선행 연구', '한 일', '한계', '본 과제 활용'],
    ['VespAI [14]\n(O\'Shea-Wheller 외 2024)', '라즈베리파이 + YOLOv5로 등검은말벌·유럽말벌 판별', '판별까지만, 표시 기능 없음', '가중치를 출발점으로 우리 조건에 파인 튜닝'],
    ['여왕벌 마킹 통 [30]', '플런저로 벌을 망에 눌러 망 너머로 표시', '사람이 손으로 누르고 표시', '승강 바닥 + 투명 격자판으로 기계화'],
    ['벌 대량 표시 [17][18][19]', '벌통 입구에서 지나가는 벌 모두에 가루·물감 자동 표시', '판별 없이 전부 표시', '판별한 한 마리에만 점 마킹'],
    ['말벌 추적법 [9][20][21]', '무선 발신기·하모닉 레이더 등 5가지 추적', '모두 사람이 붙잡아 부착', '표시 단계를 자동화'],
    ['벌통 입구 계수기 [23][24]', '적외선 빛 차단으로 출입 판정', '표시 기능 없음', '입구·방생 문의 빛 게이트'],
    ['2D 펜 플로터 [28]', '리드스크루 XY로 펜 이동', '곤충 표시 용도 아님', 'XY 펜 마킹부 구조'],
  ], { header: true }),
  P(''),
  head('용어 풀이 (본문에 나오는 말)'),
  table([2300, 7906], [
    ['용어', '뜻'],
    ['생태계교란 생물', '생태계 균형을 깨뜨릴 우려가 있어 환경부가 지정해 관리하는 외래 생물 — 함부로 풀어 주거나 옮기는 행위가 법으로 제한됨'],
    ['일벌 · 여왕벌', '여왕벌은 알을 낳아 무리를 늘리는 개체, 일벌은 먹이 사냥과 둥지 관리를 맡는 개체'],
    ['표시-귀소 탐색', '말벌에 색 점을 찍어 놓아준 뒤, 둥지에 다녀와 다시 오는 시간과 날아가는 방향으로 둥지 위치를 찾는 방법'],
    ['YOLO (욜로)', '사진을 한 번 보고 그 안의 물체가 무엇인지와 어디 있는지(네모 상자)를 함께 찾는 딥러닝 물체 검출 모델 (You Only Look Once). YOLOv5s는 그중 작고 빠른 판'],
    ['가중치', 'AI 모델이 학습으로 얻은 숫자 값들의 묶음 — 모델이 배운 내용을 담은 파일'],
    ['파인 튜닝', '처음부터 학습하지 않고, 이미 학습된 가중치에서 출발해 우리 사진으로 조금 더 학습시키는 방법'],
    ['라벨 · 신뢰도', '라벨은 학습 사진에 사람이 "여기가 말벌"이라고 그린 네모 표시, 신뢰도는 AI가 "말벌이다"라고 판단한 확신 정도 (0~1, 본 과제는 0.5 이상만 인정)'],
    ['중흉배판', '말벌 가슴 등 쪽 가운데의 단단한 판 — 이 판의 폭으로 여왕벌과 일벌을 구분'],
    ['리드스크루', '모터가 나사 축을 돌리면 축에 끼운 너트가 앞뒤로 곧게 움직이는 부품 (도는 움직임 → 곧은 움직임)'],
    ['스텝 모터 · 서보', '스텝 모터는 정해진 작은 각도씩 끊어 돌아 위치를 정확히 맞추는 모터, 서보는 명령한 각도(또는 길이)로 가서 멈추는 구동기'],
    ['리니어 서보', '막대가 명령한 길이만큼 곧게 나오고 들어가는 서보 — 본 과제에서 바닥을 올리고 내림'],
    ['스카치 요크', '돌아가는 핀이 판의 세로 홈을 밀어 판을 곧게 미끄러지게 하는 기구 — 본 과제의 미닫이 문'],
    ['빛 게이트', '적외선 빛줄기를 쏘고 받는 센서 — 빛이 끊기면 그 자리를 무언가 지나간 것으로 판단'],
    ['강압 컨버터 · 돌입 전류', '강압 컨버터는 12 V를 5 V·7.4 V처럼 낮은 전압으로 바꾸는 부품, 돌입 전류는 모터를 켜는 순간 잠깐 크게 흐르는 전류'],
    ['자유물체도', '물체 하나만 떼어 놓고 그 물체가 받는 힘을 모두 화살표로 그린 그림 — 역학 계산의 출발점'],
    ['공진', '흔들어 주는 박자가 물체 고유의 흔들림 박자와 맞아 흔들림이 크게 커지는 현상'],
    ['자립 (나사)', '나사에 힘이 걸려도 나사가 스스로 거꾸로 돌아 풀리지 않는 성질'],
    ['시뮬레이션', '실제 기계 없이 컴퓨터 안에서 센서·모터를 흉내 내어 프로그램을 시험하는 일'],
    ['간섭 검사', '3D 모델에서 부품끼리 서로 파고드는(겹치는) 곳을 찾는 검사'],
    ['FreeCAD · Raspberry Pi · Arduino', '무료 3D 설계 프로그램 · 카메라와 AI를 돌리는 손바닥만 한 컴퓨터 · 모터와 센서를 직접 움직이는 작은 제어 보드'],
    ['B2G', '기업이 정부·지자체·공공기관에 제품을 파는 사업 방식 (Business to Government)'],
  ], { header: true }),
  head('작품 제작에 필요한 기술'),
  li('객체 검출: YOLOv5s (한 장의 사진에서 물체 위치를 네모로 찾는 딥러닝 모델) + 파인 튜닝 (이미 학습된 가중치를 우리 촬영 조건에 맞게 추가 학습)'),
  li('크기 측정: 격자 간격 4.4 mm를 자로 써서 가슴(중흉배판) 폭 측정 → 폭 4.4 mm 이상이면 여왕벌로 판정 (Pérez-de-Heredia 2017 기준)'),
  li('기구: 리니어 서보 승강 바닥, XY 리드스크루 이송 + 펜 들기 서보, 문 3개 (MG90S 서보, 스카치 요크 미닫이)'),
  li('센서·제어: 적외선 빛 게이트 3쌍, Raspberry Pi 5 + Camera Module 3, Arduino UNO 2대, 12 V 단일 전원'),
  li('설계 검증: FreeCAD 생성 스크립트·간섭 검사, 역학 계산 (정역학·동역학·재료역학), 펌웨어 PC 시뮬레이션'),
]));

main.push(bar('과제해결방법 및 수행과정'));
main.push(body([
  head('문제해결 방안 및 과정'),
  li('해결 방안: 판별 (YOLO) + 고정 (마킹 통 원리) + 표시 (펜 플로터) 세 가지 기존 기술을 한 모듈로 결합'),
  li('원칙: "한 마리를 정확히" — 한 번에 한 마리만 들여보내 판별한 뒤, 일벌은 고정·점 마킹 후 내보내고 지정 개체는 격리'),
  li('외부 전문가 자문으로 처음 계획 (형광 가루 자가 표시·비행 방향 추정) 폐기 → 직접 점 마킹 + 재포획 시각 기록으로 전환'),
  li('부품 수를 줄이는 방향으로 단순화: 바닥 구동을 로드셀 → 스프링·스위치 → 리니어 모듈 → 리니어 서보 하나로 변경 (위치와 힘 상한을 한 부품으로)'),
  li('만들기 전에 검증: CAD 간섭 검사, 역학 계산, 제어 프로그램 PC 시뮬레이션, AI 파인 튜닝 시험'),
  new Paragraph({ keepNext: true, alignment: AlignmentType.CENTER, spacing: { before: 120, after: 40 }, children: [r('표1. 수행 과정과 주요 결정', { bold: true, size: 18 })] }),
  table([1400, 4300, 4506], [
    ['날짜', '결정·수행', '이유·근거'],
    ['9/28', '지도교수 피드백 반영', '카메라 반응 속도, 일벌·여왕벌 분류, 통로 구체화 요청'],
    ['10/2·10/8', '외부 전문가 자문 → 형광 가루 자가 표시·비행 방향 추정 폐기', '가루가 쉽게 지워짐, 빠른 비행을 가까이서 촬영해 방향 잡기 어려움'],
    ['10/11', '수성 아크릴 마커 사용, 여왕벌 격리, 문헌 기반 설계 입력값 확정', '자문 결과 직접 칠하는 표시로 전환, 흉부 폭·몸길이·트랩 입구 8~9 mm 문헌 값'],
    ['10/28', '재설계: 시판 트랩 장착 모듈, 바닥 승강형 마킹실', '"한 마리를 정확히" 원칙, 새 트랩 제작 대신 모듈'],
    ['11/02', '역학 계산 10항목 발표', '힘은 넉넉, 문 끼임·펜 충격 위험 → 제어 순서 반영'],
    ['11/09', '카메라 Camera Module 3, 카메라–격자 153.5 mm', '720p 60 fps, 마킹실 전체가 시야에 들어감'],
    ['11/14', '바닥 구동을 리니어 서보 하나로 단순화', '교수님 피드백 "로드셀은 과함", 부품 수 감소'],
    ['11/15', 'YOLO 파인 튜닝 v1~v3', '원본 모델이 격자 너머 말벌을 거의 못 찾음'],
    ['11/17', '12 V 단일 전원, 펌웨어 v0.3, 제어 시험 274개 통과', '배선 단순화, 끼임 방지 규칙'],
    ['11/18', 'CAD 전체 수정·검사 자동화 (run_full)', '움직이는 부품 새 겹침 0 판정'],
    ['11/23', 'XY 모터 대체 검토 (NEMA17 + T8) 및 조립 검사', '기존 모터 납기 지연'],
  ], { header: true }),
  img('fig_goal_ai_s.jpg', 14), cap('그림 2. 작동 5단계와 ② 판별 단계 — VespAI 원본 실행 화면, 우리 격자판 조건 파인 튜닝 학습 사진'),
]));

main.push(bar('과제의 내용'));
main.push(body([
  head('결과물의 특장점'),
  li('사람 손 없는 점 마킹: 위험한 손 표시 단계를 기계가 대신해 쏘임 위험 감소'),
  li('판별: YOLOv5s를 VespAI 가중치에서 우리 표본·격자 조건으로 파인 튜닝 → 학습 미사용 표본 917/917 장면 검출 (철망 시험)'),
  li('여왕벌 구분: 격자 간격 4.4 mm를 자로 써서 가슴 폭 측정 (사진 5장의 중앙값), 못 재면 계절 규칙 적용 (3~5월·9~11월은 여왕벌로 보고 격리)'),
  li('고정: 여왕벌 마킹 통 원리를 기계화 — 리니어 서보가 백색 바닥을 올려 말벌을 투명 격자판 (2T, 네모 구멍 3.0 mm, 간격 4.4 mm)에 눌러 고정, 위치 지정 서보라 바닥이 격자 아래 5 mm에서 바로 정지'),
  li('점 마킹: XY 이송 장치가 펜을 가슴 위로 옮긴 뒤 격자 구멍으로 점 마킹, 펜 누르는 힘 약 0.3 N (홀더·마커 자중), 마지막 2 mm는 천천히'),
  li('한 마리씩: 입구 문 + 빛 게이트로 한 마리씩 들여보냄, 문틈이 빈 것을 확인한 뒤 닫아 끼임 방지'),
  li('선택 격리: 지정한 개체만 표시 없이 격리 (현재 여왕벌·다른 종·2마리 이상), 방제 모드는 표시 없이 모두 격리'),
  li('종일 무인 운용: 낮에는 표시·방생, 밤에는 LED 조명으로 포획만 (해 뜨고 30분 뒤 ~ 해 지기 30분 전을 낮으로 계산, 말벌은 밤에 비행하지 않음 [31])'),
  li('기록: 나간 시각·다시 잡힌 시각 자동 기록 → 왕복 시간 계산'),
  li('확장성: 시제품은 마커 한 색 (사람이 1시간마다 색 교체) → 여러 색 마커로 색 교체까지 완전 자동화 목표, 격리 대상 변경 가능'),
  li('설치: 시판 트랩 위에 얹는 모듈, 2020 알루미늄 프레임'),
  img('fig_struct_s.jpg', 14), cap('그림 3. 장치 구성 — CAD 정면도 ① 포획통 ② 카메라 ③ 마킹실 ④ 제어·전원 ⑤ 시판 트랩'),
  img('fig_idea_s.jpg', 14), cap('그림 4. 마킹실 작동 원리 — ① 촬영 ② 바닥 상승·고정 ③ 정한 높이에서 정지 ④ 격자 구멍으로 점 마킹'),
]));

main.push(bar('과제의 기술 및 계산'));
main.push(body([
  head('개념 설계'),
  li('기능 분해: 들이기 → 가려내기 (판별) → 붙잡기 (고정) → 점 마킹 → 내보내고 기록'),
  li('형태 분석표로 기능별 대안 비교 → 바닥 승강형 마킹실 + XY 펜 + 빛 게이트 문 조합 선정'),
  li('운용 모드 2개: 조사 모드 (일벌만 표시해 내보냄 — 퇴치 권한이 있는 공공기관 운용 전제), 방제 모드 (표시 없이 모두 격리)'),
  li('처리 순서: 들어옴 (빛 게이트·입구 문 닫힘) → 판별 (YOLO·크기) → 고정 (바닥 상승) → 점 마킹 (XY 펜) → 내보냄 (방생 문, 시각 기록)'),
  img('fig_p_design_s.jpg', 10.5), cap('그림 5. 설계 요점 — 시판 트랩 장착형, 입구 통로, 마킹실, XY 펜, 설계 검토'),
  head('상세 설계'),
  table([1700, 4300, 4206], [
    ['기능', '부품·사양', '근거·비고'],
    ['들이기', '입구 서보 문 (MG90S) + 적외선 빛 게이트', '벌통 입구 계수기의 통로 판정 [23][24]'],
    ['판별', 'Raspberry Pi 5 + Camera Module 3 (720p 60 fps, 격자 위 153.5 mm) + YOLOv5s', 'VespAI 가중치에서 파인 튜닝 [14]'],
    ['고정', 'mightyZAP 리니어 서보 (행정 26 mm, 정격 6 N) + 투명 아크릴 격자판 2T', '여왕벌 마킹 통 원리 [30]'],
    ['점 마킹', 'XY 리드스크루 이송 + 펜 들기 SG90 서보 + 수성 아크릴 마커 (노랑)', '펜 플로터 구조 [28]'],
    ['내보냄·기록', '방생 문 + 빛 게이트, 나간 시각·재포획 시각 기록', '왕복 시간 → 거리 [12]'],
    ['전원·제어', '12 V 5 A 하나 → 퓨즈 → 비상 정지 → 강압 5.0 V·7.4 V, Arduino UNO 2대 + Pi 5', '배선 단순화, 켤 때 서보를 하나씩 켜 돌입 전류 방지'],
    ['조명', 'LED 3구 모듈 백색 12 V 2개 (카메라 판 아래)', '밤에도 촬영·포획'],
  ], { header: true }),
  P(''),
  P([r('표2. 역학 계산 (11/02 발표 기준, 교재 유제로 방법을 확인한 뒤 우리 값으로 풀이 [32])', { bold: true, size: 18 })], { align: AlignmentType.CENTER, before: 120 }),
  table([700, 1600, 3500, 3100, 1306], [
    ['번호', '항목', '무엇을 왜 계산했나', '결과', '분야'],
    ['M1', '바닥 올리는 나사', '모터 힘으로 바닥을 올릴 수 있는지, 멈췄을 때 스스로 내려가지 않는지', '10배 여유, 자립', '기계요소'],
    ['M2', '펜 옮기는 힘', 'XY 모터가 펜을 밀어 옮길 수 있는지', '수백 배 여유', '동역학'],
    ['M3', '찍는 힘', '펜이 말벌을 너무 세게 누르지 않는지', '0.31 N, 한계 0.5 N 안', '정역학'],
    ['M4', '펜 드는 서보', '서보가 펜을 들어 올릴 수 있는지', '14배 여유', '정역학'],
    ['M5', '한쪽 구동 끼임', '축 한쪽만 밀 때 비틀려 걸리지 않는지', 'X축 문제없음, 안내 핀은 PTFE 테이프로 마찰 감소', '정역학 (마찰)'],
    ['M6', '봉 처짐', '펜 무게로 안내 봉이 휘는 양', '0.01 mm (무시할 수준)', '재료역학'],
    ['M7', '문 닫기', '문이 닫히는 시간과 말벌이 끼일 위험', '약 0.2초 → 빛 게이트로 빈 것을 확인한 뒤 닫음', '동역학'],
    ['M8', '펜 내리는 속도', '펜을 내려찍을 때의 충격', '빠르면 충격 2~5배 → 마지막 2 mm 감속', '동역학'],
    ['M9', '옮기는 시간', '한 마리를 처리하는 데 걸리는 시간', '약 30초, 잉크 건조가 관건', '동역학'],
    ['M10', '흔들림 박자', '모터 진동이 기계의 고유 진동과 맞아 크게 흔들리지 않는지', '2~3 rpm 공진만 피하면 됨', '동역학'],
  ], { header: true }),
  li('11/02 이후 바닥 구동이 리니어 서보로 바뀌었고 XY 모터도 바뀔 예정 → M1·M2·M9는 바뀐 부품으로 다시 계산 예정'),
  img('m3_s.jpg', 11), cap('그림 6. M3 찍는 힘 자유물체도'),
  img('m8_s.jpg', 11), cap('그림 7. M8 펜 내려찍기 충격 자유물체도'),
  head('검증 (만들기 전)'),
  li('CAD: FreeCAD 전체 조립 모델에서 펜·바닥을 여러 자세로 움직이며 부품 겹침 검사 — 움직이는 부품 28개 × 고정 부품 139개 새 겹침 0 (11/18), 이후 찾은 Y축 끝 겹침은 판 모양을 고쳐 해결 (11/23)'),
  li('제어: 실제 아두이노 펌웨어를 PC에서 가상 센서·모터로 실행 (모터 92개, 문 90개) + Python 가짜 카메라·가짜 말벌로 처리 순서 시험 (통신 37개, 처리 55개) → 274개 통과 (274개 상황 모두 예상한 대로 동작)'),
  li('AI: 학습에 쓰지 않은 표본 2마리의 영상을 장면(사진 한 장)마다 검사, 신뢰도 50 % 이상만 검출로 인정 → 917/917은 장면 917개 모두에서 말벌을 1마리 이상 찾았다는 뜻'),
  img('chart_v3_s.jpg', 12), cap('그림 8. YOLO 파인 튜닝 단계별 격자 너머 검출 장면 비율 — v1 32.0 % (312/975), v2 26.1 % (472/1811), v3 100 % (917/917), 단계마다 시험 영상이 다름'),
  li('v3: 표본 6마리·사진 155장으로 학습, 격자만 있는 장면 헛검출 2.1 % (17/797)'),
  li('한계: 시험 격자는 검은 철망 4 mm (실제 아크릴 격자와 모양 다름), 장면 기준 집계, 다른 곤충·살아 있는 말벌 미시험, 웹캠 조건'),
]));

main.push(bar('기대효과 및 개선방향'));
main.push(body([
  head('기대효과 및 개선방향'),
  img('fig_use_s.jpg', 14), cap('그림 9. 활용 — 지자체·방제 기관용 둥지 조사 장비 (B2G) 흐름과 거리 추정'),
  li('실용성: 손으로 잡아 표시하던 위험한 작업을 기계가 대신 → 쏘임 위험 감소'),
  li('실용성: 낮엔 표시·방생, 밤엔 LED로 포획만 → 사람 없이 종일 운용, 표시·시각 기록 인력 절감'),
  li('실용성: 마킹 색·재포획 시각 → 왕복 시간으로 둥지까지 거리 범위 추정 — 거리 = (왕복 시간 − 둥지 체류 45 s) ÷ 2 × 비행 속도 1.8~5.4 m/s, 둥지 195~1,331 m는 왕복 약 2~25분 [12]'),
  li('계산 예: 왕복 10분 (600 s) → (600 − 45) ÷ 2 = 277.5 s 편도 비행 → 277.5 s × 1.8~5.4 m/s = 약 500~1,500 m 떨어진 곳에 둥지'),
  li('시장성·사업화: 지자체·방제 기관용 B2G 둥지 조사 장비, 양봉농가는 방제 모드로 사용'),
  li('경제성: 새 트랩이 아닌 시판 트랩 장착 모듈 → 기존 방제 장비 재활용'),
  li('사회적 효과: 둥지를 빨리 찾아 제거 → 양봉 피해 감소에 기여'),
  li('개선방향: 실물 조립 후 표본 말벌로 판별·고정·표시 동작 시험 (확정)'),
  li('개선방향: 여러 색 마커로 색 교체까지 자동화 → 완전 자동화'),
  li('개선방향: Camera Module 3 영상으로 YOLO 재시험, 다른 곤충·여왕벌 학습 데이터 추가'),
  li('개선방향: 야외 귀소 시험은 생태계교란 생물 방생 허가가 필요 → 후속 연구로 제안 [15]'),
  li('개선방향: 실외 방수, 배터리 운용 (LiFePO4 12.8 V 20 Ah 상자 설계), 표본 시험 결과로 특허 출원 검토'),
]));

main.push(bar('7. 팀원간 역할'));
main.push(body([
  P([r('팀원간 역할 분담', { bold: true, size: 18 })], { align: AlignmentType.CENTER }),
  table([1300, 2953, 850, 1300, 2953, 850], [
    ['이름', '역할', '참여도(%)', '이름', '역할', '참여도(%)'],
    ['이서현', '팀장 — 기구 설계·CAD, 역학 계산, 회로·펌웨어, 제어 시험, 문서·발표', { t: '50', align: AlignmentType.CENTER }, '이승준', '팀원 — YOLO 파인 튜닝·비전 시험, 부품 구매·가공 발주, XY 구동부 대체 검토', { t: '50', align: AlignmentType.CENTER }],
  ], { header: true }),
  P([r('참여도는 백분율로 기재 (팀원 합계 100 %)', { size: 16, color: '444444' })], { before: 60 }),
]));

const refs = [
  '환경부(2024.04), "4월~10월 불청객 등검은말벌 이렇게 대처하세요!", 대한민국 정책브리핑',
  '홍동의·정철의(2024), "꿀벌 해충 등검은말벌 방제를 위한 화학 살충제 이용 가능성 평가", 「한국응용곤충학회지, Vol. 63 No. 1」, pp. 13-23',
  'Choi M.B., Hong E.J., Kwon O.(2021), "Defensive behavior of the invasive alien hornet, Vespa velutina, against color, hair and auditory stimuli of potential aggressors", 「PeerJ, Vol. 9」, e11249',
  '트위그뉴스(2018.12), "환경부, 외래종 등검은말벌 피해액 연간 1750억원"',
  'Wakefield M., Jones E.(2018.06), "Asian Hornet Analysis", 「BeeFarmer」',
  'Rome Q. 외(2015), "Caste differentiation and seasonal changes in Vespa velutina colonies in its introduced range", 「Journal of Applied Entomology, Vol. 139 No. 10」, pp. 771-782',
  'Davies P., O\'Sullivan H.(2025.09), "Tracking technology taking on the yellow-legged hornet", APHA Science Blog',
  'Lioy S. 외(2020), "Effectiveness and Selectiveness of Traps and Baits for Catching the Invasive Hornet Vespa velutina", 「Insects, Vol. 11 No. 10」, 706',
  'Kennedy P.J. 외(2018), "Searching for nests of the invasive Asian hornet (Vespa velutina) using radio-telemetry", 「Communications Biology, Vol. 1」, 88',
  'Vespawatch, "Locate nests"',
  'Tompkins B., "Tracking Asian hornets – how it\'s done", 「Bee Craft」',
  'Rojas-Nossa S.V. 외(2022), "Method for Nest Detection of the Yellow-Legged Hornet in High Density Areas", 「Frontiers in Insect Science, Vol. 2」',
  'Hivora, "Hivora Sense"',
  'O\'Shea-Wheller T.A. 외(2024), "VespAI: a deep learning-based system for the detection of invasive hornets", 「Communications Biology, Vol. 7」',
  '법제처(2018.12), "생태계교란 생물에 대하여 금지되는 행위의 범위" 법령해석 (안건 18-0488)',
  '생물다양성 보전 및 이용에 관한 법률 제24조',
  'Martin A.P. 외(2006), "A modular system for trapping and mass-marking bumblebees", 「Apidologie, Vol. 37」, pp. 341-350',
  'Hagler J. 외(2011), "A method for distinctly marking honey bees originating from multiple apiary locations", 「Journal of Insect Science, Vol. 11」, 143',
  'Mikery-Pacheco O. 외(2013), "A method for mass marking honeybees", 「Acta Zoológica Mexicana, Vol. 29 No. 1」, pp. 248-251',
  'Lioy S. 외(2021), "Tracking the invasive hornet Vespa velutina in complex environments by means of a harmonic radar", 「Scientific Reports, Vol. 11」',
  'Wang C. 외(2024), "A Review of Five Existing Hornet-Tracking Methods", 「Insects, Vol. 15」, 601',
  'Herrera C. 외(2022), "Automated detection of the yellow-legged hornet (Vespa velutina) using an optical sensor with machine learning", Wiley',
  'Struye M.H. 외(1994), "Microprocessor-controlled monitoring of honeybee flight activity at the hive entrance", 「Apidologie, Vol. 25」, pp. 384-395',
  'Quiles-Latorre F.J. 외(2024), "FPGA-Based Bee Counter System", 「IEEE Access, Vol. 12」, pp. 30362-30381',
  'Yoon C. 외, "A Computational System to Support Fully Automated Mark-Recapture Studies of Ants", CSCI-ISCI',
  'Plaza G.S., Meyers L. 외, "Identification of honeybees with paint codes using Convolutional Neural Networks", CSCI-ISCI',
  '세계일보(2023.11), "시판품 대비 최대 20배 효과" (충남도 농업기술원 등검은말벌 유인 조성물 특허출원)',
  'Mani S.R. 외(2018), "Design and Implementation of low-cost 2D plotter Computer Numeric Control (CNC) Machine", 「IJERT, Vol. 7 No. 5」',
  '"Cost-Effective Robotic Handwriting System with AI Integration"(2025), arXiv 2501.06783',
  'Irish Beekeepers\' Association, "Clipping and Marking a Queen"',
  'Poidatz J., Monceau K., Bonnard O., Thiéry D.(2018), "Activity rhythm and action range of workers of the invasive hornet predator of honeybees Vespa velutina, measured by radio frequency identification tags", 「Ecology and Evolution, Vol. 8 No. 15」, pp. 7588-7598',
  'Riley W.F. 외, 「Engineering Mechanics: Statics」 / Meriam J.L. 외, 「Engineering Mechanics: Dynamics」 / Gere J.M., 「Mechanics of Materials」',
];
main.push(bar('8. 참고문헌'));
main.push(body(refs.map((t, i) => P([r(`${i + 1}. ${t}`, { size: 16 })], { indent: { left: 360, hanging: 360 }, before: 10, after: 10, line: 250 }))));

main.push(bar('9. 기타 참고할 내용'));
main.push(body([
  li('외부 경진대회: 2026학년도 충남앵커공유대학 캡스톤 경진대회 (그린바이오 분야) 참가 신청 — 포스터 발표'),
  li('설계 기록 공개: GitHub 저장소 britams/-capstone-project-repo (CAD 생성 스크립트, 역학 계산, 회로·펌웨어, 시험 코드, AI 사용 기록)'),
  li('AI 도구 사용: 설계 문서 정리·검사 스크립트 작성에 생성형 AI (Claude) 사용, 값은 팀이 설계 문서·시험 기록으로 확인'),
  li('그림 2의 VespAI 화면은 공개 예시 영상 (O\'Shea-Wheller 2024, CC BY-NC-SA)을 우리 PC에서 실행한 결과'),
]));

const big = new Table({ width: { size: W, type: WidthType.DXA }, columnWidths: [W], rows: main });

const doc = new Document({
  styles: { default: { document: { run: { font: FONT, size: 19 } } } },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 850, bottom: 850, left: 850, right: 850 } } },
    children: [
      P([r('창의융합 경진대회 과제보고서', { bold: true, size: 36 })], { align: AlignmentType.CENTER, after: 160 }),
      info, P('', { before: 0, after: 0 }), big,
      P([r('위와 같이 과제보고서를 제출합니다.', { size: 24 })], { align: AlignmentType.CENTER, before: 500 }),
      P([r('2026년   11월      일', { size: 24 })], { align: AlignmentType.CENTER, before: 300 }),
      P([r('대표학생   이 서 현   (인)', { size: 24 })], { align: AlignmentType.CENTER, before: 300 }),
      P([r('천안공과대학 학장  귀하', { bold: true, size: 32 })], { align: AlignmentType.CENTER, before: 600 }),
    ],
  }],
});
Packer.toBuffer(doc).then(b => { fs.writeFileSync(process.argv[2] || 'report.docx', b); console.log('ok'); });
