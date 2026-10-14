import httpx
import pytest

BASE_URL = "http://127.0.0.1:8130"

@pytest.mark.asyncio
async def test_host_header_dns_rebinding_defense():
    """Security audit: Hostile host header must be rejected with HTTP 403."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        # Attack with spoofed external host header
        res = await client.get("/api/system/info", headers={"Host": "attacker.com:8130"})
        assert res.status_code == 403
        assert "Forbidden" in res.text


@pytest.mark.asyncio
async def test_anti_clickjacking_and_mime_headers():
    """Security audit: Verify anti-clickjacking and nosniff protection headers."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.get("/api/system/info")
        assert res.status_code == 200
        headers = res.headers
        assert headers.get("x-frame-options") == "DENY"
        assert headers.get("x-content-type-options") == "nosniff"
        assert "no-store" in headers.get("cache-control", "")


@pytest.mark.asyncio
async def test_podman_sandbox_drive_d_specs():
    """Security audit: Verify Drive D: sandbox configuration and profile specs."""
    async with httpx.AsyncClient(base_url=BASE_URL) as client:
        res = await client.get("/api/sandbox/status")
        assert res.status_code == 200
        data = res.json()

        assert "profiles" in data
        profile_ids = [p["id"] for p in data["profiles"]]
        assert "podman_secure_d" in profile_ids
        assert "podman_airgapped" in profile_ids

        # Verify airgapped profile specs
        airgapped = next(p for p in data["profiles"] if p["id"] == "podman_airgapped")
        assert "Offline" in airgapped["network"]
        assert "Air-Gapped" in airgapped["security"]


@pytest.mark.asyncio
async def test_sandbox_canary_execution_healthcheck():
    """Security audit: Run live sandbox canary probe and verify execution telemetry."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=25.0) as client:
        res = await client.post("/api/sandbox/test")
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert data["returncode"] == 0
        assert "PODMAN_SECURE_D_HEALTHY" in data["output"]
