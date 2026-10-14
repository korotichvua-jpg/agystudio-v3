import asyncio
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:8130"

def test_rapid_session_switch_race_invariant(page: Page):
    """Chaos test: Rapidly switch between multiple sessions to verify selectSessionCounter debounce."""
    page.goto(BASE_URL)
    page.wait_for_selector("#newSessionBtn")

    # Create 3 distinct sessions with identifiable titles
    for i in range(1, 4):
        page.evaluate(f"() => createNewSession('Race Session {i}')")
        page.wait_for_timeout(300)

    # Wait for session items to render
    page.wait_for_selector(".session-item", timeout=5000)
    session_items = page.locator(".session-item")
    count = session_items.count()
    assert count >= 3

    # Fast clicking loop (rapid race simulation)
    for _ in range(3):
        for idx in range(min(3, count)):
            session_items.nth(idx).click()
            page.wait_for_timeout(50)

    # Settle and verify stability
    page.wait_for_timeout(800)
    # Ensure currentSessionTitle is rendered and no unhandled error modal appears
    title_el = page.locator("#currentSessionTitle")
    expect(title_el).to_be_visible()


def test_rapid_input_typing_preflight_debounce(page: Page):
    """Verify typing rapidly with backspaces correctly settles the preflight router strip."""
    page.goto(BASE_URL)
    prompt_input = page.locator("#promptInput")
    preflight = page.locator("#preflightStrip")

    # Fast typing sequence
    prompt_input.press_sequentially("implement a distributed paxos state machine", delay=20)
    expect(preflight).to_be_visible(timeout=4000)
    expect(page.locator("#preflightModel")).to_contain_text("claude-opus-4-6-thinking")

    # Rapidly clear
    prompt_input.fill("")
    page.wait_for_timeout(300)
    expect(preflight).to_be_hidden()


def test_zero_reload_layout_lab_cycling(page: Page):
    """Verify instant zero-reload transitions through all multi-pane layout modes."""
    page.goto(BASE_URL)

    lab_btn = page.locator("#openLabModalBtn")
    expect(lab_btn).to_be_visible()

    modes = ["split", "arena", "dock", "grid"]
    for mode in modes:
        lab_btn.click()
        modal = page.locator("#layoutLabModal")
        expect(modal).to_be_visible()

        # Click the corresponding layout card
        page.locator(f"div[onclick*=\"applyCanvasModeFromLab('{mode}')\"]").click()
        expect(modal).to_be_hidden()
        page.wait_for_timeout(200)

        # Assert document body received the correct layout class
        has_class = page.evaluate(f"() => document.body.classList.contains('canvas-mode-{mode}')")
        assert has_class, f"Expected body to have canvas-mode-{mode}"

    # Return to standard view
    page.select_option("#canvasModeSelect", "standard")
    has_standard = page.evaluate("() => !document.body.classList.contains('canvas-mode-grid')")
    assert has_standard
