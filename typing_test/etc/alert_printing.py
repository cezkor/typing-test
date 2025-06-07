import curses
from typing_test.etc.colors import ColorPairs as clp
from typing_test.etc.window_checker import WindowChecker
from typing_test.etc import RawKeyCodes


class AlertEmitter:
    __MIN_X = 3

    # minimal y is determined by alert length

    def __init__(self, window, colored):

        self._window = window
        self._colored = colored
        if self._window is None:
            raise ValueError("Argument window is None")
        if self._colored is None:
            raise ValueError("Argument colored is None")
        self.__window_checker = WindowChecker(window, colored)

    def print_alert(self, alert: str, color: int = clp.WHITE_TEXT) -> bool:

        curses.noecho()
        curses.raw()

        w = self._window
        w.keypad(True)
        w.clear()
        curses.curs_set(0)
        y, x = w.getmaxyx()
        alertLines = alert.splitlines()
        alertsBiggerLengths = [len(a) for a in alertLines if len(a) >= self.__MIN_X]

        min_y = max(y // self.__MIN_X + 1, len(alertLines))
        if len(alertsBiggerLengths) == 0:
            min_x = self.__MIN_X
        else:
            min_x = max(alertsBiggerLengths)
        do_leave = self.__window_checker.guard_window_size(min_y, min_x)
        if do_leave:
            return do_leave
        y, x = w.getmaxyx()

        yyy = 0
        for yy in range(len(alertLines)):
            if self._colored:
                w.addstr(yy, 0, alertLines[yy], curses.color_pair(color))
            else:
                w.addstr(yy, 0, alertLines[yy])
            yyy = yy
        if yyy < y - 1:
            yyy += 1
        if self._colored:
            w.addstr(yyy, 0, "Press any key to continue, Ctrl + C to leave", curses.color_pair(clp.GREEN_TEXT))
        else:
            w.addstr(yyy, 0, "Press any key to continue, Ctrl + C to leave")

        w.refresh()

        c = w.getch()
        return c == RawKeyCodes.CTRL_C
