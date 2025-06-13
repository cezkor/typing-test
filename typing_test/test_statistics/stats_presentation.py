"""! Contains subscreens for presenting score data (results and statistics)."""

import curses
from typing_test.etc.colors import ColorPairs as clp
from .statistics_calculation import FinalDataStringConst as FDSC
from .data_presentation import PresentationOfData


## Presents scores and statistics in a table.
class TabularStatsSubscreen:

    ## Initializes new instance of this class.
    #
    # This method will throw an exception if window, terminal color support or score data are not provided.
    #
    # @param self object pointer
    # @param master_window window from which a subwindow for this subscreen is derived
    # @param colored terminal text color support
    # @param begin_y height relative to top left corner of master window at which subscreen will be drawn
    # @param begin_x width relative to top left corner of master window at which subscreen will be drawn
    # @param data represents data of preformed tests
    # (as calculated by StatisticsCalculator or read from \ref score_data "score data file")
    # @param show_only (optional) specifies which columns of data should be shown in table

    def __init__(self, master_window, colored, begin_y: int, begin_x: int, data: list[dict],
                 show_only=None):
        ## Contains upper limits for lengths of each score data field representation string
        self.__allow_span = PresentationOfData.maxLengthForPresentation
        ## Holds identifiers of columns from \ref score_data "score data file" which never will be printed
        self.__EXCLUDED = [FDSC.TEST_COUNT]
        ## Holds identifiers of columns from \ref score_data "score data file" which will be printed if show_only
        # is not provided or contains only columns listed in ::__EXCLUDED
        self.__BASE_SHOW = [x for x in FDSC.constsFieldOrderList if x not in self.__EXCLUDED]
        ## Window from which a subwindow for this subscreen is derived
        self._master_window = master_window
        ## Terminal text color support
        self._colored = colored
        ## Height relative to top left corner of master window at which subscreen will be drawn
        self._by = begin_y
        ## Width relative to top left corner of master window at which subscreen will be drawn
        self._bx = begin_x
        ## Represents data of preformed tests
        # (as calculated by StatisticsCalculator or read from \ref score_data "score data file")
        self._data = data
        ## Holds identifiers of columns from \ref score_data "score data file" to be printed in the table
        self._show = show_only

        self._test_args()

        if show_only is None:
            self._show = self.__BASE_SHOW
        else:
            self._show = [x for x in show_only if x not in self.__EXCLUDED]
            if len(self._show) == 0:
                self._show = self.__BASE_SHOW

        y, x = master_window.getmaxyx()
        ## Required width of subwindow
        self._required_len = sum([self.__allow_span[n]+1 for n in self._show]) - 1
        ## Required height of subwindow
        self._required_hgt = 2 + len(data)
        
        if y >= self._required_hgt + begin_y and x >= self._required_len + begin_x:
            self._window = master_window.derwin(self._required_hgt, self._required_len, self._by, self._bx)
        else:
            self._window = None

        ## @var _window
        # Subwindow to which the table is printed

    ## Helper method.
    # Checks if master window, terminal text color support variable and test data were provided.
    # @param self object pointer
    def _test_args(self):
        if self._master_window is None:
            raise ValueError('Argument window is None')
        if self._colored is None:
            raise ValueError('Argument colored is None')
        if self._data is None:
            raise ValueError('Argument data is None')

    ## Helper method for printing horizontal line and column labels according to __allow_span.
    # @param self object pointer

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

    ## Prints the table in subwindow.
    # Before printing, it is checked whether master window can fit subwindow. If it is not possible, nothing is printed.
    # If subwindow object was not created, it is created in this method. Then the table is printed with
    # __print_banner() and _print_data() methods.
    # @param self object pointer

    def print(self):
        if len(self._data) == 0:
            return

        # TO DO? There is probably a better way of handling not being able to fit content (i.e. using a window checker)
        # But that requires access to window checker - which requires refactoring.
        y, x = self._master_window.getmaxyx()
        if y < self._required_hgt + self._by or x < self._required_len + self._bx:
            return
        if self._window is None:
            self._window = self._master_window.derwin(self._required_hgt, self._required_len, self._by, self._bx)

        y, x = self._window.getyx()
        self._window.clear()
        self.__print_banner()

        self._print_data()

        self._window.refresh()
        self._window.move(y, x)

    ## Helper method for printing each row of data according to __allow_span.
    # @param self object pointer
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


## Presents scores and statistics of a test in detail - each row for each field.
class SingleDataSliceStatsSubscreen:

    ## Initializes new instance of this class.
    #
    # This method will throw an exception if window, terminal color support or score data are not provided.
    #
    # @param self object pointer
    # @param master_window window from which a subwindow for this subscreen is derived
    # @param colored terminal text color support
    # @param begin_y height relative to top left corner of master window at which subscreen will be drawn
    # @param begin_x width relative to top left corner of master window at which subscreen will be drawn
    # @param data_slice represents data of a preformed test
    # (as calculated by StatisticsCalculator or read from \ref score_data "score data file")

    def __init__(self, master_window, colored, begin_y: int, begin_x: int, data_slice: dict):
        ## Window from which a subwindow for this subscreen is derived
        self._master_window = master_window
        ## Terminal text color support
        self._colored = colored
        ## Height relative to top left corner of master window at which subscreen will be drawn
        self._by = begin_y
        ## Width relative to top left corner of master window at which subscreen will be drawn
        self._bx = begin_x
        ## Dictionary representing a given test; contains fields represented by keys from FinalDataStringConst
        self._data = data_slice

        self._test_args()

        ## Width for each field name
        self._name_width = max(list(map(len, FDSC.long_names.values())))
        ## Width for each value of field
        self._value_width = max(list(PresentationOfData.maxLengthForPresentation.values()))

        y, x = master_window.getmaxyx()

        ## Required width of subwindow
        self._required_len = 5 + self._name_width + 3 + self._value_width
        ## Required height of subwindow
        self._required_hgt = 1 + len(FDSC.constsFieldOrderList)

        if y >= self._required_hgt + begin_y and x >= self._required_len + begin_x:
            self._window = master_window.derwin(self._required_hgt, self._required_len, self._by, self._bx)
        else:
            self._window = None

    ## Helper method.
    # Checks if master window, terminal text color support variable and test data were provided and if test data slice
    # is not empty and contains all required keys for columns from \ref score_data "score data file"
    # (from FinalDataStringConst).
    # @param self object pointer
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

    ## Prints test data slice.
    # @param self object pointer

    def print(self):
        y, x = self._master_window.getmaxyx()
        if y < self._required_hgt + self._by or x < self._required_len + self._bx:
            return
        if self._window is None:
            self._window = self._master_window.derwin(self._required_hgt, self._required_len, self._by, self._bx)

        y, x = self._window.getyx()
        self._window.clear()

        self._print_data()

        self._window.refresh()
        self._window.move(y, x)

    ## Helper method for printing each field of test data.
    # @param self object pointer

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
                        self._window.addnstr(i, 0, namePart, self._required_len, curses.color_pair(clp.WHITE_TEXT))
                        self._window.addnstr(i, len(namePart), valuePart,
                                             self._required_len, curses.color_pair(clp.BLUE_TEXT))
                    else:
                        self._window.addnstr(i, 0, namePart + valuePart, self._required_len)
                except curses.error:
                    pass
                i += 1
