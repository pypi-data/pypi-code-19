"""
This module use the win32com.client library for python to extract user emails
from outlook and organize them in a pandas dataframe structure.
"""

from __future__ import division
from __future__ import print_function

from topiceval.preprocessing import textcleaning
import topiceval.preprocessing.emailsprocess as emailprocess

import pandas as pd

import win32com.client
import multiprocessing as mp
import os
import logging


def extract_usermails(threaded, excludefolders, usenltk):
    """
    Extract mails from inbox, store as a dataframe and return the directory name and the dataframe.

    The steps followed are:

    1. Make a data directory at current location to store temporary data

    2. Extract user mails from outlook using win32.client API. Always extracts from inbox and sent_items,
        additional folders can be mentioned via command-line. These are stored in a dataframe with
        associated metadata information that will be used to derive email importance measure at a later
        stage.

    3. If threaded option is True, then from all mails belonging to a single mail thread, only
        the largest is retained and the rest are discarded.
        If threaded is False, then previous conversation content is removed from all mails, maintaining
        only the most recent message in the extracted mail => all mails in a conversation form separate
        docs

    4. Signature Removal: Some common phrases that form signatures are removed

    5. The clean_text() function of textcleaning.py module is applied. It tokenizes text, removes special
        characters, identifies metadata info, url's, email addresses, numbers, money figures, weekdays etc.,
        along with additional option of lemmatization. Some effort is made to remove template text by removing
        information that folllows multiple special character of the same kind (like --------)

    6. Phrase Detection: Gensim's phrase detection module is used to form bigrams # TODO: Trigrams etc

    7. Next step is removal of stopwords. The popular extended list of stopwords available online is used
        for this task since we aim at removal of topically poor words.

    Parameters
    ----------
    :param threaded: bool, if True, treats threaded conversation as a single document
    :param excludefolders: string, comma separated list of extra folders to exclude
    :param usenltk: bool, whether to use nltk's lemmatization. Requires nltk wordnet download

    :return: string, pandas.DataFrame corresponding to the directory path to store temporary data
        and dataframe holding user's email information
    """
    ''' Make data directory at current location for temporary storage of data '''
    dirname = make_user_dir()
    ''' Get email items from inbox, sent_items and any extrafolders mentioned through command line
        Currently configured to use 2 processes for parallel extraction of mails from inbox and sent mails
        extrafolders are traversed serially '''
    # TODO: Turn on multiprocessing after sufficient testing and benchmarking
    items = extract(excludefolders, use_multiprocessing=False)
    df = makedf(items, threaded, usenltk)
    # emails_dict = make_emails_dict(df)
    emailprocess.make_doc2bow(df, dirname)
    return dirname


def encodeit(s):
    if isinstance(s, str):
        return (s.encode('utf-8')).decode('utf-8')
    else:
        return s


def extract_helper(messages, folder_type, items):
    message = messages.GetFirst()
    while message:
        try:
            d = dict()
            d['Subject'] = encodeit(getattr(message, 'Subject', '<UNKNOWN>'))
            d['SentOn'] = encodeit(getattr(message, 'SentOn', '<UNKNOWN>'))
            d['SenderName'] = encodeit(getattr(message, 'SenderName', '<UNKNOWN>'))
            d['CC'] = encodeit(getattr(message, 'CC', '<UNKNOWN>'))
            d['BCC'] = encodeit(getattr(message, 'BCC', '<UNKNOWN>'))
            d['To'] = encodeit(getattr(message, 'To', '<UNKNOWN>'))
            d['Body'] = encodeit(getattr(message, 'Body', '<UNKNOWN>'))
            d['ConversationID'] = encodeit(getattr(message, 'ConversationID', '<UNKNOWN>'))
            d['ConversationIndex'] = encodeit(getattr(message, 'ConversationIndex', '<UNKNOWN>'))
            d['FolderType'] = folder_type
            if d['SentOn'] != '<UNKNOWN>' and d['ConversationID'] != '<UNKNOWN>':
                items.append(d)
        except Exception as inst:
            print("Error processing mail", inst)

        message = messages.GetNext()
    return items


def extract_helper_mp(folder_num, folder_type):
    items = []
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    messages = outlook.GetDefaultFolder(folder_num).Items
    message = messages.GetFirst()
    while message:
        try:
            d = dict()
            d['Subject'] = encodeit(getattr(message, 'Subject', '<UNKNOWN>'))
            d['SentOn'] = str(encodeit(getattr(message, 'SentOn', '<UNKNOWN>')))
            d['SenderName'] = encodeit(getattr(message, 'SenderName', '<UNKNOWN>'))
            d['CC'] = encodeit(getattr(message, 'CC', '<UNKNOWN>'))
            d['BCC'] = encodeit(getattr(message, 'BCC', '<UNKNOWN>'))
            d['To'] = encodeit(getattr(message, 'To', '<UNKNOWN>'))
            d['Body'] = encodeit(getattr(message, 'Body', '<UNKNOWN>'))
            d['ConversationID'] = encodeit(getattr(message, 'ConversationID', '<UNKNOWN>'))
            d['ConversationIndex'] = encodeit(getattr(message, 'ConversationIndex', '<UNKNOWN>'))
            d['FolderType'] = folder_type
            if d['SentOn'] != '<UNKNOWN>' and d['ConversationID'] != '<UNKNOWN>':
                items.append(d)
        except Exception as inst:
            print("Error processing mail", inst)

        message = messages.GetNext()
    return items


def extract(excludefolders, use_multiprocessing=False):
    items = []
    folders = {"inbox": 6, "sent_items": 5}     # append "deleted_items": 3 if wanted
    ''' Mails from folders in default folder set won't be extracted during extraction from extra-folders. 
       "archive" has been removed from default folder set and will be extracted unless excluded '''
    default_folder_set = {'deleted items', 'inbox', 'outbox', 'sent items', 'personmetadata', 'tasks', 'junk email',
                          'drafts', 'calendar', 'rss subscriptions', 'quick step settings', 'yammer root',
                          'conversation action settings', 'externalcontacts', 'important', 'journal', 'files',
                          'contacts', 'conversation history', 'social activity notifications', 'sync issues', 'notes',
                          'reminders',
                          'the file so that changes to the file will be reflected in your item.', 'work'}
    exclude_folder_set = set([foldername.lower() for foldername in excludefolders.split(',')])

    if use_multiprocessing:
        logging.info("Using multiprocessing while extracting mails...")
        folders_mp = [tup for tup in folders.items()]
        num_processes = len(folders_mp)
        p = mp.Pool(processes=num_processes)
        for i in range(num_processes):
            res = p.apply_async(extract_helper_mp, args=(folders_mp[i][1], folders_mp[i][0]))
            items.extend(res.get())
        p.close()
        p.join()

    else:
        outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
        for folder_type in folders:
            logging.info("Extracting emails from {0}".format(folder_type))
            folder = outlook.GetDefaultFolder(folders[folder_type])
            logging.info("Got messages...")
            messages = folder.Items
            logging.info("extacting messages...")
            items = extract_helper(messages=messages, folder_type=folder_type, items=items)
            logging.info("done extacting messages")

    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    all_folders = [folder for folder in outlook.Folders[0].folders]
    extrafolders = [folder for folder in all_folders if (str(folder).lower() not in default_folder_set
                                                         and str(folder).lower() not in exclude_folder_set)]
    if len(extrafolders) > 0:
        for folder in extrafolders:
            logging.info("Extracting emails from {0}".format(folder))
            messages = folder.Items
            items = extract_helper(messages=messages, folder_type=folder, items=items)
    return items


def make_user_dir():
    path = "./data_topiceval/userdata/"
    if os.path.exists(path):
        for filename in os.listdir(path):
            os.remove(os.path.join(path, filename))
    else:
        os.makedirs(path)
    logging.info("Saving data at {0}{1}".format(os.path.dirname(os.path.abspath(__file__)), path[1:]))
    return path


def makedf(items, threaded, usenltk):
    items.sort(key=lambda tup: tup['SentOn'])
    keys = ["ConversationID", "SentOn", "SenderName", "To", "CC", "BCC", "Subject", "Body",
            "FolderType"]
    df = pd.DataFrame()
    logging.debug("Making user-emails' dataframe...")
    for key in keys:
        try:
            df[key] = [str(d[key]) for d in items]
        except Exception as e:
            logging.debug("Exception: {}".format(e))
            df[key] = [d[key].encode('utf-8') for d in items]
    df.set_index(keys=["ConversationID"], inplace=True, drop=False)
    df['SentOn'] = pd.to_datetime(df['SentOn'], infer_datetime_format=True)
    logging.debug("Cleaning email bodies in dataframe...")
    # names = get_names(df)
    if threaded:
        bool_list = emailprocess.remove_redundant_threads(df)
        df = df[bool_list]
    else:
        df['Body'] = df['Body'].apply(emailprocess.remove_threads)
    df['Body'] = df['Body'].apply(emailprocess.remove_signature)
    bigram_phraser = emailprocess.phrase_detection(df)
    df['CleanBody'] = df['Body'].apply(textcleaning.clean_text, args=(usenltk,))
    df['CleanBody'] = df['CleanBody'].apply(emailprocess.phraser, args=(bigram_phraser,))
    df['CleanBody'] = df['CleanBody'].apply(textcleaning.remove_stops)
    # df['CleanBody'] = df['CleanBody'].apply(emailprocess.replace_names, args=(names, ))
    logging.debug("Done cleaning email bodies in dataframe")

    '''Earlier user mails were stored as a pickled dataframe, discontinued due to privacy concerns'''
    # df_filename = dirname + "emails.pkl"
    # df.to_pickle(df_filename)
    # logging.debug("Saved user-emails df at %s" % df_filename)
    # return df_filename, df
    return df


def get_names(df):
    return df["SenderName"].unique().tolist()


# def make_emails_dict(df):
#     emails_dict = {}
#     for elem in df.index.unique():
#         emails_dict[elem] = []
#     for idx, row in df.iterrows():
#         emails_dict[row["ConversationID"]].append((row["ConversationIndex"], row["Body"]))
#     return emails_dict
