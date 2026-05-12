"""Capture portfolio screenshots for docs/screenshots/.

Assumes:
  - Patched backend running at http://127.0.0.1:8100 (backend/_europa_run.py)
  - Frontend vite dev server at http://127.0.0.1:5773

Not part of the shipped product. Lives in scripts/ alongside the demo runner.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from playwright.async_api import async_playwright

FRONTEND = "http://127.0.0.1:5773"
BACKEND = "http://127.0.0.1:8100"
OUT = Path(__file__).resolve().parent.parent / "docs" / "screenshots"
DEMO_EMAIL = "demo@europa.dev"
DEMO_PASSWORD = "demo123"
QUERY = "Compare major cloud providers on 2026 enterprise AI governance offerings."


async def login(page):
    await page.goto(f"{FRONTEND}/")
    await page.wait_for_selector('input[type="email"]')
    await page.fill('input[type="email"]', DEMO_EMAIL)
    await page.fill('input[type="password"]', DEMO_PASSWORD)
    await page.click('button[type="submit"]')
    await page.wait_for_url("**/dashboard")


async def shot_section(page, locator_text, out_name, *, top_padding=20):
    """Screenshot a section starting near the top of viewport, anchored on heading."""
    heading = page.get_by_text(locator_text, exact=False).first
    await heading.evaluate(
        "(el, pad) => { const r = el.getBoundingClientRect(); "
        "window.scrollBy({top: r.top - pad, behavior: 'instant'}); }",
        top_padding,
    )
    await page.wait_for_timeout(300)
    await page.screenshot(path=str(OUT / out_name), full_page=False)
    print(f"captured {out_name}")


async def main():
    OUT.mkdir(parents=True, exist_ok=True)
    async with async_playwright() as pw:
        browser = await pw.chromium.launch()
        context = await browser.new_context(viewport={"width": 1440, "height": 900})
        page = await context.new_page()

        await login(page)

        # 1. Research Query page (full page so all controls visible)
        await page.goto(f"{FRONTEND}/research")
        await page.wait_for_selector("textarea")
        await page.fill("textarea", QUERY)
        # Open advanced controls (allow/deny domains)
        for b in await page.query_selector_all('button[type="button"]'):
            text = (await b.inner_text() or "").strip().lower()
            if "advanced" in text:
                await b.click()
                break
        await page.wait_for_timeout(400)
        # NOTE: leave allow_domains empty so the sample-data sources
        # (which use *.test domains for honest mock data) are not filtered out.
        # Deny list is harmless to populate.
        deny_input = await page.query_selector('input[placeholder*="reddit.com"]')
        if deny_input:
            await deny_input.fill("reddit.com, quora.com")
        await page.screenshot(path=str(OUT / "01-query-input.png"), full_page=True)
        print("captured 01-query-input.png")

        # Submit
        await page.click('button[type="submit"]')
        await page.wait_for_url("**/results/**", timeout=180_000)
        await page.wait_for_selector("text=Research plan", timeout=60_000)
        await page.wait_for_timeout(1000)

        # Helper: clip-screenshot the section starting at an h2 heading.
        # We compute the heading's absolute position, then take a viewport-sized
        # clip from the FULL page screenshot (no scrolling needed).
        async def shot_h2(text, out_name, height=900, top_padding=12):
            box = await page.evaluate(
                """(t) => {
                    const h = Array.from(document.querySelectorAll('h2'))
                        .find(x => x.textContent.trim() === t);
                    if (!h) return null;
                    const parent = h.closest('section') || h.parentElement;
                    const rect = parent.getBoundingClientRect();
                    return {
                        top: rect.top + window.scrollY,
                        left: rect.left + window.scrollX,
                        width: rect.width,
                    };
                }""",
                text,
            )
            if not box:
                raise RuntimeError(f"H2 not found: {text!r}")
            # Take a full-page screenshot then crop with Pillow.
            from io import BytesIO

            from PIL import Image
            png = await page.screenshot(full_page=True)
            img = Image.open(BytesIO(png))
            top = max(0, int(box["top"]) - top_padding)
            crop = img.crop((0, top, img.width, min(img.height, top + height)))
            crop.save(OUT / out_name)
            print(f"captured {out_name}")

        # 4. Final cited report — top of results page (executive summary, findings,
        # metrics, evidence table). Tall crop from a full-page screenshot so all of
        # the trust-and-evidence panels are visible without needing to scroll.
        from io import BytesIO

        from PIL import Image
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(300)
        png4 = await page.screenshot(full_page=True)
        img4 = Image.open(BytesIO(png4))
        img4.crop((0, 0, img4.width, min(img4.height, 1700))).save(
            OUT / "04-final-cited-report.png"
        )
        print("captured 04-final-cited-report.png")

        # 2. Task decomposition — the "Research plan" section (sub-questions)
        await shot_h2("Research plan", "02-task-decomposition.png", height=500)

        # 3. Source cards — the "Evidence table" panel renders source rows with
        # credibility scores and domains. Pair it with "Source citations" below
        # by capturing a taller crop.
        await shot_h2("Evidence table", "03-source-cards.png", height=900)

        # 6. Execution timeline — the per-stage "Execution trace" section
        await shot_h2("Execution trace", "06-execution-timeline.png", height=900)

        # 5. FastAPI Swagger docs — tall crop from full page so endpoints list is
        # legible without the whole schema appendix dominating the image.
        await page.goto(f"{BACKEND}/docs")
        await page.wait_for_selector(".swagger-ui", timeout=15_000)
        await page.wait_for_selector(".opblock", timeout=15_000)
        await page.wait_for_timeout(1500)
        png5 = await page.screenshot(full_page=True)
        img5 = Image.open(BytesIO(png5))
        img5.crop((0, 0, img5.width, min(img5.height, 1400))).save(
            OUT / "05-api-docs.png"
        )
        print("captured 05-api-docs.png")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
