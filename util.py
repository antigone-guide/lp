#!/usr/bin/env python3

import os
from termios import *
from types import *
from sys import stdin, stdout

enable_color = 1

colors = dict([c.split() for c in (     # make dict {"red": "31", ...}
  "black 30, red 31, green 32, brown 33, blue 34, purple 35, cyan 36, lgray 37, gray 1;30, "
  "lred 1;31, lgreen 1;32, yellow 1;33, lblue 1;34, pink 1;35, lcyan 1;36, white 1;37"
).split(', ')])

"\033]Pg4040ff\033\\"


def color(text, fg, bg=None, raw=0):
    # init vars
    xterm, bgcode = 0, ''
    if not enable_color or not fg:
        return text
    if not isinstance(fg, str):
        fg, bg = fg
    opencol, closecol = "\033[", "m"
    tpl = "\033[%sm"
    if raw:
        opencol, closecol = r"\033[", r"\033[0m"
    # clear = opencol + '0' + closecol
    clear = tpl % 0
    if os.environ["TERM"] == "xterm":
        xterm = 1

    # create color codes
    if xterm and fg == "yellow":    # In xterm, brown comes out as yellow..
        fg = "brown"
    # fgcode = opencol + colors[fg] + closecol
    fgcode = tpl % colors[fg]
    if bg:
        if bg == "yellow" and xterm: bg = "brown"

        try: bgcode = opencol + colors[bg].replace('3', '4', 1) + closecol
        except KeyError: pass

    return "%s%s%s%s" % (bgcode, fgcode, text, clear)


class Term:
    def __init__(self):
        self.fd = stdin.fileno()
        self.new_term, self.old_term = tcgetattr(self.fd), tcgetattr(self.fd)
        self.new_term[3] = (self.new_term[3] & ~ICANON & ~ECHO)

    def normal(self):
        """Set 'normal' terminal settings."""
        tcsetattr(self.fd, TCSAFLUSH, self.old_term)

    def clear(self):
        """Clear screen."""
        os.system("clear")

    def cline(self):
        """Clear line."""
        stdout.write('\r' + ' '*self.size()[1])
        stdout.flush()

    def curses(self):
        """Set 'curses' terminal settings. (noecho, something else?)"""
        tcsetattr(self.fd, TCSAFLUSH, self.new_term)

    def getch(self, prompt=None):
        if prompt:
            stdout.write(prompt)
            stdout.flush()
        self.curses()
        c = os.read(self.fd, 3)
        self.normal()
        try:
            return unicode(c)[2:-1]
        except NameError:
            return str(c)[2:-1]

    def size(self):
        import struct, fcntl
        h, w = struct.unpack("hhhh", fcntl.ioctl(0, TIOCGWINSZ, "\000"*8))[0:2]
        if not h:
            h, w = 24, 80
        return h, w
