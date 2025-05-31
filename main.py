from main_app.app import App
from curses import wrapper


def main(stdscr):
    """ Initialize and run the typing test app"""
    App(stdscr).run()


if __name__ == '__main__':
    wrapper(main)
