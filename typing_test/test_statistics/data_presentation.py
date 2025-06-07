from datetime import datetime
import time
from typing import Callable
from typing_test.test_statistics.statistics_calculation import FinalDataStringConst as FDSC


def pod_shorten_datetime(datetime_iso_str: str):
    return datetime.fromisoformat(datetime_iso_str).isoformat(timespec="seconds").replace("T", " ")


def pod_total_time(seconds: float): 
    return time.strftime("%M:%S", time.gmtime(seconds))


class PresentationOfData:

    PRESENT = 0
    MODIFIER = 1
    AS_IS = -1
    MODIFY = -2

    presented: dict[dict[int, Callable]] = {
        FDSC.AVG_KEYSTROKES_PER_MINUTE: {PRESENT: AS_IS, MODIFIER: str},
        FDSC.KEYSTROKES: {PRESENT: AS_IS, MODIFIER: str},
        FDSC.INCORRECT_KEYSTROKES: {PRESENT: AS_IS, MODIFIER: str},
        FDSC.AVG_WORDS_PER_MINUTE: {PRESENT: AS_IS, MODIFIER: str},
        FDSC.TEST_NUMBER: {PRESENT: AS_IS, MODIFIER: str},
        FDSC.TEST_COUNT: {PRESENT: AS_IS, MODIFIER: str},
        FDSC.TESTS_BEGAN_ON: {PRESENT: MODIFY, MODIFIER: pod_shorten_datetime},
        FDSC.CATEGORY_OF_TESTS: {PRESENT: AS_IS, MODIFIER: str},
        FDSC.WORD_COUNT_OF_EACH_TEST: {PRESENT: AS_IS, MODIFIER: str},
        FDSC.TOTAL_TIME: {PRESENT: MODIFY, MODIFIER: pod_total_time}
    }

    maxLengthForPresentation: dict[int] = {
        FDSC.AVG_KEYSTROKES_PER_MINUTE: 7,
        FDSC.KEYSTROKES: 8,
        FDSC.INCORRECT_KEYSTROKES: 8,
        FDSC.AVG_WORDS_PER_MINUTE: 7,
        FDSC.TEST_NUMBER: 7,
        FDSC.WORD_COUNT_OF_EACH_TEST: 7,
        FDSC.TESTS_BEGAN_ON: 20,
        FDSC.CATEGORY_OF_TESTS: 7,
        FDSC.TOTAL_TIME: 10,
        FDSC.TEST_COUNT: 7
    }
