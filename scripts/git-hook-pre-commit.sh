#!/bin/bash

FILES=$(find ./python3 -name '*.py' | tr '\n' ' ')
ERRFLAG=0

OUTPUT=`pyflakes ${FILES} 2>&1`
if [ -n "$OUTPUT" ] ; then
    echo "pyflake errors:"
    echo "$OUTPUT"
    echo ""
    ERRFLAG=1
fi

OUTPUT=`pep8 ${FILES} | grep -Ev "E265|E266|E402|E501"`
if [ -n "$OUTPUT" ] ; then
    echo "pep8 errors:"
    echo "$OUTPUT"
    echo ""
    ERRFLAG=1
fi

OUTPUT=`unittest/autotest.py 2>&1`
if [ "$?" == 1 ] ; then
    echo "unittest errors:"
    echo "$OUTPUT"
    echo ""
    ERRFLAG=1
fi

if [ "${ERRFLAG}" == 1 ] ; then
    exit 1
fi

