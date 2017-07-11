from __future__ import print_function
from __future__ import division

from topiceval.usereval import senddata
import topiceval.usereval.topicevalGUI as topicevalGUI
from topiceval.coherence.semantic import semantic_coherence

import numpy as np

from PyQt5 import QtGui, QtWidgets, QtCore
from PyQt5.QtWidgets import QApplication, QMessageBox

import sys
import os
import pickle
import logging
import operator


def topic_tuple_overlap(topictups):
    """
    Return an overlap measure over 3 topic distributions

    :param topictups: a list of 3 tuples, each tuple contains word-probability information
    :return: overlap measure given by product of probabilities of words overlapping across all
        three tuples
    """
    topic_dicts = {}, {}, {}
    for i, topictup in enumerate(topictups):
        for tup in topictup:
            topic_dicts[i][tup[0]] = tup[1]
    overlap = 0.0
    for word in topic_dicts[0]:
        try:
            overlap += topic_dicts[0][word] * topic_dicts[1][word] * topic_dicts[2][word]
        except KeyError:
            continue
    return overlap


def all_triplet_overlaps(models):
    """
    Get overlap measure for all possible triplet combination of topics

    :param models: a list of 3 topic models
    :return: a list containing overlap measures for all triplets
    """
    num_topics = len(models[0].representative_topic_tuples)
    all_overlaps = []
    for i in range(num_topics):
        for j in range(num_topics):
            for k in range(num_topics):
                all_overlaps = all_overlaps + [
                    [[i, j, k], topic_tuple_overlap([models[0].representative_topic_tuples[i],
                                                     models[1].representative_topic_tuples[j],
                                                     models[2].representative_topic_tuples[k]])]]
    return all_overlaps


class TopicEvalWindowClass(QtWidgets.QMainWindow, topicevalGUI.Ui_MainWindow):
    def __init__(self, models, dirname, num_topics, threaded):

        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

        self.i = 0
        self.all_models = models
        self.dirname = dirname
        self.num_topics = num_topics
        self.threaded = threaded
        self.wordspertopic = 10
        self.states = [0] * 3
        self.mapping = [0, 1, 2]
        self.selected_items = [[]] * 3
        self.headings = [""] * 3
        self.added_words = [""] * 3
        rep1, rep2, rep3 = self.topics_order()
        self.rep_order = [rep1, rep2, rep3]

        self.listWidgets = [self.listWidget_1, self.listWidget_2, self.listWidget_3]
        self.showNext10PushButtons = [self.showNext10PushButton_1, self.showNext10PushButton_2,
                                      self.showNext10PushButton_3]
        self.showPrevious10PushButtons = [self.showPrevious10PushButton_1, self.showPrevious10PushButton_2,
                                          self.showPrevious10PushButton_3]
        self.buttonGroups = [self.buttonGroup_1, self.buttonGroup_2, self.buttonGroup_3]
        self.comboBoxes = [self.comboBox_1, self.comboBox_2, self.comboBox_3]

        path = os.path.dirname(os.path.abspath(__file__)) + "/resources/icon.png"
        self.setWindowIcon(QtGui.QIcon(path))

        self.fontSpinBox.valueChanged.connect(self.change_font_size)

        path = os.path.dirname(os.path.abspath(__file__)) + "/resources/bkdimage.jpg"
        try:
            self.bkdLabel.setPixmap(QtGui.QPixmap(path))
            self.bkdLabel.setScaledContents(True)
        except AttributeError:
            pass

        self.nextCommandLinkButton.clicked.connect(self.show_next_topic)

        # TODO: Fix this, using lambda in for loop is not working as it takes the final value of i for every button
        self.showNext10PushButtons[0].clicked.connect(lambda: self.show_next_10(0))
        self.showNext10PushButtons[1].clicked.connect(lambda: self.show_next_10(1))
        self.showNext10PushButtons[2].clicked.connect(lambda: self.show_next_10(2))
        self.showPrevious10PushButtons[0].clicked.connect(lambda: self.show_previous_10(0))
        self.showPrevious10PushButtons[1].clicked.connect(lambda: self.show_previous_10(1))
        self.showPrevious10PushButtons[2].clicked.connect(lambda: self.show_previous_10(2))
        for buttonGroup in self.buttonGroups:
            buttonGroup.buttonClicked.connect(self.groupbutton_clicked)
        for i in range(len(self.states)):
            self.update_gui(i)

            # self.topicimageLabel.setPixmap(QtGui.QPixmap(dirname + '/topic%d.png' % self.i))
            # self.topicimageLabel.setScaledContents(True)

    # def show_next_image(self):
    #     if self.i >= self.num_topics:
    #         return
    #     self.topicimageLabel.setPixmap(QtGui.QPixmap(self.dirname + '/topic%d.png' % self.i))
    #     self.topicimageLabel.setScaledContents(True)
    #     self.i += 1
    #     if self.i >= self.num_topics:
    #         self.nextCommandLinkButton.setText("Finish!")
    #     return

    def topics_order(self):
        """
        Decide order in which to show topics based on their word-overlap measure

        :return: 3 lists containing order of topic no. for the corresponding topic model
        """
        all_overlaps = all_triplet_overlaps(self.all_models)
        sorted_overlaps = sorted(all_overlaps, key=operator.itemgetter(1), reverse=True)
        set1, set2, set3 = set(), set(), set()
        rep1, rep2, rep3 = [], [], []
        topics_covered = 0
        for item in sorted_overlaps:
            if topics_covered >= self.num_topics:
                break
            topic_nums = item[0]
            if topic_nums[0] in set1 or topic_nums[1] in set2 or topic_nums[2] in set3:
                continue
            else:
                rep1.append(topic_nums[0])
                rep2.append(topic_nums[1])
                rep3.append(topic_nums[2])
                set1.add(topic_nums[0])
                set2.add(topic_nums[1])
                set3.add(topic_nums[2])
                topics_covered += 1
        assert (len(rep1) == self.num_topics and len(rep2) == self.num_topics and len(rep3) == self.num_topics)
        return rep1, rep2, rep3

    def change_font_size(self):
        size = self.fontSpinBox.value()
        font = QtGui.QFont()
        font.setPointSize(size)
        font.setItalic(True)
        font.setWeight(50)
        for listWidget in self.listWidgets:
            listWidget.setFont(font)
        return

    def scores_update(self):
        """ Update stored score for the topic as given by the user """
        for i, group in enumerate(self.buttonGroups):
            score = int(group.checkedButton().text())
            modelnum = self.mapping[i]
            self.all_models[modelnum].representative_topics_scores += [score]
        return

    def labels_update(self):
        """ Update stored label-based feedback for the topic as given by the user """
        for i in range(3):
            modelnum = self.mapping[i]
            self.all_models[modelnum].representative_topics_enumlabels.append(self.comboBoxes[i].currentText())
            self.all_models[modelnum].representative_topics_textlabels.append(self.headings[i])
            self.all_models[modelnum].representative_topics_addedwords.append(self.added_words[i])
            # self.all_models[modelnum].representative_topics_selectedwords.\
            #     append([index.row() for index in self.listWidgets[i].selectedIndexes()])
            self.all_models[modelnum].representative_topics_selectedwords += [self.selected_items[i]]
        return

    def unselect_radiobuttons(self):
        for buttonGroup in self.buttonGroups:
            buttonGroup.setExclusive(False)
            for button in buttonGroup.buttons():
                button.setChecked(False)
            buttonGroup.setExclusive(True)
        return

    def reset_comboboxes(self):
        for combobox in self.comboBoxes:
            combobox.setCurrentIndex(0)
        return

    def groupbutton_clicked(self):
        all_selected_flag = True
        for group in self.buttonGroups:
            if group.checkedId() == -1:
                all_selected_flag = False
                break
        if all_selected_flag:
            self.nextCommandLinkButton.setEnabled(True)
        else:
            self.nextCommandLinkButton.setEnabled(False)
        return

    def show_next_10(self, i):
        if self.states[i] == 1:
            last_idx = self.listWidgets[i].count() - 1
            for j in range(last_idx + 1):
                if self.listWidgets[i].item(j).isSelected():
                    self.selected_items[i] += [j]
            self.headings[i] = self.listWidgets[i].item(2).text()
            self.added_words[i] = self.listWidgets[i].item(last_idx).text()

        self.states[i] += 1
        self.update_gui(i)
        return

    def show_previous_10(self, i):
        self.states[i] -= 1
        self.update_gui(i)
        return

    def show_next_topic(self):
        self.i += 1
        self.scores_update()
        self.labels_update()
        self.mapping = np.random.choice(len(self.all_models), 3, replace=False)
        print(self.mapping)
        if self.i >= self.num_topics:
            self.states = [-1] * len(self.states)
            self.show_results()
        else:
            self.states = [0] * len(self.states)
        for i in range(len(self.states)):
            self.update_gui(i)
        return

    def show_topic(self, i):
        start = (self.states[i] - 1) * self.wordspertopic
        end = start + self.wordspertopic
        total_weight, strings = self.tuples_to_strings(start=start, end=end, i=i)
        self.listWidgets[i].addItems(["Total Wt (%d:%d)" % (start + 1, end), "(%0.3f)" % total_weight, ""])
        self.listWidgets[i].item(2).setTextAlignment(132)  # centering
        self.listWidgets[i].item(1).setTextAlignment(132)  # centering
        self.listWidgets[i].item(0).setTextAlignment(132)  # centering
        self.listWidgets[i].item(2).setFlags(self.listWidgets[i].item(2).flags() & ~QtCore.Qt.ItemIsSelectable)
        self.listWidgets[i].item(1).setFlags(self.listWidgets[i].item(1).flags() & ~QtCore.Qt.ItemIsSelectable)
        self.listWidgets[i].item(0).setFlags(self.listWidgets[i].item(0).flags() & ~QtCore.Qt.ItemIsSelectable)
        self.listWidgets[i].addItems(strings)
        if self.states[i] == 1:
            self.listWidgets[i].addItem("")
            lastitem_idx = self.listWidgets[i].count() - 1
            self.listWidgets[i].item(lastitem_idx).setFlags(self.listWidgets[i].item(lastitem_idx).flags() |
                                                            QtCore.Qt.ItemIsEditable)
            self.listWidgets[i].item(lastitem_idx).setFlags(self.listWidgets[i].item(lastitem_idx).flags()
                                                            & ~QtCore.Qt.ItemIsSelectable)
            self.listWidgets[i].item(lastitem_idx).setForeground(QtGui.QBrush(QtGui.QColor(220, 220, 220)))
            self.listWidgets[i].item(2).setFlags(self.listWidgets[i].item(2).flags() | QtCore.Qt.ItemIsEditable)
            self.listWidgets[i].item(2).setToolTip("Write a label for the topic!")
            self.listWidgets[i].item(2).setForeground(QtGui.QBrush(QtGui.QColor(220, 220, 220)))
            if self.headings[i] == "" or self.headings[i] == "(Enter Topic Label)":
                self.listWidgets[i].item(2).setText("(Enter Topic Label)")
            else:
                self.listWidgets[i].item(2).setText(self.headings[i])
            for itemnum in self.selected_items[i]:
                self.listWidgets[i].item(itemnum).setSelected(True)
            if self.added_words[i] == "" or self.added_words[i] == "(Add Words)":
                self.listWidgets[i].item(lastitem_idx).setText("Add Words")
            else:
                self.listWidgets[i].item(lastitem_idx).setText(self.added_words[i])
        return

    def update_gui(self, i):
        state = self.states[i]
        if state == 0:
            self.states[i] = 1
            self.listWidgets[i].clear()
            self.show_topic(i)
            self.showNext10PushButtons[i].setEnabled(True)
            self.showPrevious10PushButtons[i].setEnabled(False)
            self.unselect_radiobuttons()
            self.reset_comboboxes()
            self.nextCommandLinkButton.setEnabled(False)
        if state == 1:
            self.listWidgets[i].clear()
            self.show_topic(i)
            self.showNext10PushButtons[i].setEnabled(True)
            self.showPrevious10PushButtons[i].setEnabled(False)
        elif state == 2:
            self.listWidgets[i].clear()
            self.show_topic(i)
            self.showNext10PushButtons[i].setEnabled(True)
            self.showPrevious10PushButtons[i].setEnabled(True)
        elif state == 3:
            self.listWidgets[i].clear()
            self.show_topic(i)
            self.showNext10PushButtons[i].setEnabled(False)
            self.showPrevious10PushButtons[i].setEnabled(True)
        elif state == -1:
            for listWidget in self.listWidgets:
                listWidget.clear()
            for showPrevious10PushButton in self.showPrevious10PushButtons:
                showPrevious10PushButton.setEnabled(False)
            for showNext10PushButton in self.showNext10PushButtons:
                showNext10PushButton.setEnabled(False)
            self.nextCommandLinkButton.setEnabled(True)
            self.nextCommandLinkButton.setText("Submit")
            self.nextCommandLinkButton.clicked.connect(self.showdialog)
        return

    def show_results(self):
        for model in self.all_models:
            print("\n------------------- Results for {0} -------------------".format(model.modelname))
            print("Average user score for model is %0.2f(%0.2f)" % (np.mean(model.representative_topics_scores),
                                                                    np.var(model.representative_topics_scores)))
            njunk = model.representative_topics_enumlabels.count("Junk")
            nfused = model.representative_topics_enumlabels.count("Fused")
            nunbalanced = model.representative_topics_enumlabels.count("Unbalanced")
            print("Number of labels: junk: %d, imbalanced: %d, fused: %d" % (njunk, nfused, nunbalanced))
            nintruder_words = 0
            for added_words in model.representative_topics_selectedwords:
                nintruder_words += len(added_words)
            avg_intruder_words = nintruder_words / len(model.representative_topics_selectedwords)
            print("Average intruder words per topic: {}\n".format(avg_intruder_words))
            avg_coherence = np.mean(model.representative_topics_semcoherences)
            var_coherence = np.var(model.representative_topics_semcoherences)
            print("Average semantic coherence of topics: %0.2f(%0.2f)" %(avg_coherence, var_coherence))
        return

    def cleanup(self):
        dirpath = self.dirname
        files = [os.path.join(dirpath, f) for f in os.listdir(dirpath) if os.path.isfile(os.path.join(dirpath, f))]
        for file in files:
            os.remove(file)
        try:
            os.rmdir(dirpath)
            # TODO: Change brute name to chunk of dirpath
            os.rmdir("./data_topiceval")
            logging.info("Completed temporary file cleanup.")
        except OSError:
            logging.warning("Could not delete the temp folder. You may do it manually for directory at %s" % dirpath)
        return

    def showdialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("Thank you! Ready to send results!")
        msg.setInformativeText("The results will be sent via email. Privacy is of utmost importance and only the "
                               "top words shown to you and the scores/other info added by you will be sent.")
        msg.setWindowTitle("Submit Results")
        # TODO: Set details of files being sent
        # msg.setDetailedText("The details of files being sent are as follows: 1) topic matrices: the word-probability"
        #                     " distribution of topics, the top words were shown and ranked by you. "
        #                     "2) Your scores for the topics "
        #                     "3) This data will be sent to t-avsriv@microsoft.com")
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)

        # noinspection PyUnresolvedReferences
        msg.buttonClicked.connect(self.msgbtn)
        sys.exit(msg.exec_())

    def msgbtn(self, i):
        if i.text() == "OK":
            self.submit()
        else:
            buttonReply = QMessageBox.question(self, 'Really Quit', "The scores won't be sent. Quit(Yes) "
                                                                    "or Submit(\"No\")?",
                                               QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if buttonReply == QMessageBox.Yes:
                self.close()
            else:
                self.submit()
        return

    def submit(self):
        threaded = self.threaded
        shown_topic_tuples = []
        shown_topic_scores = []
        shown_topic_enumlabels = []
        shown_topic_textlabels = []
        shown_topic_addedwords = []
        shown_topic_selectedwords = []
        for i, model in enumerate(self.all_models):
            shown_topic_tuples.append([model.modelname, threaded,
                                       model.representative_topic_tuples[:self.num_topics]])
            # shown_topic_tuples.append([model.modelname, threaded,
            #                            model.representative_topic_tuples[self.rep_order[i]]])
            shown_topic_scores.append(model.representative_topics_scores)
            shown_topic_enumlabels.append(model.representative_topics_enumlabels)
            shown_topic_textlabels.append(model.representative_topics_textlabels)
            shown_topic_addedwords.append(model.representative_topics_addedwords)
            shown_topic_selectedwords.append(model.representative_topics_selectedwords)

        with open(self.dirname + "shown_topic_tuples.pkl", "wb") as handle:
            pickle.dump(shown_topic_tuples, handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open(self.dirname + "shown_topic_scores.pkl", "wb") as handle:
            pickle.dump(shown_topic_scores, handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open(self.dirname + "shown_topic_enumlabels.pkl", "wb") as handle:
            pickle.dump(shown_topic_enumlabels, handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open(self.dirname + "shown_topic_textlabels.pkl", "wb") as handle:
            pickle.dump(shown_topic_textlabels, handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open(self.dirname + "shown_topic_addedwords.pkl", "wb") as handle:
            pickle.dump(shown_topic_addedwords, handle, protocol=pickle.HIGHEST_PROTOCOL)
        with open(self.dirname + "shown_topic_selectedwords.pkl", "wb") as handle:
            pickle.dump(shown_topic_selectedwords, handle, protocol=pickle.HIGHEST_PROTOCOL)
        os.remove(self.dirname + "Amatrix.npz")
        os.remove(self.dirname + "corpus.npy")
        os.remove(self.dirname + "dfindices_in_corpus.npy")
        # np.save(dirname + "shown_topic_tuples.npy", shown_topic_tuples)
        # np.save(dirname + "shown_topic_scores.npy", shown_topic_scores)
        senddata.makezip(self.dirname)
        senddata.sendmail()
        QMessageBox.information(self, 'Success', "Results sent successfully!")
        self.cleanup()
        return

    def tuples_to_strings(self, start, end, i):
        if self.i >= self.num_topics:
            return
        # tuple_list = self.all_models[self.mapping[i]].representative_topic_tuples[self.i][start:end]
        tuple_list = \
            self.all_models[self.mapping[i]].representative_topic_tuples[self.rep_order[self.mapping[i]][self.i]][start:end]
        coherence = semantic_coherence(self.dirname, self.all_models[self.mapping[i]], tuple_list, numwords=10)
        self.all_models[self.mapping[i]].representative_topics_semcoherences.append(coherence)
        strings = ["%s (%0.3f)" % (tup[0], tup[1]) for tup in tuple_list]
        total_weight = 0.
        for tup in tuple_list:
            total_weight += tup[1]
        return total_weight, strings

    def closeEvent(self, event):
        """ Upon closing the application, cleanup all temporary data """
        self.cleanup()
        event.accept()
        return

        # def closeEvent(self, event):
        #
        #     quit_msg = "Are you sure you want to exit the program?"
        #     reply = QMessageBox.question(self, 'Message',
        #                                        quit_msg, QMessageBox.Yes, QMessageBox.No)
        #
        #     if reply == QMessageBox.Yes:
        #         event.accept()
        #     else:
        #         event.ignore()


def main(models, dirname, num_topics, threaded):
    app = QApplication(sys.argv)
    window = TopicEvalWindowClass(models=models, dirname=dirname, num_topics=num_topics, threaded=threaded)
    window.show()
    app.exec_()
    return
