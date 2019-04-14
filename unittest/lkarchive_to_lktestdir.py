#!/usr/bin/env python3
# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t -*-

"""Convert linux kernel archive file to test linux kernel source directory"""

import os
import sys
import shutil
import tarfile
import fnmatch

if len(sys.argv) != 2:
    raise Exception("usage: strip_linux_kernel.py <kernel_archive>")

kernel_archive = sys.argv[1]
kernel_name = os.path.basename(kernel_archive[:kernel_archive.index(".tar")])

# extract kernel archive
if os.path.exists(kernel_name):
    shutil.rmtree(kernel_name)
with tarfile.open(kernel_archive) as f:
    f.extractall()

# remove all the uneccessary files
for root, dirs, files in os.walk(kernel_name, topdown=False):
    if root.startswith(os.path.join(kernel_name, "scripts")):
        continue
    if root.startswith(os.path.join(kernel_name, "Documentation")):    # "make clean" needs it
        continue
    for f in files:
        if f == "Kconfig" or fnmatch.fnmatch(f, "Kconfig.*"):
            continue
        if f == "Kbuild":
            continue
        if f == "Makefile" or fnmatch.fnmatch(f, "Makefile.*"):
            continue
        if fnmatch.fnmatch(f, "*defconfig"):
            continue
        os.unlink(os.path.join(root, f))
    for d in dirs:
        if os.path.islink(os.path.join(root, d)):                      # remove any directory soft-link
            os.unlink(os.path.join(root, d))
        elif os.listdir(os.path.join(root, d)) == []:
            os.rmdir(os.path.join(root, d))
