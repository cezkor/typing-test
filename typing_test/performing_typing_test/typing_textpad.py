import curses
import curses.ascii
from typing_test.etc.window_checker import WindowChecker
from typing_test.etc.colors import addstr_full_rgls_color, ColorPairs as clp
from typing_test.text_handlers.textbox import Textbox
from typing_test.performing_typing_test.words_handler import WordsHandler, WordsHandlerStringConst as SC


class TypingTextpad(Textbox):

    def __init__(self, window, colored, lines: int, cols: int, begin_y: int, begin_x: int,
                 window_checker: WindowChecker = None):
        super().__init__(window, colored, lines, cols, begin_y, begin_x, window_checker=window_checker, wrap_text=True)
        self._info_window = None
        self._test_text = ''
        self._test_text_lines = []

        self._text_color = clp.GRAY_TEXT
        self._good_text_color = clp.GREEN_TEXT
        self._bad_text_color = clp.RED_TEXT
        self._goodOrBadDict = {True: self._good_text_color, False: self._bad_text_color}

        self._words_handler = WordsHandler()

        self._can_fit_text = False
        self._number_of_test = -1

    @property
    def number_of_test(self):
        return self._number_of_test

    @number_of_test.setter
    def number_of_test(self, n: int):
        self._number_of_test = n

    @property
    def info_window(self):
        return self._info_window

    @info_window.setter
    def info_window(self, w):
        self._info_window = w

    @property
    def test_text(self):
        return self._test_text

    @test_text.setter
    def test_text(self, text):
        self._recalc_or_and_set_test_text_lines(text)

    def _recalc_or_and_set_test_text_lines(self, text, recalc_only: bool = False):
        tmp1, tmp2 = self._true_plaintext, self._laid_out_plaintext
        # test text layout and text discovery strongly depends on how it can be displayed
        self._true_plaintext = text
        self._recalc_laid_out_plaintext()
        self._test_text_lines = self._laid_out_plaintext

        if self._lines < len(self._laid_out_plaintext):
            # it is incorrect not to display all lines of text
            self._can_fit_text = False
            self._test_text = text
        else:
            # plaintext is generated only using visible lines
            self._can_fit_text = True
            self._recalc_true_plaintext()
            self._test_text = self._true_plaintext

        self._true_plaintext, self._laid_out_plaintext = tmp1, tmp2

        self._words_handler.test_text_dict = {
            SC.TEST_TEXT: self._test_text,
            SC.TEST_TEXT_LINES: self._test_text_lines,
            SC.RECALC_ONLY: recalc_only
        }

    @property
    def test_data(self):
        return self._words_handler.test_data

    def edit(self):
        wh = self._words_handler
        self._recalc_or_and_set_test_text_lines(self._test_text, True)
        wh.start_registering()

        if self._info_window is not None:
            self._info_window.print_info(self._words_handler.misinputs, self._number_of_test)

        do_leave = False
        while not self._can_fit_text:
            _, x = self._window.getmaxyx()
            do_leave = self._master_window_checker.guard_window_size(1, x + 1)
            if do_leave:
                break
            _, self._cols = self._window.getmaxyx()
            self._recalc_or_and_set_test_text_lines(self._test_text, True)
        if do_leave:
            return '', False, True

        # this method can end either because it needs redrawing
        _, redraw, do_leave = super().edit()
        if do_leave:
            return _, False, True
        if not redraw:
            # or the test is over
            redraw = not self._are_texts_matching()
        return _, redraw, do_leave

    def _handle_arrow_keys(self, key: int):
        pass  # do not allow moving cursor in any other way than via backspace and putting characters

    @staticmethod
    def __char_or_space_or_hash(char: str, replace: bool):
        if replace and char == ' ':
            return '#'
        else:
            return char

    def _put_line_to_subwindow(self, lnum: int):
        if self._subwindow is not None and lnum < self._lines:
            swin = self._subwindow
            gobDict = self._goodOrBadDict
            y, x = swin.getyx()
            if self._colored:
                if len(''.join(self._laid_out_plaintext[lnum])) > 0:
                    wh = self._words_handler
                    line_text = ''.join(self._laid_out_plaintext[lnum])
                    if lnum < len(self._test_text_lines):
                        test_text_line = self._test_text_lines[lnum]
                    else:
                        test_text_line = []

                    lt_len = len(line_text)
                    for i in range(lt_len):
                        # spaces in incorrect position are represented with # character
                        is_correct = wh.is_correct_at(lnum, i)
                        swin.addch(lnum, i, self.__char_or_space_or_hash(line_text[i], not is_correct),
                                   curses.color_pair(gobDict[is_correct]))

                    gray_text = ''.join([test_text_line[i] for i in range(lt_len, self._cols)])
                    if len(gray_text) > 0:
                        addstr_full_rgls_color(self._subwindow, self._colored,
                                               lnum, lt_len, gray_text, self._text_color)
                else:
                    if lnum < len(self._test_text_lines):
                        addstr_full_rgls_color(self._subwindow, self._colored,
                                               lnum, 0, ''.join(self._test_text_lines[lnum]), self._text_color)
            else:
                swin.addstr(lnum, 0, self._laid_out_plaintext[lnum])
            swin.move(y, x)

    def _are_texts_matching(self) -> bool:
        wh = self._words_handler
        return wh.is_registering and wh.is_all_correct()

    def _handle_key(self, key: int) -> tuple[bool, bool, bool]:
        wh = self._words_handler

        if curses.ascii.isascii(key) and curses.ascii.isprint(key):
            swin = self._subwindow
            y, x = swin.getyx()

            char_in_test_text = self._test_text_lines[y][x]
            if char_in_test_text == '':
                ttc = self._ttc_checker
                # if at end of test text line, jump to next line if possible
                doPut = wh.register_character(chr(curses.ascii.ascii(key)), y, x)
                if self._info_window is not None:
                    self._info_window.print_info(self._words_handler.misinputs, self._number_of_test)
                if not doPut:
                    return False, False, False
                ny, nx = ttc.where_to_traverse(y, x, curses.KEY_RIGHT, self._lines, self._cols)
                swin.move(ny, nx)
            else:
                doPut = wh.register_character(chr(curses.ascii.ascii(key)), y, x)
                if not doPut:
                    return False, False, False

        _, redraw, do_leave = super()._handle_key(key)

        if self._info_window is not None:
            self._info_window.print_info(self._words_handler.misinputs, self._number_of_test)

        end = wh.is_registering and wh.is_all_correct()

        return end, redraw, do_leave

    def _handle_backspace(self):

        if self._subwindow is not None:
            swin = self._subwindow
            lo = self._laid_out_plaintext
            ttc = self._ttc_checker
            wh = self._words_handler

            y, x = swin.getyx()

            if y <= len(self._test_text_lines):
                if (y + 1, x + 1) == swin.getmaxyx():
                    if lo[y][x] != self.__EMPTY:
                        dy, dx = y, x
                        wh.unregister_character(dy, dx)
                    elif lo[y][x] == self.__EMPTY and self._cols > 1 and lo[y][x - 1] != self.__EMPTY:
                        dy, dx = y, x - 1
                        wh.unregister_character(dy, dx)
                else:
                    dy, dx = ttc.where_to_traverse(y, x, curses.KEY_LEFT, self._lines, self._cols)
                    wh.unregister_character(dy, dx)

            super()._handle_backspace()

            if self._info_window is not None:
                self._info_window.print_info(self._words_handler.misinputs, self._number_of_test)

