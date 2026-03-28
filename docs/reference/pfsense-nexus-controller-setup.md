# Netgate Nexus Controller Setup

Source: https://docs.netgate.com/pfsense/en/latest/nexus/setup.html
Ingested: 2026-03-28

## Overview

Before instances of pfSense Plus software can be registered to the Netgate Nexus controller for tasks such as multi-instance management (MIM), there are several setup tasks to complete.

## Enable Netgate Nexus Controller

The Netgate Nexus controller must be enabled and running before registering instances.

1. Open the pfSense Plus software WebGUI on the designated controller
2. Navigate to **System > Advanced**, Netgate Nexus tab
3. Check **Enable**
4. Configure any other options as needed
5. Click **Save**

## Firewall Rules for Netgate Nexus

The Netgate Nexus controller does not automatically add firewall rules for the Netgate Nexus GUI or external controller VPN connectivity. Firewall rules are necessary for instances to connect the VPN itself and for administrators to reach the Netgate Nexus GUI.

**Note:** The Netgate Nexus controller automatically passes traffic tunneled through its VPN between the instances and the controller. There is no need to manage rules for that internal communication.

### Allowing Incoming Netgate Nexus VPN Connections

Add a rule on WAN to pass connections to the Netgate Nexus VPN port.

1. Open the pfSense Plus software WebGUI on the designated controller
2. Navigate to **Firewall > Rules**, WAN tab
3. Click to add a new rule at the top of the list
4. Configure the rule with the following options:

| Setting | Value |
|---------|-------|
| Action | Pass |
| Protocol | UDP |
| Source | Any (or specific static addresses via alias) |
| Destination | This Firewall (self) |
| Destination Port | (Other) → Custom: `_nexus_vpn_port_` |

**Note:** `_nexus_vpn_port_` is a built-in alias which automatically contains the random port the controller selected to use for incoming VPN connections.

5. Click **Save**
6. Click **Apply Changes**

### Allowing Netgate Nexus GUI Access

Access to the Netgate Nexus GUI is also restricted by firewall rules. If local interfaces or VPNs are restricted, rules must be added there as well.

**⚠️ Danger:** Do not expose this port to the Internet. Limit access as much as possible. Use a VPN for remote access.

The ports for GUI access are configured in the Netgate Nexus options (General Options).

As with the pfSense Plus software WebGUI, the best practice is to restrict access to specific management hosts, networks, or VPN clients.

## Accessing the Netgate Nexus GUI

To access the Netgate Nexus GUI, follow the links in the Netgate Nexus status under **System > Advanced, Netgate Nexus tab**.

Use the HTTPS link to securely access the Netgate Nexus controller.

**Note:** If the Netgate Nexus controller is using a self-signed TLS certificate, it may be necessary to click through a browser warning about the validity of the self-signed certificate.

## Netgate Nexus Authentication

After following the link, the controller displays a login screen.

**Tip:** Bookmark this page for faster access.

The Netgate Nexus controller uses the pfSense Plus software User Manager, so the same credentials work for both the Netgate Nexus controller and the pfSense Plus software WebGUI.

Enter valid credentials and click **Sign In** to access the Netgate Nexus GUI.

## Related

- [Netgate Nexus Controller Configuration Options](options.html)
- [General Options](options.html#nexus-pfsense-options-general)
- [Viewing Netgate Nexus Status](options.html#nexus-pfsense-status)
- [User Manager](../usermanager/index.html)