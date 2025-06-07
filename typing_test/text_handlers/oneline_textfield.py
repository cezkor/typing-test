import curses
import curses.ascii

from typing_test.etc import RawKeyCodes
from typing_test.etc.window_checker import WindowChecker
from typing_test.text_handlers.textbox import Textbox


class AcceptingTextbox(Textbox):

    def _handle_key(self, key: int) -> tuple[bool, bool, bool]:
        end, redraw, do_leave = super()._handle_key(key)
        if key in [curses.KEY_ENTER, curses.ascii.NL, RawKeyCodes.ASCII_ENTER]:
            end = True
        return end, redraw, do_leave


class OnelineTextFieldSubwindow:

    def __init__(self, window, colored, length: int = 5, begin_y: int = 0, begin_x: int = 0, window_checker=None):

        self._window = window
        self._colored = colored
        self._length = length
        self._y = begin_y
        self._x = begin_x
        if window_checker is None:
            wc = self._window_checker = WindowChecker(window, colored)
            y, x = self._window.getmaxyx()
            wc.min_y, wc.min_x = y - 1, x - 1
        else:
            self._window_checker = window_checker

        self.__test_args()

    def __test_args(self):
        if self._window is None:
            raise ValueError('Argument window is None')
        if self._colored is None:
            raise ValueError('Argument colored is None')
        if self._length < 1:
            raise ValueError('Length of field less than one')

    def probe_for_text(self) -> tuple[str, bool, bool]:

        tbox = AcceptingTextbox(
            self._window,
            self._colored,
            1,
            self._length,
            self._y,
            self._x,
            window_checker=self._window_checker
        )

        return tbox.edit()


