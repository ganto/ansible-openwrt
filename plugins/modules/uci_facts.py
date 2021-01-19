#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (c) 2021, Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r'''
---
module: uci_facts
short_description: Return OpenWRT UCI configuration as fact data
description:
    - Return OpenWRT UCI configuration as fact data for all supported services.
version_added: "1.0.0"
requirements:
    - OpenWRT-based system with C(uci) command-line utility.
options:
  config:
    description:
      - Reduce facts gathering to given config (e.g. network, system).
    type: str
  section:
    description:
      - Reduce facts gathering to given config section.
      - Requires C(config) to be defined.
      - Can be defined as named or unnamed section.
    type: str
notes:
    - This module is mostly a wrapper around the C(uci show) command.
author:
  - Reto Gantenbein (@ganto)
'''

EXAMPLES = r'''
- name: Populate UCI facts
  uci_facts:

- debug:
    var: ansible_facts.uci

'''

RETURN = r'''
ansible_facts:
  description:
  - Facts to add to ansible_facts about the UCI configuration on the system
  returned: always
  type: complex
  contains:
    uci:
      description:
      - Facts gathered from the UCI utility.
      returned: success
      type: dict
    uci_config:
      description:
      - Name of the config element of the facts.
      returned: When C(config) option is defined.
      type: str
      sample: network
    uci_section:
      description:
      - Name of the section element of the facts.
      returned: When C(section) option is defined.
      type: str
      sample: wan
    uci_version:
      description:
      - Version of the C(uci) command-line utility.
      returned: success
      type: str
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ganto.openwrt.plugins.module_utils.uci import UnifiedConfigurationInterface


def main():
    module_args = dict(
        config=dict(type='str'),
        section=dict(type='str')
    )

    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    results = dict(ansible_facts={})

    elements = []
    if module.params['config']:
        elements.append(module.params['config'])
        results['ansible_facts'].update(uci_config=module.params['config'])
    if module.params['section']:
        if not module.params['config']:
            module.fail_json(msg='missing required argument: config')
        elements.append(module.params['section'])
        results['ansible_facts'].update(uci_section=module.params['section'])

    args = []
    if len(elements) > 0:
        args.append('.'.join(elements))

    uci = UnifiedConfigurationInterface(module)
    try:
        results['ansible_facts'].update(uci=uci.show(args))

    except OSError as e:
        module.fail_json(msg="%s: %s" % (e.filename, e.strerror))

    version = uci.version()
    if version:
        results['ansible_facts'].update(uci_version=version)

    module.exit_json(**results)


if __name__ == '__main__':
    main()
