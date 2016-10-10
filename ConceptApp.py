# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ConceptApp.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(795, 600)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.treeWidget = QtGui.QTreeWidget(self.centralwidget)
        self.treeWidget.setGeometry(QtCore.QRect(20, 10, 760, 370))
        self.treeWidget.setRootIsDecorated(False)
        self.treeWidget.setUniformRowHeights(False)
        self.treeWidget.setItemsExpandable(False)
        self.treeWidget.setAllColumnsShowFocus(False)
        self.treeWidget.setWordWrap(True)
        self.treeWidget.setHeaderHidden(False)
        self.treeWidget.setExpandsOnDoubleClick(True)
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        item_0 = QtGui.QTreeWidgetItem(self.treeWidget)
        item_0 = QtGui.QTreeWidgetItem(self.treeWidget)
        self.treeWidget.header().setVisible(True)
        self.treeWidget.header().setCascadingSectionResizes(True)
        self.treeWidget.header().setDefaultSectionSize(75)
        self.treeWidget.header().setHighlightSections(True)
        self.treeWidget.header().setMinimumSectionSize(50)
        self.treeWidget.header().setSortIndicatorShown(False)
        self.treeWidget.header().setStretchLastSection(True)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 795, 21))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuFile = QtGui.QMenu(self.menubar)
        self.menuFile.setObjectName(_fromUtf8("menuFile"))
        self.menuIRC = QtGui.QMenu(self.menubar)
        self.menuIRC.setObjectName(_fromUtf8("menuIRC"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.actionQuit = QtGui.QAction(MainWindow)
        self.actionQuit.setObjectName(_fromUtf8("actionQuit"))
        self.actionMessage_as_Bot = QtGui.QAction(MainWindow)
        self.actionMessage_as_Bot.setObjectName(_fromUtf8("actionMessage_as_Bot"))
        self.actionWhisper_as_Bot = QtGui.QAction(MainWindow)
        self.actionWhisper_as_Bot.setObjectName(_fromUtf8("actionWhisper_as_Bot"))
        self.actionTimeout_as_Bot = QtGui.QAction(MainWindow)
        self.actionTimeout_as_Bot.setObjectName(_fromUtf8("actionTimeout_as_Bot"))
        self.actionBan_as_Bot = QtGui.QAction(MainWindow)
        self.actionBan_as_Bot.setObjectName(_fromUtf8("actionBan_as_Bot"))
        self.menuFile.addAction(self.actionQuit)
        self.menuIRC.addAction(self.actionMessage_as_Bot)
        self.menuIRC.addAction(self.actionWhisper_as_Bot)
        self.menuIRC.addSeparator()
        self.menuIRC.addAction(self.actionTimeout_as_Bot)
        self.menuIRC.addAction(self.actionBan_as_Bot)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuIRC.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow", None))
        self.treeWidget.headerItem().setText(0, _translate("MainWindow", "UTags", None))
        self.treeWidget.headerItem().setText(1, _translate("MainWindow", "Username", None))
        self.treeWidget.headerItem().setText(2, _translate("MainWindow", "Message", None))
        __sortingEnabled = self.treeWidget.isSortingEnabled()
        self.treeWidget.setSortingEnabled(False)
        self.treeWidget.topLevelItem(0).setText(0, _translate("MainWindow", "MOD", None))
        self.treeWidget.topLevelItem(0).setText(1, _translate("MainWindow", "TheKillar25", None))
        self.treeWidget.topLevelItem(0).setText(2, _translate("MainWindow", "Test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test test", None))
        self.treeWidget.topLevelItem(1).setText(0, _translate("MainWindow", "---", None))
        self.treeWidget.topLevelItem(1).setText(1, _translate("MainWindow", "chinorlf", None))
        self.treeWidget.topLevelItem(1).setText(2, _translate("MainWindow", "Hey guys, I\'m gay", None))
        self.treeWidget.setSortingEnabled(__sortingEnabled)
        self.menuFile.setTitle(_translate("MainWindow", "File", None))
        self.menuIRC.setTitle(_translate("MainWindow", "IRC", None))
        self.actionQuit.setText(_translate("MainWindow", "Quit", None))
        self.actionMessage_as_Bot.setText(_translate("MainWindow", "Message as Bot", None))
        self.actionWhisper_as_Bot.setText(_translate("MainWindow", "Whisper as Bot", None))
        self.actionTimeout_as_Bot.setText(_translate("MainWindow", "Timeout as Bot", None))
        self.actionBan_as_Bot.setText(_translate("MainWindow", "Ban as Bot", None))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    MainWindow = QtGui.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())

