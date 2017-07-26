from lib.inputoutput import outputvector, ParseVectors, _shared_params, VectorIO
import numpy as np
import sys
from select import select


def confusion_matrix(parser):
    """ Generates a confusion matrix from a set of predictions.
    Should be easy with scikit learn see link:
    http://scikit-learn.org/stable/modules/generated/sklearn.metrics.confusion_matrix.html#sklearn.metrics.confusion_matrix
    :return:
    """

    parser.add_argument('--cutoff',
                        type=float,
                        default=0.0,
                        nargs=1,
                        help='Given score will be used for the prediction cutoff.')

    parser.add_argument('-p', "--predictions",
                        nargs='?',
                        type=str,
                        help='Predictions via model of known classes.')

    _shared_params(parser)

    args = parser.parse_args()

    from sklearn.metrics import confusion_matrix as calc_confusion_matrix_

    prediction_vecs = ParseVectors(
        args.predictions,
        args.column_titles,
        args.row_titles,
        delimiter=args.delimiter
    )

    true_classes = []
    predicted_classes = []
    for row_id, prediction_vector in prediction_vecs.generate():

        true_class = prediction_vector[0]
        predicted_class = prediction_vector[1]
        score = prediction_vector[2]

        if score > args.cutoff:
            true_classes.append(true_class)
            predicted_classes.append(predicted_class)

    conf_matrix = calc_confusion_matrix_(true_classes, predicted_classes)

    ParseVectors("", delimiter=args.delimiter).out(conf_matrix)


from math import sqrt


def MCC(fn, fp, tn, tp):
    fn, fp, tn, tp = float(fn), float(fp), float(tn), float(tp)
    try:
        numerator = tp * tn - fp * fn
        denominator = sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
        return numerator/denominator
    except ZeroDivisionError:
        return -1.0


def accuracy(FN, FP, TN, TP):
    return 1.0


def prediction_stats(parser):
    """ Calculate basic stats for a set of predictions.
    """

    parser.add_argument('matrices',
                        nargs='*',
                        help='Matrices to add to a base matrix.')

    parser.add_argument('--true-class',
                        type=int,
                        default=0,
                        nargs=1,
                        help='The column containing the true class of the samples.')

    parser.add_argument('--model-class',
                        type=int,
                        default=0,
                        nargs=1,
                        help='The column containing the true class of the samples.')

    parser.add_argument('--prediction',
                        type=int,
                        default=0,
                        nargs=1,
                        help='The column containing the true class of the samples.')

    parser.add_argument('--prediction-true-value',
                        type=str,
                        default="True",
                        nargs=1,
                        help='The column containing the true class of the samples.')

    _shared_params(parser, only_apply_on=True)

    args = parser.parse_args()

    # Get list of all files to add.
    sources = args.addable_matrices

    # If a matrix is passed from stdin use this as the base matrix and add other to it.
    # Use the technique below to prevent hanging if no stdin info present.
    # https://repolinux.wordpress.com/2012/10/09/non-blocking-read-from-stdin-in-python/
    while sys.stdin in select([sys.stdin], [], [], 0)[0]:
        if sys.stdin.readable():
            sources.insert(0, "sys.stdin")
        break

    class_metrics_dict = {}
    # Add remaining matrices to the base matrix.
    for matrix_file_name in sources:
        vector_parser = ParseVectors(
            matrix_file_name,
            has_col_names=args.column_titles,
            has_row_names=args.row_titles,
            delimiter=args.delimiter,
            only_apply_on_columns=args.only_apply_on
        )

        for row_title, input_vector in vector_parser.generate(return_type=str):
            # Select needed columns
            # Build score dict for each class
            # Multi-class MCC called Rk http://rk.kvl.dk/introduction/index.html
            true_class = input_vector[args.true_class]
            model_class = input_vector[args.model_class]
            prediction_value = input_vector[args.prediction]

            if model_class not in class_metrics_dict:
                # FN, FP, TN, TP
                class_metrics_dict.update({model_class: [0, 0, 0, 0]})

            if true_class == model_class:
                if prediction_value == args.prediction_true_value:
                    class_metrics_dict[model_class][3] += 1  # TP
                else:
                    class_metrics_dict[model_class][0] += 1  # FN
            else:
                if prediction_value == args.prediction_true_value:
                    class_metrics_dict[model_class][1] += 1  # FP
                else:
                    class_metrics_dict[model_class][2] += 1  # TN

        out_row_titles, out_matrix = [], []
        for class_name in sorted(class_metrics_dict):
            print(MCC(class_metrics_dict[class_name]))

    # Output the sum of the matrices.
    # matrix_parser.out(matrix, matrix_parser.getcolumntitles(), matrix_parser.getrowtitles())


def shape(parser):
    """
    :return:
    """

    parser.add_argument('infile',
                        nargs='+',
                        type=str,
                        default="sys.stdin")

    _shared_params(parser)

    args = parser.parse_args()

    for in_file in args.infile:
        input_matrix = ParseVectors(
            in_file,
            has_col_names=args.column_titles,
            has_row_names=args.row_titles,
            delimiter=args.delimiter
        ).parse()

        height, width = input_matrix.shape

        ParseVectors("", delimiter=args.delimiter).out([[height, width]])


def run_lda(parser, ordered_file_names_iter, has_title=False, has_row_ids=False):
    """ Run an LDA

    :param ordered_file_names_iter:
    :param has_title:
    :param has_row_ids:
    :return:
    """

    from sklearn.lda import LDA

    vectors = []
    vector_classes = []
    vector_row_ids = []
    class_int = 0
    from sklearn import datasets

    iris = datasets.load_iris()
    target_names = iris.target_names

    print(target_names)

    y = iris.target

    print(y)

    for file_name in sorted(ordered_file_names_iter):

        f_obj = open(file_name)

        if has_title:
            title = f_obj.readline().split()

        for line in f_obj:
            spln = line.strip().split()
            if has_row_ids:
                vector_row_ids.append(spln.pop(0))

            vector_classes.append(class_int)
            vectors.append([float(x) for x in spln])

        class_int += 1

    vectors = np.array(vectors)
    vector_classes = np.array(vector_classes)
    print(vector_classes)
    lda = LDA(n_components=3)
    X_r2 = lda.fit(vectors, vector_classes).transform(vectors)

    print(X_r2)
    '''
    plt.figure()
    for c, i, target_name in zip("rgb", [0, 1, 2], ["0", "1"]):
        plt.scatter(X_r2[vector_classes == i, 0], X_r2[vector_classes == i, 1],
                    c=c, label=target_name)

    plt.legend()
    plt.title('LDA of IRIS dataset')

    plt.show()
    '''


def columnstats(parser):
    """Calculate various statistics about a matrix.
    Average values
    stddev
    quantiles 10, 25, 75, 90
    non-zero rows

    :return:
    """
    parser.add_argument('--infiles',
                        dest='infiles',
                        nargs='+',
                        required=True,
                        help="")

    parser.add_argument('--has_title',
                        dest='has_title',
                        type=bool,
                        required=False,
                        default=False,
                        help="")

    parser.add_argument('--has_row_ids',
                        dest='has_row_ids',
                        type=bool,
                        required=False,
                        default=False,
                        help="")

    args = parser.parse_known_args()[0]

    in_files = args.infiles
    has_title = args.has_title
    has_row_ids = args.has_row_ids

    for file_name in sorted(in_files):

        f_obj = open(file_name)

        if has_title:
            title = f_obj.readline().strip().split()

        # Maybe we should be using the CSV module for this?
        data_list = []

        count_from = 0
        if has_row_ids:
            count_from = 1

        for line in f_obj:
            spln = line.strip().split()

            for i in range(count_from, len(spln)):
                if data_list is []:
                    for tmp_i in range(count_from, len(spln) + 1):
                        data_list.append([])
                # print(i, len(data_list), len(spln))
                data_list[i].append(float(spln[i]))

        # Label columns numerically if they do not have title labels.
        if not has_title:
            title = [str(i) for i in range(count_from, len(data_list) + 1)]

        print("\t".join(("Col_ID", "Average", "Median", "Standard_Dev",
                         "10th", "25th", "75th", "90th", "#non-zero")))

        for i in range(count_from, len(title)):
            out_line = (
                title[i],
                np.average(data_list[i]),
                np.median(data_list[i]),
                np.std(data_list[i]),
                np.percentile(data_list[i], 10),
                np.percentile(data_list[i], 25),
                np.percentile(data_list[i], 75),
                np.percentile(data_list[i], 90),
                len([x for x in data_list[i] if x > 0])
            )

            print("\t".join([str(x) for x in out_line]))


# =======================================================================================================================
#                                                  Feature Selection
# =======================================================================================================================

def run_pca(parser):
    """ Maps data to a lower dimensional space with using principal component analysis.

    Example:
    $ cat matrix.csv
    5,50,12500,98,1
    8,13,3250,28,1
    3,16,4000,35,1
    2,20,5000,45,1
    1,24,6000,77,-1

    $ vectools pca -d , matrix.csv
    -6.40999614277e-06,0.150292846224,0.987734717554,-0.0423342423033,5.40753522195e-14
    0.00399985968832,2.90264282242e-05,-4.28977889059e-06,2.35416599035e-06,-0.999992000096
    0.99996492208,0.00725660705543,-0.00107244471956,0.000588541886596,0.00399996800038
    0.00735905296636,-0.985982872887,0.146628865479,-0.0792691271653,1.18904885937e-13
    5.47848233979e-06,0.0720914388758,-0.0536558793689,-0.995953749438,1.55071441799e-12

    """

    parser.add_argument('matrices',
                        nargs='*',
                        help='Matrices to perform PCA on.')

    parser.add_argument('-n', "--components",
                        type=int,
                        default=2,
                        help='number of components to keep')

    _shared_params(parser, only_apply_on=True, random_state=True)

    args = parser.parse_args()
    from sklearn.decomposition import PCA, IncrementalPCA

    vec_parser = VectorIO(
        only_apply_on=args.only_apply_on,
        delimiter=args.delimiter,
        has_col_names=args.column_titles,
        has_row_names=args.row_titles
    )

    data_frame, sliced_frame = vec_parser.parse_vectors(args.matrices)
    row_titles = data_frame.index

    # if args.components is None or args.components > np.shape(matrix)[1]:
    if args.components > sliced_frame.shape[1]:
        exit("Error not enough columns.")

    # @TODO: Set up large option.
    # pca = IncrementalPCA(n_components=args.components, batch_size=10)
    # pca_result = pca.fit_transform(sliced_frame.as_matrix())

    pca = PCA(n_components=args.components, random_state=args.random_state)

    pca_result = pca.fit_transform(sliced_frame.as_matrix())

    out_col_titles = ["pca_{}".format(i) for i in range(args.components)]

    vec_parser.set_column_titles(out_col_titles)

    for i in range(len(pca_result)):
        vec_parser.iterative_out(row_titles[i], pca_result[i])


def roc_curve(parser):
    """ Calculates the receiver operating characteristic (ROC) curve for a binary classification.

    Given a set of binary classifications are various threshold settings.
    Files should be passed in order or named so that they sort in ascending order.

    Returns a line that represents the roc curve.

    The curve is created by plotting the true positive rate (TPR) against the false positive rate
    (FPR) at various threshold settings. The true-positive rate is also known as sensitivity,
    recall or probability of detection[1] in machine learning. The false-positive rate is also known as the
    fall out or probability of false alarm[1] and can be calculated as (1  specificity)
    :return:
    """

    parser.add_argument('class_scores_vectors',
                        metavar='training_vectors',
                        type=str,
                        nargs='?',
                        help='Files containing vectors for training an SVM.')

    _shared_params(parser)

    args = parser.parse_args()

    from sklearn.metrics import roc_curve, auc

    prediction_vec_obj = ParseVectors(
        args.class_scores_vectors,
        args.column_titles,
        args.row_titles,
        delimiter=args.delimiter
    )

    prediction_vecs = prediction_vec_obj.parse()

    import numpy as np
    import matplotlib.pyplot as plt
    from itertools import cycle

    from sklearn import svm, datasets
    from sklearn.metrics import roc_curve, auc
    from sklearn.model_selection import train_test_split
    from sklearn.preprocessing import label_binarize
    from sklearn.multiclass import OneVsRestClassifier
    from scipy import interp

    height, width = prediction_vecs.shape
    assert width % 2 is 0, "Error: Predictions and score columns must be present."
    lw = 2
    for i in range(0, width, 2):
        labels_vecs = prediction_vecs[:, i]
        predictions_vecs = prediction_vecs[:, i+1]
        print(labels_vecs)
        print(predictions_vecs)
        fpr, tpr, _ = roc_curve(labels_vecs, predictions_vecs)
        roc_auc = auc(fpr, tpr)
        print(fpr, tpr, roc_auc)

    plt.figure()
    plt.plot(fpr, tpr,
             label='micro-average ROC curve (area = {0:0.2f})'
                   ''.format(roc_auc),
             color='deeppink', linewidth=4)

    plt.plot([0, 1], [0, 1], 'k--', lw=lw)
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.show()
    true_classes = []
    predicted_classes = []
    #for prediction_vector in prediction_vecs.generate():
    #    true_classes.append(prediction_vector[1][1])
    #    predicted_classes.append(prediction_vector[1][2])
    #conf_matrix = calc_confusion_matrix_(true_classes, predicted_classes)  # conf_matrix
    #ParseVectors("", delimiter=args.delimiter).out(conf_matrix)


# y_score = classifier.fit(x_train, y_train).decision_function(x_test)
# y_score = fit_obj.decision_function(x_test)
# y_test[:, i], y_score[:, i]
# fpr = dict()
# tpr = dict()
# fpr, tpr, _ = roc_curve(testing_labels[:, 0], testing_predictions[:, 0])
# print(fpr, tpr)
# roc_auc = auc(fpr, tpr)

def relative_support():
    """
    Closed pattern == x is closed if x if frequent and no super pattern y > x exists with the same support
    Max-pattern
    Support is the probability that a transaction contains x and y
    An item is frequent if the support of X in no less than a min sup threshold denoted as sigma
    :return:
    """
    # TODO
    pass


def absolute_support():
    pass


def pearson_group(parser):
    """ Calculates the pearson correlation coefficient with a cutoff at a given threshold ?????

    The first column is the name of the line. It has to be unique (e.g. IDs).
    The second column has to be the group (e.g. lncRNA, protein_coding, male or female. It depends on what you want to compare.)
    The remaining columns are sources. Where the data comes from or at which time the data was recorded.

    Example:
    $ cat correlation.vec
    course1,English,56,75,45,71,62,64,58,80,76,61
    course2,Maths,66,70,40,60,65,56,59,77,67,63
    course3,Maths,50,25,55,23,30,29,45,20,24,31

    $ vectortools.py pearson correlation.vec -d , -r 0.6 -g Maths,English
    group.1_group.2,key.1_key.2,pearson_coefficient,p-value,source1.1,source1.2,source2.1,source2.2,source3.1,source3.2,source4.1,source4.2,source5.1,source5.2,source6.1,source6.2,source7.1,source7.2,source8.1,source8.2,source9.1,source9.2,source10.1,source10.2
    Maths_English,course3_course1,-0.917374227662,0.00018438067236,50.0,56.0,25.0,75.0,55.0,45.0,23.0,71.0,30.0,62.0,29.0,64.0,45.0,58.0,20.0,80.0,24.0,76.0,31.0,61.0
    Maths_English,course2_course1,0.80588057964,0.0048790052238,66.0,56.0,70.0,75.0,40.0,45.0,60.0,71.0,65.0,62.0,56.0,64.0,59.0,58.0,77.0,80.0,67.0,76.0,63.0,61.0

    """
    import warnings

    warnings.filterwarnings("ignore")
    parser.add_argument('vector', nargs='?', type=str, help='vector for pearson correlation', default="sys.stdin")
    # parser.add_argument('-c', "--column-titles", action="store_true", help='column titles are defined')

    parser.add_argument('-g',
                        "--groups",
                        type=str,
                        required=True,
                        help='Groups to calculate the correlation for. Requires two or more groups (comma seperated)')

    parser.add_argument('-r', '--pearson-correlation-threshold',
                        type=float,
                        default=0.90)

    parser.add_argument('-p', '--p-value-threshold',
                        type=float,
                        default=0.05)

    parser.add_argument('--processes',
                        type=int,
                        default=1)

    parser.add_argument('-n', '--number-of-values-above-zero',
                        help="(default: 5)",
                        type=int,
                        default=5)

    _shared_params(parser, True, False, True, True)

    args = parser.parse_args()

    input_vector = ParseVectors(
        args.vector,
        args.column_titles,
        None,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )

    matrix = input_vector.parse()
    cols = input_vector.col_titles
    groups = args.groups.split(",")
    processes = args.processes
    above_zero = args.number_of_values_above_zero
    correlation_threshold = args.pearson_correlation_threshold
    p_value_threshold = args.p_value_threshold

    (new_matrix, new_cols) = _calc_correlation(matrix, cols, groups, processes, above_zero, correlation_threshold,
                                               p_value_threshold,_pearson_calc)

    input_vector.out(new_matrix, new_cols)


def _calc_correlation(matrix, cols, groups, processes, above_zero, correlation_threshold, p_value_threshold, function,
                      text="pearson_coefficient"):

    import multiprocessing

    new_matrix = []
    new_cols = ["group.1_group.2"]

    if cols is not None and len(cols) > 0:
        new_cols.append("{0}.1_{0}.2".format(cols[0]))
        new_cols.extend((text, "p-value"))
        for column in cols[2:]:
            new_cols.extend(("{}.1".format(column), "{}.2".format(column)))
    else:
        new_cols.append("key.1_key.2")
        new_cols.extend((text, "p-value"))
        for i in range(2, np.shape(matrix)[1]):
            new_cols.extend(("source{}.1".format((i - 1)), "source{}.2".format((i - 1))))

    if len(groups) < 2:
        raise ValueError("to few arguments for groups")
    dok = {}  # dict of keys
    for group in groups:
        dok[group] = {}
    lines = np.shape(matrix)[0]
    for i in range(0, lines):
        # if the value in the second column is in the dict then you can insert it there
        if matrix[i][1] in dok:
            # dok[lincRNA][ENGBLABLA] = [0.1 1.0 ...]
            dok[matrix[i][1]][matrix[i][0]] = [float(x) for x in matrix[i][2:]]
    group1, tail = groups[0], groups[1:]
    with multiprocessing.Pool(processes=processes) as pool:
        res = list()
        while len(tail) > 0:
            for key1 in dok[group1]:
                for group2 in tail:
                    for key2 in dok[group2]:
                        x = dok[group1][key1][:]
                        y = dok[group2][key2][:]
                        for index, xvalue in enumerate(x):
                            if xvalue == 0 or y[index] == 0:
                                del x[index]
                                del y[index]
                        if len(x) > above_zero:
                            res.append(pool.apply_async(function, (
                                dok, group1, group2, key1, key2, x, y, correlation_threshold,
                                p_value_threshold)))

            group1, tail = tail[0], tail[1:]
        for result in res:
            row = result.get()
            if row is not None:
                new_matrix.append(result.get())
    return new_matrix, new_cols


def _pearson_calc(dok, group1, group2, key1, key2, x, y, pct, pv):
    """

    :param dok: dict of keys. groups as first level keys, identifier as second level key with a list of values inside
    :param group1: first group
    :param group2: second group
    :param key1: first identifier
    :param key2: second identifier
    :param x: values of the first one where there are no zeros in values of the second one
    :param y: values of the second one where there are no zeros in values of the first on
    :param pct: pearson coefficient correlation threshold (R**2>=pct)
    :param pv: p-value threshold (p-value <= pv)
    :return: None if correlation is not good enough or the result list of strings
    """
    from scipy.stats.stats import pearsonr
    pear, p_value = pearsonr(x, y)
    if abs(pear) >= pct and p_value <= pv:
        row_i = []
        row_i.extend(("{}_{}".format(group1, group2), "{}_{}".format(key1, key2), pear, p_value))
        for index, value in enumerate(dok[group1][key1]):
            row_i.extend((value, dok[group2][key2][index]))
        return (row_i)
    return None


def _spearman_calc(dok, group1, group2, key1, key2, x, y, pct, pv):
    """

    :param dok: dict of keys. groups as first level keys, identifier as second level key with a list of values inside
    :param group1: first group
    :param group2: second group
    :param key1: first identifier
    :param key2: second identifier
    :param x: values of the first one where there are no zeros in values of the second one
    :param y: values of the second one where there are no zeros in values of the first on
    :param pct: pearson coefficient correlation threshold (R**2>=pct)
    :param pv: p-value threshold (p-value <= pv)
    :return: None if correlation is not good enough or the result list of strings
    """
    from scipy.stats.stats import spearmanr
    rho, p_value = spearmanr(x, y)
    if abs(rho) >= pct and p_value <= pv:
        row_i = []
        row_i.extend(("{}_{}".format(group1, group2), "{}_{}".format(key1, key2), rho, p_value))
        for index, value in enumerate(dok[group1][key1]):
            row_i.extend((value, dok[group2][key2][index]))
        return row_i
    return None


def spearman(parser):
    """ Calculates the Spearman's rank correlation coefficient.
    Requirements:
    There has to be a vector containing columns with IDs, group IDs, and lots of values.
    The Spearman's rank correlation coefficient is a measurement for correspondence between
    two variables.
    This function calculates this correlation coefficient between each sample with the group id,
    declared with the --groups parameter.
    Additionally, this function filters the results with a given threshold (-r parameter).
    Moreover a p-test is given. In addition to the cutoff with the correlation coefficient,
    it is possible to set a p-value cutoff (-p threshold).
    To reduce computation time and false positives, a number of how many values each sample should have above zero
    can be specified (-n parameter)

    Example:
    $ cat correlation.vec
    course1,English,56,75,45,71,62,64,58,80,76,61
    course2,Maths,66,70,40,60,65,56,59,77,67,63
    course3,Maths,50,25,55,23,30,29,45,20,24,31

    $ vectortools.py spearman correlation.vec -d , -r 0.6 -g Maths,English
    group.1_group.2,key.1_key.2,spearmans_rho,p-value,source1.1,source1.2,source2.1,source2.2,source3.1,source3.2,source4.1,source4.2,source5.1,source5.2,source6.1,source6.2,source7.1,source7.2,source8.1,source8.2,source9.1,source9.2,source10.1,source10.2
    Maths_English,course3_course1,-0.963636363636,7.32097480953e-06,50.0,56.0,25.0,75.0,55.0,45.0,23.0,71.0,30.0,62.0,29.0,64.0,45.0,58.0,20.0,80.0,24.0,76.0,31.0,61.0
    Maths_English,course2_course1,0.672727272727,0.0330412225454,66.0,56.0,70.0,75.0,40.0,45.0,60.0,71.0,65.0,62.0,56.0,64.0,59.0,58.0,77.0,80.0,67.0,76.0,63.0,61.0

    """
    parser.add_argument('vector',
                        nargs='?',
                        type=str,
                        help='vector for pearson correlation',
                        default="sys.stdin")

    # parser.add_argument('-c', "--column-titles", action="store_true", help='column titles are defined')
    parser.add_argument('-g', "--groups",
                        type=str, required=True,
                        help='Groups to calculate the correlation for. Requires two or more groups (comma seperated)')

    parser.add_argument('-r', '--spearmans-rank-correlation-threshold',
                        type=float,
                        default=0.90)

    parser.add_argument('-p', '--p-value-threshold',
                        type=float,
                        default=0.05)

    parser.add_argument('-n', '--number-of-values-above-zero',
                        help="(default: 5)",
                        type=int,
                        default=5)

    # parser.add_argument('-d', "--delimiter", nargs='?',
    #                     help='sequence of characters the columns are separated. default: <TAB>', default="\t")

    parser.add_argument('--processes',
                        type=int,
                        default=1)

    _shared_params(parser, True, False, True, True)
    args = parser.parse_args()

    input_vector = ParseVectors(
        args.vector,
        args.column_titles,
        None,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )

    matrix = input_vector.parse()

    groups = args.groups.split(",")

    columns = input_vector.col_titles
    processes = args.processes
    above_zero = args.number_of_values_above_zero
    correlation_threshold = args.spearmans_rank_correlation_threshold
    p_value_threshold = args.p_value_threshold
    (new_matrix, new_cols) = _calc_correlation(matrix, columns, groups, processes, above_zero, correlation_threshold,
                                               p_value_threshold, _spearman_calc, "spearmans_rho")
    input_vector.out(new_matrix, new_cols)


def summary(parser):
    """ Summarizes a matrix columnwise.
    If the matrix contains only numbers, it produces a summary
    containing the name of the column, its minimum and maximum
    value, the value of the 1st and 3rd quantile,
    and the median and mean

    Example:
    $ cat matrix.csv
    5,50,12500,98,1
    8,13,3250,28,1
    3,16,4000,35,1
    2,20,5000,45,1
    1,24,6000,77,-1

    $ vectortools.py summary -d ,  matrix.csv
    stat    0       1       2       3       4
    min     1       13      3250    28      -1
    1stQu   2.0     16.0    4000.0  35.0    1.0
    median  3.0     20.0    5000.0  45.0    1.0
    mean    3.8     24.6    6150.0  56.6    0.6
    3rdQu   5.0     24.0    6000.0  77.0    1.0
    max     8       50      12500   98      1

    """
    parser.add_argument('vector',
                        nargs='?',
                        type=str,
                        default="sys.stdin",
                        help='vector to summarize')

    parser.add_argument('--human-readable',
                        action="store_true",
                        default=None,
                        help="print human readable output (no vector)")

    _shared_params(parser, only_apply_on=True)

    args = parser.parse_args()

    input_vector = ParseVectors(
        args.vector,
        args.column_titles,
        args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )

    matrix = input_vector.parse()
    columns = input_vector.col_titles
    rows = input_vector.row_titles
    m_type = input_vector.return_type
    if m_type == str:
        _ssumary(matrix, columns, rows, args.human_readable)
    elif m_type == float:
        _fsummary(matrix, columns, rows, args.human_readable)
    else:
        raise TypeError("unknown type of matrix")


def _fsummary(matrix, columns=None, rows=None, human=None):
    """

    :param matrix:
    :param columns:
    :param rows:
    :param human:
    :return:
    """
    strings = {"name": "", "max": "", "min": "", "median": "", "1stQu": "", "mean": "", "3rdQu": ""}
    order = ["name", "min", "1stQu", "median", "mean", "3rdQu", "max"]
    if human is not None:
        for index, column in enumerate(matrix.T):
            if len(strings["name"]) > 74:
                for key in order:
                    v = strings[key]
                    sys.stdout.write("{}\n".format(v))
                    strings[key] = ""
                sys.stdout.write("\n")
            name_s = ""
            if columns is not None:
                name_s += "{}".format(columns[index])
            else:
                name_s += "{}".format(index)
            while len(name_s) < 24:
                name_s += " "
            strings["name"] += name_s
            strings["min"] += "min:\t{:.4f}\t\t".format(np.amin(column))
            strings["1stQu"] += "1stQu:\t{:.4f}\t\t".format(np.percentile(column, 25))
            strings["median"] += "median:\t{:.4f}\t\t".format(np.median(column))
            strings["mean"] += "mean:\t{:.4f}\t\t".format(np.mean(column))
            strings["3rdQu"] += "3rdQu:\t{:.4f}\t\t".format(np.percentile(column, 75))
            strings["max"] += "max:\t{:.4f}\t\t".format(np.amax(column))
        for key in order:
            v = strings[key]
            sys.stdout.write("{}\n".format(v))
            strings[key] = ""
        sys.stdout.write("\n")
    else:
        strings["name"] += "stat"
        strings["min"] += "min"
        strings["1stQu"] += "1stQu"    # :\t{:.4f}\t\t".format(np.percentile(column, 25))
        strings["median"] += "median"  # :\t{:.4f}\t\t".format(np.median(column))
        strings["mean"] += "mean"      # :\t{:.4f}\t\t".format(np.mean(column))
        strings["3rdQu"] += "3rdQu"    # :\t{:.4f}\t\t".format(np.percentile(column, 75))
        strings["max"] += "max"        # :\t{:.4f}\t\t".format(np.amax(column))

        for index, column in enumerate(matrix.T):

            if columns is not None:
                strings["name"] += "\t{}".format(columns[index])
            else:
                strings["name"] += "\t{}".format(index)

            strings["min"] += "\t{}".format(np.amin(column))
            strings["1stQu"] += "\t{}".format(np.percentile(column, 25))
            strings["median"] += "\t{}".format(np.median(column))
            strings["mean"] += "\t{}".format(np.mean(column))
            strings["3rdQu"] += "\t{}".format(np.percentile(column, 75))
            strings["max"] += "\t{}".format(np.amax(column))

        for k in order:
            v = strings[k]
            sys.stdout.write("{}\n".format(v))


def _ssumary(matrix, columns=None, rows=None, human=None):
    """

    :param matrix:
    :param columns:
    :param rows:
    :return:
    """
    sys.stdout.write("matrix contains strings\n")
    # TODO more infos pls


def minimum(parser):
    """ Returns a vector containing the minimum value for each column in a matrix.

    Example:
    $ cat matrix.csv
    5,50,12500,98,1
    8,13,3250,28,1
    3,16,4000,35,1
    2,20,5000,45,1
    1,24,6000,77,-1

    $ vectortools.py min matrix.csv -d ,
    1,13,3250,28,-1

    """
    parser.add_argument('vector',
                        nargs='?',
                        type=str,
                        default="sys.stdin",
                        help='A matrix')

    _shared_params(parser, only_apply_on=True)

    args = parser.parse_args()

    input_vector = ParseVectors(
        args.vector,
        args.column_titles,
        args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )

    matrix = input_vector.parse()
    columns = input_vector.col_titles
    rows = input_vector.row_titles

    # it makes no sense to display row titles anymore.
    # If there are column titles and row titles remove the col-title of the column with the row titles
    if rows is not None and columns is not None:
        columns = columns[1:]

    input_vector.out(_column_wise_calculation(matrix, np.min), columns, None)


def maximum(parser):
    """ Returns a vector containing the maximum value for each column in a matrix.

    Example:
    $ cat matrix.csv
    5,50,12500,98,1
    8,13,3250,28,1
    3,16,4000,35,1
    2,20,5000,45,1
    1,24,6000,77,-1

    $ vectortools.py max matrix.csv -d ,
    8,50,12500,98,1
    """
    parser.add_argument('vector',
                        nargs='?',
                        type=str,
                        help='vector to calculate maximum for', default="sys.stdin")

    _shared_params(parser, only_apply_on=True)

    args = parser.parse_args()

    input_vector = ParseVectors(
        args.vector,
        args.column_titles,
        args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on)

    matrix = input_vector.parse()
    columns = input_vector.col_titles
    rows = input_vector.row_titles

    # it makes no sense to display row titles anymore.
    # If there are column titles and row titles remove the col-title of the column with the row titles
    if rows is not None and columns is not None:
        columns = columns[1:]

    input_vector.out(_column_wise_calculation(matrix, np.max), columns, None)


def median(parser):
    """ Returns a vector containing the median value for each column in a matrix.

    Example:
    $ cat matrix.csv
    5,50,12500,98,1
    8,13,3250,28,1
    3,16,4000,35,1
    2,20,5000,45,1
    1,24,6000,77,-1

    $ vectortools.py median matrix.csv -d ,
    3.0,20.0,5000.0,45.0,1.0

    """
    parser.add_argument('vector', nargs='?', type=str, help='vector to calculate median for', default="sys.stdin")
    _shared_params(parser, only_apply_on=True)
    args = parser.parse_args()

    input_vector = ParseVectors(
        args.vector,
        args.column_titles,
        args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )

    matrix = input_vector.parse()
    columns = input_vector.col_titles
    rows = input_vector.row_titles

    if rows is not None and columns is not None:
        columns = columns[1:]

    input_vector.out(_column_wise_calculation(matrix, np.median), columns, None)


def percentile(parser):
    """ Returns a vector containing the percentile for each column in a vector.
    The percentile is a measure indicating the value below which a given percentage
    of observations in a group of observations fall (wikipedia.org/wiki/Percentile).

    Examples:
    $ cat matrix.csv
    5,50,12500,98,1
    8,13,3250,28,1
    3,16,4000,35,1
    2,20,5000,45,1
    1,24,6000,77,-1

    $ vectortools.py percentile matrix.csv -p 0.5 -d ,
    3.0,20.0,5000.0,45.0,1.0

    $ vectortools.py percentile matrix.csv -p 0.75 -d ,
    5.0,24.0,6000.0,77.0,1.0

    $ vectortools.py percentile matrix.csv -p 0.25 -d ,
    2.0,16.0,4000.0,35.0,1.0
    """

    parser.add_argument("vector",
                        nargs="?",
                        type=str,
                        default="sys.stdin",
                        help="A vector to calculate the percentile for")

    parser.add_argument("-p", "--percentile",
                        metavar="p",
                        required=True,
                        type=float,
                        help="Percentile between 0 and 1")

    _shared_params(parser, only_apply_on=True)

    args = parser.parse_args()

    input_vector = ParseVectors(
        args.vector,
        args.column_titles,
        args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )

    matrix = input_vector.parse()
    new_matrix = []
    row = []
    # transposed matrix to get the columns instead of rows
    for column in matrix.T:
        # numpy function for percentile
        row.append(np.percentile(column, args.percentile * 100))

    # get the names of rows and columns. Could be None
    rows = input_vector.row_titles
    columns = input_vector.col_titles

    new_matrix.append(row)
    # it makes no sense to display row titles anymore.
    # If there are column titles and row titles remove the col-title of the column with the row titles
    if rows is not None and columns is not None:
        columns = columns[1:]

    input_vector.out(new_matrix, columns, None)


def average(parser):
    """ Returns a vector containing the mean/average value for each column in a matrix.

    $ cat matrix.csv
    5,50,12500,98,1
    8,13,3250,28,1
    3,16,4000,35,1
    2,20,5000,45,1
    1,24,6000,77,-1

    $ vectortools.py mean matrix.csv -d ,
    3.8,24.6,6150.0,56.6,0.6

    """

    parser.add_argument('vector', nargs='?', type=str, help='vector to calculate average for', default="sys.stdin")
    _shared_params(parser, only_apply_on=True)
    args = parser.parse_args()

    input_vector = ParseVectors(
        args.vector,
        args.column_titles,
        args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on
    )

    matrix = input_vector.parse()
    columns = input_vector.col_titles
    rows = input_vector.row_titles
    # it makes no sense to display row titles anymore.
    # If there are column titles and row titles remove the col-title of the column with the row titles
    if rows is not None and columns is not None:
        columns = columns[1:]

    input_vector.out(_column_wise_calculation(matrix, np.mean), columns, None)


def sd(parser):
    """ Returns a vector containing the standard deviation of values within each column in a matrix.

    Examples:
    $ cat matrix.csv
    5,50,12500,98,1
    8,13,3250,28,1
    3,16,4000,35,1
    2,20,5000,45,1
    1,24,6000,77,-1

    $ vectortools.py sd matrix.csv -d ,
    2.7748873851,14.7918896697,3697.97241742,29.787581305,0.894427191


    """
    parser.add_argument('vector',
                        nargs='?',
                        type=str,
                        default="sys.stdin",
                        help='vector to calculate standard deviation for')

    _shared_params(parser, only_apply_on=True)

    args = parser.parse_args()

    input_vector = ParseVectors(
        args.vector,
        args.column_titles,
        args.row_titles,
        delimiter=args.delimiter,
        only_apply_on_columns=args.only_apply_on)

    matrix = input_vector.parse()
    columns = input_vector.col_titles
    rows = input_vector.row_titles

    # If there are column titles and row titles remove the col-title of the column with the row titles
    if rows is not None and columns is not None:
        columns = columns[1:]

    new_matrix = []
    row = []

    # transposed matrix to get the columns instead of rows
    for column in matrix.T:
        row.append(np.std(column, ddof=1))
    new_matrix.append(row)
    input_vector.out(new_matrix, columns, None)


def _column_wise_calculation(vector, function):
    """
    To apply a function on each column of a vector, transpose it and run a for loop over it.
    Here the vector and the function are given and returns a matrix containing one row
    of
    :param vector: the vector to apply the function on
    :param function: the function which runs over each column
    :return: returns a matrix containing one row with the results of each application on the columns
    """
    matrix = []
    row = []
    for column in vector.T:
        row.append(function(column))
    matrix.append(row)
    return matrix
