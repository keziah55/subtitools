#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Subtitle file manipulation tool.

See `adapt convert -h` or `adapt shift -h` for more information.
"""

import sys
import shift
import convert

modules = {"shift": shift,
           "convert": convert}

arg0, *args = sys.argv[1:]

if arg0 in ["-h" or "--help"]:
    print(__doc__.strip())
elif (mod:=modules.get(arg0, None)) is not None:
    mod.main(*args)
else:
    print(f"Unknown option '{arg0}'. Please see 'adapt -h' for usage")
