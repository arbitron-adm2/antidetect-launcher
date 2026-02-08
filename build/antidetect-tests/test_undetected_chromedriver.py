#!/usr/bin/env python3
"""Test undetected-chromedriver on antidetect sites."""

import time
import undetected_chromedriver as uc


def test_undetected_chromedriver():
    """Test undetected-chromedriver against detection sites."""
    print("=" * 60)
    print("TESTING: undetected-chromedriver")
    print("=" * 60)
    
    options = uc.ChromeOptions()
    options.add_argument("--window-size=1920,1080")
    
    driver = uc.Chrome(options=options, headless=False)
    
    try:
        # Test 1: BrowserScan
        print("\n[1] Testing browserscan.net...")
        driver.get("https://www.browserscan.net/")
        time.sleep(8)
        
        driver.save_screenshot("uc_browserscan.png")
        print("    Screenshot saved: uc_browserscan.png")
        
        # Test 2: CreepJS
        print("\n[2] Testing CreepJS...")
        driver.get("https://abrahamjuliot.github.io/creepjs/")
        time.sleep(10)
        
        driver.save_screenshot("uc_creepjs.png")
        print("    Screenshot saved: uc_creepjs.png")
        
        print("\n[undetected-chromedriver] Test complete!")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    test_undetected_chromedriver()
