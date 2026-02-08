#!/usr/bin/env python3
import asyncio
import json
from playwright.async_api import async_playwright
from playwright_stealth import Stealth


async def extract_browserscan_results(page):
    await asyncio.sleep(5)
    
    results = {}
    
    try:
        score_el = await page.query_selector(".score-value, .trust-score, [class*='score']")
        if score_el:
            results["score"] = await score_el.text_content()
    except:
        pass
    
    try:
        webdriver_el = await page.query_selector("text=WebDriver")
        if webdriver_el:
            parent = await webdriver_el.evaluate("el => el.closest('tr, .item, .row')?.textContent")
            results["webdriver"] = parent
    except:
        pass
    
    try:
        all_text = await page.evaluate("document.body.innerText")
        lines = all_text.split('\n')
        for line in lines[:50]:
            if any(x in line.lower() for x in ['score', 'detect', 'bot', 'automation', 'webdriver']):
                results.setdefault("relevant_lines", []).append(line.strip())
    except:
        pass
    
    return results


async def extract_creepjs_results(page):
    await asyncio.sleep(8)
    
    results = {}
    
    try:
        trust_el = await page.query_selector(".trust-score, [class*='trust'], #trust-score")
        if trust_el:
            results["trust_score"] = await trust_el.text_content()
    except:
        pass
    
    try:
        lies_el = await page.query_selector("text=lies")
        if lies_el:
            parent = await lies_el.evaluate("el => el.closest('.row, tr, div')?.textContent")
            results["lies"] = parent
    except:
        pass
    
    try:
        all_text = await page.evaluate("document.body.innerText")
        lines = all_text.split('\n')
        for line in lines[:100]:
            if any(x in line.lower() for x in ['trust', 'lie', 'bot', 'fingerprint', '%']):
                if len(line.strip()) < 200:
                    results.setdefault("relevant_lines", []).append(line.strip())
    except:
        pass
    
    return results


async def test_with_extraction(name, browser_launcher):
    print(f"\n{'='*60}")
    print(f"TESTING: {name}")
    print(f"{'='*60}")
    
    results = {"name": name, "browserscan": {}, "creepjs": {}}
    
    try:
        page = await browser_launcher()
        
        print("\n[1] Testing browserscan.net...")
        await page.goto("https://www.browserscan.net/", timeout=60000)
        results["browserscan"] = await extract_browserscan_results(page)
        print(f"    Results: {json.dumps(results['browserscan'], indent=2, default=str)[:500]}")
        
        print("\n[2] Testing CreepJS...")
        await page.goto("https://abrahamjuliot.github.io/creepjs/", timeout=60000)
        results["creepjs"] = await extract_creepjs_results(page)
        print(f"    Results: {json.dumps(results['creepjs'], indent=2, default=str)[:500]}")
        
    except Exception as e:
        results["error"] = str(e)
        print(f"    Error: {e}")
    
    return results


async def main():
    all_results = []
    
    stealth = Stealth()
    async with stealth.use_async(async_playwright()) as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        result = await test_with_extraction(
            "playwright-stealth",
            lambda: asyncio.coroutine(lambda: page)()
        )
        all_results.append(result)
        await browser.close()
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()
        
        print("\n" + "="*60)
        print("TESTING: plain playwright (BASELINE)")
        print("="*60)
        
        print("\n[1] Testing browserscan.net...")
        await page.goto("https://www.browserscan.net/", timeout=60000)
        bs_results = await extract_browserscan_results(page)
        print(f"    Results: {json.dumps(bs_results, indent=2, default=str)[:500]}")
        
        print("\n[2] Testing CreepJS...")
        await page.goto("https://abrahamjuliot.github.io/creepjs/", timeout=60000)
        cj_results = await extract_creepjs_results(page)
        print(f"    Results: {json.dumps(cj_results, indent=2, default=str)[:500]}")
        
        all_results.append({
            "name": "plain playwright",
            "browserscan": bs_results,
            "creepjs": cj_results
        })
        
        await browser.close()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    with open("test_results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print("\nResults saved to test_results.json")


if __name__ == "__main__":
    asyncio.run(main())
