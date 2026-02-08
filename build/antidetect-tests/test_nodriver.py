#!/usr/bin/env python3
"""Test nodriver on antidetect sites."""

import asyncio
import nodriver as uc


async def test_nodriver():
    """Test nodriver against detection sites."""
    print("=" * 60)
    print("TESTING: nodriver")
    print("=" * 60)
    
    browser = await uc.start(headless=False)
    
    try:
        # Test 1: BrowserScan
        print("\n[1] Testing browserscan.net...")
        page = await browser.get("https://www.browserscan.net/")
        await asyncio.sleep(8)
        
        # Take screenshot
        await page.save_screenshot("nodriver_browserscan.png")
        print("    Screenshot saved: nodriver_browserscan.png")
        
        # Test 2: CreepJS
        print("\n[2] Testing CreepJS...")
        page2 = await browser.get("https://abrahamjuliot.github.io/creepjs/")
        await asyncio.sleep(10)
        
        await page2.save_screenshot("nodriver_creepjs.png")
        print("    Screenshot saved: nodriver_creepjs.png")
        
        # Try to get some detection info
        try:
            # Get trust score from CreepJS
            trust_el = await page2.find("trust score", best_match=True)
            if trust_el:
                print(f"    CreepJS element found: {trust_el}")
        except Exception as e:
            print(f"    Could not extract trust score: {e}")
        
        print("\n[nodriver] Test complete!")
        
    finally:
        await browser.stop()


if __name__ == "__main__":
    asyncio.run(test_nodriver())
