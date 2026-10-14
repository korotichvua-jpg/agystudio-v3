import asyncio
import uuid
import httpx
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

BASE_URL = "http://127.0.0.1:8130"

@pytest.mark.asyncio
async def test_concurrent_sessions_wal_stress():
    """Stress-test SQLite WAL concurrency with 20 parallel session creations and reads."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        async def create_and_verify(idx: int):
            title = f"Stress Session {idx} - {uuid.uuid4().hex[:6]}"
            res = await client.post("/api/sessions", json={"title": title})
            assert res.status_code == 200, f"Session create failed with {res.status_code}: {res.text}"
            sess_id = res.json()["id"]

            # Query session immediately
            get_res = await client.get(f"/api/sessions/{sess_id}")
            assert get_res.status_code == 200
            assert get_res.json()["title"] == title

            # Add message
            msg_res = await client.get(f"/api/sessions/{sess_id}/messages")
            assert msg_res.status_code == 200
            return sess_id

        # Fire 20 parallel tasks concurrently
        results = await asyncio.gather(*[create_and_verify(i) for i in range(20)])
        assert len(results) == 20
        assert len(set(results)) == 20, "All session IDs must be unique"

        # Cleanup created stress sessions
        for sess_id in results:
            del_res = await client.delete(f"/api/sessions/{sess_id}")
            assert del_res.status_code == 200


@pytest.mark.asyncio
async def test_sse_stream_client_abort_resilience():
    """Verify server gracefully handles client aborting an SSE stream midway."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=10.0) as client:
        # Create a session
        s_res = await client.post("/api/sessions", json={"title": "SSE Abort Test"})
        sess_id = s_res.json()["id"]

        try:
            # Connect to stream but disconnect after reading the first chunk
            async with client.stream(
                "POST",
                "/api/query",
                json={
                    "session_id": sess_id,
                    "prompt": "/models",
                    "model": "auto-router",
                    "effort": "low"
                }
            ) as response:
                assert response.status_code == 200
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        # Immediate break simulating abrupt client disconnect / window close
                        break

            # Give server event loop a brief moment to process disconnect
            await asyncio.sleep(0.3)

            # Ensure backend remains completely healthy and session is accessible
            check_res = await client.get(f"/api/sessions/{sess_id}")
            assert check_res.status_code == 200
        finally:
            await client.delete(f"/api/sessions/{sess_id}")


@given(st.text(min_size=1, max_size=200))
@settings(max_examples=25, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture])
@pytest.mark.asyncio
async def test_property_based_router_preview_fuzz(prompt_text):
    """Property-based fuzzing: /api/router/preview must never 500 on arbitrary text."""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=5.0) as client:
        res = await client.post(
            "/api/router/preview",
            json={"prompt": prompt_text, "model": "auto-router", "effort": "low"}
        )
        assert res.status_code == 200
        data = res.json()
        assert "resolved_model" in data
        assert "tier" in data
        assert "estimated_tokens" in data
        assert data["estimated_tokens"] >= 1
