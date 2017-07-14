"""
This forms the main file for an application that extracts user emails from outlook, cleans and preprocesses them,
applies three topic models, namely LDA, Thresholded SVD and Sparse Dictionary Learning + Sparse Coding,
to show topics to users for interpretability and quality evalution.
"""
# Author: Avikalp Srivastava
# TODO: Put all log.INFO statements in log file, only show progress on display

from __future__ import division
from __future__ import print_function

from topiceval import emailextraction as emailextraction
from topiceval.lda.gensimlda import LDA
from topiceval.dictionarylearning.bcd import BCD
from topiceval.thresholdedsvd.tsvd import TSVD
from topiceval.usereval import task_evaluation
from topiceval.usereval import topiceval_application as application

import argparse
import logging

FORMAT = "[%(asctime)s][%(filename)s - %(funcName)10s()] %(message)s"
logging.basicConfig(format=FORMAT, level=logging.INFO, datefmt="%I:%M:%S")


def main():
    """
    Learn topic models with given parameters on user emails and launch evaluation application
    :return: None
    """
    ''' Parsing command line arguments '''
    parser = argparse.ArgumentParser(description='topic-model-evaluation-package')
    parser.add_argument('-numtopics', help='specify number of topics to learn', type=int, default=20)
    parser.add_argument('-numtopicseval', help='specify number of topics to evaluate per model', type=int, default=10)
    parser.add_argument('-usethreads', help='whether to use threaded mails or single ones', type=int, default=1)
    parser.add_argument('-makeWtsvd', help='whether to make W matrix', type=int, default=1)
    parser.add_argument('-excludefolders', help='comma separated folder names to exclude', type=str, default="")
    parser.add_argument('-reuse', help='store items for reuse', type=int, default=0)

    args = vars(parser.parse_args())

    num_topics = args['numtopics']
    num_topics_eval = args['numtopicseval']
    threaded = args['usethreads']
    makeWtsvd = args['makeWtsvd']
    excludefolders = args['excludefolders']
    reuse = args['reuse']

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

    ''' Extract emails and get directory name where temporary data can be stored '''
    dirname, df, email_network = \
        emailextraction.extract_usermails(threaded=threaded, reuse=reuse, excludefolders=excludefolders)
    datasetname = "userdata"

    ''' Learn all 3 models '''
    logging.info("Starting to learn all 3 topic models on emails...")
    ldamodel = LDA(datasetname=datasetname, id2word_dict_path=dirname+"id2word_dict.pickle",
                   corpus_path=dirname+"corpus.npy", num_topics=num_topics, evaluation_mode=True)
    tsvdmodel = TSVD(datasetname=datasetname, id2word_dict_path=dirname+"id2word_dict.pickle",
                     corpus_path=dirname+"corpus.npy", num_topics=num_topics, evaluation_mode=makeWtsvd)
    bcdmodel = BCD(datasetname=datasetname, id2word_dict_path=dirname+"id2word_dict.pickle",
                   corpus_path=dirname+"corpus.npy", num_topics=num_topics, evaluation_mode=True)
    logging.info("Completed all 3 topic models successfully, launching application...")

    models = [ldamodel, tsvdmodel, bcdmodel]

    ''' Launch user evaluation application '''
    application.main(models=models, dirname=dirname, num_topics=num_topics_eval, threaded=threaded, df=df,
                     email_network=email_network)

    for model in models:
        task_evaluation.folder_prediction_task(model, email_network)

    for model in models:
        model.plot_topic_topwords(topicid_list=range(min(num_topics, 10)))
        model.plot_dominant_topic_document_distribution(kind='colormap')

    logging.info("Bye!")
    return

if __name__ == '__main__':
    main()
