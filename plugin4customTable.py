# -*- coding: utf-8 -*-
import sys
import random
from PyQt4 import QtCore, QtGui

## This class enables items of TableWidget to be of float type

class QCustomTableWidgetItem(QtGui.QTableWidgetItem):
    def __init__ (self, value):
        super(QCustomTableWidgetItem, self).__init__(str(value))

    def __lt__ (self, other):
        if (isinstance(other, QCustomTableWidgetItem)):
            selfDataValue  = float(self.data(QtCore.Qt.EditRole))
            otherDataValue = float(other.data(QtCore.Qt.EditRole))
            return selfDataValue < otherDataValue
        else:
            return QtGui.QTableWidgetItem.__lt__(self, other)