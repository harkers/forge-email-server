# Homepage Label Standard

Every Dockerized service on Titan should include Homepage labels for automatic dashboard discovery.

## Required Labels

```yaml
labels:
  - homepage.group=<GroupName>
  - homepage.name=<ServiceName>
  - homepage.icon=<IconReference>
  - homepage.href=<ServiceURL>
  - homepage.description=<OneLineDescription>
```

## Optional Labels

```yaml
labels:
  - homepage.weight=<NumericOrder>
  - homepage.target=_blank|_self
  - homepage.widget.type=<WidgetType>
  - homepage.widget.url=<WidgetDataURL>
```

## Icon Sources

Homepage supports multiple icon sources:

- **Simple Icons**: `si-<name>` (e.g., `si-github`, `si-docker`)
- **Material Design Icons**: `mdi-<name>` (e.g., `mdi-robot-outline`)
- **Dashboard Icons**: place PNG files in `/app/public/icons/` and reference as `icon.png`

## Example: Core Service

```yaml
labels:
  - homepage.group=Core
  - homepage.name=OpenClaw
  - homepage.icon=mdi-robot-outline
  - homepage.href=https://openclaw.titan.local
  - homepage.description=Agent orchestration
  - homepage.weight=5
```

## Example: Infra Service

```yaml
labels:
  - homepage.group=Infra
  - homepage.name=Proxmox
  - homepage.icon=proxmox.png
  - homepage.href=https://192.168.10.100:8006
  - homepage.description=Virtualization host
  - homepage.weight=10
```

## Example: Service with Widget

```yaml
labels:
  - homepage.group=Infra
  - homepage.name=Portainer
  - homepage.icon=si-portainer
  - homepage.href=https://portainer.titan.local
  - homepage.description=Container management
  - homepage.weight=15
  - homepage.widget.type=portainer
  - homepage.widget.url=http://portainer:9000
```

## Group Reference

| Group | Purpose |
|-------|---------|
| Core | Essential services (OpenClaw, Authentik, Nginx) |
| Infra | Infrastructure (Proxmox, Portainer, Grafana) |
| Forge | Delivery tools (Forge Pipeline, ForgeHome) |
| Labs | Experimental/test services |

## Weight Ordering

Lower weight = appears first in group.

Suggested ranges:
- 1-10: Core critical services
- 10-50: Standard services
- 50+: Labs/experimental