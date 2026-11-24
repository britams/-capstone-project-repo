import asyncio, json
from playwright.async_api import async_playwright
JS = r"""
() => {
  const out = [];
  const pages = document.querySelectorAll('section.page');
  pages.forEach((pg, i) => {
    const pr = pg.getBoundingClientRect();
    const limit = pr.bottom - 9 * 3.7795; // 아래 여백 9mm
    let worst = 0, who = '';
    pg.querySelectorAll('*').forEach(el => {
      if (el.closest('.foot') || el.closest('svg')) return;
      const r = el.getBoundingClientRect();
      if (r.height === 0) return;
      const over = r.bottom - limit;
      if (over > worst) { worst = over; who = el.className || el.tagName; }
      const overR = r.right - (pr.right - 9 * 3.7795);
      if (overR > 2 && !(el.closest('.ov'))) { if (overR > worst) { worst = overR; who = 'RIGHT:' + (el.className || el.tagName); } }
    });
    const imgs = [...pg.querySelectorAll('img')].filter(im => !im.complete || im.naturalWidth === 0).map(im => im.src);
    if (worst > 1 || imgs.length) out.push({page: i + 1, over_px: Math.round(worst), who, broken: imgs});
  });
  return out;
}
"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1123, "height": 794})
        await pg.goto("file://" + __import__("os").path.join(__import__("os").path.dirname(__import__("os").path.abspath(__file__)), "manual.html"), wait_until="networkidle")
        await pg.emulate_media(media="print")
        res = await pg.evaluate(JS)
        print(json.dumps(res, ensure_ascii=False, indent=0))
        await b.close()
asyncio.run(main())
