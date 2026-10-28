"""reliability_mc.py — 마킹 장치 신뢰성 몬테카를로 (CAP-AI-SJ-24)

질문: "설계대로 만들면 일벌 한 마리를 제대로(흉부 안전영역에) 마킹하는 확률이 95 % 이상인가?"
방법: 모르는 값(팁 굵기, 점 크기, 비전 오차, 자세, 잉크 묻음 …)은 범위로 두고 '세계' 하나마다 값을 뽑는다(인식 불확실성).
      세계마다 말벌 수천 마리를 흘려 성공률을 구하고, 세계들에 걸친 성공률 분포의 하위 5 %(P5)를 '보수적 신뢰성'으로 본다.
      P5 ≥ 0.95 → "가정 범위 안에서는 95 % 이상" (실물 시험으로 확인해야 하는 '예측값'이지 증명이 아님).

구성
  A. 기하 (한 번 시도): 격자 → 갈 수 있는 팁 위치 → 플래너(mark_planner)가 고른 점 → 실제 흉부 안전영역에 찍혔나
  B. 한 마리 과정: 자세(등 위/뒤집힘) → 뒤집힘 판별 → 기하 → 잉크 묻음(2번 찍기) → 점 확인(J4) → 실패면 바닥 내렸다 올려 다시 (최대 N회)
  C. 여왕벌 판별 (크기): 흉부 폭 측정 오차에 따른 '여왕벌을 일벌로 보고 놓아줌' 확률
  D. 시간: 구동 속도별 한 마리 처리 시간 (급이 제외)
  E. 실물 시험 표본 수: '95 % 이상, 신뢰수준 95 %'를 시험으로 보이려면 몇 마리가 필요한가

실행: python reliability_mc.py [--quick]  → reliability_results.json (+ 화면 요약)
"""
import json
import math
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'vision', 'scripts'))
from mark_planner import Grid, reachable_points, in_safe, point_success_prob  # noqa: E402

QUICK = '--quick' in sys.argv
N_WORLDS = 40 if QUICK else 120
N_GEOM = 120 if QUICK else 250
N_HORNETS = 1500 if QUICK else 4000

# ---------------------------------------------------------------- 범위 (근거·판정)
RANGES = dict(
    tip_d=(1.5, 2.5),        # 샤피 크리에이티브 불렛 팁이 격자 두께(1.5 mm) 깊이에서의 지름 [추측 — 실측 전, D6 d_tip 미정]
    dot_d=(1.0, 2.0),        # 찍힌 점 지름 [추측 — J9 시험 전]
    sig_v=(0.3, 0.7),        # 비전 흉부 중심 오차 σ (축당 mm). D6 e_xy ±1 mm ≈ 2σ [가능성 높음]
    sig_th=(5.0, 15.0),      # 흉부 방향 오차 σ (도) [추측]
    sig_sz=(0.05, 0.15),     # 크기 추정 오차 σ (mm) — 15.6 화소/mm에서 경계 ±1~2 화소 [가능성 높음]
    sig_mech=(0.1, 0.25),    # 기구 위치 오차 σ (mm): 나사 백래시·원점·마커 축 밀림 보정 후 [추측]
    kL=(0.65, 0.85),         # 흉부 길이 중 '찍어도 되는' 비율 [추측 — 날개 뿌리·소순판 피함]
    kW=(0.60, 0.80),         # 흉부 폭 중 '찍어도 되는' 비율 [추측]
    LW=(1.20, 1.45),         # 흉부 길이/폭 [추측 — 표본 실측으로 확정]
    p_up=(0.30, 0.80),       # 바닥으로 눌렀을 때 등이 격자 쪽(위)일 확률 [추측 — 아래 '행동' 참고, 가장 불확실]
    a_flip=(0.95, 0.995),    # 뒤집힘 판별 정확도 [가능성 높음 — 등/배 무늬가 확연함, 학습 필요]
    p_ink=(0.80, 0.97),      # 한 번 찍을 때 잉크가 묻을 확률 [추측 — J9 F_ink 시험 전]
    tpr=(0.90, 0.99),        # 점 확인 검출률 (J4 합성 96 %) [가능성 높음]
    fpr=(0.01, 0.05),        # 점 확인 오검출률 (J4 합성 2 %) [가능성 높음]
)
W_WORKER = (3.79, 4.49)       # 흉부 폭 (Pérez-de-Heredia 2017, D6) [확실 — 문헌]
W_QUEEN = (4.61, 4.87)


def draw_world(rng, overrides=None):
    w = {k: rng.uniform(*v) for k, v in RANGES.items()}
    if overrides:
        for k, v in overrides.items():
            w[k] = rng.uniform(*v) if isinstance(v, tuple) else v
    return w


# ---------------------------------------------------------------- A. 기하 한 번
def geom_attempt_rates(world, grid, rng, n=N_GEOM, p_min=0.5, k_dabs_points=1):
    """반환: (good, skip, mis, mean_bad_dots_if_k) — k_dabs_points>1이면 상위 k곳을 다 찍는 정책(승준 원안)의 결과도 셈."""
    pts = reachable_points(grid, world['tip_d'])
    r_dot = world['dot_d'] / 2
    good = skip = mis = 0
    bad_dots_total = 0
    good_any_total = 0
    for _ in range(n):
        tx, ty = rng.uniform(-12, 12, 2)
        th = rng.uniform(0, 2 * math.pi)
        wT = rng.uniform(*W_WORKER)
        LT = wT * world['LW']
        est = (tx + rng.normal(0, world['sig_v']), ty + rng.normal(0, world['sig_v']),
               th + math.radians(rng.normal(0, world['sig_th'])),
               LT + rng.normal(0, world['sig_sz']), wT + rng.normal(0, world['sig_sz']))
        unc = (world['sig_v'], math.radians(world['sig_th']), world['sig_sz'])
        near = pts[np.hypot(pts[:, 0] - est[0], pts[:, 1] - est[1]) <= 5.0]
        if len(near) == 0:
            skip += 1
            continue
        probs = point_success_prob(near, est, unc, world['kL'], world['kW'], r_dot, rng, n_samples=96,
                                   sigma_mech=world['sig_mech'])
        order = np.argsort(-probs)
        if k_dabs_points > 1:   # 원안: 확률 상위 k곳(서로 점 지름 이상 떨어진)을 모두 찍음
            chosen = []
            for i in order:
                if all(np.hypot(*(near[i] - near[j])) >= world['dot_d'] for j in chosen):
                    chosen.append(i)
                if len(chosen) == k_dabs_points:
                    break
            hit = 0
            for i in chosen:
                ax, ay = near[i] + rng.normal(0, world['sig_mech'], 2)
                ok = in_safe(ax, ay, tx, ty, th, LT, wT, world['kL'], world['kW'], r_dot)
                hit += int(ok)
            bad_dots_total += len(chosen) - hit
            good_any_total += int(hit > 0)
            continue
        i = order[0]
        if probs[i] < p_min:
            skip += 1
            continue
        ax, ay = near[i] + rng.normal(0, world['sig_mech'], 2)
        if in_safe(ax, ay, tx, ty, th, LT, wT, world['kL'], world['kW'], r_dot):
            good += 1
        else:
            mis += 1
    if k_dabs_points > 1:
        return dict(good_any=good_any_total / n, bad_dots_per_hornet=bad_dots_total / n)
    return dict(good=good / n, skip=skip / n, mis=mis / n)


# ---------------------------------------------------------------- B. 한 마리 과정
def hornet_process(world, geo, rng, n_max, n=N_HORNETS):
    """반환: success(제대로 찍힘·확인), mismark(안전영역 밖 점이 한 번이라도), false_done(점 없는데 찍혔다고 봄), attempts 평균
    (배열 연산: 말벌 n마리 × 시도 n_max회를 한꺼번에 뽑음)"""
    p_ink2 = 1 - (1 - world['p_ink']) ** 2          # 같은 자리 2번 찍기
    R = rng.random((5, n, n_max))
    up = R[0] < world['p_up']
    says_up = (R[1] < world['a_flip']) == up
    mark = says_up & up                              # 등 위를 맞게 봄 → 찍으러 감
    ventral = says_up & ~up                          # 뒤집혔는데 등 위로 봄 → 배에 찍음 (나쁨)
    skipg = R[2] < geo['skip']
    misg = (~skipg) & (R[2] < geo['skip'] + geo['mis'])
    goodg = ~(skipg | misg)
    dot = R[3] < p_ink2
    seen = R[4] < np.where(dot, world['tpr'], world['fpr'])
    terminal = mark & goodg & seen                   # '찍혔다'고 보고 끝냄
    bad = ventral | (mark & misg)
    has_t = terminal.any(axis=1)
    t = np.where(has_t, terminal.argmax(axis=1), n_max - 1)
    idx = np.arange(n_max)[None, :] <= t[:, None]
    success = has_t & dot[np.arange(n), t]
    false_done = has_t & ~dot[np.arange(n), t]
    mism = (bad & idx).any(axis=1)
    attempts = t + 1
    return dict(success=float(success.mean()), mismark=float(mism.mean()), false_done=float(false_done.mean()),
                attempts=float(attempts.mean()))


# ---------------------------------------------------------------- C. 여왕벌 판별
def queen_release_prob(sig, thr, n=200000, rng=None):
    rng = rng or np.random.default_rng(3)
    q = rng.uniform(*W_QUEEN, n) + rng.normal(0, sig, n)
    wk = rng.uniform(*W_WORKER, n) + rng.normal(0, sig, n)
    return dict(queen_called_worker=float((q < thr).mean()), worker_called_queen=float((wk >= thr).mean()))


# ---------------------------------------------------------------- D. 시간
def cycle_time(v_xy, v_floor, attempts, prepos=False, s_f=36.5, d_wait=58.0, d_hole=4.4, retract=10.0):
    t_first = 1.0 + 2.0 + s_f / v_floor + 1.0
    move = d_wait / v_xy
    if prepos:   # 바닥이 올라가는 동안 마커를 흉부 근처(카메라 시야 가장자리)까지 미리 보냄
        move = max(0.0, move - s_f / v_floor) + 10.0 / v_xy
    t_first += move + 1.6 + 1.0
    t_retry = 2 * retract / v_floor + 1.0 + d_hole / v_xy + 1.6 + 1.0
    return t_first + max(0.0, attempts - 1) * t_retry + 10.0   # + 방생 10 s (S4 가정), 급이 제외


# ---------------------------------------------------------------- E. 실물 시험 표본 수
def demo_n(R=0.95, C=0.95, failures=0):
    """이항: 실패 ≤ f로 R 이상을 신뢰수준 C로 보이는 최소 시행 수"""
    from math import comb
    n = failures + 1
    while True:
        p = sum(comb(n, i) * (1 - R) ** i * R ** (n - i) for i in range(failures + 1))
        if p <= 1 - C:
            return n
        n += 1


GOOD_V = dict(sig_v=(0.2, 0.4), sig_th=(3.0, 8.0))          # 키포인트 모델 + 격자를 자로 쓴 보정 [가능성 높음 — 시험 필요]
FINE = dict(tip_d=(0.8, 1.2), dot_d=(0.8, 1.5))              # 가는 팁 마커(약 1 mm) [추측 — 제품 선정 필요]
UP = dict(p_up=(0.6, 0.9))                                   # 아래 조명·위 어둡게로 바닥에 머물게 [추측 — 행동 시험 필요]
DESIGNS = {
    'D0 지금 (사각 격자 피치 4.4·구멍 3.0, 샤피 불렛)': dict(grid=Grid('square', 4.4, 3.0)),
    'D1 얇은 살 (사각 피치 3.8·구멍 3.0)': dict(grid=Grid('square', 3.8, 3.0)),
    'D2 슬롯 격자 (피치 4.0·틈 3.0, 리브 12 mm)': dict(grid=Grid('slot', 4.0, 3.0)),
    'D3 D2 + 비전 개선 (σ 0.2~0.4 mm)': dict(grid=Grid('slot', 4.0, 3.0), over=dict(**GOOD_V)),
    'D4 D3 + 등 위 자세 유도 (p_up 0.6~0.9)': dict(grid=Grid('slot', 4.0, 3.0), over=dict(**GOOD_V, **UP)),
    'D5 D4 + 가는 팁 (약 1 mm) + 틈 3.5 (피치 4.5)': dict(grid=Grid('slot', 4.5, 3.5), over=dict(**GOOD_V, **UP, **FINE)),
    'D6 사각 구멍 3.5 (피치 4.3) + 가는 팁 + 비전 개선 + 자세 유도': dict(grid=Grid('square', 4.3, 3.5), over=dict(**GOOD_V, **UP, **FINE)),
    'D7 D5 + 기준 p_min 0.3 (더 과감히 찍음)': dict(grid=Grid('slot', 4.5, 3.5), over=dict(**GOOD_V, **UP, **FINE), p_min=0.3),
    'D8 D5 + 기준 p_min 0.8 (확실할 때만 찍음)': dict(grid=Grid('slot', 4.5, 3.5), over=dict(**GOOD_V, **UP, **FINE), p_min=0.8),
}
N_MAX_LIST = [1, 2, 3, 4, 6, 8, 12]


def main():
    t0 = time.time()
    rng = np.random.default_rng(2026)
    res = dict(ranges=RANGES, n_worlds=N_WORLDS, n_geom=N_GEOM, n_hornets=N_HORNETS, designs={})
    for name, d in DESIGNS.items():
        rows = []
        for _ in range(N_WORLDS):
            wd = draw_world(rng, d.get('over'))
            geo = geom_attempt_rates(wd, d['grid'], rng, p_min=d.get('p_min', 0.5))
            row = dict(geo=geo)
            for nm in N_MAX_LIST:
                row[nm] = hornet_process(wd, geo, rng, nm, n=N_HORNETS // 2 if nm > 3 else N_HORNETS)
            rows.append(row)
        g = np.array([[r['geo']['good'], r['geo']['skip'], r['geo']['mis']] for r in rows])
        out = dict(geom_good_p50=float(np.median(g[:, 0])), geom_good_p5=float(np.percentile(g[:, 0], 5)),
                   geom_skip_p50=float(np.median(g[:, 1])), geom_mis_p50=float(np.median(g[:, 2])),
                   geom_mis_p95=float(np.percentile(g[:, 2], 95)), by_nmax={})
        for nm in N_MAX_LIST:
            s = np.array([r[nm]['success'] for r in rows])
            mm = np.array([r[nm]['mismark'] for r in rows])
            fd = np.array([r[nm]['false_done'] for r in rows])
            at = np.array([r[nm]['attempts'] for r in rows])
            out['by_nmax'][nm] = dict(success_p50=float(np.median(s)), success_p5=float(np.percentile(s, 5)),
                                      mismark_p50=float(np.median(mm)), mismark_p95=float(np.percentile(mm, 95)),
                                      false_done_p50=float(np.median(fd)), attempts_mean=float(at.mean()))
        out['n_for_p5_95'] = next((nm for nm in N_MAX_LIST if out['by_nmax'][nm]['success_p5'] >= 0.95), None)
        out['n_for_p50_95'] = next((nm for nm in N_MAX_LIST if out['by_nmax'][nm]['success_p50'] >= 0.95), None)
        res['designs'][name] = out
        print(f"{name}: 기하 1회 성공 중앙 {out['geom_good_p50']:.2f} (P5 {out['geom_good_p5']:.2f}), 건너뜀 {out['geom_skip_p50']:.2f}, 오마킹 {out['geom_mis_p50']:.3f}")
        for nm in N_MAX_LIST:
            b = out['by_nmax'][nm]
            print(f"   N≤{nm}: 성공 중앙 {b['success_p50']:.3f} / P5 {b['success_p5']:.3f}, 오마킹 {b['mismark_p50']:.3f} (P95 {b['mismark_p95']:.3f}), 평균 시도 {b['attempts_mean']:.2f}")
        print('   → 95 % 도달 시도 수: 중앙값 기준', out['n_for_p50_95'], '/ P5 기준', out['n_for_p5_95'])

    # 원안: 상위 k곳을 모두 찍기 — 흉부 밖 점 개수 (D0 격자)
    rng2 = np.random.default_rng(7)
    topk = {}
    for kk in (2, 3, 10, 20):
        vals = []
        for _ in range(max(10, N_WORLDS // 4)):
            wd = draw_world(rng2)
            vals.append(geom_attempt_rates(wd, Grid('square', 4.4, 3.0), rng2, n=80, k_dabs_points=kk))
        topk[kk] = dict(good_any=float(np.median([v['good_any'] for v in vals])),
                        bad_dots=float(np.median([v['bad_dots_per_hornet'] for v in vals])))
    res['top_k_policy_D0'] = topk
    print('원안(상위 k곳 모두 찍기, D0): 1곳이라도 맞을 확률·흉부 밖 점 개수', topk)

    # 여왕벌
    res['queen'] = {f'sigma {s} thr {t}': queen_release_prob(s, t) for s in (0.05, 0.1, 0.15) for t in (4.40, 4.50, 4.55)}
    print('여왕벌 → 일벌 오판 (σ, 경계):', {k: round(v['queen_called_worker'], 3) for k, v in res['queen'].items()})

    # 시간
    res['time'] = {}
    for label, vxy, vf, pre in (('28BYJ-48 (보유)', 1.96, 1.96, False), ('28BYJ-48 + 미리 이동', 1.96, 1.96, True),
                                ('NEMA17 X·Y + 28BYJ 바닥', 80.0, 1.96, True), ('NEMA17 X·Y·바닥', 80.0, 20.0, True)):
        res['time'][label] = {n: round(cycle_time(vxy, vf, n, pre), 1) for n in (1, 2, 3, 4)}
    print('한 마리 시간(급이 제외, 시도 1~4회):', res['time'])

    res['demo_trials'] = {f'실패 {f}회 허용': demo_n(0.95, 0.95, f) for f in (0, 1, 2)}
    print('95 %/95 % 실물 시험 마리 수:', res['demo_trials'])
    res['runtime_s'] = round(time.time() - t0, 1)
    with open(os.path.join(HERE, 'reliability_results.json'), 'w', encoding='utf-8') as fp:
        json.dump(res, fp, ensure_ascii=False, indent=1)
    print('끝', res['runtime_s'], 's')


if __name__ == '__main__':
    main()
