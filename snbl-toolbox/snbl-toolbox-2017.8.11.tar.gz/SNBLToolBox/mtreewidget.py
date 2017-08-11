#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets


class MTreeWidget(QtWidgets.QTreeWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.addedLayers = 0

    def mouseDoubleClickEvent(self, event):
        if self.itemAt(event.pos()) is None:
            item = QtWidgets.QTreeWidgetItem(self)
            item.setFlags(item.flags() | QtCore.Qt.ItemIsEditable)
            if self.addedLayers == 0 or self.addedLayers >= 3:
                item.setText(0, '1 0 0')
                item.setText(1, '0 1 0')
            elif self.addedLayers == 1:
                item.setText(0, '1 0 0')
                item.setText(1, '0 0 1')
            elif self.addedLayers == 2:
                item.setText(0, '0 1 0')
                item.setText(1, '0 0 1')
            item.setText(2, '0 0 0')
            item.setText(3, '1.0')
            item.setText(4, '0.01')
            self.addTopLevelItem(item)
            self.addedLayers += 1
        super().mouseDoubleClickEvent(event)

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if event.button() == QtCore.Qt.RightButton and item is not None:
            self.takeTopLevelItem(self.indexOfTopLevelItem(item))
            self.addedLayers -= 1
        else:
            super().mousePressEvent(event)

    def getLayers(self):
        res = []
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            layer = {
                'hkl1': item.text(0),
                'hkl2': item.text(1),
                'center': item.text(2),
                'qmax': item.text(3),
                'thickness': item.text(4),
            }
            res.append(layer)
        return res
