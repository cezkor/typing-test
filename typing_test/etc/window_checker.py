"""! Window size guarding (checking)."""

import curses
from typing_test.etc.colors import ColorPairs as clp
from typing_test.etc import RawKeyCodes


## Window size guard, printing to the entire window.
#
# \important Objects containing object of WindowCheckerScreen class should use ::guard_window_size() to ensure proper
# window size.
# Especially, if given object processes keystrokes, anytime it encounters the \c curses.KEY_RESIZE keycode it should
# use window checker to ensure it is still possible to fit the content and then reprint the content.

class WindowCheckerScreen:

    ## Text displayed to user when window size is less than minimal guarded
    _TEXT = "Window size too small; please resize, then press any key to try again or press Ctrl + C and leave"
    ## Length of ::_TEXT
    _TEXT_LEN = len(_TEXT)

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
        self._min_y, self._min_x = window.getmaxyx()
        ## @var _min_y
        # Minimal number of lines to guard (default: current number of lines of the window)
        ## @var _min_x
        # Minimal number of columns to guard (default: current number of columns of the window)

    ## Getter of ::_min_y
    # @param self object pointer
    # @returns minimal number of lines to guard
    @property
    def min_y(self):
        return self._min_y

    ## Setter of ::_min_y
    # @param self object pointer
    # @param min_y new minimal number of lines to guard
    @min_y.setter
    def min_y(self, min_y):
        self._min_y = min_y

    ## Getter of ::_min_x
    # @param self object pointer
    # @returns minimal number of columns to guard
    @property
    def min_x(self):
        return self._min_x

    ## Setter of ::_min_x
    # @param self object pointer
    # @param min_x new minimal number of columns to guard
    @min_x.setter
    def min_x(self, min_x):
        self._min_x = min_x

    ## Helper method for printing window size information to user.
    # @param self object pointer
    def __print_banner(self):

        w = self._window
        if self._colored:
            w.addstr(0, 0, self._TEXT,
                     curses.color_pair(clp.WHITE_TEXT))
        else:
            w.addstr(0, 0, self._TEXT)

    ## Waits for the user to either leave the application or resize the terminal of the window.
    # The size of at least ::_min_y lines by ::_min_x columns is required to exit this method, provided user
    # did not choose to leave. Provided satisfactory window size then user has to press any key to continue.
    #
    # @param self object pointer
    # @param min_y (optional) minimal number of lines; overwrites ::_min_y
    # @param min_x (optional) minimal number of columns; overwrites ::_min_x
    # @return boolean value describing whether user wants to leave the application (after pressing \c Ctrl \c + \c C)

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
