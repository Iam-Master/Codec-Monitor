# Changelog

All notable changes to Codec Monitor will be documented in this file.

## [1.1.1] - 2026-06-26

### Security
- Hardened CSV export against formula injection — all string fields now sanitized for leading `=`, `+`, `-`, `@`, tab, CR characters
- Added WebSocket Origin check mirroring the HTTP CSRF check — rejects cross-origin connections from untrusted browser tabs
- XSS hardening: codec color values are now validated before injection into style attributes
- Device-photo fetch now enforces HTTPS-only to public hosts (SSRF hardening against loopback/private/metadata IPs)

### Fixed
- Fixed potential KeyError in `list_known_devices()` when active device dict lacks a `name` key
- Photo fetch atomic-write now guarantees `.tmp` cleanup on failure (no orphan files)
- Frontend history trim now uses consistent MAX_HISTORY=2200 (was triggering at 2200 but keeping only 2000)

### Added
- `docs/API.md` — full HTTP endpoint and WebSocket message-type reference
- Troubleshooting section in README
- 50 backend pytest cases + 20 frontend node:test cases covering all security/robustness fixes
- `frontend/utils.js` — shared utility library (escapeHtml, safeColor, trimHistory)

### Docs
- Clarified architecture diagram timing labels (sleep intervals, not cycle durations)
- Added icon.ico/icon.png to project structure tree
- Added orientation header comment to app.js documenting page sections and WS protocol
- Corrected `start_minimized` description (it works — launches window hidden to tray)

## [1.1.0] - 2026-06-26

### Security
- Fixed a path-traversal bug in the `/photos/` HTTP handler that allowed reading arbitrary local files
- Escaped device/codec/output names before inserting them into the DOM, fixing a stored-XSS path via a maliciously-named Bluetooth device
- Removed a device-name-derived entry from the device-photo domain allowlist, and now validate the `Content-Type` of fetched images before saving them
- Added an Origin/Referer check to reject cross-origin `POST` requests to `/settings`, `/refresh`, and `/open-sound-settings` (CSRF mitigation)

### Fixed
- `since_hours` query parameter on `/history`, `/stats`, and `/export.csv` now returns `400 Bad Request` instead of crashing the request on invalid input
- Unified MAC address normalization into a single shared helper to prevent battery-cache lookups silently diverging
- Device/endpoint name matching now prefers the most specific match instead of the first substring match, fixing battery/codec misattribution between similarly-named paired devices (e.g. "Buds" vs "Buds Pro")
- Device photo downloads are now written atomically (temp file + rename) instead of directly to the final path
- All SQLite connections now use a busy timeout to avoid intermittent "database is locked" errors under concurrent requests

## [1.0.0] - 2026-06-24

### Features
- Real-time Bluetooth codec detection (SBC, AAC, aptX, aptX HD, LDAC) via Alt A2DP Driver registry
- Live dashboard with bitrate, sample rate, bit depth, battery, and connection uptime
- Session timeline chart (Chart.js) with configurable time ranges
- Connection stability tracking (disconnects and codec downgrades)
- Device management page with live connection status via Win32 CfgMgr32 API
- Codec comparison page with educational breakdowns
- Debounced alert system with toast notifications
- Export to CSV, Markdown, and PDF
- System tray integration (minimize to tray, background monitoring)
- Light and dark theme support
- Automatic device photo fetching via DuckDuckGo image search
- Settings page (poll interval, retention, notifications, tracked devices, close behavior)
- Single-instance enforcement with bring-to-front on re-launch
- PyInstaller packaging for standalone exe
- Inno Setup installer script
