"""VespAI 실시간 웹캠 검출 (CAP-AI-SJ-09)

PC에 연결된 카메라(또는 영상 파일)로 VespAI 가중치를 실시간 실행하고, 박스를 화면에 그린다.
monitor_run.py와 달리 화면 표시·키 조작·기록이 있고, 메일 기능은 없다.

사용:
    python vespai_live_webcam.py --yolo <yolov5 폴더> --weights <.pt> [--source 0] [--conf 0.5] [--out out_live]
    --source  카메라 번호(0, 1, …) 또는 영상 파일 경로. 기본: 0번부터 열리는 카메라를 찾음
    --conf    표시 기준 신뢰도 (기본 0.5 — 화면·종이에 띄운 사진은 실물보다 신뢰도가 낮게 나와서 VespAI 기본 0.8보다 낮춤)
    --no-window  화면 없이 실행 (기록만)

키 (영상 창을 클릭한 상태에서):
    q / Esc  끝내기        s  지금 화면 저장        + / -  기준 신뢰도 0.05씩 올리기/내리기
    c  다음 카메라로 바꾸기

결과 (<out>):
    live_summary.txt  카메라·해상도·프레임 수·평균 추론 시간·검출 수
    detections.csv    검출 기록 (1초에 최대 1줄)
    snap_*.jpg        s 키로 저장한 화면

주의: .pt는 피클 형식 — VespAI 원본 저장소 가중치(J1 스크립트가 SHA-256 검사한 것)에만 쓸 것.
"""
import argparse
import csv
import datetime
import os
import platform
import sys
import time

import cv2
import torch

NAMES = {0: 'V. crabro (European hornet)', 1: 'V. velutina (Asian hornet)'}
COLORS = {0: (0, 165, 255), 1: (0, 0, 255)}  # BGR: 주황 / 빨강


def open_camera(source):
    """카메라 번호 또는 파일 경로로 VideoCapture를 연다. (cap, 설명, 카메라 번호|None) 반환, 실패 시 (None, 이유, None)."""
    if isinstance(source, str) and not source.isdigit():
        cap = cv2.VideoCapture(source)
        return (cap, f'file {source}', None) if cap.isOpened() else (None, f'cannot open file {source}', None)
    indices = [int(source)] if source is not None else [0, 1, 2, 3]
    backends = [cv2.CAP_DSHOW, cv2.CAP_MSMF, cv2.CAP_ANY] if os.name == 'nt' else [cv2.CAP_ANY]
    for idx in indices:
        for be in backends:
            cap = cv2.VideoCapture(idx, be)
            if cap.isOpened():
                cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
                cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
                ok, _ = cap.read()
                if ok:
                    return cap, f'camera {idx} (backend {be})', idx
            cap.release()
    return None, 'no camera opened (indices %s)' % indices, None


def draw(frame, preds, conf_thr, fps, infer_ms):
    """박스·라벨·상태 줄을 그린다. 그린 박스 수를 종별로 반환."""
    counts = {0: 0, 1: 0}
    for x1, y1, x2, y2, conf, cls in preds:
        cls = int(cls)
        if conf < conf_thr or cls not in counts:
            continue
        counts[cls] += 1
        c = COLORS[cls]
        p1, p2 = (int(x1), int(y1)), (int(x2), int(y2))
        cv2.rectangle(frame, p1, p2, c, 2)
        label = f'{NAMES[cls]} {conf:.2f}'
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2)
        cv2.rectangle(frame, (p1[0], p1[1] - th - 8), (p1[0] + tw + 4, p1[1]), c, -1)
        cv2.putText(frame, label, (p1[0] + 2, p1[1] - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    status = (f'velutina {counts[1]}  crabro {counts[0]}  |  conf>={conf_thr:.2f}  |  '
              f'{fps:.1f} fps  infer {infer_ms:.0f} ms  |  q:quit s:save +/-:conf c:camera')
    cv2.rectangle(frame, (0, 0), (frame.shape[1], 28), (0, 0, 0), -1)
    cv2.putText(frame, status, (6, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    return counts


def run(model, cap, cam_desc, args, cam_idx=None):
    os.makedirs(args.out, exist_ok=True)
    log_path = os.path.join(args.out, 'detections.csv')
    new_log = not os.path.exists(log_path)
    log_f = open(log_path, 'a', newline='', encoding='utf-8')
    log = csv.writer(log_f)
    if new_log:
        log.writerow(['time', 'camera', 'species', 'conf', 'x1', 'y1', 'x2', 'y2'])

    conf_thr = args.conf
    model.conf = 0.25  # 모델은 낮게 뽑고, 표시·기록은 conf_thr로 거름 (+/- 키로 바로 바뀌게)
    n_frames, infer_total, det_total = 0, 0.0, {0: 0, 1: 0}
    best = {0: 0.0, 1: 0.0}
    last_log, t_prev, fps = 0.0, time.time(), 0.0
    size = None
    t_start = time.time()

    while True:
        ok, frame = cap.read()
        if not ok:
            print('프레임을 못 받음 — 끝냄 (영상 끝 또는 카메라 끊김)')
            break
        size = (frame.shape[1], frame.shape[0])
        t0 = time.time()
        r = model(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        infer = time.time() - t0
        preds = r.pred[0].tolist()
        n_frames += 1
        if n_frames > 1:  # 첫 장은 준비 시간 포함
            infer_total += infer
        now = time.time()
        fps = 0.9 * fps + 0.1 * (1.0 / max(now - t_prev, 1e-6)) if n_frames > 1 else 0.0
        t_prev = now

        counts = draw(frame, preds, conf_thr, fps, infer * 1000)
        for p in preds:
            if p[4] >= conf_thr and int(p[5]) in best:
                best[int(p[5])] = max(best[int(p[5])], p[4])
        if sum(counts.values()) and now - last_log >= 1.0:
            ts = datetime.datetime.now().isoformat(timespec='seconds')
            for x1, y1, x2, y2, conf, cls in preds:
                if conf >= conf_thr and int(cls) in det_total:
                    det_total[int(cls)] += 1
                    log.writerow([ts, cam_desc, NAMES[int(cls)], f'{conf:.3f}', int(x1), int(y1), int(x2), int(y2)])
            log_f.flush()
            last_log = now

        if args.no_window:
            if args.max_frames and n_frames >= args.max_frames:
                break
            continue
        cv2.imshow('VespAI live (q to quit)', frame)
        key = cv2.waitKey(1) & 0xFF
        if key in (ord('q'), 27):
            break
        if key == ord('s'):
            p = os.path.join(args.out, 'snap_' + datetime.datetime.now().strftime('%Y%m%d_%H%M%S') + '.jpg')
            cv2.imwrite(p, frame)
            print('저장:', p)
        if key in (ord('+'), ord('=')):
            conf_thr = min(0.95, conf_thr + 0.05)
        if key in (ord('-'), ord('_')):
            conf_thr = max(0.05, conf_thr - 0.05)
        if key == ord('c') and cam_idx is not None:
            cap.release()
            for step in range(1, 5):
                nxt = (cam_idx + step) % 4
                new_cap, desc, _ = open_camera(nxt)
                if new_cap is not None:
                    cap, cam_desc, cam_idx = new_cap, desc, nxt
                    print('카메라 바꿈:', desc)
                    break
            else:
                print('다른 카메라 없음')
                cap, cam_desc, _ = open_camera(cam_idx)

    cap.release()
    log_f.close()
    if not args.no_window:
        cv2.destroyAllWindows()
    avg = infer_total / (n_frames - 1) if n_frames > 1 else float('nan')
    summary = [
        f"실행 {datetime.datetime.now().isoformat(timespec='seconds')} / {time.time() - t_start:.0f} s",
        f"Python {platform.python_version()} / torch {torch.__version__} / OpenCV {cv2.__version__}",
        f"입력 {cam_desc} / 해상도 {size}",
        f"프레임 {n_frames} / 평균 추론 {avg * 1000:.0f} ms / 마지막 fps {fps:.1f}",
        f"검출 기록 (1초 간격) velutina {det_total[1]} / crabro {det_total[0]} / 최종 기준 conf {conf_thr:.2f}",
        f"최고 신뢰도 velutina {best[1]:.3f} / crabro {best[0]:.3f}",
    ]
    with open(os.path.join(args.out, 'live_summary.txt'), 'a', encoding='utf-8') as fp:
        fp.write('\n'.join(summary) + '\n\n')
    print('\n'.join(summary))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--yolo', required=True)
    ap.add_argument('--weights', required=True)
    ap.add_argument('--source', default=None, help='카메라 번호 또는 영상 파일 (기본: 자동 찾기)')
    ap.add_argument('--conf', type=float, default=0.5)
    ap.add_argument('--out', default='out_live')
    ap.add_argument('--no-window', action='store_true')
    ap.add_argument('--max-frames', type=int, default=0, help='--no-window일 때 이 프레임 수 뒤 끝냄 (0 = 끝까지)')
    args = ap.parse_args()

    cap, desc, cam_idx = open_camera(args.source)
    if cap is None:
        print('카메라를 열 수 없음:', desc)
        print('확인: ① 카메라 연결 ② Windows 설정 → 개인 정보 및 보안 → 카메라 → "데스크톱 앱이 카메라에 액세스하도록 허용" 켜기 '
              '③ 다른 프로그램(Zoom, Teams, 카메라 앱)이 카메라를 쓰고 있지 않은지')
        sys.exit(2)
    print('입력:', desc)

    sys.path.insert(0, args.yolo)
    print('모델 불러오는 중 (약 20초)…')
    model = torch.hub.load(args.yolo, 'custom', path=args.weights, source='local', _verbose=False)
    print('클래스:', model.names)
    run(model, cap, desc, args, cam_idx=cam_idx)


if __name__ == '__main__':
    main()
