# -*- coding: utf-8 -*-
"""light_test.py — 조명이 필요한지 고르는 시험 (명령 정리 3-B 1번, CAP-AI-54)

무엇을 가리나 (판정 기준은 `design/2026-11-09_조명시험_계획_서현.md`):
  사용 A  판별·자세·점 확인 사진 (process.py 는 위 조명 TOP 255) → 밝기·고름·노랑 점 검출률
  사용 B  대기 중 마리 수 사진 (process.py 는 아래 조명 BOT 255) → 빈 사진과의 차이로 말벌이 보이나
  아래 조명은 사진 말고 '말벌을 바닥에 머물게 함'(행동)도 맡는다 → 이 시험으로는 빼지 않는다.

1) Pi (카메라 + UNO 2 연결): 더미 하나 놓을 때마다 한 번
     python light_test.py capture --amb bright --tag dot01   (빈 마킹실은 --tag empty01)
   조명 4가지 (TOP, BOT) = (0,0) (255,0) (0,255) (255,255) 를 돌며 3장씩, 노출·게인·초점·흰색 고정.
   파일: <out>/<amb>_T<top>_B<bot>_<tag>_<k>.png  (tag 는 dot / nodot / empty 로 시작)
2) PC: python light_test.py analyze <폴더> [--ppm 11.5]
3) 스크립트 점검 (합성 사진): python light_test.py selftest
"""
import argparse
import glob
import json
import os
import re
import sys
import time

import cv2
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'vision', 'scripts'))
from dot_detect import find_dots          # 승준 J4 검출기 그대로 (고치지 않음)

COMBOS = ((0, 0), (255, 0), (0, 255), (255, 255))
# 기준 (AI 판단, 서현 위임 — 값은 [추측], 첫 실측 뒤 다시 봄)
CRIT = dict(v_lo=80, v_hi=220, sat_max=0.01,      # A1 ROI 중앙 밝기, V ≥ 250 비율
            uni_min=0.6,                            # A2 4×4 칸 중앙값 최소/최대
            det_min=0.90, fp_max=0.05,              # A3 R5 검출률 90 %, 오검출 5 %
            diff_v=30, wasp_mm2=50, empty_mm2=10, b_min=0.95)   # B 차이 화소·면적·맞힌 비율
NAME = re.compile(r'^(?P<amb>[^_]+)_T(?P<t>\d+)_B(?P<b>\d+)_(?P<tag>[a-z]+)\d*_\d+\.png$')
CAM = dict(size=(1536, 864), frame_us=16667, exp_us=8000, gain=4.0, focus_m=0.1535)   # CM3 720p60 모드 (정의서 SJ-53)


def roi_of(img, ppm, side_mm=40):
    h, w = img.shape[:2]
    r = int(side_mm * ppm / 2)
    return img[max(0, h // 2 - r):h // 2 + r, max(0, w // 2 - r):w // 2 + r]


def brightness(roi):
    v = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)[..., 2]
    blocks = [np.median(b) for row in np.array_split(v, 4, 0) for b in np.array_split(row, 4, 1)]
    return float(np.median(v)), float((v >= 250).mean()), float(min(blocks) / max(max(blocks), 1))


def changed_mm2(img, empty, ppm, p=CRIT):
    d = cv2.absdiff(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.cvtColor(empty, cv2.COLOR_BGR2GRAY))
    m = cv2.morphologyEx((d > p['diff_v']).astype(np.uint8), cv2.MORPH_OPEN, np.ones((3, 3), np.uint8))
    return float(m.sum()) / ppm ** 2


def analyze(folder, ppm, p=CRIT, quiet=False):
    groups = {}
    for f in sorted(glob.glob(os.path.join(folder, '*.png'))):
        m = NAME.match(os.path.basename(f))
        if m:
            groups.setdefault((m['amb'], int(m['t']), int(m['b'])), []).append((m['tag'], f))
    res = {}
    for key, items in sorted(groups.items()):
        imgs = [(tag, roi_of(cv2.imread(f), ppm)) for tag, f in items]
        lit = [r for tag, r in imgs if tag != 'empty']
        bs = [brightness(r) for r in lit]
        v_med = float(np.median([b[0] for b in bs])) if bs else 0
        sat = max([b[1] for b in bs], default=1)
        dot = [len(find_dots(r, ppm)[0]) > 0 for tag, r in imgs if tag == 'dot']
        nod = [len(find_dots(r, ppm)[0]) > 0 for tag, r in imgs if tag == 'nodot']
        det = sum(dot) / len(dot) if dot else None
        fp = sum(nod) / len(nod) if nod else None
        empties = [r for tag, r in imgs if tag == 'empty']
        uni = min([brightness(r)[2] for r in empties], default=0)     # 고름은 빈 마킹실로 (말벌이 칸을 어둡게 함)
        b_ok = None
        if len(empties) >= 2 and lit:
            ref = empties[0]
            hit = [changed_mm2(r, ref, ppm) >= p['wasp_mm2'] for r in lit]
            quiet_e = [changed_mm2(r, ref, ppm) < p['empty_mm2'] for r in empties[1:]]
            b_ok = min(sum(hit) / len(hit), sum(quiet_e) / len(quiet_e))
        a_pass = (p['v_lo'] <= v_med <= p['v_hi'] and sat <= p['sat_max'] and uni >= p['uni_min']
                  and det is not None and det >= p['det_min'] and fp is not None and fp <= p['fp_max'])
        b_pass = b_ok is not None and b_ok >= p['b_min']
        res[key] = dict(v=v_med, sat=sat, uni=uni, det=det, fp=fp, n_dot=len(dot), n_nodot=len(nod),
                        b=b_ok, A=a_pass, B=b_pass)
        if not quiet:
            fmt = lambda x: '-' if x is None else '%.2f' % x
            print('%-7s T%-3d B%-3d  V %5.1f  포화 %.3f  고름 %.2f  검출 %s (%d)  오검출 %s (%d)  B %s  → A %s  B %s'
                  % (key[0], key[1], key[2], v_med, sat, uni, fmt(det), len(dot), fmt(fp), len(nod), fmt(b_ok),
                     'O' if a_pass else 'X', 'O' if b_pass else 'X'))
    return res, verdict(res, quiet)


def verdict(res, quiet=False):
    ambs = sorted({k[0] for k in res})
    every = lambda t, b, what: bool(ambs) and all(res.get((a, t, b), {}).get(what) for a in ambs)
    out = {}
    if every(0, 0, 'A'):
        out['A'] = '위 조명 없어도 됨 → TOP 뺄 수 있음 (Q1·D3·LIGHT TOP·링 182)'
    elif every(255, 0, 'A'):
        out['A'] = '위 조명 필요 (지금 설계대로)'
    elif every(255, 255, 'A'):
        out['A'] = '위만으로 부족 → 사진 찍을 때 위·아래 둘 다 켬 (process.py lights 고침)'
    else:
        out['A'] = '어느 조합도 통과 못 함 → 조명 세기·자리 다시'
    if every(0, 255, 'B'):
        out['B'] = '대기 중 아래 조명만으로 마리 수 셈 (지금 설계대로)'
    elif every(255, 255, 'B'):
        out['B'] = '대기 중에도 위 조명 필요 → process.py to_idle·press 고침, 전력 다시 (elec_budget)'
    else:
        out['B'] = '대기 사진으로 마리 수 못 셈 → 빛 게이트 장부만 믿음 (idle_check 끔)'
    out['BOT'] = ('사진에는 아래 조명이 필요 없음 — 빼는 것은 살아 있는 말벌 행동 시험(2027-07) 뒤'
                  if every(0, 0, 'B') else '아래 조명 유지 (사진에도 필요)')
    if not quiet:
        for k in ('A', 'B', 'BOT'):
            print('판정 %-3s: %s' % (k, out[k]))
    return out


def capture(out, amb, tag, n=3, settle_s=0.5):
    """Pi 에서만. UNO 2 (trap_doors) 로 LIGHT, Picamera2 로 고정 노출 사진. [미검증 — Pi·CM3 없음]"""
    from picamera2 import Picamera2
    from ports import open_serial_ports, identify
    doors = identify(open_serial_ports())['trap_doors']
    cam = Picamera2()
    cam.configure(cam.create_video_configuration(main={'size': CAM['size'], 'format': 'RGB888'}))
    cam.start()
    doors.command('LIGHT TOP 255')
    doors.command('LIGHT BOT 0')
    time.sleep(1.5)                                   # 흰색 맞춤만 자동으로 한 번
    gains = cam.capture_metadata()['ColourGains']
    cam.set_controls({'AeEnable': False, 'AwbEnable': False, 'ColourGains': gains,
                      'ExposureTime': CAM['exp_us'], 'AnalogueGain': CAM['gain'],
                      'FrameDurationLimits': (CAM['frame_us'], CAM['frame_us']),
                      'AfMode': 0, 'LensPosition': 1 / CAM['focus_m']})
    os.makedirs(out, exist_ok=True)
    meta_all = {}
    for t, b in COMBOS:
        doors.command('LIGHT TOP %d' % t)
        doors.command('LIGHT BOT %d' % b)
        time.sleep(settle_s)
        for k in range(n):
            name = '%s_T%d_B%d_%s_%d.png' % (amb, t, b, tag, k)
            arr = cam.capture_array()                 # RGB888 = 메모리 순서 BGR → cv2 그대로
            cv2.imwrite(os.path.join(out, name), arr)
            md = cam.capture_metadata()
            meta_all[name] = {x: md.get(x) for x in ('ExposureTime', 'AnalogueGain', 'Lux', 'LensPosition')}
    doors.command('LIGHT TOP 0')
    doors.command('LIGHT BOT 0')
    cam.stop()
    with open(os.path.join(out, 'meta_%s_%s.json' % (amb, tag)), 'w') as fp:
        json.dump(dict(cam=CAM, colour_gains=gains, frames=meta_all), fp, indent=1)
    print('%d장 → %s' % (len(COMBOS) * n, out))


def selftest(folder, ppm=11.5, n=20):
    """합성 사진으로 '판정 논리'만 확인 (실제 빛을 흉내 내지 않음 — 성능 보장 아님)."""
    from make_synthetic_dummies import make
    rng = np.random.default_rng(7)
    os.makedirs(folder, exist_ok=True)
    for f in glob.glob(os.path.join(folder, '*.png')):
        os.remove(f)
    # 밝기 = 바깥빛 + 위 0.55 + 아래 0.25 / 한쪽 기울기: 바깥빛만이면 큼 (트랩 옆면에서 들어옴)
    tilt = {(0, 0): 0.6, (255, 0): 0.1, (0, 255): 0.3, (255, 255): 0.1}
    for amb, ambient in (('bright', 0.30), ('dim', 0.15)):
        scenes = [('dot', make(rng, ppm, True)[0]) for _ in range(n)] + [('nodot', make(rng, ppm, False)[0]) for _ in range(n)]
        empty = np.full_like(scenes[0][1], 215)
        scenes += [('empty', (empty + rng.normal(0, 3, empty.shape)).clip(0, 255).astype(np.uint8)) for _ in range(3)]
        for (t, b), tl in tilt.items():
            gain = ambient + 0.55 * (t > 0) + 0.25 * (b > 0)
            for i, (tag, img) in enumerate(scenes):
                h, w = img.shape[:2]
                ramp = 1 - tl * np.linspace(0, 1, w)[None, :, None]
                out = np.clip(img.astype(np.float32) * gain * ramp, 0, 255).astype(np.uint8)
                cv2.imwrite(os.path.join(folder, '%s_T%d_B%d_%s%02d_0.png' % (amb, t, b, tag, i)), out)
    res, v = analyze(folder, ppm)
    # ① 사진 처리: 밝은 날 위 조명 없음 X / 위 조명 O, 빈 사진 대비 B (아래 조명 O, 다 끔 X)
    ok = [not res[('bright', 0, 0)]['A'], res[('bright', 255, 0)]['A'],
          res[('bright', 0, 255)]['B'], not res[('dim', 0, 0)]['B']]
    # ② 판정표: 결과 표를 손으로 만들어 넣음
    R = lambda **kv: {(a, t, b): dict(A=kv.get('A%d%d' % (t > 0, b > 0), False), B=kv.get('B%d%d' % (t > 0, b > 0), False))
                      for a in ('bright', 'dim') for t, b in COMBOS}
    ok += [verdict(R(A00=True, A10=True), True)['A'].startswith('위 조명 없어도'),
           verdict(R(A10=True), True)['A'].startswith('위 조명 필요'),
           verdict(R(A11=True), True)['A'].startswith('위만으로 부족'),
           verdict(R(), True)['A'].startswith('어느 조합도'),
           verdict(R(B01=True), True)['B'].startswith('대기 중 아래 조명만으로'),
           verdict(R(B11=True), True)['B'].startswith('대기 중에도 위'),
           verdict(R(B00=True, B01=True), True)['BOT'].startswith('사진에는 아래 조명이 필요 없음')]
    print('selftest %d/%d' % (sum(map(bool, ok)), len(ok)), 'PASS' if all(ok) else 'FAIL')
    ok = all(ok)
    return ok


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest='cmd', required=True)
    c = sp.add_parser('capture'); c.add_argument('--amb', required=True); c.add_argument('--tag', required=True)
    c.add_argument('--out', default='light_test_photos'); c.add_argument('--n', type=int, default=3)
    a_ = sp.add_parser('analyze'); a_.add_argument('folder'); a_.add_argument('--ppm', type=float, default=11.5)
    s = sp.add_parser('selftest'); s.add_argument('--out', default=os.path.join(__import__('tempfile').gettempdir(), 'light_selftest'))
    a = ap.parse_args()
    if a.cmd == 'capture':
        capture(a.out, a.amb, a.tag, a.n)
    elif a.cmd == 'analyze':
        analyze(a.folder, a.ppm)
    else:
        sys.exit(0 if selftest(a.out) else 1)


if __name__ == '__main__':
    main()
