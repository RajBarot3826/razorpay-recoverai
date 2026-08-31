"""
RecoverAI — Automated HD Video Recording Script
Records a high-definition 1080p walkthrough of RecoverAI for the Razorpay Buildathon video submission.
"""

import asyncio
import os
import shutil
from playwright.async_api import async_playwright

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "recordings")
os.makedirs(OUTPUT_DIR, exist_ok=True)

async def record_demo():
    print("[*] Starting RecoverAI Automated HD Video Recording...")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--start-maximized", "--no-sandbox"]
        )
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=OUTPUT_DIR,
            record_video_size={"width": 1920, "height": 1080}
        )
        
        page = await context.new_page()
        
        # 1. Open Dashboard
        print("[1/11] Navigating to RecoverAI Dashboard...")
        await page.goto("http://localhost:3000", wait_until="networkidle")
        await page.wait_for_timeout(2000)
        
        # 2. Showcase Overview & Judge Presentation Presets
        print("[2/11] Overview & Running 'Festive Rush' Scenario (150 UPI Txns)...")
        await page.click('button:has-text("Festive Rush")')
        await page.wait_for_timeout(4500)
        
        # 3. Scroll Down Overview Table
        print("[3/11] Scrolling Overview Table & Metrics...")
        await page.mouse.wheel(0, 500)
        await page.wait_for_timeout(2500)
        await page.mouse.wheel(0, -500)
        await page.wait_for_timeout(1500)
        
        # 4. Open AI Recovery Sandbox
        print("[4/11] Demonstrating Live AI Sandbox & WhatsApp Nudge Preview...")
        await page.click('button:has-text("AI Sandbox")')
        await page.wait_for_timeout(2000)
        
        # Click scenario chip
        await page.click('button:has-text("UPI Timeout")')
        await page.wait_for_timeout(1000)
        
        # Execute AI Agents
        print("[5/11] Executing AI Recovery Agents live (Gemini + ML)...")
        await page.click('button:has-text("Execute AI Recovery Agents")')
        await page.wait_for_timeout(3500)
        
        # Click Live Razorpay Test Order Creator
        print("[6/11] Creating real test order via Razorpay API...")
        await page.click('button:has-text("Create Live Razorpay Test Order")')
        await page.wait_for_timeout(2500)
        
        # 5. Open Recovery Pipeline Architecture
        print("[7/11] Showing 6-Stage Recovery Pipeline Flow...")
        await page.click('button:has-text("Recovery Pipeline")')
        await page.wait_for_timeout(1500)
        await page.click('button:has-text("Simulate Live Pipeline Flow")')
        await page.wait_for_timeout(6500)
        
        # 6. Open Transactions Ledger
        print("[8/11] Exploring Transaction Ledger, Filters, and Audit Trail...")
        await page.click('button:has-text("Transactions")')
        await page.wait_for_timeout(1500)
        
        # Filter by Recovered Only
        await page.click('button:has-text("Recovered Only")')
        await page.wait_for_timeout(1500)
        
        # Expand first row audit trail
        rows = await page.query_selector_all('.tx-row-item')
        if rows:
            await rows[0].click()
            await page.wait_for_timeout(2500)
        
        # 7. Open Analytics & ROI Financial Calculator
        print("[9/11] Showcasing Merchant ROI Financial Impact Calculator...")
        await page.click('button:has-text("Analytics")')
        await page.wait_for_timeout(2000)
        await page.mouse.wheel(0, 600)
        await page.wait_for_timeout(1500)
        
        # Click ₹5 Crores preset
        await page.click('button:has-text("₹5 Crores")')
        await page.wait_for_timeout(2500)
        await page.mouse.wheel(0, -600)
        await page.wait_for_timeout(1000)
        
        # 8. Open Customer Profiles
        print("[10/11] Checking Customer Recovery Profiles...")
        await page.click('button:has-text("Customers")')
        await page.wait_for_timeout(1500)
        await page.click('button:has-text("Nudge Customer")')
        await page.wait_for_timeout(2000)
        
        # 9. Open Settings & Dark Theme Demonstration
        print("[11/11] Settings, Live API Pings & Dark Theme Toggle...")
        await page.click('button:has-text("Settings")')
        await page.wait_for_timeout(1500)
        
        # Ping Google Gemini
        ping_btns = await page.query_selector_all('button:has-text("Test Ping")')
        if len(ping_btns) > 1:
            await ping_btns[1].click()
            await page.wait_for_timeout(1500)
        
        # Toggle Dark Theme
        await page.click('.theme-toggle-btn')
        await page.wait_for_timeout(2500)
        
        # Return to Overview in Dark Theme
        await page.click('button:has-text("Overview")')
        await page.wait_for_timeout(3000)
        
        # Toggle back to Light Theme for closing shot
        await page.click('.theme-toggle-btn')
        await page.wait_for_timeout(2500)
        
        video_path = await page.video.path()
        print(f"[*] Raw video recorded to: {video_path}")
        
        await context.close()
        await browser.close()
        
        final_video_name = os.path.join(OUTPUT_DIR, "recoverai_demo_walkthrough.webm")
        if os.path.exists(video_path):
            shutil.copyfile(video_path, final_video_name)
            print(f"[SUCCESS] FINAL DEMO VIDEO READY AT: {final_video_name}")
            print(f"[*] Video Size: {os.path.getsize(final_video_name) / (1024*1024):.2f} MB")

if __name__ == "__main__":
    asyncio.run(record_demo())
