#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utility functions.
"""
from pathlib import Path
import os
import re

def read_lines(p: Path, encoding=None, strip_empty=True, quiet=False) -> list[str]:
    """ 
    Return list of lines from file `p`.
    
    If `encoding` is explicitly provided, use that. 
    Otherise, attempt to use `charset_normalizer <https://pypi.org/project/charset-normalizer/>`_ to detect encoding.
    If `encoding` is None and charset_normalizer is not installed, use default
    'utf-8'.
    """
    if encoding is not None:
        text = _read_file(p, encoding=encoding)
    else:
        try:
            from charset_normalizer import from_path
        except:
            text = _read_file(p)
            if not quiet:
                print("** For better results, install charset_normalizer **")
        else:
            text = str(from_path(p).best())
        
    if '\r' not in os.linesep and '\r' in text:
        # if test has \r chars that are not necessary on this OS, remove them
        text = re.sub(r"\r", "", text)
        
    if strip_empty:
        lines = [line for line in text.split(os.linesep) if line]
    else:
        lines = [line for line in text.split(os.linesep)]
    
    print(lines[:10])
    
    return lines

def _read_file(p, encoding='utf-8'):
    with open(p, encoding='utf-8') as fileobj:
        text = fileobj.read()
    return text