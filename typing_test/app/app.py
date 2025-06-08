import curses
import importlib.resources
import os

from typing_test import test_statistics
from typing_test.etc.alert_printing import AlertEmitter
import typing_test.prompts.whole_screen_prompts.start_screen_prompt as ss
import typing_test.prompts.whole_screen_prompts.test_parameters_prompt as tp
import typing_test.prompts.whole_screen_prompts.stats.stats_showing_prompts as stats
from typing_test.etc.colors import colors_init, set_window_colors, ColorPairs as clp
from typing_test.performing_typing_test.typing_tester import TypingTester
from typing_test.performing_typing_test.typing_tester import TestParametersStringConst as TTSC
from typing_test.test_statistics.statistics_calculation import StatisticsCalculator
from datetime import datetime
from typing_test.performing_typing_test.summary import SummaryHandler
from typing_test.performing_typing_test.typing_tester import WordLengthCategory as WLC


class App:

    def __init__(self, stdscr):

        self._leave_early = False

        self._stdscr = stdscr
        colors_init()
        self._colored = curses.has_colors()
        set_window_colors(self._stdscr)

        self._words = []
        try:
            wordsPathObj = importlib.resources.as_file(
                # modified file based on
                # https://github.com/first20hours/google-10000-english/blob/master/google-10000-english-no-swears.txt
                importlib.resources.files("typing_test.etc").joinpath("words.csv")
            )
            with wordsPathObj as wordsPath:
                with wordsPath.open("r", encoding="utf8") as f:
                    for line in f.readlines():
                        try:
                            word, length = tuple(line.split(","))
                            if int(length) == 0 or word == '' or len(word) == 0:
                                raise ValueError
                            if word.find("\'") != -1 or word.find("\"") != -1:
                                raise ValueError
                            wordData = {WLC.WORD: word, WLC.LENGTH: int(length)}
                            self._words.append(wordData)
                        except ValueError:
                            pass
        except OSError:
            if self._colored:
                self._stdscr.addstr(0, 0, "Unable to access words file!", curses.color_pair(clp.RED_TEXT))
            else:
                self._stdscr.addstr(0, 0, "Unable to access words file!")
            self._stdscr.addstr(1, 0, "Press any key to leave...")
            self._stdscr.getkey()
            self._leave_early = True
            return

        self.__alerter = AlertEmitter(self._stdscr, self._colored)

        self._score_file_path = None
        SCORE_FILE_NAME = "typing_scores.csv"
        homeDir = os.path.expanduser("~")
        if not os.path.exists(homeDir):
            self._leave_early = self.__alerter.print_alert("Unable to access home directory!", clp.RED_TEXT)
        else:
            try:
                p = os.path.join(homeDir, SCORE_FILE_NAME)
                test_statistics.file_management.try_to_save_to_file(os.path.join(homeDir, SCORE_FILE_NAME), [])
                self._score_file_path = p
            except OSError:
                p = os.path.join(homeDir, SCORE_FILE_NAME)
                if not os.path.exists(p):
                    try:
                        test_statistics.file_management.try_to_save_to_file(p, [])
                    except OSError:
                        self._leave_early = \
                            self.__alerter.print_alert("Unable to access or open score file!\n" + p, clp.RED_TEXT)
                    except ValueError as v:
                        self._leave_early = self.__alerter.print_alert(str(v), clp.RED_TEXT)
            except ValueError as v:
                self._leave_early = self.__alerter.print_alert(str(v), clp.RED_TEXT)
            finally:
                self._score_file_path = os.path.join(homeDir, SCORE_FILE_NAME)

    def run(self):

        if self._leave_early:
            curses.flushinp()
            curses.nocbreak()
            self._stdscr.keypad(False)
            curses.echo()
            return

        try:
            while True:

                start_screen = ss.StartScreen(self._stdscr, self._colored, self.__alerter)
                choice, = start_screen.prompt_user()
                if start_screen.do_leave:
                    break

                if choice == ss.Choices.LEAVE:
                    break
                elif choice == ss.Choices.THE_TEST:
                    picker = tp.TestParametersPicker(self._stdscr, self._colored, self.__alerter)
                    testCount, wordCount, category = picker.prompt_user()
                    if picker.do_leave:
                        break

                    params_of_each_test = {
                        TTSC.TEST_COUNT: testCount,
                        TTSC.WORD_COUNT: wordCount,
                        TTSC.CATEGORY: category,
                    }
                    test_began_on = datetime.utcnow()
                    tester = TypingTester(
                        self._stdscr,
                        self._colored,
                        self._words,
                        params_of_each_test,
                        alerter=self.__alerter
                    )
                    testData = tester.do_the_tests()
                    if tester.do_leave:
                        break

                    statistics = StatisticsCalculator(testData, params_of_each_test, test_began_on).calculate()

                    summary = SummaryHandler(self._stdscr, self._colored, self._score_file_path, statistics,
                                             alerter=self.__alerter)
                    summary.show()
                    if summary.do_leave:
                        break

                elif choice == ss.Choices.STATISTICS:
                    statsManager = stats.MainStats(self._stdscr, self._colored, self._score_file_path)
                    statsManager.show()
                    if statsManager.do_leave:
                        break

        except KeyboardInterrupt:
            """ If not caught or ignored earlier """
            pass
        finally:
            curses.flushinp()
            curses.nocbreak()
            self._stdscr.keypad(False)
            curses.echo()

