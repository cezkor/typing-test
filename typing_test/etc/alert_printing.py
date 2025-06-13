"""! Printing alerts to user."""

import curses
from typing_test.etc.colors import ColorPairs as clp
from typing_test.etc.window_checker import WindowCheckerScreen
from typing_test.etc import RawKeyCodes


## Class for alert printing to entire terminal window.
class AlertEmitterScreen:

    ## Minimal number of columns required for printing an alert
    # @note Minimal number of lines are determined dynamically by alert text length in ::print_alert().
    # Text of an alert may require more columns than ::__MIN_X. This is only the minimal value required by the class.
    __MIN_X = 3

    ## Initializes new instance of this class.
    #
    # @param self object pointer
    # @param window Curses' window object
    # @param colored terminal text color support

    def __init__(self, window, colored):

        ## Curses' window object
        self._window = window
        ## Terminal text color support
        self._colored = colored
        if self._window is None:
            raise ValueError("Argument window is None")
        if self._colored is None:
            raise ValueError("Argument colored is None")
        ## Window size checker
        self.__window_checker = WindowCheckerScreen(window, colored)

    ## Prints alert to window. An alert is an information presented
    # to user which does not require them to provide any input (see typing_test::prompts::Prompt)
    # besides any key to skip.
    #
    # If possible, the information is printed within entire window. Window checker is used to ensure it is possible to
    # print within given window.
    #
    # @param self object pointer
    # @param alert text of the alert
    # @param color identifier of color to use (see ColorPairs)
    # @return boolean value describing whether user wants to leave the application (after pressing \c Ctrl \c + \c C)
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

        # determining minimal lines number
        min_y = max(y // self.__MIN_X + 1, len(alertLines)) + 2
        # determining actual minimal cols number
        if len(alertsBiggerLengths) == 0:
            min_x = self.__MIN_X
        else:
            min_x = max(alertsBiggerLengths)

        c = curses.KEY_RESIZE
        while c == curses.KEY_RESIZE:
            do_leave = self.__window_checker.guard_window_size(min_y, min_x)
            if do_leave:
                return True
            y, x = w.getmaxyx()
            # printing alert
            yyy = 0
            for yy in range(len(alertLines)):
                if self._colored:
                    w.addstr(yy, 0, alertLines[yy], curses.color_pair(color))
                else:
                    w.addstr(yy, 0, alertLines[yy])
                yyy = yy
            if yyy < y - 1:
                # required for putting the line below with one line empty (which is why at least two lines are required)
                yyy += 1
            if self._colored:
                w.addstr(yyy, 0, "Press any key to continue, Ctrl + C to leave", curses.color_pair(clp.GREEN_TEXT))
            else:
                w.addstr(yyy, 0, "Press any key to continue, Ctrl + C to leave")

            w.refresh()

            c = w.getch()

        return c == RawKeyCodes.CTRL_C
