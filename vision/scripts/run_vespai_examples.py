"""VespAI 예시 이미지 검출 (CAP-AI-SJ-02)

monitor/monitor_run.py와 같은 방식(torch.hub local custom)으로 가중치를 불러
저장소의 예시 프레임(images/example-detections)에 검출을 돌리고, 종별 개수·신뢰도·추론 시간을 출력한다.

사용:
    python run_vespai_examples.py <yolov5 폴더> <가중치 .pt> <images/example-detections 폴더> <결과 폴더>
예:
    python run_vespai_examples.py vespai/models/yolov5 vespai/models/yolov5-params/yolov5s-all-data.pt \
        vespai/images/example-detections out

주의: .pt는 피클 형식이라 여는 순간 코드가 실행될 수 있다 — VespAI 원본 저장소 가중치에만 쓸 것.
torch 2.6 이상이면 실행 전에 환경변수 TORCH_FORCE_NO_WEIGHTS_ONLY_LOAD=1 이 필요할 수 있다 (미검증).
"""
import glob
import os
import sys
import time

import cv2
import torch

CONF = 0.8  # monitor_run.py 기본값
CLASS_VELUTINA, CLASS_CRABRO = 1, 0  # monitor_run.py 기준


def frame_no(path):
    return int(os.path.basename(path).split('-')[-1].split('.')[0])


def main():
    yolo_dir, weights, img_root, out_dir = sys.argv[1:5]
    os.makedirs(out_dir, exist_ok=True)
    sys.path.insert(0, yolo_dir)

    t0 = time.time()
    model = torch.hub.load(yolo_dir, 'custom', path=weights, source='local', _verbose=False)
    model.conf = CONF
    print(f"모델 로드 {time.time() - t0:.1f}s, 클래스 = {model.names}")

    print("정답종\t프레임\tvelutina\tcrabro\t원결과행수\t신뢰도\t초")
    for species in ['velutina', 'crabro']:
        for f in sorted(glob.glob(os.path.join(img_root, species, 'frames', '*.jpeg')), key=frame_no):
            img = cv2.cvtColor(cv2.imread(f), cv2.COLOR_BGR2RGB)
            t = time.time()
            r = model(img)
            dt = time.time() - t
            p = r.pred[0]
            n_v = int((p[:, -1] == CLASS_VELUTINA).sum())
            n_c = int((p[:, -1] == CLASS_CRABRO).sum())
            confs = ','.join(f"{c:.2f}" for c in p[:, 4].tolist())
            label = f.replace(os.sep + 'frames' + os.sep, os.sep + 'labels' + os.sep).replace('.jpeg', '.txt')
            ref = len(open(label, encoding='utf-8').read().strip().splitlines()) - 1 if os.path.exists(label) else -1
            print(f"{species}\t{os.path.basename(f)}\t{n_v}\t{n_c}\t{ref}\t{confs}\t{dt:.2f}")
            r.render()
            cv2.imwrite(os.path.join(out_dir, f"{species}-{os.path.basename(f)}"),
                        cv2.cvtColor(r.ims[0], cv2.COLOR_RGB2BGR))


if __name__ == '__main__':
    main()
