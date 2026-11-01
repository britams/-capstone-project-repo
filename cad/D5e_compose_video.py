# -*- coding: utf-8 -*-
"""D5e 애니메이션 프레임(main_*.png, inset_*.png, frames_*.json) → 글자·진행 막대를 붙인 영상 (CAP-AI-20)
실행 (PIL + ffmpeg): python3 D5e_compose_video.py <프레임 폴더> <출력 폴더>
"""
import glob
import json
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFont

src, dst = sys.argv[1], sys.argv[2]
os.makedirs(dst, exist_ok=True)
comp = os.path.join(dst, "comp")
os.makedirs(comp, exist_ok=True)
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
FONTB = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
f_title = ImageFont.truetype(FONTB, 26, index=1)
f_step = ImageFont.truetype(FONTB, 27, index=1)
f_real = ImageFont.truetype(FONT, 20, index=1)
f_small = ImageFont.truetype(FONT, 17, index=1)

meta = []
for f in sorted(glob.glob(os.path.join(src, "frames_*.json"))):
    meta += json.load(open(f, encoding="utf-8"))
meta.sort(key=lambda m: m["i"])
N = len(meta)

# main 프레임의 그림 영역 (흰 바탕 제외) — 여러 장을 합쳐 고정 자르기
box = None
for m in meta[::15]:
    im = Image.open(os.path.join(src, "main_%04d.png" % m["i"])).convert("L")
    bb = im.point(lambda p: 255 if p < 250 else 0).getbbox()
    if bb:
        box = bb if box is None else (min(box[0], bb[0]), min(box[1], bb[1]), max(box[2], bb[2]), max(box[3], bb[3]))
pad = 12
box = (max(0, box[0] - pad), max(0, box[1] - pad), box[2] + pad, box[3] + pad)

W, H = 1440, 810
LW = 740                                                   # 왼쪽 전체 그림 폭
steps = []
for m in meta:
    if not steps or steps[-1][0] != m["step"]:
        steps.append([m["step"], m["t"], m["t"]])
    steps[-1][2] = m["t"]
T = meta[-1]["t"]

for m in meta:
    i = m["i"]
    can = Image.new("RGB", (W, H), "white")
    mi = Image.open(os.path.join(src, "main_%04d.png" % i)).convert("RGB").crop(box)
    sc = min(LW / mi.width, (H - 60) / mi.height)
    mi = mi.resize((int(mi.width * sc), int(mi.height * sc)), Image.LANCZOS)
    can.paste(mi, ((LW - mi.width) // 2, 50 + (H - 50 - mi.height) // 2))
    ii = Image.open(os.path.join(src, "inset_%04d.png" % i)).convert("RGB")
    ii = ii.resize((660, 495), Image.LANCZOS)
    can.paste(ii, (W - 660 - 20, 50))
    d = ImageDraw.Draw(can)
    d.rectangle((W - 660 - 20, 50, W - 20, 545), outline=(150, 150, 150), width=2)
    d.text((W - 660 - 12, 56), "마킹실 확대", font=f_small, fill=(90, 90, 90))
    d.text((20, 12), "말벌 자동 마킹 트랩 D5e — 한 마리 처리 동작 (시간은 줄여서 보임)", font=f_title, fill=(25, 25, 25))
    # 단계 글자
    x0, y0 = W - 680, 560
    d.text((x0, y0), m["step"], font=f_step, fill=(20, 60, 140))
    if m["real"]:
        d.text((x0, y0 + 40), m["real"], font=f_real, fill=(170, 60, 30))
    J = m["J"]
    d.text((x0, y0 + 75), "바닥 %5.1f mm   마커 (%5.1f, %5.1f)   펜 서보 %5.1f°   입구 문 %s   방생 문 %s" % (
        J["floor"], J["xm"], J["ym"], J["horn"], "열림" if J["door_entry"] < 0 else "닫힘", "열림" if J["door_rel"] < 0 else "닫힘"),
        font=f_small, fill=(60, 60, 60))
    # 진행 막대
    bx0, bx1, by = x0, W - 24, y0 + 120
    d.rectangle((bx0, by, bx1, by + 14), fill=(232, 232, 232))
    for k, (nm, a, b) in enumerate(steps):
        xa = bx0 + (bx1 - bx0) * a / T
        d.line((xa, by - 3, xa, by + 17), fill=(170, 170, 170), width=1)
    xt = bx0 + (bx1 - bx0) * m["t"] / T
    d.rectangle((bx0, by, xt, by + 14), fill=(40, 100, 200))
    d.text((x0, by + 22), "색: 파랑 = 서보 (문 MG90S, 펜 SG90) · 회색 원통 = 28BYJ-48 · 금색 = T8 너트",
           font=f_small, fill=(90, 90, 90))
    d.text((x0, by + 44), "     주황 판 = 문판 · 노랑 = 마커 · 주황 몸 = 말벌 (보이게 칠함) · 노란 점 = 마킹",
           font=f_small, fill=(90, 90, 90))
    d.text((x0, by + 70), "모델: cad/D5e_module_kinematic.py (관절 변수 스프레드시트 Joints) · CAP-AI-20",
           font=f_small, fill=(120, 120, 120))
    can.save(os.path.join(comp, "c_%04d.png" % i))

mp4 = os.path.join(dst, "D5e_동작_한마리처리.mp4")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-framerate", "12", "-i", os.path.join(comp, "c_%04d.png"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "20", mp4], check=True)
gif = os.path.join(dst, "D5e_동작_한마리처리.gif")
pal = os.path.join(dst, "pal.png")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-vf", "fps=8,scale=760:-1:flags=lanczos,palettegen=stats_mode=diff", pal], check=True)
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp4, "-i", pal, "-lavfi",
                "fps=8,scale=760:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=4", gif], check=True)
try:
    os.remove(pal)
except OSError:
    pass
print(N, "frames", os.path.getsize(mp4) // 1024, "KB mp4", os.path.getsize(gif) // 1024, "KB gif")
