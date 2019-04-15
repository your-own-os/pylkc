#!/usr/bin/env python3

import os
import sys
import pylkcutil
from multiprocessing import Process

if len(sys.argv) < 3:
    print("%s <kconfig-rule-file> <kernel-source-directory>" % (sys.argv[0]))
    sys.exit(1)

with open("./tmpconfig", "w") as f:
    f.write("DEFAULT_HOSTNAME=\"(none)\"\n")
    f.write("\n")

    # deprecated symbol, but many drivers still need it
    f.write("FW_LOADER=y\n")
    f.write("\n")

    # deprecated symbol, but wine needs it
    f.write("X86_16BIT=y\n")
    f.write("\n")

    # deprecated symbol, but my GPU (especially Intel GPU) still needs it
    f.write("VGA_ARB=y\n")
    f.write("\n")

    # framebuffer console depends on it, it must be in whitelist until userspace VT is ready
    f.write("DRM_FBDEV_EMULATION=y\n")
    f.write("\n")

    # atk9k depends on it
    f.write("DEBUG_FS=y\n")
    f.write("\n")

    # H3C CAS 2.0 still use legacy virtio device, so it is needed
    f.write("VIRTIO_PCI_LEGACY=y\n")
    f.write("\n")

    # we still need iptables
    f.write("NETFILTER_XTABLES=y\n")
    f.write("IP_NF_IPTABLES=y\n")
    f.write("IP_NF_ARPTABLES=y\n")
    f.write("\n")

    # unstable kernel has some extra functions
    f.write("FB=y\n")
    f.write("[symbols:/Device drivers/Graphics support/Frame buffer Devices]=y\n")
    f.write("[symbols:/Device drivers/Graphics support/Console display driver support]=y\n")
    f.write("\n")

    # symbols we don't like
    f.write("[debugging-symbols:/]=n\n")
    f.write("[deprecated-symbols:/]=n\n")
    f.write("[workaround-symbols:/]=n\n")
    f.write("[experimental-symbols:/]=n\n")
    f.write("[dangerous-symbols:/]=n\n")
    f.write("\n")

    with open(sys.argv[1], "r") as f2:
        f.write(f2.read())

# generate the real ".config"
p = Process(target=pylkcutil.generator.generate,
            args=(sys.argv[2], "allnoconfig+module", "./tmpconfig",),
            kwargs={"output": os.path.join(sys.argv[2], ".config")})
p.start()
p.join()

# end of the whole process
print(".config file generated in directory %s" % (sys.argv[2]))
os.unlink("./tmpconfig")
