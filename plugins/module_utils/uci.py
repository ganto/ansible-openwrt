# -*- coding: utf-8 -*-
# Copyright (C) 2021, Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from re import match

from ansible.module_utils.common.process import get_bin_path


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
        self.uci_path = get_bin_path('uci', required=True)

    def _exec(self, args):
        args.insert(0, self.uci_path)

        rc, stdout, stderr = self.module.run_command(args)
        if rc != 0:
            path, _, strerror = stderr.strip().partition(' ')
            raise OSError(rc, strerror, path.strip(':'))

        return stdout

    def add(self, args):
        args.insert(0, 'add')
        return uci_parse_value(self._exec(args))

    def add_list(self, args):
        args.insert(0, 'add_list')
        self._exec(args)

    def changes(self, args=[]):
        args.insert(0, 'changes')

        result = self._exec(args)
        # TODO: fix multi-line changes, changes with key=value
        output = uci_parse_value(result)

        return output

    def commit(self, args=[]):
        args.insert(0, 'commit')
        self._exec(args)

    def delete(self, args):
        args.insert(0, 'delete')
        self._exec(args)

    def get(self, args=[]):
        args.insert(0, 'get')
        return uci_parse_value(self._exec(args))

    def revert(self, args):
        args.insert(0, 'revert')
        self._exec(args)

    def set(self, args):
        args.insert(0, 'set')
        self._exec(args)

    def section_name(self, key, trimconfig=False):
        args = '.'.join(key.split('.')[0:2])

        output = list(self.show([args]))[0]
        if trimconfig:
            return output.split('.')[1]
        else:
            return output

    def show(self, args=[]):
        args.insert(0, 'show')
        return uci_parse_output(self._exec(args))

    def version(self):
        opkg = get_bin_path('opkg')
        if opkg:
            rc, out, err = self.module.run_command([opkg, 'info', 'uci'])
            if rc == 0:
                for line in out.splitlines():
                    if match('^Version', line):
                        return line.split()[1]
