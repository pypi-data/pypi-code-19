from caserec.utils.cross_fold_validation import CrossFoldValidation

from caserec.evaluation.statistical_analysis import StatisticalAnalysis

from caserec.evaluation.rating_prediction import RatingPredictionEvaluation

from caserec.recommenders.rating_prediction.matrixfactorization import MatrixFactorization
from caserec.recommenders.rating_prediction.msmf import MSMF

# dir_dataset = "C:/Users/forte/OneDrive/msmf/datasets/filmtrust/"
# dir_dataset = "C:/Users/forte/OneDrive/msmf/datasets/ciaodvd/"
# dir_dataset = "C:/Users/forte/OneDrive/msmf/datasets/yahoo_movies/"
# dir_dataset = "C:/Users/forte/OneDrive/msmf/datasets/movielens/"
# dir_dataset = "C:/Users/forte/OneDrive/msmf/datasets/amazon/"
dir_dataset = "C:/Users/forte/OneDrive/msmf/datasets/booking_crossing/"

# CrossFoldValidation(input_file=dir_dataset + "user_rated_books_reduce.dat", dir_folds=dir_dataset).execute()


for f in range(10):
    fold_dir = dir_dataset + "folds/" + str(f) + "/"
    training_file = fold_dir + "train.dat"
    test_file = fold_dir + "test.dat"
    mf_file = fold_dir + "predict_mf.dat"
    msmf_file = fold_dir + "predict_msmf.dat"

    MatrixFactorization(training_file, test_file, prediction_file=mf_file, baseline=True).execute()
    MSMF(training_file, test_file, prediction_file=msmf_file, min_feedback=20, baseline=True,
         similarity_metric='correlation').execute()


# Evaluation

# msmf = RatingPredictionEvaluation().folds_evaluation(dir_dataset + 'folds/', n_folds=10,
#                                                      name_prediction="predict_msmf.dat", name_test="test.dat")
# mf = RatingPredictionEvaluation().folds_evaluation(dir_dataset + 'folds/', n_folds=10,
#                                                      name_prediction="predict_mf.dat", name_test="test.dat")


# msmf = RatingPredictionEvaluation().folds_evaluation_item_cold_start(dir_dataset + 'folds/', n_folds=10,
#                                                      name_prediction="predict_msmf.dat", name_test="test.dat", min_feedback=15)
# mf = RatingPredictionEvaluation().folds_evaluation_item_cold_start(dir_dataset + 'folds/', n_folds=10,
#                                                      name_prediction="predict_mf.dat", name_test="test.dat", min_feedback=15)

# print("RMSE MF:: ", mf[0], " RMSE MSMF::", msmf[0])
# StatisticalAnalysis(mf[2], msmf[2]).wilcoxon()

# print("MAE MF:: ", mf[3], " MAE MSMF::", msmf[3])
# StatisticalAnalysis(mf[5], msmf[5]).wilcoxon()
