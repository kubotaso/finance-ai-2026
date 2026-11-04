"""FREDの画面を、ブラウザを自動で操作して撮るプログラム。

(2) FREDをウェブで使う の図1〜図5は、このプログラムで撮った画面です。
Playwright（ブラウザをプログラムから操作するライブラリ）で FRED のページを開き、
ボタンを押したり選択肢を選んだりしてから、画面を screenshots/ に保存します。

実行：python fred_screenshots.py
"""
import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

OUT = Path(__file__).resolve().parent / "screenshots"
FRED = "https://fred.stlouisfed.org"


# 系列ページを開き、表示が終わるまで5秒待つ。
async def open_series(ctx, series_id):
    page = await ctx.new_page()
    await page.goto(f"{FRED}/series/{series_id}",
                    wait_until="domcontentloaded", timeout=90000)
    await page.wait_for_timeout(5000)
    return page


# 図1：「consumer price index japan」の検索結果。
async def search_japan(ctx):
    page = await ctx.new_page()
    await page.goto(f"{FRED}/searchresults/?st=consumer%20price%20index%20japan",
                    wait_until="domcontentloaded", timeout=90000)
    await page.wait_for_timeout(6000)
    await page.screenshot(path=OUT / "fred_search_japan_cpi.png")
    await page.close()


# 図2：CPI（CPIAUCSL）の系列ページ。開いてそのまま撮る。
async def series_page(ctx):
    page = await open_series(ctx, "CPIAUCSL")
    await page.screenshot(path=OUT / "fred_series_page.png")
    await page.close()


# 図3：「Edit Graph」を押し、「Units」で「Percent Change from Year Ago」を選ぶ。
async def units_pc1(ctx):
    page = await open_series(ctx, "CPIAUCSL")
    await page.click("#edit-graph-button")
    await page.wait_for_timeout(2000)
    await page.select_option("#transformation",
                             label="Percent Change from Year Ago")
    await page.wait_for_timeout(5000)
    await page.screenshot(path=OUT / "fred_units_pc1.png")
    await page.close()


# 図4：実質GDP（GDPC1）に潜在GDP（GDPPOT）を加え、式 100*(a-b)/b を当てる。
async def formula_gap(ctx):
    page = await open_series(ctx, "GDPC1")
    await page.click("#edit-graph-button")
    await page.wait_for_timeout(2000)
    box = page.locator("input[id^='react-select'][id$='-input']").first
    await box.click()
    await box.fill("GDPPOT")            # 検索欄に系列IDを入力する
    await page.wait_for_timeout(4000)
    await page.keyboard.press("Enter")  # 候補を選ぶ
    await page.wait_for_timeout(1500)
    await page.click("#add-fred-series-button")
    await page.wait_for_timeout(3000)
    await page.fill("#formula-input", "100*(a-b)/b")
    await page.click("text=Apply Formula")
    await page.wait_for_timeout(5000)
    await page.screenshot(path=OUT / "fred_formula_gap.png")
    await page.close()


# 図5：「Download」を押して、メニューを開いた画面。
async def download_menu(ctx):
    page = await open_series(ctx, "CPIAUCSL")
    await page.click("#download-button")
    await page.wait_for_timeout(2000)
    await page.screenshot(path=OUT / "fred_download_menu.png")
    await page.close()


async def main():
    OUT.mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch()   # 画面に出さずにブラウザを動かす
        ctx = await browser.new_context(
            viewport={"width": 1400, "height": 1000}, locale="en-US")
        for shot in (search_japan, series_page, units_pc1, formula_gap,
                     download_menu):
            await shot(ctx)
            print("保存：", shot.__name__)
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
