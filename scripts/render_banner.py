"""Render animated banner.gif from banner.svg using Playwright."""

from __future__ import annotations

import asyncio
import io
from pathlib import Path

from PIL import Image
from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
SVG_PATH = ROOT / "assets" / "banner.svg"
GIF_PATH = ROOT / "assets" / "banner.gif"
PNG_PATH = ROOT / "assets" / "banner.png"

FRAMES = 36
FRAME_MS = 120  # 4.3s loop


async def main() -> None:
    svg = SVG_PATH.read_text(encoding="utf-8")
    html = (
        "<!DOCTYPE html><html><head><meta charset='utf-8'></head>"
        "<body style='margin:0;padding:0;background:#030303;overflow:hidden'>"
        f"{svg}</body></html>"
    )

    frames: list[Image.Image] = []
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        page = await browser.new_page(viewport={"width": 1200, "height": 280, "deviceScaleFactor": 2})
        await page.set_content(html, wait_until="load")
        await page.wait_for_timeout(150)
        for _ in range(FRAMES):
            png_bytes = await page.screenshot(type="png")
            frames.append(Image.open(io.BytesIO(png_bytes)).convert("P", palette=Image.ADAPTIVE, colors=128))
            await page.wait_for_timeout(FRAME_MS)
        await browser.close()

    GIF_PATH.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        GIF_PATH,
        save_all=True,
        append_images=frames[1:],
        duration=FRAME_MS,
        loop=0,
        optimize=True,
    )
    frames[FRAMES // 2].save(PNG_PATH, format="PNG")
    print(f"Wrote {GIF_PATH} ({len(frames)} frames)")
    print(f"Wrote {PNG_PATH} (static fallback)")


if __name__ == "__main__":
    asyncio.run(main())
