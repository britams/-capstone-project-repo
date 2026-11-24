# -*- coding: utf-8 -*-
import json, os
import spec as SP

steps, ctxkeys = SP.compute()
main_final = ctxkeys["main"]
LATER = SP.TRAP + SP.COLLAR + SP.ENTRY + SP.ISO
main_nolater = [k for k in main_final if k not in LATER]

jobs = []
splits = []
GREY = None
for s in steps:
    focus = s["focus"] if s["focus"] else (s["new"] + s["done"])
    jobs.append(dict(name="S_" + s["id"], done=s["done"], new=s["new"], ctx=[], off=s["off"], d=s["d"], up=s["up"],
                     focus=focus, W=1500, H=1050, margin=s["margin"]))

# 부품 사진
thumb_keys = {}
for pid, p in SP.P.items():
    if p["kind"] != "cad" or not p["thumb"]:
        continue
    keys = []
    for i, (k, idx) in enumerate(p["thumb"]):
        if idx is None:
            keys.append(k)
        else:
            nk = "th_%s_%d" % (pid, i)
            splits.append([nk, k, idx])
            keys.append(nk)
    thumb_keys[pid] = keys
    colors = {}
    for i, (k, idx) in enumerate(p["thumb"]):
        colors[keys[i]] = SP.mat(k)
    d = (-1, 1, -0.8)
    if pid in ("deck101", "top105", "campl", "pipb", "grid300p", "floor304", "cup220", "estopplate", "p197", "arm226"):
        d = (-1, 0.8, -1.3)
    if pid in ("ya", "yb", "cp", "ym", "pipv", "falcs"):
        d = (-0.35, 1, -0.35)
    if pid in ("p217", "sp", "hv", "xn", "sv", "estopplate"):
        d = (-1, 0.35, -0.3)
    if pid in ("post610", "rail320", "bar156", "xrod", "yrod"):
        d = (-1, 1, -0.8)
    jobs.append(dict(name="T_" + pid, done=[], new=[], nat=keys, colors=colors, off={}, d=d, up=(0, 0, 1),
                     focus=keys, W=520, H=400, margin=1.10))

# 특별 그림
nat_all = {k: SP.mat(k) for k in main_final}
jobs.append(dict(name="X_cover", done=[], new=[], nat=main_final, colors=nat_all, off={}, d=(-1, 1, -0.55), up=(0, 0, 1),
                 focus=main_final, W=1300, H=1600, margin=1.04))
jobs.append(dict(name="X_demo", done=[], new=[], nat=main_nolater, colors=nat_all, off={}, d=(-1, 1, -0.55), up=(0, 0, 1),
                 focus=main_nolater, W=1300, H=1500, margin=1.04))
top_hide = SP.TOPP + SP.CAMU + SP.TOP_X + ["tb_top"]
nat_top = [k for k in main_nolater if k not in top_hide]
jobs.append(dict(name="X_top", done=[], new=[], nat=nat_top, colors=nat_all, off={}, d=(0, 0, -1), up=(0, 1, 0),
                 focus=nat_top, W=1400, H=1300, margin=1.06))
secs = {}
for s in steps:
    secs.setdefault(s["sec"], [])
    for k in s["new"]:
        if k not in secs[s["sec"]]:
            secs[s["sec"]].append(k)
for sec, keys in secs.items():
    base = main_final if sec == "G" else main_nolater
    jobs.append(dict(name="X_sec_" + sec, done=[k for k in base if k not in keys], new=[k for k in keys if k in base],
                     off={}, d=(-1, 1, -0.6), up=(0, 0, 1), focus=base, W=900, H=1100, margin=1.04))

out = dict(splits=splits, jobs=jobs)
os.makedirs("/mnt/user-data/outputs", exist_ok=True)
json.dump(out, open("/mnt/user-data/outputs/manual_jobs_v3.json", "w", encoding="utf-8"), ensure_ascii=False)
json.dump(thumb_keys, open("data/thumb_keys.json", "w", encoding="utf-8"), ensure_ascii=False)
print(len(jobs), "jobs", len(splits), "splits", os.path.getsize("/mnt/user-data/outputs/manual_jobs_v3.json"))
