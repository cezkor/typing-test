import curses

from etc import RawKeyCodes
from etc.colors import addstr_full_rgls_color, ColorPairs as clp
from prompts import Prompt
from test_statistics.file_management import try_to_read_file
from test_statistics.stats_presentation import *
from test_statistics.statistics_calculation import FinalDataStringConst as FDSC
from text_handlers.oneline_textfield import OnelineTextFieldSubwindow
from typing_test.etc import TestParametersBounds


class MainStats(Prompt):
    __MAX_LINES_FOR_DATA = 10

    def __init__(self, window, colored, score_file_path):
        super().__init__(window, colored)
        self._top_10_by_wpm = None
        self._score_file_path = score_file_path
        self._window_checker.min_y = self.__MAX_LINES_FOR_DATA + 11 - 1
        self._window_checker.min_x = 80 - 1
        self._do_leave = self._window_checker.guard_window_size()
        self._data = None

    def show(self):

        if self._data is None:
            try:
                self._data = try_to_read_file(self._score_file_path)
                tmp = sorted(self._data, key=lambda x: x[FDSC.AVG_WORDS_PER_MINUTE], reverse=True)
                self._top_10_by_wpm = []
                for i in range(len(tmp)):
                    if i == 10:
                        break
                    self._top_10_by_wpm.append(tmp[i])
            except OSError:
                self._do_leave = self._alerter.print_alert("Unable to access or open score file!", clp.RED_TEXT)
                return
            except ValueError as v:
                self._do_leave = self._alerter.print_alert(str(v), clp.RED_TEXT)
                return

        if self._do_leave or self._data is None or self._top_10_by_wpm is None:
            return

        window = self._window
        wc = self._window_checker

        curses.raw()
        curses.noecho()
        curses.curs_set(0)
        window.clear()
        window.keypad(True)

        self._do_leave = self._window_checker.guard_window_size()
        if self._do_leave:
            return

        self.__print_banner()

        while True:

            c = window.getch()
            if c == RawKeyCodes.CTRL_C:
                self._do_leave = True
                break
            elif c == ord('s'):
                self._do_leave = self._window_checker.guard_window_size()
                if self._do_leave:
                    return
                ss = ShowScores(self._window, self._colored, self._data)
                ss.traverse()
                self._do_leave = ss.do_leave
                if self._do_leave or ss.go_back_to_menu:
                    break
                window.clear()
                self.__print_banner()
                window.keypad(True)
                curses.curs_set(0)
            elif c == ord('b'):
                self._do_leave = False
                break
            elif c == curses.KEY_RESIZE:
                self._do_leave = wc.guard_window_size()
                if self._do_leave:
                    break
                window.clear()
                self.__print_banner()
                window.keypad(True)
                curses.curs_set(0)

    def __print_banner(self):

        window = self._window
        y, _ = window.getmaxyx()

        addstr_full_rgls_color(window, self._colored, 0, 0, "Typing Test - Scores and Statistics",
                               clp.WHITE_TEXT)
        addstr_full_rgls_color(window, self._colored, 2, 3, "Top 10 in highest words per minute:",
                               clp.BLUE_TEXT)
        TabularStatsSubwindow(self._window, self._colored, 4, 3 + 2, self._top_10_by_wpm,
                              [FDSC.TESTS_BEGAN_ON, FDSC.TOTAL_TIME, FDSC.CATEGORY_OF_TESTS,
                               FDSC.WORD_COUNT_OF_EACH_TEST,
                               FDSC.AVG_WORDS_PER_MINUTE]).print()
        addstr_full_rgls_color(window, self._colored, y - 2, 3, "Press [b] to go back to menu, [s] to show scores,"
                                                                " Ctrl+C to leave", clp.WHITE_TEXT)
        window.refresh()


class ShowScores(Prompt):
    __MAX_LINES_FOR_DATA: int = 10

    def __init__(self, window, colored, stats_data):

        super().__init__(window, colored)

        self._stats_data = stats_data
        self._window_checker.min_x = 80 - 1
        self._window_checker.min_y = self.__MAX_LINES_FOR_DATA + 11 - 1
        self._do_leave = self._window_checker.guard_window_size()
        self._go_back_to_menu = False

        self._pages = []
        pages_num = len(stats_data) // self.__MAX_LINES_FOR_DATA
        if len(stats_data) > pages_num * self.__MAX_LINES_FOR_DATA:
            pages_num += 1
        tmp = self._stats_data
        for i in range(pages_num):
            self._pages.insert(i, tmp[:self.__MAX_LINES_FOR_DATA])
            tmp = tmp[self.__MAX_LINES_FOR_DATA:]
        self._pages_index = 0

    @property
    def go_back_to_menu(self):
        return self._go_back_to_menu

    def _move_pages_index(self, by: int = 0):
        n = len(self._pages)
        if n == 0:
            self._pages_index = 0
            return
        i = self._pages_index + by
        if i < 0:
            self._pages_index = n - 1
        elif i >= n:
            self._pages_index = 0
        else:
            self._pages_index = i

    def traverse(self):

        if self._do_leave:
            return

        window = self._window
        wc = self._window_checker

        curses.raw()
        curses.noecho()

        def print_score(which: int) -> tuple[bool, bool]:
            do_leave = False
            go_back_to_menu = False
            window.clear()
            self._do_leave = self._window_checker.guard_window_size()
            if self._do_leave:
                return True, False
            self.__print_scores_banner(self._pages[self._pages_index], which - 1)
            window.keypad(True)
            curses.curs_set(0)

            while True:
                c = window.getch()
                if c == RawKeyCodes.CTRL_C:
                    do_leave = True
                    break
                elif c == ord('b'):
                    go_back_to_menu = True
                    break
                elif c == ord('s'):
                    break
                elif c == curses.KEY_RESIZE:
                    self._window_checker.guard_window_size()
                    window.clear()
                    self._do_leave = self._window_checker.guard_window_size()
                    if self._do_leave:
                        return False, False
                    self.__print_scores_banner(self._pages[self._pages_index], which)
                    window.keypad(True)
                    curses.curs_set(0)

            return do_leave, go_back_to_menu

        def redraw_main():
            window.clear()
            self.__print_main_banner()
            window.keypad(True)
            curses.curs_set(0)

        redraw_main()

        while True:

            c = window.getch()
            if c == RawKeyCodes.CTRL_C:
                self._do_leave = True
                break
            elif c == ord('1'):
                self._move_pages_index(-1)
                self._do_leave = self._window_checker.guard_window_size()
                if self._do_leave:
                    return
                redraw_main()
            elif c == ord('2'):
                self._move_pages_index(1)
                self._do_leave = self._window_checker.guard_window_size()
                if self._do_leave:
                    return
                redraw_main()
            elif c == ord('3'):
                do_redraw = True
                while do_redraw:
                    self._do_leave = self._window_checker.guard_window_size()
                    if self._do_leave:
                        return
                    y, x = window.getmaxyx()
                    self._window.move(y - 2, 0)
                    self._window.clrtobot()
                    self.__print_main_banner()
                    text = "Give line number: "
                    addstr_full_rgls_color(window, self._colored, y - 3, 3, text.ljust(x-5), clp.WHITE_TEXT)
                    addstr_full_rgls_color(window, self._colored, y - 2, 3, "Press Ctrl+C to leave".ljust(x-5),
                                           clp.WHITE_TEXT)
                    textField = OnelineTextFieldSubwindow(self._window, self._colored,
                                                          begin_x=len(text)+3, begin_y=y-3, window_checker=self._window_checker)
                    window.refresh()
                    while True:
                        result, do_redraw, self._do_leave = textField.probe_for_text()
                        if self._do_leave:
                            break
                        if do_redraw:
                            continue
                        try:
                            result = int(result)
                            if len(self._pages) == 0:
                                return
                            if result < 1 or result > len(self._pages[self._pages_index]):
                                continue
                        except (ValueError,  TypeError) as e:
                            continue
                        break
                    if self._do_leave:
                        break
                    self._do_leave, self._go_back_to_menu = print_score(result)
                    if self._do_leave or self._go_back_to_menu:
                        break
                if self._do_leave or self._go_back_to_menu:
                    break
                redraw_main()
            elif c == ord('b'):
                self._do_leave = False
                self._go_back_to_menu = True
                break
            elif c == curses.KEY_RESIZE:
                self._do_leave = wc.guard_window_size()
                if self._do_leave:
                    break
                redraw_main()

    def __print_main_banner(self):

        window = self._window
        window.clear()
        y, _ = window.getmaxyx()

        addstr_full_rgls_color(window, self._colored, 0, 0, "Typing Test - Scores",
                               clp.WHITE_TEXT)

        addstr_full_rgls_color(window, self._colored, y - 3, 3,
                               "Press [1] to switch to previous page"
                               " [2] to next page, [3] to show details,",
                               clp.WHITE_TEXT)
        addstr_full_rgls_color(window, self._colored, y - 2, 3, "[b] to go back to menu, Ctrl+C to leave",
                               clp.WHITE_TEXT)

        if len(self._pages) == 0:
            window.refresh()
            return

        TabularStatsSubwindow(self._window, self._colored, 2, 6, self._pages[self._pages_index],
                              [FDSC.TESTS_BEGAN_ON, FDSC.TOTAL_TIME, FDSC.CATEGORY_OF_TESTS,
                               FDSC.WORD_COUNT_OF_EACH_TEST,
                               FDSC.AVG_WORDS_PER_MINUTE]).print()

        for i in range(len(self._pages[self._pages_index])):
            addstr_full_rgls_color(window, self._colored, 2 + 2 + i, 0, str(i+1).rjust(3),
                                   clp.BLUE_TEXT)

        window.refresh()

    def __print_scores_banner(self, score_data: list[dict], which: int):

        window = self._window
        window.clear()
        y, x = window.getmaxyx()

        addstr_full_rgls_color(window, self._colored, 0, 0, "Typing Test - Score Data",
                               clp.WHITE_TEXT)
        addstr_full_rgls_color(window, self._colored, y - 3, 3, "Press [b] to go back to menu, [s] to go back to "
                                                                "scores,"
                                                                " Ctrl+C to leave".ljust(x-4)
                                                                , clp.WHITE_TEXT)
        addstr_full_rgls_color(window, self._colored, y-2, 0, "".ljust(x-1),
                               clp.WHITE_TEXT)
        if len(self._pages) == 0:
            return
        SingleDataSliceStatsSubwindow(self._window, self._colored, 2, 3, score_data[which]).print()

        window.refresh()
