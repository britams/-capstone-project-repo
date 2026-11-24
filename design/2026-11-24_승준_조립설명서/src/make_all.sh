#!/bin/bash
# 그림(r/)이 있을 때 PDF 전체 다시 만들기.  사용: bash make_all.sh <레포 경로> <출력 PDF>
set -e
cd "$(dirname "$0")"
python3 build.py
python3 make_pdf.py "$PWD/manual.html" "$PWD/manual_body.pdf"
python3 check_overflow.py     # [] 이면 잘린 글·깨진 그림 없음
python3 merge_appendix.py "$1" "$2"
mkdir -p pv
python3 - <<'PY'
import subprocess, re, json
out = subprocess.run(['pdftotext', '-layout', 'manual_body.pdf', '-'], capture_output=True, text=True).stdout
idx = {}
for i, p in enumerate(out.split('\f')):
    m = re.match(r'\s*([A-H][0-9]{1,2})\s', p)
    if m: idx.setdefault(m.group(1), i + 1)
json.dump(idx, open('pv/idx.json', 'w'))
print('단계 → 쪽:', idx)
PY
