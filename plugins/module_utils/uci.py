# Copyright (c) 2021, Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from re import match

STRIP_QUOTES = r'\'\"\\'


def uci_parse_value(value):
    val = value.strip(STRIP_QUOTES)
    if len(val) == 0:
        return ''

    val = val.splitlines()[0]

    if val.isdigit():
        val = int(val)
    elif ' ' in val:
        val = val.split()

    return val


def uci_parse_output(msg):
    if len(msg) == 0:
        return {}

    lines = msg.splitlines()
    items = dict(item.split('=', maxsplit=1) for item in lines)

    for key, val in items.items():
        items[key] = uci_parse_value(val)

    return items


class UnifiedConfigurationInterface():

    def __init__(self, module):
        self.module = module
        self.uci_path = module.get_bin_path('uci', required=True)

    def _exec(self, args):
        args.insert(0, self.uci_path)

        rc, out, err = self.module.run_command(args)
        if rc != 0:
            return dict(error=err, rc=rc)

        return dict(output=out, rc=rc)

    def changes(self, args=[]):
        args.insert(0, 'changes')

        result = self._exec(args)
        return dict(output=uci_parse_output(result['output']), rc=result['rc'])

    def commit(self, args=[]):
        args.insert(0, 'commit')
        return dict(rc=self._exec(args)['rc'])

    def get(self, args=[]):
        args.insert(0, 'get')

        result = self._exec(args)
        return dict(output=uci_parse_value(result['output']), rc=result['rc'])

    def set(self, args=None):
        args.insert(0, 'set')
        return dict(rc=self._exec(args)['rc'])

    def show(self, args=[]):
        args.insert(0, 'show')

        result = self._exec(args)
        return dict(output=uci_parse_output(result['output']), rc=result['rc'])

    def version(self):
        opkg = self.module.get_bin_path('opkg')
        if opkg:
            rc, out, err = self.module.run_command([opkg, 'info', 'uci'])
            if rc == 0:
                for line in out.splitlines():
                    if match('^Version', line):
                        return line.split()[1]
