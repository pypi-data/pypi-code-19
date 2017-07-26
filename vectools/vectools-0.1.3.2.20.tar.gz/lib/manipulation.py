from __future__ import print_function
import numpy as np
from lib.inputoutput import ParseVectors, _shared_params, _slice_list, VectorIO, _create_slice_list, legal_characters, error_quit, check_file_existence
from collections import OrderedDict
import pandas as pd

# http://stats.stackexchange.com/questions/65762/how-to-standardize-data-for-hierarchical-clustering
# http://sebastianraschka.com/Articles/2014_pca_step_by_step.html
# See link for a good list of operations.
# http://wiki.scipy.org/NumPy_for_Matlab_Users#head-0c3c49ec7eef424bd3d361e5d8e2955f533750d6


def transpose(parser):
    """ Transposes a matrix.

    Transpose a matrix, if more than one matrix is passed each will be transposed and printed.

    #Examples:

    $ cat matrix.csv
    id,a,b
    c,1,2
    d,3,4

    $ vectools transpose --delimiter , --row-titles --column-titles matrix.csv
    id,c,d
    a,1,3
    b,2,4
    """

    parser.add_argument('matrices',
                        nargs=1,
                        help='Matrices to add to a base matrix.')

    _shared_params(parser, enable_column_titles=True, enable_row_titles=False)

    args = parser.parse_args()

    # Transpose handles row and column swap, therefore, no need to handle rows or columns.
    vp = VectorIO(
        # only_apply_on=only_apply_on, # Disable on this one?
        delimiter=args.delimiter,
        # has_col_names=args.column_titles,
        # has_row_names=args.row_titles
    )

    for matrix_data_frame, _ in vp.yield_matrices(args.matrices[0]):
        # Invert col and row
        # tmp_has_row_names = vp.has_row_names
        # vp.has_row_names = vp.has_col_names
        # vp.has_col_names = tmp_has_row_names
        vp.out(matrix_data_frame.T)


def create_matrix(parser):
    """ Create matrices, either of m rows and n columns filled with values v or special e.g. identity matrices, etc.
    """
    # Numpy array
    # https://docs.scipy.org/doc/numpy/reference/routines.array-creation.html
    # Eye
    # https://docs.scipy.org/doc/numpy/reference/generated/numpy.eye.html#numpy.eye
    """
    Upper triangular matrix / Lower triangular matrix
    Diagonal matrix
    Scalar matrix.
    Identity matrix.
    Transpose of a matrix
    Symmetric matrix
     Inverse of a matrix.
    Commutative and anti-commutative matrices.  said to commute.
    Periodic matrix.   A2 = A, then A is called idempotent.
    Nilpotent matrix.
    """
    matrix_type_choices = ["identity"]

    parser.add_argument('-y', "--height",
                        type=int,
                        required=True,
                        help="The height of the matrix being generated.")

    parser.add_argument('-x', "--width",
                        type=int,
                        required=True,
                        help='The length of the matrix being generated.')

    parser.add_argument('-v', "--value",
                        type=str,
                        required=True,
                        help='The value to populate the matrix with.')

    parser.add_argument('-s', "--special",
                        type=str,
                        choices=matrix_type_choices,
                        default=None,
                        help='Special matrix types, identify etc. Height/width values many be overridden. \
                        Width is given precedence over height. ')

    _shared_params(parser)

    args = parser.parse_args()

    if args.special is None:
        # Make a matrix. Data types should be safe due to type checking by argparse (I think).
        output_matrix = [[args.value for x in range(args.width)] for y in range(args.height)]
        output_matrix = np.array(output_matrix)
    elif args.special == "identity":
        output_matrix = np.identity(args.width)
    else:
        assert False, "Error: Unrecognised matrix type."

    # Output the matrix.
    ParseVectors("", delimiter=args.delimiter).out(output_matrix)


# def makeaddable(parser, ordered_file_names_iter, has_row_ids=False):
#     """Makes sets of vectors comparible by adding columns missing between them.
#     """
#
#     """
#     This function is made to make sets of vectors comparible by adding columns missing
#     from the other.
#     IN:
#     f_obj_iter - an iterable containing file objects.
#     has_row_ids - will turn on/off handleing special rowid rows.
#     OUT:
#     will write vectors to files based on their original names
#     '''
#
#     :param ordered_file_names_iter:
#     :param has_row_ids:
#     :return:
#     """
#
#     delim = "\t"
#     file_obj_list = []
#     title_union = set()
#     for file_name in sorted(ordered_file_names_iter):
#         print(file_name)
#         f_obj = open(file_name)
#         title = f_obj.readline().split()
#         print(title)
#         # Remove the row id if present
#         if has_row_ids:
#             title.pop(0)
#
#         file_obj_list.append([f_obj, title])
#         title_set = set(title)
#         assert len(title_set) == len(title), "ERROR: row ids are not unique."
#         # make a set of all unique title ids
#         title_union.update(title_set)
#
#     new_title = sorted(title_union)
#     print(new_title)
#     # Convert each vector row into a dict.
#     for f_obj, title in file_obj_list:
#
#         out_f_obj = open(f_obj.name + ".colad.vec", "w")
#
#         print(delim.join(new_title), file=out_f_obj)
#
#         for line in f_obj:
#             # I think the titles should have allready been read.
#             # @TODO: Need a varible parsing function here.
#             spln = line.strip().split()
#
#             out_row = []
#             if has_row_ids:
#                 out_row.append(spln.pop(0))
#                 print(out_row)
#
#             title_val_dict = dict(zip(title, spln))
#
#             for el in new_title:
#                 out_val = "0"
#                 if el in title_val_dict:
#                     out_val = title_val_dict[el]
#                     print(el, out_val)
#                 out_row.append(out_val)
#
#             print(delim.join(out_row), file=out_f_obj)


def vec_slice(parser):
    """ Removes columns from a matrix.
    This function is to slice a matrix
    You have to say which columns you want to keep (--keep-cols) or to remove (--remove-cols)
    in a comma separated list like 1,3,7 or 1,4:7,9:

    See function chop if you want to remove rows


    #Examples:

    $ cat matrix.tsv
    id,c,d,e
    a,1,2,3
    b,3,4,5

    $ vectools slice --keep-cols 0,2 --delimiter , --row-titles --column-titles matrix.tsv
    id,c,e
    a,1,3
    b,3,5

    $ vectools slice --remove-cols 1:2 --delimiter , --column-titles matrix.tsv
    id,e
    a,3
    b,5
    """

    parser.add_argument('matrices',
                        nargs='*',
                        # required=True,
                        help='Matrices to add to a base matrix.')

    # nargs='?' One argument will be consumed from the command line if possible, and produced as a single item.
    # If no command-line argument is present, the value from default will be produced.
    parser.add_argument('--keep-cols',
                        type=str,
                        nargs='?',
                        default=None,
                        help="The columns which should be kept. Comma separated")

    parser.add_argument('--remove-cols',
                        type=str,
                        nargs='?',
                        default=None,
                        help="The columns which should be removed. Omitted if --keep-cols is present. Comma separated")

    _shared_params(parser)

    args = parser.parse_args()

    # There is no reason to run operation if not values passed.
    if args.keep_cols is None and args.remove_cols is None:
        raise ValueError("Nothing given for either keep-cols nor remove-cols")

    if args.keep_cols is not None:
        keep = True
        only_apply_on = args.keep_cols
    else:
        keep = False
        only_apply_on = args.remove_cols

    vp = VectorIO(
        only_apply_on=only_apply_on,
        delimiter=args.delimiter,
        has_col_names=args.column_titles,
        has_row_names=args.row_titles
    )

    for row_title, _, only_apply_on_vector in vp.yield_vectors(args.matrices, keep=keep):

        vp.iterative_out(row_title, only_apply_on_vector, sliced_col_titles=True)


def group_by(parser):
    """ Combines rows around key columns and optionally preforms mathematical operations on groups.
    Available operations are AVG, COUNT, MAX, MIN, and SUM.

    :param parser:
    :return:
    """
    # http://stackoverflow.com/questions/164319/is-there-any-difference-between-group-by-and-distinct
    # AVG, COUNT, MAX, MIN, SUM

    _shared_params(
        parser,
        enable_column_titles=True,
        enable_row_titles="The matrix has row titles. If set, the first row id encountered will be used.",
        only_apply_on=True
    )

    parser.add_argument('--reverse',
                        action="store_true",
                        help="Only print rows if they appear more than once.")

    parser.add_argument('infile',
                        nargs='?',
                        type=str,
                        default="sys.stdin")

    args = parser.parse_args()

    vector_parser = ParseVectors(
        file_name=args.infile,
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        col_titles=None,
        row_titles=None,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )

    generator = vector_parser.generate(return_type=str)

    # Hold seen vectors here.
    seen_set = set()

    # To save the first appearance in the reverse case.
    first_appearance_rows = dict()

    for row_title, input_vector in generator:

        only_apply_on_cols = tuple(_getsliceorfulllist(args.only_apply_on, input_vector))

        if args.reverse:
            # Save the first appearance in a dict.
            if only_apply_on_cols not in first_appearance_rows:
                first_appearance_rows[only_apply_on_cols] = (row_title, input_vector)
            # If its already in there get the first appearance.
            else:
                row_title, input_vector = first_appearance_rows[only_apply_on_cols]
                if only_apply_on_cols not in seen_set:
                    vector_parser.iterative_out(
                        row_title=row_title,
                        vector=input_vector,
                        column_titles=vector_parser.getcolumntitles())

                    seen_set.add(only_apply_on_cols)
        else:
            if only_apply_on_cols not in seen_set:
                vector_parser.iterative_out(
                    row_title=row_title,
                    vector=input_vector,
                    column_titles=vector_parser.getcolumntitles())

            seen_set.add(only_apply_on_cols)


def unique(parser):
    """ Returns unique rows in a matrix.

    This function returns unique rows of a matrix.
    If column titles are defined, the first row does not count as row
    If row titles are defined, rows titles, the first row id encountered will be used.


    #Examples:

    $ cat matrix.csv
    1 0 1 0 1
    1 0 1 0 1
    0 1 0 1 0
    0 1 0 1 0
    0 1 0 1 0
    0 1 0 1 0
    2 0 1 0 1
    2 0 1 0 1
    2 0 1 0 1
    0 2 0 1 0
    0 2 0 1 0
    0 2 0 1 0
    0 2 0 1 0
    0 2 0 1 0
    0 2 0 1 0
    0 2 0 1 0
    0 2 0 1 0
    0 2 0 1 0
    0 2 0 1 0
    0 2 0 1 0
    2 0 2 0 1
    2 0 2 0 1

    $ vectools unique matrix.csv
    0 1 0 1 0
    0 2 0 1 0
    1 0 1 0 1
    2 0 1 0 1
    2 0 2 0 1

    $ cat matrix.csv
    id,1,2
    id,1,2
    b,1,2
    id,1,2

    $ vectools unique -d , --row-titles --column-titles matrix.csv
    id,1,2
    id,1,2


    ENSMUSG00000102037 	Bcl2a1a
    ENSMUSG00000102037	A1
    ENSMUSG00000102037	BB218357
    ENSMUSG00000102037	Bcl2a1
    ENSMUSG00000102037	Bcl2a1a
    ENSMUSG00000102037	Bfl-1
    ENSMUSG00000102037	Bfl1
    ENSMUSG00000102037	Hbpa1
    ENSMUSG00000079293 	Clec7a
    ENSMUSG00000079293	beta-glucan receptor
    ENSMUSG00000079293	beta-GR
    ENSMUSG00000079293	Bgr
    ENSMUSG00000079293	Clecsf12
    ENSMUSG00000079293	dectin-1
    ENSMUSG00000079293	Dectin1
    ENSG00000172243	CLEC7A
    ENSG00000172243	BGR
    ENSG00000172243	CANDF4
    ENSG00000172243	CLECSF12
    ENSG00000172243	dectin-1
    ENSG00000172243	DECTIN1
    ENSG00000172243	hDectin-1

    """
    from collections import OrderedDict
    _shared_params(
        parser,
        enable_column_titles=True,
        enable_row_titles="The matrix has row titles. If set, the first row id encountered will be used.",
        only_apply_on=True
    )
    parser.add_argument('--reverse',
                        action="store_true",
                        help="Only print rows if they appear more than once.")
    # Possible new features. Controlling kept rows.
    # parser.add_argument('--min',
    #                     action="store_true",
    #                    help="")
    # parser.add_argument('--max',
    #                     action="store_true",
    #                     help="")
    parser.add_argument('--count',
                        action="store_true",
                        help="Print counts of each unique variable.")
    # @TODO: Allow for different matching algorithms to be used. i.e. case insensitive, google refine clustering algos
    # https://github.com/OpenRefine/OpenRefine/blob/master/main/src/com/google/refine/clustering/binning/FingerprintKeyer.java
    parser.add_argument('--ignore-case',
                        action="store_true",
                        help="Print counts of each unique variable.")
    parser.add_argument('--fingerprint',
                        action="store_true",
                        help="Match using text fingerprint.")
    parser.add_argument('matrices',
                        nargs='*',
                        help='Matrices to subtracts from a base matrix.')

    args = parser.parse_args()

    from lib.textclustering import fingerprint

    vp = VectorIO(
        only_apply_on=args.only_apply_on,
        delimiter=args.delimiter,
        has_col_names=args.column_titles,
        has_row_names=args.row_titles
    )

    # To save the first appearance.
    first_appearance_rows = OrderedDict()

    # Save the first files row titles.
    col_names = None

    for row_title, vector, only_apply_on_vector in vp.yield_vectors(args.matrices):

        if args.ignore_case:
            only_apply_on_vector = tuple(x.lower() for x in only_apply_on_vector)

        if args.fingerprint:
            only_apply_on_vector = tuple(fingerprint(x) for x in only_apply_on_vector)

        # If other modifications not present convert to tuple for hashing in dict.
        if type(only_apply_on_vector) is not tuple:
            only_apply_on_vector = tuple(only_apply_on_vector)

        # If first appearance
        if only_apply_on_vector not in first_appearance_rows:
            first_appearance_rows[only_apply_on_vector] = [row_title, vector, 0]

        first_appearance_rows[only_apply_on_vector][-1] += 1

    # if args.column_titles and not col_names:
    if args.column_titles and args.count:
            vp.add_column("Counts", -1)

    # Output results.
    for element in first_appearance_rows:
        row_title, out_vec, row_counts = None, None, None

        if args.reverse:
            # If reverse set only keep row with a count greater than one.
            if first_appearance_rows[element][-1] > 1:
                row_title, out_vec, row_counts = first_appearance_rows[element]
        else:
            # If reverse is not set keep any row in dict since all are now unique.
            row_title, out_vec, row_counts = first_appearance_rows[element]

        if out_vec is not None:
            if args.count:
                out_vec = np.append(out_vec, [row_counts])
            vp.iterative_out(row_title=row_title, vector=out_vec)


def concatenate(parser):
    """ Concatenates two matrices at a given axis
    @TODO: Does this mean we can get rid of append?
    Concatenate two matrices at a given axis.

    #Examples:

    $ cat matrix.csv
    1 0 1 0 1
    0 1 0 1 0
    2 0 1 0 1
    0 2 0 1 0
    2 0 2 0 1

    $ vectools concatenate matrix.csv matrix.csv  --axis 0
    1 0 1 0 1
    0 1 0 1 0
    2 0 1 0 1
    0 2 0 1 0
    2 0 2 0 1
    1 0 1 0 1
    0 1 0 1 0
    2 0 1 0 1
    0 2 0 1 0
    2 0 2 0 1

    $ vectools concatenate matrix.csv matrix.csv  --axis 1
    1 0 1 0 1 1 0 1 0 1
    0 1 0 1 0 0 1 0 1 0
    2 0 1 0 1 2 0 1 0 1
    0 2 0 1 0 0 2 0 1 0
    2 0 2 0 1 2 0 2 0 1
    :param parser:
    :return:
    """

    # parser.add_argument('matrices',
    #                    metavar='matrices',
    #                    type=str,
    #                    nargs='+',
    #                    help='A set of matrices to concatenate')

    parser.add_argument('matrices',
                        nargs='*',
                        # required=True,
                        help='Matrices to add to a base matrix.')

    parser.add_argument('-a', "--axis",
                        type=int,
                        default=1,
                        help='which axis the sequence of arrays should join along')

    #parser.add_argument('-d', "--delimiter",
    #                    nargs='?',
    #                    default="\t",
    #                    help='sequence of characters the columns are separated. default: <TAB>')

    _shared_params(parser)

    args = parser.parse_args()

    # In this function rows and columns are handled
    vp = VectorIO(
        only_apply_on=None,
        delimiter=args.delimiter,
    )

    out_frames = []

    widths_must_match = False
    heights_must_match = False
    if args.axis is 0:
        widths_must_match = True
        heights_must_match = False
    elif args.axis is 1:
        widths_must_match = False
        heights_must_match = True
    else:
        exit("ERROR: Can only work along axis 0 and 1.")

    for matrix, _ in vp.yield_matrices(args.matrices, matrix_widths_must_match=widths_must_match,
                                       matrix_heights_must_match=heights_must_match):

        # If axis = 0 keep only first columns.
        if args.axis is 0 and out_frames != [] and args.column_titles:
            matrix.drop(0, axis=0, inplace=True)

        # If axis = 1 keep only first rows.
        if args.axis is 1 and out_frames != [] and args.row_titles:
            matrix.drop(0, axis=1, inplace=True)

        # In the future if using the VectorIO class to manage name data frame you will need this.
        # matrix.reset_index(drop=True, inplace=True)

        out_frames.append(matrix)

    vp.out(pd.concat(out_frames, ignore_index=True, axis=args.axis))
    # ParseVectors("", delimiter=args.delimiter).out(output_matrix)


def _union():
    pass
    """
            # The number of key columns must be equal for any to match.
        if len(base_keys) != len(concat_keys):
            raise ValueError("Length of keys doesn't fit")

        new_base_matrix = []

        base_matrix_obj = ParseVectors(
            file_name=args.base_matrix,
            has_col_names=args.column_titles,
            has_row_names=args.row_titles,
            delimiter=args.delimiter,
            generate_vectors=False
        )
        base_matrix = base_matrix_obj.parse()

        # has_col_names = False, has_row_names = False, delimiter = "\t", generate_vectors = False
        # Handle base matrix column titles.
        # If base matrix has no titles but append matrices do.
        append_titles = None
        if args.column_titles or args.column_titles_2:
            if args.column_titles:
                append_titles = base_matrix_obj.col_titles
            else:
                append_titles = np.array(["None" for i in range(len(base_matrix[0]))])

        for matrix_to_append in args.matrices_to_append:

            mta = ParseVectors(matrix_to_append, args.column_titles_2, args.row_titles_2)
            mta_matrix = mta.parse()

            # Handle column names.
            if args.column_titles or args.column_titles_2:
                if args.column_titles_2:
                    append_titles = np.concatenate((append_titles, mta_matrix.col_titles))
                else:
                    tmp_arr = np.array(["None" for i in range(len(mta_matrix[0]))])
                    append_titles = np.concatenate((append_titles, tmp_arr))

            new_base_matrix = []
            for base_row in base_matrix:
                for append_row in mta_matrix:
                    new_base_matrix.append(np.concatenate((base_row, append_row)))


            # Handle column titles
            if args.column_titles or args.column_titles_2:
                new_base_matrix.insert(0, append_titles)

            base_matrix = np.array(new_base_matrix)
    """


def _inner_join(base_matrix, base_keys, append_matrices, append_keys, base_column_titles, append_column_titles,
                delimiter, slice_str, none_value="None"):
    """ Preforms an inner join for the join function. See the join function for details.

    The inner join function find the intersection of a base matrix and a set of append matrices.
    To do this:
        1. The append matrices are iterated in the order given.
            2. After parsing the append matrix rows are saved as dictionary values with the join columns as keys.
            3. Each row of the base matrix is iterated over.
            4. Base matrix rows with no key in the dictionary are discarded.
                5. Otherwise the value of the append row is added.
            6. The newly joined matrix is set to the base matrix.
        7. Output the joined matrix.

    :param base_matrix: The file name of the base matrix.
    :param base_keys: A list of columns to use as join keys.
    :param append_matrices: a list of matrix file names.
    :param append_keys: A list of columns to use as join keys.
    :param base_column_titles: True or False, tells if the base matrix has columns or not.
    :param append_column_titles: True or False, tells if the base matrices have columns or not.
    :param slice_str: A string representing
    :param delimiter: The delimiter to use when splitting
    :return: A matrix object with the base matrix and append matrices appended to it joined via keys.
    """
    from collections import OrderedDict

    # Make a base matrix object. The append matrices will be added to this matrix.
    base_matrix_obj = ParseVectors(
        file_name=base_matrix,
        has_col_names=base_column_titles,
        has_row_names=False,  # Row titles should just be treated as normal columns.
        delimiter=delimiter
    )
    # Parse the base matrix.
    base_matrix = base_matrix_obj.parse()

    # Handle base matrix column titles.
    # If base matrix has no titles but append matrices do.
    append_titles = None
    if base_column_titles or append_column_titles:
        if base_column_titles:
            append_titles = base_matrix_obj.col_titles
        else:
            append_titles = np.array([none_value for i in range(len(base_matrix[0]))])

    # Begin the join.
    for matrix_to_append in append_matrices:

        # Parse each append matrix.
        mta = ParseVectors(
            file_name=matrix_to_append,
            has_col_names=append_column_titles,
            has_row_names=False,  # Row titles should just be treated as normal columns.
            delimiter=delimiter
        )
        mta_matrix = mta.parse()

        # Create an ordered dict to store append matrix values in.
        mta_dict = OrderedDict({tuple(row[concat_key] for concat_key in append_keys): row for row in mta_matrix})

        # If the dictionary is the same length as the list, we know the keys are unique.
        assert len(mta_matrix) == len(mta_dict), "Error:  matrices must be unique."

        # Use this in case we want to allow different column settings
        if base_column_titles or append_column_titles:
            if append_column_titles:
                append_titles = np.concatenate((append_titles, mta_matrix.col_titles))
            else:

                tmp_arr = _getsliceorfulllist(slice_str, [none_value for i in mta_matrix[0]])
                append_titles = np.concatenate((append_titles, tmp_arr))

        new_base_matrix = []
        for vec_row in base_matrix:

            row_key = tuple(vec_row[base_key] for base_key in base_keys)

            if row_key in mta_dict:

                #if slice_list:
                #    tmp_contact_vec = [mta_dict[row_key][i] for i in slice_list]
                #else:
                #    tmp_contact_vec = mta_dict[row_key]

                tmp_contact_vec = _getsliceorfulllist(slice_str, mta_dict[row_key])
                new_base_matrix.append(np.concatenate((vec_row, tmp_contact_vec)))

                # else:
                #     tmp_contact_vec = np.array(["None" for i in range(len(mta_matrix[0]))])
                # new_base_matrix.append(np.concatenate((vec_row, tmp_contact_vec)))

        # Handle column titles
        if base_column_titles or append_column_titles:
            new_base_matrix.insert(0, append_titles)

        # Update the base matrix for the next round.
        base_matrix = np.array(new_base_matrix)

    return base_matrix_obj, base_matrix


def _left_join(base_matrix, base_keys, append_matrices, append_keys, base_column_titles, append_column_titles,
               delimiter, slice_str, none_value="None"):
    """ Preforms a left outer join. See the join function for more details.

    The left join function outputs the base matrix with a set of append matrices and/or None values.

    To do this:
        1. The append matrices are iterated in the order given.
            2. After parsing the append matrix rows are saved as dictionary values with the join columns as keys.
            3. Each row of the base matrix is iterated over.
            4. Base matrix rows with no key in the dictionary have a list or "None" values appended equal to the length
               of the current append matrix.
                5. Otherwise the value of the append row is added.
            6. The newly joined matrix is set to the base matrix.
        7. Output the joined matrix.

    :param base_matrix: The file name of the base matrix.
    :param base_keys: A list of columns to use as join keys.
    :param append_matrices: a list of matrix file names.
    :param append_keys: A list of columns to use as join keys.
    :param base_column_titles: True or False, tells if the base matrix has columns or not.
    :param append_column_titles: True or False, tells if the base matrices have columns or not.
    :param slice_str: A string representing
    :param delimiter: The delimiter to use when splitting
    :return: A matrix object with the base matrix and append matrices appended to it joined via keys.
    """

    from collections import OrderedDict

    base_matrix_obj = ParseVectors(
        file_name=base_matrix,
        has_col_names=base_column_titles,
        has_row_names=False,  # Row titles should just be treated as normal columns.
        delimiter=delimiter
    )
    base_matrix = base_matrix_obj.parse()

    # Handle base matrix column titles.
    # If base matrix has no titles but append matrices do.
    append_titles = None
    if base_column_titles or append_column_titles:
        if base_column_titles:
            append_titles = base_matrix_obj.col_titles
        else:
            append_titles = np.array([none_value for i in range(len(base_matrix[0]))])

    for matrix_to_append in append_matrices:
        # Parse the append matrix.
        mta = ParseVectors(
            file_name=matrix_to_append,
            has_col_names=append_column_titles,
            has_row_names=False,  # Row titles should just be treated as normal columns.
            delimiter=delimiter,
        )
        mta_matrix = mta.parse()

        # For base rows without a matching append row.
        null_base_values = _getsliceorfulllist(slice_str, [none_value for i in range(len(mta_matrix[0]))])

        # Make an ordered dict of the input
        mta_dict = OrderedDict({tuple(row[concat_key] for concat_key in append_keys): row for row in mta_matrix})

        # Multiple row with the same keys would require joining all combinations. Therefore, must be unique.
        if len(mta_matrix) != len(mta_dict):
            error_quit("Error: the key columns of the append matrices must be unique.")

        if base_column_titles or append_column_titles:

            if append_column_titles:
                tmp_arr = _getsliceorfulllist(slice_str, mta.col_titles)
            else:
                tmp_arr = _getsliceorfulllist(slice_str, [none_value for i in mta[0]])

            append_titles = np.concatenate((append_titles, tmp_arr))

        new_base_matrix = []
        for vec_row in base_matrix:

            # Find the key in the base matrix.
            row_key = tuple(vec_row[base_key] for base_key in base_keys)

            if row_key in mta_dict:
                tmp_contact_vec = _getsliceorfulllist(slice_str, mta_dict[row_key])
            else:
                # If not, fill the right with "None" values.
                tmp_contact_vec = np.array(null_base_values)

            new_base_matrix.append(np.concatenate((vec_row, tmp_contact_vec)))

        # Handle column titles
        if base_column_titles or append_column_titles:
            new_base_matrix.insert(0, append_titles)

        # Set the base matrix to the new matrix
        base_matrix = np.array(new_base_matrix)

    return base_matrix_obj, base_matrix


def _outer_join(base_matrix, base_keys, append_matrices, append_keys, base_column_titles, append_column_titles,
                delimiter, slice_str, none_value="None"):
    """
    :param base_matrix: The file name of the base matrix.
    :param base_keys: A list of columns to use as join keys.
    :param append_matrices: a list of matrix file names.
    :param append_keys: A list of columns to use as join keys.
    :param base_column_titles: True or False, tells if the base matrix has columns or not.
    :param append_column_titles: True or False, tells if the base matrices have columns or not.
    :param slice_str: A string representing
    :param delimiter: The delimiter to use when splitting
    :return: A matrix object with the base matrix and append matrices appended to it joined via keys.
    """
    # Read over base matrix, join and pop from append matrices.
    # When base matrix finished add non-popped from append matrices

    base_matrix_obj = ParseVectors(
        file_name=base_matrix,
        has_col_names=base_column_titles,
        has_row_names=False,  # Row titles should just be treated as normal columns.
        delimiter=delimiter
    )
    base_matrix = base_matrix_obj.parse()

    # Handle base matrix column titles.
    append_titles = None
    if base_column_titles or append_column_titles:
        if base_column_titles:
            append_titles = base_matrix_obj.col_titles
        else:
            append_titles = np.array([none_value for i in base_matrix[0]])

    # Begin the join. First for each append matrix.
    for matrix_to_append in append_matrices:

        # This needs to be reset in case of multiple append matrices, the length of the base matrix will change.
        empty_base_matrix = [none_value for i in base_matrix[0]]

        # Parse append matrix.
        mta = ParseVectors(
            file_name=matrix_to_append,
            has_col_names=append_column_titles,
            has_row_names=False,  # Row titles should just be treated as normal columns.
            delimiter=delimiter
        )
        mta_matrix = mta.parse()

        # Handle titles.
        if base_column_titles or append_column_titles:
            if append_column_titles:
                tmp_arr = _getsliceorfulllist(slice_str, mta.col_titles)
            else:
                tmp_arr = _getsliceorfulllist(slice_str, [none_value for i in mta_matrix[0]])

            append_titles = np.concatenate((append_titles, tmp_arr))

        # Make a empty append matrix.
        empty_append_matrix = [none_value for i in range(len(mta_matrix[0]))]

        # To accommodate non-unique base matrices.
        # Move values to here after they have been seen once.
        seen_once_dict = {}

        # Make a dictionary using the given tuple as a key.
        mta_dict = {tuple(row[concat_key] for concat_key in append_keys): row for row in mta_matrix}

        # If matrices are not unique rows will be duplicated.
        assert len(mta_matrix) == len(mta_dict), "Error: Append matrix keys must be unique."

        new_base_matrix = []
        for vec_row in base_matrix:

            row_key = tuple(vec_row[base_key] for base_key in base_keys)

            if row_key in mta_dict:
                tmp_contact_vec = mta_dict[row_key]
                # Move to seen matrix.
                seen_once_dict[row_key] = mta_dict[row_key]
                # Delete from original append dict
                del mta_dict[row_key]

            elif row_key in seen_once_dict:
                # This accommodates non-unique base matrices.
                # Allowing deletion of entries from the main dict, but leaving them still join-able.
                tmp_contact_vec = mta_dict[row_key]
            else:
                tmp_contact_vec = np.array(empty_append_matrix)

            tmp_contact_vec = _getsliceorfulllist(slice_str, tmp_contact_vec)

            # Add row to output matrix.
            new_base_matrix.append(np.concatenate((vec_row, tmp_contact_vec)))

        # Remaining keys have not been used.
        for row_key in mta_dict:
            if slice:
                tmp_remaining = _getsliceorfulllist(slice_str, mta_dict[row_key])
                # np.array([mta_dict[row_key][i] for i in slice_list])
            else:
                tmp_remaining = np.array(mta_dict[row_key])

            new_base_matrix.append(np.concatenate((empty_base_matrix, tmp_remaining)))

        # Handle column titles
        if base_column_titles or append_column_titles:
            new_base_matrix.insert(0, append_titles)

        # Finally update matrix.
        base_matrix = new_base_matrix

    return base_matrix_obj, base_matrix


def _getsliceorfulllist(slice_str, row_list, keep=True):
    """ If slice_str is None return original list, else return a slice of the list described with slice_str.

    :param slice_str:
    :param row_list:
    :return:
    new_matrix, list_with_indices =_slice_list(matrix, slice_string, keep=True)
    new_matrix, list_with_indices = _slice_list(np.array([row_list]), slice_str, keep=True))

    """
    if slice_str is not None:
        new_matrix, _ = _slice_list(np.array([row_list]), slice_str, keep=keep)
        out_list = new_matrix[0]
    else:
        out_list = row_list
    return out_list


def _handlenegativeindex():
    pass


def _generatekeycollist(index_str):
    """ Return a list of integer keys from a string separated by commas or colons.
    Commas = simple delimiters
    Colons = Ranges.
    :return: A list of integers.
    """

    key_list = []

    for index_el in index_str.split(","):

        # Colons indicate ranges. Therefore, treat these as a special case.
        if ":" in index_el:
            start_and_stop_range = index_el.split(":")

            assert index_el.count(":") == 1, "Error: Only once colon allowed per range. %s" % index_el
            assert len(start_and_stop_range) == 2, "Error: Ranges must have one start and one stop. %s " % index_el

            start = int(start_and_stop_range[0])
            stop = int(start_and_stop_range[1])

            assert start < stop, "Error: Start must be less than stop. %s < %s " % (start, stop,)

            for i in range(start, stop):
                key_list.append(i)
        else:
            # Other values should be simple integers.
            key_list.append(int(index_el))

    return key_list


def join(parser):
    """ Joins two or more matrices on one or more columns.

    The join function joins a matrix with one or more matrices based on set of
    one or more columns. The first matrix passed will be treated as the base
    (base matrix) which the others are appended to (append matrices). Each
    additional append matrix will be appended to the join of the base matrix
    and it's predecessor. The base matrix can be different, however, the
    append matrices must all share the same shape and column order.

    The join function offers four types of joins, LEFT, INNER, and OUTER.

    LEFT  - Actually, a left outer join, keeps all elements in the base matrix
            and either appends matching rows from the append matrices, or adds
            a row of "None" values.

            Requirements:
                1. Join columns of append matrices must be unique.

    INNER - Returns only rows matching between the matrices.

            Requirements:
                1. Join columns of base matrices must be unique.
                2. Join columns of append matrices must be unique.

    OUTER - Returns all rows from the base and append matrices. Fills in
            non-matched rows with "None" values.

    More information can be found at the following links:
    https://en.wikipedia.org/wiki/Join_(SQL)
    https://en.wikipedia.org/wiki/Join_(SQL)#Inner_join
    https://en.wikipedia.org/wiki/Cartesian_product

    Join two matrices on a key column. Various join types are supported. Left outer join is the default.
    Note: Multiple files can be added for the second field these will be appended.
    Also the first file must have unique values for the column being joined, but the second set of files need not
    be unique.

    #Examples:

    ```
    $ cat matrix_a.vec
    a   1
    b   2
    c   3

    $ cat matrix_b.vec
    a   4
    b   5
    e   7

    # A left join. This keeps all values on the left
    $ vectools join matrix_a.vec matrix_b.vec
    a   1   a   4
    b   2   b   5
    c   3   None    None

    # A inner join. This keeps all values common to both.
    $ vectools join -j INNER -k1 0 -k2 0 matrix_a.vec matrix_b.vec
    a   1   a   4
    b   2   b   5

    # An outer join. This keeps all values on the left. Not all tables must have unique keys for this join.
    $ vectools join -j OUTER -k1 0 -k2 0 matrix_a.vec matrix_b.vec
    a   1   a   4
    b   2   b   5
    c   3   None    None
    None    None    e   7

    $ cat matrix_c.vec
    a   9
    b   9
    d   9

    vectools join -s 1: matrix_*.vec

    @TODO: Finish making slice examples.
    vectools join -s 1 -k1 0 -k2 0 matrix_a.vec matrix_b.vec
    vectools join -s 0:2 -k1 0 -k2 0 matrix_a.vec matrix_b.vec
    vectools join -s 2: -k1 0 -k2 0 matrix_a.vec matrix_b.vec
    vectools join -s :2 -k1 0 -k2 0 matrix_a.vec matrix_b.vec
    """

    base_matrix_obj = []
    joined_matrix = []
    join_types = ["LEFT", "INNER", "OUTER"]  # "RIGHT", "FULL", "SELF", "CARTESIAN" "UNION",

    parser.add_argument('-j', '--join-type',
                        type=str,
                        required=False,
                        choices=join_types,
                        default=join_types[0],
                        help='(left) matrix with k1 and c1 ')

    parser.add_argument('-c1', "--base-column-titles",
                        action="store_true",
                        help='The base matrix has column titles.')

    parser.add_argument('-c2', "--append-column-titles",
                        action="store_true",
                        help='The append matrix has column titles.')

    parser.add_argument('-k1', '--base-join-columns',
                        metavar='key1',
                        type=str,
                        default="0",
                        help='key-columns of the base matrix to join on.')

    parser.add_argument('-k2', '--append-join-columns',
                        metavar='key2',
                        type=str,
                        default="0",
                        help='key-columns of the append matrices to join on.')

    parser.add_argument('-s', '--slice',
                        metavar='slice',
                        type=str,
                        required=False,
                        default=None,
                        help='Optional: Select which columns from the append matrix to keep.')

    parser.add_argument('matrices_to_append',
                        metavar='matrices_to_append',
                        type=str,
                        nargs='+',
                        help='Files to join, the first is treated as the base and following files the append matrices.')

    # Get shared parameters, such as the delimiting character, etc.
    _shared_params(parser, enable_row_titles=False, enable_column_titles=False)

    args = parser.parse_args()

    base_matrix = args.matrices_to_append[0]
    append_matrices = args.matrices_to_append[1:]

    # Check for errors.
    if not len(append_matrices) > 0:
        error_quit("Error: No append matrices passed.", exit_program=True)

    check_file_existence(base_matrix, accept_stdin=False)
    check_file_existence(append_matrices, accept_stdin=False)

    # Parse the keys to join the matrices on.
    base_keys = _generatekeycollist(args.base_join_columns)
    append_keys = _generatekeycollist(args.append_join_columns)

    # We cannot match any rows if the sizes of the the join columns sets are different.
    if len(base_keys) != len(append_keys):
        raise ValueError("Error: The number columns to join on base and append matrices are different.")

    if args.join_type == "INNER":

        # The base matrix
        base_matrix_obj, joined_matrix = _inner_join(
            base_matrix=base_matrix,
            base_keys=base_keys,
            append_matrices=append_matrices,
            append_keys=append_keys,
            base_column_titles=args.base_column_titles,
            append_column_titles=args.append_column_titles,
            delimiter=args.delimiter,
            slice_str=args.slice
        )

    elif args.join_type == "LEFT":

        base_matrix_obj, joined_matrix = _left_join(
            base_matrix=base_matrix,
            base_keys=base_keys,
            append_matrices=append_matrices,
            append_keys=append_keys,
            base_column_titles=args.base_column_titles,
            append_column_titles=args.append_column_titles,
            delimiter=args.delimiter,
            slice_str=args.slice
        )
    elif args.join_type == "OUTER":

        base_matrix_obj, joined_matrix = _outer_join(
            base_matrix=base_matrix,
            base_keys=base_keys,
            append_matrices=append_matrices,
            append_keys=append_keys,
            base_column_titles=args.base_column_titles,
            append_column_titles=args.append_column_titles,
            delimiter=args.delimiter,
            slice_str=args.slice
        )
    elif args.join_type == "UNION":
        pass
    else:
        error_quit('ERROR: Unknown join type "%s".' % args.join_type)


    base_matrix_obj.out(joined_matrix)
    # ParseVectors("").out(base_matrix)


def vrep(parser):
    """ Returns rows which contain a given set of elements.
    Vector Search a Regular expression and Print
    The keep list should be a text file with one item per line.
    This is useful for values in row when you don't know the order.
    Search a regular expression and print
    :return:
    """

    parser.add_argument('matrices',
                        nargs='*',
                        help='Matrices to add to a base matrix.')

    parser.add_argument('-v', "--invert-match",
                        action="store_true",
                        help='Returned vectors do not matching any of the specified patterns.')

    parser.add_argument("--large",
                        action="store_true",
                        help='')

    parser.add_argument('-o', "--order-independent",
                        action="store_true",
                        help='Returned vectors do not matching any of the specified patterns.')

    # parser.add_argument("--only-apply-on-pattern",
    #                    nargs='?',
    #                    help="Only consider the specified columns in the first matrix containing patters.")

    # parser.add_argument("--only-apply-on-search",
    #                    nargs='?',
    #                    help="Only consider the specified columns in the search matrices.")

    _shared_params(parser, only_apply_on=True)

    args = parser.parse_args()

    vp = VectorIO(
        only_apply_on=args.only_apply_on,
        delimiter=args.delimiter,
        has_col_names=args.column_titles,
        has_row_names=args.row_titles
    )

    filter_vp = VectorIO(
        only_apply_on=args.only_apply_on,
        delimiter=args.delimiter,
        has_col_names=args.column_titles,
        has_row_names=args.row_titles
    )

    matrices = args.matrices
    filter_file = matrices.pop(0)

    if args.large:
        # In the case that there are more filter vectors than query vectors.
        vec_dict = OrderedDict()
        row_titles_dict = OrderedDict()

        # First parse the matrices to filter vectors.
        for row_title, vector, select_cols in vp.yield_vectors(matrices):
            vec_key = frozenset(select_cols) if args.order_independent else tuple(select_cols)
            vec_dict[vec_key] = vector
            row_titles_dict[vec_key] = row_title

        # Next parse filter vectors and delete any remove matching queries.
        for row_title, _, select_cols in filter_vp.yield_vectors(filter_file):
            filter_key = frozenset(select_cols) if args.order_independent else tuple(select_cols)
            # If invert_match is True, print only when the key is not in dict.
            # If invert_match is False, print only when the key is in the dict.
            if filter_key in vec_dict:
                del vec_dict[filter_key]
                del row_titles_dict[filter_key]

        # Parse vectors to filter again and decide to print or not based on the dict.
        # This is needed as the dictionary will only keep one instance of each vector.
        for row_title, vector, select_cols in vp.yield_vectors(matrices):
            tmp_query = frozenset(select_cols) if args.order_independent else tuple(select_cols)
            if args.invert_match and tmp_query in vec_dict:
                vp.iterative_out(row_title, vector)
            elif not args.invert_match and tmp_query not in vec_dict:
                vp.iterative_out(row_title, vector)
    else:
        key_set = set()
        # @TODO: Behavior can get weird if select_cols used.
        for row_title, vector, select_cols in vp.yield_vectors(filter_file):
            key_set.add(frozenset(vector) if args.order_independent else tuple(vector))

        for row_title, vector, select_cols in filter_vp.yield_vectors(matrices):
            tmp_query = frozenset(select_cols) if args.order_independent else tuple(select_cols)
            if args.invert_match != (tmp_query in key_set):
                filter_vp.iterative_out(row_title, vector)


def vector_sort(parser):
    """ Sort a vector based on columns given by keys

    Sort a vector based on columns given with the parameter:
    --keys (comma separated). Default is the first column.
    Default is sorting in ascending order
    To sort descending, give the parameter --reverse

    #Examples:
    $ cat matrix.csv
    2,50,12500,98,1
    0,13,3250,28,1
    1,16,4000,35,1
    2,20,5000,45,1
    1,24,6000,77,-1

    $ vectools sort matrix.csv -d ,
    0,13,3250,28,1
    1,16,4000,35,1
    1,24,6000,77,-1
    2,50,12500,98,1
    2,20,5000,45,1

    $ vectools sort matrix.csv -d , --keys 4,3,2,1,0
    1,24,6000,77,-1
    0,13,3250,28,1
    1,16,4000,35,1
    2,20,5000,45,1
    2,50,12500,98,1

    $ vectools sort matrix.csv -d , --keys 4,3,2,1,0 --reverse
    2,50,12500,98,1
    2,20,5000,45,1
    1,16,4000,35,1
    0,13,3250,28,1
    1,24,6000,77,-1
    """
    from natsort import index_natsorted, order_by_index

    parser.add_argument('matrices',
                        nargs='*',
                        help='Matrices to subtracts from a base matrix.')

    parser.add_argument("--natural",
                        action="store_true",
                        help='Use natural sorting.')

    parser.add_argument("--descending",
                        action="store_true",
                        help='Sort in descending order.')

    parser.add_argument('-k', '--keys',
                        type=legal_characters,
                        default="0",
                        help='Columns to sort by ordered by precedence (comma separated). Default: First column')

    _shared_params(parser, only_apply_on=True)

    args = parser.parse_args()

    vp = VectorIO(
        only_apply_on=args.keys,
        delimiter=args.delimiter,
        has_col_names=args.column_titles,
        has_row_names=args.row_titles
    )

    df, sf = vp.parse_vectors(args.matrices)

    if args.natural:
        df = df.reindex(index=order_by_index(df.index, index_natsorted(sf.as_matrix(), reverse=args.descending)))
    else:
        keys = [df.columns[i] for i in _create_slice_list(args.keys, df.shape[-1])]
        df = df.sort_values(by=keys, axis=0, ascending=not args.descending)

    vp.out(df)


def append_values_to(parser):
    """ Append values to a given matrix row or column wise.

    This functions allows a user to append standard values to a matrix row wise or column wise

    #Examples:

    $ cat matrix.csv
    2,50,12500,98,1
    0,13,3250,28,1
    1,16,4000,35,1
    2,20,5000,45,1
    1,24,6000,77,-1

    #>axis = 1<

    $ vectools append_values_to -d , --values 0 matrix.csv
    2,50,12500,98,1,0
    0,13,3250,28,1,0
    1,16,4000,35,1,0
    2,20,5000,45,1,0
    1,24,6000,77,-1,0

    $ vectools append_values_to -d , --values 0,2,4,3,2,1 matrix.csv
    2,50,12500,98,1,0,2,4,3,2,1
    0,13,3250,28,1,0,2,4,3,2,1
    1,16,4000,35,1,0,2,4,3,2,1
    2,20,5000,45,1,0,2,4,3,2,1
    1,24,6000,77,-1,0,2,4,3,2,1

    $ vectools append_values_to -d , --values 0,2,4,3,2,1 matrix.csv  --to 0,2,4,3,2,1
    0,1,2,2,2,3,50,4,12500,98,1
    0,1,0,2,2,3,13,4,3250,28,1
    0,1,1,2,2,3,16,4,4000,35,1
    0,1,2,2,2,3,20,4,5000,45,1
    0,1,1,2,2,3,24,4,6000,77,-1

    $ vectortools append_values_to -d , --values 0,2 matrix.csv  --to 0,4
    0,2,50,12500,2,98,1
    0,0,13,3250,2,28,1
    0,1,16,4000,2,35,1
    0,2,20,5000,2,45,1
    0,1,24,6000,2,77,-1

    #>axis = 0<

    $ vectools append_values_to --axis 0 -d , --values 0 matrix.csv2,50,12500,98,1
    0,13,3250,28,1
    1,16,4000,35,1
    2,20,5000,45,1
    1,24,6000,77,-1
    0,0,0,0,0

    $ vectools append_values_to --axis 0 -d , --values 0,1,2,3,4 matrix.csv
    2,50,12500,98,1
    0,13,3250,28,1
    1,16,4000,35,1
    2,20,5000,45,1
    1,24,6000,77,-1
    0,0,0,0,0
    1,1,1,1,1
    2,2,2,2,2
    3,3,3,3,3
    4,4,4,4,4

    $ vectortools.py append_values_to --axis 0 -d , --values 0,foo,bar matrix.csv --to 0,3,7
    0,0,0,0,0
    2,50,12500,98,1
    0,13,3250,28,1
    foo,foo,foo,foo,foo
    1,16,4000,35,1
    2,20,5000,45,1
    1,24,6000,77,-1
    bar,bar,bar,bar,bar

    """
    parser.add_argument('infile', nargs='?', type=str, default="sys.stdin")

    parser.add_argument(
        '-v', '--values', type=str, help="The values, comma separated, to add to the matrix.",
        required=True)

    parser.add_argument(
        '-a', '--axis',
        type=int, nargs='?',
        help="Append row(s) (0) or columns (1) to matrix. Default: 1", default=1)

    parser.add_argument(
        '--to',
        type=str,
        help="In which column/row the values should be inserted. Default: Append at end")

    _shared_params(parser)
    args = parser.parse_args()
    vector_parser = ParseVectors(args.infile, args.column_titles, args.row_titles, delimiter=args.delimiter)
    matrix = vector_parser.parse()
    cols = vector_parser.col_titles
    rows = vector_parser.row_titles

    values = args.values.split(",")
    if args.to is not None:
        positions = args.to.split(",")
    else:
        positions = [-1] * len(values)
    for index, value in enumerate(values):
        if index >= len(positions):
            position = -1
        else:
            position = int(positions[index])
        # row append
        if args.axis == 0:
            matrix = _append_row(matrix, rows, position, value, index)
        # column append
        elif args.axis == 1:
            matrix = _append_column(matrix, cols, position, value, index, rows)
        else:
            raise ValueError('wrong argument for --axis: %i' % args.axis)

    vector_parser.out(matrix, cols, rows)


def chop(parser):
    """ Removes rows from a matrix.
    This function removes rows from a matrix
    You have to say which rows you want to keep (--keep-rows) or to remove (--remove-rows)
    in a comma separated list like 1,3,7 or 1,4:7,9:


    See slice if you want to remove columns


    #Examples:

    $ cat matrix.csv
    1	0	1	0	1
    0	1	0	1	0
    2	0	1	0	1
    0	2	0	1	0
    2	0	2	0	1

    $ vectortools.py chop --keep-rows 1:4 matrix.csv
    0	1	0	1	0
    2	0	1	0	1
    0	2	0	1	0
    2	0	2	0	1

    $ vectortools.py chop --remove-rows 0,2:4 matrix.csv
    0	1	0	1	0

    """
    parser.add_argument('infile',
                        nargs='?',
                        type=str,
                        default="sys.stdin")

    parser.add_argument('--keep-rows',
                        metavar="KEPT-ROWS",
                        type=str,
                        default=None,
                        help="The rows which should be kept. Comma separated")

    parser.add_argument('--remove-rows',
                        metavar="REMOVED-ROWS",
                        type=str,
                        help="The rows which should be removed. Omitted if --keep-rows is present. Comma separated")

    _shared_params(parser)  # , only_apply_on=True

    args = parser.parse_args()

    vector_parser = ParseVectors(
        file_name=args.infile,
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        # col_titles=None,
        # row_titles=None,
        delimiter=args.delimiter,
        # only_apply_on_columns=args.only_apply_on
    )

    matrix = vector_parser.parse()
    cols = vector_parser.col_titles
    rows = vector_parser.row_titles

    number_of_rows, _ = np.shape(matrix)

    if args.keep_rows is None and args.remove_rows is None:
        raise ValueError("Nothing given for either keep-rows nor remove-rows")
    if args.keep_rows is not None:
        row_list = args.keep_rows.split(',')
    else:
        row_list = args.remove_rows.split(',')
    try:
        crow_list = []
        for el in row_list:
            # find colon if present
            index_of_colon = el.find(":")

            # first = 0
            last = number_of_rows
            # if colon is present
            if index_of_colon != -1:
                # if the colon is at the beginning like :3
                if index_of_colon == 0:
                    last = int(el[1:len(el)]) + 1

                # if the colon is at the end of the element like 20:
                if index_of_colon == (len(el) - 1):
                    first = int(el[:len(el) - 1])
                else:
                    first = int(el[:index_of_colon])
                    last = int(el[index_of_colon + 1:]) + 1
                crow_list.extend(list(range(first, last)))
            else:
                crow_list.append(int(el))
        row_list = crow_list[:]
    except ValueError:
        raise ValueError("there is a non-integer value in your list of to keeping/removing column list\n")
    if args.keep_rows is None:
        tmp_number_of_rows, _ = np.shape(matrix)
        nrow_list = list(range(0, tmp_number_of_rows))
        row_list = list(set(row_list))
        for x in row_list:
            nrow_list.remove(x)
        row_list = nrow_list[:]
    new_matrix = matrix[row_list, :]

    if rows is not None:
        rows = [rows[i] for i in row_list]

    vector_parser.out(new_matrix, cols, rows)  # , cols, rows)


def aggregate(parser):
    """ Aggregate values into rows based on key-columns.

    The aggregate function is similar to join in that it combines rows of data based on key-columns. However, unlike
    join it will combine the values of matching rows behind each unique key and only output the key-column and append
    column(s) .For example the matrix a matrix with two rows r1(a, 1) r2(a,2) would aggregate to r1(a, 1;2). Finally
    users can choose between the output creating a single column with the append values combined on a specified
    delimiter or creating n new columns, where n in the largest number of aggregated values on a key.

    #Examples:

    cat matrix.csv
    key1,a
    key1,b
    key2,c

    vectools aggregate -d , -k1 0 -k2 1 matrix.csv
    key1,a,b
    key2,c,None

    vectools aggregate -d , --combine-on ";"  key_matrix.csv many_matrix.csv
    key1,a;b
    key2,c

    """

    parser.add_argument('-kc', '--key-columns',
                        # metavar="0,1:-1",
                        type=str,
                        default="0",
                        help='The columns to group the aggregate values on.')

    parser.add_argument('-ac', '--append-columns',
                        type=str,
                        default="1:",
                        help='The columns aggregate on key columns.')

    parser.add_argument('-ad', '--aggregate-delimiter',
                        type=str,
                        help="Combine all aggregated values into one column delimited by a character.",
                        default=None)

    parser.add_argument('-nv', '--none-value',
                        type=str,
                        help="The value to print for none values.",
                        default=None)

    parser.add_argument('matrices',
                        nargs='*',
                        help='Matrices to add to a base matrix.')

    _shared_params(parser)

    args = parser.parse_args()

    # Parse matrices and build aggregate list as we go, can move line by line.

    aggregate_dict = OrderedDict()
    longest_list_len = 0

    vp = VectorIO(
        delimiter=args.delimiter,
        has_col_names=args.column_titles,
        # has_row_names=args.row_titles
    )

    for row_title, vector, _ in vp.yield_vectors(args.matrices):
        # Get key
        key_vec = tuple(_getsliceorfulllist(args.key_columns, vector))
        # Get append
        append_vec = _getsliceorfulllist(args.append_columns, vector)

        if key_vec not in aggregate_dict:
            aggregate_dict[key_vec] = []

        for row_el in append_vec:
            aggregate_dict[key_vec].append(row_el)

        agg_len = len(aggregate_dict[key_vec])

        if agg_len > longest_list_len:
            longest_list_len = agg_len

    if args.column_titles:
        key_col_list = list(_getsliceorfulllist(args.key_columns, vp.col_titles))
        append_col_list = list(_getsliceorfulllist(args.append_columns, vp.col_titles))

        new_col_list = []
        if args.aggregate_delimiter:
            new_col_list = [args.aggregate_delimiter.join(append_col_list)]
        else:
            while len(new_col_list) < longest_list_len:
                new_col_list += append_col_list

        # If column names are present update column names.
        vp.set_column_titles(key_col_list + new_col_list)

    # Output aggregated rows.
    for key in aggregate_dict:

        if args.aggregate_delimiter:
            aggregate_dict[key] = [args.aggregate_delimiter.join(aggregate_dict[key])]
        else:
            while len(aggregate_dict[key]) < longest_list_len:
                aggregate_dict[key].append(args.none_value)

        vp.iterative_out("", list(key) + aggregate_dict[key])


def format_vec(parser):
    """ Convert between various vector formats.
    This function changes formats to other formats:
    csv -> svmlight (named)
    svmlight (named) -> csv
    Declare your inputs format and the output format you wish to have
    If you have in input or output named svmlight, declare it with
    the --named parameter

    Examples:

    $ cat matrix.csv
    5,50,12500,98,1
    8,13,3250,28,1
    3,16,4000,35,1
    2,20,5000,45,1
    1,24,6000,77,-1

    $ vectools format -i csv -o svmlight matrix.csv -d ,
    5.0,1:50.0,2:12500.0,3:98.0,4:1.0
    8.0,1:13.0,2:3250.0,3:28.0,4:1.0
    3.0,1:16.0,2:4000.0,3:35.0,4:1.0
    2.0,1:20.0,2:5000.0,3:45.0,4:1.0
    1.0,1:24.0,2:6000.0,3:77.0,4:-1.0

    $ cat matrix.svmlight
    1,1:2,2:50,3:12500,4:98
    1,1:0,2:13,3:3250,4:28
    1,1:1,2:16,3:4000,4:35
    1,1:2,2:20,3:5000,4:45
    -1,1:1,2:24,3:6000,4:77

    $ vectools format -o csv -i svmlight matrix.svmlight -d ,
    1,2,50,12500,98
    1,0,13,3250,28
    1,1,16,4000,35
    1,2,20,5000,45
    -1,1,24,6000,77

    $ cat matrix.namedsvmlight
    1,group:2,age:50,kcal/day:12500,km/day:98
    1,group:0,age:13,kcal/day:3250,km/day:28
    1,group:1,age:16,kcal/day:4000,km/day:35
    1,group:2,age:20,kcal/day:5000,km/day:45
    -1,group:1,age:24,kcal/day:6000,km/day:77

    $ vectools format -o csv -i svmlight matrix.namedsvmlight -d ,
    1,2,50,12500,98
    1,0,13,3250,28
    1,1,16,4000,35
    1,2,20,5000,45
    -1,1,24,6000,77

    $ vectools format -o csv -i svmlight matrix.namedsvmlight -d , --named
    Class,group,age,kcal/day,km/day
    1,2,50,12500,98
    1,0,13,3250,28
    1,1,16,4000,35
    1,2,20,5000,45
    -1,1,24,6000,77

    $ vectools format -o csv -i svmlight matrix.namedsvmlight -d , --named | vectools \
                     format -o svmlight -i csv --named -d ,
    Class,1:group,2:age,3:kcal/day,4:km/day
    1.0,1:2.0,2:50.0,3:12500.0,4:98.0
    1.0,1:0.0,2:13.0,3:3250.0,4:28.0
    1.0,1:1.0,2:16.0,3:4000.0,4:35.0
    1.0,1:2.0,2:20.0,3:5000.0,4:45.0
    -1.0,1:1.0,2:24.0,3:6000.0,4:77.0

    """
    parser.add_argument('infile', nargs='?', type=str, default="sys.stdin")

    parser.add_argument('--class-column',
                        type=int,
                        default=0,
                        help="Which column is the class column. Default first (0)")

    parser.add_argument('--named',
                        action="store_true",
                        help='convert it to named svm_light format')

    parser.add_argument('-i', '--in-format',
                        type=str,
                        default="csv",
                        help="The format of infile. Could be one of {csv, svmlight}. Default: csv")

    parser.add_argument('-o', '--out-format',
                        type=str,
                        default="svmlight",
                        help="The format of the output file. Could be one of {csv, svmlight}. Default: svmlight")

    _shared_params(parser)

    args = parser.parse_args()

    vector_parser = ParseVectors(
        args.infile,
        args.column_titles,
        args.row_titles,
        delimiter=args.delimiter)

    out_machine = ParseVectors(
        "", args.column_titles, args.row_titles, delimiter=args.delimiter)

    if args.in_format == "csv":
        if args.out_format == "svmlight":
            _to_svm_light(vector_parser, args, out_machine)
        elif args.out_format == "csv":
            out_machine.out(vector_parser.parse(), vector_parser.col_titles, vector_parser.row_titles)
        else:
            "out-format {} with in-format {} not implemented yet".format(args.out_format, args.in_format)
            assert False
    elif args.in_format == "svmlight":
        if args.out_format == "csv":
            _to_csv(vector_parser, args)
        else:
            "out-format {} with in-format {} not implemented yet".format(args.out_format, args.in_format)
            assert False
    else:
        "in-format {} not implemented yet".format(args.in_format)
        assert False


def _to_svm_light(vector_parser, args, out_machine):
    """

    :param vector_parser:
    :param args:
    :param out_machine:
    :return:
    """
    cols = None
    for row_line in vector_parser.generate(args.row_titles):
        row, line = row_line
        line = list(line)
        if vector_parser.has_col_names and cols is None:
            cols = vector_parser.col_titles
            cols.insert(0, cols.pop(args.class_column))
        # get the class to the beginning
        line.insert(0, line.pop(args.class_column))

        for index, el in enumerate(line):
            if index == 0:
                pass
            else:
                if args.named and cols is not None:
                    line[index] = "{}:{}".format(str(cols[index]), str(line[index]))
                else:
                    line[index] = "{}:{}".format(str(index), str(line[index]))
        out_machine.iterative_out(row_title=None, vector=line)


def _to_csv(vector_parser, args):
    """ Convert an svm^light or named svm^light format vector to character separated values (csv).
    With this function you can change your input format to another format.
    In this case you convert from svm_light format to character separated values

    see `vectortools.py to_svmlight` to convert from svm_light to csv

    """
    matrix = vector_parser.parse()
    cols = []
    class_name = "Class"
    list_of_dicts = []
    for line in matrix:
        line_dict = dict()
        for index, el in enumerate(line):
            if index == 0:
                if class_name not in cols:
                    cols.append(class_name)
                line_dict[class_name] = el
            else:
                (col, element) = el.split(":")
                if col not in cols:
                    cols.append(col)
                line_dict[col] = element
        list_of_dicts.append(line_dict)
    csv_matrix = []
    for line_dict in list_of_dicts:
        line = []
        for col in cols:
            if col in line_dict:
                line.append(line_dict[col])
            else:
                line.append("--")
        csv_matrix.append(line)
    if args.named:
        vector_parser.out(csv_matrix, cols)
    else:
        vector_parser.out(csv_matrix)


def _append_row(matrix, rows, position, value, num=0):
    """

    :param matrix:
    :param rows:
    :param position:
    :param value:
    :return:
    """
    if type(value) == str:
        matrix = matrix.astype(str)
    if position < 0:
        nrow = np.shape(matrix)[0]
        position = position + 1 + nrow
    if rows is not None:
        rows.insert(position, 'r%i' % (num,))
    matrix = np.insert(matrix, position, value, axis=0)
    return matrix


def _append_column(matrix, cols, position, value, num=0, rows_are_defined=None):
    """

    :param matrix:
    :param cols:
    :param position:
    :param value:
    :return:
    """
    col_position = position
    if type(value) == str:
        matrix = matrix.astype(str)
    if position < 0:
        ncol = np.shape(matrix)[1]
        position = position + 1 + ncol
        col_position = position
    if rows_are_defined:
        col_position = position + 1
    if cols is not None:
        cols.insert(col_position, 'c%i' % num)

    matrix = np.insert(matrix, position, value, axis=1)
    return matrix
