#!/usr/bin/env python3

# Copyright (c) 2005-2014 Fpemud <fpemud@sina.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import pylkc
from multiprocessing import Process


class CheckError(Exception):

    def __init__(self, name, value, realValue):
        if name.startswith("/"):
            message = "choice \"%s\" has incorrect value" % (name)
        else:
            message = "symbol %s has incorrect value" % (name)
        super(CheckError, self).__init__(message)
        self.name = name
        self.value = value
        self.realValue = realValue


def check_value(ksrcDir, cfgFile, name, value):
    pylkc.init(ksrcDir)
    try:
        pylkc.conf_parse(ksrcDir)
        pylkc.conf_read(cfgFile)
        for sym in pylkc.all_symbols():
            sym.calc_value()
        if name.startswith("/"):
            ret = _getChoice(name)
            if ret != value:
                raise CheckError(name, value, ret)
        else:
            ret = _getValue(name)
            if ret != value:
                raise CheckError(name, value, ret)
    finally:
        pylkc.release()


def check_values(ksrcDir, cfgFile, valueDict):
    pylkc.init(ksrcDir)
    try:
        pylkc.conf_parse(ksrcDir)
        pylkc.conf_read(cfgFile)
        for sym in pylkc.all_symbols():
            sym.calc_value()
        for k, v in valueDict.items():
            if k.startswith("/"):
                ret = _getChoice(k)
                if ret != v:
                    raise CheckError(k, v, ret)
            else:
                ret = _getValue(k)
                if ret != v:
                    raise CheckError(k, v, ret)
    finally:
        pylkc.release()


############## implementations ################################################


def _getValue(symbolName):
    sym = pylkc.sym_find(symbolName)
    if sym.get_type() == pylkc.symbol.TYPE_UNKNOWN:
        assert False
    elif sym.get_type() == pylkc.symbol.TYPE_BOOLEAN:
        if sym.get_tristate_value() == pylkc.tristate.no:
            return "n"
        else:
            return "y"
    elif sym.get_type() == pylkc.symbol.TYPE_TRISTATE:
        if sym.get_tristate_value() == pylkc.tristate.no:
            return "n"
        elif sym.get_tristate_value() == pylkc.tristate.mod:
            return "m"
        elif sym.get_tristate_value() == pylkc.tristate.yes:
            return "y"
        else:
            assert False
    elif sym.get_type() == pylkc.symbol.TYPE_INT:
        return int(sym.get_string_value())
    elif sym.get_type() == pylkc.symbol.TYPE_HEX:
        assert False
    elif sym.get_type() == pylkc.symbol.TYPE_STRING:
        return sym.get_string_value()
    elif sym.get_type() == pylkc.symbol.TYPE_OTHER:
        assert False
    else:
        assert False


def _getChoice(menuPath):
    menuObj = pylkc.menu_find_by_path(menuPath, True)
    for m in menuObj.list:
        if m.sym.get_tristate_value() != pylkc.tristate.no:
            return m.sym.name
    assert False
