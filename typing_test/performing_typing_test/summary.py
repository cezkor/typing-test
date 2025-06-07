import curses
import curses.ascii
from typing_test.etc.colors import ColorPairs as clp, addstr_full_rgls_color
from typing_test.prompts import Prompt
from typing_test.test_statistics.statistics_calculation import FinalDataStringConst as FDSC
from typing_test.prompts.subwindow_prompts.confirmation_prompt import Confirmation
from typing_test.test_statistics.file_management import try_to_save_to_file
from typing_test.test_statistics.stats_presentation import TabularStatsSubwindow


class SummaryHandler(Prompt):

    def __init__(self, window, colored, score_file_path, test_data: list[dict], alerter=None):
        self._test_data = test_data
        self._score_file_path = score_file_path
        super().__init__(window, colored, alerter)

    def _test_args(self):
        super()._test_args()
        if self._test_data is None:
            raise ValueError("Test data is none")
        if len(self._test_data) == 0:
            raise ValueError("Test data is empty")
        for d in self._test_data:
            for x in FDSC.constsFieldOrderList:
                if x not in d.keys():
                    raise ValueError(f"Test dict lacks {x}")

    def _try_saving(self) -> bool:
        try:
            try_to_save_to_file(score_file_path=self._score_file_path, final_test_data=self._test_data)
        except OSError:
            return self._alerter.print_alert("Unable to access or open score file!", clp.RED_TEXT)
        except (ValueError,  TypeError) as v:
            return self._alerter.print_alert(str(v), clp.RED_TEXT)

    def __print_banner(self):

        window = self._window
        try:
            addstr_full_rgls_color(window, self._colored, 0, 3, "Summary", clp.WHITE_TEXT)
        except curses.error:
            pass
        window.refresh()

    def show(self):
        show_only = [FDSC.TEST_NUMBER, FDSC.TOTAL_TIME, FDSC.CATEGORY_OF_TESTS, FDSC.WORD_COUNT_OF_EACH_TEST,
                     FDSC.AVG_WORDS_PER_MINUTE, FDSC.KEYSTROKES, FDSC.INCORRECT_KEYSTROKES]

        while True:
            self._window.clear()
            y, x = self._window.getmaxyx()

            do_leave = self._window_checker.guard_window_size(len(self._test_data)+5, x)
            if do_leave:
                break
            curses.curs_set(0)
            self._window.clear()
            self.__print_banner()
            stw = TabularStatsSubwindow(self._window, self._colored, 1, 3+3, self._test_data, show_only)
            stw.print()
            self._window.refresh()
            y, x = self._window.getmaxyx()
            confirmation_subwindow = self._window.subwin(1, x - 4, y - 2, 3)
            while True:
                confirmation_subwindow.clear()
                saving = Confirmation(confirmation_subwindow, self._colored, self._alerter,
                                      yes_key=ord('y'), no_key=ord('n'),
                                      prompt_text="Do you want to save scores and stats then go back to menu? Yes [y] "
                                                  "No""[n]")
                do_save, = saving.prompt_user()
                if saving.do_leave or not do_save:
                    leave_or_not_saving = Confirmation(confirmation_subwindow, self._colored, self._alerter)
                    do_it, = leave_or_not_saving.prompt_user()
                    if do_it and saving.do_leave:
                        do_leave = True
                        break
                    if do_it:
                        break
                else:
                    break

            if do_leave:
                break

            if do_save:
                self._try_saving()
                break
            else:
                break

        self._do_leave = do_leave
