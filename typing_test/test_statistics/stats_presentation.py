import curses
from typing_test.etc.colors import ColorPairs as clp
from .statistics_calculation import FinalDataStringConst as FDSC
from .data_presentation import PresentationOfData


class TabularStatsSubwindow:

    def __init__(self, window, colored, begin_y: int, begin_x: int, data: list[dict],
                 show_only=None):
        self.__allow_span = PresentationOfData.maxLengthForPresentation
        self.__EXCLUDED = [FDSC.TEST_COUNT]
        self.__BASE_SHOW = [x for x in FDSC.constsFieldOrderList if x not in self.__EXCLUDED]
        self._master_window = window
        self._colored = colored
        self._by = begin_y
        self._bx = begin_x
        self._data = data
        self._show = show_only

        self._test_args()

        if show_only is None:
            self._show = self.__BASE_SHOW
        else:
            self._show = [x for x in show_only if x not in self.__EXCLUDED]
            if len(self._show) == 0:
                self._show = self.__BASE_SHOW

        y, x = window.getmaxyx()
        self._required_len = sum([self.__allow_span[n]+1 for n in self._show]) - 1
        self._required_hgt = 2 + len(data)
        
        if y >= self._required_hgt + begin_y and x >= self._required_len + begin_x:
            self._window = window.derwin(self._required_hgt, self._required_len, self._by, self._bx)
        else:
            self._window = None

    def _test_args(self):
        if self._master_window is None:
            raise ValueError('Argument window is None')
        if self._colored is None:
            raise ValueError('Argument colored is None')
        if self._data is None:
            raise ValueError('Argument data is None')

    def __print_banner(self):

        header = ''
        for hn in self._show:
            header = header + FDSC.short_name[hn].rjust(self.__allow_span[hn]) + " "

        try:
            if self._colored:
                self._window.hline(1, 0, curses.ACS_HLINE, self._required_len, curses.color_pair(clp.WHITE_TEXT))
                self._window.addnstr(0, 0, header, self._required_len, curses.color_pair(clp.BLUE_TEXT))
            else:
                self._window.hline(1, 0, curses.ACS_HLINE, self._required_len)
                self._window.addnstr(0, 0, header, self._required_len)
        except curses.error:
            pass

    def print(self):
        if len(self._data) == 0:
            return

        y, x = self._master_window.getmaxyx()
        if y < self._required_hgt + self._by or x < self._required_len + self._bx:
            return
        if self._window is None:
            self._window = self._master_window\
                .derwin(self._required_hgt, self._required_len, self._by, self._bx)

        y, x = self._master_window.getyx()
        self._window.clear()
        self.__print_banner()

        self._print_data()

        self._window.refresh()
        self._master_window.move(y, x)

    def _print_data(self):
        if self._window is not None:
            i = 0
            PoD = PresentationOfData
            AS_IS = PoD.AS_IS
            PRESENT = PoD.PRESENT
            MODIFIER = PoD.MODIFIER
            for data_slice in self._data:
                text = ''
                for n in self._show:
                    if PoD.presented[n][PRESENT] != AS_IS and callable(PoD.presented[n][MODIFIER]):
                        str_to_add = PoD.presented[n][MODIFIER](data_slice[n])
                    else:
                        str_to_add = str(data_slice[n])
                    if len(str_to_add) > self.__allow_span[n]:
                        str_to_add = "toolong"

                    justify_by = self.__allow_span[n]
                    text = text + str(str_to_add).rjust(justify_by) + " "
                try:
                    if self._colored:
                        self._window.addnstr(2+i, 0, text, self._required_len, curses.color_pair(clp.WHITE_TEXT))
                    else:
                        self._window.addnstr(2+i, 0, text, self._required_len)
                except curses.error:
                    pass
                i += 1


class SingleDataSliceStatsSubwindow:

    def __init__(self, window, colored, begin_y: int, begin_x: int, data_slice: dict):
        self._master_window = window
        self._colored = colored
        self._by = begin_y
        self._bx = begin_x
        self._data = data_slice

        self._test_args()

        self._name_width = max(list(map(len, FDSC.long_names.values())))
        self._value_width = max(list(PresentationOfData.maxLengthForPresentation.values()))

        y, x = window.getmaxyx()

        self.__required_len = 5 + self._name_width + 3 + self._value_width
        self._required_hgt = 1 + len(FDSC.constsFieldOrderList)

        if y >= self._required_hgt + begin_y and x >= self.__required_len + begin_x:
            self._window = window.derwin(self._required_hgt, self.__required_len, self._by, self._by)
        else:
            self._window = None

    def _test_args(self):
        if self._master_window is None:
            raise ValueError('Argument window is None')
        if self._colored is None:
            raise ValueError('Argument colored is None')
        if self._data is None:
            raise ValueError('Argument data is None')
        if len(self._data) == 0:
            raise ValueError('Data is empty')
        for k in FDSC.constsFieldOrderList:
            if k not in self._data.keys():
                raise ValueError(f"Data dict lacks {k}")

    def print(self):
        y, x = self._master_window.getmaxyx()
        if y < self._required_hgt or x < self.__required_len:
            return
        if self._window is None:
            self._window = self._master_window \
                .derwin(self._required_hgt, self.__required_len, self._by, self._by)

        y, x = self._master_window.getyx()
        self._window.clear()

        self._print_data()

        self._window.refresh()
        self._master_window.move(y, x)

    def _print_data(self):
        if self._window is not None:
            i = 0
            PoD = PresentationOfData
            AS_IS = PoD.AS_IS
            PRESENT = PoD.PRESENT
            MODIFIER = PoD.MODIFIER
            for n in FDSC.constsFieldOrderList:
                namePart = FDSC.long_names[n].ljust(self._name_width) + " : "
                if PoD.presented[n][PRESENT] != AS_IS and callable(PoD.presented[n][MODIFIER]):
                    valuePart = PoD.presented[n][MODIFIER](self._data[n])
                else:
                    valuePart = str(self._data[n])
                try:
                    if self._colored:
                        self._window.addnstr(i, 0, namePart, self.__required_len, curses.color_pair(clp.WHITE_TEXT))
                        self._window.addnstr(i, len(namePart), valuePart,
                                             self.__required_len, curses.color_pair(clp.BLUE_TEXT))
                    else:
                        self._window.addnstr(i, 0, namePart + valuePart, self.__required_len)
                except curses.error:
                    pass
                i += 1
