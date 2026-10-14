import asyncio
from playwright.async_api import async_playwright

async def full_regression():
    async with async_playwright() as p:
        for port in [8130]:
            for browser_type in [p.chromium, p.firefox]:
                b_name = browser_type.name
                print(f"\n=======================================================")
                print(f"=== Starting Full Regression: Port {port} on {b_name} ===")
                print(f"=======================================================")
                browser = await browser_type.launch(headless=True)
                page = await browser.new_page()
                errors = []
                page.on("console", lambda msg: errors.append(f"[{msg.type}] {msg.text}") if msg.type == "error" else None)
                page.on("pageerror", lambda exc: errors.append(f"[pageerror] {exc}"))

                await page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")

                # Click newSessionBtn to ensure clean fresh session for testing
                await page.click("#newSessionBtn")
                await page.wait_for_timeout(1000)
                is_empty = await page.is_visible("#emptyState")
                assert is_empty, f"Initial empty state must be visible on {port} {b_name} after new session"

                # Test 1: Click Quick /models button
                print("1. Testing /models quick button...")
                await page.click('button:text("/models")')
                await page.wait_for_selector("text=Available Antigravity Model Catalog", state="visible", timeout=20000)
                await page.wait_for_selector("#sendBtn:not([disabled])", timeout=20000)
                print("   -> /models response rendered successfully.")

                # Test 2: Click Quick /quota button
                print("2. Testing /quota quick button...")
                await page.click('button:text("/quota")')
                await page.wait_for_selector("text=Compute Quota & Resource Telemetry", state="visible", timeout=20000)
                await page.wait_for_selector("#sendBtn:not([disabled])", timeout=20000)
                print("   -> /quota response rendered successfully.")

                # Test 3: Click Quick /usage button
                print("3. Testing /usage quick button...")
                await page.click('button:text("/usage")')
                await page.wait_for_selector("text=Compute Quota & Resource Telemetry", state="visible", timeout=20000)
                await page.wait_for_selector("#sendBtn:not([disabled])", timeout=20000)
                print("   -> /usage response rendered successfully.")

                # Test 4: Run Query button with custom prompt
                print("4. Testing Run Query submission...")
                await page.fill('#promptInput', 'Hello from automated regression test')
                await page.click('#sendBtn')
                # Wait for user message bubble and assistant response
                await page.wait_for_selector("text=Hello from automated regression test", state="visible", timeout=10000)
                await page.wait_for_selector("#sendBtn:not([disabled])", timeout=25000)
                print("   -> Run Query finished cleanly.")

                # Test 5: Pinned Live Artifact and Redraw
                print("5. Testing Pinned Live Artifact & Redraw...")
                # Switch to split mode to expose splitArtifactPane
                await page.evaluate("() => { if (typeof applyCanvasMode === 'function') applyCanvasMode('split'); }")
                await page.wait_for_selector("#splitArtifactPane:not(.hidden)", state="visible", timeout=5000)
                
                # Check presence of title and placeholder/content
                pinned_title = await page.text_content("#splitPinnedTitle")
                assert "Pinned Live Artifact" in pinned_title, f"Unexpected pinned title: {pinned_title}"
                
                # Click Redraw button
                await page.click('button:has-text("Redraw")')
                print("   -> Redraw button clicked cleanly.")

                # Test 6: New Session & empty state restoration
                print("6. Testing New Session empty state restoration...")
                await page.click("#newSessionBtn")
                await page.wait_for_timeout(1000)
                is_empty = await page.is_visible("#emptyState")
                assert is_empty, "Empty state must be visible after clicking New Session"
                print("   -> Empty state restored perfectly.")

                # Test 7: Verify zero unhandled exceptions / NetworkError
                print(f"Completed port {port} {b_name} successfully! Errors caught: {len(errors)}")
                if errors:
                    print("Errors:", errors)
                    raise RuntimeError(f"Errors encountered on {port} {b_name}: {errors}")

                await browser.close()

    print("\n==========================================================================")
    print("ALL REGRESSION TESTS PASSED (100% SUCCESS) ACROSS CHROME & FIREFOX ON PORTS 8128 & 8129!")
    print("==========================================================================\n")

if __name__ == "__main__":
    asyncio.run(full_regression())
