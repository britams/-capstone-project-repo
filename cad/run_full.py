# -*- coding: utf-8 -*-
"""전체 수정 + 검사 한 번에 — 하네스 (서현 11/18 03:40 '하네스 엔지니어링', CAP-AI-62). 설명: docs/00_AI작업_하네스.md 4·5장
  python.exe cad/run_full.py <이름> [먼저 돌릴.py ...]   cwd = cad, FreeCAD 1.1 bin\\python.exe로 (GUI FreeCAD 안에서 돌리지 말 것)
  python.exe cad/run_full.py --check                     돌리지 않고 지금 결과 파일만 판정
차례: 먼저 돌릴 스크립트 → recolor → full_merge → _make_no → _add_feed → 그림 → 나사 검사 → 움직임 검사 (MOTION_ALL=1, PEN_LIFT=12.1).
하나씩 차례로 (같이 돌리면 말없이 죽은 적 있음, 11/17). 옛 _chain_*.py (PC에만 있음)를 대신함.
끝나면 split/_harness_<이름>.json = PASS/FAIL + 이유: 움직임 새 겹침·대기 겹침 0 · 나사 겹침은 알려진 것만 · meviy 판 끝단 ≥ 1 mm · 결과 파일이 이번에 새로 써졌는지"""
import json, os, subprocess, sys, time
C = os.path.dirname(os.path.abspath(__file__)); S = os.path.join(C, "split")
FC = r"C:\Program Files\FreeCAD 1.1\bin\freecad.exe"
KNOWN = {frozenset(("218s_SK8_bolts", "217s_x_motor_screws"))}       # 11/17부터 늘 있는 옛 겹침 1건


def load(n):
    p = os.path.join(S, n)
    return (json.load(open(p, encoding="utf-8")), os.path.getmtime(p)) if os.path.exists(p) else (None, 0)


def judge(t0=0):
    why = []
    m, tm = load("_motion_penup.json")
    if m is None or tm < t0:
        why.append("움직임 검사 결과가 이번에 안 써짐 (죽었는지 확인)")
    elif not m.get("ok") or m.get("motion_new") or m.get("park_overlaps"):
        why.append("움직임: 새 겹침 %d · 대기 겹침 %d %s" % (len(m.get("motion_new") or []), len(m.get("park_overlaps") or []), (m.get("error") or "")[-200:]))
    s, ts = load("_screw_clash.json")
    if s is None or ts < t0:
        why.append("나사 검사 결과가 이번에 안 써짐 (죽었는지 확인)")
    else:
        new = [c for c in s.get("clash", []) if frozenset((c[0].split(" ")[0], c[2].split(" ")[0])) not in KNOWN]
        if new or "error" in s:
            why.append("나사 새 겹침: " + "; ".join("%s ↔ %s" % (c[0][:40], c[2][:40]) for c in new) + (s.get("error") or "")[-200:])
    v, tv = load("_meviy.json")
    if v is not None:
        bad = [k for k, x in v.items() if isinstance(x, dict) and (x["bad"] or not x["valid"] or x["min_edge"] < 1.0)]
        if bad or not v.get("ok"):
            why.append("meviy 판 끝단 < 1 mm 또는 모양 깨짐: " + (", ".join(bad) or (v.get("error") or "")[-200:]))
    return dict(result="FAIL" if why else "PASS", why=why,
                files={"_motion_penup.json": time.ctime(tm), "_screw_clash.json": time.ctime(ts), "_meviy.json": time.ctime(tv) if tv else None})


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a or a[0] == "--check":
        r = judge(); print(json.dumps(r, ensure_ascii=False, indent=1)); sys.exit(0 if r["result"] == "PASS" else 1)
    tag, pre = a[0], a[1:]
    miss = [x for x in pre if not os.path.exists(os.path.join(C, x))]
    if miss:                                                          # 없는 파일을 freecad.exe에 주면 빈 창이 하나 뜨고 안 닫힘 (11/18)
        sys.exit("없는 스크립트: %s — git pull 됐는지 확인" % miss)
    t0, log = time.time(), []
    LOG = os.path.join(S, "_harness_%s.log" % tag)

    def run(script, env=None):
        t = time.time(); rc = subprocess.run([FC, script], cwd=C, env=env).returncode
        log.append([script, rc, round(time.time() - t)])
        open(LOG, "w", encoding="utf-8").write(json.dumps(log, ensure_ascii=False))

    for x in pre + ["recolor.py", "full_merge.py", "_make_no.py", "_add_feed.py"]:
        run(x)
    run("D5g_render.py", dict(os.environ, D5G_FILE=os.path.join(C, "D5g_full.FCStd")))
    run("check_screw_clash.py")
    run("s2_motion_v3_check.py", dict(os.environ, MOTION_ALL="1", PEN_LIFT="12.1"))
    r = judge(t0); r.update(tag=tag, steps=log, minutes=round((time.time() - t0) / 60, 1))
    json.dump(r, open(os.path.join(S, "_harness_%s.json" % tag), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
