from typing import Tuple

from typing_test.etc import RawKeyCodes
from typing_test.prompts import Prompt
from typing_test.text_handlers.oneline_textfield import OnelineTextFieldSubwindow

import curses
import curses.ascii
from typing_test.etc.colors import ColorPairs as clp, addstr_full_rgls_color
from typing_test.performing_typing_test.typing_tester import WordLengthCategory as wlc

from typing_test.performing_typing_test.typing_tester import WordLengthCategory
from typing_test.performing_typing_test.etc import TestParametersBounds as Bounds


class TestParametersPicker(Prompt):

    def __init__(self, window, colored, alerter=None):
        super().__init__(window, colored, alerter)
        self._window_checker.min_y = 10 - 1
        self._window_checker.min_x = 80 - 1
        self._do_leave = self._window_checker.guard_window_size()

    def prompt_user(self) -> Tuple:

        if self._do_leave:
            return None, None, None

        wordsCount = Bounds.defaults[Bounds.WORD_COUNT]
        testCount = Bounds.defaults[Bounds.TEST_COUNT]
        category = WordLengthCategory.MIXED
        boundsSet = Bounds.boundsSet
        maxWC, minWC = \
            boundsSet[Bounds.WORD_COUNT][Bounds.MAX_VAL_NAME], boundsSet[Bounds.WORD_COUNT][Bounds.MIN_VAL_NAME]
        maxTC, minTC = \
            boundsSet[Bounds.TEST_COUNT][Bounds.MAX_VAL_NAME], boundsSet[Bounds.TEST_COUNT][Bounds.MIN_VAL_NAME]

        window = self._window
        wc = self._window_checker

        subtext1 = f"Number of tests in a row ({Bounds.defaults[Bounds.TEST_COUNT]}) <{minTC} - {maxTC}> : "
        subtext1_done = subtext1 + f"{testCount}"
        subtext2 = f"Number of words per test ({Bounds.defaults[Bounds.WORD_COUNT]}) <{minWC} - {maxWC}> : "
        subtext2_done = subtext2 + f"{wordsCount}"
        subtext3 = "Choose word length category (Mixed)"
        subtext4 = f"Mixed [1]"\
                   f" Short <{wlc.lengthSet[wlc.SHORT][wlc.MIN_VAL_NAME]},"\
                   f" {wlc.lengthSet[wlc.SHORT][wlc.MAX_VAL_NAME]}> [2]" \
                   f" Medium <{wlc.lengthSet[wlc.MEDIUM][wlc.MIN_VAL_NAME]}," \
                   f" {wlc.lengthSet[wlc.MEDIUM][wlc.MAX_VAL_NAME]}> [3]" \
                   f" Long <{wlc.lengthSet[wlc.LONG][wlc.MIN_VAL_NAME]}," \
                   f" {wlc.lengthSet[wlc.LONG][wlc.MAX_VAL_NAME]}> [4]"
        new_banner1 = "Press 1, 2, 3 or 4 to pick a value, Enter to pick default, Ctrl + C to leave"

        while True:

            curses.curs_set(1)
            curses.echo()
            curses.raw()

            window.clear()
            self.__print_banner()
            window.refresh()

            # test count

            addstr_full_rgls_color(window, self._colored, 3, 0, subtext1, clp.WHITE_TEXT)
            window.refresh()
            result, redraw, do_leave = OnelineTextFieldSubwindow(
                window,
                self._colored,
                2,
                3,
                len(subtext1),
                wc
            ).probe_for_text()
            if do_leave:
                self._do_leave = do_leave
                break
            if redraw:
                continue
            try:
                if len(result.strip()) == 0:
                    pass
                else:
                    testCount = int(result)
                    if testCount < minTC or testCount > maxTC:
                        raise ValueError
            except ValueError:
                self._do_leave = self._alerter.print_alert("Invalid number of test")
                if self._do_leave:
                    break
                continue

            redraw = True
            while redraw:
                # word count
                addstr_full_rgls_color(window, self._colored, 5, 0, subtext2, clp.WHITE_TEXT)
                window.refresh()
                window.move(5, len(subtext2))
                result, redraw, do_leave = OnelineTextFieldSubwindow(
                    window,
                    self._colored,
                    3,
                    5,
                    len(subtext2),
                    wc
                ).probe_for_text()
                if do_leave:
                    self._do_leave = do_leave
                    break
                if redraw:
                    self.__print_banner()
                    addstr_full_rgls_color(window, self._colored, 3, 0, subtext1_done, clp.WHITE_TEXT)
                    continue
                try:
                    if len(result.strip()) == 0:
                        pass
                    else:
                        wordsCount = int(result)
                        if wordsCount < minWC or wordsCount > maxWC:
                            raise ValueError
                except ValueError:
                    self._do_leave = self._alerter.print_alert("Invalid number of words")
                    if self._do_leave:
                        break
                    redraw = True
                    continue

            if self._do_leave:
                break

            # length category
            curses.curs_set(0)
            curses.noecho()
            addstr_full_rgls_color(self._window, self._colored, 10, 0, new_banner1,
                                   clp.WHITE_TEXT)
            addstr_full_rgls_color(self._window, self._colored, 7, 0, subtext3,
                                   clp.WHITE_TEXT)
            addstr_full_rgls_color(self._window, self._colored, 8, 0, subtext4,
                                   clp.WHITE_TEXT)
            window.refresh()

            while True:
                c = window.getch()
                if c == RawKeyCodes.CTRL_C:
                    self._do_leave = True
                    break
                elif c in [ord('4'), ord('1'), ord('2'), ord('3')]:
                    category = int(chr(curses.ascii.ascii(c))) - 1
                    break
                elif c in [curses.KEY_ENTER, curses.ascii.NL, RawKeyCodes.ASCII_ENTER]:
                    break
                elif c == curses.KEY_RESIZE:
                    self._do_leave = wc.guard_window_size()
                    if self._do_leave:
                        break
                    self.__print_banner()
                    curses.curs_set(0)
                    addstr_full_rgls_color(window, self._colored, 3, 0, subtext1_done, clp.WHITE_TEXT)
                    addstr_full_rgls_color(window, self._colored, 5, 0, subtext2_done, clp.WHITE_TEXT)
                    addstr_full_rgls_color(self._window, self._colored, 10, 0, new_banner1,
                                           clp.WHITE_TEXT)
                    addstr_full_rgls_color(self._window, self._colored, 7, 0, subtext3,
                                           clp.WHITE_TEXT)
                    addstr_full_rgls_color(self._window, self._colored, 8, 0, subtext4,
                                           clp.WHITE_TEXT)
                    window.refresh()

            break

        return testCount, wordsCount, category

    def __print_banner(self):
        addstr_full_rgls_color(self._window, self._colored, 0, 0, "Typing Test - Test Parameters",
                               clp.WHITE_TEXT)
        addstr_full_rgls_color(self._window, self._colored, 10, 0, "Press Enter to confirm value, Ctrl + C to leave",
                               clp.WHITE_TEXT)

