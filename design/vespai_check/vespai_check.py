# -*- coding: utf-8 -*-
"""VespAI 점검 — 우리 장치 조건에서 검출이 얼마나 되는지 (서현, CAP-AI-21, 2026-11-02)

우리 장치는 VespAI 학습 장면과 세 가지가 다르다.
  ① 카메라가 격자판(구멍 Ø3, 피치 4.4 → 열린 면적 약 36 %) 너머로 말벌을 본다
  ② 마킹실(40 × 40 mm)만 잘라 넣으면 말벌이 화면의 절반 이상을 채운다
  ③ 입력 크기 (YOLOv5 AutoShape 기본 640)
이 스크립트는 같은 화면을 조건을 바꿔 넣고 검출 여부를 비교한다. 모델 불러오기·색 변환은 승준 vespai_live_webcam.py와 같다.

웹캠:  python vespai_check.py --yolo <yolov5 폴더> --weights <.pt>            (키: g 격자, k 마킹실만, i 입력 640/1280,
                                                                             [ ] 화면 폭 mm, +/- 신뢰도, s 저장, q 끝)
파일:  python vespai_check.py --yolo ... --weights ... <영상.mp4 또는 사진 폴더>  (조건 5개를 자동으로 돌려 표로)
시험:  python vespai_check.py --fake <영상 또는 폴더>                          (가짜 모델 — 코드 흐름만 확인)
"""
import argparse
import csv
import glob
import os
import sys
import time

import cv2
import numpy as np

NAMES = {0: 'crabro', 1: 'velutina'}          # VespAI 가중치 클래스 순서 (승준 J1 확인)
GRID = dict(pitch=4.4, hole=3.0, chamber=40.0)  # mm — D6 설계변수표 g_p, g_h, 마킹실 안쪽
PLATE = (205, 205, 205)                        # 격자판 색 (BGR, 밝은 회색 PLA 가정)
CONDS = [("전체 640", False, False, 640), ("전체+격자 640", True, False, 640), ("마킹실만 640", False, True, 640),
         ("마킹실만+격자 640", True, True, 640), ("전체 1280", False, False, 1280)]
_mask_cache = {}


def grid_mask(h, w, px_per_mm):
    key = (h, w, round(px_per_mm, 3))
    if key not in _mask_cache:
        m = np.zeros((h, w), np.uint8)
        p, r = GRID["pitch"] * px_per_mm, max(1, int(round(GRID["hole"] / 2 * px_per_mm)))
        cx, cy = w / 2.0, h / 2.0
        nx, ny = int(w / (2 * p)) + 2, int(h / (2 * p)) + 2
        for i in range(-nx, nx + 1):
            for j in range(-ny, ny + 1):
                cv2.circle(m, (int(round(cx + i * p)), int(round(cy + j * p))), r, 255, -1)
        _mask_cache.clear()
        _mask_cache[key] = m
    return _mask_cache[key]


def prepare(frame, grid, crop, frame_mm):
    """frame(BGR) → 모델에 넣을 그림(BGR). frame_mm = 화면 가로가 실제로 몇 mm인지"""
    h, w = frame.shape[:2]
    ppm = w / frame_mm
    img = frame
    if grid:
        m = grid_mask(h, w, ppm)
        img = np.empty_like(frame)
        img[:] = PLATE
        img[m > 0] = frame[m > 0]
    if crop:
        s = int(round(GRID["chamber"] * ppm))
        s = max(16, min(s, h, w))
        x0, y0 = (w - s) // 2, (h - s) // 2
        img = img[y0:y0 + s, x0:x0 + s]
    return img


class FakeModel:
    """가짜 모델: 가운데에 velutina 하나를 conf 0.6~0.9로 냄 (코드 흐름 확인용)"""
    conf = 0.25
    names = NAMES

    def __call__(self, im, size=640):
        h, w = im.shape[:2]
        c = 0.6 + 0.3 * np.random.rand()

        class R:
            pred = [np.array([[w * 0.4, h * 0.4, w * 0.6, h * 0.6, c, 1.0]])]
        return R()


def load_model(args):
    if args.fake:
        return FakeModel()
    import torch
    sys.path.insert(0, args.yolo)
    print('모델 불러오는 중 (약 20초)…')
    model = torch.hub.load(args.yolo, 'custom', path=args.weights, source='local', _verbose=False)
    model.conf = 0.25
    print('클래스:', model.names)
    return model


def detect(model, img_bgr, size, conf_thr):
    r = model(cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB), size=size)
    out = []
    for x1, y1, x2, y2, c, k in np.asarray(r.pred[0].tolist() if hasattr(r.pred[0], 'tolist') else r.pred[0]).reshape(-1, 6):
        if c >= conf_thr and int(k) in NAMES:
            out.append((x1, y1, x2, y2, float(c), int(k)))
    return out


def frames_from(path, every):
    if os.path.isdir(path):
        fs = sorted(sum([glob.glob(os.path.join(path, e)) for e in ('*.jpg', '*.jpeg', '*.png', '*.JPG', '*.PNG')], []))
        for f in fs:
            im = cv2.imdecode(np.fromfile(f, np.uint8), cv2.IMREAD_COLOR)
            if im is not None:
                yield os.path.basename(f), im
        return
    cap = cv2.VideoCapture(path)
    i = 0
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        if i % every == 0:
            yield 'frame_%05d' % i, fr
        i += 1


def run_file(model, args):
    os.makedirs(args.out, exist_ok=True)
    rows, stat = [], {c[0]: [0, 0, 0.0] for c in CONDS}       # 장수, velutina 있는 장, 최고 conf 합
    t0 = time.time()
    for name, fr in frames_from(args.input, args.every):
        for cname, g, k, size in CONDS:
            dets = detect(model, prepare(fr, g, k, args.frame_mm), size, args.conf)
            v = [d for d in dets if d[5] == 1]
            c = [d for d in dets if d[5] == 0]
            best = max([d[4] for d in v], default=0.0)
            st = stat[cname]
            st[0] += 1
            st[1] += 1 if v else 0
            st[2] += best
            rows.append([name, cname, len(v), len(c), '%.3f' % best])
    with open(os.path.join(args.out, 'check_frames.csv'), 'w', newline='', encoding='utf-8-sig') as f:
        w = csv.writer(f)
        w.writerow(['frame', 'condition', 'n_velutina', 'n_crabro', 'best_velutina_conf'])
        w.writerows(rows)
    lines = ['VespAI 점검 결과 — 입력 %s, 화면 폭 %.0f mm 가정, 신뢰도 %.2f, %.0f s' % (args.input, args.frame_mm, args.conf, time.time() - t0),
             '조건\t장수\t등검은말벌 검출 장\t비율\t평균 최고 신뢰도']
    for cname, *_ in CONDS:
        n, k, s = stat[cname]
        lines.append('%s\t%d\t%d\t%.0f %%\t%.2f' % (cname, n, k, 100.0 * k / max(n, 1), s / max(n, 1)))
    txt = '\n'.join(lines)
    open(os.path.join(args.out, 'check_summary.txt'), 'w', encoding='utf-8').write(txt + '\n')
    print(txt)


def run_live(model, args):
    src = int(args.source) if str(args.source).isdigit() else args.source
    cap = cv2.VideoCapture(src, cv2.CAP_DSHOW) if (os.name == 'nt' and isinstance(src, int)) else cv2.VideoCapture(src)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    if not cap.isOpened():
        print('카메라를 열 수 없음 — Windows 설정 → 개인 정보 → 카메라 → 데스크톱 앱 허용, 다른 프로그램이 쓰는지 확인')
        sys.exit(2)
    os.makedirs(args.out, exist_ok=True)
    g, k, size, conf, fmm = False, False, 640, args.conf, args.frame_mm
    log = open(os.path.join(args.out, 'check_live.csv'), 'w', newline='', encoding='utf-8-sig')
    lw = csv.writer(log)
    lw.writerow(['time_s', 'condition', 'n_velutina', 'n_crabro', 'best_velutina_conf'])
    per = {}
    t_start, t_last = time.time(), 0.0
    t_snap, n_snap = -9.0, 0
    print('키: g 격자  k 마킹실만  i 입력 640/1280  [ ] 화면 폭 mm  +/- 신뢰도  s 저장  q 끝')
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        img = prepare(fr, g, k, fmm)
        dets = detect(model, img, size, conf)
        cname = ('마킹실만' if k else '전체') + ('+격자' if g else '') + ' %d' % size
        show = img.copy()
        for x1, y1, x2, y2, c, kk in dets:
            col = (0, 0, 255) if kk == 1 else (0, 165, 255)
            cv2.rectangle(show, (int(x1), int(y1)), (int(x2), int(y2)), col, 2)
            cv2.putText(show, '%s %.2f' % (NAMES[kk], c), (int(x1), max(12, int(y1) - 4)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, col, 1)
        if show.shape[1] < 640:
            sc = 640.0 / show.shape[1]
            show = cv2.resize(show, None, fx=sc, fy=sc, interpolation=cv2.INTER_NEAREST)
        tag = '%s  frame %.0f mm  conf %.2f  | g grid  k chamber  i size  [ ] mm  +/- conf  s save  q quit' % (
            cname.replace('마킹실만', 'CHAMBER').replace('전체', 'FULL').replace('+격자', '+GRID'), fmm, conf)
        cv2.putText(show, tag, (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 3)
        cv2.putText(show, tag, (8, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.imshow('VespAI check (Seohyun)', show)
        now = time.time() - t_start
        if dets and now - t_snap >= 1.0 and n_snap < 600:      # 박스가 뜬 장면을 1초에 1장 자동 저장 → 진짜 말벌인지 나중에 판정
            tagc = ('K' if k else 'F') + ('G' if g else '')       # F 전체 / K 마킹실만, G 격자
            cv2.imwrite(os.path.join(args.out, 'auto_%06.1f_%s.jpg' % (now, tagc)), show)
            t_snap, n_snap = now, n_snap + 1
        if now - t_last >= 1.0:
            t_last = now
            v = [d for d in dets if d[5] == 1]
            best = max([d[4] for d in v], default=0.0)
            lw.writerow(['%.1f' % now, cname, len(v), len(dets) - len(v), '%.3f' % best])
            p = per.setdefault(cname, [0, 0])
            p[0] += 1
            p[1] += 1 if v else 0
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        if key == ord('g'):
            g = not g
        if key == ord('k'):
            k = not k
        if key == ord('i'):
            size = 1280 if size == 640 else 640
        if key == ord(']'):
            fmm += 20
        if key == ord('[') and fmm > 60:
            fmm -= 20
        if key in (ord('+'), ord('=')):
            conf = min(0.95, conf + 0.05)
        if key == ord('-'):
            conf = max(0.05, conf - 0.05)
        if key == ord('s'):
            cv2.imwrite(os.path.join(args.out, 'snap_%d.jpg' % int(now)), show)
    log.close()
    cap.release()
    cv2.destroyAllWindows()
    lines = ['VespAI 점검 (웹캠) — 조건별 1초 기록 중 등검은말벌이 잡힌 비율']
    for cname, (n, kk) in per.items():
        lines.append('%s\t%d s\t%d s\t%.0f %%' % (cname, n, kk, 100.0 * kk / max(n, 1)))
    txt = '\n'.join(lines)
    open(os.path.join(args.out, 'check_summary.txt'), 'w', encoding='utf-8').write(txt + '\n')
    print(txt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('input', nargs='?', help='영상 파일 또는 사진 폴더 (없으면 웹캠)')
    ap.add_argument('--yolo')
    ap.add_argument('--weights')
    ap.add_argument('--source', default='0')
    ap.add_argument('--conf', type=float, default=0.5)
    ap.add_argument('--frame-mm', type=float, default=280.0, help='화면 가로의 실제 길이 mm (웹캠 약 20 cm 거리면 약 280 [추측])')
    ap.add_argument('--every', type=int, default=5, help='영상에서 몇 프레임마다 볼지')
    ap.add_argument('--out', default='out_check')
    ap.add_argument('--fake', action='store_true')
    args = ap.parse_args()
    model = load_model(args)
    if args.input:
        run_file(model, args)
    else:
        run_live(model, args)


if __name__ == '__main__':
    main()
