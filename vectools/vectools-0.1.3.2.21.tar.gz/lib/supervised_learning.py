import numpy as np
from lib.inputoutput import vecparse, outputvector
from lib.inputoutput import ParseVectors, _shared_params, _slice_list
from lib.inputoutput import COLUMN_TITLE_FOR_OUTPUT_MATRICES as standard_col_title
import lib.outputcolorer as bc
from select import select
from sklearn.metrics import accuracy_score
import pickle
import argparse
import sys


'''
def _shared_params(parser, enable_column_titles=True, enable_row_titles=True, enable_delimiter=True, round_to=True):
    """ This function stores basic arguments used in almost every other function.

    :param parser: An argparse object.
    :return: Does not return anything, however, adds variables to the argparse object.
    """
    if enable_column_titles:
        parser.add_argument('-c', "--column-titles",
                            action="store_true",
                            help='The matrix has column titles.')

    if enable_row_titles:
        parser.add_argument('-r', "--row-titles",
                            action="store_true",
                            help='row titles are defined')

    if enable_delimiter:
        parser.add_argument('-d', "--delimiter",
                            nargs='?',
                            default="\t",
                            help='sequence of characters the columns are separated. default: <TAB>')

    if round_to:
        parser.add_argument(
            "--round-to",
            type=int,
            default=5,
            help='The number of decimal places to round to .')
'''


def _generate_param_grid(kernel_name, c_range, gamma_range, degree_range, coef0_range, binary=True):
    """ This function handles generating a parameter grid for the grid search from the command line input.

    One complication is that multi-class a binary classiciations use different parameter formats.

    :param kernel_name: A valid kernel name (str).
    :param c_range: The range of C values (string delimited with commas).
    :param gamma_range: The range of gamma values (list of floats).
    :param degree_range: The range of degree values (list of integers).
    :param coef0_range: The range of coef0 values (list of floats).
    :param binary:
    :return: A parameter grid dict inside a list.

    [{ 'C':      [0.001, 0.01, 0.1, 1, 10, 100],
       'gamma':  [0.001, 0.01, 0.1, 1, 10, 100],
        'coef0':  [0.1, 0.0, 1],
        'degree': [3, 4, 5, 6],
        'kernel': [ 'rbf']
    }]

    parameters = {
        "estimator__C": [1, 2, 4, 8],
        "estimator__gamma": [0.001, 0.01, 0.1, 1, 10, 100],
        "estimator__degree": [1, 2, 3, 4],
        "estimator__kernel": ["linear", "poly", "rbf"],
    }

        kernal_name=args.kernel,
        C_range=[float(f) for f in args.C.strip().split(",")],
        gamma_range=[float(f) for f in args.gamma.strip().split(",")],
        degree_range=[int(i) for i in args.degree.strip().split(",")],
        coef0_range=[float(f) for f in args.coef0.strip().split(",")]

    # 'poly',
    # 'linear',
    # 'sigmoid'
    # poly   C,degree, coef0.
    # gamma  C, gamma .
    # sigmoid C, coef0.

    """

    param_grid = dict()

    if not binary:
        if "linear" in kernel_name:
            pass # param_grid["C"] = [float(i) for i in coef0_range.strip().split(",")]

        if "poly" in kernel_name:
            param_grid["coef0"] = [float(i) for i in coef0_range.strip().split(",")]
            param_grid["degree"] = [int(i) for i in degree_range.strip().split(",")]

        if "rbf" in kernel_name:
            param_grid["gamma"] = [float(f) for f in gamma_range.strip().split(",")]

        if "sigmoid" in kernel_name:
            param_grid["coef0"] = [float(i) for i in coef0_range.strip().split(",")]

        #else:
        #    assert False, "Error: Unknown kernel name."

        param_grid["C"] = [float(f) for f in c_range.strip().split(",")]
        param_grid["kernel"] = kernel_name.split(",")
        param_grid = [param_grid]

    else:
        param_grid = {
            "estimator__C":      [float(i) for i in c_range.strip().split(",")],
            "estimator__gamma":  [float(f) for f in gamma_range.strip().split(",")],
            "estimator__degree": [int(i) for i in degree_range.strip().split(",")],
            "estimator__coef0":  [float(f) for f in coef0_range.strip().split(",")],
            "estimator__kernel": [str(s) for s in kernel_name.strip().split(",")]
        }

    return param_grid


def _available_kernels():
    return ["rbf", "linear", "poly", "sigmoid"]


def multi_col_pred_to_int_pred(prediction_matrix):
    """ One vs rest multi column row to a single column row with ints of classes.
    :param prediction_matrix:
    :param names_dict:
    :return:
    """

    # Unfortunately binary and multi-class output arrays are different shapes.
    if len(prediction_matrix.shape) is 1:
        in_row = list(prediction_matrix)
    else:
        in_row = []
        for pred_row in prediction_matrix:

            col_value = -1
            for i in range(len(pred_row)):
                if pred_row[i] == 1:
                    assert col_value < 0, "Error: row contains multiple predictions."
                    col_value = i
            # assert col_value is not None, "Error row must have a prediction."
            in_row.append(col_value)

    return in_row


class BandwidthAction(argparse.Action):

    def __call__(self, parser, namespace, values, option_string=None):
        if values < 12:
            parser.error("Minimum bandwidth for {0} is 12".format(option_string))
            # raise argparse.ArgumentError("Minimum bandwidth is 12")

        setattr(namespace, self.dest, values)


class DefaultListAction(argparse.Action):
    """ This allows a choices like behavior for argparse but combinations of the choice are also valid.
    """
    CHOICES = _available_kernels()

    def __call__(self, parser, namespace, values, option_string=""):
        if values:
            for value in values.strip().split(","):
                if value not in self.CHOICES:
                    message = (
                        "invalid choice: {0!r} (choose from {1})".format(
                            value,
                            ', '.join([repr(action) for action in self.CHOICES])
                        )
                    )
                    raise argparse.ArgumentError(self, message)
            setattr(namespace, self.dest, values)


def _handle_variable_diffs(key_name_list, variable_dict, null_val=""):

    for name in key_name_list:
        if name in variable_dict:
            return variable_dict[name]
    return null_val


def handle_grid_output(cv_results, delimiter="\t"):
    """

    :param cv_results:
    :param delimiter:

    :return:
    """
    not_found_val = "-"

    metrics_out_list = [
        delimiter.join([
            "train_score", "train_std",
            "mean_test_score", "std_test_score",
            "kernel", "C", "coef0", "degree", "gamma"
        ])
    ]

    for train_mean, train_std, test_mean, test_std, params in zip(
            cv_results["mean_train_score"], cv_results["std_train_score"],
            cv_results["mean_test_score"], cv_results["std_test_score"],
            cv_results['params']):
        # print("%0.3f (+/-%0.03f) for %r" % (mean, std * 2, params))

        kernel = _handle_variable_diffs(['kernel', 'estimator__kernel'], params, not_found_val)
        C = str(_handle_variable_diffs(['C', 'estimator__C'], params, not_found_val))
        coef0 = str(_handle_variable_diffs(['coef0', 'estimator__coef0'], params, not_found_val))
        degree = str(_handle_variable_diffs(['degree', 'estimator__degree'], params, not_found_val))
        gamma = str(_handle_variable_diffs(['gamma', 'estimator__gamma'], params, not_found_val))

        metrics_out_list.append(
            delimiter.join([
                "%0.4f" % train_mean, "%0.4f" % train_std,
                "%0.4f" % test_mean, "%0.4f" % test_std,
                kernel, C, coef0, degree, gamma
            ])
        )

    return metrics_out_list


def svm_train(parser):
    """ Preforms k-fold testing followed by independent set testing on a set of training vectors.
        @TODO: It should be possible to generalize this function further. Think about a many vs many.
        1. Get positive set of vectors.
        2. Get a negative set of vectors.
        3. Assign labels to each.

        Ideal behavior
        output performance of each node in the grid.
        final line it the best parameter.
        many-vs-many possible?
        Find the parameters that make a good model and output them, also output model trained from these.
        Grid Search
            k-fold test & optimal parameter search.
        :return:
    """
    # http://stats.stackexchange.com/questions/95797/how-to-split-the-dataset-for-cross-validation-learning-curve-and-final-evaluat
    # http://scikit-learn.org/stable/modules/generated/sklearn.grid_search.GridSearchCV.html#sklearn.grid_search.GridSearchCV
    # http://scikit-learn.org/stable/modules/sgd.html
    # positive_val = 0
    # negative_val = 1

    parser.add_argument('training_vectors',
                        metavar='training_vectors',
                        type=str,
                        nargs='+',
                        help='Files containing vectors for training an SVM.')

    parser.add_argument('--independent-size',
                        dest='independent_size',
                        type=float,
                        default=0.1,
                        help="The percent to include in the test data set.")

    parser.add_argument('--folds',
                        dest='folds',
                        type=int,
                        default=5,
                        help="Number of folds for testing.")

    parser.add_argument('--binary',
                        action="store_true",
                        help="Causes a traditional binary classification to be used. If more than two files are\n" +
                             "passed a one-vs-rest classification is preformed. Additionally this will output\n" +
                             "classes as columns of true or false (0|1) values.\n ")

    parser.add_argument('--seed',
                        dest='seed',
                        type=int,
                        default=0,
                        help="rand seed")

    parser.add_argument('--kernel',
                        dest='kernel',
                        type=str,
                        action=DefaultListAction,
                        metavar="{%s}" % ",".join(_available_kernels()),
                        default=",".join(_available_kernels()),
                        help="Choose one or more kernels for training. Separate names with commas.")

    parser.add_argument('--model',
                        dest='model',
                        type=str,
                        default=False,
                        help="The base name for the model generated from testing.")

    parser.add_argument('--metrics',
                        dest='metrics',
                        type=str,
                        default=False,
                        help="Writes training stars to a given file name. Otherwise metrics are printed to STDOUT.")

    parser.add_argument('--best-metrics',
                        dest='best_metrics',
                        type=str,
                        default=False,
                        help="The name of file to output data about the best metric to. " +
                             "If not provided printed to STOUT.")

    parser.add_argument('--predictions',
                        dest='predictions',
                        type=str,
                        default=False,
                        help="Print confusion matrix of results.")

    parser.add_argument('--C',
                        type=str,
                        required=False,
                        default="0.1,1,10,100,1000",  #
                        help='Optional: A comma separated list of C values to grid search. Must be greater than 0. ')

    parser.add_argument('--gamma',
                        type=str,
                        required=False,
                        default="0.001,0.01,0.1,1,10,100",  # "0.1,5",  #
                        help='Optional: A comma separated list of gamma values for the grid search.')

    parser.add_argument('--coef0',
                        type=str,
                        required=False,
                        default="0.1,1",
                        help='Optional: A comma separated list of coef0 values for the grid search.')

    parser.add_argument('--degree',
                        type=str,
                        required=False,
                        default="1,2,4,6,8",  # "2,4",  #
                        help='Optional: Degree values to grid search. Must be comma separated integers >= 1.')

    _shared_params(parser)

    # @TODO: Implement ability to pass class membership inside file.

    args = parser.parse_known_args()[0]
    from sklearn.model_selection import train_test_split, KFold, GridSearchCV
    from sklearn.svm import SVC
    from sklearn.preprocessing import label_binarize
    from sklearn.multiclass import OneVsRestClassifier
    from collections import OrderedDict

    vector_list = []                  # Stores all class vectors.
    row_id_list = []                  # Stored all row IDs, use for regaining shuffled titles.
    id_list = []                      # Stores all class identities.
    id_number = 0                     # Tells which class id to use, is incremented by one for each class.
    int_to_name_dict = OrderedDict()  # Use this to convert int ids to file names.

    # These handle output of predictions on the independent set test.
    # Thus, they are only used when doing a binary classification with row or column titles.
    # row_testing_labels is especially important as we lose order when spliting and testing.
    row_testing_labels = []      # Stores row titles for predictions on independent test.
    predictions_column_id = []   #

    # Parse matrices and add to vector_list.
    # Also add each rows class identity to id_list.
    for file_name in args.training_vectors:
        # Parse the input.
        matrix_obj = ParseVectors(
            file_name=file_name,
            has_col_names=args.column_titles,
            has_row_names=args.row_titles,
            delimiter=args.delimiter)

        # Add vector values to vector_list and identity labels to id_list.
        for row_id, row_vector in matrix_obj.generate(save_row_names=True):
            vector_list.append(row_vector)
            if args.row_titles:
                row_id_list.append(row_id)
            id_list.append(id_number)

        # Store class integer labels as keys pointing to file/class names so that they
        # are retrievable after classification.
        int_to_name_dict.update({id_number: file_name})

        # Increment for next class.
        id_number += 1

    # Convert to numpy arrays so for scikit-learn
    vector_array = np.array(vector_list)
    id_array = np.array(id_list)

    # Binarize labels in a one-vs-all fashion so one-vs-one and multi-class classifications can be done seamlessly.
    # We can run a multi-class classifications in the same manner. However, we cannot generate some types of analysis
    # plots such as ROC curves and cannot manipulate the score cutoff.

    if args.binary:

        score = "accuracy"
        # Generate lists of parameters to use in the grid search.
        # Multiple kernels can be used and parameter lists can be modified.
        # At the moment it seems kernels will use parameters which do not effect their outputs.
        # e.g. linear using gamma in its grid search. This doesn't cause any errors, but reduced the training speed.
        param_grid = _generate_param_grid(
            kernel_name=args.kernel,
            c_range=args.C,
            gamma_range=args.gamma,
            degree_range=args.degree,
            coef0_range=args.coef0,
            binary=args.binary
        )

        # Transform Integer based IDs into binary vector IDs.
        # e.g. [0, 1, 2,...]  [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        binary_id_array = label_binarize(id_array, classes=list(int_to_name_dict))

        # Split vectors into training and testing sets.
        training_vectors, testing_vectors, training_labels, testing_labels = train_test_split(
            vector_array,     # Vectors
            binary_id_array,  # Labels
            test_size=args.independent_size,
            random_state=args.seed)

        if args.row_titles:
            _, _, row_training_labels, row_testing_labels = train_test_split(
                vector_array,  # Vectors
                row_id_list,   # Labels
                test_size=args.independent_size,
                random_state=args.seed)

        cross_validation_obj = KFold(  # Stratified
            n_splits=args.folds,
            shuffle=True,
            random_state=args.seed
        )

        # Make the classifier object
        # Make a grid search object, with desired ranges and kernels.
        classifier = GridSearchCV(
            estimator=OneVsRestClassifier(SVC()),  # class_weight="balanced"
            scoring=score,
            cv=cross_validation_obj,
            refit=True,
            param_grid=param_grid,
        )

        # Tune the classifier object by fitting training data.
        classifier.fit(training_vectors, training_labels)

        testing_predictions = classifier.decision_function(testing_vectors)
        best_index = classifier.best_index_
        cv_results = classifier.cv_results_
        scorer = classifier.scorer_

        train_splits, test_splits = [], []
        for tmp_train_splits, tmp_test_splits in cross_validation_obj.split(training_labels):
            train_splits.append(tmp_train_splits)
            test_splits.append(tmp_test_splits)

        for i in range(classifier.n_splits_):
            tmp_train_str = "split%d_train_score" % i
            tmp_test_str = "split%d_test_score" % i
            for train_el, test_el in cv_results[tmp_train_str], cv_results[tmp_test_str]:
                print(train_el, test_el)

        exit()
        best_estimator = classifier.best_estimator_.estimator



        if args.predictions:

            preds_matrix_obj = ParseVectors(
                has_col_names=args.column_titles,
                #has_row_names=args.row_titles,
                delimiter=args.delimiter)

            predictions_column_id.append("true_class")
            predictions_column_id.append("model_class")
            predictions_column_id.append("prediction")
            predictions_column_id.append("prediction_score")



            out_file = []
            if len(int_to_name_dict) is 2:
                for i in range(len(testing_predictions)):
                    out_file.append([
                        str(training_labels[i, 0]),
                        str(training_labels[i, 0]),
                        str(testing_predictions[i, 0])])
            else:
                for i in range(len(testing_labels[:, 0])):

                    true_class = None
                    for j in range(len(int_to_name_dict)):  # sorted(int_to_name_dict):
                        if testing_labels[i, j] == 1:
                            true_class = j

                    for j in range(len(int_to_name_dict)):  # sorted(int_to_name_dict):

                        if testing_predictions[i, j] >= 0:
                            tmp_decision = "True"
                        else:
                            tmp_decision = "False"

                        out_file.append([
                            str(true_class),
                            str(j),
                            tmp_decision,
                            str(testing_predictions[i, j])]
                        )

            preds_matrix_obj.out(
                out_file,
                column_titles=predictions_column_id,
                #row_titles=row_testing_labels,
                output_type=args.predictions)

    else:
        score = "accuracy"

        if args.predictions:
            bc.error_quit("ERROR: Prediction scores are only available for binary classifications. Exiting.")

        param_grid = _generate_param_grid(
            kernel_name=args.kernel,
            c_range=args.C,
            gamma_range=args.gamma,
            degree_range=args.degree,
            coef0_range=args.coef0,
            binary=False
        )

        # Make a grid search object, with desired ranges and kernels.
        cross_validation_obj = KFold(  # Stratified
            n_splits=args.folds,
            shuffle=True,
            random_state=args.seed
        )

        classifier = GridSearchCV(
            estimator=SVC(),
            scoring=score,
            cv=cross_validation_obj,
            # refit=True,
            param_grid=param_grid,
        )

        classifier.fit(vector_array, id_array)
        y_preds = classifier.predict(vector_array)

        # p = precision_score(id_array, y_preds, average='macro')
        # p = precision_score(id_array, y_preds, average='micro')
        cm_col_ids = np.array(
            ["actual_classes"] + ["predicted_" + int_to_name_dict[i] for i in sorted(int_to_name_dict)])
        cm_row_ids = np.array(["actual_" + int_to_name_dict[i] for i in sorted(int_to_name_dict)])

        if args.predictions:
            out_preds = []
            for i in range(len(id_array)):
                out_preds.append(args.delimiter.join([
                    int_to_name_dict[id_array[i]].split("/")[-1],
                    str(id_array[i]),
                    str(y_preds[i])]))
            prediction_files = open(args.predictions, "w")
            prediction_files.write("\n".join(out_preds))
            prediction_files.close()

        best_index = classifier.best_index_
        cv_results = classifier.cv_results_
        best_estimator = classifier.best_estimator_

        """
        if len(int_to_name_dict) is 2:
            for class_number in y_preds:
                print(int_to_name_dict[class_number])
        else:
            for class_number in y_preds:
                print(int_to_name_dict[class_number])
        """

    # Output metrics for model.
    metrics_out_list = handle_grid_output(classifier.cv_results_, args.delimiter)
    if args.metrics:
        metrics_file_obj = open(args.metrics, 'w')
        metrics_file_obj.write("\n".join(metrics_out_list))
        metrics_file_obj.close()
    # else:
    #    print("\n".join(metrics_out_list))

    # I am not sure which titles I want to use yet.
    best_metrics = [
        "Model_Name\t%s" % args.model,
        "Best_Test_Accuracy\t%0.4f" % cv_results["mean_train_score"][best_index],
        "Best_Train_Accuracy\t%0.4f" % cv_results["mean_test_score"][best_index],
        "Best_Model_Kernel\t%s" % best_estimator.kernel,
        "Best_Model_C\t%s" % best_estimator.C,
        "Best_Model_Gamma\t%s" % best_estimator.gamma,
        "Best_Model_Epsilon\t%s" % best_estimator.epsilon,
        "Best_Model_Coef0\t%s" % best_estimator.coef0
    ]
    out_str = "\n".join(best_metrics)

    if args.best_metrics:
        out_metrics_file_obj = open(args.best_metrics, 'w')
        out_metrics_file_obj.write(out_str)
        out_metrics_file_obj.close()
    else:
        print(out_str)

    # Finally output the metrics file. I would like to use something other than a pickle, but I can't figure out
    # a good alternative. Also using the standard pickle instead of the sci-it learn as the sci-kit learn version
    # will output many files, whereas the, standard pickle only outputs one.
    # If a model name is provided, output a model file.
    # http://scikit-learn.org/stable/modules/model_persistence.html
    if args.model:
        with open(args.model, 'wb') as fid:
            classifier.best_estimator_.int_to_name_dict = int_to_name_dict
            pickle.dump(classifier.best_estimator_, fid)


def svm_classify(parser):
    """ Predicts the class of a set of unknown vectors using an SVM model.
    :return:
    set_params(\*\*params) 	Set the parameters of this estimator.
    """
    # @TODO: Add support for various methods for inputting models.

    parser.add_argument('unknowns',
                        nargs='*',
                        help='Matrices to add to a base matrix.')

    parser.add_argument("--model",
                        dest="model",
                        type=str,
                        help="At the moment, needs a model file. ")

    parser.add_argument('--binary',
                        action="store_true",
                        help="Causes a traditional binary classification to be used. If more than two files are\n" +
                             "passed a one-vs-rest classification is preformed. Additionally this will output\n" +
                             "classes as columns of true or false (0|1) values.\n ")

    parser.add_argument('--raw-scores',
                        action="store_true",
                        help="")

    parser.add_argument('--binary-scores',
                        action="store_true",
                        help="")

    _shared_params(parser, only_apply_on=True)

    args = parser.parse_args()

    # Get model, for now this will be a pickle, however, I would like to change this to something safer.
    with open(args.model, 'rb') as pickle_file:
        clf = pickle.load(pickle_file)

    out_matrix_obj = ParseVectors(
        file_name="",
        has_col_names=args.column_titles,
        has_row_names=args.row_titles,  # Row titles should just be treated as normal columns.
        delimiter=args.delimiter,
        only_apply_on_columns=None)

    # Since we are generating new columns here we must create the column names instead of parsing them.
    if args.column_titles:
        output_column_titles = []
        if args.row_titles:
            output_column_titles.append(standard_col_title)
        output_column_titles += ["Predicted_Class_ID", "Predicted_Class_Name"]

        out_matrix_obj.setcolumntitles(output_column_titles)

    # Get list of all files to add.
    sources = args.unknowns

    # If a matrix is passed from stdin use this as the base matrix and add other to it.
    # Use the technique below to prevent hanging if no stdin info present.
    # https://repolinux.wordpress.com/2012/10/09/non-blocking-read-from-stdin-in-python/
    while sys.stdin in select([sys.stdin], [], [], 0)[0]:
        if sys.stdin.readable():
            sources.insert(0, "sys.stdin")
        break

    # If no stdin is present, use the first filename passed as the base matrix.
    # Add remaining matrices to the base matrix.
    # Iterate over all input matrices and add them to vector_list, also add each rows class identity to id_list.
    for add_matrix_file_name in sources:
        matrix_obj = ParseVectors(
            add_matrix_file_name,
            has_col_names=args.column_titles,
            has_row_names=args.row_titles,
            delimiter=args.delimiter,
            # only_apply_on_columns=args.only_apply_on
        )

        for row_title, row_vector in matrix_obj.generate():
            # Predict the class of the given vector.

            # This gives boolean values.
            # pred = clf.predict([row_vector])[0]
            # print(pred)
            # This will give actual scores.
            pred = clf.decision_function([row_vector])[0]

            predicted_class_int_id, predicted_class_name = None, None
            cut_off = 0
            for i in range(len(pred)):

                if pred[i] > cut_off:
                    predicted_class_int_id, predicted_class_name = i, clf.int_to_name_dict[i]
                    # Update so that lower positive predictions do not override highest pred.
                    cut_off = pred[i]

            out_vec = [
                predicted_class_int_id,                       # The integer id of the class.
                predicted_class_name  # The text name of the class.
            ]
            # out_vec = []
            # out_vec = [str(i) for i in pred[0]]
            out_matrix_obj.iterative_out(
                row_title=row_title,
                vector=out_vec,
                column_titles=out_matrix_obj.getcolumntitles(),
            )



def linear_regression(parser):
    """ Preforms linear regression via least squares on a set of vectors.

    :param parser:
    :return:
    """
    from sklearn import datasets, linear_model

    parser.add_argument('matrix',
                        nargs='?',
                        type=str,
                        default="sys.stdin",
                        help='matrix with training set. Last column has to be the target values.\
                         The others are training sets.')

    parser.add_argument('-p', '--prediction-set',
                        type=str,
                        help="Path to prediction set vectors.")

    parser.add_argument('-c', "--column_titles",
                        action="store_true",
                        help='column titles are defined')

    parser.add_argument('-r', "--row_titles",
                        action="store_true",
                        help='row titles are defined')

    parser.add_argument("--fast",
                        action="store_true",
                        help='As fast as it could be')

    parser.add_argument('-n', "--normalize",
                        action="store_true",
                        help='If the switch is set the values are normalized before the linear regression')

    parser.add_argument('-o', "--output-coefficients",
                        action="store_true",
                        help='write estimated coefficients on STDERR')

    args = parser.parse_args()
    matrix, column_titles, row_titles, m_type = vecparse(
        args.matrix, args.column_titles, args.row_titles)

    prediction, column_titles2, row_titles2, m_type2 = vecparse(
        args.prediction_set, args.column_titles, args.row_titles)

    training = matrix[:, :-1]
    target = matrix[:, -1]
    n = 1
    if args.fast:
        n = -1

    regr = linear_model.LinearRegression(normalize=args.normalize, n_jobs=n)
    regr.fit(training, target)

    if args.output_coefficients:
        import sys
        sys.stderr.write("Interception:\t")
        sys.stderr.write(str(regr.intercept_))
        sys.stderr.write("\nCoefficients:\t")
        sys.stderr.write(str(regr.coef_))
        sys.stderr.write("\n")

    output = np.zeros((prediction.shape[0], prediction.shape[1] + 1))
    output[:, :-1] = prediction
    output[:, -1] = regr.predict(prediction)

    outputvector(output, column_titles, row_titles)


def neural_network():
    """
    :return:
    """
    pass


def random_forest():
    """
    :return:
    http://blog.yhat.com/posts/python-random-forest.html
    """
    pass


def naive_bayes():
    """

    :return:
    """
    pass


def decision_trees():
    """

    :return:
    """
    pass


# ValueError: 'matthews_corrcoef' is not a valid scoring value. Valid options are [
# 'accuracy', 'adjusted_rand_score', 'average_precision', 'f1', 'f1_macro', 'f1_micro', 'f1_samples',
# 'f1_weighted', 'neg_log_loss', 'neg_mean_absolute_error', 'neg_mean_squared_error',
# 'neg_median_absolute_error', 'precision', 'precision_macro', 'precision_micro', 'precision_samples',
# 'precision_weighted', 'r2', 'recall', 'recall_macro', 'recall_micro', 'recall_samples',
# 'recall_weighted', 'roc_auc']
# http://stackoverflow.com/questions/12632992/gridsearch-for-an-estimator-inside-a-onevsrestclassifier
# http://pyml.sourceforge.net/doc/howto.pdf
# ROC curve.
# Confusion matrix.
# http://scikit-learn.org/stable/auto_examples/svm/plot_rbf_parameters.html
"""
fpr = dict()
tpr = dict()
# ----------------- True and False positives -------------------
if len(int_to_name_dict) is 2:
    fpr[0], tpr[0], _ = roc_curve(y_test, y_score)
    # roc_auc = auc(fpr, tpr)
else:
    for i in sorted(int_to_name_dict):
        fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])

longest_list = 0
for el in tpr:
    if len(tpr[el]) > longest_list:
        longest_list = len(tpr[el])

true_and_false_pos_rates = [[] for i in range(longest_list)]

for i in range(longest_list):
    for j in range(len(tpr)):
        try:
            f = str(round(fpr[j][i], args.roundto))
            t = str(round(tpr[j][i], args.roundto))
        except IndexError:
            f = "1.0"
            t = "1.0"
        true_and_false_pos_rates[i].append(f)
        true_and_false_pos_rates[i].append(t)

true_and_false_pos_rates_out_arr = []
for i in range(longest_list):
    true_and_false_pos_rates_out_arr.append(args.delimiter.join(true_and_false_pos_rates[i]))

# if args.best_pos_rates:
#    out_metrics_file_obj = open(args.best_pos_rates, 'w')
#    out_metrics_file_obj.write("\n".join(true_and_false_pos_rates_out_arr))
#    out_metrics_file_obj.close()
# else:
#    print("\n".join(true_and_false_pos_rates_out_arr))

grid_scores_ : list of named tuples
Contains scores for all parameter combinations in param_grid. Each entry corresponds to one parameter setting.
Each named tuple has the attributes:
        parameters, a dict of parameter settings
        mean_validation_score, the mean score over the cross-validation folds
        cv_validation_scores, the list of scores for each fold

    for el in classifier.cv_results_:
        mean_of_accuracy_score = round(el[1], args.roundto)
        tmp_metrics_out_list = ["mean_of_accuracy_score:%s" % str(mean_of_accuracy_score)]
        for key_el in el[0]:
            tmp_metrics_out_list.append(key_el+":%s" % el[0][key_el])
        metrics_out_list.append("\t".join(tmp_metrics_out_list))
"""
# estimator = SVC()
# classifier = OneVsRestClassifier(
#    estimator=estimator,
#    #scoring=score,
#    #cv=cross_validation_obj,
#    #param_grid=param_grid
# )
# classifier.fit(x_train, y_train)
# for el in classifier.grid_scores_:
# print(classifier.cv_results_.keys())
# mean_of_accuracy_score = round(classifier.cv_results_["mean_test_score"], ROUNDTO)

"""

print(__doc__)

import numpy as np
import matplotlib.pyplot as plt
from itertools import cycle

from sklearn import svm, datasets
from sklearn.metrics import roc_curve, auc
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import label_binarize
from sklearn.multiclass import OneVsRestClassifier
from scipy import interp

# Import some data to play with
iris = datasets.load_iris()
X = iris.data
y = iris.target

# Binarize the output
y = label_binarize(y, classes=[0, 1, 2])
n_classes = y.shape[1]

# Add noisy features to make the problem harder
random_state = np.random.RandomState(0)
n_samples, n_features = X.shape
X = np.c_[X, random_state.randn(n_samples, 200 * n_features)]

# shuffle and split training and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.5,
                                                    random_state=0)

# Learn to predict each class against the other
classifier = OneVsRestClassifier(
     svm.SVC(
         kernel='linear',
         probability=True,
         random_state=random_state
     )
)
y_score = classifier.fit(X_train, y_train).decision_function(X_test)


print(y_test[:, 0])
print(y_score[:, 0])


# Compute ROC curve and ROC area for each class
fpr = dict()
tpr = dict()
roc_auc = dict()
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_test[:, i], y_score[:, i])
    roc_auc[i] = auc(fpr[i], tpr[i])

# Compute micro-average ROC curve and ROC area
#fpr["micro"], tpr["micro"], _ = roc_curve(y_test.ravel(), y_score.ravel())
#roc_auc["micro"] = auc(fpr["micro"], tpr["micro"])


plt.figure()
lw = 2
plt.plot(
    fpr[0],
    tpr[0],
    color='darkorange',
    lw=lw,
    label='ROC curve (area = %0.2f)' % roc_auc[0]
)
plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver operating characteristic example')
plt.legend(loc="lower right")
plt.show()

# Make training and test classes.
# x_train, x_test, y_train, y_test = train_test_split(
#    vector_array,  # Vectors
#    id_array,      # Labels
#    test_size=args.independent_size,
#    random_state=0)
"""


