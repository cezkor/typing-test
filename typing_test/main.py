from typing_test.app import App
from curses import wrapper


def main(stdscr):
    """! Initialize and run the typing test app, given a terminal screen.

        @param stdscr curses' screen object
    """
    App(stdscr).run()


def entry_point():
    """! Starting point for the app.

        Provides screen object for the app.
    """
    wrapper(main)


if __name__ == '__main__':
    entry_point()
