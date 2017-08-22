#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QLabel


class Label(QLabel):
    """
    Simple white label with Akkurat-Mono

    Args:
        label(str): The text of the label.
    """

    def __init__(self, label):
        QLabel.__init__(self, label)
        self.setStyleSheet("font-family:Akkurat-Mono;color:white")
        self.setMinimumHeight(5)
