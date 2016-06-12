#!/bin/bash

if [[ -e "./.git" || -e "./.svn" ]] ; then
    ROOTDIR="."
elif [[ -e "../.git" || -e "../.svn" ]] ; then
    ROOTDIR=".."
else
    echo "Error: No version control system (Git, Subversion) found!"
    exit 1
fi

if [ -e "${ROOTDIR}/.git" ] ; then
    echo "Installing Git hooks..."
    ln -sf "../../scripts/git-hook-pre-commit.sh" "${ROOTDIR}/.git/hooks/pre-commit"
    echo "Done."
    exit 0
fi

if [ -e "${ROOTDIR}/.svn" ] ; then
    echo "Error: Unimplemented yet!"
    exit 1
fi

exit 1
