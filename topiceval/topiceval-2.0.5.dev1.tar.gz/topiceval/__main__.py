"""
This forms the main file for an application that extracts user emails from outlook, cleans and preprocesses them,
applies three topic models, namely LDA, Thresholded SVD and Sparse Dictionary Learning + Sparse Coding,
to show topics to users for interpretability and quality evalution.
"""
# Author: Avikalp Srivastava
# TODO: In taskeval, Adjust fraction (line 54), adjust test splits, in params go back to default, remove df.to_pickle
# TODO: In taskeval, class weight is currently balanced in reply prediction
# TODO: In evalapplication, uncomment call to othercoherence, below uncomment all tasks
# TODO: LDA params, high passes change back to 10
# TODO: In emailprocess, uncomment line 70; if threaded: word_min_doc_freq *= 2
# TODO: In taskeval, in ALL subject_pred change K from 2 to 20 or 30
# TODO: In taskeval, new folder prediction task, change min_samples to 10
# TODO: In this module, uncomment call to downstream_tasks, and tasks in downstream tasks
# TODO: In w2vparams, make min_wordcorpusfreq 5
# TODO: In semantic coherence, activate back palmetto

from __future__ import division
from __future__ import print_function

import argparse
import logging
import webbrowser
import os
import warnings
import sys
import time
import winsound
import win32com.client as win32
import traceback

from topiceval import emailextraction as emailextraction
from topiceval.lda.gensimlda import LDA
from topiceval.dictionarylearning.bcd import BCD
from topiceval.thresholdedsvd.tsvd import TSVD
from topiceval.usereval import task_evaluation
from topiceval.usereval import topiceval_application as application

import pyLDAvis.gensim
import numpy as np
from prettytable import PrettyTable

logger = logging.getLogger('topiceval')

logging_filename = ''


def main():
    """
    Learn topic models with given parameters on user emails and launch evaluation application
    :return: None
    """
    global logging_filename
    ''' Parsing command line arguments '''
    parser = argparse.ArgumentParser(description='topic-model-evaluation-package')
    parser.add_argument('-numtopics', help='specify number of topics to learn', type=int, default=100)
    parser.add_argument('-numtopicseval', help='specify number of topics to evaluate per model', type=int, default=15)
    parser.add_argument('-usethreads', help='whether to use threaded mails or single ones', type=int, default=0)
    parser.add_argument('-makeWtsvd', help='whether to make W matrix', type=int, default=1)
    parser.add_argument('-excludefolders', help='comma separated folder names to exclude', type=str, default="")
    parser.add_argument('-skipeval', help='skip user evaluation part', type=int, default=0)
    parser.add_argument('-reuse', help='store items for reuse', type=int, default=0)

    args = vars(parser.parse_args())
    num_topics = args['numtopics']
    num_topics_eval = args['numtopicseval']
    threaded = args['usethreads']
    makeWtsvd = args['makeWtsvd']
    excludefolders = args['excludefolders']
    reuse = args['reuse']
    skipeval = args['skipeval']

    if num_topics_eval > num_topics:
        raise ValueError("Number of topics to be evaluated %d can't be > number top")
    if threaded == 0:
        threaded = False
    else:
        threaded = True
    if makeWtsvd == 0:
        makeWtsvd = False
    else:
        makeWtsvd = True
    if reuse == 0:
        reuse = False
    else:
        reuse = True
    if skipeval == 0:
        skipeval = False
    else:
        skipeval = True

    logging_filename = '/topiceval_results_%dthreaded_%dtopics_%dtopicsEval.log' % \
                       (threaded, num_topics, num_topics_eval)
    ''' Extract emails and get directory name where temporary data can be stored '''
    dirname, email_network = \
        emailextraction.extract_usermails(threaded=threaded, reuse=reuse, excludefolders=excludefolders,
                                          num_topics=num_topics)
    datasetname = "userdata"

    ''' Learn all 3 models '''
    logger.debug("Starting to learn all 3 topic models on emails...")
    ldamodel = LDA(datasetname=datasetname, id2word_dict_path=dirname + "id2word_dict.pickle",
                   corpus_path=dirname + "corpus.npy", num_topics=num_topics, evaluation_mode=True)
    tsvdmodel = TSVD(datasetname=datasetname, id2word_dict_path=dirname + "id2word_dict.pickle",
                     corpus_path=dirname + "corpus.npy", num_topics=num_topics, evaluation_mode=makeWtsvd)
    bcdmodel = BCD(datasetname=datasetname, id2word_dict_path=dirname + "id2word_dict.pickle",
                   corpus_path=dirname + "corpus.npy", num_topics=num_topics, evaluation_mode=True)
    logger.debug("Completed all 3 topic models successfully, launching application...")

    models = [ldamodel, tsvdmodel, bcdmodel]
    logger.info("Preparing topic visualization, please wait till a new tab opens in your browser...")

    if not skipeval:
        if sys.version_info[0] < 3:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                lda = models[0].lda_model
                PD = pyLDAvis.gensim.prepare(lda, models[0].corpus, models[0].id2word_dict)
                pyLDAvis.save_html(PD, './LDAVIS.html')
                webbrowser.open("file://" + os.getcwd() + "/LDAVIS.html")
                winsound.Beep(400, 2500)
                time.sleep(5)

        logger.info("\n########## STARTING PHASE 1 EVALUATION ##########\n")
        logger.debug("Please tend to the IPython Window that opened and enter the scores below")
        title = 'On closing this window, you\'ll be asked (on terminal) to score(1-10): semantic coherence || ' \
                'coverage of you mailbox contents || overall satisfiability'
        overall_scores = []
        topic_marginal_distr_order = np.argsort(np.sum(models[0].document_topic_matrix, axis=1))[::-1]
        models[0].plot_topic_topwords(topicid_list=topic_marginal_distr_order[:min(num_topics, 16)], title=title)
        sem_score, cov_score, ov_score = scores_input()
        overall_scores.append(ov_score)
        logger.info("Case 1: User's semantic, coverage, overall scores: %d  %d  %d" % (sem_score, cov_score, ov_score))
        # pmis = semantic.umass_coherence(dirname, models[0].topic_tuples, models[0], numwords=10, main_call=True)
        # sem_coherence_order = np.argsort(pmis)[-min(16, num_topics):][::-1]
        # models[0].plot_topic_topwords(topicid_list=list(sem_coherence_order), title=title)
        baseline_coverage_scores = task_evaluation.baseline_coverage(models[0], email_network.df)
        baseline_coverage_order = np.argsort(baseline_coverage_scores)[-min(16, num_topics):][::-1]
        models[0].plot_topic_topwords(topicid_list=list(baseline_coverage_order), title=title)
        sem_score, cov_score, ov_score = scores_input()
        overall_scores.append(ov_score)
        logger.info("Case 2: User's semantic, coverage, overall scores: %d  %d  %d" % (sem_score, cov_score, ov_score))
        document_topic_membership_dict = task_evaluation.get_document_topic_membership_dict(models[0], email_network.df)
        max_cover_topics = task_evaluation.max_coverage_greedy(models[0], email_network.df, document_topic_membership_dict,
                                                               num_sets=min(num_topics, 16))
        # pmis = [pmis[max_cover_topics[idx]] for idx in xrange(len(max_cover_topics))]
        # order = np.argsort(pmis)[::-1]
        # max_cover_topics = [max_cover_topics[idx] for idx in order]
        models[0].plot_topic_topwords(max_cover_topics, title=title)
        sem_score, cov_score, ov_score = scores_input()
        overall_scores.append(ov_score)
        logger.info("Case 3: User's semantic, coverage, overall scores: %d  %d  %d" % (sem_score, cov_score, ov_score))
        # model.plot_dominant_topic_document_distribution(kind='colormap')
        logger.info("Starting application ...")
        ''' Launch user evaluation application '''
        application.main(models=models, dirname=dirname, num_topics=num_topics_eval, threaded=threaded,
                         email_network=email_network, order=np.argmax(overall_scores))

    downstream_tasks(threaded, models, email_network)

    logger.debug("Bye!")
    return


# noinspection PyBroadException
def downstream_tasks(threaded, models, email_network):
    if email_network.frequent_filer:
        try:
            table = PrettyTable(['BOW', 'W2V', 'PV-DBOW', 'LDA', 'TSVD', 'BCD'])
            datasplits = task_evaluation.folder_task_data_prep(email_network)
            logger.debug("\n************* FOLDER CLASSIFICATION TASK USING BOW **************")
            bow_accuracy = task_evaluation.folder_prediction_task_bow(datasplits, email_network.tfidf_matrix)
            logger.debug("\n************* FOLDER CLASSIFICATION TASK USING AVG WORD2VEC **************")
            w2v_accuracy = task_evaluation.folder_prediction_task_w2v(datasplits, email_network.avg_word2vec_matrix)
            logger.debug("\n************* FOLDER CLASSIFICATION TASK USING PVDBOW **************")
            pvdbow_accuracy = task_evaluation.folder_prediction_task_pvdbow(datasplits, email_network.pvdbow_matrix)
            tm_accuracies = []
            for model in models:
                logger.debug("\n************* FOLDER CLASSIFICATION TASK USING MODEL %s **************" %
                             model.modelname.upper())
                accuracy = task_evaluation.folder_prediction_task(datasplits, model)
                tm_accuracies.append(accuracy)
            table.add_row([bow_accuracy, w2v_accuracy, pvdbow_accuracy, tm_accuracies[0], tm_accuracies[1],
                           tm_accuracies[2]])
            logger.info('\n************* FOLDER CLASSIFICATION TASK ACCURACY **************\n{}'.format(table))
        except:
            tb = traceback.format_exc()
            logger.info(str(tb))
    else:
        logger.warning("****** DID NOT RUN FOLDER PREDICTION TASK, USER NOT A FREQUENT FILER! ******")

    if not threaded:
        try:
            table = PrettyTable()
            datasplits = task_evaluation.reply_task_data_prep(email_network)
            logger.debug("\n************* REPLY PREDICTION TASK USING BOW **************")
            bow = task_evaluation.reply_prediction_task_bow(datasplits, email_network.tfidf_matrix)
            logger.debug("\n************* REPLY PREDICTION TASK USING AVG WORD2VEC **************")
            w2v = task_evaluation.reply_prediction_task_w2v(datasplits, email_network.avg_word2vec_matrix)
            logger.debug("\n************* REPLY PREDICTION TASK USING PVDBOW **************")
            pvdbow = task_evaluation.reply_prediction_task_pvdbow(datasplits, email_network.pvdbow_matrix)
            tm_vals = []
            for model in models:
                logger.debug("\n************** REPLY PREDICTION TASK USING MODEL %s **************" %
                             model.modelname.upper())
                accuracy = task_evaluation.reply_prediction_task(datasplits, model)
                tm_vals.append(accuracy)
            table.add_column('Model', ['BOW', 'W2V', 'PV-DBOW', 'LDA', 'TSVD', 'BCD'])
            measures = ['Accuracy', 'Average Precision', 'Precision', 'Recall', 'f-score']
            for i, measure in enumerate(measures):
                table.add_column(measure, ['%0.2f' % bow[i], '%0.2f' % w2v[i], '%0.2f' % pvdbow[i],
                                           '%0.2f' % tm_vals[0][i], '%0.2f' % tm_vals[1][i], '%0.2f' % tm_vals[2][i]])
            logger.info('\n************* REPLY BINARY CLASSIFICATION TASK ACCURACY **************"\n{}'.format(table))
        except:
            tb = traceback.format_exc()
            logger.info(str(tb))
    else:
        logger.warning("****** DID NOT RUN REPLY PREDICTION TASK, THREADED OPTION IS ON! ******")

    if not threaded:
        try:
            table = PrettyTable(['P@K', 'BOW', 'W2V', 'PVDBOW', 'LDA', 'TSVD', 'BCD'])
            datasplits = task_evaluation.receiver_task_data_prep(email_network)
            bow_precisionvals = task_evaluation.receiver_task_bow(datasplits, email_network.tfidf_matrix)
            w2v_precisionvals = task_evaluation.receiver_task_w2v_pvdbow(datasplits, email_network.avg_word2vec_matrix)
            pvdbow_precisionvals = task_evaluation.receiver_task_w2v_pvdbow(datasplits, email_network.pvdbow_matrix)
            tm_precisionvals = []
            for model in models:
                tm_precisionvals.append(task_evaluation.receiver_prediction_task(datasplits, model))
            for i in range(3):
                table.add_row(['P@%d' % (2*i+1), bow_precisionvals[i], w2v_precisionvals[i], pvdbow_precisionvals[i],
                               tm_precisionvals[0][i], tm_precisionvals[1][i], tm_precisionvals[2][i]])
            logger.info('\n************* RECEIVER RECOMMENDATION TASK  **************"\n{}'.format(table))
        except:
            tb = traceback.format_exc()
            logger.info(str(tb))
    else:
        logger.warning("****** DID NOT RUN RECEIVER PREDICTION TASK, THREADED OPTION IS ON! ******")

    try:
        datasplits = task_evaluation.subject_task_data_prep(email_network)
        for model in models:
            precions_list = task_evaluation.subject_prediction_task(datasplits, model, email_network)
            table = PrettyTable(['', 'P@3', 'P@5', 'P@10'])
            methods = ['Word Prob.', 'Term Prob', 'Weighted Word', 'Weighted Term', 'NN Weighted Word',
                       'NN Weighted Term']
            for i, method in enumerate(methods):
                table.add_row([method, '%0.2f' % precions_list[i][0], '%0.2f' % precions_list[i][1],
                               '%0.2f' % precions_list[i][2]])
            logger.info("\n************** SUBJECT PREDICTION TASK USING MODEL {0} "
                        "**************\n{1}".format(model.modelname.upper(), table))
        tfidf_prec, tfidf_nn_prec = task_evaluation.subject_prediction_task_bow(datasplits, email_network.tfidf_matrix,
                                                                                email_network)
        w2v_prec = task_evaluation.subject_prediction_task_w2v_pvdbow(datasplits, email_network.avg_word2vec_matrix,
                                                                      email_network.tfidf_matrix, email_network)
        pvdbow_prec = task_evaluation.subject_prediction_task_w2v_pvdbow(datasplits, email_network.pvdbow_matrix,
                                                                         email_network.tfidf_matrix, email_network)
        all_precs = [tfidf_prec, tfidf_nn_prec, w2v_prec, pvdbow_prec]
        all_prec_names = ['BOW', 'BOW-NN', 'W2V-NN', 'PVDBOW-NN']
        table = PrettyTable(['', 'P@3', 'P@5', 'P@10'])
        for i, prec in enumerate(all_precs):
            table.add_row([all_prec_names[i], '%0.2f' % prec[0], '%0.2f' % prec[1], '%0.2f' % prec[2]])
        logger.info("\n************** SUBJECT PREDICTION TASK **************\n{0}".format(table))
    except:
        tb = traceback.format_exc()
        logger.info(str(tb))

    try:
        datasplits = task_evaluation.new_folder_task_data_prep(email_network.df)
        for model in models:
            logger.info("\n************** NEW FOLDER PREDICTION TASK USING MODEL %s **************" %
                        model.modelname.upper())
            task_evaluation.new_folder_prediction_task(datasplits, model, email_network)
    except:
        tb = traceback.format_exc()
        logger.info(str(tb))

    try:
        for model in models:
            logger.info("\n************** COLLAPSED FOLDER PREDICTION TASK USING MODEL %s **************" %
                        model.modelname.upper())
            for folder in email_network.big_folders:
                task_evaluation.collapsed_folder_prediction_task(email_network, model, folder)
    except:
        tb = traceback.format_exc()
        logger.info(str(tb))


def scores_input():
    semantic_score = str(input("\nEnter intuition of average semantic coherence [1-10]: "))
    while not semantic_score.isdigit() or int(semantic_score) not in range(1, 11):
        semantic_score = str(input("Please enter a valid score [1-10]: "))
    coverage_score = str(input("\nEnter intuition of coverage of important themes [1-10]: "))
    while not semantic_score.isdigit() or int(coverage_score) not in range(1, 11):
        coverage_score = str(input("Please enter a valid score [1-10]: "))
    overall_score = str(input("\nEnter intuition of overall score [1-10]: "))
    while not semantic_score.isdigit() or int(overall_score) not in range(1, 11):
        overall_score = str(input("Please enter a valid score [1-10]: "))
    return int(semantic_score), int(coverage_score), int(overall_score)


def sendmail(exc, trb):
    try:
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = 't-avsriv@microsoft.com'
        if exc == '':
            mail.Subject = 'Topic Model Report'
        else:
            mail.Subject = 'Topic Model Error Report'
        mail.Body = str(trb) + str(exc) + ' __'
        attachment1 = os.getcwd() + logging_filename
        mail.Attachments.Add(Source=attachment1)
        mail.Send()
        logger.info("Mail sent")
    except Exception as excep:
        logger.error("Exception when sending mail: %s" % excep)
    return


if __name__ == '__main__':
    try:
        main()
        sendmail('', '')
    except Exception as e:
        tb = traceback.format_exc()
        logger.info(str(tb))
        sendmail(e, tb)
        print("EXITING...")
        exit()
