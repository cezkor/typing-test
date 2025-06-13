"""! Presentation of data to show in subscreens of typing_test.test_statistics.stats_presentation."""

from datetime import datetime
import time
from typing import Callable
from typing_test.test_statistics.statistics_calculation import FinalDataStringConst as FDSC

## Converts string of datetime in ISO 8601 format to shortened string representing datetime in local time zone.
# @param datetme_iso_str string of datetime timestamp in ISO 8601 format
# @returns string of datetime timestamp in local time zone with time separated from date only by a whitespace;
# time is represented with hours, minutes and seconds; datetime is represented otherwise in a manner similar to ISO 8601


def pod_shorten_datetime(datetime_iso_str: str):
    return datetime.fromisoformat(datetime_iso_str).isoformat(timespec="seconds").replace("T", " ")


## Converts seconds to string representing minutes and seconds
# @param seconds count of seconds
# @returns string representing minutes and seconds in the form \c minutes:seconds


def pod_total_time(seconds: float): 
    return time.strftime("%M:%S", time.gmtime(seconds))


## Describes how to convert each field in the scores file (using identifiers from FinalDataStringConst) to string
# @note All its members are static.


class PresentationOfData:

    ## Key for ::presented dict; field describing how to present a score data field
    PRESENT = 0
    ## Key for ::presented dict; field describing how to convert (modify) a score data field
    MODIFIER = 1
    ## Score data field should be only converted to string
    AS_IS = -1
    ## Score data field should be modified using modifier (accessed with ::MODIFIER key)
    MODIFY = -2

    ## Describes how to present a score data field and how to modify it before presenting if necessary
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

    ## Defines upper limits for lengths of each score data field representation string
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
