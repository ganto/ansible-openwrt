#!/usr/bin/python

# Copyright: (c) 2021, Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: uci
short_description: Configuration interface for OpenWRT
version_added: "1.0.0"
description:
  - Manage OpenWRT system configuration settings.
options:
  command:
    description:
      - UCI command to run
    choices: ['get', 'set']
  commit:
    description:
      - Persist changes to configuration file.
      - This can be limitted to an individual file if the appropriate C(config) element is given.
    type: bool
    default: false
  key:
    description:
      - Configuration key to operate on
      - Usually in the format <config>.<section>[.<option>]
  named:
    description:
      - Resolve unamed section in output
    type: bool
    default: true
author:
  - Reto Gantenbein (@ganto)
'''

RETURN = r'''
result:
    description: Output of the 'uci' command.
    type: str
    returned: always
result_list:
    description: the list form of result
    returned: when I(command=get)
    type: list of string
rc:
    description: Return code of the 'oci' commad.
    type: int
'''

from collections import OrderedDict

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ganto.openwrt.plugins.module_utils.uci import UnifiedConfigurationInterface


def main():
    module = AnsibleModule(
        argument_spec=dict(
            command=dict(type='str', choices=['get', 'set']),
            commit=dict(type='bool', default=False),
            config=dict(type='str'),
            key=dict(type='str'),
            named=dict(type='bool', default=True),
            option=dict(type='str'),
            section=dict(type='str'),
            value=dict(type='str'),
        ),
        mutually_exclusive=[['key', 'config'],
                            ['key', 'section'],
                            ['key', 'option']],
        required_one_of=[['command', 'commit']],
        supports_check_mode=True,
    )

    input = OrderedDict(
        config=module.params['config'],
        section=module.params['section'],
        option=module.params['option'],
    )
    if module.params['key']:
        elements = module.params['key'].split('.')
        input['config'] = elements[0]
        if len(elements) > 1:
            input['section'] = elements[1]
        if len(elements) > 2:
            input['option'] = elements[2]

    result = dict(
        changed=False,
        result={}
    )
    diff = dict(
        before={},
        after={}
    )

    uci = UnifiedConfigurationInterface(module)

    # Check if uci is in an uncommitted state
    args = []
    if input['config']:
        args.append(input['config'])
    changes = uci.changes(args)['output']

    if len(changes) > 0:
        if module.params['commit']:
            diff['before'].update(committed=False)
            diff['after'].update(committed=True)
            result['changed'] = True
        else:
            result['result'].update(committed=False)

        result.update(changes=changes)

    # Get or set a value
    if module.params['command'] in ['get', 'set']:

        current_value = uci.get(
            ['.'.join(n for n in input.values() if n is not None)])['output']
        input_value = module.params['value']

        if (module.params['command'] == 'set' and
                input_value != current_value):

            diff['before'].update(value=current_value)
            diff['after'].update(value=input_value)
            result['changed'] = True

            if not module.check_mode:
                uci.set(['.'.join(n for n in input.values()
                                  if n is not None) + ('=%s' % input_value)])

            result['result'].update(value=input_value)
        else:
            result['result'].update(value=current_value)

    if input['config']:
        result['result'].update(config=input['config'])

    result['result'].update(named=module.params['named'])
    if not module.params['named']:
        result['result'].update(section=input['section'])
    else:
        named = uci.show(['.'.join(list(input.values())[0:2])])
        result['result'].update(section=list(named['output'])[0].split('.')[1])

    if input['option']:
        result['result'].update(option=input['option'])

    # Commit pending changes
    if (result['changed'] or len(changes) > 0) and module.params['commit']:
        if not module.check_mode:
            args = []
            if input['config']:
                args.append(input['config'])

            uci.commit(args)

        result['result'].update(committed=True)

    if len(diff['before'].keys()) > 0:
        result.update(diff=diff)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
