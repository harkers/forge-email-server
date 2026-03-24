# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

---

## Infrastructure Learnings (2026-03-24)

### Forge Pipeline Deployment

**Host**: titan (192.168.10.80 LAN, 100.117.50.105 Tailscale)

**Images**:
- `localhost:5000/ddh-web:latest` (port 4173)
- `localhost:5000/ddh-api:latest` (port 4181)

**Nginx Config (Host Network Mode)**:
```nginx
location /api/ {
    proxy_pass http://192.168.10.80:4181/api/;  # Use explicit IP, not 'api' hostname
}
```

**Why**: Host network mode bypasses Docker DNS. Container uses host's DNS, not Docker's internal DNS. Using `api` hostname causes public DNS lookup → Cloudflare IPs → timeout.

**MCP Deployer Payload**:
```json
{
  "label": "ddh-web",
  "image": "localhost:5000/ddh-web:latest",
  "listen_port": 4173,
  "pull": false,
  "auto_approve": false,
  "env": { "VITE_API_URL": "http://192.168.10.80:4181" }
}
```

### Trilium ETAPI

**Host**: `http://192.168.10.5:8080`
**Auth**: Plain `Authorization: <token>` header (NOT Bearer)
**Token**: `x2aVxHZNg6HO_2GItibwJswEbIqRJDPerRW3LIk1MTquibcjXpVgvdHQ=`

**Calendar Structure**:
```
Calendar → 2026 → 03 - March → 24 - Tuesday → Daily Summary
```

### Quarto CLI

**Location**: `~/.local/bin/quarto`
**Version**: 1.4.557
**Bundled Deno**: `~/.local/quarto/bin/tools/x86_64/deno` (v2.3.1)

**Important**: Must use bundled Deno, not system Deno. System Deno (v2.7.7) incompatible with quarto.js.

### Vite API URL

**Rule**: Set `VITE_API_URL` at build time based on deployment target:
```bash
VITE_API_URL=http://192.168.10.80:4181 npm run build
```

Hardcoded URL bakes into static assets. `localhost` only works on titan.
