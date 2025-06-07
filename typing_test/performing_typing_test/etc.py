

class TestParametersBounds:
    MAX_VAL_NAME = 100
    MIN_VAL_NAME = 200

    TEST_COUNT = "tc"
    WORD_COUNT = "wc"

    boundsSet = {

        TEST_COUNT: {MIN_VAL_NAME: 1, MAX_VAL_NAME: 20},
        WORD_COUNT: {MIN_VAL_NAME: 3, MAX_VAL_NAME: 250}
    }

    defaults = {

        TEST_COUNT: 1,
        WORD_COUNT: 100

    }

