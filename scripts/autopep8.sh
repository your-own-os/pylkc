#!/bin/bash

FILES=$(find ./python3 -name '*.py' | tr '\n' ' ')

autopep8 -ia --ignore=E265,E501 ${FILES}
