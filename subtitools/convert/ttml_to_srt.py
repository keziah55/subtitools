#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Convert .ttml subtitle files to .srt
"""

import re
from bs4 import BeautifulSoup
from .srt_converter import SrtConverter, Subtitle

class TtmlToSrtConverter(SrtConverter):
    
    def _parse(self, p) -> list:
        """ Return list of 'p' tags in body of `p`  """
        self._verify_file(p)
        with open(p) as fileobj:
            soup = BeautifulSoup(fileobj, "xml")  
        # hack:
        # we need <p> elements, the text in these in the subtitles
        # each <p> may contain spans indicating another speaker
        # however, they may also contain line breaks that *don't* indicate abother speaker
        # i couldn't figure out how to get the text and spans, but ignore the brs
        # so let's just directly replace them with "\n" here
        body = str(soup.body)
        body = re.sub(r"\<br */?\>", "\n", body)
        soup = BeautifulSoup(body, "xml")
        lines = soup.find_all('p')
        return lines

    def _parse_subtitle(self, line: str, **kwargs) -> str: 
        try:
            ts = [line[key] for key in ['begin', 'end']]
        except KeyError:
            raise RuntimeError(f"Could not get 'begin' and 'end' from {line}")
        else:
            ts = [self._format_time(t) for t in ts]
            
        # `line` is <p> element, which contains it's own text and may contain spans
        # get all text, but as separate entities
        # as spans indicate another speaker
        lines = [s for s in line.stripped_strings] 
        if len(lines) > 1:
            lines = [f"- {s}" for s in lines]
        text = "\n".join(lines)
        sub = Subtitle(*ts, text)
        return sub
            
        # text = line.get_text(separator="\n")
        # lines = [line.strip() for line in text.split("\n")]
        # text = "\n".join(lines)
        # sub = Subtitle(*ts, text)
        # return sub
    
    def _verify_subtitles(self, subtitles):
        """ 
        Check if there are multiple subtitles with the same start time. 
        
        If so, combine them.
        """
        subs = [] # list of verified subtitles
        idx = 0
        while idx < len(subtitles):
            group = [] # make temp group of subs with same start
            # could be more than two with the same start, so need inner while loop
            while idx < len(subtitles)-1 and subtitles[idx] == subtitles[idx+1]:
                if not group:
                    # if starting group, append first sub
                    group.append(subtitles[idx])
                # append next
                group.append(subtitles[idx+1])
                idx += 1
            
            if group:
                start = group[0].start
                stop = max([Subtitle.timestamp_to_seconds(sub.stop) for sub in group])
                stop = Subtitle.seconds_to_timestamp(stop)
                text = "\n".join([sub.text for sub in group])
                sub = Subtitle(start, stop, text)
            else:
                sub = subtitles[idx]
            subs.append(sub)
            idx += 1
        return subs
    
    @staticmethod
    def _format_time(ts):
        split = ts.split(":")
        if len(split) == 3:
            hr, mn, sc_ms = split
        elif len(split) == 2:
            mn, sc_ms = split
            hr = 0
        else:
            raise RuntimeError(f"Cannot parse timestamp '{ts}'")
            
        split = sc_ms.split('.')
        if len(split) == 2:
            sc, ms = split
        elif len(split) == 1:
            sc = split[0]
            ms = 0
        else:
            raise RuntimeError(f"Cannot parse timestamp '{ts}'")
            
        ts = [int(t) for t in (hr, mn, sc, ms)]
        return "{:02d}:{:02d}:{:02d},{:03d}".format(*ts)
        
if __name__ == "__main__":
    
    import argparse
    
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('in_file', help='input ttml file')
    parser.add_argument('out_file', help='path to write srt file to')
    
    args = parser.parse_args()
    
    conv = TtmlToSrtConverter()
    conv.convert(args.in_file, args.out_file)