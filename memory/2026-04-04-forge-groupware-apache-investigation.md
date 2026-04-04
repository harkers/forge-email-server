# Forge Groupware - Apache Investigation - 2026-04-04

## Investigation Summary

**Date:** 2026-04-04 08:38 UTC
**Issue:** Apache processes running on ports 80/443, cannot stop via systemd

## Findings

### Apache Process Analysis

Apache processes found:
```
root      308704  0.0  0.0   2672  1076 ?        S    08:15   0:00 /bin/sh /usr/sbin/apache2ctl
root      308706  0.0  0.2  16768 11532 ?        S    08:15   0:00 /usr/sbin/apache2
www-data  308707  0.0  0.2 1221568 8096 ?        Sl   08:15   0:00 /usr/sbin/apache2
...
```

**Parent PIDs:**
- PID 38311: `/usr/bin/python3 /usr/bin/supervisord -c /opt/supervisord.conf`
- PID 308842: `containerd-shim-runc-v2` (Docker container)

### Source Investigation

1. **NOT a systemd service:**
   - `systemctl stop apache2` → "Unit apache2.service could not be found"
   - No apache2.service in /etc/systemd/system/

2. **NOT from Roundcube container:**
   - Roundcube uses bridge network (groupware-net)
   - Port mapping: 8080:80 only
   - Not using host networking

3. **Apache is serving:**
   ```
   $ curl http://localhost:80/
   → "Apache2 Debian Default Page: It works"
   ```

4. **Binaries not in standard location:**
   - `/usr/sbin/apache2ctl` - not found via `which`
   - `/usr/sbin/apache2` - not found via `which`
   - But processes are running with these paths

### Hypothesis

Apache is likely running from:
- A Docker container with `--network host` (binds directly to host ports)
- Or a legacy installation started via init script/rc.local
- Or supervisord-managed process from an older setup

**Cannot stop because:**
- No sudo access to run `killall apache2`
- No systemd service to stop
- Unknown parent process keeping it alive

## Security Assessment

| Risk Level | Finding |
|------------|---------|
| **Medium** | Apache exposed on 80/443 with unknown origin |
| **Low** | Serving only default Debian page (no sensitive data) |
| **Low** | GCP firewall may block external access anyway |
| **Mitigated** | Nginx on 8081/8443 provides alternative |

## Resolution Decision

**Chosen approach:** Work around Apache rather than fight it

1. ✅ Nginx running on 8081/8443 (working)
2. ✅ SOGo accessible via nginx
3. ⏳ Deploy Cloudflare Tunnel to localhost:8443
4. ⏳ Ignore Apache (will be bypassed entirely)

## Next Steps

1. Create Cloudflare Tunnel at one.dash.cloudflare.com
2. Deploy cloudflared container pointing to nginx
3. Configure public hostnames
4. **Later:** Investigate Apache source when convenient/sudo available

## Files Created

- `CLOUDFLARE_TUNNEL_WORKAROUND.md` - Detailed workaround guide
