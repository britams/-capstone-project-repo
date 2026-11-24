# -*- coding: utf-8 -*-
"""manual_body.pdf 뒤에 217 판 1:1 도안 (레포 design/2026-11-23_XY모터_NEMA17/...1대1도안.pdf)을 붙여 최종 PDF를 만든다.
사용: python3 merge_appendix.py <레포 경로> <출력 PDF>"""
import sys, os
from pypdf import PdfReader, PdfWriter
repo, out = sys.argv[1], sys.argv[2]
base = os.path.dirname(os.path.abspath(__file__))
body = PdfReader(os.path.join(base, "manual_body.pdf"))
app = PdfReader(os.path.join(repo, "design/2026-11-23_XY모터_NEMA17/2026-11-23_승준_판구멍_1대1도안.pdf"))
w = PdfWriter()
for p in list(body.pages) + list(app.pages):
    w.add_page(p)
w.add_metadata({"/Title": "말벌 자동 마킹 트랩 — 조립 설명서", "/Author": "팀 초벌 · 이승준 (Claude와 정리)",
                "/Subject": "레고식 단계별 조립 설명서 — FreeCAD D5g_full_SJ1123_플라스틱판_NEMA17 기준"})
with open(out, "wb") as f:
    w.write(f)
print(len(w.pages), "pages ->", out)
