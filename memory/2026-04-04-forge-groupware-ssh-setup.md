# Memory: Forge Groupware Deployment — SSH Key Setup

**Date:** 2026-04-04 09:13 UTC  
**Context:** GCP VM forge-mail-server SSH access setup

---

## SSH Key Generated for VM Access

**Key Type:** ED25519  
**Comment:** openclaw@titan  
**Private Key:** `~/.ssh/forge_groupware`  
**Public Key:**
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMGAIWkTAQB4qt2IAbxHSw2UwaAN7lEiVyazGdadFG9S openclaw@titan
```

---

## VM Status

- **VM:** forge-mail-server
- **Public IP:** 35.214.38.182
- **Tailscale IP:** 100.70.13.38
- **GCP Firewall:** 5 mail port rules created (25, 587, 143, 993, 80)
- **Serial Console Setup:** Already completed by user
- **SSH Access:** Pending — key needs to be added to VM

---

## Next Step Required

**Add SSH public key to VM via GCP Serial Console:**

```bash
mkdir -p /home/stu/.ssh
echo 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIMGAIWkTAQB4qt2IAbxHSw2UwaAN7lEiVyazGdadFG9S openclaw@titan' >> /home/stu/.ssh/authorized_keys
chown -R stu:stu /home/stu/.ssh
chmod 700 /home/stu/.ssh
chmod 600 /home/stu/.ssh/authorized_keys
```

**Once key is added, deployment can proceed via:**
```bash
ssh -i ~/.ssh/forge_groupware stu@35.214.38.182
```

---

## Related Files

- `projects/forge-groupware/VM-STATUS-REPORT-2026-04-04.md` — Full status report
- `projects/forge-groupware/serial-console-setup.sh` — VM setup script
- `projects/forge-groupware/test-deployment.sh` — Port connectivity tests
- `~/.ssh/forge_groupware` — Private key (keep secure)

---

## Deployment Readiness

| Step | Status |
|------|--------|
| VM Provisioned | ✅ Complete |
| DNS Configured | ✅ Complete |
| SendGrid Auth | ✅ Complete |
| GCP Firewall Rules | ✅ Complete (5 rules) |
| Serial Console Setup | ✅ Complete (user confirmed) |
| SSH Key Generated | ✅ Complete |
| SSH Key Added to VM | ⏳ Pending user action |
| Copy Deployment Files | ⏳ Blocked |
| Run deploy.sh | ⏳ Blocked |
| Service Tests | ⏳ Blocked |

---

*Saved to memory — awaiting SSH key addition to VM*