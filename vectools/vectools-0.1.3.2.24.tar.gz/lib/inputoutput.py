import sys
import numpy as np
import argparse
import os
import pandas as pd
import os.path

# Some functions make their totally new output matrices. # This constant gives the column name for row titles.
# So that this will be consistent across all functions.
COLUMN_TITLE_FOR_OUTPUT_MATRICES = "row_title"
"""
Handle printing in color
"""
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'

# Various static variables.
FILE_NOT_FOUND_STR = "Error: File %s does not exist"
NO_STDIN = "Error: This module cannot read from STDIN"
STDIN_INDICATOR = "-"


def error_quit(quit_str, exit_program=True):
    """ Print in red and exit.
    :param quit_str: The string to display on error.
    :param  exit_program: Returns a string instead of exiting if False.
    :return: None or string
    """
    out_str = FAIL + quit_str + ENDC
    if exit_program:
        quit(FAIL + quit_str + ENDC)
    return out_str


def check_file_existence(files, accept_stdin=True):
    """ This program handles graceful exiting when a given input file does not exist or data is passed from STDIN and
    the given input cannot read from STDIN.
    :param files: A string or list of file names
    :param accept_stdin: Set to false when STDIN is not allowed.
    :return: None, will exit the program when
    """
    if type(files) is str:
        if files == STDIN_INDICATOR:
            if not accept_stdin:
                error_quit(NO_STDIN, exit_program=True)
        else:
            if not os.path.isfile(files):
                error_quit(FILE_NOT_FOUND_STR % files, exit_program=True)

    elif type(files) == list:
        for file_name in files:
            if file_name == STDIN_INDICATOR:
                if not accept_stdin:
                    error_quit(NO_STDIN, exit_program=True)
            else:
                if not os.path.isfile(file_name):
                    error_quit(FILE_NOT_FOUND_STR % files, exit_program=True)


def cast_datatype(float_int_or_str):
    """
    :param float_int_or_str:
    :return:
    """
    # Check the highest datatype to cast to
    try:
        float_int_or_str = float(float_int_or_str)
        if float_int_or_str - int(float_int_or_str) == 0:
            float_int_or_str = int(float_int_or_str)
    except ValueError:
        # try:
        float_int_or_str = str(float_int_or_str)
        # except ValueError:
        #    matrix = matrix.astype(object)
    return float_int_or_str


class VectorIO:
    """ Handle vector parsing and output.
    http://stackoverflow.com/questions/17091769/python-pandas-fill-a-dataframe-row-by-row?rq=1
    """
    def __init__(self, only_apply_on="", delimiter=None, comment_character=None,
                 has_col_names=False, has_row_names=False):

        if only_apply_on is None or only_apply_on is False:
            only_apply_on = ""
        self.only_apply_on = only_apply_on
        self.only_apply_on_index_values = []

        # A list of integer indices to include in the only-apply-on vectors.
        # Set after vector is parsed as slicing could include negative numbers.
        # Thus, we need to know the total length to generate the full range.
        self.slice_list = []

        self.column_row_title = None

        self.col_titles = None
        self.sliced_col_titles = []

        self.delimiter = delimiter
        self.comment_character = comment_character
        self.comments = []
        self.height = 0
        self.width = 0

        self.has_col_names = has_col_names
        self.has_row_names = has_row_names

        self._column_have_been_printed = False

        if has_col_names:
            self.col_indexes = 0
        else:
            self.col_indexes = None

        if has_row_names:
            self.row_indexes = 0
        else:
            self.row_indexes = None

    def set_column_titles(self, column_title_list):
        """ Sets column titles.

        :param column_title_list:
        :return:
        """
        # @TODO: Resolve row and column printing differences.
        # @TODO: Think about -ci/-co columns input/output only and -c for both
        self.col_indexes = column_title_list
        # self.col_indexes = column_title_list

    def _cast_matrix(self, np_matrix):
        matrix = np_matrix[:]
        # Check the highest datatype to cast to
        try:
            matrix = matrix.astype(float)
            if np.count_nonzero(matrix - matrix.astype(int)) == 0:
                matrix = matrix.astype(int)
        except ValueError:
            try:
                matrix = matrix.astype(str)
            except ValueError:
                matrix = matrix.astype(object)
        return matrix

    def out(self, data_frame, index_label=None):

        if type(data_frame) is not pd.DataFrame:
            data_frame = pd.DataFrame(data_frame)

        sys.stdout.write(
            data_frame.to_csv(
                sep=self.delimiter,
                index_label=index_label,
                header=self.has_col_names,
                index=self.has_row_names
            )
        )

    def add_column(self, column_title, position=-1):
        """ This function handles adding new columns to
        :param column_title:
        :param new_column:
        :param position:
        :return:
        """

        if position < 0:
            position = len(self.col_titles) + position + 1

        # Update column titles if present.
        if self.has_col_names:
            assert position < len(self.col_titles) + 1
            # Update apply-only-on coordinates if they are greater than the insert value.
            for i in range(len(self.only_apply_on_index_values)):
                if self.only_apply_on_index_values[i] > position:
                    self.only_apply_on_index_values[i] += 1

            if self.sliced_col_titles:
                tmp_list = list(self.sliced_col_titles)
                tmp_list.insert(position, column_title)
                self.sliced_col_titles = np.array(tmp_list)

            tmp_list = list(self.col_titles)
            tmp_list.append(column_title)
            self.col_titles = np.array(tmp_list)
            self.col_indexes = np.array(tmp_list)

    def iterative_out(self, row_title, vector, sliced_col_titles=False, column_titles=None, output_type='sys.stdout'):
        """ Handles output of vectors and column and row titles as they are created.
        :param row_title: The text for the row title.
        :param vector: The vector for the given row.
        :param column_titles: A list of column titles. This is only printed once during the first instance.
        :param output_type: Where to output to.
        :return:
        """
        if output_type != 'sys.stdout':
            output_type = open(output_type, 'w')
        else:
            output_type = sys.stdout

        # Handle column titles output.
        if self.col_indexes is not None and self.has_col_names and not self._column_have_been_printed:

            tmp_col_indexes = self.sliced_col_titles if sliced_col_titles else self.col_indexes

            tmp_col_indexes = list(tmp_col_indexes) if hasattr(tmp_col_indexes, "__iter__") else [tmp_col_indexes]

            assert (tmp_col_indexes is not [] and tmp_col_indexes is not None), "Error: No column titles available."

            if self.has_row_names:
                if self.column_row_title is None:
                    tmp_col_indexes = np.insert(tmp_col_indexes, 0, "_")
                else:
                    tmp_col_indexes = np.array([self.column_row_title] + list(tmp_col_indexes))

            output_type.write(self.delimiter.join(tmp_col_indexes) + '\n')
            self._column_have_been_printed = True

        # Format vector output to string.
        row_string = np.char.mod('%s', vector)
        row_s = self.delimiter.join(row_string)

        # Add row if row titles were passed.
        if (row_title is not None) and (row_title is not False and self.has_row_names):
            row_s = row_title + self.delimiter + row_s

        # Finally, write the vector.
        output_type.write(row_s + "\n")

    def _yield_file_names(self, parse_str_or_list):
        """
        :param parse_str_or_list:
        :return:
        """
        if type(parse_str_or_list) is str:
            parse_str_or_list = [parse_str_or_list]

        for file_name in parse_str_or_list:
            # while len(parse_str_or_list) > 0:
            # file_name = parse_str_or_list.pop(0)

            if not os.path.isfile(file_name) and file_name != STDIN_INDICATOR and "/dev/fd/" not in file_name:
                error_quit("""File "%s" does not exist or is unreadable.""" % (file_name,))

            file_obj = file_name if file_name != STDIN_INDICATOR  else sys.stdin

            yield file_obj

    def add_comment_line(self, comment_line):
        assert len(comment_line) > 0 and comment_line[0] == self.comment_character, comment_line
        self.comments.append(comment_line.strip())

    def __cast_matrix_datatype(self, np_matrix):
        """
        :param np_matrix:
        :return:
        """
        # Check the highest datatype to cast to
        matrix = np_matrix[:]
        try:
            matrix = matrix.astype(float)
            if np.count_nonzero(matrix - matrix.astype(int)) == 0:
                matrix = matrix.astype(int)
        except ValueError:
            try:
                matrix = matrix.astype(str)
            except ValueError:
                matrix = matrix.astype(object)
        return matrix

    def _getsliceorfulllist(self, row_list, keep=True):
        """ If slice_str is None return original list, else return a slice of the list described with slice_str.

        :param slice_str:
        :param row_list:
        :return:
        new_matrix, list_with_indices =_slice_list(matrix, slice_string, keep=True)
        new_matrix, list_with_indices = _slice_list(np.array([row_list]), slice_str, keep=True))

        """
        if self.only_apply_on is not None and self.only_apply_on != "":
            new_matrix, index_list = _slice_list(np.array([row_list]), self.only_apply_on, keep=keep)
            if self.only_apply_on_index_values == []:
                self.only_apply_on_index_values = index_list
            out_list = new_matrix[0]
        else:
            out_list = row_list

        return out_list

    def _row_title_and_vec(self, line):
        """
        :param line:
        :return:
        """
        vector = line.strip("\n").split(self.delimiter)

        if self.has_row_names:
            # Remove the first column from the vector and use it as the title.
            tmp_row_title = vector.pop(0)
        else:
            tmp_row_title = None

        return tmp_row_title, vector

    def yield_vectors(self, parse_str_or_list, keep=True):
        """ Returns output as one large matrix with new files appended to the end of previous files.
        Generate will generate vectors or rows.
        :param parse_str_or_list:
        :return:
        """
        """ This function is intended to handle parsing large files. As such the row title are not saved in the
        main class, unless specifically told to do so by setting save_row_names to True.
        Instead row titles are broadcasted in the Row class.
        save_row_names: Row names will be saved in a list, allowing them to be accessed after the generator finishes.
        keep: If True apply-only-on will return a the described columns if false removes described columns.
        :return:
        """
        for file_name in self._yield_file_names(parse_str_or_list):
            file_obj = open(file_name) if file_name != sys.stdin else sys.stdin
            col_title_flag = True
            for line in file_obj:

                # Comments should appear before any of the data. Always strings, therefore does not need casting.
                if len(line) > 0 and line[0] == self.comment_character:
                    self.add_comment_line(line)

                elif self.has_col_names and col_title_flag:
                    col_title_flag = False
                    if self.col_titles is None:
                        # Next if column titles are present store these.
                        # Always strings, therefore does not need casting.
                        tmp_row_title, split_line = self._row_title_and_vec(line)

                        self.col_titles = split_line
                        self.col_indexes = split_line
                        self.column_row_title = tmp_row_title
                        self.sliced_col_titles = self._getsliceorfulllist(self.col_titles, keep=keep)
                else:
                    tmp_row_title, split_line = self._row_title_and_vec(line)
                    vector = np.array(split_line)
                    sliced_vector = np.array(self._getsliceorfulllist(split_line, keep=keep))
                    yield tmp_row_title, self._cast_matrix(vector), self._cast_matrix(sliced_vector)

    def parse_vectors(self, parse_str_or_list):
        """ Returns output as one large matrix with new files appended to the end of previous files.

        Generate will generate vectors or rows.
        :param generate:
        :return:
        """
        # Returns lists of tables.
        data_frames, sliced_frames = self.parse_matrices(parse_str_or_list)

        # If no slice present data_frames becomes the slice.
        no_sliced_frames = len(sliced_frames) > 0 and sliced_frames[0] is None
        return pd.concat(data_frames), pd.concat(data_frames if no_sliced_frames else sliced_frames)

    def yield_matrices(self, parse_str_or_list, matrix_widths_must_match=True, matrix_heights_must_match=True):

        for file_name in self._yield_file_names(parse_str_or_list):

            df = pd.read_csv(file_name,
                             delimiter=self.delimiter,
                             header=self.col_indexes,
                             index_col=self.row_indexes)

            df_width = 1 if len(df.shape) == 1 else df.shape[1]
            df_height = df.shape[0]

            if self.width is 0 and self.height is 0:
                self.width = df_width
                self.height = df_height
            else:
                if matrix_widths_must_match:
                    assert self.width == df_width, str(self.width)+" != "+str(df_width)
                if matrix_heights_must_match:
                    assert self.height == df_height, str(self.height)+" != "+str(df_height)

            sliced_frame = None
            if self.only_apply_on != "":
                self.slice_list = _create_slice_list(self.only_apply_on, self.width)
                sliced_frame = df.iloc[:, self.slice_list]

            yield df, sliced_frame

    def parse_matrices(self, parse_str_or_list, matrix_widths_must_match=True, matrix_heights_must_match=True):
        """ Returns each file as discrete matrices.
        Generate will generate fully parsed individual matrices.
        :return:
        """

        data_frames, sliced_frames = [], []
        widths_match, heights_match = matrix_widths_must_match, matrix_heights_must_match
        for df, sliced_frame in self.yield_matrices(parse_str_or_list, widths_match, heights_match):
            data_frames.append(df)
            sliced_frames.append(sliced_frame)

        return data_frames, sliced_frames


def _create_slice_list(only_apply_on, width):
    """ This function converts pythonic index descriptions i.e. 1,2:4,-1 into a list of exact integers.

    :param index_str:
    :return:
    """
    number_of_columns = width

    # Check for out-of-bounds integers.
    for test_int in only_apply_on.replace(":", ",").split(","):
        if int(test_int) >= number_of_columns:
            error_quit("Error: slice key (%s) out of bounds." % (test_int,))

    comma_separated_values = only_apply_on.split(",")
    # list_with_indices = list(map(int,comma_separated_values))
    list_with_indices = []
    for el in comma_separated_values:
        index_of_colon = el.find(":")
        last = number_of_columns
        if index_of_colon != -1:  # this means ':' found
            if len(el) == 1:
                list_with_indices.extend(list(range(0, last)))
            else:
                reverse = False
                # if the colon is at the beginning like :3
                if index_of_colon == 0:
                    first = 0
                    last = int(el[1:len(el)])  # + 1
                    if last < 0:
                        last = number_of_columns + last
                # if the colon is at the end of the element like 20:
                elif index_of_colon == (len(el) - 1):
                    first = int(el[:len(el) - 1])
                    last = number_of_columns - 1
                else:
                    first = int(el[:index_of_colon])
                    last = int(el[index_of_colon + 1:])

                if (first < 0) ^ (last < 0):  # one is negative
                    if first < 0:
                        first = number_of_columns + first
                    else:
                        last = number_of_columns + last
                if first > last:
                    first, last = last, first
                    reverse = True
                last += 1
                list_of_range = list(range(first, last))
                if reverse:
                    list_of_range = list_of_range[::-1]
                list_with_indices.extend(list_of_range)
        else:
            list_with_indices.append(int(el))

    return list_with_indices


class Vectors:

    def __init__(self, only_apply_on=None, has_col_names=False, has_row_names=False, col_titles=list, row_titles=list,
                 vectors=None):

        self.only_apply_on = only_apply_on
        self.only_apply_on_index_values = []

        # self.vectors = []
        # self.selected_column_vectors = []
        self.matrix = []
        self.matrix_height = 0
        self.matrix_length = 0
        self.selected_columns_matrix = []
        self.has_col_names = has_col_names
        self.has_row_names = has_row_names
        self.col_titles = col_titles
        self.row_titles = row_titles
        # self.delimiter = delimiter

    def __make_column_selection(self, matrix):
        """
        :return:
        """
        if self.only_apply_on is not None:
            matrix, col_list = _slice_list(matrix, self.only_apply_on, keep=True)
            if self.has_row_names:
                col_list = [x + 1 for x in col_list]
                col_list.insert(0, 0)
            if self.has_col_names:
                self.col_titles = [self.col_titles[i] for i in col_list]

            self.only_apply_on_index_values = col_list

        return matrix

    def __cast_matrix_datatype(self, np_matrix):
        """
        :param np_matrix:
        :return:
        """
        # Check the highest datatype to cast to
        matrix = np_matrix[:]
        try:
            matrix = matrix.astype(float)
            if np.count_nonzero(matrix - matrix.astype(int)) == 0:
                matrix = matrix.astype(int)
        except ValueError:
            try:
                matrix = matrix.astype(str)
            except ValueError:
                matrix = matrix.astype(object)
        return matrix

    def parse(self, parse_str_or_list, delimiter):
        """ If passed a string parse a single file. If passed a list parse all files or stdin in list.
        :return:
        """
        if type(parse_str_or_list) is str:
            parse_str_or_list = [parse_str_or_list]

        for file_name in parse_str_or_list:
            """
            Parse an entire vector file into a numpy array data structure.
            :return:
            """
            matrix = []
            # Decide which value to parse from.
            file_obj = open(file_name) if file_name != 'sys.stdin' else sys.stdin

            if self.has_col_names:
                self.col_titles = file_obj.readline().strip("\n").split(delimiter)

            if self.has_row_names:
                self.row_titles = []

            for line in file_obj:
                line_split = line.strip("\n").split(delimiter)

                if self.has_row_names:
                    self.row_titles.append(line_split.pop(0))

                matrix.append(line_split)

            matrix = np.array(matrix)

            # Matrix length must stay the same but multiple matrices can be combined
            #if self.matrix_length is 0:
            #else:

            self.matrix = self.__cast_matrix_datatype(matrix)
            self.selected_columns_matrix = self.__cast_matrix_datatype(self.__make_column_selection(matrix))

            if file_name != 'sys.stdin':
                file_obj.close()

    def get_matrix(self):
        return self.matrix

    def get_selected_matrix(self):
        """ Return only apply on columns.
        :return:
        """
        return self.selected_columns_matrix

    def get_updated_matrix(self):
        """ Return original matrix with columns.
        :return:
        """
        return self.matrix

    def add_column(self, column_title, column_values, position):
        """ This function handles adding new columns to

        :param column_title:
        :param new_column:
        :param position:
        :return:
        """

        # assert position < len()

        # Update apply-only-on coordinates if they are greater than the insert value.
        for i in range(len(self.only_apply_on_index_values)):
            if self.only_apply_on_index_values[i] > position:
                self.only_apply_on_index_values[i] += 1

        # Update column titles if present.
        if self.has_col_names:
            self.col_titles.insert(position, column_title)

        # Add column to matrix
        self.matrix = np.insert(self.matrix, position, column_values, axis=1)

    def add_row(self, column_title, column_values, position):
        """ This function handles adding new columns to
        :param column_title:
        :param column_values:
        :param position:
        :return:
        """

        assert position < len()

        # Update apply-only-on coordinates if they are greater than the insert value.
        for i in range(len(self.only_apply_on_index_values)):
            if self.only_apply_on_index_values[i] > position:
                self.only_apply_on_index_values[i] += 1

        # Update column titles if present.
        if self.has_col_names:
            self.col_titles.insert(position, column_title)

        # Add column to matrix
        self.matrix = np.insert(self.matrix, position, column_values, axis=1)

    def concatenate(self):
        pass

    def get_initial_vectors(self):
        pass

    def selected_column_vectors(self):
        pass


class ParseVectors:
    """
    This class needs to handle sever situations
    1. Input of text stream
    2. Input of file name

    output
    1. Output fully parsed matrix.
    2. Output a generated matrix.

    This function parses tsv files to a tupel of the containing matrix, col_titles, row_titles
    """

    def __init__(self, file_name="",
                 has_col_names=False,
                 has_row_names=False,
                 col_titles=None,
                 row_titles=None,
                 comment_character=None,
                 delimiter="\t",
                 only_apply_on_columns=None):

        self.file_name = file_name

        self.has_col_names = has_col_names

        self.col_titles = col_titles

        self.has_row_names = has_row_names

        self.row_titles = row_titles

        self.comment_character = comment_character

        self.only_on = only_apply_on_columns
        self.delimiter = delimiter
        self.matrix = None
        self.return_type = float

        self._column_have_been_printed = False

    def getcolumntitles(self):
        """ @TODO: Add code here to parse the columns if matrix has not been parsed yet.
        At the moment this will return none if the matrix has not been parsed yet.
        Also check to see if  has cols or not.
        :return:
        """
        return self.col_titles

    def getrowtitles(self):
        """ @TODO: Add code here to parse the row if matrix has not been parsed yet.
        At the moment this will return none if the matrix has not been parsed yet.
        Also check to see if  has rows or not.
        :return:
        """
        return self.row_titles

    def setrowtitles(self, new_row_titles):
        """ @TODO: Add code here to parse the row if matrix has not been parsed yet.
        At the moment this will return none if the matrix has not been parsed yet.
        Also check to see if  has rows or not.
        :return:
        """
        self.row_titles = new_row_titles

    def setcolumntitles(self, new_column_titles):
        """ A simple set function to set the column titles.
        :param new_column_titles:
        :return:
        """
        # @TODO: Add some assert staments to validate input.
        self.col_titles = new_column_titles

    def __handleinput(self):

        if self.file_name != 'sys.stdin':
            file_obj = open(self.file_name)
        else:
            file_obj = sys.stdin
        return file_obj

    def parse(self):
        """
        Parse an entire vector file into a numpy array data structure.

        :return:
        """
        file_obj = self.__handleinput()
        matrix = []

        if self.has_col_names:
            self.col_titles = file_obj.readline().strip("\n").split(self.delimiter)

        if self.has_row_names:
            self.row_titles = []

        for line in file_obj:
            line_split = line.strip("\n").split(self.delimiter)

            if self.has_row_names:

                self.row_titles.append(line_split.pop(0))

            matrix.append(line_split)

        self.matrix = self._cast_matrix(np.array(matrix))

        if self.file_name != 'sys.stdin':
            file_obj.close()

        return self.matrix  # , self.col_titles, self.row_titles, self.return_type

    def generate(self, save_row_names=False, return_type=None):
        """ This function is intended to handle parsing large files. As such the row title are not saved in the
        main class, unless specifically told to do so by setting save_row_names to True.
        Instead row titles are broadcasted in the Row class.

        save_row_names: Row names will be saved in a list, allowing them to be accessed after the generator finishes.
        :return:
        """
        # For cases when we known we have row columns bu they are not pre-defined.
        if save_row_names and self.row_titles is None:
            self.row_titles = []

        file_obj = self.__handleinput()

        has_not_been_casted = True

        if self.has_col_names:
            self.col_titles = file_obj.readline().strip("\n").split(self.delimiter)
            # self.col_titles = np.array(file_obj.readline().strip("\n").split(self.delimiter))
        # The first row gives us the highest datatype. Int should not be taken, because if the first row
        # contains integer and the second floats, then you truncate important information of the latter.
        # So float should be the highest datatype, then string and then object.
        # But, it is discussable whether casting is necessary. The function generate is for reading
        # line by line. So every function handles rows independent. I will cast to floats if possible, that every row
        # with numbers looks the same. When strings appear, they appear...
        self.return_type = return_type

        for line in file_obj:

            if line[0] is not self.comment_character:

                line_split = line.strip("\n").split(self.delimiter)

                if self.has_row_names:
                    # Remove the first column from the vector and use it as the title.
                    tmp_row_title = line_split.pop(0)

                    # Only save the row name unless specifically told to do so.
                    if save_row_names:
                        self.row_titles.append(tmp_row_title)
                else:
                    tmp_row_title = None

                vector = np.array([line_split])
                vector = self._cast_matrix(vector)[0]

                yield tmp_row_title, vector

        if self.file_name != 'sys.stdin':
            file_obj.close()

    def out(self, ndarray, column_titles=None, row_titles=None, output_type='sys.stdout'):
        """ Handle the standard task out outputting the vector.
        :param ndarray:
        :param column_titles:
        :param row_titles:
        :param output_type:
        :return:
        """
        from collections import Iterable

        if output_type != 'sys.stdout':
            output_type = open(output_type, 'w')
        else:
            output_type = sys.stdout

        # Handle column titles output.
        if column_titles is not None:
            output_type.write(self.delimiter.join(column_titles) + '\n')

        if not isinstance(ndarray, Iterable):
            """ Occasionally input from various functions produces non-iterable data types, e.g. numbers. This
            check will fix those condition be creating a 2d iterable.
            """
            ndarray = [[ndarray]]

        for index, row in enumerate(ndarray):
            row_string = np.char.mod('%s', row)
            row_s = self.delimiter.join(row_string)
            if row_titles is not None:
                output_type.write(str(row_titles[index]) + self.delimiter)
            output_type.write(row_s + "\n")

    def iterative_out(self, row_title, vector, column_titles=None, output_type='sys.stdout'):
        """ Handles output of vectors and column and row titles as they are created.
        :param row_title: The text for the row title.
        :param vector: The vector for the given row.
        :param column_titles: A list of column titles. This is only printed once during the first instance.
        :param output_type: Where to output to.
        :return:
        """
        if output_type != 'sys.stdout':
            output_type = open(output_type, 'w')
        else:
            output_type = sys.stdout

        # Handle column titles output.
        if self.col_titles is not None and self.has_col_names and not self._column_have_been_printed:
            assert self.col_titles is not [], "Error: Set to print column titles, but no column titles exist."

            self.col_titles = [str(x) for x in self.col_titles]

            output_type.write(self.delimiter.join(self.col_titles) + '\n')

            self._column_have_been_printed = True

        # Handle row titles output.
        row_string = np.char.mod('%s', vector)
        row_s = self.delimiter.join(row_string)

        if (row_title is not None) and (row_title is not False and self.has_row_names):
            row_s = row_title + self.delimiter + row_s

        # Finally, write the vector.
        output_type.write(row_s + "\n")

    def _cast_matrix(self, np_matrix):
        matrix = np_matrix[:]

        if self.only_on is not None:
            matrix, col_list = _slice_list(matrix, self.only_on, keep=True)
            if self.has_row_names:
                col_list = [x + 1 for x in col_list]
                col_list.insert(0, 0)
            if self.has_col_names:
                self.col_titles = [self.col_titles[i] for i in col_list]

        # Check the highest datatype to cast to
        try:
            matrix = matrix.astype(float)
            if np.count_nonzero(matrix - matrix.astype(int)) == 0:
                matrix = matrix.astype(int)
        except ValueError:
            try:
                matrix = matrix.astype(str)
            except ValueError:
                matrix = matrix.astype(object)
        return matrix


# This might be a better way to get input.
# http://docs.scipy.org/doc/numpy/user/basics.io.genfromtxt.html#defining-the-input
def vecparse(filename, col_names=False, row_names=False):
    """
    This function parses tsv files to a tupel of the containing matrix, col_titles, row_titles, type_of_matrix
    :param filename: file to be parsed
    :param col_names: if file contains a header. Default: false => None
    :param row_names: if file contains row_titles. Default: false => None
    :return: (matrix, col_titles, row_titles, type_of_matrix)
    """
    if filename != 'sys.stdin':
        file = open(filename)
    else:
        file = sys.stdin
    if col_names:
        col_titles = np.array(file.readline().strip("\n").split('\t'))
    else:
        col_titles = None
    matrix = []
    row_titles = []
    return_type = object
    for line in file:

        line_split = line.strip("\n").split('\t')
        if row_names:
            row_titles.append(line_split.pop(0))
        else:
            row_titles = None

        for tryout in (float, str, object):
            try:
                line_split = list(map(tryout, line_split))
                return_type = tryout
            except ValueError:
                continue
            break

        matrix.append(line_split)

    ndarray = np.array(matrix, dtype=return_type)
    matrix = ndarray
    if filename != 'sys.stdin':
        file.close()
    return matrix, col_titles, row_titles, return_type


def outputvector(ndarray, column_titles=None, row_titles=None, output_type='sys.stdout'):
    """ Handle the standard task out outputting the vector.
    :param ndarray:
    :param column_titles:
    :param row_titles:
    :param output_type:
    :return:
    """
    if output_type != 'sys.stdout':
        output_type = open(output_type, 'w')
    else:
        output_type = sys.stdout
    if column_titles is not None:
        output_type.write("\t".join(column_titles) + '\n')

    for index, row in enumerate(ndarray):
        row_string = np.char.mod('%s', row)
        row_s = "\t".join(row_string)
        if row_titles is not None:
            output_type.write(str(row_titles[index]) + "\t")
        output_type.write(row_s + "\n")


class VectorFormats:
    """This class handles the output format of vectors.

    """
    def __init__(self):
        self.format_choices = ["TSV", "SVMLIGHT", "DICT"]

    def getavailableformats(self):
        return self.format_choices

    def getdefaultformat(self):
        return self.format_choices[0]

    def outputformat(self):
        pass


class ParseFasta:
    # @TODO: How to handle non-standard or illegal chars???

    def __init__(self, input_format="FASTA"):
        """
        """

        self.format_choices = {
            "FASTA": self.fastasequencegenerator,
            "FAVEC": self.fastasvecgenerator
        }
        # Setting this will allow automatic parsing or generating.
        self.input_format = "FASTA"

    def fastasequencegenerator(self, fasta_txt):
        """"This function parses fasta files and generates tuples of fasta id and fasta sequences.
        Where the format of a fasta is  >{Description}\n{Sequence}[\n>{Description}\n{Sequence}]*",
        Generates
        :param fasta_txt:
        :return: (fasta_title, fasta_seq)
        """

        fasta_seq_list = []
        fasta_title = None
        for fasta_line in fasta_txt:
            if fasta_line[0] == ">":
                if fasta_title is not None:
                    yield fasta_title, "".join(fasta_seq_list)
                    fasta_seq_list = []
                fasta_title = fasta_line.strip()
                assert len(fasta_title) > 0
            else:
                fasta_seq_list.append(fasta_line.strip())

        # Return the last sequence.
        yield fasta_title, "".join(fasta_seq_list)

    def fastasvecgenerator(self, fasta_txt, DELIM):
        """A vector with the description as the first column and sequence in the second."
        Generates fasta_title, fasta_seq tuples
        :param fasta_txt:
        :return:
        """

        fasta_seq_list = []
        fasta_title = None
        line_number = 0

        for fasta_vec in fasta_txt:

            line_number += 1
            fasta_vec_list = fasta_vec.strip().split(DELIM)
            assert len(fasta_vec_list) == 2, "Error: Incorrect vector length. Line %s." % line_number
            fasta_title, fasta_seq = fasta_vec_list

            yield fasta_title, fasta_seq

    def getavailableformats(self):
        return list(self.format_choices)

    def getdefaultformat(self):
        return "FASTA"

    def setinputformat(self, input_format):
        assert input_format in self.format_choices
        self.input_format = input_format

    def generatefastaobjects(self, fasta_txt):
        """ Returns a generator that will generate name, seq tuples from a fasta file or fasta vec.
        """
        return self.format_choices[self.input_format](fasta_txt)


def legal_characters(value):
    """ This function is passed as to argparse.add_argument's type variable. It checks for illegal characters and
    if found prints an error message.
    """
    illegal_chars = set(value) - set("-0123456789,:")
    if illegal_chars:
        err_str = 'Illegal character(s) "%s". Only integers, ":", and, "," allowed.' % ", ".join(
            sorted(list(illegal_chars)))
        raise argparse.ArgumentTypeError(error_quit(err_str))
    return value


def _shared_params(parser, enable_column_titles=True, enable_row_titles=True, enable_delimiter=True,
                   only_apply_on=False, random_state=False):
    """ This function stores basic arguments used in almost every other function.

    The default variables offer two types of functionality.

    Passing a:
     False -  silences them
     True - Includes them in the argparse object.
     A string - overrides the default string.

    :param parser: An argparse object.
    :return: Does not return anything. However, does add variables to the argparse object.
    """

    if enable_column_titles:
        # Override the help string if a string is passed instead of a boolean.
        if type(enable_column_titles) == str:
            help_string = enable_column_titles
        else:
            help_string = 'The matrix has column titles.'
        parser.add_argument(
            '-c', "--column-titles",
            action="store_true",
            help=help_string
        )

    if enable_row_titles:
        if type(enable_row_titles) == str:
            help_string = enable_row_titles
        else:
            help_string = 'The matrix has row titles.'
        parser.add_argument(
            '-r', "--row-titles",
            action="store_true",
            help=help_string
        )

    if enable_delimiter:
        if type(enable_delimiter) == str:
            help_string = enable_delimiter
        else:
            help_string = 'The characters used to separate columns. default: <TAB>'
        parser.add_argument(
            '-d', "--delimiter",
            nargs='?',
            default="\t",
            help=help_string
        )

    # We have not found a condition where this not applicable.
    parser.add_argument(
        '--roundto',
        type=int,
        default=5,
        help="Round to n decimal places (when rounding is available)."
    )

    if only_apply_on:
        if type(enable_delimiter) == str:
            help_string = enable_delimiter
        else:
            help_string = "Apply operation on a subset of columns. " + \
                          "Use comma separated integers for single columns or ranges as start:end. " + \
                          "Default: all columns."

        parser.add_argument(
            "--only-apply-on",
            type=legal_characters,
            nargs='?',
            help=help_string
        )

    if random_state:
        parser.add_argument(
            '-rs', '--random-state',
            type=int,
            default=None,
            help=''
        )


def _slice_list(matrix, slice_string, keep=True):
    """

    :param matrix:
    :param slice_string:
    :param keep:
    :return:
    """
    number_of_columns = np.shape(matrix)[1]
    comma_separated_values = slice_string.split(",")

    # list_with_indices = list(map(int,comma_separated_values))
    list_with_indices = []
    for el in comma_separated_values:
        index_of_colon = el.find(":")
        last = number_of_columns
        if index_of_colon != -1:  # this means ':' found
            if len(el) == 1:
                list_with_indices.extend(list(range(0, last)))
            else:
                reverse = False
                # if the colon is at the beginning like :3
                if index_of_colon == 0:
                    first = 0
                    last = int(el[1:len(el)])  # + 1
                    if last < 0:
                        last = number_of_columns + last
                # if the colon is at the end of the element like 20:
                elif index_of_colon == (len(el) - 1):
                    first = int(el[:len(el) - 1])
                    last = number_of_columns - 1
                else:
                    first = int(el[:index_of_colon])
                    last = int(el[index_of_colon + 1:])
                if (first < 0) ^ (last < 0):  # one is negative
                    if first < 0:
                        first = number_of_columns + first
                    else:
                        last = number_of_columns + last
                if first > last:
                    first, last = last, first
                    reverse = True
                last += 1
                list_of_range = list(range(first, last))
                if reverse:
                    list_of_range = list_of_range[::-1]
                list_with_indices.extend(list_of_range)
        else:
            list_with_indices.append(int(el))

        f = lambda x: x % number_of_columns

        list_with_indices = list(map(f, list_with_indices))

    if keep is False:
        ncol_list = list(range(0, number_of_columns))
        col_list = list(set(list_with_indices))
        for x in col_list:
            ncol_list.remove(x)
        list_with_indices = ncol_list[:]

    new_matrix = matrix[:, list_with_indices]
    return new_matrix, list_with_indices
