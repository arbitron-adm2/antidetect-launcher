#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright


async def test_plain_playwright():
    print("=" * 60)
    print("TESTING: plain playwright (BASELINE - no stealth)")
    print("=" * 60)
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080}
        )
        page = await context.new_page()
        
        try:
            print("\n[1] Testing browserscan.net...")
            await page.goto("https://www.browserscan.net/", timeout=60000)
            await asyncio.sleep(8)
            
            await page.screenshot(path="plain_playwright_browserscan.png")
            print("    Screenshot saved: plain_playwright_browserscan.png")
            
            print("\n[2] Testing CreepJS...")
            await page.goto("https://abrahamjuliot.github.io/creepjs/", timeout=60000)
            await asyncio.sleep(10)
            
            await page.screenshot(path="plain_playwright_creepjs.png")
            print("    Screenshot saved: plain_playwright_creepjs.png")
            
            print("\n[plain playwright] Test complete!")
            
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_plain_playwright())
