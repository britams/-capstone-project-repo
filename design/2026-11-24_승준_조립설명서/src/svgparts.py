# -*- coding: utf-8 -*-
"""나사·너트 그림 (SVG). 단위 mm. 축은 +x 방향, 머리는 x<0 (접시머리는 0~)."""
import math

NUT_AF = {2: 4.0, 2.5: 5.0, 3: 5.5, 4: 7.0, 5: 8.0}
PITCH = {2: 0.4, 2.5: 0.45, 3: 0.5, 4: 0.7, 5: 0.8}
STEEL = "#c9ccd1"; EDGE = "#3c4048"; DARKS = "#2b2d31"


def _threads(x0, x1, d, pitch, step=1.0):
    out = []
    p = pitch * step
    x = x0 + p
    while x < x1 - 0.05:
        out.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="%.3f"/>' % (x, -d / 2, x - p * 0.6, d / 2, EDGE, max(0.06, d * 0.03)))
        x += p
    return out


def screw_paths(kind, d, L, black=False):
    """kind: button, pan, socket, csk, tap, set. 반환: (요소 목록, xmin, xmax, ymax)"""
    fill = DARKS if black else STEEL
    sw = max(0.12, d * 0.05)
    el = []
    if kind == "csk":
        dk = 2.0 * d
        hk = (dk - d) / 2.0
        el.append('<path d="M0,%.2f L%.2f,%.2f L%.2f,%.2f L0,%.2f Z" fill="%s" stroke="%s" stroke-width="%.2f"/>' % (-dk / 2, hk, -d / 2, hk, d / 2, dk / 2, fill, EDGE, sw))
        el.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="%s" stroke="%s" stroke-width="%.2f"/>' % (hk, -d / 2, L - hk, d, fill, EDGE, sw))
        el += _threads(hk + 0.3, L, d, PITCH.get(d, 0.5))
        return el, 0.0, L, dk / 2
    if kind == "set":
        el.append('<rect x="0" y="%.2f" width="%.2f" height="%.2f" fill="%s" stroke="%s" stroke-width="%.2f"/>' % (-d / 2, L, d, fill, EDGE, sw))
        el += _threads(0.2, L, d, PITCH.get(d, 0.5))
        el.append('<rect x="0" y="%.2f" width="%.2f" height="%.2f" fill="none" stroke="%s" stroke-width="%.2f" stroke-dasharray="%.2f,%.2f"/>' % (-d * 0.3, d * 0.6, d * 0.6, EDGE, sw * 0.8, d * 0.15, d * 0.1))
        return el, 0.0, L, d / 2
    if kind == "button":
        dk, k = 1.75 * d, 0.55 * d
        el.append('<path d="M0,%.2f C%.2f,%.2f %.2f,%.2f %.2f,0 C%.2f,%.2f %.2f,%.2f 0,%.2f Z" fill="%s" stroke="%s" stroke-width="%.2f"/>' % (
            -dk / 2, -k * 0.55, -dk / 2, -k, -dk * 0.25, -k, -k, dk * 0.25, -k * 0.55, dk / 2, dk / 2, fill, EDGE, sw))
    elif kind == "socket":
        dk, k = 1.6 * d, 1.0 * d
        el.append('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="%.2f" fill="%s" stroke="%s" stroke-width="%.2f"/>' % (-k, -dk / 2, k, dk, d * 0.12, fill, EDGE, sw))
    else:  # pan, tap
        dk, k = 2.0 * d, 0.7 * d
        el.append('<path d="M0,%.2f L%.2f,%.2f Q%.2f,%.2f %.2f,%.2f L%.2f,%.2f Q%.2f,%.2f %.2f,%.2f L0,%.2f Z" fill="%s" stroke="%s" stroke-width="%.2f"/>' % (
            -dk / 2, -k * 0.6, -dk / 2, -k, -dk / 2, -k, -dk * 0.3, -k, dk * 0.3, -k, dk / 2, -k * 0.6, dk / 2, dk / 2, fill, EDGE, sw))
        el.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="%.2f"/>' % (-k, -dk * 0.18, -k, dk * 0.18, EDGE, sw * 1.6))
    if kind == "tap":
        tip = min(1.5 * d, L * 0.3)
        el.append('<path d="M0,%.2f L%.2f,%.2f L%.2f,0 L%.2f,%.2f L0,%.2f Z" fill="%s" stroke="%s" stroke-width="%.2f"/>' % (-d / 2, L - tip, -d / 2, L, L - tip, d / 2, d / 2, fill, EDGE, sw))
        el += _threads(0.2, L - tip * 0.5, d, PITCH.get(d, 0.5) * 1.6)
    else:
        el.append('<rect x="0" y="%.2f" width="%.2f" height="%.2f" fill="%s" stroke="%s" stroke-width="%.2f"/>' % (-d / 2, L, d, fill, EDGE, sw))
        el += _threads(0.2, L, d, PITCH.get(d, 0.5))
    return el, -k, L, dk / 2


def nut_paths(d):
    af = NUT_AF.get(d, 2 * d)
    r = af / math.sqrt(3)
    pts = " ".join("%.2f,%.2f" % (r * math.cos(math.radians(30 + 60 * i)), r * math.sin(math.radians(30 + 60 * i))) for i in range(6))
    return ['<polygon points="%s" fill="%s" stroke="%s" stroke-width="%.2f"/>' % (pts, STEEL, EDGE, 0.15),
            '<circle cx="0" cy="0" r="%.2f" fill="white" stroke="%s" stroke-width="0.15"/>' % (d / 2, EDGE)], r


def washer_paths(d):
    ro = 1.05 * d if d < 3 else (7.0 / 2 if d == 3 else 1.1 * d)
    return ['<circle cx="0" cy="0" r="%.2f" fill="%s" stroke="%s" stroke-width="0.15"/>' % (ro, STEEL, EDGE),
            '<circle cx="0" cy="0" r="%.2f" fill="white" stroke="%s" stroke-width="0.15"/>' % (d * 0.55, EDGE)], ro


def springnut_paths(d):
    w, h = 10.0, 6.0
    return ['<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" rx="1.2" fill="%s" stroke="%s" stroke-width="0.18"/>' % (-w / 2, -h / 2, w, h, STEEL, EDGE),
            '<circle cx="0" cy="0" r="%.2f" fill="white" stroke="%s" stroke-width="0.15"/>' % (d / 2, EDGE),
            '<circle cx="%.2f" cy="0" r="1.1" fill="#8a8f98" stroke="%s" stroke-width="0.12"/>' % (w / 2 - 1.8, EDGE),
            '<path d="M%.2f,%.2f L%.2f,%.2f" stroke="%s" stroke-width="0.25"/>' % (-w / 2 + 1, -h / 2 + 0.8, -w / 2 + 1, h / 2 - 0.8, EDGE)], w / 2


def spacer_paths(d, L):
    od = 6.0
    return ['<rect x="0" y="%.2f" width="%.2f" height="%.2f" fill="#f3f3f0" stroke="%s" stroke-width="0.18"/>' % (-od / 2, L, od, EDGE),
            '<line x1="0" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="0.12" stroke-dasharray="0.5,0.4"/>' % (-d / 2, L, -d / 2, EDGE),
            '<line x1="0" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="0.12" stroke-dasharray="0.5,0.4"/>' % (d / 2, L, d / 2, EDGE)], od / 2


def tape_svg(w_px=120, h_px=80):
    return ('<svg viewBox="0 0 40 26" width="%d" height="%d"><ellipse cx="17" cy="13" rx="11" ry="11" fill="#f2efe6" stroke="#555" stroke-width="0.6"/>'
            '<ellipse cx="17" cy="13" rx="5" ry="5" fill="white" stroke="#555" stroke-width="0.5"/>'
            '<rect x="17" y="2" width="21" height="4" fill="#f2efe6" stroke="#555" stroke-width="0.5"/></svg>') % (w_px, h_px)


def icon_svg(spec, box_w=34.0, box_h=20.0, black=False):
    """부품 상자용 그림 — box 크기(mm)에 맞게 확대."""
    kind = spec[0]
    if kind == "tape":
        return tape_svg()
    d = spec[1]
    if kind == "nut":
        el, r = nut_paths(d); xmin, xmax, ymax = -r, r, r
    elif kind == "washer":
        el, r = washer_paths(d); xmin, xmax, ymax = -r, r, r
    elif kind == "springnut":
        el, r = springnut_paths(d); xmin, xmax, ymax = -r, r, 3.2
    elif kind == "spacer":
        el, ymax = spacer_paths(d, spec[2]); xmin, xmax = 0, spec[2]
    else:
        el, xmin, xmax, ymax = screw_paths(kind, d, spec[2], black)
    pad = 0.8
    vw = (xmax - xmin) + 2 * pad
    vh = 2 * ymax + 2 * pad
    return '<svg viewBox="%.2f %.2f %.2f %.2f" preserveAspectRatio="xMidYMid meet" style="width:100%%;height:100%%">%s</svg>' % (
        xmin - pad, -ymax - pad, vw, vh, "".join(el))


def onetoone_svg(spec, label):
    """1:1 그림 (실제 mm 크기). 폭은 내용에 맞춤."""
    kind = spec[0]
    d = spec[1]
    if kind == "nut":
        el, r = nut_paths(d); xmin, xmax, ymax = -r, r, r
    elif kind == "washer":
        el, r = washer_paths(d); xmin, xmax, ymax = -r, r, r
    elif kind == "springnut":
        el, r = springnut_paths(d); xmin, xmax, ymax = -r, r, 3.2
    else:
        el, xmin, xmax, ymax = screw_paths(kind, d, spec[2], black=False)
    pad = 0.6
    w = (xmax - xmin) + 2 * pad
    h = 2 * ymax + 2 * pad
    return '<svg viewBox="%.2f %.2f %.2f %.2f" style="width:%.2fmm;height:%.2fmm">%s</svg>' % (xmin - pad, -ymax - pad, w, h, w, h, "".join(el))
