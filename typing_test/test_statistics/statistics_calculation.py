from typing_test.performing_typing_test.words_handler import WordsHandlerStringConst as WHSC
from typing_test.performing_typing_test.typing_tester import TestParametersStringConst as TTSC, WordLengthCategory as WLC
from datetime import datetime


class FinalDataStringConst:

    AVG_WORDS_PER_MINUTE = "wpm"
    KEYSTROKES = WHSC.KEYSTROKES
    INCORRECT_KEYSTROKES = WHSC.INCORRECT_KEYSTROKES
    AVG_KEYSTROKES_PER_MINUTE = "kpm"
    TEST_NUMBER = WHSC.TEST_NUMBER
    TESTS_BEGAN_ON = "tests_began_on"
    CATEGORY_OF_TESTS = TTSC.CATEGORY
    WORD_COUNT_OF_EACH_TEST = TTSC.WORD_COUNT
    TEST_COUNT = TTSC.TEST_COUNT
    TOTAL_TIME = "total_time"

    constsFieldOrderList = [
        TESTS_BEGAN_ON,
        TEST_NUMBER,
        TEST_COUNT,
        CATEGORY_OF_TESTS,
        WORD_COUNT_OF_EACH_TEST,
        TOTAL_TIME,
        KEYSTROKES,
        INCORRECT_KEYSTROKES,
        AVG_WORDS_PER_MINUTE,
        AVG_KEYSTROKES_PER_MINUTE
    ]

    long_names = {
        AVG_KEYSTROKES_PER_MINUTE: "average keystrokes per minute",
        KEYSTROKES: "keystrokes count",
        INCORRECT_KEYSTROKES: "invalid keystrokes",
        AVG_WORDS_PER_MINUTE: "average words count per minute",
        TEST_NUMBER: "number of test",
        TEST_COUNT: "total tests count",
        TESTS_BEGAN_ON: "tests began on",
        CATEGORY_OF_TESTS: "category",
        WORD_COUNT_OF_EACH_TEST: "words per test",
        TOTAL_TIME: "total time (minutes:seconds)"
    }
    short_name = {
        AVG_KEYSTROKES_PER_MINUTE: "kpm",
        KEYSTROKES: "keys",
        INCORRECT_KEYSTROKES: "errors",
        AVG_WORDS_PER_MINUTE: "wpm",
        TEST_NUMBER: "n.o.t.",
        WORD_COUNT_OF_EACH_TEST: "words",
        TESTS_BEGAN_ON: "began",
        CATEGORY_OF_TESTS: "cat.",
        TOTAL_TIME: "time",
        # not used
        TEST_COUNT: "tests"
    }


class StatisticsCalculator:

    def __init__(self, test_data: list[dict], test_info_data: dict, tests_began_on: datetime):

        if test_data is None:
            raise ValueError("Test data is none")
        if len(test_data) == 0:
            raise ValueError("Test data is empty")
        for d in test_data:
            for x in [ WHSC.PROPER_WORDS_OCCURRENCE,
                      WHSC.INCORRECT_KEYSTROKES, WHSC.KEYSTROKES, WHSC.TEST_BEGINNING_TIME, WHSC.TEST_NUMBER]:
                if x not in d.keys():
                    raise ValueError(f"Test dict lacks {x}")
        self._tests = test_data
        if test_info_data is None:
            raise ValueError("Test info data is none")
        if len(test_info_data) == 0:
            raise ValueError("Test info data is empty")
        for x in [TTSC.CATEGORY, TTSC.WORD_COUNT, TTSC.TEST_COUNT]:
            if x not in test_info_data:
                raise ValueError(f"Test info dict lacks {x}")
        self._tests_params = test_info_data
        if tests_began_on is None:
            tests_began_on = datetime.utcnow()
        self._tests_began_on = tests_began_on

    def __calculate_seconds_wpm_kpm(self, test_slice: dict) -> tuple[float,float, float]:
        bg = test_slice[WHSC.TEST_BEGINNING_TIME]
        ed = test_slice[WHSC.PROPER_WORDS_OCCURRENCE][-1]
        k = float(test_slice[WHSC.KEYSTROKES])
        w = float(self._tests_params[TTSC.WORD_COUNT])
        seconds = ed - bg
        minutes = seconds/60.0
        if minutes <= 0.0:
            minutes = 1.0

        return round(seconds, 3), round(w / minutes, 2), round(k / minutes, 2)

    def calculate(self) -> list[dict]:
        finalTestData = []
        fdsc = FinalDataStringConst
        params = self._tests_params

        for test_slice in self._tests:
            wpm_kpm = self.__calculate_seconds_wpm_kpm(test_slice)
            d = {fdsc.TEST_NUMBER: test_slice[WHSC.TEST_NUMBER],
                 fdsc.KEYSTROKES: test_slice[WHSC.KEYSTROKES],
                 fdsc.INCORRECT_KEYSTROKES: test_slice[WHSC.INCORRECT_KEYSTROKES],
                 fdsc.CATEGORY_OF_TESTS: WLC.names[params[TTSC.CATEGORY]],
                 fdsc.WORD_COUNT_OF_EACH_TEST: params[TTSC.WORD_COUNT],
                 fdsc.TEST_COUNT: params[TTSC.TEST_COUNT],
                 fdsc.TESTS_BEGAN_ON: self._tests_began_on.isoformat(),
                 fdsc.AVG_WORDS_PER_MINUTE: wpm_kpm[1],
                 fdsc.AVG_KEYSTROKES_PER_MINUTE: wpm_kpm[2],
                 fdsc.TOTAL_TIME: wpm_kpm[0] }

            finalTestData.append(d)

        return finalTestData
