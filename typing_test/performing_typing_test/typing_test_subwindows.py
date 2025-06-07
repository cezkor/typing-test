import curses
import curses.ascii
from typing_test.etc.colors import addstr_full_rgls_color, ColorPairs as clp


class TypingTestInformationSubwindow:

    def __init__(self, window, colored, begin_y: int, begin_x: int):
        self._master_window = window
        self._colored = colored
        self._by = begin_y
        self._bx = begin_x
        y, x = window.getmaxyx()
        if y > 5:
            self._window = window.derwin(5, x, begin_y, begin_x)
        else:
            self._window = None
        self._test_args()

    def _test_args(self):
        if self._master_window is None:
            raise ValueError('Argument window is None')
        if self._colored is None:
            raise ValueError('Argument colored is None')

    def __print_banner(self):

        _, x = self._window.getmaxyx()

        if self._colored:
            self._window.hline(0, 0, curses.ACS_HLINE, x, curses.color_pair(clp.WHITE_TEXT))
        else:
            self._window.hline(0, 0, curses.ACS_HLINE, x)
        try:
            addstr_full_rgls_color(self._window, self._colored, 3, 0,
                                   "Press Ctrl + C to leave without saving", clp.WHITE_TEXT)
        except curses.error:
            pass

    def print_info(self, mis_inputs: int, test_number: int):
        y, x = self._master_window.getmaxyx()
        if y < 5:
            return
        if self._window is None:
            self._window = self._master_window.derwin(5, x, self._by, self._bx)

        y, x = self._master_window.getyx()
        self._window.clear()
        self.__print_banner()
        text = f"Number of test: {test_number} Misinputs: "
        if self._colored:
            self._window.addstr(2, 0, text, clp.WHITE_TEXT)
            if mis_inputs > 0:
                color = clp.RED_TEXT
            else:
                color = clp.GREEN_TEXT
            self._window.addstr(2, len(text), f"{mis_inputs}", curses.color_pair(color))
        else:
            self._window.addstr(2, 0, f"{text} {mis_inputs}")

        self._window.refresh()
        self._master_window.move(y, x)
