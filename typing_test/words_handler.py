import time


class WordsHandlerStringConst:
    TEST_TEXT = "text"
    TEST_TEXT_LINES = "lines"
    RECALC_ONLY = "recalc"

    PROPER_WORDS_OCCURRENCE = "proper_words_occurence"
    KEYSTROKES = "keystrokes"
    INCORRECT_KEYSTROKES = "incorrect_keystrokes"
    TEST_BEGINNING_TIME = "begin_time"
    TEST_NUMBER = "test_number"


class WordsHandler:

    _HAS_SPACE = -6
    _LACKS_SPACE = -7
    _NEEDS_SPACE = -1
    _NO_WORD = -2
    _NO_CHARACTER = -3
    _GOOD = -4
    _NOT_GOOD = -5

    _TOKEN_WORD = "word"
    _CORRECTNESS = "correctness"
    _POSITIONS = "positions"

    def __init__(self):

        self._ttd: dict = {}
        self._tokenList: list[dict] = []
        # in regards to tokenList
        self._correctTokensIndexes = set()
        self._correctTokensMadeOn = dict()
        self._tokenLookupTable: list[list[int]] = []

        self._is_registering = False
        self._beginning = -1.0
        self._end = -1.0
        self._keystrokes = 0
        self._incorrect_keystrokes = 0

    def _recalc_token_positions(self):
        if WordsHandlerStringConst.TEST_TEXT not in self._ttd.keys():
            raise ValueError("No test text in test text dict")
        if WordsHandlerStringConst.TEST_TEXT_LINES not in self._ttd.keys():
            raise ValueError("No test text lines in test text dict")

        if WordsHandlerStringConst.RECALC_ONLY not in self._ttd.keys() or not self._ttd[WordsHandlerStringConst.RECALC_ONLY]:
            return

        test_text_lines = self._ttd[WordsHandlerStringConst.TEST_TEXT_LINES]
        ttl = test_text_lines

        xx = len(test_text_lines[0])
        yy = len(test_text_lines)
        lookup = self._tokenLookupTable = [[self._NO_WORD] * xx for _ in range(yy)]

        # recalc positions of tokens
        j, i = 0, 0
        word, wordLen = self._tokenList[j][self._TOKEN_WORD], len(self._tokenList[j][self._TOKEN_WORD])
        linesPositionToWordPosition = {}
        wlist_len = len(self._tokenList)
        for iy in range(yy):
            for ix in range(xx):
                # assume seeing a word
                if ttl[iy][ix] == '':
                    # skip line, still look for the word
                    break
                elif ttl[iy][ix] != ' ':
                    if i >= wordLen:
                        raise ValueError("Test text and test text lines mismatch")
                    if ttl[iy][ix] == word[i]:
                        # match character to word by
                        # position to word
                        lookup[iy][ix] = j
                        # word to position
                        linesPositionToWordPosition[(iy, ix)] = i
                        i += 1
                    else:
                        raise ValueError("Test text and test text lines mismatch")
                elif ttl[iy][ix] == ' ':
                    if i < wordLen:
                        raise ValueError("Test text and test text lines mismatch")
                    # end looking for word
                    lookup[iy][ix] = self._NEEDS_SPACE
                    if j == wlist_len:
                        raise ValueError("Test text and test text lines mismatch")
                    else:
                        self._tokenList[j][self._POSITIONS] = linesPositionToWordPosition
                        linesPositionToWordPosition = {}
                        if j < wlist_len:
                            j = j + 1
                            if j <= wlist_len - 1:
                                word, wordLen = \
                                    self._tokenList[j][self._TOKEN_WORD], len(self._tokenList[j][self._TOKEN_WORD])
                            linesPositionToWordPosition = {}
                        i = 0
                else:
                    raise ValueError("Test text and test text lines mismatch")
        if wlist_len - 1 == j:
            self._tokenList[j][self._POSITIONS] = linesPositionToWordPosition

    def _tokenize_test_text(self):

        if WordsHandlerStringConst.TEST_TEXT not in self._ttd.keys():
            raise ValueError("No test text in test text dict")
        if WordsHandlerStringConst.TEST_TEXT_LINES not in self._ttd.keys():
            raise ValueError("No test text lines in test text dict")

        if WordsHandlerStringConst.RECALC_ONLY in self._ttd.keys() and self._ttd[WordsHandlerStringConst.RECALC_ONLY]:
            self._recalc_token_positions()
            return

        test_text: str = self._ttd[WordsHandlerStringConst.TEST_TEXT]
        test_text_lines: list[list[str]] = self._ttd[WordsHandlerStringConst.TEST_TEXT_LINES]
        ttl = test_text_lines

        wordList = test_text.split(" ")
        xx = len(test_text_lines[0])
        yy = len(test_text_lines)
        lookup = self._tokenLookupTable = [[self._NO_WORD] * xx for _ in range(yy)]

        # generate token list
        j, i = 0, 0
        word, wordLen = wordList[j], len(wordList[j])
        linesPositionToWordPosition = {}
        wlist_len = len(wordList)
        for iy in range(yy):
            for ix in range(xx):
                # assume seeing a word
                if ttl[iy][ix] == '':
                    # skip line, still look for the word
                    break
                elif ttl[iy][ix] != ' ':
                    if i >= wordLen:
                        raise ValueError("Test text and test text lines mismatch")
                    if ttl[iy][ix] == word[i]:
                        # match character to word by
                        # position to word
                        lookup[iy][ix] = j
                        # word to position
                        linesPositionToWordPosition[(iy, ix)] = i
                        i += 1
                    else:
                        raise ValueError("Test text and test text lines mismatch")
                elif ttl[iy][ix] == ' ':
                    if i < wordLen:
                        raise ValueError("Test text and test text lines mismatch")
                    # end looking for word
                    lookup[iy][ix] = self._NEEDS_SPACE
                    if j == wlist_len:
                        raise ValueError("Test text and test text lines mismatch")
                    else:
                        self._tokenList.append({
                            self._TOKEN_WORD: word,
                            self._POSITIONS: linesPositionToWordPosition,
                            self._CORRECTNESS: [self._NO_CHARACTER] * len(word)
                        })
                        linesPositionToWordPosition = {}
                        if j < wlist_len:
                            j = j + 1
                            if j <= wlist_len - 1:
                                word, wordLen = wordList[j], len(wordList[j])
                        i = 0
                else:
                    raise ValueError("Test text and test text lines mismatch")
        if j == wlist_len - 1:
            self._tokenList.append({
                self._TOKEN_WORD: word,
                self._POSITIONS: linesPositionToWordPosition,
                self._CORRECTNESS: [self._NO_CHARACTER] * len(word)
            })

    def is_correct_at(self, y: int, x: int):
        i = self._tokenLookupTable[y][x]
        if i == self._NO_WORD:
            return True
        if i in [self._HAS_SPACE, self._NEEDS_SPACE]:
            return True
        if i == self._LACKS_SPACE:
            return False
        token = self._tokenList[i]
        if (y, x) not in token[self._POSITIONS]:
            return False
        pos = token[self._POSITIONS][(y, x)]
        if token[self._CORRECTNESS][pos] != self._NOT_GOOD:
            return True
        return False

    def start_registering(self):
        if len(self._tokenLookupTable) == 0 or len(self._ttd) < 2:
            raise ValueError("Test text dict empty or not set")

        if not self._is_registering:
            self._is_registering = True
            self._beginning = time.monotonic()

    def register_character(self, char: str, y: int, x: int) -> bool:

        time_of_possible_correctness = time.monotonic()
        if not self._is_registering:
            return False
        self._keystrokes += 1

        lookup = self._tokenLookupTable
        tokens = self._tokenList

        if lookup[y][x] == self._NEEDS_SPACE and char == ' ':
            self._keystrokes += 1
            lookup[y][x] = self._HAS_SPACE
            return True
        if lookup[y][x] == self._NO_WORD:
            self._keystrokes += 1
            self._incorrect_keystrokes += 1
            return False
        if lookup[y][x] == self._NEEDS_SPACE and char != ' ':
            lookup[y][x] = self._LACKS_SPACE
            self._keystrokes += 1
            self._incorrect_keystrokes += 1
            return True
        if lookup[y][x] == self._LACKS_SPACE and char != ' ':
            self._keystrokes += 1
            self._incorrect_keystrokes += 1
            return True
        if lookup[y][x] == self._LACKS_SPACE and char == ' ':
            lookup[y][x] = self._HAS_SPACE
            self._keystrokes += 1
            return True

        i = lookup[y][x]

        token = tokens[i]
        correctness = token[self._CORRECTNESS]
        word = token[self._TOKEN_WORD]
        char_position = token[self._POSITIONS][(y, x)]
        if char == word[char_position]:
            correctness[char_position] = self._GOOD
            # because user is able only to backspace or to put a character, checking at the end of a word is enough
            # correctly written words are counted only once
            # that is, there is no penalty in deleting correct word
            if char_position == len(word) - 1 and i not in self._correctTokensIndexes:
                is_correct = True
                for j in range(len(word)):
                    if correctness[j] != self._GOOD:
                        is_correct = False
                        break
                if is_correct:
                    self._correctTokensIndexes.add(i)
                    self._correctTokensMadeOn[i] = time_of_possible_correctness
            self._keystrokes += 1
            return True
        else:
            correctness[char_position] = self._NOT_GOOD
            self._incorrect_keystrokes += 1
            self._keystrokes += 1
            return True

    def unregister_character(self, y: int, x: int):

        if not self._is_registering:
            return

        self._keystrokes += 1

        lookup = self._tokenLookupTable
        tokens = self._tokenList

        if lookup[y][x] in [self._NO_WORD, self._NEEDS_SPACE]:
            return

        if lookup[y][x] in [self._HAS_SPACE, self._LACKS_SPACE]:
            lookup[y][x] = self._NEEDS_SPACE
            return

        i = lookup[y][x]

        token = tokens[i]
        correctness = token[self._CORRECTNESS]
        char_position = token[self._POSITIONS][(y, x)]
        correctness[char_position] = self._NO_CHARACTER

    def is_all_correct(self) -> bool:
        return len(self._correctTokensIndexes) == len(self._tokenList)

    @property
    def test_text_dict(self):
        return self._ttd

    @test_text_dict.setter
    def test_text_dict(self, ttd):
        self._ttd = ttd
        self._tokenize_test_text()

    @property
    def misinputs(self):
        return self._incorrect_keystrokes

    @property
    def is_registering(self):
        return self._is_registering

    @property
    def test_data(self):
        return {
            WordsHandlerStringConst.PROPER_WORDS_OCCURRENCE: sorted(list(self._correctTokensMadeOn.values())),
            WordsHandlerStringConst.KEYSTROKES: self._keystrokes,
            WordsHandlerStringConst.INCORRECT_KEYSTROKES: self._incorrect_keystrokes,
            WordsHandlerStringConst.TEST_BEGINNING_TIME: self._beginning
        }

