"""dot_detect.py — 흉부 위 노랑 마커 점 찾기 (작업지시 J4, CAP-AI-SJ-20)

마커: 샤피 크리에이티브 노랑 (10/28 결정, 구매목록 A4). 카메라: 격자 위 200 mm, 약 15.6 화소/mm (인터페이스 정의서 2차, J3에서 실측).

등검은말벌은 다리·배 넷째 마디가 노랑·주황 → 색만 보면 헷갈림. 그래서 세 가지를 같이 본다:
  ① 색: HSV 노랑 범위   ② 모양: 지름이 점 크기(기본 0.6~3.0 mm, 격자선에 쪼개진 것은 이어 붙임)이고 둥근 것 (원형도)
  ③ 주변: 점 둘레 고리가 어두움 (흉부 위에 찍힌 점이면 둘레가 검은 흉부)
선택: --roi x y r (화소)로 흉부 둘레만 보게 하면 더 안전 (J8 흉부 좌표가 나오면 그 값을 씀).

사용:
    python dot_detect.py 사진.jpg [--px-per-mm 15.6] [--roi 640 480 120] [--show out.jpg]
    python dot_detect.py --eval 폴더 [--px-per-mm 15.6]
        폴더 안 파일 이름에 'nodot'이 있으면 점 없는 사진, 'dot'이 있으면 점 있는 사진으로 보고 검출률(R5 목표 90%)·오검출을 셈
"""
import argparse
import glob
import math
import os
import sys

import cv2
import numpy as np

DEF = dict(
    h_lo=18, h_hi=40,        # OpenCV H 0~179: 노랑 약 20~35
    s_min=110, v_min=130,
    d_min_mm=0.6, d_max_mm=3.0,
    close_mm=0.4,            # 격자선(약 0.3 mm)이 점을 쪼개면 이어 붙임
    circ_min=0.65,           # 4πA/P²
    ring_v_max=90,           # 점 둘레 고리 밝기(V) 중앙값 상한 — 흉부는 어두움
    ring_dark_frac=0.6,      # 고리 화소 중 어두운 비율 하한
)


def find_dots(img_bgr, px_per_mm=15.6, roi=None, p=DEF):
    hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
    h, s, v = cv2.split(hsv)
    mask = ((h >= p['h_lo']) & (h <= p['h_hi']) & (s >= p['s_min']) & (v >= p['v_min'])).astype(np.uint8) * 255
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    k = max(3, int(round(p['close_mm'] * px_per_mm)) | 1)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (k, k)))
    if roi is not None:
        rmask = np.zeros_like(mask)
        cv2.circle(rmask, (int(roi[0]), int(roi[1])), int(roi[2]), 255, -1)
        mask &= rmask
    n, lab, stats, cent = cv2.connectedComponentsWithStats(mask, 8)
    a_min = math.pi * (p['d_min_mm'] * px_per_mm / 2) ** 2
    a_max = math.pi * (p['d_max_mm'] * px_per_mm / 2) ** 2
    out, rejected = [], []
    for i in range(1, n):
        area = stats[i, cv2.CC_STAT_AREA]
        comp = (lab == i).astype(np.uint8)
        cnts, _ = cv2.findContours(comp, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        per = cv2.arcLength(cnts[0], True) if cnts else 0
        circ = 4 * math.pi * area / (per * per) if per > 0 else 0
        d_mm = 2 * math.sqrt(area / math.pi) / px_per_mm
        cx, cy = cent[i]
        reason = None
        if area < a_min:
            reason = 'small'
        elif area > a_max:
            reason = 'large'
        elif circ < p['circ_min']:
            reason = 'not_round'
        else:
            r = math.sqrt(area / math.pi)
            ring = np.zeros_like(comp)
            cv2.circle(ring, (int(round(cx)), int(round(cy))), int(r * 2.2 + 2), 1, -1)
            cv2.circle(ring, (int(round(cx)), int(round(cy))), int(r * 1.4 + 1), 0, -1)
            ring &= (1 - comp)
            vals = v[ring.astype(bool)]
            if vals.size == 0:
                reason = 'no_ring'
            else:
                dark_frac = float((vals <= p['ring_v_max']).mean())
                if dark_frac < p['ring_dark_frac']:
                    reason = 'ring_not_dark'
        rec = dict(x=float(cx), y=float(cy), d_mm=round(d_mm, 2), circ=round(circ, 2), area=int(area))
        (rejected if reason else out).append({**rec, 'reason': reason} if reason else rec)
    out.sort(key=lambda d: -d['area'])
    return out, rejected


def draw(img, dots, rejected):
    vis = img.copy()
    for d in rejected:
        cv2.drawMarker(vis, (int(d['x']), int(d['y'])), (128, 128, 128), cv2.MARKER_TILTED_CROSS, 12, 1)
    for d in dots:
        r = max(6, int(d['d_mm'] * 8))
        cv2.circle(vis, (int(d['x']), int(d['y'])), r, (0, 255, 0), 2)
        cv2.putText(vis, f"{d['d_mm']}mm", (int(d['x']) + r, int(d['y'])), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
    return vis


def evaluate(folder, px_per_mm):
    files = sorted(sum([glob.glob(os.path.join(folder, e)) for e in ('*.jpg', '*.jpeg', '*.png')], []))
    tp = fn = tn = fp = 0
    rows = []
    for f in files:
        name = os.path.basename(f).lower()
        truth = None if ('nodot' not in name and 'dot' not in name) else ('nodot' not in name)
        img = cv2.imread(f)
        dots, _ = find_dots(img, px_per_mm)
        found = len(dots) > 0
        rows.append((os.path.basename(f), truth, found, len(dots)))
        if truth is True:
            tp += found; fn += not found
        elif truth is False:
            fp += found; tn += not found
    for r in rows:
        print('\t'.join(map(str, r)))
    pos, neg = tp + fn, tn + fp
    print(f'점 있는 사진 {pos}장 중 검출 {tp} → 검출률 {tp / pos:.1%}' if pos else '점 있는 사진 없음')
    print(f'점 없는 사진 {neg}장 중 오검출 {fp} → 오검출률 {fp / neg:.1%}' if neg else '점 없는 사진 없음')
    return tp, fn, tn, fp


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('image', nargs='?')
    ap.add_argument('--eval')
    ap.add_argument('--px-per-mm', type=float, default=15.6)
    ap.add_argument('--roi', type=float, nargs=3, metavar=('X', 'Y', 'R'))
    ap.add_argument('--show')
    a = ap.parse_args()
    if a.eval:
        evaluate(a.eval, a.px_per_mm)
        return
    if not a.image:
        ap.error('사진 경로 또는 --eval 폴더')
    img = cv2.imread(a.image)
    if img is None:
        sys.exit(f'사진을 못 읽음: {a.image}')
    dots, rej = find_dots(img, a.px_per_mm, a.roi)
    print(f'점 {len(dots)}개:', dots)
    print(f'버린 노랑 영역 {len(rej)}개:', [(round(r["x"]), round(r["y"]), r["reason"]) for r in rej])
    if a.show:
        cv2.imwrite(a.show, draw(img, dots, rej))


if __name__ == '__main__':
    main()
