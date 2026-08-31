import asyncio
import os
from playwright.async_api import async_playwright

async def audit_all_pages():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.on("console", lambda msg: errors.append(f"Console error: {msg.text}") if msg.type == "error" else None)

        print("[*] Navigating to http://localhost:3000 ...")
        await page.goto("http://localhost:3000", wait_until="networkidle")
        await asyncio.sleep(1)

        tabs = ["overview", "sandbox", "transactions", "pipeline", "analytics", "customers", "insights", "alerts", "settings"]
        
        for tab in tabs:
            print(f"[*] Testing tab: {tab}")
            nav_btn = page.locator(f"button.nav-item:has-text('{tab.capitalize()}')").first
            if await nav_btn.count() == 0:
                nav_btn = page.locator(f"button.nav-item").filter(has_text=tab)
            if await nav_btn.count() > 0:
                await nav_btn.click()
                await asyncio.sleep(0.5)
                # Take screenshot
                os.makedirs("audit_screenshots", exist_ok=True)
                await page.screenshot(path=f"audit_screenshots/tab_{tab}.png", full_page=True)
                print(f"    [OK] Captured tab_{tab}.png")

        # Test Theme Toggle
        print("[*] Testing Theme Toggle...")
        theme_btn = page.locator(".theme-toggle-btn")
        if await theme_btn.count() > 0:
            await theme_btn.click()
            await asyncio.sleep(0.5)
            await page.screenshot(path="audit_screenshots/theme_dark.png", full_page=True)
            await theme_btn.click()
            await asyncio.sleep(0.5)

        # Test Notifications Popover
        print("[*] Testing Notifications Popover...")
        notif_btn = page.locator(".notif-btn")
        if await notif_btn.count() > 0:
            await notif_btn.click()
            await asyncio.sleep(0.5)
            await page.screenshot(path="audit_screenshots/notifications_popover.png")
            await notif_btn.click()

        # Test Sandbox Diagnostic Run
        print("[*] Testing Sandbox Form & Diagnostics...")
        await page.locator("button.nav-item:has-text('Sandbox')").click()
        await asyncio.sleep(0.5)
        run_diag_btn = page.locator("button.gradient-run-btn:has-text('Run Diagnostics')")
        if await run_diag_btn.count() > 0:
            await run_diag_btn.click()
            await asyncio.sleep(1)
            await page.screenshot(path="audit_screenshots/sandbox_diagnosed.png", full_page=True)

        # Test Pipeline Simulation
        print("[*] Testing Pipeline Simulator...")
        await page.locator("button.nav-item:has-text('Recovery Pipeline')").click()
        await asyncio.sleep(0.5)
        sim_btn = page.locator("button:has-text('Simulate Pipeline Flow')")
        if await sim_btn.count() > 0:
            await sim_btn.click()
            await asyncio.sleep(2)
            await page.screenshot(path="audit_screenshots/pipeline_simulating.png", full_page=True)

        # Test Analytics ROI Slider
        print("[*] Testing Analytics ROI Preset Buttons...")
        await page.locator("button.nav-item:has-text('Analytics')").click()
        await asyncio.sleep(0.5)
        preset_5cr = page.locator("button.roi-preset-btn:has-text('₹5 Crores')")
        if await preset_5cr.count() > 0:
            await preset_5cr.click()
            await asyncio.sleep(0.5)
            await page.screenshot(path="audit_screenshots/analytics_5cr.png", full_page=True)

        # Test Transactions Search and Filter
        print("[*] Testing Transactions Filtering & Expanded Row...")
        await page.locator("button.nav-item:has-text('Transactions')").click()
        await asyncio.sleep(0.5)
        card_filter = page.locator("button.filter-pill-btn:has-text('UPI')")
        if await card_filter.count() > 0:
            await card_filter.click()
            await asyncio.sleep(0.5)
        # Expand row
        first_row = page.locator("tr.tx-row-item").first
        if await first_row.count() > 0:
            await first_row.click()
            await asyncio.sleep(0.5)
            await page.screenshot(path="audit_screenshots/transactions_expanded.png", full_page=True)

        await browser.close()
        
        print("\n" + "="*60)
        print(f"AUDIT COMPLETED WITH {len(errors)} CONSOLE/PAGE ERRORS.")
        for e in errors:
            print("  Error:", e)
        print("="*60)

if __name__ == "__main__":
    asyncio.run(audit_all_pages())
