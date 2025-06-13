from typing_test.etc.alert_printing import AlertEmitterScreen
from typing_test.etc.window_checker import WindowCheckerScreen


class Prompt:

    """

    Prompt asks user to make a choice or input a value

    """

    def __init__(self, window, colored, alerter=None):
        self._window = window
        self._colored = colored
        if alerter is None:
            self._alerter = AlertEmitterScreen(window, colored)
        else:
            self._alerter = alerter
        self._test_args()
        self._window_checker = WindowCheckerScreen(window, colored)
        self._do_leave = False

    @property
    def do_leave(self):
        return self._do_leave

    def _test_args(self):
        if self._window is None:
            raise ValueError('Argument window is None')
        if self._colored is None:
            raise ValueError('Argument colored is None')
