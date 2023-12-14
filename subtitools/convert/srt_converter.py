#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Base class for converting to srt files.

Use a mixin/subclass to implement `_parse_subtitle` method.

Users should call :meth:`SrtConverter.convert` to read and write files.
"""
from pathlib import Path
import re
from ..utils import read_lines

class Subtitle:
    """ 
    Class representing a pair of start and stop times and text for a subtitle line. 
    
    `start` and `stop` should be strings in "HH:MM:ss,mmm" format. If the format
    differs slightly (e.g. '.' instead of ',' as millisecond separator), it will
    attempt to rectify this internally.
    
    Use the :meth:`start` and :meth:`stop` properties to access the component
    strings; formatting the Subtitle as a string automatically renders it correctly.
    
    The less than, greater than and equal to operators compare the :meth:`start` 
    values of Timestamps.
    """
    
    def __init__(self, start, stop, text):
        # verify format of `start` and `stop` before assigning
        hr, mn, sc, ms = self._verify_string(start)
        self._start = self.format_timestamp(hr, mn, sc, ms)
        hr, mn, sc, ms = self._verify_string(stop)
        self._stop = self.format_timestamp(hr, mn, sc, ms)
        
        self._text = text
        
    @property
    def start(self):
        return self._start
    
    @property
    def stop(self):
        return self._stop
    
    @property
    def text(self):
        return self._text
    
    def __lt__(self, other):
        """ Return True if self's `start` is before other's """
        return self.timestamp_to_seconds(self.start) < self.timestamp_to_seconds(other.start)
    
    def __gt__(self, other):
        """ Return True if self's `start` is after other's """
        return self.timestamp_to_seconds(self.start) > self.timestamp_to_seconds(other.start)
    
    def __eq__(self, other):
        """ Return True if self's `start` is same as other's """
        return self.start == other.start
    
    def __repr__(self):
        return f"{self.start} --> {self.stop}\n{self.text}"
    
    @staticmethod
    def format_timestamp(hr, mn, sc, ms) -> str:
        """ Given hours, minutes, seconds, milliseconds, return timestamp string. """
        ts = [int(t) for t in (hr, mn, sc, ms)]
        return "{:02d}:{:02d}:{:02d},{:03d}".format(*ts)
    
    @classmethod
    def seconds_to_timestamp(cls, s: float) -> str:
        """ Convert int `s` in seconds to timestamp in format "HH:MM:ss,mmm" """
        hr, mn = divmod(s, 3600)
        mn, sc = divmod(mn, 60)
        sc, ms = divmod(sc, 1)
        ms *= 1000
        return cls.format_timestamp(hr, mn, sc, ms)
    
    @classmethod
    def timestamp_to_seconds(cls, ts: str) -> float:
        """ Convert timestamp string to number of seconds """
        hr, mn, sc, ms = cls._verify_string(ts)
        sc += 3600*hr + 60*mn + ms/1000
        return sc
    
    @staticmethod
    def _verify_string(ts):
        """ Verify that string `ts` represents a timestamp in the expected format. """
        try:
            hr, mn, sc, ms = [float(s) for s in re.split(r"\:|\,", ts)]
        except Exception:
            try:
                hr, mn, sc, ms = [float(s) for s in re.split(r"\:|\.", ts)]
            except Exception:
                msg = f"Could not parse timestamp '{ts}'. Expected format is 'HH:MM:ss,mmm'"
                raise RuntimeError(msg)
        return hr, mn, sc, ms

class SrtConverter:
    
    def __init__(self, quiet=False):
        self._quiet = quiet
        self._subs = []

    def convert(self, in_path, out_path=None, encoding='utf-8', **kwargs):
        """ 
        Convert subtitle file `in_path` to srt and write to `out_path`
        
        If `out_path` is None, prompt to overwrite (if `self.quiet` is False - 
        otherwise overwrite without prompting).
        """
        in_path = Path(in_path)
        file_content = self._parse(in_path, encoding=encoding)
        
        if out_path is None:
            out_path = in_path
        else:
            out_path = Path(out_path)
            if not self._quiet and out_path.exists():
                overwrite = self._prompt_overwrite(out_path)
                if not overwrite:
                    print("Aborting")
                    return
                
        subtitles = [self._parse_subtitle(line, **kwargs) for line in file_content]
        subtitles = self._verify_subtitles(subtitles)
        subtitles = self._index_subtitles(subtitles)
        subtitles = "\n".join(subtitles)
        
        with open(out_path, 'w') as fileobj:
            fileobj.write(subtitles)
            
    def _parse(self, p: Path, encoding: str='utf-8') -> list:
        """ 
        Return list of non-empty lines in file `path`. 
        
        If overriding, this method must return an iterable object.
        """
        self._verify_file(p)
        lines = read_lines(p)
        return lines
    
    def _parse_subtitle(self, line: str, **kwargs) -> Subtitle:
        """
        Implement this method in subclasses/mixins.
        
        Parse `line` to get start and stop times, and the subtitle content.
        
        Return a :class:`Subtitle` object.
        """
        raise NotImplementedError("Implement '_parse_subtitle' in subclasses/mixins")
        
    def _verify_subtitles(self, subtitles: list[Subtitle]) -> list[Subtitle]:
        """ Override this in subclasses to check the subtitles returned by :meth:`_parse_subtitle` """
        return subtitles
    
    def _index_subtitles(self, subtitles: list[Subtitle]) -> list[str]:
        """ Return list of indexed strings from list of Subtitles. """
        subtitles = [f"{idx+1}\n{sub}\n" for idx, sub in enumerate(subtitles)]
        return subtitles
        
    @staticmethod
    def _verify_file(p: Path):
        """ 
        Verify that `p` exists and is a file. 
        
        Raises exceptions if either of these conditions is False. Otherwise return True.
        """
        if not p.exists():
            raise FileNotFoundError(f"No such file {p}")
        if not p.is_file():
            raise RuntimeError(f"Path {p} is not a file")
        return True
    
    @staticmethod
    def _prompt_overwrite(p: Path) -> bool:
        """ Ask user if they want to overwrite file `p` """
        reply = input(f"File '{p}' already exists. Overwrite? [Y/n] ")
        reply = reply.strip().lower()
        if not reply or reply.startswith('y'):
            return True
        else:
            return False