# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtMultimediaWidgets import QVideoWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 542)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.mediaWidget = QVideoWidget(self.centralwidget)
        self.mediaWidget.setObjectName("mediaWidget")
        self.verticalLayout.addWidget(self.mediaWidget)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.curTimeLabel = QtWidgets.QLabel(self.centralwidget)
        self.curTimeLabel.setObjectName("curTimeLabel")
        self.horizontalLayout_2.addWidget(self.curTimeLabel)
        self.progressSlider = QtWidgets.QSlider(self.centralwidget)
        self.progressSlider.setOrientation(QtCore.Qt.Horizontal)
        self.progressSlider.setObjectName("progressSlider")
        self.horizontalLayout_2.addWidget(self.progressSlider)
        self.endTimeLabel = QtWidgets.QLabel(self.centralwidget)
        self.endTimeLabel.setObjectName("endTimeLabel")
        self.horizontalLayout_2.addWidget(self.endTimeLabel)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.urlLineEdit = QtWidgets.QLineEdit(self.centralwidget)
        self.urlLineEdit.setObjectName("urlLineEdit")
        self.horizontalLayout.addWidget(self.urlLineEdit)
        self.playBtn = QtWidgets.QPushButton(self.centralwidget)
        self.playBtn.setObjectName("playBtn")
        self.horizontalLayout.addWidget(self.playBtn)
        self.pauseBtn = QtWidgets.QPushButton(self.centralwidget)
        self.pauseBtn.setObjectName("pauseBtn")
        self.horizontalLayout.addWidget(self.pauseBtn)
        self.stopBtn = QtWidgets.QPushButton(self.centralwidget)
        self.stopBtn.setObjectName("stopBtn")
        self.horizontalLayout.addWidget(self.stopBtn)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 8)
        self.verticalLayout.setStretch(1, 1)
        self.verticalLayout.setStretch(2, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.curTimeLabel.setText(_translate("MainWindow", "current"))
        self.endTimeLabel.setText(_translate("MainWindow", "end"))
        self.playBtn.setText(_translate("MainWindow", "播放"))
        self.pauseBtn.setText(_translate("MainWindow", "暂停"))
        self.stopBtn.setText(_translate("MainWindow", "停止"))
