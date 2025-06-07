from enum import Enum
from typing import Tuple

from typing_test.etc import RawKeyCodes
from typing_test.prompts import Prompt
import curses
import curses.ascii
from typing_test.etc.colors import ColorPairs as clp, addstr_full_rgls_color


class Choices(Enum):
    LEAVE = 0
    THE_TEST = 1
    STATISTICS = 2


class StartScreen(Prompt):

    def __init__(self, window, colored, alerter=None):
        super().__init__(window, colored, alerter)
        self._window_checker.min_y = 7 - 1
        self._window_checker.min_x = 50 - 1
        self._do_leave = self._window_checker.guard_window_size()

    def prompt_user(self) -> Tuple:

        if self._do_leave:
            return None,

        window = self._window
        wc = self._window_checker

        curses.raw()
        curses.noecho()
        curses.curs_set(0)
        window.clear()
        window.keypad(True)

        choice = Choices.LEAVE
        self.__print_banner()

        while True:

            c = window.getch()
            # Ctrl + C in raw mode and keypad
            if c == RawKeyCodes.CTRL_C:
                self._do_leave = True
                break
            elif c == ord('1'):
                choice = Choices.THE_TEST
                break
            elif c == ord('2'):
                choice = Choices.STATISTICS
                break
            elif c == curses.KEY_RESIZE:
                self._do_leave = wc.guard_window_size()
                if self._do_leave:
                    break
                window.clear()
                self.__print_banner()
                window.keypad(True)
                curses.curs_set(0)

        return tuple([choice])

    def __print_banner(self):

        window = self._window
        begin_x = 0
        begin_y = 0

        addstr_full_rgls_color(window, self._colored, begin_y, begin_x, "Typing Test",
                               clp.WHITE_TEXT)
        addstr_full_rgls_color(window, self._colored, begin_y + 6, begin_x + 3, "Press 1 or 2; Ctrl + C to leave",
                               clp.WHITE_TEXT)
        addstr_full_rgls_color(window, self._colored, begin_y + 2, begin_x + 3, "Do the tests [1]",
                               clp.WHITE_TEXT)
        addstr_full_rgls_color(window, self._colored, begin_y + 3, begin_x + 3,
                               "Show statistics and previous scores [2]", clp.WHITE_TEXT)

        window.refresh()
