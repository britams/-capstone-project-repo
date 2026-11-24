import asyncio, sys
from playwright.async_api import async_playwright
async def main(src, out):
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/usr/bin/google-chrome", args=["--no-sandbox"])
        pg = await b.new_page()
        await pg.goto("file://" + src, wait_until="networkidle")
        await pg.wait_for_timeout(500)
        await pg.pdf(path=out, prefer_css_page_size=True, print_background=True)
        await b.close()
asyncio.run(main(sys.argv[1], sys.argv[2]))
