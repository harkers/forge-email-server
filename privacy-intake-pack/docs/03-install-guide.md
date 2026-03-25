# Installation Guide for titan

## 1. Create working directory

```bash
sudo mkdir -p /opt/privacy-intake
sudo chown -R stu:stu /opt/privacy-intake
```

Copy the contents of this pack into `/opt/privacy-intake`.

## 2. Review and set environment values

Edit:

```bash
cp .env.example .env
nano .env
```

Populate:
- database password
- Cloudflare tunnel token if using containerised cloudflared
- hostname
- secret key
- trusted origin values

## 3. Build and start stack

```bash
docker compose pull
docker compose build
docker compose up -d
```

## 4. Confirm containers

```bash
docker compose ps
docker compose logs -f app
docker compose logs -f worker
docker compose logs -f postgres
```

## 5. Validate database is internal-only

There should be no host-published postgres port.

```bash
docker ps --format 'table {{.Names}}\t{{.Ports}}'
ss -tulpn | grep 5432
```

Expected:
- no `0.0.0.0:5432`
- ideally no host binding at all for postgres

## 6. Cloudflare Tunnel

Choose one path:

### Option A: containerised cloudflared
Use the included service in `docker-compose.yml`

### Option B: host-managed cloudflared
Use the example systemd unit under `ops/systemd/`

If titan already uses host-managed cloudflared for other services, keep the same operational pattern for consistency.

## 7. Cloudflare Access

Create a self-hosted application for your chosen hostname and allow only your identity.
Recommended:
- one specific email identity
- short session duration
- no public bypass rule
- add service token only later if automation needs it

## 8. Health checks

```bash
curl -I http://127.0.0.1:18080/healthz
curl -I http://127.0.0.1:18080/
```

The app can be bound to localhost on the host for admin testing, but do not open it publicly.

## 9. Backups

Install the backup script from `ops/backup/backup-postgres.sh` and schedule it with cron or systemd timer.

## 10. First login and smoke test

- open the Cloudflare-protected hostname
- submit a test case
- confirm the case appears
- confirm task events are generated
- confirm the worker advances the task state
