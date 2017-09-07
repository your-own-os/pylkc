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
pylkcx

@author: Fpemud
@license: GPLv3 License
@contact: fpemud@sina.com
"""

__author__ = "fpemud@sina.com (Fpemud)"
__version__ = "0.0.1"

import os
import re
import pylkc


def get_kernel_version():
    assert pylkc._all_symbols_list is not None
    return os.environ["KERNELVERSION"]


def compare_kernel_version(kernel_version1, kernel_version2):
    """Returns 1 when kernel_version1 > kernel_version2
       Returns -1 when kernel_version1 < kernel_version2
       Returns 0 when kernel_version1 == kernel_version2"""

    vlist1 = kernel_version1.split(".")
    vlist2 = kernel_version2.split(".")

    i = 0
    while True:
        if len(vlist1) < i + 1 and len(vlist2) < i + 1:
            return 0
        if len(vlist1) >= i + 1 and len(vlist2) < i + 1:
            return 1
        if len(vlist1) < i + 1 and len(vlist2) >= i + 1:
            return -1

        if vlist1[i] > vlist2[i]:
            return 1
        if vlist1[i] < vlist2[i]:
            return -1

        i = i + 1

    return 0


def is_menu_debugging(menu_obj):
    if menu_obj.sym is None or menu_obj.sym.name is None or menu_obj.prompt is None:
        return False
    if menu_obj.prompt.type == pylkc.property.TYPE_COMMENT:
        return False

    if re.search("(_|^)DEBUG(_|$)", menu_obj.sym.name):
        return True
    if re.search("(_|^)TRACING(_|$)", menu_obj.sym.name):
        return True
    if re.search("(_|^)TESTMODE(_|$)", menu_obj.sym.name):
        return True
    if re.search("(_|^)DEVELOPER(_|$)", menu_obj.sym.name):
        return True
    if re.search("(_|^)DEBUGFS(_|$)", menu_obj.sym.name):
        return True

    if re.search("debug functions", menu_obj.get_prompt(), re.I):
        return True
    if re.search("debug interface", menu_obj.get_prompt(), re.I):
        return True
    if re.search("testing support", menu_obj.get_prompt(), re.I):
        return True
    if re.search("verbose .* error reporting", menu_obj.get_prompt(), re.I):
        return True

    menu_list = [
        "KPROBES",
        "KALLSYMS",
        "KALLSYMS_ALL",
        "X86_MCE_INJECT",                           # Machine check injector support
        "NUMA_EMU",                                 # NUMA emulation
        "X86_CHECK_BIOS_CORRUPTION",                # Check for low memory corruption
        "CMDLINE_BOOL",                             # Built-in kernel command line
        "PCIEAER_INJECT",
        "INPUT_EVBUG",
        "MAC80211_MESSAGE_TRACING",                 # Trace all mac80211 debug messages
        "ATH5K_TEST_CHANNELS",                      # Enables testing channels on ath5k
        "SCSI_LOGGING",                             # SCSI logging facility
        # testers
        "MEMTEST",
        "ARCH_MEMORY_PROBE",                        # Enable sysfs memory/probe interface
        "CRYPTO_TEST",
        "CRC32_SELFTEST",
        "GLOB_SELFTEST",
        "XZ_DEC_TEST",
        "CMDLINE_BOOL",
        # end
        "SND_SUPPORT_OLD_API",
        "SND_VERBOSE_PROCFS",
        "SND_VERBOSE_PRINTK",
        # filesystem debugging
        "BTRFS_FS_CHECK_INTEGRITY",
        "BTRFS_FS_RUN_SANITY_TESTS",
        "BTRFS_ASSERT",
        "JFS_STATISTICS",
        "REISERFS_CHECK",
        "REISERFS_PROC_INFO",
        "XFS_WARN",
        # end
        "V4L_TEST_DRIVERS",
    ]
    if menu_obj.sym.name in menu_list:
        return True

    return False


def is_menu_deprecated(menu_obj):
    if menu_obj.sym is None or menu_obj.sym.name is None or menu_obj.prompt is None:
        return False
    if menu_obj.prompt.type == pylkc.property.TYPE_COMMENT:
        return False

    if re.search("deprecated", menu_obj.get_prompt(), re.I):
        return True
    if re.search("obsolete", menu_obj.get_prompt(), re.I):
        return True
    if re.search("legacy", menu_obj.get_prompt(), re.I):
        return True
    if re.search("very old", menu_obj.get_prompt(), re.I):
        return True

    menu_list = [
        "USELIB",                                   # uselib syscall
        "UNUSED_SYMBOLS",                           # Enable unused/obsolete exported symbols
        "SYSFS_DEPRECATED",
        "SYSFS_DEPRECATED_V2",
        "NO_HZ",                                    # Old Idle dynticks config
        "X86_MPPARSE",                              # Enable MPS table
        "X86_VSYSCALL_EMULATION",
        "AMD_NUMA",                                 # Old style AMD Opteron NUMA detection
        "GART_IOMMU",                               # Old AMD GART IOMMU support
        "ACPI_PROCFS_POWER",
        "PROC_PID_CPUSET",                          # Include legacy /proc/<pid>/cpuset file
        "DNOTIFY",                                  # deprecated by inotify
        # deprecated by CONFIG_EFIVAR_FS
        "EFI_VARS",
        "EFI_RUNTIME_MAP",
        # end
        "ISA_DMA_API",                              # ISA-style DMA support, it's deprecated
        "UEVENT_HELPER",
        "FW_LOADER",
        "FW_LOADER_USER_HELPER_FALLBACK",
        "IP_NF_IPTABLES",
        "IP_NF_ARPTABLES",
        "IP6_NF_IPTABLES",
        "NETFILTER_XTABLES",
        "AF_RXRPC",
        "WIMAX",
        "VGA_SWITCHEROO",
        "VIDEO_FIXED_MINOR_RANGES",
    ]
    if menu_obj.sym.name in menu_list:
        return True

    return False


def is_menu_workaround(menu_obj):
    if menu_obj.sym is None or menu_obj.sym.name is None or menu_obj.prompt is None:
        return False
    if menu_obj.prompt.type == pylkc.property.TYPE_COMMENT:
        return False

    menu_list = [
        "X86_REROUTE_FOR_BROKEN_BOOT_IRQS",    # Reroute for broken boot IRQs
        "PCI_QUIRKS",                          # Enable PCI quirk workarounds
        "COMPAT_VDSO",                         # Compat VDSO support
        "DRM_LOAD_EDID_FIRMWARE",
    ]
    if menu_obj.sym.name in menu_list:
        return True

    return False


def is_menu_experimental(menu_obj):
    if menu_obj.sym is None or menu_obj.sym.name is None or menu_obj.prompt is None:
        return False
    if menu_obj.prompt.type == pylkc.property.TYPE_COMMENT:
        return False

    if re.search("preliminary", menu_obj.get_prompt(), re.I):
        return True
    if re.search("experimental", menu_obj.get_prompt(), re.I):
        return True

    menu_list = [
        "PCI_CNB20LE_QUIRK",                   # Read CNB20LE Host Bridge Windows
        "STAGING",                             # Staging drivers
        "DRM_I915_PRELIMINARY_HW_SUPPORT",
    ]
    if menu_obj.sym.name in menu_list:
        return True

    return False


def is_menu_dangerous(menu_obj):
    if menu_obj.sym is None or menu_obj.sym.name is None or menu_obj.prompt is None:
        return False
    if menu_obj.prompt.type == pylkc.property.TYPE_COMMENT:
        return False

    if re.search("dangerous", menu_obj.get_prompt(), re.I):
        return True
    if re.search("unsafe", menu_obj.get_prompt(), re.I):
        return True
    if re.search("use with caution", menu_obj.get_prompt(), re.I):
        return True

    menu_list = [
    ]
    if menu_obj.sym.name in menu_list:
        return True

    return False


def _is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False
