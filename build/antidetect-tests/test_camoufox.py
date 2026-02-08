#!/usr/bin/env python3
import asyncio
from camoufox.async_api import AsyncCamoufox


async def test_camoufox():
    print("=" * 60)
    print("TESTING: camoufox")
    print("=" * 60)
    
    async with AsyncCamoufox(headless=False) as browser:
        page = await browser.new_page()
        
        try:
            print("\n[1] Testing browserscan.net...")
            await page.goto("https://www.browserscan.net/", timeout=60000)
            await asyncio.sleep(8)
            
            await page.screenshot(path="camoufox_browserscan.png")
            print("    Screenshot saved: camoufox_browserscan.png")
            
            print("\n[2] Testing CreepJS...")
            await page.goto("https://abrahamjuliot.github.io/creepjs/", timeout=60000)
            await asyncio.sleep(10)
            
            await page.screenshot(path="camoufox_creepjs.png")
            print("    Screenshot saved: camoufox_creepjs.png")
            
            print("\n[camoufox] Test complete!")
            
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_camoufox())
