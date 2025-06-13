"""! Handling score data (score file, presentation of data, calculation of statistics).

@subsection score_data Score data file
Score data file is a csv file containing information on each typing tests. Its file base name is @c typing_scores.csv
(::file_management.SCORE_BASE_NAME). The file is stored in user's home directory.


The information is stored in rows. Excluding the first row, each row represents a test and
consists of (in the order present in statistics_calculation::FinalDataStringConst.constsFieldOrderList):
- When testing began (UTC timestamp, ISO 8601 format)
- Ordinal number of the test in a given set of tests
- Total number of tests in a given set of tests
- Category of length of words in a test (see WordLengthCategory)
- Count of words in a test
- Total duration time (in seconds) spent on a test
- Total count of keystrokes in a test
- Count of invalid keystrokes in a test
- \anchor wpm Average word count per minute (@e wpm for short) for a test
- \anchor kpm Average keystroke count per minute (@e kpm for short) for a test.


Total time, kpm and wpm are to be calculated. Wpm and kpm are considered statistics hence the name of
::statistics_calculation module in which all three are calculated.

Its first row contains header with name of each field but
the first column is preceded by value @c ### (::file_management.__BEG_OF_HEADER) representing a
\anchor decoy_col @e decoy @e column.
Each next row is preceded by value @c # (::file_management.__BEG_FILL) as to fill the decoy column. The decoy column
exists to distinguish the file as score file. Order of the other fields is based on
 statistics_calculation::FinalDataStringConst.constsFieldOrderList.
"""

