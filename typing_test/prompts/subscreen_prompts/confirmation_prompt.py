from typing import Tuple

from typing_test.prompts import Prompt
import curses
import curses.ascii
from typing_test.etc.colors import ColorPairs as clp, addstr_full_rgls_color
from typing_test.etc import RawKeyCodes


class ConfirmationSubscreen(Prompt):

    def __init__(self,
                 window,
                 colored,
                 alerter=None,
                 yes_key=ord('1'),
                 no_key=ord('2'),
                 prompt_text=None):
        super().__init__(window, colored, alerter)
        self._window_checker.min_y = 0
        self._do_leave = self._window_checker.guard_window_size()
        if prompt_text is None:
            self._prompt_text = f"Are you sure? Yes [{chr(yes_key)}] No [{chr(no_key)}]"
        else:
            self._prompt_text = prompt_text
        self._yes_key, self._no_key = yes_key, no_key

    def __print_banner(self):

        window = self._window
        try:
            addstr_full_rgls_color(window, self._colored, 0, 0, self._prompt_text,
                               clp.WHITE_TEXT)
        except curses.error:
            pass
        window.refresh()

    def prompt_user(self) -> Tuple:

        if self._do_leave:
            return tuple([True])

        window = self._window
        wc = self._window_checker

        curses.raw()
        curses.noecho()
        curses.curs_set(0)
        window.clear()
        window.keypad(True)

        yes = False
        self.__print_banner()

        while True:

            c = window.getch()
            if c == self._yes_key or c == RawKeyCodes.CTRL_C:
                if c == RawKeyCodes.CTRL_C:
                    self._do_leave = True
                yes = True
                break
            elif c == self._no_key:
                break
            elif c == curses.KEY_RESIZE:
                wc.guard_window_size()
                window.clear()
                window.keypad(True)
                self.__print_banner()
                curses.curs_set(0)

        return tuple([yes])
