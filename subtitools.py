#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Subtitle file manipulation tool.

See `subtitools convert -h` or `subtitools shift -h` for more information.
"""

import sys
import subtitools.shift
import subtitools.convert

modules = {"shift": subtitools.shift,
           "convert": subtitools.convert}

arg0, *args = sys.argv[1:]

if arg0 in ["-h" or "--help"]:
    print(__doc__.strip())
elif (mod:=modules.get(arg0, None)) is not None:
    mod.main(*args)
else:
    print(f"Unknown option '{arg0}'. Please see 'subtitools -h' for usage")
