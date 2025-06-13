"""! \ref wpm "Wpm", \ref kpm "kpm", total time calculation; preparing typing test data slice for saving.

    Also contains FinalDataStringConst with names of the fields of \ref score_data "score data file".
"""

from typing_test.performing_typing_test.words_handler import WordsHandlerStringConst as WHSC
from typing_test.performing_typing_test.typing_tester import TestParametersStringConst as TTSC, WordLengthCategory as WLC
from datetime import datetime

## Defines identifiers and names of fields of score data and their expected order.
#
# Identifiers of fields are in some cases taken from WordLengthCategory,
# WordsHandlerStringConst and TestParametersStringConst classes.
#
# @note All its members are static.
#
# \sa \ref score_data


class FinalDataStringConst:

    ## Identifier of average word count per minute (also called \ref wpm "wpm")
    AVG_WORDS_PER_MINUTE = "wpm"
    ## Identifier of total keystroke count per test
    KEYSTROKES = WHSC.KEYSTROKES
    ## Identifier of total count of incorrect keystrokes per test
    INCORRECT_KEYSTROKES = WHSC.INCORRECT_KEYSTROKES
    ## Identifier of average keystroke count per minute (also called \ref kpm "kpm")
    AVG_KEYSTROKES_PER_MINUTE = "kpm"
    ## Identifier of ordinal number of test in given typing tests set
    TEST_NUMBER = WHSC.TEST_NUMBER
    ## Identifier of timestamp representing when testing began
    TESTS_BEGAN_ON = "tests_began_on"
    ## Identifier of the word category of tests (WordLengthCategory)
    CATEGORY_OF_TESTS = TTSC.CATEGORY
    ## Identifier of count of words per test
    WORD_COUNT_OF_EACH_TEST = TTSC.WORD_COUNT
    ## Identifier of total count of tests in given set of typing tests
    TEST_COUNT = TTSC.TEST_COUNT
    ## Identifier of total duration time per test
    TOTAL_TIME = "total_time"

    ## Defines order of fields in \ref score_data "score data file"; also used for presentation
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

    ## Defines names to be used in presenting given row of typing test data in detail
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
    ## Defines names to be used for presenting typing tests data in a table
    short_name = {
        AVG_KEYSTROKES_PER_MINUTE: "kpm",
        KEYSTROKES: "keys",
        INCORRECT_KEYSTROKES: "badkeys",
        AVG_WORDS_PER_MINUTE: "wpm",
        TEST_NUMBER: "n.o.t.",
        WORD_COUNT_OF_EACH_TEST: "words",
        TESTS_BEGAN_ON: "began",
        CATEGORY_OF_TESTS: "cat.",
        TOTAL_TIME: "time",
    }

## Calculates data to save to \ref score_data "score data file".
# Data consists of mainly statistics (\ref wpm , \ref kpm) but also total duration time and timestamp in ISO 8601 format
# (due to convenience).

## Calculates statistics and other data based on test data
# (given by typing_test::performing_typing_test::typing_tester::TypingTesterScreen).
#
# Results of calculations are used to save them in the \ref score_data "score data file".


class StatisticsCalculator:

    ## Initializes new instance of this class.
    #
    # This method will throw an exception if test data or test parameters are not provided or are incomplete (i.e. any
    # element does not contain required keys).
    #
    # @param self object pointer
    # @param test_data represents results from a test set; each element has to contain keys from WordsHandlerStringConst
    # @param test_info_data contains test parameters for test set;
    # each element has to contain keys from TestParametersStringConst
    # @param tests_began_on represents timestamp of when testing for test set began; when \c None,
    # assumed to be the present time

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
        ## Contains results of whole test set.
        #
        #  Each dictionary represents a typing test from the set and should contain
        #  time of writing correctly a given word in given test,
        #  keystrokes counts - all keystrokes and invalid keystrokes and ordinal number of the test.
        self._tests = test_data
        if test_info_data is None:
            raise ValueError("Test info data is none")
        if len(test_info_data) == 0:
            raise ValueError("Test info data is empty")
        for x in [TTSC.CATEGORY, TTSC.WORD_COUNT, TTSC.TEST_COUNT]:
            if x not in test_info_data:
                raise ValueError(f"Test info dict lacks {x}")
        ## Contains parameters of whole test set.
        #
        # This dictionary should contain word length category,
        # count of words in each test and count of all tests in test set.
        self._tests_params = test_info_data
        if tests_began_on is None:
            tests_began_on = datetime.utcnow()
        ## Timestamp of when the testing with the test set began.
        #
        # If not provided (\c None) assumed to be the present time (\c datetime.utcnow()).
        self._tests_began_on = tests_began_on

    ## Helper method; calculates total duration time (in seconds), \ref wpm and \ref kpm for each test.
    #
    #  Seconds are rounded to 3 digits after period, \ref wpm and \ref kpm to 2 digits.
    #
    #  @param self object pointer
    #  @param test_slice represent a test from test set
    #  @returns
    #  tuple (duration time in seconds, \ref wpm, \ref kpm).
    def __calculate_seconds_wpm_kpm(self, test_slice: dict) -> tuple[float, float, float]:
        bg = test_slice[WHSC.TEST_BEGINNING_TIME]
        ed = test_slice[WHSC.PROPER_WORDS_OCCURRENCE][-1]
        k = float(test_slice[WHSC.KEYSTROKES])
        w = float(self._tests_params[TTSC.WORD_COUNT])
        seconds = ed - bg
        if seconds <= 0.0:
            seconds = 1.0
        seconds_in_minute = 60.0

        return round(seconds, 3), round(seconds_in_minute * w / seconds, 2), round(seconds_in_minute * k / seconds, 2)

    ## Calculates results and statistics based on given test set (given when instating this object).
    #  @param self object pointer
    #  @returns set of calculated score data for the test set for
    #  use in writing it to the \ref score_data "score data file".
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
