# Ansible Collection: ganto.openwrt

[![CI](https://github.com/ganto/ansible-openwrt/workflows/CI/badge.svg?event=push)](https://github.com/ganto/ansible-openwrt/actions?query=workflow%3ACI)

This Ansible collection consists of modules and roles to manage [OpenWRT](https://openwrt.org/) based systems.

_IMPORTANT: This collection is still in early development and cannot be installed via Ansible Galaxy yet. Check the bundled [Molecule](https://molecule.readthedocs.io/) tests for the implemented use-cases. Everything else is not tested!_

### Roles

So far the following Ansible roles are implemented:
| Role Name | Role Configuration                          | Description      |
| --------- | ------------------------------------------- | ---------------- |
| network   | [defaults](roles/network/defaults/main.yml) | Define network configuration through [UCI network options](https://openwrt.org/docs/guide-user/network/ucicheatsheet) |
| dnsmasq   | [defaults](roles/dnsmasq/defaults/main.yml) | Manage DHCP and basic DNS through [UCI dhcp](https://openwrt.org/docs/guide-user/base-system/dhcp) options |
| opkg      | [defaults](roles/opkg/defaults/main.yml)    | Feeds configuration, package installation and system updates |
| system    | [defaults](roles/system/defaults/main.yml)  | Basic system settings through [UCI system options](https://openwrt.org/docs/guide-user/base-system/system_configuration) |


### License

[GPL-3.0](https://spdx.org/licenses/GPL-3.0-or-later.html) or some later version


### Author

The content of this repository was written by:

- [Reto Gantenbein](https://linuxmonk.ch/) | [e-mail](mailto:reto.gantenbein@linuxmonk.ch) | [GitHub](https://github.com/ganto)
