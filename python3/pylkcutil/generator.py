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

"""Key types:

     1. symbol:           trivial, no explaination
                          example: BINFMT_SCRIPT=y
                                   DEFAULT_HOSTNAME="(none)"

     2. choice:           trivial, no explaination
                          example: /General setup/Timers subsystem/Timer tick handling=NO_HZ_IDLE

     3. symbols:          all the symbols under the specified menu
                          example: [symbols:PROC_FS]=y
                                   [symbols:/File systems]=n

     4. normal-symbols:   all the symbols under the specified menu, excluding DEBUG, DEPRECATED, EXPERIMENTAL, DANGEROUS ones
                          example: [normal-symbols:EXT2_FS]=m
                                   [normal-symbols:/Networking support]=m

     5. debugging-symbols:

     6. deprecated-symbols:

     7. workaround-symbols:

     8. experimental-symbols:

     9. dangerous-symbols:

     10. regex-symbols:          symbols that has a matching name under the specified menu
                                 example: [regex-symbols:\bISCSI\b:/Device Drivers]=n

     11. prompt-regex-symbols:   symbols that has a matching prompt under the specified menu
                                 example: [prompt-regex-symbols:Support initial ramdisks compressed using .*:/General setup]=n
"""

"""selection constrain rules:
     1. symbol can make stricter contrains for its parent symbol
     2. symbol can make stricter contrains for symbol under parent menu
"""

"""Rules are executed in order, new rules are not able to:
     1. change old selection value.
     2. hide a symbol which has value "y" or "m".
     3. make stricter selection contrains out of the scope of the above selection constrain rules.

   If a new rule does the above, then there's a conflict.
     For key symbol and choice, a conflict leads to operation failure.
     For key *-symbols, a conflict means the current symbol is ignored.
"""

"""baseConfig values:
     1. defconfig
     2. allnoconfig
     3. allnoconfig+module
"""


import os
import re
import pylkc
import pylkcx
from multiprocessing import Process


class EventHandler:

    def progressChanged(self, stage):
        # values for stage parameter: initialized, rule-file-parsed, base-config-loaded, finished
        pass

    def symbolChanged(self, symbolName, symbolValue):
        pass

    def choiceChanged(self, menuPath, choiceValue):
        pass


class SyntaxError(Exception):

    def __init__(self, context, lineNo, message):
        msg = "rule %d (%s): syntax error, %s" % (lineNo, context.ruleDict[lineNo], message)
        super(SyntaxError, self).__init__(msg)


class ConflictError(Exception):

    def __init__(self, context, item, recSym=None):
        ln = item.lineNo
        rule = context.ruleDict[ln]

        if item.symbolMenu is not None:
            if recSym is not None:
                msg = "rule %d (%s): symbol %s conflicts with value record \"%s=%s\"" % (ln, rule, item.symbolMenu.sym.name, recSym.name, context.symValueRecord[recSym])
            else:
                msg = "rule %d (%s): symbol %s conflicts with value record" % (ln, rule, item.symbolMenu.sym.name)
        elif item.choiceMenu is not None:
            if recSym is not None:
                msg = "rule %d (%s): choice \"%s\" conflicts with value record \"%s=%s\"" % (ln, rule, _getMenuPath(item.choiceMenu), recSym.name, context.symValueRecord[recSym])
            else:
                msg = "rule %d (%s): choice \"%s\" conflicts with value record" % (ln, rule, _getMenuPath(item.choiceMenu))
        else:
            assert False

        super(ConflictError, self).__init__(msg)


class NotExecutedError(Exception):

    def __init__(self, context, item, reason):
        if reason == "invisibility":
            msg = "rule %d (%s) ignored by invisibility" % (item.lineNo, context.ruleDict[item.lineNo])
        else:
            assert False
        super(NotExecutedError, self).__init__(msg)


class InternalError(Exception):

    def __init__(self, message):
        super(InternalError, self).__init__(message)


def generate(ksrcDir, baseConfig, ruleFile, baseConfigFilename=None, output=None, eventHandler=None):
    if baseConfig == "file":
        assert baseConfigFilename is not None
    if output is None:
        output = os.path.join(ksrcDir, ".config")

    context = _Context()
    context.eventHandler = eventHandler
    if context.eventHandler is not None:
        context.eventHandler.progressChanged("initialized")

    pylkc.init(ksrcDir)
    try:
        pylkc.conf_parse(ksrcDir)

        # load base config
        if baseConfig == "defconfig":
            _makeDefConfig(ksrcDir, "")
        elif baseConfig == "allnoconfig":
            _makeAllNoConfig()
        elif baseConfig == "allnoconfig+module":
            _makeAllNoConfig()
            pylkc.sym_find("MODULES").set_tristate_value(pylkc.tristate.yes)
        elif baseConfig == "file":
            pylkc.conf_read(baseConfigFilename)
        else:
            assert False
        for sym in pylkc.all_symbols():
            sym.calc_value()
        if context.eventHandler is not None:
            context.eventHandler.progressChanged("base-config-loaded")

        # parse rule file
        context.parseRuleFile(ruleFile)
        if context.eventHandler is not None:
            context.eventHandler.progressChanged("rule-file-parsed")

        # record pre-set values
        if baseConfig == "allnoconfig":
            _presetSymbol(context, "EXPERT", "y")
            _presetSymbol(context, "EMBEDDED", "y")
        elif baseConfig == "allnoconfig+module":
            _presetSymbol(context, "EXPERT", "y")
            _presetSymbol(context, "EMBEDDED", "y")
            _presetSymbol(context, "MODULES", "y")
        else:
            pass

        # do operation
        while len(context.itemRunList) > 0:
            item = context.itemRunList.pop(0)
            if item.symbolMenu is not None:
                if item.value.startswith("\""):
                    _procSymbolNonYmn(context, item)
                elif _is_int(item.value):
                    _procSymbolNonYmn(context, item)
                else:
                    _procSymbolYmn(context, item)
            elif item.choiceMenu is not None:
                _procChoice(context, item)
            else:
                assert False

        pylkc.conf_write(output)

        # final check:
        # 1. check if any symbol is ignored by invisibility
        for item in context.itemRunList:
            if item.symbolMenu is not None:
                if item.symbolMenu in context.symValueRecord:
                    continue
                if item.symbolMenu.sym.get_type() not in [pylkc.symbol.TYPE_BOOLEAN, pylkc.symbol.TYPE_TRISTATE]:
                    continue
                if item.value == "n":
                    continue
                if not item.vforce:
                    continue
                raise NotExecutedError(context, item, "invisibility")
            elif item.choiceMenu is not None:
                if any(m in context.symValueRecord for m in item.choiceMenu.list):
                    continue
                raise NotExecutedError(context, item, "invisibility")
            else:
                assert False

        pylkc.conf_write(output)
        if context.eventHandler is not None:
            context.eventHandler.progressChanged("finished")
    finally:
        pylkc.release()


############## implementations ################################################


class _Context:

    class _Item:

        def __init__(self):
            self.index = -1                 # const
            self.lineNo = -1                # const
            self.symbolMenu = None          # const, for symbol
            self.choiceMenu = None          # const, for choice
            self.value = None               # const
            self.vforce = None              # const

        def __lt__(self, other):
            return self.index < other.index

    def __init__(self):
        self.eventHandler = None
        self.ruleDict = dict()              # <ruleNo-int, rule-string>, const
        self.itemList = []                  # const
        self.symRefDict = dict()            # <symbol, symbol-list>, const, visibility and constraint of "symbol-list" may change if "symbol" changes
        self.symItemDict = dict()           # <symbol, item-list>, const, "item-list" need re-exec if "symbol" changes

        self.itemRunList = []
        self.symValueDict = dict()          # <symbol, (value, visible, rev_dep.tri)>
        self.symValueRecord = dict()        # <symbol, value-string>
        self.symAltValueRecord = dict()     # <symbol, value-string-list>

    def parseRuleFile(self, ruleFile):
        # fill self.ruleDict
        lineList = []
        with open(ruleFile) as f:
            lineList = f.read().split("\n")
        for i in range(0, len(lineList)):
            line = lineList[i]
            if line == "":                      # remove empty line
                continue
            if line.startswith("#"):            # remove comment
                continue
            m = re.match("^(.*?) +#.*$", line)  # remove comment
            if m is not None:
                line = m.group(1)
            self.ruleDict[i + 1] = line

        # fill self.itemList
        for lineNo, line in self.ruleDict.items():
            key = line.split("=")[0]
            value = line.split("=")[1].strip("\t ")
            if key.startswith("["):
                kis = key[1:-1].split(":")
                if kis[0] == "symbols":
                    mstr = kis[1]
                    def _filterFunc(menuObj):
                        return False
                elif kis[0] == "normal-symbols":
                    mstr = kis[1]
                    def _filterFunc(menuObj):
                        if pylkcx.is_menu_debugging(menuObj):
                            return True
                        if pylkcx.is_menu_deprecated(menuObj):
                            return True
                        if pylkcx.is_menu_workaround(menuObj):
                            return True
                        if pylkcx.is_menu_experimental(menuObj):
                            return True
                        if pylkcx.is_menu_dangerous(menuObj):
                            return True
                        return False
                elif kis[0] == "debugging-symbols":
                    mstr = kis[1]
                    def _filterFunc(menuObj):
                        return not pylkcx.is_menu_debugging(menuObj)
                elif kis[0] == "deprecated-symbols":
                    mstr = kis[1]
                    def _filterFunc(menuObj):
                        return not pylkcx.is_menu_deprecated(menuObj)
                elif kis[0] == "workaround-symbols":
                    mstr = kis[1]
                    def _filterFunc(menuObj):
                        return not pylkcx.is_menu_workaround(menuObj)
                elif kis[0] == "experimental-symbols":
                    mstr = kis[1]
                    def _filterFunc(menuObj):
                        return not pylkcx.is_menu_experimental(menuObj)
                elif kis[0] == "dangerous-symbols":
                    mstr = kis[1]
                    def _filterFunc(menuObj):
                        return not pylkcx.is_menu_dangerous(menuObj)
                elif kis[0] == "regex-symbols":
                    regexPattern = kis[1]
                    mstr = kis[2]
                    def _filterFunc(menuObj):
                        if menuObj.sym is None:
                            return True
                        if menuObj.sym.name is None:
                            return True
                        if not re.match(regexPattern, menuObj.sym.name):
                            return True
                        return False
                elif kis[0] == "prompt-regex-symbols":
                    regexPattern = kis[1]
                    mstr = kis[2]
                    def _filterFunc(menuObj):
                        return not re.match(regexPattern, menuObj.get_prompt())
                else:
                    raise SyntaxError(self, lineNo, "invalid key %s" % (kis[0]))
                self._generateMenuInfoSymbols(lineNo, mstr, _filterFunc, value)
            elif key.startswith("/"):
                self._generateMenuInfoChoice(lineNo, key, value)
            else:
                self._generateMenuInfoSymbol(lineNo, key, value)

        # fill self.symRefDict
        if True:
            # init
            for sym in pylkc.all_symbols():
                self.symRefDict[sym] = set()

            # for "Selects" expression
            for sym in pylkc.all_symbols():
                for prop in sym.get_properties(pylkc.property.TYPE_SELECT):
                    self.symRefDict[sym].add(prop.get_symbol())

            # for "Depends on" expression
            for sym in pylkc.all_symbols():
                for s in _allSymbolsInExpr(sym.dir_dep.expr):
                    if s not in self.symRefDict:
                        continue                     # ???
                    self.symRefDict[s].add(sym)

            # convert set to list
            for k in self.symRefDict:
                self.symRefDict[k] = list(self.symRefDict[k])

        # fill self.symItemDict
        for item in self.itemList:
            if item.symbolMenu is not None:
                if item.symbolMenu.sym in self.symItemDict:
                    self.symItemDict[item.symbolMenu.sym].append(item)
                else:
                    self.symItemDict[item.symbolMenu.sym] = [item]
            elif item.choiceMenu is not None:
                for m in item.choiceMenu.list:
                    if m.sym in self.symItemDict:
                        self.symItemDict[m.sym].append(item)
                    else:
                        self.symItemDict[m.sym] = [item]
            else:
                assert False

        # fill self.itemRunList
        self.itemRunList = list(self.itemList)

        # fill self.symValueDict
        for sym in pylkc.all_symbols():
            self.symValueDict[sym] = (_symGetValue(sym), sym.visible, sym.rev_dep.tri)

    def _generateMenuInfoSymbol(self, lineNo, symbolName, value):
        sym = pylkc.sym_find(symbolName)
        if sym is None:
            raise SyntaxError(self, lineNo, "symbol %s not found" % (symbolName))
        menuObj = pylkc.menu_find_by_sym(sym)
        if menuObj is None:
            raise SyntaxError(self, lineNo, "symbol %s not found" % (symbolName))

        if sym.get_type() == pylkc.symbol.TYPE_BOOLEAN:
            newvlist = _merge_vlist(_str2vlist(value), ["n", "y"])
            if len(newvlist) == 0:
                raise SyntaxError(self, lineNo, "invalid value for BOOLEAN symbol %s" % (symbolName))
            value = _vlist2str(newvlist)
        elif sym.get_type() == pylkc.symbol.TYPE_INT and not _is_int(value):
            raise SyntaxError(self, lineNo, "invalid value \"%s\" for INT symbol %s" % (value, symbolName))

        item = self._Item()
        item.index = len(self.itemList)
        item.lineNo = lineNo
        item.symbolMenu = menuObj
        item.value = value
        item.vforce = True
        self.itemList.append(item)

    def _generateMenuInfoChoice(self, lineNo, menuPath, value):
        menuObj = pylkc.menu_find_by_path(menuPath, True)
        if menuObj is None:
            raise SyntaxError(self, lineNo, "choice \"%s\" not found" % (menuPath))
        if any(m.sym is None or not m.sym.is_choice_value() for m in menuObj.list):
            raise SyntaxError(self, lineNo, "menu \"%s\" is not a choice" % (menuPath))
        if not any(m.sym.name == value for m in menuObj.list):
            raise SyntaxError(self, lineNo, "invalid value %s for choice \"%s\"" % (value, menuPath))

        item = self._Item()
        item.index = len(self.itemList)
        item.lineNo = lineNo
        item.choiceMenu = menuObj
        item.value = value
        item.vforce = True
        self.itemList.append(item)

    def _generateMenuInfoSymbols(self, lineNo, mstr, filterFunc, value):
        if mstr.startswith("/"):
            menuObj = pylkc.menu_find_by_path(mstr, True)
            if menuObj is None:
                raise SyntaxError(self, lineNo, "menu \"%s\" not found" % (mstr))
        else:
            menuObj = pylkc.menu_find_by_sym(pylkc.sym_find(mstr))
            if menuObj is None:
                raise SyntaxError(self, lineNo, "menu %s not found" % (mstr))
        self._generateMenuInfoSymbolsImpl(lineNo, menuObj, filterFunc, value)

    def _generateMenuInfoSymbolsImpl(self, lineNo, menuObj, filterFunc, value):
        recordSelf = True
        if recordSelf and menuObj.sym is None:
            recordSelf = False
        if recordSelf and menuObj.sym.is_choice_value():
            recordSelf = False
        if recordSelf and menuObj.sym.get_type() not in [pylkc.symbol.TYPE_BOOLEAN, pylkc.symbol.TYPE_TRISTATE]:
            recordSelf = False
        if recordSelf and filterFunc(menuObj):
            recordSelf = False
        if recordSelf:
            newv = value
            if menuObj.sym.get_type() == pylkc.symbol.TYPE_BOOLEAN:
                newvlist = _merge_vlist(_str2vlist(value), ["n", "y"])
                if len(newvlist) == 0:
                    raise SyntaxError(self, lineNo, "invalid value for BOOLEAN symbol %s" % (menuObj.sym.name))
                newv = _vlist2str(newvlist)
            item = self._Item()
            item.index = len(self.itemList)
            item.lineNo = lineNo
            item.symbolMenu = menuObj
            item.value = newv
            item.vforce = False
            self.itemList.append(item)

        for m in menuObj.list:
            self._generateMenuInfoSymbolsImpl(lineNo, m, filterFunc, value)


def _procSymbolYmn(context, item):
    # return True means symbol value changed, return False means symbol value not changed
    assert item.symbolMenu is not None

    # temporarily invisible
    if not item.symbolMenu.is_visible():
        return False

    # get new value list, do value list conflict check
    if item.symbolMenu.sym in context.symValueRecord:
        newvlist = _merge_vlist(context.symAltValueRecord[item.symbolMenu.sym], _str2vlist(item.value))
        if len(newvlist) == 0:
            if item.vforce:
                raise ConflictError(context, item, item.symbolMenu.sym)
            else:
                return False
    else:
        newvlist = _str2vlist(item.value)

    # ignore temporarily
    newvlist = _vlistFilterByVisibleAndSelectionConstraint(item.symbolMenu, newvlist)
    if len(newvlist) == 0:
        return False

    # set symbol value, do advanced conflict check
    ovalue = _menuGetValue(item.symbolMenu)
    bModified = _menuSetValue(context, item.symbolMenu, newvlist[0])
    if bModified:
        try:
            _checkConflict(context, item)
        except ConflictError:
            if not item.vforce:
                _menuSetValue(context, item.symbolMenu, ovalue)
                return False
            raise
        _updateItemRunList(context, item)
        _updateSymValueDict(context, item)
        if context.eventHandler is not None:
            context.eventHandler.symbolChanged(item.symbolMenu.sym.name, newvlist[0])

    # record symbol value
    context.symValueRecord[item.symbolMenu.sym] = newvlist[0]
    context.symAltValueRecord[item.symbolMenu.sym] = newvlist

    return bModified


def _procSymbolNonYmn(context, item):
    # return True means symbol value changed, return False means symbol value not changed
    assert item.symbolMenu is not None
    assert item.vforce

    symbolName = item.symbolMenu.sym.name
    value = item.value if not item.value.startswith("\"") else item.value[1:-1]

    # temporarily invisible
    if not item.symbolMenu.is_visible():
        return False

    # do basic conflict check
    if item.symbolMenu.sym in context.symValueRecord:
        if item.value != context.symValueRecord[item.symbolMenu.sym]:
            raise ConflictError(context, item)
        return False

    # set symbol value, do advanced conflict check
    bModified = _menuSetValue(context, item.symbolMenu, value)
    if bModified:
        _checkConflict(context, item)
        _updateItemRunList(context, item)
        _updateSymValueDict(context, item)
        if context.eventHandler is not None:
            context.eventHandler.symbolChanged(symbolName, value)

    # record symbol value
    context.symValueRecord[item.symbolMenu.sym] = value

    return bModified


def _procChoice(context, item):
    # return True means symbol value changed, return False means symbol value not changed
    assert item.choiceMenu is not None

    menuPath = _getMenuPath(item.choiceMenu)

    # temporarily invisible
    if not item.choiceMenu.is_visible():
        return False

    # do basic conflict check
    if True:
        foundSet = set()
        for m in item.choiceMenu.list:
            v = "y" if m.sym.name == item.value else "n"
            if m.sym in context.symValueRecord:
                if v != context.symValueRecord[m.sym]:
                    raise ConflictError(context, item, m.sym)
                foundSet.add(True)
            else:
                foundSet.add(False)
        if len(foundSet) > 1:
            raise InternalError("invalid value record for choice \"%s\"" % (menuPath))

    # set choice value, do advanced conflict check
    bModified = _setChoice(context, item.choiceMenu, item.value)
    if bModified:
        _checkConflict(context, item)
        _updateItemRunList(context, item)
        _updateSymValueDict(context, item)
        if context.eventHandler is not None:
            context.eventHandler.choiceChanged(menuPath, item.value)

    # record choice value
    for m in item.choiceMenu.list:
        newvlist = [_tval2str(m.sym.get_tristate_value())]
        if m.sym in context.symValueRecord:
            context.symValueRecord[m.sym] = newvlist[0]
            context.symAltValueRecord[m.sym] = _merge_vlist(context.symAltValueRecord[m.sym], newvlist)
        else:
            context.symValueRecord[m.sym] = newvlist[0]
            context.symAltValueRecord[m.sym] = newvlist

    return bModified


def _checkConflict(context, item):
    recSet = set()
    if item.symbolMenu is not None:
        tmpValueDict, tmpAltValueDict = _checkConflictImpl(context, item, item.symbolMenu.sym, recSet)
    elif item.choiceMenu is not None:
        tmpValueDict = dict()
        tmpAltValueDict = dict()
        for m in item.choiceMenu.list:
            if m.sym in recSet:
                continue
            tmpValueDict2, tmpAltValueDict2 = _checkConflictImpl(context, item, m.sym, recSet)
            tmpValueDict.update(tmpValueDict2)
            tmpAltValueDict.update(tmpAltValueDict2)
    else:
        assert False

    for sym in tmpValueDict:
        if context.eventHandler is not None:
            context.eventHandler.symbolChanged(sym.name, tmpValueDict[sym])
        context.symValueRecord[sym] = tmpValueDict[sym]
        context.symAltValueRecord[sym] = tmpAltValueDict[sym]


def _checkConflictImpl(context, item, sym, recSet):
    recSet.add(sym)

    tmpValueDict = dict()
    tmpAltValueDict = dict()

    oldv = context.symValueDict[sym][0]
    newv = _symGetValue(sym)

    # has record, do check
    if sym in context.symValueRecord:
        recv = context.symValueRecord[sym]
        if sym.get_type() not in [pylkc.symbol.TYPE_BOOLEAN, pylkc.symbol.TYPE_TRISTATE]:
            # check for non-ymn symbol value conflict
            if not pylkc.menu_find_by_sym(sym).is_visible():
                raise ConflictError(context, item, sym)
            if newv != recv:
                raise ConflictError(context, item, sym)
        else:
            # check for ymn symbol value conflict, record altvalue change if no conflict found
            if recv in ["y", "m"] and not pylkc.menu_find_by_sym(sym).is_visible():
                raise ConflictError(context, item, sym)
            vlist = context.symAltValueRecord[sym]
            if newv != recv:
                if newv not in vlist:
                    raise ConflictError(context, item, sym)
                tmpValueDict[sym] = newv
                tmpAltValueDict[sym] = _strip_vlist(vlist, newv)

    # symbol changed, do recuresion
    if newv != oldv:
        for s in context.symRefDict.get(sym, []):
            if s in recSet:
                continue
            tmpValueDict2, tmpAltValueDict2 = _checkConflictImpl(context, item, s, recSet)
            tmpValueDict.update(tmpValueDict2)
            tmpAltValueDict.update(tmpAltValueDict2)

    return (tmpValueDict, tmpAltValueDict)


def _updateItemRunList(context, item):
    recSet = set()
    if item.symbolMenu is not None:
        for s in context.symRefDict.get(item.symbolMenu.sym, []):
            _updateItemRunListImpl(context, item, s, recSet)
    elif item.choiceMenu is not None:
        for m in item.choiceMenu.list:
            for s in context.symRefDict.get(m.sym, []):
                if s in recSet:
                    continue
                _updateItemRunListImpl(context, item, s, recSet)
    else:
        assert False
    context.itemRunList.sort()


def _updateItemRunListImpl(context, item, sym, recSet):
    recSet.add(sym)
    for si in context.symItemDict.get(sym, []):
        if _isVisibileAndConstraintRangeWider(context, si) and si not in context.itemRunList:
            context.itemRunList.append(si)
    if context.symValueDict[sym][0] != _symGetValue(sym):      # oldv != newv
        for s in context.symRefDict.get(sym, []):
            if s in recSet:
                continue
            _updateItemRunListImpl(context, item, s, recSet)


def _updateSymValueDict(context, item):
    recSet = set()
    if item.symbolMenu is not None:
        _updateSymValueDictImpl(context, item, item.symbolMenu.sym, recSet)
    elif item.choiceMenu is not None:
        for m in item.choiceMenu.list:
            if m.sym in recSet:
                continue
            _updateSymValueDictImpl(context, item, m.sym, recSet)
    else:
        assert False


def _updateSymValueDictImpl(context, item, sym, recSet):
    recSet.add(sym)

    oldv = context.symValueDict[sym]
    newv = _symGetValue(sym)
    if oldv == newv:
        return

    context.symValueDict[sym] = (_symGetValue(sym), sym.visible, sym.rev_dep.tri)
    for s in context.symRefDict.get(sym, []):
        if s in recSet:
            continue
        _updateSymValueDictImpl(context, item, s, recSet)


def _isVisibileAndConstraintRangeWider(context, item):
    if item.symbolMenu is not None:
        if context.symValueDict[item.symbolMenu.sym][1] < item.symbolMenu.sym.visible:
            return True
        if context.symValueDict[item.symbolMenu.sym][2] > item.symbolMenu.sym.rev_dep.tri:
            return True
        return False
    elif item.choiceMenu is not None:
        if context.symValueDict[item.choiceMenu.sym][1] < item.choiceMenu.sym.visible:
            return True
        if context.symValueDict[item.choiceMenu.sym][2] > item.choiceMenu.sym.rev_dep.tri:
            return True
        for m in item.choiceMenu.list:
            if context.symValueDict[m.sym][1] < m.sym.visible:
                return True
            if context.symValueDict[m.sym][2] > m.sym.rev_dep.tri:
                return True
        return False
    else:
        assert False


def _makeAllNoConfig():
    pylkc.conf_read(None)

    # clear all symbol setttings
    defaultValueDict = {"EXPERT": pylkc.tristate.yes, "EMBEDDED": pylkc.tristate.yes}
    while True:
        changed = False
        for sym in pylkc.all_symbols():
            sym.calc_value()
            if sym.is_choice_value():
                continue
            if sym.name in defaultValueDict:
                if sym.get_tristate_value() == defaultValueDict[sym.name]:
                    continue
                ret = sym.set_tristate_value(defaultValueDict[sym.name])
                if not ret:
                    raise InternalError("failed to set default value for symbol %s" % (sym.name))
            elif sym.get_type() in [pylkc.symbol.TYPE_BOOLEAN, pylkc.symbol.TYPE_TRISTATE]:
                if sym.get_tristate_value() == pylkc.tristate.no:
                    continue
                ret = sym.set_tristate_value(pylkc.tristate.no)
                if not ret:
                    continue
            else:
                continue
            changed = True
        if not changed:
            break


def _makeDefConfig(ksrcDir, arch):
    subarch = pylkc._get_sub_arch(arch)
    fn = os.path.join(ksrcDir, subarch, "%s_defconfig" % (arch))
    pylkc.conf_read(fn)


def _presetSymbol(context, symbolName, symbolValue):
    sym = pylkc.sym_find(symbolName)
    assert context.symValueDict[sym][0] == symbolValue
    context.symValueRecord[sym] = symbolValue
    context.symAltValueRecord[sym] = [symbolValue]


def _menuSetValue(context, menuObj, symbolValue):
    return _symSetValue(context, menuObj.sym, symbolValue)


def _symSetValue(context, sym, symbolValue):
    # if no need to modify, return directly
    if sym.get_type() == pylkc.symbol.TYPE_UNKNOWN:
        assert False
    elif sym.get_type() == pylkc.symbol.TYPE_BOOLEAN:
        assert symbolValue in ["y", "n"]
        if sym.get_tristate_value() == _str2tval(symbolValue):
            return False
    elif sym.get_type() == pylkc.symbol.TYPE_TRISTATE:
        assert symbolValue in ["y", "m", "n"]
        if sym.get_tristate_value() == _str2tval(symbolValue):
            return False
    elif sym.get_type() == pylkc.symbol.TYPE_INT:
        assert _is_int(symbolValue)
        if sym.get_string_value() == symbolValue:
            return False
    elif sym.get_type() == pylkc.symbol.TYPE_HEX:
        assert False
    elif sym.get_type() == pylkc.symbol.TYPE_STRING:
        if sym.get_string_value() == symbolValue:
            return False
    elif sym.get_type() == pylkc.symbol.TYPE_OTHER:
        assert False
    else:
        assert False

    # change value
    if sym.get_type() == pylkc.symbol.TYPE_BOOLEAN:
        ret = sym.set_tristate_value(_str2tval(symbolValue))
    elif sym.get_type() == pylkc.symbol.TYPE_TRISTATE:
        ret = sym.set_tristate_value(_str2tval(symbolValue))
    elif sym.get_type() == pylkc.symbol.TYPE_INT:
        ret = sym.set_string_value(symbolValue)
    elif sym.get_type() == pylkc.symbol.TYPE_STRING:
        ret = sym.set_string_value(symbolValue)
    else:
        assert False
    assert ret
    sym.calc_value()

    # calculate sym-ref value, try suppress sym-ref value change
    change = 9999
    while change > 0:
        change = 0
        for s in context.symRefDict.get(sym, []):
            change += _calcAndSuppressSymRef(context, sym, s)

    return True


def _setChoice(context, menuObj, choiceValue):
    bFound = False
    bNeedModify = False
    for m in menuObj.list:
        if m.sym.name == choiceValue:
            bFound = True
            if m.sym.get_tristate_value() == pylkc.tristate.no:
                bNeedModify = True
        else:
            if m.sym.get_tristate_value() != pylkc.tristate.no:
                bNeedModify = True
    assert bFound
    if not bNeedModify:
        return False

    # change value
    for m in menuObj.list:
        if m.sym.name == choiceValue:
            ret = m.sym.set_tristate_value(pylkc.tristate.yes)
            assert ret
    for m in menuObj.list:
        m.sym.calc_value()

    # calculate sym-ref value, try suppress sym-ref value change
    change = 9999
    while change > 0:
        change = 0
        for m in menuObj.list:
            for s in context.symRefDict.get(m.sym, []):
                change += _calcAndSuppressSymRef(context, m.sym, s)

    return True


def _calcAndSuppressSymRef(context, osym, sym):
    sym.calc_value()
#    if _symGetValue(sym) == context.symValueDict[sym][0]:
#        return 0

    change = 0
    if sym.visible > pylkc.tristate.no and sym.get_type() in [pylkc.symbol.TYPE_BOOLEAN, pylkc.symbol.TYPE_TRISTATE] and not sym.is_choice_value():
        ov = _str2tval(context.symValueDict[sym][0])
        if sym.get_tristate_value() == ov:
            return change
        nv = ov
        while True:
            if nv > sym.visible:
                nv -= 1
                if sym.get_type() == pylkc.symbol.TYPE_BOOLEAN and nv == pylkc.tristate.mod:
                    nv = pylkc.tristate.no
            elif nv < sym.rev_dep.tri:
                nv += 1
                if sym.get_type() == pylkc.symbol.TYPE_BOOLEAN and nv == pylkc.tristate.mod:
                    nv = pylkc.tristate.yes
            else:
                break
        if sym.get_tristate_value() != nv:
            ret = sym.set_tristate_value(nv)
            assert ret
            change = 1

    for s in context.symRefDict.get(sym, []):
        change += _calcAndSuppressSymRef(context, osym, s)

    return change


def _menuGetValue(menuObj):
    return _symGetValue(menuObj.sym)


def _symGetValue(sym):
    if sym.get_type() == pylkc.symbol.TYPE_UNKNOWN:
        return None
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
        return sym.get_string_value()
    elif sym.get_type() == pylkc.symbol.TYPE_HEX:
        return sym.get_string_value()
    elif sym.get_type() == pylkc.symbol.TYPE_STRING:
        return sym.get_string_value()
    elif sym.get_type() == pylkc.symbol.TYPE_OTHER:
        assert False
    else:
        assert False


def _getChoice(menuObj):
    for m in menuObj.list:
        if m.sym.get_tristate_value() != pylkc.tristate.no:
            return m.sym.name
    assert False


def _getMenuPath(menuObj):
    ret = ""
    while True:
        ret = "/" + pylkcx.path.escape(menuObj.get_prompt()) + ret
        if menuObj.get_parent_menu() == menuObj:
            break
        menuObj = menuObj.get_parent_menu()
    return ret


def _vlistFilterByVisibleAndSelectionConstraint(menuObj, vlist):
    ret = []
    for v in vlist:
        if _str2tval(v) < menuObj.sym.rev_dep.tri:
            continue
        if _str2tval(v) > menuObj.sym.visible:
            continue
        ret.append(v)
    return ret


def _allSymbolsInExpr(exprObj):
    ret = []
    if exprObj is None:
        return []
    if exprObj.type == pylkc.expr.TYPE_NONE:
        return []
    if exprObj.left is not None:
        if exprObj.type in [pylkc.expr.TYPE_OR, pylkc.expr.TYPE_AND, pylkc.expr.TYPE_NOT, pylkc.expr.TYPE_LIST]:
            ret += _allSymbolsInExpr(exprObj.left.expr)
        elif exprObj.type in [pylkc.expr.TYPE_EQUAL, pylkc.expr.TYPE_UNEQUAL, pylkc.expr.TYPE_LTH, pylkc.expr.TYPE_LEQ, pylkc.expr.TYPE_GTH, pylkc.expr.TYPE_GEQ, pylkc.expr.TYPE_SYMBOL, pylkc.expr.TYPE_RANGE]:
            ret.append(exprObj.left.sym)
        else:
            assert False
    if exprObj.right is not None:
        if exprObj.type in [pylkc.expr.TYPE_OR, pylkc.expr.TYPE_AND, pylkc.expr.TYPE_NOT, pylkc.expr.TYPE_LIST]:
            ret += _allSymbolsInExpr(exprObj.right.expr)
        elif exprObj.type in [pylkc.expr.TYPE_EQUAL, pylkc.expr.TYPE_UNEQUAL, pylkc.expr.TYPE_LTH, pylkc.expr.TYPE_LEQ, pylkc.expr.TYPE_GTH, pylkc.expr.TYPE_GEQ, pylkc.expr.TYPE_RANGE]:
            ret.append(exprObj.right.sym)
        else:
            assert False
    return ret


def _isSymbolInExpr(sym, exprObj):
    if exprObj is None:
        return False
    if exprObj.type == pylkc.expr.TYPE_NONE:
        return False

    if exprObj.left is not None:
        if exprObj.type in [pylkc.expr.TYPE_OR, pylkc.expr.TYPE_AND, pylkc.expr.TYPE_NOT, pylkc.expr.TYPE_LIST]:
            if _isSymbolInExpr(sym, exprObj.left.expr):
                return True
        elif exprObj.type in [pylkc.expr.TYPE_EQUAL, pylkc.expr.TYPE_UNEQUAL, pylkc.expr.TYPE_SYMBOL, pylkc.expr.TYPE_RANGE]:
            if exprObj.left.sym == sym:
                return True
        else:
            assert False
    if exprObj.right is not None:
        if exprObj.type in [pylkc.expr.TYPE_OR, pylkc.expr.TYPE_AND, pylkc.expr.TYPE_NOT, pylkc.expr.TYPE_LIST]:
            if _isSymbolInExpr(sym, exprObj.right.expr):
                return True
        elif exprObj.type in [pylkc.expr.TYPE_EQUAL, pylkc.expr.TYPE_UNEQUAL, pylkc.expr.TYPE_RANGE]:
            return exprObj.right.sym == sym
            if exprObj.right.sym == sym:
                return True
        else:
            assert False
    return False


def _is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def _str2tval(s):
    vdict = {"y": pylkc.tristate.yes, "m": pylkc.tristate.mod, "n": pylkc.tristate.no}
    return vdict[s]


def _tval2str(t):
    vdict = {pylkc.tristate.yes: "y", pylkc.tristate.mod: "m", pylkc.tristate.no: "n"}
    return vdict[t]


def _str2vlist(s):
    return s.split(",")


def _vlist2str(vlist):
    return ",".join(vlist)


def _merge_vlist(vlist1, vlist2):
    # example: [m, y] + [y, n] = [y]
    #          [m, n] + [n, m] = [m]
    #          [n, m, y] + [m, y] = [m, y]
    #          [m] + [y] = []
    ret = []
    s = 0
    for v in vlist2:
        try:
            i = vlist1.index(v)
            if i < s:
                continue
            ret.append(v)
            s = i
        except ValueError:
            pass
    return ret


def _strip_vlist(vlist, v):
    return vlist[vlist.index(v):]
