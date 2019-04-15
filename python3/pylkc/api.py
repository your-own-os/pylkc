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

import os
import shutil
import subprocess
import ctypes


library = None


def init_library(kernel_src_path):
    global _kernel_src_path
    global _kcfg_path
    global _so_file
    global library

    assert _kernel_src_path == ""

    _kernel_src_path = kernel_src_path
    _kcfg_path = os.path.join(_kernel_src_path, "scripts", "kconfig")
    _so_file = os.path.join(_kcfg_path, "pylkc.so")

    _build_so_file()

    library = ctypes.CDLL(_so_file)
    if True:
        # void conf_parse(const char *name)
        library.conf_parse.argtypes = [ctypes.c_char_p]
        library.conf_parse.restype = None

        # int conf_read(const char *name)
        library.conf_read.argtypes = [ctypes.c_char_p]
        library.conf_read.restype = ctypes.c_int

        # int conf_write(const char *name)
        library.conf_write.argtypes = [ctypes.c_char_p]
        library.conf_write.restype = ctypes.c_int

        # void conf_set_changed_callback(void (*fn)(void))
        library.conf_set_changed_callback.argtypes = [ctypes.c_void_p]                 # simplified, argument type is not important
        library.conf_set_changed_callback.restype = None

        # void conf_set_message_callback(void (*fn) (const char *fmt, va_list ap))
        library.conf_set_message_callback.argtypes = [ctypes.c_void_p]                 # simplified, argument type is not important
        library.conf_set_message_callback.restype = None

        # bool menu_is_empty(struct menu *menu)
        library.menu_is_empty.argtypes = [ctypes.POINTER(struct_menu)]
        library.menu_is_empty.restype = ctypes.c_char

        # bool menu_is_visible(struct menu *menu)
        library.menu_is_visible.argtypes = [ctypes.POINTER(struct_menu)]
        library.menu_is_visible.restype = ctypes.c_char

        # bool menu_has_prompt(struct menu *menu)
        library.menu_has_prompt.argtypes = [ctypes.POINTER(struct_menu)]
        library.menu_has_prompt.restype = ctypes.c_char

        # const char *menu_get_prompt(struct menu *menu)
        library.menu_get_prompt.argtypes = [ctypes.POINTER(struct_menu)]
        library.menu_get_prompt.restype = ctypes.c_char_p

        # struct menu *menu_get_root_menu(struct menu *menu)
        library.menu_get_root_menu.argtypes = [ctypes.POINTER(struct_menu)]
        library.menu_get_root_menu.restype = ctypes.POINTER(struct_menu)

        # struct menu *menu_get_parent_menu(struct menu *menu)
        library.menu_get_parent_menu.argtypes = [ctypes.POINTER(struct_menu)]
        library.menu_get_parent_menu.restype = ctypes.POINTER(struct_menu)

        # bool menu_has_help(struct menu *menu)
        library.menu_has_help.argtypes = [ctypes.POINTER(struct_menu)]
        library.menu_has_help.restype = ctypes.c_char

        # const char *menu_get_help(struct menu *menu)
        library.menu_get_help.argtypes = [ctypes.POINTER(struct_menu)]
        library.menu_get_help.restype = ctypes.c_char_p

        # struct symbol *sym_lookup(const char *name, int flags)
        library.sym_lookup.argtypes = [ctypes.c_char_p, ctypes.c_int]
        library.sym_lookup.restype = ctypes.POINTER(struct_symbol)

        # struct symbol *sym_find(const char *name)
        library.sym_find.argtypes = [ctypes.c_char_p]
        library.sym_find.restype = ctypes.POINTER(struct_symbol)

        # const char *sym_escape_string_value(const char *in)
        library.sym_escape_string_value.argtypes = [ctypes.c_char_p]
        library.sym_escape_string_value.restype = ctypes.c_char_p

        # void sym_calc_value(struct symbol *sym)
        library.sym_calc_value.argtypes = [ctypes.POINTER(struct_symbol)]
        library.sym_calc_value.restype = None

        # enum symbol_type sym_get_type(struct symbol *sym)
        library.sym_get_type.argtypes = [ctypes.POINTER(struct_symbol)]
        library.sym_get_type.restype = ctypes.c_int

        # bool sym_tristate_within_range(struct symbol *sym, tristate val)
        library.sym_tristate_within_range.argtypes = [ctypes.POINTER(struct_symbol), ctypes.c_int]
        library.sym_tristate_within_range.restype = ctypes.c_char

        # bool sym_set_tristate_value(struct symbol *sym, tristate val)
        library.sym_set_tristate_value.argtypes = [ctypes.POINTER(struct_symbol), ctypes.c_int]
        library.sym_set_tristate_value.restype = ctypes.c_char

        # tristate sym_toggle_tristate_value(struct symbol *sym)
        library.sym_toggle_tristate_value.argtypes = [ctypes.POINTER(struct_symbol)]
        library.sym_toggle_tristate_value.restype = ctypes.c_int

        # bool sym_string_valid(struct symbol *sym, const char *str)
        library.sym_string_valid.argtypes = [ctypes.POINTER(struct_symbol), ctypes.c_char_p]
        library.sym_string_valid.restype = ctypes.c_char

        # bool sym_string_within_range(struct symbol *sym, const char *str)
        library.sym_string_within_range.argtypes = [ctypes.POINTER(struct_symbol), ctypes.c_char_p]
        library.sym_string_within_range.restype = ctypes.c_char

        # bool sym_set_string_value(struct symbol *sym, const char *newval)
        library.sym_set_string_value.argtypes = [ctypes.POINTER(struct_symbol), ctypes.c_char_p]
        library.sym_set_string_value.restype = ctypes.c_char

        # bool sym_is_changable(struct symbol *sym)
        library.sym_is_changable.argtypes = [ctypes.POINTER(struct_symbol)]
        library.sym_is_changable.restype = ctypes.c_char

        # struct property *sym_get_choice_prop(struct symbol *sym)
        library.sym_get_choice_prop.argtypes = [ctypes.POINTER(struct_symbol)]
        library.sym_get_choice_prop.restype = ctypes.POINTER(struct_property)

        # this changes to static in linux-4.1.1, so we have no easy access
        # struct property *sym_get_default_prop(struct symbol *sym)
        #library.sym_get_default_prop.argtypes = [ctypes.POINTER(struct_symbol)]
        #library.sym_get_default_prop.restype = ctypes.POINTER(struct_property)

        # const char *sym_get_string_value(struct symbol *sym)
        library.sym_get_string_value.argtypes = [ctypes.POINTER(struct_symbol)]
        library.sym_get_string_value.restype = ctypes.c_char_p

        # struct symbol *prop_get_symbol(struct property *prop)
        library.prop_get_symbol.argtypes = [ctypes.POINTER(struct_property)]
        library.prop_get_symbol.restype = ctypes.POINTER(struct_symbol)

        # tristate expr_calc_value(struct expr *e)
        library.expr_calc_value.argtypes = [ctypes.POINTER(struct_expr)]
        library.expr_calc_value.restype = ctypes.c_int

        # struct symbol *symbol_hash[SYMBOL_HASHSIZE]
        g_symbol_hash_type = ctypes.POINTER(struct_symbol) * SYMBOL_HASHSIZE
        library.g_symbol_hash = g_symbol_hash_type.in_dll(library, "symbol_hash")


def fini_library():
    global _kernel_src_path
    global _kcfg_path
    global _so_file
    global library

    assert _kernel_src_path != ""

    del library
    library = None
    library = library       # trick: to suppress pyflakes warning

    _clean_so_file()

    _so_file = ""
    _kcfg_path = ""
    _kernel_src_path = ""


# typedef enum tristate {
#         no, mod, yes
# } tristate;
tristate_no = 0
tristate_mod = 1
tristate_yes = 2

# enum expr_type { };
E_NONE = 0
E_OR = 1
E_AND = 2
E_NOT = 3
E_EQUAL = 4
E_UNEQUAL = 5
E_LTH = 6
E_LEQ = 7
E_GTH = 8
E_GEQ = 9
E_LIST = 10
E_SYMBOL = 11
E_RANGE = 12

# enum prop_type { };
P_UNKNOWN = 0
P_PROMPT = 1
P_COMMENT = 2
P_MENU = 3
P_DEFAULT = 4
P_CHOICE = 5
P_SELECT = 6
P_RANGE = 7
P_ENV = 8
P_SYMBOL = 9

# enum symbol_type { };
S_UNKNOWN = 0
S_BOOLEAN = 1
S_TRISTATE = 2
S_INT = 3
S_HEX = 4
S_STRING = 5
S_OTHER = 6

# symbol data structure macros
SYMBOL_MAXLENGTH = 256
SYMBOL_HASHSIZE = 9973

# symbol flag value macros
SYMBOL_CONST = 0x0001
SYMBOL_CHECK = 0x0008
SYMBOL_CHOICE = 0x0010
SYMBOL_CHOICEVAL = 0x0020
SYMBOL_VALID = 0x0080
SYMBOL_OPTIONAL = 0x0100
SYMBOL_WRITE = 0x0200
SYMBOL_CHANGED = 0x0400
SYMBOL_AUTO = 0x1000
SYMBOL_CHECKED = 0x2000
SYMBOL_WARNED = 0x8000
SYMBOL_DEF = 0x10000
SYMBOL_DEF_USER = 0x10000
SYMBOL_DEF_AUTO = 0x20000
SYMBOL_DEF3 = 0x40000
SYMBOL_DEF4 = 0x80000

# enum {
#         S_DEF_USER,        /* main user value */
#         S_DEF_AUTO,        /* values read from auto.conf */
#         S_DEF_DEF3,        /* Reserved for UI usage */
#         S_DEF_DEF4,        /* Reserved for UI usage */
#         S_DEF_COUNT
# };
S_DEF_USER = 0
S_DEF_AUTO = 1
S_DEF_DEF3 = 2
S_DEF_DEF4 = 3
S_DEF_COUNT = 4


class struct_menu(ctypes.Structure):
    pass


class struct_symbol(ctypes.Structure):
    pass


class struct_symbol_value(ctypes.Structure):
    pass


class struct_property(ctypes.Structure):
    pass


class struct_expr(ctypes.Structure):
    pass


class union_expr_data(ctypes.Union):
    pass


class struct_expr_value(ctypes.Structure):
    pass


# union expr_data {
#         struct expr *expr;
#         struct symbol *sym;
# };
union_expr_data._fields_ = [("expr", ctypes.POINTER(struct_expr)),
                            ("sym", ctypes.POINTER(struct_symbol)), ]

# struct expr_value {
#         struct expr *expr;
#         tristate tri;
# };
struct_expr_value._fields_ = [("expr", ctypes.POINTER(struct_expr)),
                              ("tri", ctypes.c_int), ]

# struct expr {
#         enum expr_type type;
#         union expr_data left, right;
# };
struct_expr._fields_ = [("type", ctypes.c_int),
                        ("left", union_expr_data),
                        ("right", union_expr_data), ]

# struct property {
#         struct property *next;
#         struct symbol *sym;
#         enum prop_type type;
#         const char *text;
#         struct expr_value visible;
#         struct expr *expr;
#         struct menu *menu;
#         struct file *file;
#         int lineno;
# };
struct_property._fields_ = [("next", ctypes.POINTER(struct_property)),
                            ("sym", ctypes.POINTER(struct_symbol)),
                            ("type", ctypes.c_int),
                            ("visible", struct_expr_value),
                            ("expr", ctypes.POINTER(struct_expr)),
                            ("menu", ctypes.POINTER(struct_menu)),
                            ("file", ctypes.c_void_p),                     # simplified, nobody use it
                            ("lineno", ctypes.c_int), ]

# struct symbol_value {
#         void *val;
#         tristate tri;
# };
struct_symbol_value._fields_ = [("val", ctypes.c_void_p),
                                ("tri", ctypes.c_int), ]

# struct symbol {
#         struct symbol *next;
#         char *name;
#         enum symbol_type type;
#         struct symbol_value curr;
#         struct symbol_value def[S_DEF_COUNT];
#         tristate visible;
#         int flags;
#         struct property *prop;
#         struct expr_value dir_dep;
#         struct expr_value rev_dep;
# };
struct_symbol._fields_ = [("next", ctypes.POINTER(struct_symbol)),
                          ("name", ctypes.c_char_p),
                          ("type", ctypes.c_int),
                          ("curr", struct_symbol_value),
                          ("def", struct_symbol_value * S_DEF_COUNT),
                          ("visible", ctypes.c_int),
                          ("flags", ctypes.c_int),
                          ("prop", ctypes.POINTER(struct_property)),
                          ("dir_dep", struct_expr_value),
                          ("rev_dep", struct_expr_value), ]

# struct menu {
#         struct menu *next;
#         struct menu *parent;
#         struct menu *list;
#         struct symbol *sym;
#         struct property *prompt;
#         struct expr *visibility;
#         struct expr *dep;
#         unsigned int flags;
#         char *help;
#         struct file *file;
#         int lineno;
#         void *data;
# };
struct_menu._fields_ = [("next", ctypes.POINTER(struct_menu)),
                        ("parent", ctypes.POINTER(struct_menu)),
                        ("list", ctypes.POINTER(struct_menu)),
                        ("sym", ctypes.POINTER(struct_symbol)),
                        ("prompt", ctypes.POINTER(struct_property)),
                        ("visibility", ctypes.POINTER(struct_expr)),
                        ("dep", ctypes.POINTER(struct_expr)),
                        ("flags", ctypes.c_uint),
                        ("help", ctypes.c_char_p),
                        ("file", ctypes.c_void_p),                     # simplified, nobody use it
                        ("lineno", ctypes.c_int),
                        ("data", ctypes.c_void_p), ]


############## implementations ################################################


_kernel_src_path = ""
_kcfg_path = ""
_so_file = ""


def _build_so_file():
    global _kernel_src_path
    global _kcfg_path
    global _so_file

    # generate zconf.lex.c
    cmd = ["flex", "-o", os.path.join(_kcfg_path, "zconf.lex.c"), "-L", os.path.join(_kcfg_path, "zconf.l")]
    proc = subprocess.Popen(cmd)
    proc.wait()

    # generate zconf.tab.h
    subprocess.Popen([
        "bison",
        "-o",
        "/dev/null",
        "--defines=%s" % (os.path.join(_kcfg_path, "zconf.tab.h")),
        "-t",
        "-l",
        os.path.join(_kcfg_path, "zconf.y")
    ]).wait()

    # generate zconf.tab.c
    subprocess.Popen([
        "bison",
        "-o",
        os.path.join(_kcfg_path, "zconf.tab.c"),
        "-t",
        "-l",
        os.path.join(_kcfg_path, "zconf.y")
    ]).wait()

    # generate pylkc.so
    subprocess.Popen([
        "cc",
        "-fPIC",
        "-shared",
        os.path.join(_kcfg_path, "conf.c"),
        os.path.join(_kcfg_path, "confdata.c"),
        os.path.join(_kcfg_path, "expr.c"),
        os.path.join(_kcfg_path, "symbol.c"),
        os.path.join(_kcfg_path, "preprocess.c"),
        os.path.join(_kcfg_path, "zconf.lex.c"),
        os.path.join(_kcfg_path, "zconf.tab.c"),
        "-o",
        os.path.join(_kcfg_path, "pylkc.so")
    ]).wait()


def _clean_so_file():
    global _kernel_src_path
    global _kcfg_path
    global _so_file

    os.unlink(_so_file)
