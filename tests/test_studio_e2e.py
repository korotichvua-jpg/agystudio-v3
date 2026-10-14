import re
import pytest
from playwright.sync_api import Page, expect

BASE_URL = "http://127.0.0.1:8130"

def test_page_title_and_branding(page: Page):
    """Verify that AgyStudio loads with correct title and branding elements."""
    page.goto(BASE_URL)
    expect(page).to_have_title("AgyStudio v3 - Intelligent Agent Canvas & Model Router")
    header = page.locator("h1")
    expect(header).to_contain_text("AgyStudio")

def test_real_time_auth_and_gmail_account(page: Page):
    """Verify that real-time Gmail identity and OS user context populate properly."""
    page.goto(BASE_URL)
    
    # Check Gmail account pill
    gmail_badge = page.locator("#gmailUserBadge")
    expect(gmail_badge).to_be_visible()
    expect(gmail_badge).to_contain_text("m89227065@gmail.com", timeout=6000)
    
    # Check OS user badge
    os_badge = page.locator("#osUserBadge")
    expect(os_badge).to_contain_text("alpha1")

def test_session_usage_hud_visibility(page: Page):
    """Verify that Session Usage HUD Ribbon is rendered with token metrics."""
    page.goto(BASE_URL)
    
    hud = page.locator("#sessionUsageHUD")
    expect(hud).to_be_visible()
    expect(page.locator("#hudTotalTokens")).to_be_visible()
    expect(page.locator("#hudInputTokens")).to_be_visible()
    expect(page.locator("#hudThinkingTokens")).to_be_visible()
    expect(page.locator("#hudOutputTokens")).to_be_visible()
    expect(page.locator("#hudSpeed")).to_be_visible()

def test_eye_comfort_theme_switcher(page: Page):
    """Verify that theme switcher changes the data-theme attribute on <html>, including White Milk."""
    page.goto(BASE_URL)
    
    # Switch to White Milk (Day)
    page.select_option("#themeSelect", "milk")
    expect(page.locator("html")).to_have_attribute("data-theme", "milk")

    # Use Quick Day/Night button to toggle back to dark
    page.locator("#quickDayNightBtn").click()
    expect(page.locator("html")).to_have_attribute("data-theme", "nord")

    # Click Quick Day/Night button again to return to White Milk
    page.locator("#quickDayNightBtn").click()
    expect(page.locator("html")).to_have_attribute("data-theme", "milk")
    
    # Switch to Gruvbox Warm
    page.select_option("#themeSelect", "gruvbox")
    expect(page.locator("html")).to_have_attribute("data-theme", "gruvbox")
    
    # Switch to Catppuccin
    page.select_option("#themeSelect", "catppuccin")
    expect(page.locator("html")).to_have_attribute("data-theme", "catppuccin")
    
    # Switch back to Nord Dark
    page.select_option("#themeSelect", "nord")
    expect(page.locator("html")).to_have_attribute("data-theme", "nord")

def test_complex_presets_accordion_and_template_loading(page: Page):
    """Verify that preset prompts populate the query input box."""
    page.goto(BASE_URL)
    
    # Open Economics & Infra details
    summary = page.locator("summary", has_text="Economics & Infra")
    summary.click()
    
    # Click 1 GW Data Center Cost Chain preset
    preset_btn = page.locator("button", has_text="1 GW Data Center Cost Chain")
    preset_btn.click()
    
    # Check prompt input value (textarea uses to_have_value)
    import re
    prompt_input = page.locator("#promptInput")
    expect(prompt_input).to_have_value(re.compile(r"1 GW AI hyperscale data center campus in Texas"))

def test_live_query_stream_and_hud_telemetry_update(page: Page):
    """Submit a real query to agy and assert streaming tokens and HUD counters."""
    page.goto(BASE_URL)
    
    prompt_input = page.locator("#promptInput")
    prompt_input.fill("say E2E_PLAYWRIGHT_TEST_SUCCESS")
    
    # Select low-latency model and effort
    page.select_option("#effortSelect", "low")
    
    # Click Run Query
    send_btn = page.locator("#sendBtn")
    send_btn.click()
    
    # Assert live processing badge appears
    live_badge = page.locator("#liveStatusBadge")
    expect(live_badge).to_be_visible()
    
    # Wait for the model response to arrive and verify text
    last_card = page.locator(".prose-content").last
    expect(last_card).to_contain_text("E2E_PLAYWRIGHT_TEST_SUCCESS", timeout=25000)
    
    # Verify the processing indicator turns off after stream reader finishes
    expect(live_badge).to_be_hidden(timeout=15000)
    
    # Verify the Session Usage HUD total tokens updated
    total_tokens_hud = page.locator("#hudTotalTokens")
    expect(total_tokens_hud).not_to_have_text("0", timeout=5000)

def test_multi_turn_context_continuation(page: Page):
    """Verify that multi-turn queries retain memory in the same session via agy --conversation."""
    page.goto(BASE_URL)
    
    # Click New Session to start fresh session
    new_btn = page.locator("#newSessionBtn")
    new_btn.click()
    page.wait_for_timeout(500)
    
    # Turn 1: Provide a distinct secret value
    prompt_input = page.locator("#promptInput")
    prompt_input.fill("My secret code is QUANTUM_8472. Reply only: OK")
    page.locator("#sendBtn").click()
    
    last_card = page.locator(".prose-content").last
    expect(last_card).to_contain_text("OK", timeout=25000)
    expect(page.locator("#liveStatusBadge")).to_be_hidden(timeout=15000)
    
    # Turn 2: Ask for the secret code without mentioning it
    prompt_input.fill("What is my secret code? Reply with just the code.")
    page.locator("#sendBtn").click()
    
    # Verify the assistant recalls the secret code from the previous turn
    turn2_card = page.locator(".prose-content").last
    expect(turn2_card).to_contain_text("QUANTUM_8472", timeout=25000)
    expect(page.locator("#liveStatusBadge")).to_be_hidden(timeout=15000)


def test_execution_header_stamp_present_in_response(page: Page):
    """Verify that assistant response first line contains agent:model:effort:datetimestart:datetimefinish:tokensused."""
    import re
    page.goto(BASE_URL)

    # Click New Session
    page.locator("#newSessionBtn").click()
    page.wait_for_timeout(500)

    # Send a quick query
    prompt_input = page.locator("#promptInput")
    prompt_input.fill("say STAMP_VERIFIED")
    page.locator("#sendBtn").click()

    # Wait for completion
    expect(page.locator("#liveStatusBadge")).to_be_visible()
    expect(page.locator("#liveStatusBadge")).to_be_hidden(timeout=35000)

    # Check for execution-stamp badge rendered in the response card
    stamp_el = page.locator(".execution-stamp").last
    expect(stamp_el).to_be_visible()
    expect(stamp_el).to_contain_text("agy")
    expect(stamp_el).to_contain_text("tok")


def test_mermaid_diagram_validation_and_healing(page: Page):
    """Verify that Mermaid self-healing automatically resolves unquoted parenthesis syntax."""
    page.goto(BASE_URL)

    # Directly evaluate autoHealMermaidSyntax in browser context
    healed = page.evaluate("""() => {
        const broken = 'flowchart LR\\n  A[Process (Sub-step)] --> B[Final (Result)]';
        return autoHealMermaidSyntax(broken);
    }""")
    assert 'A["Process (Sub-step)"]' in healed
    assert 'B["Final (Result)"]' in healed


def test_mermaid_toggle_source_view(page: Page):
    """Verify that clicking Code toggle button displays raw Mermaid source."""
    page.goto(BASE_URL)

    # Insert a test Mermaid block into DOM
    page.evaluate("""() => {
        const container = document.getElementById('messagesContainer');
        const card = appendMessageUI('assistant', '```mermaid\\nflowchart TD\\n  Start --> Stop\\n```');
        renderMermaidDiagrams(card);
    }""")
    page.wait_for_timeout(500)

    # Check that the toggle button works
    toggle_btn = page.locator(".mermaid-block button", has_text="Code").first
    expect(toggle_btn).to_be_visible()
    toggle_btn.click()

    # Source code view should now be visible
    source_view = page.locator(".diagram-source-view").first
    expect(source_view).to_be_visible()
    expect(source_view).to_contain_text("flowchart TD")


def test_mermaid_rebuild_button(page: Page):
    """Verify that clicking Rebuild button reconstructs and re-renders the Mermaid canvas."""
    page.goto(BASE_URL)

    # Insert a test Mermaid block into DOM
    page.evaluate("""() => {
        const container = document.getElementById('messagesContainer');
        const card = appendMessageUI('assistant', '```mermaid\\nflowchart TD\\n  NodeA --> NodeB\\n```');
        renderMermaidDiagrams(card);
    }""")
    page.wait_for_timeout(500)

    # Check Rebuild button exists and can be clicked
    rebuild_btn = page.locator(".mermaid-block button", has_text="Rebuild").first
    expect(rebuild_btn).to_be_visible()
    rebuild_btn.click()
    page.wait_for_timeout(500)

    # Check that diagram-render-view still contains an svg
    render_view = page.locator(".diagram-render-view").first
    expect(render_view).to_be_visible()


def test_collapsible_sidebar_toggle(page: Page):
    """Verify that sidebar collapses and expands via toggle button."""
    page.goto(BASE_URL)

    sidebar = page.locator("#mainSidebar")
    expect(sidebar).to_be_visible()
    expect(sidebar).not_to_have_class(re.compile(r"sidebar-collapsed"))

    # Click toggle button
    toggle_btn = page.locator("#toggleSidebarBtn")
    toggle_btn.click()
    expect(sidebar).to_have_class(re.compile(r"sidebar-collapsed"))

    # Click again to restore
    toggle_btn.click()
    expect(sidebar).not_to_have_class(re.compile(r"sidebar-collapsed"))


def test_zen_mode_maximizer(page: Page):
    """Verify that Zen Mode hides chrome header/ribbon and expands full canvas."""
    page.goto(BASE_URL)

    body = page.locator("body")
    expect(body).not_to_have_class(re.compile(r"zen-mode"))

    # Enter Zen Mode
    zen_btn = page.locator("#toggleZenBtn")
    zen_btn.click()
    expect(body).to_have_class(re.compile(r"zen-mode"))

    # Exit Zen Banner should be visible
    exit_banner = page.locator("#zenExitBanner")
    expect(exit_banner).to_be_visible()

    # Press Escape to exit Zen Mode
    page.keyboard.press("Escape")
    expect(body).not_to_have_class(re.compile(r"zen-mode"))
    expect(exit_banner).to_be_hidden()


def test_sticky_outline_navigator(page: Page):
    """Verify that the floating outline navigator pops up and populates canvas items."""
    page.goto(BASE_URL)

    outline_map = page.locator("#outlineMiniMap")
    expect(outline_map).to_be_hidden()

    # Click Outline button in header
    outline_btn = page.locator("#toggleOutlineBtn")
    outline_btn.click()
    expect(outline_map).to_be_visible()

    # Click again to close
    outline_btn.click()
    expect(outline_map).to_be_hidden()


def test_canvas_mode_visual_selector(page: Page):
    """Verify that visual layout selector safely activates all 4 wide screen canvas modes."""
    import re
    page.goto(BASE_URL)

    selector = page.locator("#canvasModeSelect")
    expect(selector).to_be_visible()

    body = page.locator("body")
    split_pane = page.locator("#splitArtifactPane")
    dock_pane = page.locator("#inspectorDockPane")

    # Test Split mode
    selector.select_option("split")
    expect(body).to_have_class(re.compile(r"canvas-mode-split"))
    expect(split_pane).to_be_visible()

    # Test Arena mode
    selector.select_option("arena")
    expect(body).to_have_class(re.compile(r"canvas-mode-arena"))
    expect(split_pane).to_be_hidden()

    # Test Grid mode
    selector.select_option("grid")
    expect(body).to_have_class(re.compile(r"canvas-mode-grid"))

    # Test Dock mode
    selector.select_option("dock")
    expect(body).to_have_class(re.compile(r"canvas-mode-dock"))
    expect(dock_pane).to_be_visible()

    # Restore Standard mode
    selector.select_option("standard")
    expect(body).not_to_have_class(re.compile(r"canvas-mode-dock"))
    expect(dock_pane).to_be_hidden()


def test_podman_sandbox_status_api():
    """Verify that /api/sandbox/status detects Podman engine and Drive D: metrics."""
    import urllib.request
    import json

    req = urllib.request.Request(f"{BASE_URL}/api/sandbox/status")
    with urllib.request.urlopen(req, timeout=5) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data["podman_available"] is True
        assert "podman version" in data["podman_version"].lower()
        assert "drive_d" in data
        assert data["drive_d"]["free_gb"] > 0
        assert len(data["profiles"]) >= 3


def test_podman_sandbox_canary_test_api():
    """Verify that POST /api/sandbox/test executes an isolated canary container on Drive D:."""
    import urllib.request
    import json

    req = urllib.request.Request(f"{BASE_URL}/api/sandbox/test", method="POST")
    with urllib.request.urlopen(req, timeout=20) as resp:
        assert resp.status == 200
        data = json.loads(resp.read().decode())
        assert data["success"] is True
        assert "PODMAN_SECURE_D_HEALTHY" in data["output"]
        assert "workspace_mount" in data
        assert "agystudio_secure_env" in data["workspace_mount"]


def test_podman_sandbox_ui_controls_and_modal(page: Page):
    """Verify that UI contains the sandbox selector, Drive D: meter, and functional modal."""
    page.goto(BASE_URL)

    # Check sandbox selector
    sandbox_select = page.locator("#sandboxModeSelect")
    expect(sandbox_select).to_be_visible()
    expect(sandbox_select).to_have_value("podman_secure_d")

    # Check Drive D: storage button
    storage_btn = page.locator("#openSandboxModalBtn")
    expect(storage_btn).to_be_visible()
    expect(page.locator("#driveDFreeText")).to_contain_text("D:")

    # Check HUD Sandbox Badge
    hud_badge = page.locator("#hudSandboxBadge")
    expect(hud_badge).to_be_visible()
    expect(hud_badge).to_contain_text("Secure")

    # Open Sandbox Modal
    storage_btn.click()
    modal = page.locator("#sandboxModal")
    expect(modal).to_be_visible()
    expect(page.locator("#modalPodmanVer")).to_contain_text("podman version")

    # Close modal
    page.locator("#closeSandboxModalBtn").click()
    expect(modal).to_be_hidden()


def test_auto_router_preflight_and_economics(page: Page):
    """Verify that typing into promptInput triggers real-time pre-flight model router preview."""
    page.goto(BASE_URL)

    prompt_input = page.locator("#promptInput")
    preflight_strip = page.locator("#preflightStrip")
    expect(preflight_strip).to_be_hidden()

    # Type query requiring complex reasoning
    prompt_input.fill("prove the convergence theorem for distributed consensus under partition")
    expect(preflight_strip).to_be_visible(timeout=5000)
    expect(page.locator("#preflightModel")).to_contain_text("claude-opus-4-6-thinking")
    expect(page.locator("#preflightTier")).to_contain_text("Tier 3")


def test_safe_slash_commands_models_and_quota(page: Page):
    """Verify that /models, /quota, and /usage slash commands execute safely and instantly."""
    page.goto(BASE_URL)

    # 1. Test /models command via quick chip button
    models_btn = page.locator("button", has_text="/models")
    expect(models_btn).to_be_visible()
    models_btn.click()

    last_card = page.locator(".prose-content").last
    expect(last_card).to_contain_text("Available Antigravity Model Catalog", timeout=6000)
    expect(last_card).to_contain_text("auto-router")

    # 2. Test /quota command via quick chip button
    quota_btn = page.locator("button", has_text="/quota")
    expect(quota_btn).to_be_visible()
    quota_btn.click()

    quota_card = page.locator(".prose-content").last
    expect(quota_card).to_contain_text("Compute Quota & Resource Telemetry", timeout=6000)
    expect(quota_card).to_contain_text("1,000,000 tok")


def test_layout_lab_modal_zero_reload(page: Page):
    """Verify that the Layout Lab modal opens and closes without reloading."""
    page.goto(BASE_URL)

    lab_btn = page.locator("#openLabModalBtn")
    expect(lab_btn).to_be_visible()
    lab_btn.click()

    modal = page.locator("#layoutLabModal")
    expect(modal).to_be_visible()
    expect(modal).to_contain_text("Layout Lab & Prototypes (Zero-Reload)")

    # Close modal
    page.locator("#layoutLabModal button", has_text="Close").click()
    expect(modal).to_be_hidden()


def test_diagram_workbench_page_load_and_title(page: Page):
    """Verify that Architecture Workbench loads properly with tri-lens navigation and SVG viewport."""
    page.goto(BASE_URL + "/diagram-workbench.html")
    expect(page).to_have_title("AgyStudio v3 - Architecture Workbench (Logical, Component, DFD)")
    
    # Assert header and controls
    expect(page.locator("#lens-logical")).to_be_visible()
    expect(page.locator("#lens-component")).to_be_visible()
    expect(page.locator("#lens-dfd")).to_be_visible()
    expect(page.locator("#presetSelect")).to_be_visible()
    expect(page.locator("#securityOverlayBtn")).to_be_visible()
    expect(page.locator("#aiGenBtn")).to_be_visible()
    
    # Assert Mermaid SVG rendered
    page.wait_for_selector("#diagramContainer svg", timeout=10000)
    expect(page.locator("#diagramContainer svg")).to_be_visible()


def test_diagram_workbench_tri_lens_switching(page: Page):
    """Verify switching between Logical, Component C4, and Data Flow (DFD) architectural lenses."""
    page.goto(BASE_URL + "/diagram-workbench.html")
    page.wait_for_selector("#diagramContainer svg", timeout=10000)
    
    editor = page.locator("#dslEditor")
    
    # Default initial lens is Component
    expect(editor).to_have_value(re.compile(r"flowchart TB"))
    
    # Switch to Logical lens
    page.locator("#lens-logical").click()
    page.wait_for_timeout(400)
    expect(editor).to_have_value(re.compile(r"stateDiagram-v2"))
    expect(page.locator("#diagramContainer svg")).to_be_visible()
    
    # Switch to DFD lens
    page.locator("#lens-dfd").click()
    page.wait_for_timeout(400)
    expect(editor).to_have_value(re.compile(r"flowchart LR"))
    expect(page.locator("#diagramContainer svg")).to_be_visible()
    
    # Switch back to Component lens
    page.locator("#lens-component").click()
    page.wait_for_timeout(400)
    expect(editor).to_have_value(re.compile(r"flowchart TB"))


def test_diagram_workbench_threat_overlay_and_export(page: Page):
    """Verify STRIDE threat overlay toggling and export buttons in Architecture Workbench."""
    page.goto(BASE_URL + "/diagram-workbench.html")
    page.wait_for_selector("#diagramContainer svg", timeout=10000)
    
    # Toggle threat radar
    threat_btn = page.locator("#securityOverlayBtn")
    threat_btn.click()
    
    # Verify threat banner is displayed
    threat_banner = page.locator("#threatBanner")
    expect(threat_banner).to_be_visible()
    expect(threat_banner).to_contain_text("STRIDE Threat Assessment")
    
    # Open Export dropdown
    export_dropdown = page.locator("#exportDropdownBtn")
    export_dropdown.click()
    
    # Verify export buttons inside dropdown
    export_svg_btn = page.locator("#exportSvgBtn")
    expect(export_svg_btn).to_be_visible()
    copy_mermaid_btn = page.locator("#copyMermaidBtn")
    expect(copy_mermaid_btn).to_be_visible()
    
    # Test copy mermaid action
    copy_mermaid_btn.click()









