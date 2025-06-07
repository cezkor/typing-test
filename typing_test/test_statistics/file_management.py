import os
import csv
import shutil
import random

from .statistics_calculation import FinalDataStringConst as FDSC
from .data_presentation import PresentationOfData as PoD

__BEG_OF_HEADER = "###"
__BEG_FILL = "#"


def _type_give(name: str):
    if name == FDSC.TESTS_BEGAN_ON or name == FDSC.CATEGORY_OF_TESTS:
        return str
    if name in [FDSC.AVG_WORDS_PER_MINUTE, FDSC.AVG_KEYSTROKES_PER_MINUTE, FDSC.TOTAL_TIME]:
        return float
    return int


class ExpectedDataTypes:
    varnameToType = {name: _type_give(name) for name in FDSC.constsFieldOrderList}


def try_to_move_broken_file_if_broken(score_file_path):

    with open(score_file_path, "r", encoding="utf-8", newline='') as f:
        rd = csv.DictReader(f, [__BEG_OF_HEADER] + FDSC.constsFieldOrderList, dialect='unix', restkey="NO_ZONE")
        broken = False
        was_a_row = False
        for row in rd.reader:
            was_a_row = True
            if row[0] == __BEG_OF_HEADER:
                break
            else:
                broken = True
        for row in rd:
            if row[__BEG_OF_HEADER] == __BEG_OF_HEADER:
                continue
            try:
                for n in FDSC.constsFieldOrderList:
                    strval = row[n]
                    typedval = ExpectedDataTypes.varnameToType[n](strval)
                    trueval = PoD.presented[n][PoD.MODIFIER](typedval)
            except (TypeError, ValueError) as e:
                broken = True
                break
        if not was_a_row:
            broken = True
    if not broken:
        return

    homePath = os.path.expanduser("~")
    movedFilePath = os.path.join(homePath, f"{random.randint(1, 10 ** 5)}.oldcsv")
    shutil.move(score_file_path, movedFilePath)
    try_to_save_to_file(score_file_path, [])
    raise ValueError("Score file was corrupted; file was moved to " + movedFilePath)


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

    with open(score_file_path, mode, encoding="utf-8", newline='') as f:
        wrt = csv.DictWriter(f, [__BEG_OF_HEADER] + FDSC.constsFieldOrderList, dialect='unix', restval=__BEG_FILL)
        if not file_existed:
            wrt.writeheader()
        wrt.writerows(final_test_data)

    if text is not None:
        raise ValueError(text)


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
