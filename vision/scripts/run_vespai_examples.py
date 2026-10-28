"""VespAI 예시 이미지 검출 (CAP-AI-SJ-02, 비교 기능 CAP-AI-SJ-03)

monitor/monitor_run.py와 같은 방식(torch.hub local custom, conf 0.8)으로 가중치를 불러
저장소의 예시 프레임(images/example-detections)에 검출을 돌리고,
저장소에 들어 있는 원 실행 결과(labels/)와 종별 개수·신뢰도를 비교한다.

사용:
    python run_vespai_examples.py <yolov5 폴더> <가중치 .pt> <images/example-detections 폴더> <결과 폴더>
결과:
    <결과 폴더>/result.tsv      프레임별 비교표 (UTF-8)
    <결과 폴더>/summary.txt     환경·일치율·평균 추론 시간
    <결과 폴더>/*.jpeg          박스를 그린 결과 그림

주의: .pt는 피클 형식이라 여는 순간 코드가 실행될 수 있다 — VespAI 원본 저장소 가중치에만 쓸 것.
"""
import glob
import os
import platform
import re
import sys
import time

import cv2
import torch

CONF = 0.8  # monitor_run.py 기본값
CLASS_VELUTINA, CLASS_CRABRO = 1, 0  # monitor_run.py 기준


def frame_no(path):
    return int(os.path.basename(path).split('-')[-1].split('.')[0])


def read_reference(label_path):
    """원 결과 라벨 → (velutina 수, crabro 수, 신뢰도 목록).
    monitor_run.py가 같은 파일에 표를 줄바꿈 없이 덧붙여 쓴 경우가 있어 마지막 표만 읽는다."""
    if not os.path.exists(label_path):
        return None
    text = open(label_path, encoding='utf-8').read()
    blocks = [b for b in re.split(r'\s*xmin\s+ymin\s+xmax\s+ymax\s+confidence\s+class\s+name', text) if b.strip()]
    if not blocks:
        return 0, 0, []
    rows = re.findall(r'([\d.]+)\s+(\d)\s+Vespa (velutina|crabro)', blocks[-1])
    n_v = sum(1 for _, _, s in rows if s == 'velutina')
    n_c = sum(1 for _, _, s in rows if s == 'crabro')
    return n_v, n_c, [float(c) for c, _, _ in rows]


def main():
    yolo_dir, weights, img_root, out_dir = sys.argv[1:5]
    os.makedirs(out_dir, exist_ok=True)
    sys.path.insert(0, yolo_dir)

    t0 = time.time()
    model = torch.hub.load(yolo_dir, 'custom', path=weights, source='local', _verbose=False)
    model.conf = CONF
    load_s = time.time() - t0

    header = ['정답종', '프레임', '검출_velutina', '검출_crabro', '원결과_velutina', '원결과_crabro',
              '개수일치', '검출_신뢰도', '원결과_신뢰도', '추론초']
    lines, times, match, total = ['\t'.join(header)], [], 0, 0
    print('\t'.join(header))
    for species in ['velutina', 'crabro']:
        frames = sorted(glob.glob(os.path.join(img_root, species, 'frames', '*.jpeg')), key=frame_no)
        for i, f in enumerate(frames):
            img = cv2.cvtColor(cv2.imread(f), cv2.COLOR_BGR2RGB)
            t = time.time()
            r = model(img)
            dt = time.time() - t
            if not (species == 'velutina' and i == 0):  # 첫 장은 준비 시간이 섞여 평균에서 뺌
                times.append(dt)
            p = r.pred[0]
            n_v = int((p[:, -1] == CLASS_VELUTINA).sum())
            n_c = int((p[:, -1] == CLASS_CRABRO).sum())
            confs = ','.join(f"{c:.3f}" for c in sorted(p[:, 4].tolist(), reverse=True))
            label = os.path.join(img_root, species, 'labels', os.path.basename(f).replace('.jpeg', '.txt'))
            ref = read_reference(label)
            if ref is None:
                rv = rc = '-'
                rconf, same = '', '-'
            else:
                rv, rc, rlist = ref
                rconf = ','.join(f"{c:.3f}" for c in sorted(rlist, reverse=True))
                same = 'O' if (n_v, n_c) == (rv, rc) else 'X'
                total += 1
                match += same == 'O'
            row = [species, os.path.basename(f), n_v, n_c, rv, rc, same, confs, rconf, f"{dt:.2f}"]
            lines.append('\t'.join(map(str, row)))
            print(lines[-1])
            r.render()
            cv2.imwrite(os.path.join(out_dir, f"{species}-{os.path.basename(f)}"),
                        cv2.cvtColor(r.ims[0], cv2.COLOR_RGB2BGR))

    with open(os.path.join(out_dir, 'result.tsv'), 'w', encoding='utf-8') as fp:
        fp.write('\n'.join(lines) + '\n')
    avg = sum(times) / len(times) if times else float('nan')
    summary = [
        f"Python {platform.python_version()} / torch {torch.__version__} / OpenCV {cv2.__version__}",
        f"OS {platform.platform()} / CPU {platform.processor()}",
        f"가중치 {os.path.basename(weights)} / 클래스 {model.names} / conf {CONF}",
        f"모델 로드 {load_s:.1f} s",
        f"종별 개수 일치 {match}/{total} 프레임",
        f"평균 추론 시간 {avg:.3f} s/장 (첫 장 제외, CPU, 입력 원본 크기 → 내부 640)",
    ]
    with open(os.path.join(out_dir, 'summary.txt'), 'w', encoding='utf-8') as fp:
        fp.write('\n'.join(summary) + '\n')
    print('\n'.join(summary))


if __name__ == '__main__':
    main()
