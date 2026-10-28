"""make_synthetic_dummies.py — J4·J8 시험용 합성 더미 사진 (CAP-AI-SJ-20)

실제 말벌·더미 사진이 생기기 전에 스크립트가 도는지 확인하는 용도. **성능을 보장하지 않음.**
위에서 본 말벌(격자에 눌림): 검은 머리·흉부, 어두운 배에 주황 넷째 마디, 노랑 다리, 반투명 날개, 3 mm 격자.
점 있는 사진은 흉부에 노랑 점(지름 0.9~2.0 mm). 파일 이름 dot_###.png / nodot_###.png,
정답 좌표(흉부 중심, 점 중심)는 labels.csv.

사용: python make_synthetic_dummies.py 출력폴더 [--n 40] [--px-per-mm 15.6] [--seed 1]
"""
import argparse
import csv
import math
import os

import cv2
import numpy as np


def ell(img, c, ax, ang, color, ppm):
    cv2.ellipse(img, (int(c[0]), int(c[1])), (max(1, int(ax[0] * ppm / 2)), max(1, int(ax[1] * ppm / 2))),
                ang, 0, 360, color, -1, cv2.LINE_AA)


def make(rng, ppm, with_dot):
    W = H = int(44 * ppm)                         # 마킹실 40 mm + 여유
    base = rng.uniform(200, 235)
    img = np.full((H, W, 3), base, np.float32)
    img[..., 0] *= rng.uniform(0.9, 1.0)          # 살짝 색온도 변화
    cx, cy = W / 2 + rng.uniform(-6, 6) * ppm, H / 2 + rng.uniform(-6, 6) * ppm
    ang = rng.uniform(0, 360)
    ux, uy = math.cos(math.radians(ang)), math.sin(math.radians(ang))   # 머리 쪽 방향
    px, py = -uy, ux

    def at(t_mm, s_mm=0.0):
        return (cx + (ux * t_mm + px * s_mm) * ppm, cy + (uy * t_mm + py * s_mm) * ppm)

    layer = img.copy()
    # 날개 (반투명, 흉부에서 뒤로)
    for side in (-1, 1):
        wing = layer.copy()
        ell(wing, at(-6.5, side * 2.5), (11, 3.2), ang + side * 8, (150, 160, 165), ppm)
        layer = cv2.addWeighted(wing, 0.35, layer, 0.65, 0)
    # 다리 (노랑 끝마디)
    for k, t in enumerate((1.0, 0.0, -1.0)):
        for side in (-1, 1):
            p0 = at(t, side * 1.8)
            p1 = at(t + rng.uniform(-3, 3), side * rng.uniform(5, 8))
            cv2.line(layer, (int(p0[0]), int(p0[1])), (int(p1[0]), int(p1[1])), (25, 35, 45), max(1, int(0.5 * ppm)), cv2.LINE_AA)
            p2 = (p1[0] + side * px * 3 * ppm, p1[1] + side * py * 3 * ppm)
            cv2.line(layer, (int(p1[0]), int(p1[1])), (int(p2[0]), int(p2[1])), (40, 190, 230), max(1, int(0.4 * ppm)), cv2.LINE_AA)
    # 배 (어두움 + 마디 띠 + 주황 넷째 마디)
    ell(layer, at(-9.0), (10.5, 6.5), ang, (30, 35, 45), ppm)
    for t, col in ((-6.2, (60, 120, 170)), (-8.0, (60, 120, 170)), (-10.0, (40, 140, 225))):
        ell(layer, at(t), (1.1, 6.0 - abs(t + 9) * 0.3), ang, col, ppm)
    # 흉부·머리
    thorax = at(0.0)
    tw, tl = rng.uniform(3.8, 4.6), rng.uniform(4.8, 5.6)
    ell(layer, thorax, (tl, tw), ang, (20, 22, 28), ppm)
    ell(layer, at(4.0), (2.6, 4.4), ang, (25, 30, 40), ppm)
    ell(layer, at(5.0), (1.0, 3.0), ang, (40, 120, 190), ppm)          # 얼굴 주황
    dot = None
    if with_dot:
        d_mm = rng.uniform(0.9, 2.0)
        dot = at(rng.uniform(-0.8, 0.8), rng.uniform(-0.8, 0.8))
        cv2.circle(layer, (int(dot[0]), int(dot[1])), int(d_mm * ppm / 2), (30, 215, 245), -1, cv2.LINE_AA)
    img = layer
    # 격자 (3 mm, 회색 선 0.3 mm)
    off = rng.uniform(0, 3 * ppm)
    g = 3 * ppm
    for k in range(-1, int(W / g) + 2):
        x = int(off + k * g)
        cv2.line(img, (x, 0), (x, H), (90, 90, 90), max(1, int(0.3 * ppm)))
        cv2.line(img, (0, x), (W, x), (90, 90, 90), max(1, int(0.3 * ppm)))
    # 조명 기울기·흐림·잡음
    yy, xx = np.mgrid[0:H, 0:W]
    grad = 1 + rng.uniform(-0.15, 0.15) * (xx / W - 0.5) + rng.uniform(-0.15, 0.15) * (yy / H - 0.5)
    img = img * grad[..., None] * rng.uniform(0.8, 1.1)
    img = cv2.GaussianBlur(img, (0, 0), rng.uniform(0.6, 1.6))
    img = img + rng.normal(0, rng.uniform(2, 6), img.shape)
    img = np.clip(img, 0, 255).astype(np.uint8)
    return img, thorax, dot, ang


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--n', type=int, default=40)
    ap.add_argument('--px-per-mm', type=float, default=15.6)
    ap.add_argument('--seed', type=int, default=1)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    rng = np.random.default_rng(a.seed)
    with open(os.path.join(a.out, 'labels.csv'), 'w', newline='') as fp:
        w = csv.writer(fp)
        w.writerow(['file', 'has_dot', 'thorax_x', 'thorax_y', 'dot_x', 'dot_y', 'head_angle_deg'])
        for i in range(a.n):
            for has in (True, False):
                img, th, dot, ang = make(rng, a.px_per_mm, has)
                name = f"{'dot' if has else 'nodot'}_{i:03d}.png"
                cv2.imwrite(os.path.join(a.out, name), img)
                w.writerow([name, int(has), round(th[0], 1), round(th[1], 1),
                            round(dot[0], 1) if dot else '', round(dot[1], 1) if dot else '', round(ang, 1)])
    print(f'{2 * a.n}장 → {a.out}')


if __name__ == '__main__':
    main()
