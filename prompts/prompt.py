from etc.alert_printing import AlertEmitter
from etc.window_checker import WindowChecker


class Prompt:

    """

    Prompt asks user to make a choice or input a value

    """

    def __init__(self, window, colored, alerter=None):
        self._window = window
        self._colored = colored
        if alerter is None:
            self._alerter = AlertEmitter(window, colored)
        else:
            self._alerter = alerter
        self._test_args()
        self._window_checker = WindowChecker(window, colored)
        self._do_leave = False

    @property
    def do_leave(self):
        return self._do_leave

    def _test_args(self):
        if self._window is None:
            raise ValueError('Argument window is None')
        if self._colored is None:
            raise ValueError('Argument colored is None')



