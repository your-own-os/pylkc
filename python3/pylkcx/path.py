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

"""Some examples:
    r"/Device Drivers"
    r"Device Drivers/Userspace I\/O drivers"
Escape sequences:
    "\/" "\\"
"""

import re


def basename(path):
    return split(path)[1]


def dirname(path):
    return split(path)[0]


def isabs(path):
    return path.startswith("/")


def split(path):
    ret = _full_split(path)
    if ret[0] == "/":
        if len(ret) == 1:
            return (ret[0], "")
        else:
            return (_full_join(ret[:-1]), ret[-1])
    else:
        if len(ret) == 1:
            return ("", ret[0])
        else:
            return (_full_join(ret[:-1]), ret[-1])


def join(path, *pathlist):
    return _full_join([path] + list(pathlist))


def escape(path_element):
    path_element = path_element.replace("\\", "\\\\")
    path_element = path_element.replace("/", "\\/")
    return path_element


def unescape(path_element):
    ret = ""

    bEscape = False
    for c in path_element:
        if bEscape:
            if c == "\\":
                ret += "\\"
            elif c == "/":
                ret += "/"
            else:
                assert False
            bEscape = False
            continue
        if c == "\\":
            bEscape = True
            continue
        ret += c
    assert not bEscape

    return ret


def compare(path1, path2):
    return path1 == path2


def compare_fuzzy(path1, path2):
    """1. Auto match common decorations, like "(DEPRECATED)", "(EXPERIMENTAL)", "(OBSOLETE)"
          So "Device Drivers/Ultra Wideband devices" can match "Device Drivers/Ultra Wideband devices (EXPERIMENTAL)"
       2. Auto match "..."
          So "/File systems/Miscellaneous filesystems/SquashFS.../File decompression option" can match "/File systems/Miscellaneous filesystems/SquashFS 4.0 - Squashed file system support/File decompression option"
       3. Auto match multiple spaces
       4. Ignore case"""
    path1 = _degrade(path1)
    path2 = _degrade(path2)
    if path1 == path2:
        return True
    plist1 = _full_split(path1)
    plist2 = _full_split(path2)
    if len(plist1) != len(plist2):
        return False
    for i in range(0, len(plist1)):
        p1 = plist1[i]
        p2 = plist2[i]
        if "..." in p1 and "..." in p2:
            assert False
        if "..." in p1:
            assert p1.count("...") <= 1
            t = p1.split("...")
            if t[0] != "":
                if not p2.startswith(t[0]):
                    return False
            if t[1] != "":
                if not p2.endswith(t[1]):
                    return False
        if "..." in p2:
            assert p2.count("...") <= 1
            t = p2.split("...")
            if t[0] != "":
                if not p1.startswith(t[0]):
                    return False
            if t[1] != "":
                if not p1.endswith(t[1]):
                    return False
        if "..." not in p1 and "..." not in p2:
            if plist1[i] != plist2[i]:
                return False
    return True

############## implementations ################################################


def _full_split(path):
    if path == "":
        return [""]
    if path == "/":
        return ["/"]

    ret = []
    if path[0] == "/":
        ret.append("/")
        path = path[1:]

    bEscape = False
    curret = ""
    for c in path:
        if bEscape:
            if c == "\\":
                curret += "\\\\"
            elif c == "/":
                curret += "\\/"
            else:
                assert False
            bEscape = False
            continue
        if c == "\\":
            bEscape = True
            continue
        if c == "/":
            ret.append(curret)
            curret = ""
            continue
        curret += c
    assert not bEscape
    ret.append(curret)

    return ret


def _full_join(pathlist):
    assert len(pathlist) > 0

    ret = ""
    for p in pathlist:
        if p == "":
            continue
        if p.startswith("/"):
            ret = p
            continue
        if p.endswith("/"):
            p = p[:-1]
        if ret == "":
            ret = p
        elif ret == "/":
            ret = ret + p
        else:
            ret = ret + "/" + p

    return ret


def _degrade(path):
    # letter case replacement
    path = path.lower()

    # eliminate ending "(.*)"
    while True:
        m = re.search("^(.*)\s*\\(.*\\)\s*$", path)
        if m is None:
            break
        path = m.group(1)

    # remove redundant spaces
    path = path.replace("  ", " ")

    return path
