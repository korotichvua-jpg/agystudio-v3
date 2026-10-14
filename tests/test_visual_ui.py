import os
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:8130"
SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "..", "screenshots")

@pytest.fixture(autouse=True)
def setup_dirs():
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def test_visual_standard_canvas_and_themes(page: Page):
    """Capture baseline visual UI appearance across themes in Standard view."""
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(BASE_URL)
    page.wait_for_selector("#promptInput")

    # 1. Nord Dark Theme
    page.select_option("#themeSelect", "nord")
    page.wait_for_timeout(300)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_canvas_nord_dark.png"), full_page=True)

    # 2. White Milk (Day) Theme
    page.select_option("#themeSelect", "milk")
    page.wait_for_timeout(300)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_canvas_white_milk.png"), full_page=True)

    # 3. Gruvbox Warm Theme
    page.select_option("#themeSelect", "gruvbox")
    page.wait_for_timeout(300)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "03_canvas_gruvbox_warm.png"), full_page=True)

    # 4. Catppuccin Mocha Theme
    page.select_option("#themeSelect", "catppuccin")
    page.wait_for_timeout(300)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "04_canvas_catppuccin.png"), full_page=True)


def test_visual_zero_reload_layouts(page: Page):
    """Capture multi-pane zero-reload wide screen layouts."""
    page.set_viewport_size({"width": 1600, "height": 950})
    page.goto(BASE_URL)
    page.select_option("#themeSelect", "nord")
    page.wait_for_timeout(300)

    # 1. Split View (Live Diagram / Artifact Pane)
    page.select_option("#canvasModeSelect", "split")
    page.wait_for_timeout(300)
    expect(page.locator("#splitArtifactPane")).to_be_visible()
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "05_layout_split_canvas.png"))

    # 2. Inspector Dock View
    page.select_option("#canvasModeSelect", "dock")
    page.wait_for_timeout(300)
    expect(page.locator("#inspectorDockPane")).to_be_visible()
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "06_layout_inspector_dock.png"))

    # 3. Zero-Reload Layout Lab Overlay Modal
    lab_btn = page.locator("#openLabModalBtn")
    lab_btn.click()
    page.wait_for_timeout(300)
    expect(page.locator("#layoutLabModal")).to_be_visible()
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "07_modal_layout_lab.png"))

    # Close modal
    page.locator("#layoutLabModal button", has_text="Close").click()
    expect(page.locator("#layoutLabModal")).to_be_hidden()


def test_visual_slash_commands_and_math_rendering(page: Page):
    """Capture rendered output of /models and /quota slash commands."""
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(BASE_URL)
    page.select_option("#themeSelect", "nord")

    # Click /models quick command button
    page.locator("button", has_text="/models").click()
    expect(page.locator(".prose-content").last).to_contain_text("Available Antigravity Model Catalog", timeout=6000)
    page.wait_for_timeout(500)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "08_command_models_catalog.png"))

    # Click /quota quick command button
    page.locator("button", has_text="/quota").click()
    expect(page.locator(".prose-content").last).to_contain_text("Compute Quota & Resource Telemetry", timeout=6000)
    page.wait_for_timeout(500)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "09_command_quota_telemetry.png"))


def test_visual_podman_sandbox_modal(page: Page):
    """Capture Podman Drive D: Secure Sandbox Modal with security specs."""
    page.set_viewport_size({"width": 1440, "height": 900})
    page.goto(BASE_URL)
    page.select_option("#themeSelect", "nord")

    # Open sandbox modal
    page.locator("#openSandboxModalBtn").click()
    modal = page.locator("#sandboxModal")
    expect(modal).to_be_visible()
    page.wait_for_timeout(400)
    page.screenshot(path=os.path.join(SCREENSHOT_DIR, "10_modal_podman_sandbox.png"))
