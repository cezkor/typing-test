from typing_test.etc import RawKeyCodes
from typing_test.etc.colors import ColorPairs as clp, addstr_full_rgls_color
import curses
import curses.ascii
import textwrap as tr
from typing_test.etc.window_checker import WindowCheckerScreen


class Textbox:
    __EMPTY = ''

    @staticmethod
    def __empties(n: int = 0):
        return [''] * n

    @staticmethod
    def __find_first_empty_str_from_left(l: list[str]):
        i = 0
        while i < len(l) and l[i] != '':
            i += 1
        return i

    class TerminalTraversingChecker:

        def __init__(self):

            self.dir_dict = {
                curses.KEY_UP: (-1, 0),
                curses.KEY_DOWN: (1, 0),
                curses.KEY_LEFT: (0, -1),
                curses.KEY_RIGHT: (0, 1)
            }

        # where to traverse when on the edge of screen
        def where_to_traverse(self, y: int, x: int, direction: int, y_bound: int, x_bound: int):
            if not self.can_move_there(y, x, direction, y_bound, x_bound):
                _, dx = self.dir_dict[direction]
                xp = x + dx
                if x == 0 and xp < 0 < y <= y_bound - 1:
                    return y - 1, x_bound - 1
                if x == x_bound - 1 and xp >= x_bound and 0 <= y < y_bound - 1:
                    return y + 1, 0
                return y, x
            else:
                dy, dx = self.dir_dict[direction]
                return y + dy, x + dx

        def can_move_there(self, y: int, x: int, direction: int, y_bound: int, x_bound: int):
            can = False

            if direction in self.dir_dict.keys():
                vy, vx = self.dir_dict[direction]
                yp, xp = y + vy, x + vx
                if 0 <= yp < y_bound and 0 <= xp < x_bound:
                    can = True

            return can

    def __init__(self,
                 window,
                 colored,
                 lines: int,
                 cols: int,
                 begin_y: int,
                 begin_x: int,
                 wrap_text=False,
                 window_checker=None):
        self._window = window
        self._colored = colored
        self._lines = lines
        self._cols = cols
        self._x = begin_x
        self._y = begin_y
        self._wrap = wrap_text
        if window_checker is None:
            mwc = self._window_checker = WindowCheckerScreen(window, colored)
            mwc.min_y, mwc.min_x = self._window.getmaxyx()
            mwc.min_y, mwc.min_x = mwc.min_y - 1, mwc.min_x - 1
        else:
            self._window_checker = window_checker

        self.__test_args()

        self._laid_out_plaintext: list[list[str]] = [self.__empties(cols) for x in range(lines)]
        self._true_plaintext = self.__EMPTY

        self._ttc_checker = self.TerminalTraversingChecker()
        self._subscreen = None
        self._text_color = clp.WHITE_TEXT

        self._last_y, self._last_x = -1, -1

    def __test_args(self):
        if self._window is None:
            raise ValueError('Argument window is None')
        if self._colored is None:
            raise ValueError('Argument colored is None')

    def _put_all_to_subscreen(self):
        if self._subscreen is not None:
            swin = self._subscreen
            swin.clear()
            for y in range(self._lines):
                self._put_line_to_subscreen(y)

    def _put_line_to_subscreen(self, lnum: int):
        if self._subscreen is not None and lnum < self._lines:
            y, x = self._subscreen.getyx()
            try:
                addstr_full_rgls_color(self._subscreen, self._colored,
                                       lnum, 0, ''.join(self._laid_out_plaintext[lnum]),
                                       self._text_color)
            except curses.error:
                pass
            self._subscreen.move(y, x)

    def save_position(self):
        if self._subscreen is not None and (-1, -1) != (self._last_y, self._last_x):
            self._last_y, self._last_x = self._subscreen.getyx()

    def edit(self):

        """

            main loop for editorial events
            exits when user stops editing
            or main window was resized

        """

        if self._subscreen is None:
            self._subscreen = self._window.subwin(self._lines, self._cols, self._y, self._x)

            if (self._last_y, self._last_y) == (-1, -1):
                self._last_y, self._last_x = 0, 0

        curses.raw()
        curses.noecho()
        curses.curs_set(1)
        self._subscreen.keypad(True)

        self._put_all_to_subscreen()
        self._subscreen.refresh()
        self._subscreen.move(self._last_y, self._last_x)

        do_leave = False
        endOfEdit = False
        redraw = False
        while not endOfEdit and not redraw and not do_leave:
            key = self._subscreen.getch()
            (endOfEdit, redraw, do_leave) = self._handle_key(key)
            self._subscreen.refresh()

        if not do_leave: # assume redraw
            self._recalc_whole_text()
            self._last_y, self._last_x = self._subscreen.getyx()
        return self._true_plaintext, redraw, do_leave

    def _handle_backspace(self):

        if self._subscreen is not None:
            swin = self._subscreen
            lo = self._laid_out_plaintext
            ttc = self._ttc_checker

            y, x = swin.getyx()

            ny, nx = ttc.where_to_traverse(y, x, curses.KEY_LEFT, self._lines, self._cols)
            swin.move(ny, nx)

            if (y + 1, x + 1) == swin.getmaxyx():
                if lo[y][x] != self.__EMPTY:
                    lo[y][x] = self.__EMPTY
                elif lo[y][x] == self.__EMPTY and self._cols > 1 and lo[y][x - 1] != self.__EMPTY:
                    lo[y][x - 1] = self.__EMPTY
                self._recalc_whole_text()
                self._put_all_to_subscreen()
                swin.move(ny, nx)
                return

            if lo[ny][nx] != self.__EMPTY:
                lo[ny][nx] = self.__EMPTY
                self._recalc_whole_text()
                self._put_all_to_subscreen()
                swin.move(ny, nx)

    def _handle_arrow_keys(self, key: int):
        if self._subscreen is not None and not self._has_done_editor_like_behaviour(key):
            # behave like terminal
            swin = self._subscreen
            y, x = swin.getyx()
            ttc = self._ttc_checker
            ny, nx = ttc.where_to_traverse(y, x, key, self._lines, self._cols)
            swin.move(ny, nx)

    def _put_printable(self, key: int):

        if self._subscreen is not None:
            swin = self._subscreen
            lo = self._laid_out_plaintext
            ttc = self._ttc_checker

            y, x = swin.getyx()
            # if possible to insert new character
            if lo[y][x] == self.__EMPTY:
                lo[y][x] = chr(curses.ascii.ascii(key))
                if x == self._cols - 1 and y < self._lines - 1:
                    self._recalc_whole_text()
                    self._put_all_to_subscreen()
                else:
                    try:
                        self._put_line_to_subscreen(y)
                    except curses.error:
                        """ "Attempting to write to the lower right corner of a window, subscreen, or pad will 
                        cause an exception to be raised after the character is printed." """

            else:
                self._recalc_true_plaintext()
                if len(self._true_plaintext) < self._cols * self._lines:
                    lo[y].insert(x, chr(curses.ascii.ascii(key)))
                    self._recalc_whole_text()
                    self._put_all_to_subscreen()
                else:
                    lo[y][x] = chr(curses.ascii.ascii(key))
                    try:
                        self._put_line_to_subscreen(y)
                    except curses.error:
                        """ "Attempting to write to the lower right corner of a window, subscreen, or pad will 
                        cause an exception to be raised after the character is printed." """

            # try to move to the left
            if (y + 1, x + 1) == swin.getmaxyx() or len(self._true_plaintext) == self._cols * self._lines:
                return
            ny, nx = ttc.where_to_traverse(y, x, curses.KEY_RIGHT, self._lines, self._cols)
            swin.move(ny, nx)

    def _handle_key(self, key: int) -> tuple[bool, bool, bool]:  # one is expected to override this method to add additional checks

        end = False
        redraw = False
        do_leave = False

        if self._subscreen is not None:

            if key == RawKeyCodes.CTRL_E:
                end = True
            if key == RawKeyCodes.CTRL_C:
                do_leave = True
            elif key == curses.KEY_RESIZE:
                do_leave = self._window_checker.guard_window_size()
                if do_leave:
                    return False, False, True
                # guarding window size is always responsibility of the deepest class
                # that is interpreting user input
                self._subscreen.clear()
                redraw = True
            elif key in [curses.KEY_UP, curses.KEY_DOWN, curses.KEY_LEFT, curses.KEY_RIGHT]:
                self._handle_arrow_keys(key)
            elif key in [curses.KEY_ENTER, curses.ascii.NL, RawKeyCodes.ASCII_ENTER]:
                # by default, this textbox does NOT support line breaking, only wrapping
                # line breaking won't be useful for purpose of this application
                pass
            elif curses.ascii.isascii(key) and curses.ascii.isprint(key):
                self._put_printable(key)
            elif key in [curses.KEY_BACKSPACE, curses.ascii.BS]:
                self._handle_backspace()

        return end, redraw, do_leave

    def _has_done_editor_like_behaviour(self, key: int):

        if self._subscreen is None:
            pass

        has_intervened = False
        swin = self._subscreen
        y, x = swin.getyx()
        ttc = self._ttc_checker
        move_like_pressed = key

        x_shift = 0
        coreol_case1 = (0 <= x < self._cols - 1 and self._laid_out_plaintext[y][x] == self.__EMPTY
                        and self._laid_out_plaintext[y][x + 1] == self.__EMPTY)
        coreol_case2 = (x == self._cols - 1 and self._laid_out_plaintext[y][x] == self.__EMPTY)
        cursorOnRightEndOfNotFullLine = coreol_case1 or coreol_case2
        isThereLineBelow = (0 <= y < self._lines - 1
                            and self.__find_first_empty_str_from_left(self._laid_out_plaintext[y + 1]) > 0)
        isThereEmptyBelow = (0 <= y < self._lines - 1 and self._laid_out_plaintext[y + 1][x] == self.__EMPTY)
        isThereEmptyAbove = (0 < y <= self._lines - 1 and self._laid_out_plaintext[y - 1][x] == self.__EMPTY)

        if key == curses.KEY_LEFT and x == 0:
            if 0 < y <= self._lines - 1:
                x_shift = min(-self.__find_first_empty_str_from_left(self._laid_out_plaintext[y - 1]) + 1, 0)
            move_like_pressed = curses.KEY_UP
        if key == curses.KEY_RIGHT and cursorOnRightEndOfNotFullLine:
            if isThereLineBelow:
                move_like_pressed = curses.KEY_DOWN
                x_shift = x - self.__find_first_empty_str_from_left(self._laid_out_plaintext[y + 1])
            else:
                # don't move
                return True
        # shift to beginning of line if cursor ends up trying to go into empty space
        if key == curses.KEY_DOWN and isThereLineBelow and isThereEmptyBelow:
            x_shift = x - self.__find_first_empty_str_from_left(self._laid_out_plaintext[y + 1])
        if key == curses.KEY_DOWN and not isThereLineBelow:
            # cursor should not move into empty space if it hasn't been on filled-up line (assume there is no endline)
            return True
        if key == curses.KEY_UP and isThereEmptyAbove:
            x_shift = x - self.__find_first_empty_str_from_left(self._laid_out_plaintext[y - 1])

        if key != move_like_pressed or x_shift != 0:
            if ttc.can_move_there(y, x - x_shift, move_like_pressed, self._lines, self._cols):
                vy, vx = ttc.dir_dict[move_like_pressed]
                yd, xd = y + vy, x + vx - x_shift
                swin.move(yd, xd)
            has_intervened = True

        return has_intervened

    @property
    def plaintext(self) -> str:
        self._recalc_true_plaintext()
        return self._true_plaintext

    @property
    def lines(self) -> list[str]:
        return [''.join(self._laid_out_plaintext[i]) for i in range(len(self._laid_out_plaintext))]

    @plaintext.setter
    def plaintext(self, text: str):
        self._true_plaintext = text
        self._recalc_laid_out_plaintext()

    def _recalc_whole_text(self):
        self._recalc_true_plaintext()  # based on (possibly broken by input) laid-out text
        self._recalc_laid_out_plaintext()  # based on recalculated plaintext - lay it out

    def _recalc_true_plaintext(self):
        x = ''
        for y in range(self._lines):
            x = x + ''.join(self._laid_out_plaintext[y])
        self._true_plaintext = x

    def _recalc_laid_out_plaintext(self):
        if self._wrap:

            wrapped = tr.wrap(self._true_plaintext, width=self._cols, drop_whitespace=False)
            self._laid_out_plaintext = [list(x) + self.__empties(self._cols - len(x))
                                        for x in wrapped]
            if len(self._laid_out_plaintext) < self._lines:
                for x in range(self._lines - len(self._laid_out_plaintext)):
                    self._laid_out_plaintext.append(self.__empties(self._cols))
        else:

            # lay characters as they go
            x = self._true_plaintext.strip()
            self._laid_out_plaintext.clear()
            while len(x) >= self._cols:
                self._laid_out_plaintext.append(list(x[:self._cols]))
                x = x[self._cols:]

            if self._cols > len(x) and len(self._laid_out_plaintext) < self._lines:
                self._laid_out_plaintext.append(list(x) + self.__empties(self._cols - len(x)))
            __ = len(self._laid_out_plaintext)
            for _ in range(__ - self._lines):
                self._laid_out_plaintext.append(self.__empties(self._cols))
