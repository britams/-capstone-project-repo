# -*- coding: utf-8 -*-
"""vision_format.py — 승준 비전 출력 → process.py가 읽는 한 마리 dict (서현 CAP-AI-52, 2026-11-08)

process.py의 vision.look(what)은 마리마다 아래 dict 하나씩, 리스트로 돌려준다 (인터페이스 정의서 '비전 → 제어 결과' 줄):
  species  'velutina' | 'crabro' | 'other'   VespAI 클래스 1 / 0, 신뢰도 < CONF_MIN 이면 'other' (→ 격리)
  conf     0~1
  mw_mm    중흉배판 폭 mm 또는 None (못 잼 → 계절 규칙)
  marked   흉부 ROI 안에 노랑 점이 있나 (dot_detect.find_dots 결과가 1개 이상)
  pose     'dorsal' | 'ventral' | 'side' | None,  p = 흉부 찾기 확률
  x, y     흉부 가운데 mm (원점 격자 가운데, +x 방생 문 쪽, +y 먹이통 쪽)
  thorax   (x, y, θ rad, L, w) mm — mark_planner.plan()의 est.   unc = (σ_xy, σ_θ, σ_size)
           thorax가 있으면 process.py가 mark_planner로 찍을 점을 고르고, 없으면 x, y 한 점에 찍는다.
"""
import math

CLASS = {1: 'velutina', 0: 'crabro'}     # VespAI monitor_run.py (run_vespai_examples.py CLASS_VELUTINA, CLASS_CRABRO)
CONF_MIN = 0.8                           # J1 실행 기준값


def species_of(cls_id, conf):
    return CLASS.get(cls_id, 'other') if conf >= CONF_MIN else 'other'


def px_to_mm(u, v, cam):
    """사진 화소 (u 오른쪽, v 아래) → 좌표 mm. cam = dict(u0, v0 격자 가운데 화소, px_per_mm, rot_deg 사진이 돈 각도).
    카메라 방향(rot_deg)은 장착 뒤 격자 사진으로 정한다 — 미검증."""
    dx, dy = (u - cam['u0']) / cam['px_per_mm'], -(v - cam['v0']) / cam['px_per_mm']
    a = math.radians(cam.get('rot_deg', 0.0))
    return dx * math.cos(a) - dy * math.sin(a), dx * math.sin(a) + dy * math.cos(a)


def make_obs(cls_id, conf, mw_mm=None, dots=(), pose=None, p=0.0, thorax=None, unc=(0.4, math.radians(8), 0.1)):
    """한 마리 결과를 만든다. thorax는 이미 mm 좌표 (x, y, θ, L, w)."""
    o = dict(species=species_of(cls_id, conf), conf=conf, mw_mm=mw_mm, marked=len(dots) > 0, pose=pose, p=p)
    if thorax is not None:
        o.update(x=thorax[0], y=thorax[1], thorax=tuple(thorax), unc=tuple(unc))
    return o
