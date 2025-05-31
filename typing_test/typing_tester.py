import curses
import curses.ascii
from etc.window_checker import WindowChecker
from etc.colors import addstr_full_rgls_color, ColorPairs as clp
from prompts import Prompt
import random
from typing_test.typing_textpad import TypingTextpad
from typing_test.typing_test_subwindows import TypingTestInformationSubwindow
from typing_test.words_handler import WordsHandlerStringConst as WHSC
from prompts.subwindow_prompts.confirmation_prompt import Confirmation


class TestParametersStringConst:
    WORD_COUNT = "word_count"
    CATEGORY = "category"
    TEST_COUNT = "test_count"


class WordLengthCategory:
    MIXED = 0
    SHORT = 1
    MEDIUM = 2
    LONG = 3

    WORD = "word"
    LENGTH = "length"

    MAX_VAL_NAME = 1000
    MIN_VAL_NAME = 1001

    lengthSet = {

        MIXED: {MIN_VAL_NAME: 0, MAX_VAL_NAME: 20},
        SHORT: {MIN_VAL_NAME: 0, MAX_VAL_NAME: 6},
        MEDIUM: {MIN_VAL_NAME: 7, MAX_VAL_NAME: 11},
        LONG: {MIN_VAL_NAME: 12, MAX_VAL_NAME: 20},

    }

    names = {

        MIXED: "Mixed",
        SHORT: "Short",
        MEDIUM: "Medium",
        LONG: "Long"

    }

    @staticmethod
    def is_in_category(category: int, length: int) -> bool:
        wlc = WordLengthCategory
        lSet = wlc.lengthSet[category]
        max_v = lSet[wlc.MAX_VAL_NAME]
        min_v = lSet[wlc.MIN_VAL_NAME]
        if min_v <= length <= max_v:
            return True
        return False


class TypingTester(Prompt):

    def __init__(self, window, colored, words: list, params: dict, alerter=None):
        self._params = params
        self._words = words
        super().__init__(window, colored, alerter)

    def _test_args(self):
        super()._test_args()
        if self._words is None:
            raise ValueError("Words list is None")
        if len(self._words) < 1:
            raise ValueError("Words list is empty")
        if self._params is None:
            raise ValueError("Params dictionary is None")
        for k in [TestParametersStringConst.TEST_COUNT, TestParametersStringConst.WORD_COUNT, TestParametersStringConst.WORD_COUNT]:
            if k not in self._params.keys():
                raise ValueError(f"Key {k} not in params dict")
            if self._params[k] is None:
                raise ValueError(f"{k} is None")
            if not type(self._params[k]) == int:
                raise ValueError(f"{k} is not int")

    def _generate_texts(self) -> list[str]:
        texts = []
        WLC = WordLengthCategory

        wc = self._params[TestParametersStringConst.WORD_COUNT]
        tc = self._params[TestParametersStringConst.TEST_COUNT]
        category = self._params[TestParametersStringConst.CATEGORY]
        if category == WordLengthCategory.MIXED:
            allowed_words = [w[WLC.WORD] for w in self._words]
        else:
            allowed_words = [w[WLC.WORD] for w in self._words
                             if WordLengthCategory.is_in_category(category, w[WLC.LENGTH])]
        awlen = len(allowed_words)

        for _ in range(tc):
            text = ''

            for __ in range(wc):
                text = text + " " + allowed_words[random.randint(0, awlen - 1)]

            text = text.strip(" ")
            texts.append(text)

        return texts

    def do_the_tests(self) -> list[dict]:

        testData = []
        self._do_leave = False
        texts = self._generate_texts()

        for i in range(self._params[TestParametersStringConst.TEST_COUNT]):

            y, x = self._window.getmaxyx()
            while y < 5 + 1:
                y, x = self._window.getmaxyx()
                self._do_leave = self._window_checker.guard_window_size(6, x)
                if self._do_leave:
                    break
            if self._do_leave:
                break
            ttb = TypingTextpad(
                self._window,
                self._colored,
                y - 5,
                x,
                0,
                0,
                self._window_checker
            )
            ttb.test_text = texts[i]

            y, x = self._window.getmaxyx()
            while y < 5 + 1:
                y, x = self._window.getmaxyx()
                self._do_leave = self._window_checker.guard_window_size(6, x)
                if self._do_leave:
                    break
            if self._do_leave:
                break

            ttb.info_window = TypingTestInformationSubwindow(
                self._window, self._colored, y - 5, 0)
            ttb.number_of_test = i+1

            while True:

                _, redraw, do_leave = ttb.edit()
                if do_leave:
                    ttb.save_position()
                    try:
                        cwin = self._window.derwin(1, x, y - 4, 0)
                        self._do_leave, = Confirmation(cwin, self._colored).prompt_user()
                    except curses.error:
                        self._do_leave = True
                    if self._do_leave:
                        break
                if not redraw and not do_leave:
                    # test is over
                    break
            if self._do_leave:
                break

            testDataSlice = ttb.test_data
            testDataSlice[WHSC.TEST_NUMBER] = i+1
            testData.append(testDataSlice)

        return testData
