"""
This module explores the structure in user's inbox.
"""

from __future__ import division
from __future__ import print_function

# import pandas
import numpy as np
from sklearn.model_selection import train_test_split

import operator
import logging


class EmailUser(object):
    def __init__(self, name, nsent_to, nsent_cc, nrecvd_from):
        self.name = name
        self.nsent_to = nsent_to
        self.nsent_cc = nsent_cc
        self.recvd_from = nrecvd_from


class EmailNetwork(object):
    def __init__(self, df):
        self.df = df
        self.username = self.__get_username()
        self.sent_to_users, self.cc_to_users, self.recvd_from_users, self.sent_to_users_dict, \
            self.cc_to_users_dict, self.recvd_from_users_dict = self.__get_all_users()
        self.all_users = self.sent_to_users | self.cc_to_users | self.recvd_from_users
        self.top3_users = self.__get_top3_users()
        self.custom_folders, self.folders_idc_dict = self.__get_custom_folders()
        if len(self.custom_folders) < 3:
            self.frequent_filer = False
        else:
            self.frequent_filer = True
        if self.frequent_filer:
            self.folders_X_train, self.folders_X_test, self.folders_y_train, self.folders_y_test = \
                self.folder_predicition_task()
        else:
            self.folders_X_train, self.folders_X_test, self.folders_y_train, self.folders_y_test = [None]*4
        return

    def __get_username(self):
        """ Assign the sender with most emails sent as the user name """
        sender_stats = self.df[self.df["FolderType"] == "sent_items"].groupby("SenderName")["SentOn"].count()
        sender_stats_dict = dict(zip(sender_stats.index, sender_stats.data))
        sorted_sender_stats = sorted(sender_stats_dict.items(), key=operator.itemgetter(1), reverse=True)
        username = str(sorted_sender_stats[0][0])
        if username.upper() == "<UNKNOWN>":
            logging.warning("Username detected as <UNKNOWN>! Changing to second highest sender...")
            try:
                username = str(sorted_sender_stats[1][0])
            except IndexError:
                logging.error("Username could not be detected!")
        return username

    def __get_all_users(self):
        sent_to_users = set()
        cc_to_users = set()
        recvd_from_users = set()

        # emails_sent = self.df[self.df["FolderType"] == "sent_items"]
        emails_sent = self.df[self.df["SenderName"] == self.username]

        sent_to_users_dict = {}
        for _, row in emails_sent[["To", "idx"]].iterrows():
            text = row[0]
            idx = row[1]
            to = [user.strip() for user in text.split(";")]
            for item in to:
                if item == self.username or item.upper() == "<UNKNOWN>":
                    continue
                try:
                    sent_to_users_dict[item] += [idx]
                except KeyError:
                    sent_to_users_dict[item] = [idx]
                sent_to_users.add(item)

        cc_to_users_dict = {}
        for _, row in emails_sent[["CC", "idx"]].iterrows():
            text = row[0]
            idx = row[1]
            cc = [user.strip() for user in text.split(";")]
            for item in cc:
                if item == self.username or item.upper() == "<UNKNOWN>":
                    continue
                try:
                    cc_to_users_dict[item] += [idx]
                except KeyError:
                    cc_to_users_dict[item] = [idx]
                cc_to_users.add(item)

        # emails_except_sent = self.df[self.df["FolderType"] != "sent_items"]
        emails_except_sent = self.df[self.df["SenderName"] != self.username]
        recvd_from_users_dict = {}
        for _, row in emails_except_sent[["SenderName", "idx"]].iterrows():
            text = row[0]
            idx = row[1]
            if text == self.username or text.upper() == "<UNKNOWN>":
                continue
            try:
                recvd_from_users_dict[item] += [idx]
            except KeyError:
                recvd_from_users_dict[item] = [idx]
            recvd_from_users.add(item)

        # all_recvd_counts = emails_except_sent.groupby("SenderName")["SentOn"].count()
        # recvd_from_users_dict = dict(zip(all_recvd_counts.index, all_recvd_counts.data))
        # recvd_from_users_dict.pop('<UNKNOWN>', None)
        # for user in all_recvd_counts.index:
        #     if user != self.username and user.upper() != "<UNKNOWN>":
        #         recvd_from_users.add(user)

        all_users = sent_to_users | cc_to_users | recvd_from_users

        for user in all_users:
            try:
                _ = sent_to_users_dict[user]
            except KeyError:
                sent_to_users_dict[user] = []
            try:
                _ = cc_to_users_dict[user]
            except KeyError:
                cc_to_users_dict[user] = []
            try:
                _ = recvd_from_users_dict[user]
            except KeyError:
                recvd_from_users_dict[user] = []

        return sent_to_users, cc_to_users, recvd_from_users, sent_to_users_dict, cc_to_users_dict, recvd_from_users_dict

    def __get_top3_users(self):
        sent_to_users_len_dict = {}
        for key in self.sent_to_users_dict:
            sent_to_users_len_dict[key] = len(self.sent_to_users_dict[key])
        sorted_sent_to_users = sorted(sent_to_users_len_dict.items(), key=operator.itemgetter(1), reverse=True)
        top_users = []
        for tup in sorted_sent_to_users[:3]:
            top_users.append(tup[0])
        return top_users

    def __get_custom_folders(self):
        all_folders = set(list(self.df["FolderType"].unique()))
        all_folders.remove('inbox')
        all_folders.remove('sent_items')

        folders_idc_dict = {}
        for folder in all_folders:
            folders_idc_dict[folder] = []
        for _, row in self.df[["FolderType", "idx"]].iterrows():
            folder = row[0]
            if folder not in all_folders:
                continue
            idx = row[1]
            folders_idc_dict[folder] += [idx]
        return all_folders, folders_idc_dict

    def folder_predicition_task(self):
        total_custom_mails = 0
        for key, idc in self.folders_idc_dict.items():
            total_custom_mails += len(idc)
        U = total_custom_mails / len(self.folders_idc_dict)
        retained_folders = set()
        for key, idc in self.folders_idc_dict.items():
            # TODO : Adjust fraction
            if len(idc) >= int(U/3):
                retained_folders.add(key)

        X, y = [], []
        for folder in retained_folders:
            idc = self.folders_idc_dict[folder]
            X += idc
            y += [folder]*len(idc)
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42, stratify=y)
        order = np.random.choice(len(X_train), len(X_train), replace=False)
        X_train = [X_train[i] for i in order]
        y_train = [y_train[i] for i in order]
        order = np.random.choice(len(X_test), len(X_test), replace=False)
        X_test = [X_train[i] for i in order]
        y_test = [y_train[i] for i in order]
        return X_train, X_test, y_train, y_test


        # train_data_idc, train_target = [], []
        # test_data_idc, test_target = [], []
        # for folder in retained_folders:
        #     idc = self.folders_idc_dict[folder]
        #     num_idc = len(idc)
        #     train_idc = np.random.choice(num_idc, int(0.8*num_idc), replace=False)
        #     train_data_idc += list(train_idc)
        #     train_target += [folder]*int(0.8*num_idc)
