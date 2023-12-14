#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert .sub title with format
`[start_frame][stop_frame][Subtitle]`
to srt format.
"""

import os
import re
from .srt_converter import SrtConverter, Subtitle

class SubToSrtConverter(SrtConverter):

    def _parse_subtitle(self, line: str, fps: float) -> str:
        regex = re.compile(r"\{(?P<start_frame>\d+)\}\{(?P<stop_frame>\d+)\}(?P<text>.*)")
        if (m:=regex.match(line)) is None:
            raise ValueError(f"Could not parse line '{line}'")
        else:
            frames = [int(m.group(g)) for g in ['start_frame', 'stop_frame']]
            text = re.sub(r"\|", os.linesep, m.group('text'))
            ts = [self._format_time_frames(f, fps) for f in frames]
            sub = Subtitle(*ts, text)
            return sub
            
    @classmethod
    def _format_time_frames(cls, f: int, fps: int) -> str:
        """ Convert a frame number `f` to timestamp in format "HH:MM:ss,mmm", using `fps` """
        return Subtitle.seconds_to_timestamp(f/fps)
    #     return cls._format_time_seconds(f/fps)
           
    # @staticmethod
    # def _format_time_seconds(s: float) -> str:
    #     """ Convert int `s` in seconds to timestamp in format "HH:MM:ss,mmm" """
    #     hr, mn = divmod(s, 3600)
    #     mn, sc = divmod(mn, 60)
    #     sc, ms = divmod(sc, 1)
    #     ms *= 1000
    #     ts = [int(t) for t in (hr, mn, sc, ms)]
    #     return "{:02d}:{:02d}:{:02d},{:03d}".format(*ts)

if __name__ == "__main__":
    
    import argparse
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('in_file', help='input sub file')
    parser.add_argument('out_file', help='path to write srt file to')
    parser.add_argument('-f', '--fps', help='Frame rate', 
                        default=25, type=int)
    args = parser.parse_args()
    
    conv = SubToSrtConverter()
    conv.convert(args.in_file, args.out_file, args.fps)
    
