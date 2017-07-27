import sys
from lib.inputoutput import ParseVectors, _shared_params, VectorIO, cast_datatype, error_quit
import numpy as np
from select import select


def _merge_titles(title1, title2):
    """
    Merges two title lists into one. If the titles of a row/column at given index i==j is not equal, then
     it merges to the form 'title1_title2'
    :param title1: first list
    :param title2: second list
    :return: merged list
    """
    if len(title1) == len(title2):
        for index, value in enumerate(title1):
            if value == title2[index]:
                pass
            else:
                title1[index] = value + "_" + title2[index]
    else:
        raise IndexError("Length of Titles differ")
    return title1


def _intorfloat(number_str):
    if "." in number_str:
        return float(number_str)
    else:
        return int(number_str)


def add(parser):
    """ Adds matrices or scalars to a matrix.
    Adds matrices via matrix-addition from stdin or files.

    Note: A convenience function for adding scalars is included, this actually adds a matrix of the same shape
    populated with the value provided.

    #Examples:

    $ cat matrix.csv
    1	0	0
    0	1	0
    0	0	1

    $ cat matrix_1.csv
    1	2	3
    0	0	0
    0	0	2

    $ cat matrix_2.csv
    1.0	0.0	0.0
    1.0	0.0	-1.0
    1.0	1.0	1.0

    $ vectools add matrix.csv matrix_1.csv
    2	2	3
    0	1	0
    0	0	3

    $ cat matrix.csv | vectools add matrix_1.csv
    2	2	3
    0	1	0
    0	0	3

    $ vectools add matrix.csv matrix_1.csv matrix_2.csv
    3	2	3
    1	1	-1
    1	1	4

    $ cat matrix.csv | vectools add matrix_*.csv
    3	2	3
    1	1	-1
    1	1	4

    cat matrix.csv | vectools add --scalar 4 matrix_1.csv
    6	6	7
    4	5	4
    4	4	7

    cat matrix.csv | vectools add --scalar 4.5 matrix_1.csv
    6.5	6.5	7.5
    4.5	5.5	4.5
    4.5	4.5	7.5
    """

    parser.add_argument(
        'matrices',
        nargs='*',
        help='Matrices to add to a base matrix.')

    parser.add_argument(
        '--scalar',
        default=None,
        help='Adds a given scalar to the base matrix.')

    parser.add_argument(
        '--reverse',
        action="store_true",
        help="String operations only. Reverse addition order including scalar addition (Except STDIN).")

    _shared_params(parser, only_apply_on=True)

    args = parser.parse_args()

    vp = VectorIO(
        only_apply_on=args.only_apply_on,
        delimiter=args.delimiter,
        has_col_names=args.column_titles,
        has_row_names=args.row_titles
    )

    matrix_sum = None
    for data_frame, sliced_frame in vp.yield_matrices(args.matrices):
        if matrix_sum is None:
            matrix_sum = data_frame
        else:
            if args.only_apply_on:
                # Make a linked slice.
                matrix_sum.iloc[:, vp.slice_list] += data_frame.iloc[:, vp.slice_list].as_matrix()
            else:
                matrix_sum += data_frame.as_matrix()

    # cast scalar
    if args.scalar:
        casted_scalar = cast_datatype(args.scalar)
        if args.only_apply_on:

            tmp_mat_sum_cast = matrix_sum.iloc[:, vp.slice_list].astype(type(casted_scalar))

            if args.reverse:
                matrix_sum.iloc[:, vp.slice_list] = casted_scalar + tmp_mat_sum_cast
            else:
                matrix_sum.iloc[:, vp.slice_list] += casted_scalar
        else:
            if args.reverse:
                matrix_sum = casted_scalar + matrix_sum.astype(type(casted_scalar))
            else:
                matrix_sum += casted_scalar

    vp.out(matrix_sum)


def subtract(parser):
    """ Subtracts matrices or scalars from a matrix.
    Subtracts matrices via matrix-subtraction from a base matrix passed from stdin or a file.
    requires n matrices with same dimension of the matrix in stdin or file

    Note: A convenience function for subtracting scalars is included, this actually subtracts a matrix of the same
    shape populated with the value provided.

    #Examples:

    $ cat matrix.csv
    1	0	0
    0	1	0
    0	0	1

    $ cat matrix_1.csv
    1	2	3
    0	0	0
    0	0	2

    $ cat matrix_2.csv
    1.0	0.0	0.0
    1.0	0.0	-1.0
    1.0	1.0	1.0

    $ vectools subtract matrix.csv matrix_1.csv
    0	-2	-3
    0	1	0
    0	0	-1

    $ cat matrix.csv | vectools subtract matrix_1.csv
    0	-2	-3
    0	1	0
    0	0	-1

    $ vectools subtract matrix.csv matrix_1.csv matrix_2.csv
    -1	-2	-3
    -1	1	-1
    -1	-1	-2

    $ cat matrix.csv | vectools subtract matrix_*.csv
    -1	-2	-3
    -1	1	-1
    -1	-1	-2

    cat matrix.csv | vectools subtract --scalar 4 matrix_1.csv
    -4	-6	-7
    -4	-3	-4
    -4	-4	-5

    cat matrix.csv | vectools subtract --scalar 4.5 matrix_1.csv
    -4.5	-6.5	-7.5
    -4.5	-3.5	-4.5
    -4.5	-4.5	-5.5

    """

    parser.add_argument('matrices',
                        nargs='*',
                        help='Matrices to subtracts from a base matrix.')

    parser.add_argument(
        '--scalar',
        default=None,
        help='Adds a given scalar to the base matrix.')

    parser.add_argument(
        '--reverse',
        action="store_true",
        help="Default subtracts the scalar from matrix. When passed matrix is subtracted from scalar.")

    _shared_params(parser, only_apply_on=True)

    args = parser.parse_args()

    vp = VectorIO(
        only_apply_on=args.only_apply_on,
        delimiter=args.delimiter,
        has_col_names=args.column_titles,
        has_row_names=args.row_titles
    )

    matrix_sum = None

    for data_frame, sliced_frame in vp.yield_matrices(args.matrices):

        if matrix_sum is None:
            matrix_sum = data_frame
        else:
            if args.only_apply_on:
                # Make a linked slice.
                matrix_sum.iloc[:, vp.slice_list] -= data_frame.iloc[:, vp.slice_list].as_matrix()
            else:
                matrix_sum -= data_frame

    if args.scalar:
        # Cast scalar and matrix.
        casted_scalar = cast_datatype(args.scalar)
        matrix_sum = matrix_sum.astype(type(casted_scalar))

        if args.only_apply_on:
            if args.reverse:
                matrix_sum.iloc[:, vp.slice_list] = casted_scalar - matrix_sum.iloc[:, vp.slice_list]
            else:
                matrix_sum.iloc[:, vp.slice_list] -= casted_scalar
        else:
            if args.reverse:
                matrix_sum = casted_scalar - matrix_sum
            else:
                matrix_sum -= casted_scalar

    vp.out(matrix_sum)


def multiply(parser):
    """ Multiplies matrices via matrix-multiplication or scalars.

    This function multiplies two matrices via matrix multiplication or all elements in a matrix by a scalar
    and returns a matrix.

    There are a number of constraints that must be observed when performing matrix multiplication.
        1. Only two matrices may be passed or one for scalar multiplication.
        2. Scalar multiplication and only-apply-on only works on the first matrix passed.
        3. Scalar multiplication takes place before matrix multiplication if both are passed.
        4. This function only accepts numeric matrices.
        5. The rows and columns are renamed by col: x0 to xn and row: y0 to yn

    #Examples:

    $ cat row.tsv
    1    2    3

    $ cat column.tsv
    7
    8
    9

    $ vectools multiply row.tsv column.tsv
    50

    $ vectools multiply column.tsv row.tsv
    7       14      21
    8       16      24
    9       18      27


    $ cat matrix.csv
     2    -1   0
    -1    2    -1
     0    1    2

    $ cat inverse_matrix.csv
    0.75    0.5    0.25
    0.5     1.0    0.5
    0.25    0.5    0.75

    $ vectools multiply matrix.csv inverse_matrix.csv
    1.0    0.0    0.0
    0.0    1.0    0.0
    0.0    0.0    1.0

    """
    parser.add_argument('matrixA',
                        nargs='?',
                        type=str,
                        default=None,
                        help='Base matrix')

    parser.add_argument('matrixB',
                        nargs='?',
                        type=str,
                        default=None,
                        help='Base matrix')

    parser.add_argument('--scalar',
                        default=None,
                        help='Adds a given scalar to the base matrix.')

    _shared_params(parser, only_apply_on=True)

    args = parser.parse_args()

    matrix_a_file = args.matrixA
    matrix_b_file = args.matrixB

    args = parser.parse_args()

    vp = VectorIO(
        only_apply_on=args.only_apply_on,
        delimiter=args.delimiter,
        has_col_names=args.column_titles,
        has_row_names=args.row_titles
    )

    if matrix_a_file is None:
        error_quit("Error: No append matrices passed.", exit_program=True)

    matrix_a, sliced_frame_a = vp.parse_matrices(matrix_a_file)

    vp1 = VectorIO(
        only_apply_on=args.only_apply_on,
        delimiter=args.delimiter,
        has_col_names=args.column_titles,
        has_row_names=args.row_titles
    )

    matrix_b = None
    if matrix_b_file is not None:
        matrix_b, sliced_frame_b = vp1.parse_matrices(matrix_b_file)

    # Isolate matrices from lists.
    if len(matrix_a) > 0:
        matrix_a = matrix_a[0]

    if len(sliced_frame_a) > 0:
        sliced_frame_a = sliced_frame_a[0]

    if len(matrix_b) > 0:
        matrix_b = matrix_b[0]

    # if len(sliced_frame_b) > 0:
    #    sliced_frame_b = sliced_frame_b[0]

    # Perform multiplication.
    if args.scalar:
        casted_scalar = cast_datatype(args.scalar)
        matrix_a = matrix_a.astype(type(casted_scalar))

        if args.only_apply_on:
            matrix_a.iloc[:, vp.slice_list] *= casted_scalar
        else:
            matrix_a *= casted_scalar

    if matrix_b is not None:
        # Slightly misleading as this does matrix multiplication.
        matrix_a = np.dot(matrix_a, matrix_b)

    """
    if columns is not None:
        column_titles = []
        for i in range(0, np.shape(matrix)[0]):
            column_titles.append("x" + str(i))

    if rows is not None:
        row_titles = []
        for i in range(0, np.shape(matrix)[1]):
            row_titles.append("y" + str(i))
    """

    vp.out(matrix_a)


def dot_product(parser):
    """ Calculates the dot product of two vectors.

    #Examples:

    $ cat matrix.csv
    2	-1	0
    -1	2	-1
    0 -1	2

    $ cat unit_vector.csv
    1.0	0.0	0.0
    0.0	1.0	0.0
    0.0	0.0	1.0

    $ vectools dot_product matrix.csv unit_vector.csv
    6
    """
    parser.add_argument('vector1',
                        nargs='?',
                        type=str,
                        default="sys.stdin",
                        help='first vector, only one value per line')

    parser.add_argument('vector2',
                        nargs=1,
                        type=str,
                        help='second vector, only one value per line')

    _shared_params(parser)

    args = parser.parse_args()
    v1 = args.vector1
    v2 = args.vector2[0]

    matrix_parser = ParseVectors(v1, args.column_titles, args.row_titles, args.delimiter)
    vector1 = matrix_parser.parse()

    mp = ParseVectors(v2, args.column_titles, args.row_titles, args.delimiter)
    vector2 = mp.parse()

    vector1 = vector1.reshape(-1)
    vector2 = vector2.reshape(-1)
    dot_product_result = np.dot(vector1, vector2)

    ParseVectors("", delimiter=args.delimiter).out(dot_product_result)


def inverse(parser):
    """ Calculates the inverse matrix for square matrices. (Must be invertible)

    #Examples:
    $ cat matrix.csv
    2	-1	0
    -1	2	-1
    0	-1	2

    $ vectortools.py inverse matrix.csv
    0.75	0.5	0.25
    0.5	1.0	0.5
    0.25	0.5	0.75

    """

    parser.add_argument('matrix',
                        nargs='?',
                        type=str,
                        default="sys.stdin",
                        help='square matrix to invert')

    _shared_params(parser)

    args = parser.parse_args()

    matrix_parser = ParseVectors(
        args.matrix,
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        delimiter=args.delimiter
    )

    matrix = matrix_parser.parse()

    cols = matrix_parser.col_titles
    rows = matrix_parser.row_titles

    # shape = np.shape(matrix)
    height, width = matrix.shape

    if height != width:
        raise ValueError("Matrix is not a square matrix")
    det = _calc_determinant(matrix)
    if det == 0:
        raise ValueError("Matrix is singular. It has no inverse")

    inverse_matrix = np.linalg.inv(matrix)

    matrix_parser.out(inverse_matrix, cols, rows)


def determinant(parser):
    """ Calculates the determinant for square matrices.

    #Examples:

    $ cat matrix.csv
    2	-1	0
    -1	2	-1
    0	-1	2

    $ vectools determinant matrix.csv
    4
    """
    parser.add_argument('matrix',
                        nargs='?',
                        type=str,
                        default="sys.stdin",
                        help='square matrix to calculate the determinant')

    _shared_params(parser)

    args = parser.parse_args()

    matrix_parser = ParseVectors(
        args.matrix,
        args.column_titles,
        args.row_titles,
        args.delimiter
    )

    matrix = matrix_parser.parse()

    column_titles = matrix_parser.col_titles
    row_titles = matrix_parser.row_titles

    shape = np.shape(matrix)

    if shape[0] != shape[1]:
        raise ValueError("Matrix is not a square matrix")

    det = _calc_determinant(matrix)

    sys.stdout.write(str(det) + "\n")


def _calc_determinant(matrix):
    """
    calculates the determinant recursive
    :param matrix: a square matrix (np object)
    :return: determinant (an int or float)
    """
    if np.shape(matrix)[0] == 2:
        return matrix[0][0] * matrix[1][1] - (matrix[0][1] * matrix[1][0])
    else:
        det = 0
        for index, el in enumerate(matrix[0]):
            col = list(range(0, np.shape(matrix)[0]))
            col.remove(index)
            row = list(range(1, np.shape(matrix)[0]))
            sub_matrix = matrix[np.ix_(row, col)]
            if index % 2 == 0:
                det += el * _calc_determinant(sub_matrix)
            else:
                det -= el * _calc_determinant(sub_matrix)
        return det


def eigen_values(parser):
    """ Calculates the eigenvalues of a matrix. The order is the same as in the function eigenvectors

    #Examples:
    $ cat matrix.csv
    2	-1	0
    -1	2	-1
    0	-1	2

    $ vectools eigenvalues matrix.csv
    3.41421356237	2.0	0.585786437627

    """
    parser.add_argument('matrix',
                        nargs='?',
                        type=str,
                        default="sys.stdin",
                        help='matrix to calculate the eigenvalues for')

    _shared_params(parser)

    args = parser.parse_args()

    vector_parser = ParseVectors(
        args.matrix,
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        delimiter=args.delimiter
    )

    matrix = vector_parser.parse()
    w, v = np.linalg.eig(matrix)

    vector_parser.out([w], vector_parser.col_titles, vector_parser.row_titles)


def eigen_vectors(parser):
    """ Calculates the eigenvectors of a given matrix. The order is the same as in the function eigenvalues

    #Examples:

    $ cat matrix.csv
    2	-1	0
    -1	2	-1
    0	-1	2

    $ vectools eigenvectors matrix.csv
    -0.5	-0.707106781187	0.5
    0.707106781187	4.05925293379e-16	0.707106781187
    -0.5	0.707106781187	0.5
    """
    parser.add_argument('matrix',
                        nargs='?',
                        type=str,
                        default="sys.stdin",
                        help='matrix to calculate the eigenvectors for')

    _shared_params(parser)

    args = parser.parse_args()

    vector_parser = ParseVectors(
        args.matrix,
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        delimiter=args.delimiter
    )

    matrix = vector_parser.parse()

    w, v = np.linalg.eig(matrix)

    vector_parser.out(v, vector_parser.col_titles, vector_parser.row_titles)


def sum_up(parser):
    """ Sums the columns of a matrix

    sums the matrix columnwise
    """

    parser.add_argument('matrices',
                        nargs='*',
                        help='Matrices to sum.')

    # parser.add_argument('matrix', nargs='?', type=str, help='Base matrix', default="sys.stdin")

    _shared_params(parser, only_apply_on=True)

    args = parser.parse_args()

    sources = args.matrices
    # If a matrix is passed from stdin use this as the base matrix and add other to it.
    # Use the technique below to prevent hanging if no stdin info present.
    # https://repolinux.wordpress.com/2012/10/09/non-blocking-read-from-stdin-in-python/
    first_matrix = None
    while sys.stdin in select([sys.stdin], [], [], 0)[0]:
        if sys.stdin.readable():
            first_matrix = "sys.stdin"
        break

    # If no stdin is present, use the first filename passed as the base matrix.
    if not first_matrix:
        first_matrix = sources.pop(0)
    # Parse the base matrix.
    matrix_parser = ParseVectors(
        first_matrix,
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )

    matrix = matrix_parser.parse()
    cols = matrix_parser.col_titles

    # Remove the row title.
    if args.row_titles and cols:
        cols = cols[1:]

    # Can't think of a good way to handel rows so omitting them.
    # rows = matrix_parser.row_titles

    tmp_sum = np.sum(matrix, axis=0)

    # Add remaining matrices to the base matrix.
    for add_matrix_file_name in sources:
        mp = ParseVectors(
            add_matrix_file_name,
            has_col_names=args.column_titles,
            has_row_names=args.row_titles,
            delimiter=args.delimiter,
            only_apply_on_columns=args.only_apply_on
        )

        tmp_sum = tmp_sum + np.sum(mp.parse(), axis=0)

    matrix_parser.out([tmp_sum], cols, None)
