#!/usr/bin/env python3
import asyncio
from playwright.async_api import async_playwright
from playwright_stealth import Stealth


async def test_playwright_stealth():
    print("=" * 60)
    print("TESTING: playwright-stealth")
    print("=" * 60)
    
    stealth = Stealth()
    
    async with stealth.use_async(async_playwright()) as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        
        try:
            print("\n[1] Testing browserscan.net...")
            await page.goto("https://www.browserscan.net/", timeout=60000)
            await asyncio.sleep(8)
            
            await page.screenshot(path="playwright_stealth_browserscan.png")
            print("    Screenshot saved: playwright_stealth_browserscan.png")
            
            print("\n[2] Testing CreepJS...")
            await page.goto("https://abrahamjuliot.github.io/creepjs/", timeout=60000)
            await asyncio.sleep(10)
            
            await page.screenshot(path="playwright_stealth_creepjs.png")
            print("    Screenshot saved: playwright_stealth_creepjs.png")
            
            print("\n[playwright-stealth] Test complete!")
            
        finally:
            await browser.close()


if __name__ == "__main__":
    asyncio.run(test_playwright_stealth())
