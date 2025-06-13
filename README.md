# Typing Test

Simple terminal app for typing tests.

### Requirements

Python 3.11 or newer.

`setuptools`(>=61) for installing the app.

On Windows `windows-curses` (>=2.4.1) will be required.

Doxygen, if it is needed to have code documentation.

It is recommended for the terminal displaying the application to support displaying at least **40** lines and **120** columns. Most screens in the app can be displayed with less.

### Installing

You can install this app with pip.

Assuming you cloned this repository into `typing_test`:
```bash
cd typing_test && pip install .
```

App can be run with command `typing_test`.

### Documentation

[User manual](docs/manual.md) (**coming soon**).

Code documentation can be generated with Doxygen (run `doxygen` in repository's directory) in [docs/html](docs/html) directory.