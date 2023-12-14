#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert subtitle file to .srt

Supported formats are .ttml and .sub (the latter is `[start_frame][stop_frame][Subtitle]`
and requires the frame rate to be given).

The input format can be given explictly with '--type' (without leading dot). 
Otherwise it will be inferred from the input file.
"""
import argparse
from pathlib import Path
from .ttml_to_srt import TtmlToSrtConverter
from .sub_to_srt import SubToSrtConverter

def main(*args):

    converters = {
        'ttml':TtmlToSrtConverter,
        'sub':SubToSrtConverter
    }
    
    parser = argparse.ArgumentParser(prog="subtitools convert", description=__doc__)
    parser.add_argument('in_file', help='input subtitle file')
    parser.add_argument('out_file', help='path to write srt file to')
    parser.add_argument('-f', '--fps', help='Frame rate', type=int)
    parser.add_argument('-t', '--type', help='Input format (without leading .)')
    parser.add_argument('-q', '--quiet', help='Quiet mode', action='store_true')
    parser.add_argument('-e', '--encoding', help='Encoding to use when reading file',
                        default='utf-8')
    
    args = parser.parse_args(args)
    
    in_path = Path(args.in_file)
    out_path = Path(args.out_file)
    
    if args.type is not None:
        in_type = args.type
    else:
        in_type = in_path.suffix.lstrip('.')
    
    conv_cls = converters.get(in_type, None)
    if conv_cls is None:
        raise RuntimeError(f"Unknown subtitle format '{in_type}'")
    else:
        kwargs = {}
        if args.fps is not None:
            kwargs['fps'] = args.fps
        conv = conv_cls(args.quiet)
        conv.convert(in_path, out_path, args.encoding **kwargs)