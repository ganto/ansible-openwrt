# Ansible Collection: ganto.openwrt

[![CI](https://github.com/ganto/ansible-openwrt/workflows/CI/badge.svg?event=push)](https://github.com/ganto/ansible-openwrt/actions?query=workflow%3ACI)

This Ansible collection consists of modules and roles to manage [OpenWRT](https://openwrt.org/) based systems.

_IMPORTANT: This collection is still in early development and cannot be installed via Ansible Galaxy yet. Check the bundled [molecule](molecule/default) scenario for the implemented use-cases. Everything else is not tested!_

### Roles

So far the following Ansible roles are implemented:
| Role Name | Role Configuration                          | Description      |
| --------- | ------------------------------------------- | ---------------- |
| network   | [defaults](roles/network/defaults/main.yml) | Define network configuration through [UCI network options](https://openwrt.org/docs/guide-user/network/ucicheatsheet) |
| dnsmasq   | [defaults](roles/dnsmasq/defaults/main.yml) | Manage DHCP and basic DNS through [UCI dhcp](https://openwrt.org/docs/guide-user/base-system/dhcp) options |
| isc_dhcpd | [defaults](roles/isc_dhcpd/defaults.yml)    | ISC DHCP server configuration (based on DebOps [dhcpd](https://docs.debops.org/en/master/ansible/roles/dhcpd/index.html) Ansible role) |
| opkg      | [defaults](roles/opkg/defaults/main.yml)    | Feeds configuration, package installation and system updates |
| system    | [defaults](roles/system/defaults/main.yml)  | Basic system settings through [UCI system options](https://openwrt.org/docs/guide-user/base-system/system_configuration) |

### Development

#### Testing

There is a [Molecule](https://molecule.readthedocs.io/) test profile that can be used to verify the basic functionality of the roles. The default scenario is using the [podman](https://podman.io/) container driver. If you prefer [docker](https://www.docker.com/) you can select the corresponding scenario with the `-s docker` molecule arguments.

1. Ensure you have the necessary dependencies installed (e.g. in a Python [venv](https://docs.python.org/3/tutorial/venv.html)):
```
pip install -r molecule/default/requirements.txt        # for podman
# or
pip install -r molecule/docker/requirements.txt         # for docker
```
2. Run the test suite. The options in brackets are optional but useful if you need to troubleshoot issues:
```
molecule [-vvv] test [--destroy never][-s docker]
```
3. If you used `--destroy never` the container will remain after the test run and can be inspected interactively via:
```
podman exec -it <container-id> /bin/sh                  # for podman
# or
docker exec -it <container-id> /bin/sh                  # for docker
```
4. Once you're done with inspecting the instance it has to be deleted before a new test run can be started:
```
molecule destroy [-s docker]
```

### License

[GPL-3.0](https://spdx.org/licenses/GPL-3.0-or-later.html) or some later version


### Author

The content of this repository was written by:

- [Reto Gantenbein](https://linuxmonk.ch/) | [e-mail](mailto:reto.gantenbein@linuxmonk.ch) | [GitHub](https://github.com/ganto)
