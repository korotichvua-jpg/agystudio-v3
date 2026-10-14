---
project_name: "agystudio-v3"
display_name: "AgyStudio v3"
port: 8130
type: "Web Project / FastAPI Engine"
route_path: "D:/projects/agystudio-v3"
last_build: "2026-10-14 18:00:00"
upstream: "127.0.0.1:8130"
caddy_server_key: "srv_8130"
description: "AgyStudio v3 local engineering canvas with intelligent cognitive model router and agent telemetry."
---

# Deployment Memo: AgyStudio v3

- **Target URL**: http://127.0.0.1:8130
- **Repository URL**: [https://github.com/korotichvua-jpg/agystudio-v3](https://github.com/korotichvua-jpg/agystudio-v3)
- **Project Classification**: Web Project / FastAPI Engine
- **Local Root Folder**: `D:/projects/agystudio-v3`
- **Pipeline Handlers**: `vars`, `reverse_proxy`, `file_server` (hardened against `.env*` and `.git` leakage)
- **Deployment Status**: Active & Monitored by caddy-manager (:62225)
- **Overview**: Local quantitative modeling and engineering studio powered by agy agent CLI engine and intelligent cognitive tiering.
