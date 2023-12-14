#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Given an srt file, shift the subtitle timestamps by a given time.
"""

import re
import os
from datetime import datetime, timedelta
import argparse
from utils import read_lines

rng_regex = re.compile(r"(?P<start>\d\d:\d\d:\d\d,\d\d\d) --> (?P<end>\d\d:\d\d:\d\d,\d\d\d)")
ts_regex = re.compile(r"(?P<hour>\d\d):(?P<minute>\d\d):(?P<second>\d\d),(?P<microsecond>\d\d\d)")
ts_groups = ['hour', 'minute', 'second', 'microsecond'] # final group in srt timestamp is ms, but datetime needs microsecond

def do_shift(fname, h=0, m=0, s=0, ms=0) -> str:
    """ 
    Read file `fname` and perform shift on timestamps. 
    
    Return str of new data to be written to file.
    """
    out = []
    t_shift = timedelta(hours=h, minutes=m, seconds=s, milliseconds=ms)
    
    lines = read_lines(fname, strip_empty=False)
    for line in lines:
        if (m := rng_regex.match(line)) is not None:
            start = _shift(m.group('start'), t_shift)
            end = _shift(m.group('end'), t_shift)
            line = f"{start} --> {end}"
        out.append(line
                   )
    out = os.linesep.join(out)
    return out
                
def _shift(s, t_shift):
    t = _make_time(s) # convert time from string `s` to datetime
    t = _strftime(t + t_shift) # apply shift and cast back to string
    return t

def _make_time(s):
    # given regex match group string, return datetime.datetime
    t = ts_regex.match(s)
    t = {g: int(t.group(g)) for g in ts_groups}
    t['microsecond'] *= 1000 # ms to microsecond
    d = datetime(2022, 1, 1, **t) # use any year, month, day
    return d

def _strftime(d):
    return d.strftime("%H:%M:%S,%f")[:-3] # microsecond back to ms

def make_argparser():
    parser = argparse.ArgumentParser(prog="subtitools shift", description=__doc__)
    parser.add_argument('file', help='srt file')
    parser.add_argument('-o', '--output', help='path to write to. '
                        'If not provided, input will be overwritten')
    parser.add_argument('-hr', '--hours', help='Shift hours. Default is 0', 
                        default=0, type=int)
    parser.add_argument('-m', '--minutes', help='Shift minutes. Default is 0', 
                        default=0, type=int)
    parser.add_argument('-s', '--seconds', help='Shift seconds. Default is 0', 
                        default=0, type=int)
    parser.add_argument('-ms', '--milliseconds', help='Shift milliseconds. Default is 0', 
                        default=0, type=int)
    return parser

def shift(file, output=None, hours=0, minutes=0, seconds=0, milliseconds=0):
    if output is None:
        output = file
    
    srt = do_shift(file, hours, minutes, seconds, milliseconds)
    
    with open(output, 'w') as fileobj:
        fileobj.write(srt)
    
def main(*args):
    parser = make_argparser()
    args = parser.parse_args(args)
    shift(**vars(args))

if __name__ == "__main__":

    import sys
    main(sys.argv[1:])