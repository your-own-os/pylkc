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

"""
pylkc

@author: Fpemud
@license: GPLv3 License
@contact: fpemud@sina.com
"""

__author__ = "fpemud@sina.com (Fpemud)"
__version__ = "0.0.1"

import os
import re
import ctypes
import subprocess
import builtins
from . import api
from pylkcx import path


class tristate:
    no = 0
    mod = 1
    yes = 2


class menu:

    def __init__(self, c_menu_p):
        assert c_menu_p and isinstance(c_menu_p, ctypes.POINTER(api.struct_menu))
        self.c_menu_p = c_menu_p

    @property
    def list(self):
        ret = []
        p_menu = self.c_menu_p.contents.list
        while p_menu:
            ret.append(menu(p_menu))
            p_menu = p_menu.contents.next
        return ret

    @property
    def sym(self):
        if self.c_menu_p.contents.sym:
            return symbol(self.c_menu_p.contents.sym)
        else:
            return None

    @property
    def prompt(self):
        if self.c_menu_p.contents.prompt:
            return property(self.c_menu_p.contents.prompt)
        else:
            return None

    def is_empty(self):
        """Determine if a menu is empty.
           A menu is considered empty if it contains no or only
           invisible entries."""
        return api.library.menu_is_empty(self.c_menu_p) != bytes([0])

    def is_visible(self):
        return api.library.menu_is_visible(self.c_menu_p) != bytes([0])

    def has_prompt(self):
        return api.library.menu_has_prompt(self.c_menu_p) != bytes([0])

    def get_prompt(self):
        ret = api.library.menu_get_prompt(self.c_menu_p)
        return ret.decode("utf_8") if ret else None

    def get_root_menu(self):
        return menu(api.library.menu_get_root_menu(self.c_menu_p))

    def get_parent_menu(self):
        return menu(api.library.menu_get_parent_menu(self.c_menu_p))

    def has_help(self):
        return api.library.menu_has_help(self.c_menu_p) != bytes([0])

    def get_help(self):
        return api.library.menu_get_help(self.c_menu_p).decode("utf_8")

    def __eq__(self, other):
        return ctypes.addressof(self.c_menu_p.contents) == ctypes.addressof(other.c_menu_p.contents)

    def __ne__(self, other):
        return ctypes.addressof(self.c_menu_p.contents) != ctypes.addressof(other.c_menu_p.contents)

    def __hash__(self):
        return ctypes.addressof(self.c_menu_p.contents)


class symbol:

    TYPE_UNKNOWN = 0
    TYPE_BOOLEAN = 1
    TYPE_TRISTATE = 2
    TYPE_INT = 3
    TYPE_HEX = 4
    TYPE_STRING = 5
    TYPE_OTHER = 6

    def __init__(self, c_symbol_p):
        assert c_symbol_p and isinstance(c_symbol_p, ctypes.POINTER(api.struct_symbol))
        self.c_symbol_p = c_symbol_p

    @property
    def name(self):
        if self.c_symbol_p.contents.name:
            return self.c_symbol_p.contents.name.decode("utf_8")
        else:
            return None

    @property
    def dir_dep(self):
        # corresponds to the "Depends on" field
        return expr_value(ctypes.pointer(self.c_symbol_p.contents.dir_dep))

    @property
    def rev_dep(self):
        # corresponds to the "Selected by" field
        return expr_value(ctypes.pointer(self.c_symbol_p.contents.rev_dep))

    @property
    def visible(self):
        return self.c_symbol_p.contents.visible

    def calc_value(self):
        api.library.sym_calc_value(self.c_symbol_p)

    def get_type(self):
        return int(api.library.sym_get_type(self.c_symbol_p))

    def has_value(self):
        return (self.c_symbol_p.contents.flags & api.SYMBOL_DEF_USER) != 0

    def tristate_within_range(self, tri):
        assert tristate.no <= tri <= tristate.yes
        return api.library.sym_tristate_within_range(self.c_symbol_p, ctypes.c_int(tri)) != bytes([0])

    def set_tristate_value(self, tri):
        assert tristate.no <= tri <= tristate.yes
        return api.library.sym_set_tristate_value(self.c_symbol_p, ctypes.c_int(tri)) != bytes([0])

    def toggle_tristate_value(self):
        return int(api.library.sym_toggle_tristate_value(self.c_symbol_p))

    def get_tristate_value(self):
        return int(self.c_symbol_p.contents.curr.tri)

    def string_valid(self, val):
        return api.library.sym_string_valid(self.c_symbol_p, ctypes.c_char_p(val.encode("utf_8"))) != bytes([0])

    def string_within_range(self, val):
        return api.library.sym_string_within_range(self.c_symbol_p, ctypes.c_char_p(val.encode("utf_8"))) != bytes([0])

    def set_string_value(self, newval):
        return api.library.sym_set_string_value(self.c_symbol_p, ctypes.c_char_p(newval.encode("utf_8"))) != bytes([0])

    def get_string_value(self):
        return api.library.sym_get_string_value(self.c_symbol_p).decode("utf_8")

    def is_choice(self):
        return (self.c_symbol_p.contents.flags & api.SYMBOL_CHOICE) != 0

    def is_choice_value(self):
        return (self.c_symbol_p.contents.flags & api.SYMBOL_CHOICEVAL) != 0

    def is_optional(self):
        return (self.c_symbol_p.contents.flags & api.SYMBOL_OPTIONAL) != 0

    def get_choice_prop(self):
        ret = api.library.sym_get_choice_prop(self.c_symbol_p)
        return property(ret) if ret else None

    def get_default_prop(self):
        ret = api.library.sym_get_default_prop(self.c_symbol_p)
        return property(ret) if ret else None

    def set_choice_value(self, chval):
        return chval.set_tristate_value(tristate.yes)

    def get_choice_value(self):
        return symbol(self.c_symbol_p.contents.curr.val)

    def get_properties(self, prop_type=None):
        assert prop_type is None or property.TYPE_UNKNOWN <= prop_type <= property.TYPE_SYMBOL

        st = self.c_symbol_p.contents.prop
        ret = []
        while st:
            if prop_type is None or st.contents.type == prop_type:
                ret.append(property(st))
            st = st.contents.next
        return ret

    def __eq__(self, other):
        return ctypes.addressof(self.c_symbol_p.contents) == ctypes.addressof(other.c_symbol_p.contents)

    def __ne__(self, other):
        return ctypes.addressof(self.c_symbol_p.contents) != ctypes.addressof(other.c_symbol_p.contents)

    def __hash__(self):
        return ctypes.addressof(self.c_symbol_p.contents)


class property:

    TYPE_UNKNOWN = 0
    TYPE_PROMPT = 1
    TYPE_COMMENT = 2
    TYPE_MENU = 3
    TYPE_DEFAULT = 4
    TYPE_CHOICE = 5
    TYPE_SELECT = 6
    TYPE_RANGE = 7
    TYPE_ENV = 8
    TYPE_SYMBOL = 9

    def __init__(self, c_property_p):
        assert c_property_p and isinstance(c_property_p, ctypes.POINTER(api.struct_property))
        self.c_property_p = c_property_p

    @builtins.property
    def type(self):
        return int(self.c_property_p.contents.type)

    @builtins.property
    def expr(self):
        return expr(self.c_property_p.contents.expr)

    def get_symbol(self):
        """An obscure interface, please check the use case in kernel source for detail"""
        ret = api.library.prop_get_symbol(self.c_property_p)
        return symbol(ret) if ret else None

    def __eq__(self, other):
        return ctypes.addressof(self.c_property_p.contents) == ctypes.addressof(other.c_property_p.contents)

    def __ne__(self, other):
        return ctypes.addressof(self.c_property_p.contents) != ctypes.addressof(other.c_property_p.contents)

    def __hash__(self):
        return ctypes.addressof(self.c_property_p.contents)


class expr:

    TYPE_NONE = 0
    TYPE_OR = 1
    TYPE_AND = 2
    TYPE_NOT = 3
    TYPE_EQUAL = 4
    TYPE_UNEQUAL = 5
    TYPE_LTH = 6            # less than
    TYPE_LEQ = 7            # less than or equal
    TYPE_GTH = 8            # greater than
    TYPE_GEQ = 9            # greater than or equal
    TYPE_LIST = 10
    TYPE_SYMBOL = 11
    TYPE_RANGE = 12

    def __init__(self, c_expr_p):
        """c_expr_p can be NULL!
           expr object with a NULL pointer has the following features:
             1. always evaluates to yes
             2. type == TYPE_NONE
             3. left == None
             4. right == None"""
        assert not c_expr_p or isinstance(c_expr_p, ctypes.POINTER(api.struct_expr))
        self.c_expr_p = c_expr_p

    @builtins.property
    def type(self):
        if self.c_expr_p:
            if _kver_int_less_than("4.2"):
                v = int(self.c_expr_p.contents.type)
                if v < expr.TYPE_UNEQUAL:
                    return v
                elif v < 9:
                    return v + 4         # linux-4.2 inserts 4 new enum value LTH,LEQ,GTH,GEQ before LIST
                else:
                    assert False
            else:
                v = int(self.c_expr_p.contents.type)
                assert v <= expr.TYPE_RANGE
                return v
        else:
            return expr.TYPE_NONE

    @builtins.property
    def left(self):
        if self.c_expr_p and self.c_expr_p.contents.left:
            if self.type == expr.TYPE_NONE:
                assert False
            elif self.type == expr.TYPE_OR:
                expr_or_sym = True                  # expr
            elif self.type == expr.TYPE_AND:
                expr_or_sym = True                  # expr
            elif self.type == expr.TYPE_NOT:
                expr_or_sym = True                  # expr
            elif self.type == expr.TYPE_EQUAL:
                expr_or_sym = False                 # sym
            elif self.type == expr.TYPE_UNEQUAL:
                expr_or_sym = False                 # sym
            elif self.type == expr.TYPE_LTH:
                expr_or_sym = False                 # sym
            elif self.type == expr.TYPE_LEQ:
                expr_or_sym = False                 # sym
            elif self.type == expr.TYPE_GTH:
                expr_or_sym = False                 # sym
            elif self.type == expr.TYPE_GEQ:
                expr_or_sym = False                 # sym
            elif self.type == expr.TYPE_LIST:
                expr_or_sym = True                  # expr
            elif self.type == expr.TYPE_SYMBOL:
                expr_or_sym = False                 # sym
            elif self.type == expr.TYPE_RANGE:
                expr_or_sym = False                 # sym
            else:
                assert False
            return expr_data(ctypes.pointer(self.c_expr_p.contents.left), expr_or_sym)
        else:
            return None

    @builtins.property
    def right(self):
        if self.c_expr_p and self.c_expr_p.contents.right:
            if self.type == expr.TYPE_NONE:
                assert False
            elif self.type == expr.TYPE_OR:
                expr_or_sym = True                  # expr
            elif self.type == expr.TYPE_AND:
                expr_or_sym = True                  # expr
            elif self.type == expr.TYPE_NOT:
                expr_or_sym = True                  # expr
            elif self.type == expr.TYPE_EQUAL:
                expr_or_sym = False                 # sym
            elif self.type == expr.TYPE_UNEQUAL:
                expr_or_sym = False                 # sym
            elif self.type == expr.TYPE_LTH:
                expr_or_sym = False                 # sym
            elif self.type == expr.TYPE_LEQ:
                expr_or_sym = False                 # sym
            elif self.type == expr.TYPE_GTH:
                expr_or_sym = False                 # sym
            elif self.type == expr.TYPE_GEQ:
                expr_or_sym = False                 # sym
            elif self.type == expr.TYPE_LIST:
                expr_or_sym = True                  # expr
            elif self.type == expr.TYPE_SYMBOL:
                #assert False --fixme
                return None
            elif self.type == expr.TYPE_RANGE:
                expr_or_sym = False                 # sym
            else:
                assert False
            return expr_data(ctypes.pointer(self.c_expr_p.contents.right), expr_or_sym)
        else:
            return None

    def calc_value(self):
        return int(api.library.expr_calc_value(self.c_expr_p))

    def __eq__(self, other):
        return ctypes.addressof(self.c_expr_p.contents) == ctypes.addressof(other.c_expr_p.contents)

    def __ne__(self, other):
        return ctypes.addressof(self.c_expr_p.contents) != ctypes.addressof(other.c_expr_p.contents)

    def __hash__(self):
        return ctypes.addressof(self.c_expr_p.contents)


class expr_data:

    def __init__(self, c_expr_data_p, expr_or_sym):
        assert c_expr_data_p and isinstance(c_expr_data_p, ctypes.POINTER(api.union_expr_data))
        assert isinstance(expr_or_sym, bool)
        self.c_expr_data_p = c_expr_data_p
        self.expr_or_sym = expr_or_sym

    @builtins.property
    def expr(self):
        assert self.expr_or_sym
        return expr(self.c_expr_data_p.contents.expr)

    @builtins.property
    def sym(self):
        assert not self.expr_or_sym
        return symbol(self.c_expr_data_p.contents.sym)


class expr_value:

    def __init__(self, c_expr_value_p):
        assert c_expr_value_p and isinstance(c_expr_value_p, ctypes.POINTER(api.struct_expr_value))
        self.c_expr_value_p = c_expr_value_p

    @builtins.property
    def expr(self):
        if self.c_expr_value_p.contents.expr:
            return expr(self.c_expr_value_p.contents.expr)
        else:
            return None

    @builtins.property
    def tri(self):
        return int(self.c_expr_value_p.contents.tri)

    def __eq__(self, other):
        return ctypes.addressof(self.c_expr_value_p.contents) == ctypes.addressof(other.c_expr_value_p.contents)

    def __ne__(self, other):
        return ctypes.addressof(self.c_expr_value_p.contents) != ctypes.addressof(other.c_expr_value_p.contents)

    def __hash__(self):
        return ctypes.addressof(self.c_expr_value_p.contents)


class VersionError(Exception):
    pass


def init(kernel_src_path):
    global rootmenu
    global _all_symbols_list
    global _sym_menu_dict
    global _kver_int

    _kver_int = _get_kver_int(kernel_src_path)
    if _kver_int_less_than("3.16"):
        raise VersionError("pylkc only supports kernel 3.16 and later")

    api.init_library(kernel_src_path)

    # disable all message output
    api.library.conf_set_message_callback(None)

    # use the same algorithm as the linux kernel root Makefile
    if "ARCH" not in os.environ:
        os.environ["ARCH"] = _get_sub_arch()
    os.environ["SRCARCH"] = os.environ["ARCH"]
    if os.environ["ARCH"] == "i386":
        os.environ["SRCARCH"] = "x86"
    if os.environ["ARCH"] == "x86_64":
        os.environ["SRCARCH"] = "x86"
    if os.environ["ARCH"] == "sparc32":
        os.environ["SRCARCH"] = "sparc"
    if os.environ["ARCH"] == "sparc64":
        os.environ["SRCARCH"] = "sparc"
    if os.environ["ARCH"] == "sh64":
        os.environ["SRCARCH"] = "sh"
    if os.environ["ARCH"] == "tilepro":
        os.environ["SRCARCH"] = "tile"
    if os.environ["ARCH"] == "tilegx":
        os.environ["SRCARCH"] = "tile"
    os.environ["KERNELVERSION"] = _get_kernel_version(kernel_src_path)
    os.environ["srctree"] = kernel_src_path
    os.environ["CC"] = "gcc"

    _all_symbols_list = []
    _sym_menu_dict = dict()


def release():
    global rootmenu
    global _all_symbols_list
    global _sym_menu_dict
    global _kver_int

    _kver_int = None
    _sym_menu_dict = None
    _all_symbols_list = None
    rootmenu = None
    api.fini_library()


def conf_parse(kernel_src_path):
    global rootmenu
    global _all_symbols_list
    global _sym_menu_dict

    curdir = os.getcwd()
    os.chdir(kernel_src_path)
    try:
        api.library.conf_parse(ctypes.c_char_p(os.path.join(kernel_src_path, "Kconfig").encode("utf_8")))
        rootmenu = menu(api.library.menu_get_root_menu(None))
        _generate_all_symbols_list(_all_symbols_list)
        _generate_sym_menu_dict(rootmenu, _sym_menu_dict)
    finally:
        os.chdir(curdir)


def conf_read(filename):
    if filename is not None:
        api.library.conf_read(ctypes.c_char_p(filename.encode("utf_8")))
    else:
        api.library.conf_read(ctypes.c_char_p(filename))


def conf_write(filename):
    if filename is not None:
        api.library.conf_write(ctypes.c_char_p(filename.encode("utf_8")))
    else:
        api.library.conf_write(ctypes.c_char_p(filename))


def all_symbols():
    global _all_symbols_list
    return _all_symbols_list


def sym_lookup(symbol_name, flags):
    assert False


def sym_find(symbol_name):
    ret = api.library.sym_find(ctypes.c_char_p(symbol_name.encode("utf_8")))
    return symbol(ret) if ret else None


def sym_escape_string_value(in_str):
    return api.library.sym_escape_string_value(ctypes.c_char_p(in_str.encode("utf_8"))).decode("utf_8")


def menu_find_by_path(menu_path, fuzzy=False):
    global rootmenu
    assert path.isabs(menu_path)

    curitem = rootmenu
    for p in path._full_split(menu_path)[1:]:
        found = None
        for m in curitem.list:
            if m.get_prompt() is not None:
                if fuzzy:
                    if path.compare_fuzzy(path.escape(m.get_prompt()), p):
                        found = m
                        break
                else:
                    if path.compare(path.escape(m.get_prompt()), p):
                        found = m
                        break
        if found is not None:
            curitem = found
        else:
            return None
    return curitem


def menu_find_by_sym(sym_obj):
    global _sym_menu_dict
    return _sym_menu_dict.get(sym_obj, None)


rootmenu = None


############## implementations ################################################


_all_symbols_list = None
_sym_menu_dict = None
_kver_int = None


def _get_sub_arch():
    # use the same algorithm as the linux kernel root Makefile
    cmd = "/usr/bin/uname -m | /bin/sed -e s/i.86/x86/ -e s/x86_64/x86/" \
          "                             -e s/sun4u/sparc64/" \
          "                             -e s/arm.*/arm/ -e s/sa110/arm/" \
          "                             -e s/s390x/s390/ -e s/parisc64/parisc/" \
          "                             -e s/ppc.*/powerpc/ -e s/mips.*/mips/" \
          "                             -e s/sh[234].*/sh/ -e s/aarch64.*/arm64/"
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out = proc.communicate()[0]
    assert proc.returncode == 0
    return out.decode("utf_8").rstrip()


def _get_kernel_version(kernel_src_path):
    # use the same algorithm as the linux kernel root Makefile
    buf = ""
    with open(os.path.join(kernel_src_path, "Makefile")) as f:
        buf = f.read()

    version = re.search("^VERSION =(.*)$", buf, re.M).group(1).strip()
    patch_level = re.search("^PATCHLEVEL =(.*)$", buf, re.M).group(1).strip()
    sub_level = re.search("^SUBLEVEL =(.*)$", buf, re.M).group(1).strip()
    extra_version = re.search("^EXTRAVERSION =(.*)$", buf, re.M).group(1).strip()

    ret = version
    if patch_level != "":
        ret += ".%s" % (patch_level)
    if sub_level != "":
        ret += ".%s" % (sub_level)
    ret += extra_version

    return ret


def _get_kver_int(kernel_src_path):
    # use the same algorithm as the linux kernel root Makefile
    buf = ""
    with open(os.path.join(kernel_src_path, "Makefile")) as f:
        buf = f.read()

    version = re.search("^VERSION =(.*)$", buf, re.M).group(1).strip()
    patch_level = re.search("^PATCHLEVEL =(.*)$", buf, re.M).group(1).strip()
    sub_level = re.search("^SUBLEVEL =(.*)$", buf, re.M).group(1).strip()

    ret = int(version) * 100 * 1000
    ret += int(patch_level) * 1000
    ret += int(sub_level)
    return ret


def _kver_int_less_than(kernel_version):
    global _kver_int

    vlist = kernel_version.split(".")
    ret = int(vlist[0]) * 100 * 1000
    if len(vlist) > 1:
        ret += int(vlist[1]) * 1000
    if len(vlist) > 2:
        ret += int(vlist[2])

    return _kver_int < ret


def _generate_all_symbols_list(list_obj):
    for i in range(0, api.SYMBOL_HASHSIZE):
        p_sym = api.library.g_symbol_hash[i]
        while p_sym:
            if p_sym.contents.type != api.S_OTHER:
                list_obj.append(symbol(p_sym))
            p_sym = p_sym.contents.next


def _generate_sym_menu_dict(menu_obj, dict_obj):
    if menu_obj.sym is not None:
        dict_obj[menu_obj.sym] = menu_obj
    for m in menu_obj.list:
        _generate_sym_menu_dict(m, dict_obj)
