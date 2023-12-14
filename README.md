# Subtitools

A tool for manipulating subtitle files.

## Dependencies

- python 3.9+
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)

Optionally, also install [charset_normalizer](https://pypi.org/project/charset-normalizer)
to support reading non-UTF8 file out of the box.

## Usage

You may wish to make `subtitools.py` executable and link it to a location in 
your `PATH`, for example, to create a link in `~/.local/bin`:
```bash
chmod 755 subtitools.py
SUBTITOOLS=`readlink -f subtitools.py`
cd ~/.local/bin
ln -s $SUBTITOOLS subtitools
```

The following sections assume you have done this, or something similar, and so 
you can simply call `subtitools` rather than `python3 subtitools.py`

### shift

Shift subs in a .srt file forwards or backwards, by a given number of hours, 
minutes, seconds and/or milliseconds.

See `subtitools shift -h` for more info.

### convert

Tools to convert various subtitle formats to .srt (work in progress).

See `subtitools convert -h` for more info.