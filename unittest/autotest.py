#!/usr/bin/env python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

import os
import sys
import random
import shutil
import unittest

curDir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(curDir, "../python3"))
import pylkc
import pylkcutil


class util:

    @staticmethod
    def value_refresh():
        for sym in pylkc.all_symbols():
            sym.calc_value()


class Test_Linux_3_16(unittest.TestCase):
    def setUp(self):
        self.rootDir = os.path.join(curDir, "linux-3.16")

    def runTest(self):
        pylkc.init(self.rootDir)
        try:
            pylkc.conf_parse(self.rootDir)
            pylkc.conf_read(None)
            util.value_refresh()

            if True:
                sym = pylkc.sym_find("DEFAULT_HOSTNAME")
                self.assertIsNotNone(sym)
                self.assertEqual(sym.get_string_value(), "(none)")

                ret = sym.set_string_value("")
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_string_value(), "")

            if True:
                sym = pylkc.sym_find("EXPERT")

                ret = sym.set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.yes)

                ret = sym.set_tristate_value(pylkc.tristate.no)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.no)

            if True:
                sym = pylkc.sym_find("MODULES")
                ret = sym.set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)
                util.value_refresh()

                sym = pylkc.sym_find("CRYPTO")

                ret = sym.set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.yes)

                ret = sym.set_tristate_value(pylkc.tristate.mod)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.mod)

                ret = sym.set_tristate_value(pylkc.tristate.no)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.no)

            if True:
                menuObj = pylkc.menu_find_by_path("/General setup/Kernel compression mode", True)
                self.assertIsNotNone(menuObj)

            pylkc.conf_write(None)
        finally:
            pylkc.release()

    def tearDown(self):
        if os.path.exists(".config"):
            os.remove(".config")


class Test_Linux_3_17(unittest.TestCase):
    def setUp(self):
        self.rootDir = os.path.join(curDir, "linux-3.17")

    def runTest(self):
        pylkc.init(self.rootDir)
        try:
            pylkc.conf_parse(self.rootDir)
            pylkc.conf_read(None)
            util.value_refresh()

            if True:
                sym = pylkc.sym_find("DEFAULT_HOSTNAME")
                self.assertIsNotNone(sym)
                self.assertEqual(sym.get_string_value(), "(none)")

                ret = sym.set_string_value("")
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_string_value(), "")

            if True:
                sym = pylkc.sym_find("EXPERT")
                self.assertIsNotNone(sym)

                ret = sym.set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.yes)

                ret = sym.set_tristate_value(pylkc.tristate.no)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.no)

            if True:
                sym = pylkc.sym_find("MODULES")
                ret = sym.set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.yes)

                sym = pylkc.sym_find("CRYPTO")
                self.assertIsNotNone(sym)

                ret = sym.set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.yes)

                ret = sym.set_tristate_value(pylkc.tristate.mod)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.mod)

                ret = sym.set_tristate_value(pylkc.tristate.no)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.no)

            if True:
                menuObj = pylkc.menu_find_by_path("/General setup/Kernel compression mode", True)
                self.assertIsNotNone(menuObj)

            pylkc.conf_write(None)
        finally:
            pylkc.release()

    def tearDown(self):
        if os.path.exists(".config"):
            os.remove(".config")


class Test_Linux_3_18(unittest.TestCase):
    def setUp(self):
        self.rootDir = os.path.join(curDir, "linux-3.18.1")

    def runTest(self):
        pylkc.init(self.rootDir)
        try:
            pylkc.conf_parse(self.rootDir)
            pylkc.conf_read(None)
            util.value_refresh()

            if True:
                sym = pylkc.sym_find("DEFAULT_HOSTNAME")
                self.assertIsNotNone(sym)
                self.assertEqual(sym.get_string_value(), "(none)")

                ret = sym.set_string_value("")
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_string_value(), "")

            if True:
                sym = pylkc.sym_find("EXPERT")
                self.assertIsNotNone(sym)

                ret = sym.set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.yes)

                ret = sym.set_tristate_value(pylkc.tristate.no)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.no)

            if True:
                ret = pylkc.sym_find("MODULES").set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)

                sym = pylkc.sym_find("CRYPTO")
                self.assertIsNotNone(sym)

                ret = sym.set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.yes)

                ret = sym.set_tristate_value(pylkc.tristate.mod)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.mod)

                ret = sym.set_tristate_value(pylkc.tristate.no)
                self.assertTrue(ret) 
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.no)

            if True:
                menuObj = pylkc.menu_find_by_path("/General setup/Kernel compression mode", True)
                self.assertIsNotNone(menuObj)

            pylkc.conf_write(None)
        finally:
            pylkc.release()

    def tearDown(self):
        if os.path.exists(".config"):
            os.remove(".config")


class Test_Linux_4_0(unittest.TestCase):
    def setUp(self):
        self.rootDir = os.path.join(curDir, "linux-4.0")

    def runTest(self):
        pylkc.init(self.rootDir)
        try:
            pylkc.conf_parse(self.rootDir)
            pylkc.conf_read(None)
            util.value_refresh()

            if True:
                sym = pylkc.sym_find("DEFAULT_HOSTNAME")
                self.assertIsNotNone(sym)
                self.assertEqual(sym.get_string_value(), "(none)")

                ret = sym.set_string_value("")
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_string_value(), "")

            if True:
                sym = pylkc.sym_find("EXPERT")
                self.assertIsNotNone(sym)

                ret = sym.set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.yes)

                ret = sym.set_tristate_value(pylkc.tristate.no)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.no)

            if True:
                ret = pylkc.sym_find("MODULES").set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)

                sym = pylkc.sym_find("CRYPTO")
                self.assertIsNotNone(sym)

                ret = sym.set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.yes)

                ret = sym.set_tristate_value(pylkc.tristate.mod)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.mod)

                ret = sym.set_tristate_value(pylkc.tristate.no)
                self.assertTrue(ret) 
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.no)

            if True:
                menuObj = pylkc.menu_find_by_path("/General setup/Kernel compression mode", True)
                self.assertIsNotNone(menuObj)

            pylkc.conf_write(None)
        finally:
            pylkc.release()

    def tearDown(self):
        if os.path.exists(".config"):
            os.remove(".config")


class Test_Linux_4_2(unittest.TestCase):
    def setUp(self):
        self.rootDir = os.path.join(curDir, "linux-4.2.3")

    def runTest(self):
        pylkc.init(self.rootDir)
        try:
            pylkc.conf_parse(self.rootDir)
            pylkc.conf_read(None)
            util.value_refresh()

            if True:
                sym = pylkc.sym_find("DEFAULT_HOSTNAME")
                self.assertIsNotNone(sym)
                self.assertEqual(sym.get_string_value(), "(none)")

                ret = sym.set_string_value("")
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_string_value(), "")

            if True:
                sym = pylkc.sym_find("EXPERT")
                self.assertIsNotNone(sym)

                ret = sym.set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.yes)

                ret = sym.set_tristate_value(pylkc.tristate.no)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.no)

            if True:
                ret = pylkc.sym_find("MODULES").set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)

                sym = pylkc.sym_find("CRYPTO")
                self.assertIsNotNone(sym)

                ret = sym.set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.yes)

                ret = sym.set_tristate_value(pylkc.tristate.mod)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.mod)

                ret = sym.set_tristate_value(pylkc.tristate.no)
                self.assertTrue(ret) 
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.no)

            if True:
                menuObj = pylkc.menu_find_by_path("/General setup/Kernel compression mode", True)
                self.assertIsNotNone(menuObj)

            pylkc.conf_write(None)
        finally:
            pylkc.release()

    def tearDown(self):
        if os.path.exists(".config"):
            os.remove(".config")


class Test_Linux_5_0_7(unittest.TestCase):
    def setUp(self):
        self.rootDir = os.path.join(curDir, "linux-5.0.7")

    def runTest(self):
        pylkc.init(self.rootDir)
        try:
            pylkc.conf_parse(self.rootDir)
            pylkc.conf_read(None)
            util.value_refresh()

            if True:
                sym = pylkc.sym_find("DEFAULT_HOSTNAME")
                self.assertIsNotNone(sym)
                self.assertEqual(sym.get_string_value(), "(none)")

                ret = sym.set_string_value("")
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_string_value(), "")

            if True:
                sym = pylkc.sym_find("EXPERT")
                self.assertIsNotNone(sym)

                ret = sym.set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.yes)

                ret = sym.set_tristate_value(pylkc.tristate.no)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.no)

            if True:
                ret = pylkc.sym_find("MODULES").set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)

                sym = pylkc.sym_find("CRYPTO")
                self.assertIsNotNone(sym)

                ret = sym.set_tristate_value(pylkc.tristate.yes)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.yes)

                ret = sym.set_tristate_value(pylkc.tristate.mod)
                self.assertTrue(ret)
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.mod)

                ret = sym.set_tristate_value(pylkc.tristate.no)
                self.assertTrue(ret) 
                util.value_refresh()
                self.assertEqual(sym.get_tristate_value(), pylkc.tristate.no)

            if True:
                menuObj = pylkc.menu_find_by_path("/General setup/Kernel compression mode", True)
                self.assertIsNotNone(menuObj)

            pylkc.conf_write(None)
        finally:
            pylkc.release()

    def tearDown(self):
        if os.path.exists(".config"):
            os.remove(".config")


class Test_Menu_Structure(unittest.TestCase):
    def setUp(self):
        self.rootDir = os.path.join(curDir, "linux-3.18.1")

    def runTest(self):
        pylkc.init(self.rootDir)
        try:
            pylkc.conf_parse(self.rootDir)
            pylkc.conf_read(None)

            mobj = pylkc.menu_find_by_path("/General setup")
            self.assertIn("Kernel compression mode", [m.get_prompt() for m in mobj.list])

            mobj = pylkc.menu_find_by_path("/General setup/Kernel compression mode")
            sobj = pylkc.sym_find("KERNEL_LZMA")
            self.assertTrue(mobj.sym.is_choice())
            self.assertTrue(sobj.is_choice_value())
            self.assertIn(sobj, [m.sym for m in mobj.list])

            mobj = pylkc.menu_find_by_sym(pylkc.sym_find("IKCONFIG"))
            self.assertEqual(len(mobj.list), 1)
            self.assertEqual(mobj.list[0].sym, pylkc.sym_find("IKCONFIG_PROC"))

            mobj = pylkc.menu_find_by_path("/General setup")
            self.assertTrue(mobj.is_visible())
            mobj = pylkc.menu_find_by_sym(pylkc.sym_find("MODULES"))
            self.assertTrue(mobj.is_visible())
            mobj = pylkc.menu_find_by_sym(pylkc.sym_find("EXT4_USE_FOR_EXT23"))
            self.assertFalse(mobj.is_visible())
            mobj = pylkc.menu_find_by_sym(pylkc.sym_find("CIFS_NFSD_EXPORT"))
            self.assertFalse(mobj.is_visible())

            sobj = pylkc.sym_find("DEFAULT_HOSTNAME")
            self.assertEqual(sobj.get_type(), pylkc.symbol.TYPE_STRING)
            sobj = pylkc.sym_find("MODULES")
            self.assertEqual(sobj.get_type(), pylkc.symbol.TYPE_BOOLEAN)
            sobj = pylkc.sym_find("MICROCODE")
            self.assertEqual(sobj.get_type(), pylkc.symbol.TYPE_BOOLEAN)
            sobj = pylkc.sym_find("PCI_STUB")
            self.assertEqual(sobj.get_type(), pylkc.symbol.TYPE_BOOLEAN)
            sobj = pylkc.sym_find("X86_RESERVE_LOW")
            self.assertEqual(sobj.get_type(), pylkc.symbol.TYPE_INT)
            sobj = pylkc.sym_find("PHYSICAL_START")
            self.assertEqual(sobj.get_type(), pylkc.symbol.TYPE_HEX)

            mobj = pylkc.menu_find_by_path("/General setup", True)
            self.assertIsNotNone(mobj)
            mobj = pylkc.menu_find_by_path("/Executable file formats \\/ Emulations", True)
            self.assertIsNotNone(mobj)
        finally:
            pylkc.release()

    def tearDown(self):
        pass


class Test_Path_1(unittest.TestCase):
    def runTest(self):
        self.assertEqual(pylkc.path.basename(""), "")
        self.assertEqual(pylkc.path.basename("/"), "")
        self.assertEqual(pylkc.path.basename("/General Setup"), "General Setup")
        self.assertEqual(pylkc.path.basename("/General Setup/"), "")
        self.assertEqual(pylkc.path.basename("/File systems/Miscellaneous filesystems"), "Miscellaneous filesystems")
        self.assertEqual(pylkc.path.basename("../Miscellaneous filesystems"), "Miscellaneous filesystems")


class Test_Path_2(unittest.TestCase):
    def runTest(self):
        self.assertEqual(pylkc.path.dirname(""), "")
        self.assertEqual(pylkc.path.dirname("/"), "/")
        self.assertEqual(pylkc.path.dirname("/General Setup"), "/")
        self.assertEqual(pylkc.path.dirname("/General Setup/"), "/General Setup")
        self.assertEqual(pylkc.path.dirname("/File systems/Miscellaneous filesystems"), "/File systems")
        self.assertEqual(pylkc.path.dirname("../Miscellaneous filesystems"), "..")


class Test_Path_3(unittest.TestCase):
    def runTest(self):
        self.assertEqual(pylkc.path.isabs(""), False)
        self.assertEqual(pylkc.path.isabs("/General Setup"), True)
        self.assertEqual(pylkc.path.isabs("../Miscellaneous filesystems"), False)


class Test_Path_4(unittest.TestCase):
    def runTest(self):
        self.assertEqual(pylkc.path.split(""), ("", ""))
        self.assertEqual(pylkc.path.split("/"), ("/", ""))
        self.assertEqual(pylkc.path.split("/File systems/Miscellaneous filesystems"), ("/File systems", "Miscellaneous filesystems"))
        self.assertEqual(pylkc.path.split("/Device Drivers/Userspace I\/O drivers"), ("/Device Drivers", "Userspace I\/O drivers"))
        self.assertEqual(pylkc.path.split("Device Drivers"), ("", "Device Drivers"))
        self.assertEqual(pylkc.path.split("Device Drivers/Userspace I\/O drivers"), ("Device Drivers", "Userspace I\/O drivers"))
        self.assertEqual(pylkc.path.split("Device Drivers/Userspace I\/O drivers/AEC video timestamp device (NEW)"), ("Device Drivers/Userspace I\/O drivers", "AEC video timestamp device (NEW)"))


class Test_Path_5(unittest.TestCase):
    def runTest(self):
        self.assertEqual(pylkc.path.join(""), "")
        self.assertEqual(pylkc.path.join("", ""), "")
        self.assertEqual(pylkc.path.join("/"), "/")
        self.assertEqual(pylkc.path.join("/", ""), "/")
        self.assertEqual(pylkc.path.join("/Device Drivers", "Userspace I\/O drivers"), "/Device Drivers/Userspace I\/O drivers")
        self.assertEqual(pylkc.path.join("Device Drivers", "Userspace I\/O drivers", "AEC video timestamp device (NEW)"), "Device Drivers/Userspace I\/O drivers/AEC video timestamp device (NEW)")


class Test_Path_6(unittest.TestCase):
    def runTest(self):
        self.assertEqual(pylkc.path.escape(""), "")
        self.assertEqual(pylkc.path.escape("Device Drivers"), "Device Drivers")
        self.assertEqual(pylkc.path.escape("Userspace I/O drivers"), "Userspace I\/O drivers")

        self.assertEqual(pylkc.path.unescape(""), "")
        self.assertEqual(pylkc.path.unescape("Device Drivers"), "Device Drivers")
        self.assertEqual(pylkc.path.unescape("Userspace I\/O drivers"), "Userspace I/O drivers")


class Test_Path_7(unittest.TestCase):
    def runTest(self):
        self.assertFalse(pylkc.path.compare("/General Setup", "/General setup"))
        self.assertTrue(pylkc.path.compare_fuzzy("/General Setup", "/General setup"))


class Test_Generate(unittest.TestCase):
    def setUp(self):
        self.rootDir = os.path.join(curDir, "linux-4.0")
    with open("rules.txt", "w") as f:
        ruleList = []
        ruleList.append("DEFAULT_HOSTNAME=\"(none)\"")
        ruleList.append("EXPERT=y")
        ruleList.append("EMBEDDED=y")
        ruleList.append("/General setup/Kernel compression mode=KERNEL_XZ")
        ruleList.append("LOG_BUF_SHIFT=15")
        ruleList.append("[normal-symbols:CGROUPS]=y")
        ruleList.append("SGETMASK_SYSCALL=n")
        ruleList.append("<symbols:EXPERT>=y")
        ruleList.append("[normal-symbols:/Networking support]=m")
        ruleList.append("SQUASHFS=m")
        ruleList.append("/File systems/Miscellaneous filesystems/SquashFS 4.0 - .../File decompression options=SQUASHFS_FILE_DIRECT")
        ruleList.append("[regex-symbols:\\bISCSI\\b:/Device Drivers]=n")
        f.write("\n".join(ruleList))

    def runTest(self):
        pylkcutil.generator.generate_in_proc(self.rootDir, "rules.txt", ".config")

    def tearDown(self):
        if os.path.exists(".config"):
            os.remove(".config")
        if os.path.exists("rules.txt"):
            os.remove("rules.txt")


class Test_CheckValue(unittest.TestCase):
    def setUp(self):
        self.rootDir = os.path.join(curDir, "linux-4.0")
        with open(".config", "w") as f:
            pass

    def runTest(self):
        pylkcutil.checker.check_value_in_proc(self.rootDir, ".config", "DEFAULT_HOSTNAME", "(none)")
        pylkcutil.checker.check_value_in_proc(self.rootDir, ".config", "/General setup/Kernel compression mode", "KERNEL_XZ")
        pylkcutil.checker.check_value_in_proc(self.rootDir, ".config", "EXPERT", "n")

    def tearDown(self):
        os.remove(".config")


class Test_CheckValues(unittest.TestCase):
    def setUp(self):
        self.rootDir = os.path.join(curDir, "linux-4.0")
        with open(".config", "w") as f:
            pass

    def runTest(self):
        valueDict = dict()
        valueDict["DEFAULT_HOSTNAME"] = "(none)"
        valueDict["/General setup/Kernel compression mode"] = "KERNEL_XZ"
        valueDict["EXPERT"] = "n"
        pylkcutil.checker.check_values_in_proc(self.rootDir, ".config", valueDict)

    def tearDown(self):
        os.remove(".config")


class Test_GenerateWithException(unittest.TestCase):
    def setUp(self):
        self.rootDir = os.path.join(curDir, "linux-4.0")

    def runTest(self):
        ruleList = []
        ruleList.append("ABC=y")
        with self.assertRaisesRegexp(pylkcutil.generator.ExecutionError, "a"):
            pylkcutil.generator.generate_in_proc(self.rootDir, ruleList, ".config")

    def tearDown(self):
        if os.path.exists(".config"):
            os.remove(".config")


class Test_CheckValueWithException(unittest.TestCase):
    def setUp(self):
        self.rootDir = os.path.join(curDir, "linux-4.0")
        with open(".config", "w") as f:
            pass

    def runTest(self):
        with self.assertRaisesRegexp(pylkcutil.checker.CheckError, "a"):
            pylkcutil.checker.check_value_in_proc(self.rootDir, ".config", "ABC", "n")

    def tearDown(self):
        os.remove(".config")


class Test_CheckValuesWithException(unittest.TestCase):
    def setUp(self):
        self.rootDir = os.path.join(curDir, "linux-4.0")
        with open(".config", "w") as f:
            pass

    def runTest(self):
        valueDict = dict()
        valueDict["ABC"] = "n"
        with self.assertRaisesRegexp(pylkcutil.checker.CheckError, "a"):
            pylkcutil.checker.check_values_in_proc(self.rootDir, ".config", valueDict)

    def tearDown(self):
        os.remove(".config")


def suite():
    suite = unittest.TestSuite()

    suite.addTest(Test_Path_1())
    suite.addTest(Test_Path_2())
    suite.addTest(Test_Path_3())
    suite.addTest(Test_Path_4())
    suite.addTest(Test_Path_5())
    suite.addTest(Test_Path_6())
    suite.addTest(Test_Path_7())

    # error when reading one directory twice, so do a random test
    r = random.randint(1, 7)
    if r == 1:
        suite.addTest(Test_Linux_3_16())
    elif r == 2:
        suite.addTest(Test_Linux_3_17())
    elif r == 3:
        suite.addTest(Test_Linux_3_18())
    elif r == 4:
        suite.addTest(Test_Linux_4_0())
    elif r == 5:
        suite.addTest(Test_Linux_4_2())
    elif r == 6:
        suite.addTest(Test_Linux_5_0_7())
    elif r == 7:
        suite.addTest(Test_Menu_Structure())
    else:
        assert False

#    suite.addTest(Test_Generate())
#    suite.addTest(Test_CheckValue())
#    suite.addTest(Test_CheckValues())
#    suite.addTest(Test_GenerateWithException())
#    suite.addTest(Test_CheckValueWithException())
#    suite.addTest(Test_CheckValuesWithException())

    return suite


if __name__ == "__main__":
    unittest.main(defaultTest = 'suite')
