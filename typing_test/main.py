from typing_test.main_app.app import App
from curses import wrapper


def main(stdscr):
    """ Initialize and run the typing test app"""
    App(stdscr).run()


def entry_point():
    wrapper(main)


if __name__ == '__main__':
    entry_point()
