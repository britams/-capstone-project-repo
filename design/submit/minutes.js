const fs = require('fs');
const { Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell, WidthType, ShadingType, BorderStyle, AlignmentType, HeadingLevel, PageBreak } = require('docx');
const F = '맑은 고딕';
const bd = { style: BorderStyle.SINGLE, size: 4, color: '999999' };
const cell = (t, w, head = false) => new TableCell({ width: { size: w, type: WidthType.DXA }, borders: { top: bd, bottom: bd, left: bd, right: bd },
  shading: head ? { fill: 'E8F0FA', type: ShadingType.CLEAR, color: 'auto' } : undefined, margins: { top: 60, bottom: 60, left: 100, right: 100 },
  children: (Array.isArray(t) ? t : [t]).map(x => new Paragraph({ spacing: { after: 40 }, children: [new TextRun({ text: x, font: F, size: 20, bold: head })] })) });
const L = 1800, R = 7226;
function meeting(no, date, kind, src, agenda, decided, todo) {
  return [
    new Paragraph({ heading: HeadingLevel.HEADING_2, spacing: { before: 280, after: 120 }, children: [new TextRun({ text: `${no}. ${date} — ${kind}`, font: F, bold: true, size: 26, color: '1F2A44' })] }),
    new Table({ width: { size: L + R, type: WidthType.DXA }, columnWidths: [L, R], rows: [
      ['일시·장소', `${date} · (장소 확인)`], ['참석', '이서현, 이승준 (참석 확인)'], ['안건', agenda], ['결정', decided], ['할 일', todo], ['근거 기록', src],
    ].map(([a, b]) => new TableRow({ children: [cell(a, L, true), cell(b, R)] })) }),
  ];
}
const M = [
  ['2026. 9. 28.', '지도교수 피드백 (김성관 교수님)', '바탕화면 교수님 피드백\\2026-09-28 피드백정리.txt',
    ['계획서 내용 점검'], ['비전 카메라 반응 속도로 추적 가능 여부 확인', '일벌·여왕벌을 확실히 분류해 일벌만 이동 방향 유도', '개념설계도 작성, 말벌 활동 반경 조사', '통로 만드는 방법 구체화'], ['활동 반경·크기 조사 (10/11 정리)', '개념설계도 S1 작성']],
  ['2026. 10. 2.', '외부 자문 (최문보 교수님, 경북대) 회신', '바탕화면 교수님 피드백\\10월2일_회신메일.pdf',
    ['9/30 질문에 대한 교수님 의견 반영', '마킹 방식 재검토'], ['형광 가루 자가 표시 포기 (쉽게 지워지고 절차가 복잡함)', '여왕벌 표식 방식 (직접 칠하기)으로 전환', '목표를 포획 → 식별 → 표시 → 급이 → 방생 단계로 정리'], ['표시 방식 구체화 (피스톤 + 패드 검토)']],
  ['2026. 10. 8.', '외부 자문 2차 답변 반영', '인수인계 4장 \'방향 변천\'',
    ['비행 방향·거리 추정 가능성'], ['비행 방향·거리 추정 기능 삭제 (말벌 비행이 빨라 근거리 촬영으로 방향을 잡기 어려움)', '표시는 같은 개체의 재방문 확인용으로 사용'], ['요구 조건 재정리']],
  ['2026. 10. 11.', '팀 결정', '나중 보고서를 위한 정리\\2026-10-11_진행타임라인_결정기록.md',
    ['표시 재료와 개체 처리'], ['수성 아크릴 마커 사용', '여왕벌은 격리', '문헌 기반 설계 입력값 확정 (흉부 폭, 몸길이, 트랩 입구 8~9 mm)'], ['S0 문제설정·S1 개념설계 문서화', '10/12 진행상황 보고 준비']],
  ['2026. 10. 28.', '재설계·분업 회의', 'docs/2026-10-28_분업계획_서현_승준.md, design/2026-10-28_D1~D6',
    ['10/26 발표안 재검토', '구조 방향', '분업'], ['10/26 발표안 폐기, 설계를 처음부터 다시 함', '시판 트랩 「야생 말벌 포획기」에 얹는 레트로핏 모듈', '"대량 처리보다 한 마리를 정확히" 원칙, 바닥 승강형 마킹실 (안 1)', '분업: 서현 = 기구 설계·역학계산·문서, 승준 = VespAI·비전·전자·구매·정산', '공유: GitHub 레포 + Chrome'], ['D5 개념설계·D6 설계변수표·S4 역학계산 1차', 'VespAI 저장소 실행 (J1)', '표본 확보']],
  ['2026. 10. 30.', '회의 1 (계획된 회의 — 열렸는지 확인)', 'docs/2026-10-28_분업계획_서현_승준.md 4장',
    ['분업 확정, 레트로핏 vs 새 트랩, 10/11 결정 유지 여부'], ['(회의가 열렸다면 결정 내용 기록)'], ['—']],
  ['2026. 11. 2.', '역학계산 발표', 'docs/2026-11-02_발표_역학계산_슬라이드원고.md',
    ['역학계산 10문제 발표', '동역학 위험 검토'], ['스프링 204 제거, 펜 홀더 핀 PTFE 테이프', '펜 내리기 2단계 (마지막 2 mm ≤ 60 °/s)', '문은 빛 게이트 확인 뒤 닫기', 'VespAI 점검: 격자 가림 → 투명 격자 필수'], ['D6·인터페이스 정의서 값 반영', '판별 재학습 계획']],
  ['2026. 11. 15.', '판별 AI 재학습 결과 공유', 'vision/2026-11-15_VespAI_재학습_결과_승준.md',
    ['VespAI 재학습 v1~v3 결과'], ['격자를 얹어 학습한 v3 채택 (격자 + 말벌 917/917 장면, 격자만 헛것 2.1 %)', '판별 클래스를 velutina / other 둘로 검토'], ['트랩 카메라 (CM3)로 다시 시험', '헛것 장면을 빈 화면으로 넣어 재학습']],
  ['2026. 11. 17.', '구조·전원 결정', 'design/2026-11-17_전원_12V하나_센서쉴드_서현.md',
    ['빛 게이트, 전원, 브래킷'], ['빛 게이트 3쌍 (G2·G3b·G5)', '12 V 5 A 하나 → 퓨즈 → 비상 정지 → 강압 2개', 'ㄱ자 브래킷은 미스미 FALCS'], ['구매 (승준), 가공 업체 주문']],
  ['2026. 11. 20.', '대회 준비', 'ai-log/AI_명령사항_로그.md (11/20)',
    ['창의융합 (12/2), 충남앵커공유대학 (12/4) 제출물'], ['작품명 「등검은말벌 둥지 추적 마킹 트랩」 (초안)', 'VespAI는 선행 연구로, 결과는 우리 재학습으로 제시', '판매 대상은 공공기관 (B2G)'], ['포스터·판넬·최종보고서·발표 자료 작성', '11/24 앵커 신청, 11/26 판넬, 11/30 보고서·정산']],
];
const doc = new Document({ sections: [{ properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1300, bottom: 1300, left: 1440, right: 1440 } } }, children: [
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [new TextRun({ text: '회 의 록', font: F, size: 40, bold: true })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 }, children: [new TextRun({ text: '창의적종합설계 · 팀 초벌 — 등검은말벌 둥지 추적 마킹 트랩', font: F, size: 22 })] }),
  new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 300 }, children: [new TextRun({ text: '※ 작업 기록 (레포·메일·로그)에서 결정이 있었던 날을 모은 초안임. 장소·참석은 확인 후 채우고, 회의가 아닌 날은 지울 것.', font: F, size: 18, color: 'C0392B' })] }),
  ...M.flatMap((m, i) => meeting(i + 1, ...m)),
] }] });
Packer.toBuffer(doc).then(b => { fs.writeFileSync('말벌트랩_회의록_초안.docx', b); console.log('ok'); });
