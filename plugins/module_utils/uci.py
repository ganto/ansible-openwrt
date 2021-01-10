# Copyright (c) 2021, Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from re import match


STRIP_QUOTES = r'\'\"\\'


class UnifiedConfigurationInterface():

    def __init__(self, module):
        self.module = module
        self.uci_path = module.get_bin_path('uci', required=True)

    def _exec(self, args):
        args.insert(0, self.uci_path)

        rc, out, err = self.module.run_command(args)
        if rc != 0:
            return dict(error=err)

        return self._parse_output(out)

    def _parse_output(self, msg):
        lines = msg.splitlines()
        items = dict(item.split('=', maxsplit=1) for item in lines)

        for key, val in items.items():
            val = val.strip(STRIP_QUOTES)
            if val.isdigit():
                val = int(val)
            elif ' ' in val:
                val = val.split()
            items[key] = val

        return items

    def show(self, args=[]):
        args.insert(0, 'show')

        return self._exec(args)

    def version(self):
        opkg = self.module.get_bin_path('opkg')
        if opkg:
            rc, out, err = self.module.run_command([opkg, 'info', 'uci'])
            if rc == 0:
                for line in out.splitlines():
                    if match('^Version', line):
                        return line.split()[1]
