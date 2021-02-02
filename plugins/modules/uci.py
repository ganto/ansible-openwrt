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
    choices: ['add', 'changes', 'delete', 'get', 'revert', 'set']
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
            command=dict(type='str',
                         choices=['add', 'changes', 'delete', 'get', 'revert', 'set']),
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

    if input['section'] and not ['config']:
        module.fail_json(
            msg="Option 'section' requires 'config' to be defined too.")

    result = dict(
        changed=False,
        result={}
    )
    diff = dict(
        before={},
        after={}
    )

    command = module.params['command']
    uci = UnifiedConfigurationInterface(module)

    # Check if uci is in an uncommitted state
    args = []
    if input['config']:
        args.append(input['config'])
    changes = uci.changes(args)

    if len(changes) > 0:
        if module.params['commit']:
            diff['before'].update(committed=False)
            diff['after'].update(committed=True)
            result['changed'] = True
        else:
            result['result'].update(committed=False)

    if not command:
        if not module.params['commit']:
            module.fail_json(msg="At least 'command' or 'commit' must be defined.")

        # If no command is defined then we should only commit.
        # Always add potential changes to result.
        result['result'].update(changes=changes)

    else:
        # Check required options
        if command in ['delete', 'revert']:
            if not input['config']:
                module.fail_json(
                    msg="Command '%s' requires 'config' or 'key' to be defined." % command)

        if command in ['add', 'get', 'set']:
            for element in ['config', 'section']:
                if not input[element]:
                    module.fail_json(
                        msg="Command '%s' requires '%s' or 'key' to be defined." % (command, element))

        if command in ['set']:
            if not module.params['value']:
                module.fail_json(
                    msg="Command '%s' requires 'value' to be defined." % command)

        # Add new section
        if command == 'add':
            if not module.check_mode:
                section = uci.add([input['config'], input['section']])

                result['result'].update(section=section)

            result['changed'] = True
            # A new section will be generated with the given section (type) as value
            result['result'].update(value=input['section'])

        # Query pending changes
        if command in ['changes', 'revert']:
            result['result'].update(changes=changes)
            if len(changes) == 0:
                result['result'].update(committed=True)

        # Revert uncommitted changes
        if command == 'revert':
            if len(changes) > 0:
                result['changed'] = True

                if not module.check_mode:
                    uci.revert(['.'.join(n for n in input.values()
                                         if n is not None)])

        # Get or set a value
        if command in ['get', 'set']:

            try:
                current_value = uci.get(
                    ['.'.join(n for n in input.values() if n is not None)])

            except OSError as e:
                if e.strerror != 'Entry not found':
                    raise(e)
                else:
                    if command == 'set':
                        current_value = ''
                    else:
                        module.fail_json(msg=e.strerror)

            if command == 'set':
                input_value = module.params['value']
                if input_value.isdigit():
                    input_value = int(input_value)

            if (command == 'set' and input_value != current_value):

                diff['before'].update(value=current_value)
                diff['after'].update(value=input_value)
                result['changed'] = True

                if not module.check_mode:
                    uci.set(['.'.join(n for n in input.values()
                                      if n is not None) + ('=%s' % input_value)])

                result['result'].update(value=input_value)
            else:
                result['result'].update(value=current_value)

        if command == 'delete':
            key = '.'.join(n for n in input.values() if n is not None)
            try:
                value = uci.get([key])
                section = uci.section_name(key, trimconfig=True)

                diff['before'].update(config=input['config'],
                                      section=section,
                                      value=value)
                if input['option']:
                    diff['before'].update(option=input['option'])

                if not module.check_mode:
                    uci.delete([key])
                else:
                    # If we're in check-mode the committed state cannot be
                    # determined by analyzing the changes as it's done below
                    if (('commited' not in result['result'].keys() or
                            not result['result']['committed']) and
                            not module.params['commit']):
                        diff['before'].update(committed=True)
                        diff['after'].update(committed=False)
                        result['result'].update(committed=False)

                result['changed'] = True

            except OSError as e:
                if e.strerror != 'Entry not found':
                    raise(e)

        if command in ['add', 'get', 'set']:
            if input['config']:
                result['result'].update(config=input['config'])

        if command in ['get', 'set']:

            result['result'].update(named=module.params['named'])
            if not module.params['named']:
                result['result'].update(section=input['section'])
            else:
                try:
                    section = uci.section_name("%s.%s" % (input['config'], input['section']),
                                               trimconfig=True)
                except OSError as e:
                    if e.strerror != 'Entry not found':
                        raise(e)
                    section = input['section']

                result['result'].update(section=section)

            if input['option']:
                result['result'].update(option=input['option'])

    # Commit pending changes
    if module.params['commit']:
        if ('changed' in result.keys() or len(changes) > 0) and not module.check_mode:
            args = []
            if input['config']:
                args.append(input['config'])

            uci.commit(args)

        result['result'].update(committed=True)
    else:
        # Eventually check if uci is in an uncommitted state again
        args = []
        if input['config']:
            args.append(input['config'])
        changes = uci.changes(args)

        if len(changes) > 0:
            result['result'].update(committed=False)

    # Check if there are some diffs to attach
    if len(diff['before'].keys()) > 0:
        result.update(diff=diff)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
