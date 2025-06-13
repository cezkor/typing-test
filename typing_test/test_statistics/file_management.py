"""! \ref score_data management.

@warning @e Public functions available in this module \b may throw exceptions.
"""

import os
import csv
import shutil
import random

from .statistics_calculation import FinalDataStringConst as FDSC
from .data_presentation import PresentationOfData as PoD

## Starting value of header of the \ref score_data "score data file"; represents \ref decoy_col "decoy column"
__BEG_OF_HEADER = "###"
## Filler value for the \ref decoy_col "decoy column"
__BEG_FILL = "#"

## \ref score_data basename
SCORE_BASE_NAME = "typing_scores.csv"

## Determines the type to which convert a field from \ref score_data "score data file".
#
# Used to generate variable ::ExpectedDataTypes.varnameToType.
#
# @param name string with name of a data field (static constant from FinalDataStringConst)
# @returns expected type class for given data field (string, floating point number or integer; integer in most cases)


def _type_give(name: str):
    if name == FDSC.TESTS_BEGAN_ON or name == FDSC.CATEGORY_OF_TESTS:
        return str
    if name in [FDSC.AVG_WORDS_PER_MINUTE, FDSC.AVG_KEYSTROKES_PER_MINUTE, FDSC.TOTAL_TIME]:
        return float
    return int

## Contains information on what type each data field in \ref score_data "score data file" should be converted to.


class ExpectedDataTypes:

    ## Maps type class to each field's name
    varnameToType = {name: _type_give(name) for name in FDSC.constsFieldOrderList}

## If the \ref score_data "score data file" is broken moves the old file and tries to save to a new file .
#
# File is considered broken if either the file doesn't contain any row or at least one row contains data of
# wrong type in any of its columns. Types are determined with ::ExpectedDataTypes.varnameToType.
#
# File considered broken is moved to a file of name \c <random_integer_from_1_to_10000>.oldcsv in user's home directory.
# The user is informed about the old file's new name.
#
# @param score_file_path string containing path to \ref score_data "score data file"


def try_to_move_broken_file_if_broken(score_file_path):

    broken = False
    with open(score_file_path, "r", encoding="utf-8", newline='') as f:
        rd = csv.DictReader(f, [__BEG_OF_HEADER] + FDSC.constsFieldOrderList, dialect='unix', restkey="NO_ZONE")
        for row in rd.reader:
            if row[0] == __BEG_OF_HEADER:
                break
            else:
                broken = True
        for row in rd:  # each row is a dictionary
            if row[__BEG_OF_HEADER] == __BEG_OF_HEADER:
                continue  # skip header as it does not contain data
            try:
                for n in FDSC.constsFieldOrderList:
                    strval = row[n]
                    typedval = ExpectedDataTypes.varnameToType[n](strval)
                    trueval = PoD.presented[n][PoD.MODIFIER](typedval)
            except (TypeError, ValueError) as e:
                broken = True
                break

    if not broken:
        return

    # move the broken file
    homePath = os.path.expanduser("~")
    movedFilePath = os.path.join(homePath, f"{random.randint(1, 10 ** 5)}.oldcsv")
    shutil.move(score_file_path, movedFilePath)
    # write to a new one
    try_to_save_to_file(score_file_path, [])
    raise ValueError("Score file was corrupted; file was moved to " + movedFilePath)

## Tries to save to a \ref score_data "score data file" given typing tests data slices.
#
# The function does the following:
# 1. Determines if the file exists
# 2. If it exists, checks if the file is broken with try_to_move_broken_file_if_broken(); if it was broken, a new file
# is created
# 3. Tries to write new typing tests data to the file
#
# @param score_file_path string containing path to \ref score_data "score data file"
# @param typing tests data calculated with StatisticsCalculator


def try_to_save_to_file(score_file_path, final_test_data: list[dict]):
    file_existed = os.path.exists(score_file_path)

    if file_existed:
        mode = 'a'
    else:
        mode = 'x'

    text = None
    if file_existed:
        try:
            try_to_move_broken_file_if_broken(score_file_path)
        except ValueError as v:
            text = str(v)

    try:
        with open(score_file_path, mode, encoding="utf-8", newline='') as f:
            wrt = csv.DictWriter(f, [__BEG_OF_HEADER] + FDSC.constsFieldOrderList, dialect='unix', restval=__BEG_FILL)
            if not file_existed:
                wrt.writeheader()
            wrt.writerows(final_test_data)
    except OSError:
        text = f"Error opening/writing to file {score_file_path}"

    if text is not None:
        raise ValueError(text)

## Tries to read \ref score_data "score data file".
#
# Used in subscreens from ::stats_presentation
#
# The function does the following:
# 1. Determines if the file exists; if not creates it (via try_to_save_to_file())
# 2. Checks if the file is broken with try_to_move_broken_file_if_broken(); if it was broken a new file
# is created
# 3. Reads the file per format considered in \ref score_data "score data file"
#
# @param score_file_path string containing path to \ref score_data "score data file"
# @returns list representing each row as dictionary with keys as names from FinalDataStringConst and
# data converted per ExpectedDataTypes


def try_to_read_file(score_file_path) -> list[dict]:
    ret = []

    if not os.path.exists(score_file_path):
        try_to_save_to_file(score_file_path, [])
        return ret

    try_to_move_broken_file_if_broken(score_file_path)

    with open(score_file_path, "r", encoding="utf-8", newline='') as f:
        rd = csv.DictReader(f, [__BEG_OF_HEADER] + FDSC.constsFieldOrderList, dialect='unix', restkey="NO_ZONE")
        for row in rd:
            if row[__BEG_OF_HEADER] == __BEG_OF_HEADER:
                continue
            ret.append({v: ExpectedDataTypes.varnameToType[v](row[v]) for v in FDSC.constsFieldOrderList})
    return ret
