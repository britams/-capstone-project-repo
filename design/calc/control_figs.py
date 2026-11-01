# -*- coding: utf-8 -*-
"""제어 통합 정리 그림 2장 (서현, CAP-AI-21) → design/img/control/
1) 제어_블록도_회로.png — 제어기·전원·배선 (UNO 1 움직임 / UNO 2 문·센서·조명)
2) 센서_카메라_배치.png — 방(통로) 순서와 빛 게이트 G1~G6·카메라·조명 위치 (모식도)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fbd_lib import plt, arrow, label  # noqa: E402
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle, Polygon  # noqa: E402

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "img", "control")
os.makedirs(OUT, exist_ok=True)


def box(ax, x, y, w, h, title, lines=(), fc="#eef3fb", ec="#2f5597", fs=10, tfs=12):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.15", fc=fc, ec=ec, lw=1.6))
    ax.text(x + 0.15, y + h - 0.25, title, fontsize=tfs, fontweight="bold", va="top")
    for i, t in enumerate(lines):
        ax.text(x + 0.15, y + h - 0.75 - i * 0.38, t, fontsize=fs, va="top")


def wire(ax, p, q, c="#444", lw=1.6, ls="-", text=None, toff=(0, 0.15), fs=9):
    ax.plot([p[0], q[0]], [p[1], q[1]], color=c, lw=lw, ls=ls, zorder=0)
    if text:
        ax.text((p[0] + q[0]) / 2 + toff[0], (p[1] + q[1]) / 2 + toff[1], text, fontsize=fs, ha="center", color=c,
                bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.5))


def block():
    fig, ax = plt.subplots(figsize=(20, 13))
    # 전원
    box(ax, 0.3, 10.2, 4.2, 2.2, "전원", ["① 27 W USB-C (5.1 V 5 A) → Pi 5", "② 5 V 3 A 어댑터 → 구동 레일", "    퓨즈 3 A + 1000 µF (서보 옆)", "모든 GND 공통 (Pi·UNO·레일)"], fc="#fff4e5", ec="#c55a11")
    # Pi
    box(ax, 6.0, 9.0, 7.6, 3.4, "Raspberry Pi 5 (보유) — 판단·AI·순서", [
        "+ AI HAT+ (Hailo) · AI 카메라 IMX500 (CSI, 격자 위 200 mm)",
        "AI: 종 / 여왕벌(크기) / 뒤집힘 / 흉부 위치 → 찍을 점",
        "상태 머신 · 로그 · 방마다 마릿수 셈 (게이트 + 카메라)",
        "UNO 2개에 한 줄 명령 (USB 시리얼 115200) · 2 s 하트비트",
        "원격 확인 (Wi-Fi)"])
    # UNO1
    box(ax, 0.3, 1.0, 8.8, 6.6, "UNO 1 '움직임' (보유) — 펄스·힘처럼 빠른 일", [
        "D2~D5  → ULN2003 → 28BYJ-48  바닥 F (153)",
        "D6~D9  → ULN2003 → 28BYJ-48  마커 X (215)",
        "D10~D13 → ULN2003 → 28BYJ-48 마커 Y (209)",
        "A0  → SG90 펜 들기 (205): 내릴 때 2단계",
        "       (팁 위 2 mm까지 빠르게, 마지막 2 mm ≤ 60 °/s)",
        "A1·A2 → HX711 (DT·SCK) ← 로드셀 (148)",
        "       바닥 누르기: F_p 0.5 N에서 멈춤, 가까울수록 느리게",
        "A3·A4·A5 ← 원점 스위치 F·X·Y (내부 풀업, 눌리면 GND)",
        "명령: MOVE / PATH / PRESS / PEN / HOME / STOP",
        "하트비트 끊기면: 펜 들기 → 모터 정지",
        "핀 18개 모두 사용 (NEMA17로 바꾸면 7개로 줄어듦)"], fc="#eef7ee", ec="#2e7d32")
    # UNO2
    box(ax, 10.6, 1.0, 9.0, 6.6, "UNO 2 '문·센서·조명' (보유)", [
        "D9  → MG90S 입구 문 (112)   혼 핀 미닫이",
        "D10 → MG90S 격리 문 (170)   +60° 닫힘 / −60° 열림",
        "D11 → MG90S 방생 문 (176)   한 번에 한 문만 움직임",
        "A0~A5 ← 빛 게이트 G1~G6 (적외선 빔, 디지털 출력)",
        "       G1 입구 세로관 · G2 입구 문틈 · G3 격리 문틈",
        "       G4 격리 통로 끝 · G5 방생 문틈 · G6 방생 출구",
        "D2 → MOSFET → 위 링 조명 (촬영할 때만)",
        "D3 → MOSFET → 아래 조명 (바닥, 등 위 자세 유도)",
        "D4 → MOSFET → 출구 조명 (방생·격리 쪽으로 유도)",
        "규칙: 문틈 게이트가 0.2 s 비어야 닫음,",
        "      닫는 중 막히면 즉시 다시 엶 (Pi 안 거침)"], fc="#f3eefb", ec="#6a3d9a")
    # 선
    wire(ax, (4.5, 11.3), (6.0, 11.3), c="#c55a11", lw=2.4, text="5.1 V")
    wire(ax, (2.4, 10.2), (2.4, 7.6), c="#c55a11", lw=2.4, text="5 V 레일 → ULN2003·서보·HX711", toff=(1.9, 0))
    ax.plot([4.5, 5.3, 5.3, 15.6, 15.6], [10.4, 10.4, 8.4, 8.4, 7.6], color="#c55a11", lw=2.4, zorder=0)
    ax.text(17.2, 8.55, "5 V 레일 → MG90S ×3·빔·조명", fontsize=9, color="#c55a11", ha="center", bbox=dict(fc="white", ec="none", alpha=0.85, pad=0.5))
    wire(ax, (8.0, 9.0), (5.5, 7.6), c="#2f5597", lw=2.0, text="USB (시리얼 + UNO 전원)", toff=(-0.6, 0.15))
    wire(ax, (11.5, 9.0), (14.0, 7.6), c="#2f5597", lw=2.0, text="USB", toff=(0.5, 0.1))
    wire(ax, (9.1, 4.0), (10.6, 4.0), c="#888", lw=1.2, ls="--", text="이벤트는 Pi로만 (UNO끼리 직접 안 묶음)", toff=(0, 0.25), fs=8.5)
    ax.text(0.3, 0.35, "그림은 연결 관계를 보이는 모식도 (핀 번호는 승준 J6·제어부 문서 6-2를 D5e에 맞춤). 전류: 28BYJ-48 약 0.2 A × 3, MG90S 이동 0.2~0.7 A (한 번에 하나), 조명 0.1~0.3 A → 최대 약 1.6 A < 3 A",
            fontsize=10, color="#555")
    ax.set_xlim(0, 20)
    ax.set_ylim(0, 12.8)
    ax.axis("off")
    ax.set_title("제어 블록도와 배선 — Pi 5가 판단하고, UNO 2개가 빠른 일을 한다 (D5e, 2026-11-02)", fontsize=16, fontweight="bold", loc="left")
    fig.savefig(os.path.join(OUT, "제어_블록도_회로.png"), dpi=110, bbox_inches="tight", facecolor="white")


def placement():
    fig, ax = plt.subplots(figsize=(20, 11))
    duct = "#d9e2ef"
    # 트랩 몸통
    ax.add_patch(Polygon([(0.5, 0.5), (4.5, 0.5), (5.0, 2.6), (0.0, 2.6)], closed=True, fc="#cfe8c4", ec="#4d7f3a"))
    ax.text(2.5, 1.4, "상용 트랩 몸통\n(유인액 · 노란 깔때기로 들어옴)", ha="center", fontsize=11)
    # 입구 세로관
    ax.add_patch(Rectangle((2.3, 2.6), 0.6, 4.2, fc=duct, ec="#555"))
    arrow(ax, (2.6, 3.0), (2.6, 6.2), "#2e7d32", lw=2)
    ax.text(1.0, 4.3, "입구 세로관\n(빛 쪽 위로 걸어 올라옴)", ha="center", fontsize=10)
    # 굽힘 + 수평
    ax.add_patch(Rectangle((2.3, 6.8), 3.4, 0.6, fc=duct, ec="#555"))
    # 문 112
    ax.add_patch(Rectangle((5.7, 6.5), 0.25, 1.2, fc="#f2a65a", ec="#a0522d"))
    ax.text(4.9, 8.75, "입구 문 112 (MG90S)", ha="center", fontsize=9.5)
    # 마킹실
    ax.add_patch(Rectangle((6.0, 5.2), 4.0, 3.2, fc="#f7f7f7", ec="#333", lw=1.6))
    ax.text(8.0, 7.55, "마킹실 120 (40 × 40)", ha="center", fontsize=10.5)
    ax.plot([6.0, 10.0], [8.1, 8.1], color="#777", lw=3, ls=(0, (1, 1)))
    ax.text(8.0, 8.65, "격자 130 (투명 권장) ····", fontsize=9.5, ha="center", color="#555")
    ax.add_patch(Rectangle((6.3, 5.9), 3.4, 0.25, fc="#8fbf8f", ec="#2e7d32"))
    ax.text(8.0, 5.5, "승강 바닥 140 (아래 조명)", ha="center", fontsize=9)
    ax.add_patch(Polygon([(7.6, 6.15), (8.4, 6.15), (8.0, 6.7)], closed=True, fc="#5a3a1a"))
    ax.text(8.55, 6.45, "말벌", fontsize=9)
    # 카메라
    ax.add_patch(Rectangle((7.4, 10.0), 1.2, 0.5, fc="#333"))
    ax.add_patch(Circle((8.0, 9.95), 0.18, fc="#666"))
    ax.text(8.0, 10.75, "AI 카메라 1대 (IMX500) + 위 링 조명 — 격자 위 200 mm", ha="center", fontsize=10.5, fontweight="bold")
    ax.plot([7.5, 6.0], [9.9, 8.15], color="#999", lw=0.8, ls="--")
    ax.plot([8.5, 10.0], [9.9, 8.15], color="#999", lw=0.8, ls="--")
    # 격리 통로 (위로)
    ax.add_patch(Rectangle((10.0, 7.4), 0.25, 0.9, fc="#f2a65a", ec="#a0522d"))
    ax.text(11.0, 7.0, "격리 문 170", fontsize=9.5)
    ax.add_patch(Rectangle((10.25, 7.6), 2.0, 0.5, fc=duct, ec="#555"))
    ax.add_patch(Rectangle((11.75, 8.1), 0.5, 2.4, fc=duct, ec="#555"))
    ax.add_patch(Circle((12.0, 11.6), 1.0, fc="#eaf4fb", ec="#6a8caf"))
    ax.text(12.0, 11.6, "포획통\n(여왕벌·다른 종·\n방제 모드)", ha="center", va="center", fontsize=9.5)
    arrow(ax, (10.6, 7.85), (11.6, 7.85), "#c00000", lw=2)
    arrow(ax, (12.0, 8.4), (12.0, 10.4), "#c00000", lw=2)
    # 방생 (오른쪽)
    ax.add_patch(Rectangle((10.0, 5.5), 0.25, 1.2, fc="#f2a65a", ec="#a0522d"))
    ax.text(11.0, 5.1, "방생 문 176", fontsize=9.5)
    ax.add_patch(Rectangle((10.25, 5.85), 4.0, 0.5, fc=duct, ec="#555"))
    ax.add_patch(Polygon([(14.25, 5.75), (15.0, 6.1), (14.25, 6.45)], closed=True, fc="#bbb", ec="#555"))
    ax.text(14.6, 5.25, "한 방향 출구 → 밖 (일벌: 마킹·먹이 뒤)", fontsize=9.5, ha="center")
    arrow(ax, (10.6, 6.1), (13.6, 6.1), "#2f5597", lw=2)
    # 게이트
    gates = [("G1", (2.6, 4.6), "입구 세로관 — 들어옴 알림"), ("G2", (5.45, 7.1), "입구 문틈 — 닫기 전 비었나"),
             ("G3", (10.45, 7.85), "격리 문틈"), ("G4", (12.0, 9.7), "격리 통로 끝 — 포획통에 들어감"),
             ("G5", (10.45, 6.1), "방생 문틈"), ("G6", (13.9, 6.1), "방생 출구 — 나감")]
    for g, (x, y), t in gates:
        ax.plot([x - 0.45, x + 0.45], [y, y], color="#d62728", lw=2.2, ls=(0, (2, 1)))
        ax.add_patch(Circle((x - 0.45, y), 0.09, fc="#d62728"))
        ax.add_patch(Circle((x + 0.45, y), 0.09, fc="#1f77b4"))
        label(ax, (x, y + 0.32), g, c="#d62728", fs=10, weight="bold")
    tx = 16.6
    ax.text(tx, 11.8, "빛 게이트 (적외선 빔, 송신 ● 수신 ●)", fontsize=12, fontweight="bold")
    for i, (g, _, t) in enumerate(gates):
        ax.text(tx, 11.2 - i * 0.5, "%s  %s" % (g, t), fontsize=10.5)
    ax.text(tx, 7.6, "방 이동 판정", fontsize=12, fontweight="bold")
    for i, t in enumerate(["게이트 '막힘 → 풀림' 순서 = 지나감",
                           "문틈 게이트가 0.2 s 비어야 문을 닫음",
                           "카메라: 마킹실 안 마릿수 (0이면 빈 방)",
                           "들어간 수 − 나간 수 = 방 안 마릿수",
                           "게이트와 카메라가 어긋나면 → 격리 + 로그",
                           "시간 초과(60 s) → 조명 바꿔 유도 → 로그"]):
        ax.text(tx, 7.0 - i * 0.48, "· " + t, fontsize=10.5)
    ax.set_xlim(-0.2, 22.2)
    ax.set_ylim(0, 12.8)
    ax.set_aspect("equal")
    ax.axis("off")
    ax.set_title("센서·카메라 배치 모식도 — 방(통로) 순서와 빛 게이트 G1~G6 (D5e, 크기 비례 아님)", fontsize=16, fontweight="bold", loc="left")
    fig.savefig(os.path.join(OUT, "센서_카메라_배치.png"), dpi=110, bbox_inches="tight", facecolor="white")


if __name__ == "__main__":
    block()
    placement()
    print("ok", os.listdir(OUT))
