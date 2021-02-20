# -*- coding: utf-8 -*-
# Copyright: (C) 2021, Reto Gantenbein <reto.gantenbein@linuxmonk.ch>
# SPDX-License-Identifier: GPL-3.0-or-later


def convert_to_uci_type(value):
    if isinstance(value, bool):
        return (1 if value else 0)
    return value


class FilterModule(object):
    ''' A filter to convert a boolean true to 1 and false to 0. '''

    def filters(self):
        return {
            'uci_type': convert_to_uci_type
        }
