import curses
from typing_test.etc.colors import ColorPairs as clp
from typing_test.etc import RawKeyCodes


class WindowChecker:
    _TEXT = "Window size too small; please resize, then press any key to try again or press Ctrl + C and leave"
    _TEXT_LEN = len(_TEXT)

    def __init__(self, window, colored):

        self._window = window
        self._colored = colored
        if self._window is None:
            raise ValueError("Argument window is None")
        if self._colored is None:
            raise ValueError("Argument colored is None")
        self._min_y, self._min_x = window.getmaxyx()

    @property
    def min_y(self):
        return self._min_y

    @min_y.setter
    def min_y(self, min_y):
        self._min_y = min_y

    @property
    def min_x(self):
        return self._min_x

    @min_x.setter
    def min_x(self, min_x):
        self._min_x = min_x

    def __print_banner(self):

        w = self._window
        if self._colored:
            w.addstr(0, 0, self._TEXT,
                     curses.color_pair(clp.WHITE_TEXT))
        else:
            w.addstr(0, 0, self._TEXT)

    def guard_window_size(self, min_y=None, min_x=None) -> bool:
        if min_y is None:
            min_y = self._min_y
        if min_x is None:
            min_x = self._min_x

        if not curses.isendwin():
            y, x = self._window.getmaxyx()
            while min_y > y or min_x > x:
                curses.raw()
                curses.noecho()
                curses.curs_set(0)
                self._window.clear()
                self._window.keypad(True)
                if (y - 1)*(x - 1) > self._TEXT_LEN:
                    self.__print_banner()
                    self._window.refresh()
                c = self._window.getch()
                while c == curses.KEY_RESIZE:
                    c = self._window.getch()
                if c == RawKeyCodes.CTRL_C:
                    return True
                y, x = self._window.getmaxyx()

        return False
