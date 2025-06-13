"""! Handling of terminal text colors. """

import curses
import platform

## Contains numbers identifying colors used in terminal.
#
#    @note All its members are static.
#


class ColorPairs:

    ## Represents whitespace
    VOID = 1
    WHITE_TEXT = 1
    GRAY_TEXT = 3
    RED_TEXT = 4
    GREEN_TEXT = 5
    ## Cyan
    BLUE_TEXT = 6


##   Wrapper function for addstr(y, x, st, color_pair(color))/addstr(y, x, st).
#
#    Writes to given window string in given color, if colors are supported.
#    Otherwise, it writes the string in white text.
#
#    @param window Curses' window object
#    @param colored window colored text support boolean
#    @param y line number
#    @param x column number
#    @param st string to be written to window
#    @param color identifier of color pair (number from ColorPairs class)
#
def addstr_full_rgls_color(window, colored, y, x, st, color):
    if colored:
        window.addstr(y, x, st, curses.color_pair(color))
    else:
        window.addstr(y, x, st)


## Sets color pairs of (integer from ColorPairs class, color code in terminal), if the terminal supports colors.
def colors_init():
    curses.start_color()
    curses.use_default_colors()

    if curses.has_colors():
        curses.init_pair(ColorPairs.RED_TEXT, curses.COLOR_RED, -1)
        curses.init_pair(ColorPairs.GREEN_TEXT, curses.COLOR_GREEN, -1)
        curses.init_pair(ColorPairs.BLUE_TEXT, curses.COLOR_CYAN, -1)
        if platform.system() == "Windows":
            curses.init_pair(ColorPairs.GRAY_TEXT, 8, -1)
            curses.init_pair(ColorPairs.VOID, 15, -1)
        elif curses.can_change_color():
            GRAY = 100
            WHITE = 101
            curses.init_color(GRAY, 500, 500, 500)
            curses.init_color(WHITE, 1000, 1000, 1000)
            curses.init_pair(ColorPairs.GRAY_TEXT, GRAY, -1)
            curses.init_pair(ColorPairs.VOID, WHITE, -1)
        else:
            curses.init_pair(ColorPairs.GRAY_TEXT, curses.COLOR_WHITE, -1)
            curses.init_pair(ColorPairs.VOID, curses.COLOR_WHITE, -1)


## Sets foreground and background colors of whitespace (ColorPairs.VOID) for a given window.
#
#    To make the color setting visible, window is also refreshed.
#
#    @param window Curses' window object
#

def set_window_colors(window):
    if curses.has_colors():
        window.bkgdset(' ', curses.color_pair(ColorPairs.VOID))

    window.refresh()
