import curses
import platform


class ColorPairs:
    VOID = 1
    WHITE_TEXT = 1
    GRAY_TEXT = 3
    RED_TEXT = 4
    GREEN_TEXT = 5
    BLUE_TEXT = 6


def addstr_full_rgls_color(window, colored, y, x, st, color):
    """

        wrapper for addstr(y, x, st, color_pair(color))


    """
    if colored:
        window.addstr(y, x, st, curses.color_pair(color))
    else:
        window.addstr(y, x, st)


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


def set_window_colors(window):

    if curses.has_colors():
        window.bkgdset(' ', curses.color_pair(ColorPairs.VOID))

    window.refresh()

