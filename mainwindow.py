# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(854, 604)
        MainWindow.setAutoFillBackground(False)
        MainWindow.setStyleSheet("")
        MainWindow.setAnimated(True)
        MainWindow.setDocumentMode(False)
        MainWindow.setTabShape(QtWidgets.QTabWidget.Rounded)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        MainWindow.setCentralWidget(self.centralwidget)
        self.dockWidget_3 = QtWidgets.QDockWidget(MainWindow)
        self.dockWidget_3.setStyleSheet("")
        self.dockWidget_3.setFeatures(QtWidgets.QDockWidget.DockWidgetFloatable|QtWidgets.QDockWidget.DockWidgetMovable)
        self.dockWidget_3.setAllowedAreas(QtCore.Qt.BottomDockWidgetArea|QtCore.Qt.TopDockWidgetArea)
        self.dockWidget_3.setObjectName("dockWidget_3")
        self.dockWidgetContents_3 = QtWidgets.QWidget()
        self.dockWidgetContents_3.setObjectName("dockWidgetContents_3")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.dockWidgetContents_3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_0 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_0.setObjectName("horizontalLayout_0")
        self.curTimeLabel = QtWidgets.QLabel(self.dockWidgetContents_3)
        self.curTimeLabel.setStyleSheet("QLabel {\n"
"    color: rgb(235,97,0);\n"
"}")
        self.curTimeLabel.setObjectName("curTimeLabel")
        self.horizontalLayout_0.addWidget(self.curTimeLabel)
        self.progressSlider = QtWidgets.QSlider(self.dockWidgetContents_3)
        self.progressSlider.setContextMenuPolicy(QtCore.Qt.DefaultContextMenu)
        self.progressSlider.setStyleSheet("QSlider::groove:horizontal {\n"
"    border: 0px; \n"
"} \n"
"QSlider::sub-page:horizontal {\n"
"    background: rgb(235,97,0);\n"
"    border-radius: 2px; \n"
"    margin-top:8px; \n"
"    margin-bottom:8px; \n"
"} \n"
"QSlider::add-page:horizontal { \n"
"    background: rgb(255,255,255); \n"
"    border: 0px; \n"
"    border-radius: 2px; \n"
"    margin-top:8px;\n"
"    margin-bottom:8px; \n"
"} \n"
"QSlider::handle:horizontal { \n"
"    background: rgb(255,153,102); \n"
"    border: 1px solid rgb(255,153,102); \n"
"    width: 12px; \n"
"    height:4px; \n"
"    border-radius: 7px; \n"
"    margin-top:4px; \n"
"    margin-bottom:4px; \n"
"} \n"
"QSlider::handle:horizontal:hover { \n"
"    background: rgb(255,128,6);\n"
"    border: 1px solid rgb(255,128,6); \n"
"    border-radius:7px; \n"
"} \n"
"QSlider::sub-page:horizontal:disabled { \n"
"    background: #bbb; \n"
"    border-color: #999; \n"
"} \n"
"QSlider::add-page:horizontal:disabled {\n"
"    background: #eee; \n"
"    border-color: #999; \n"
"} \n"
"QSlider::handle:horizontal:disabled { \n"
"    background: #eee;\n"
"    border: 1px solid #eee;\n"
"    border-radius: 7px; \n"
"}")
        self.progressSlider.setSingleStep(0)
        self.progressSlider.setPageStep(0)
        self.progressSlider.setOrientation(QtCore.Qt.Horizontal)
        self.progressSlider.setInvertedAppearance(False)
        self.progressSlider.setInvertedControls(False)
        self.progressSlider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.progressSlider.setObjectName("progressSlider")
        self.horizontalLayout_0.addWidget(self.progressSlider)
        self.endTimeLabel = QtWidgets.QLabel(self.dockWidgetContents_3)
        self.endTimeLabel.setStyleSheet("QLabel {\n"
"    color: rgb(235,97,0);\n"
"}")
        self.endTimeLabel.setObjectName("endTimeLabel")
        self.horizontalLayout_0.addWidget(self.endTimeLabel)
        self.verticalLayout_2.addLayout(self.horizontalLayout_0)
        self.horizontalLayout_1 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_1.setSpacing(10)
        self.horizontalLayout_1.setObjectName("horizontalLayout_1")
        self.urlLineEdit = QtWidgets.QLineEdit(self.dockWidgetContents_3)
        self.urlLineEdit.setStyleSheet("QLineEdit {\n"
"    height: 20px;\n"
"    width: 20px;\n"
"    border-width:2px;\n"
"    border-radius:4px;\n"
"    font-size:12px;\n"
"    color:black;\n"
"    border:1px solid rgb(255,153,102);\n"
"}\n"
"QLineEdit:hover {\n"
"    border-width:2px;\n"
"    border-radius:4px;\n"
"    font-size:16px;\n"
"    color:black;\n"
"    border:1px solid rgb(255,128,6);\n"
"}")
        self.urlLineEdit.setObjectName("urlLineEdit")
        self.horizontalLayout_1.addWidget(self.urlLineEdit)
        self.playBtn = QtWidgets.QPushButton(self.dockWidgetContents_3)
        self.playBtn.setStyleSheet("QPushButton {\n"
"    color: #2c2c2c;\n"
"    background: rgb(255,153,102);\n"
"    height: 20px;\n"
"    width: 70px;\n"
"    font: bold 12px;\n"
"    border: 1px solid rgb(255,153,102);\n"
"    border-radius: 4px;\n"
"}\n"
"QPushButton::hover {\n"
"    background: rgb(255,128,6);\n"
"    border: 1px solid rgb(255,153,102);\n"
"}\n"
"QPushButton::pressed {\n"
"    background: rgb(255,128,6);\n"
"    border: 1px solid rgb(255,153,102);\n"
"}")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("play.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.playBtn.setIcon(icon)
        self.playBtn.setObjectName("playBtn")
        self.horizontalLayout_1.addWidget(self.playBtn)
        self.pauseBtn = QtWidgets.QPushButton(self.dockWidgetContents_3)
        self.pauseBtn.setStyleSheet("QPushButton {\n"
"    color: #2c2c2c;\n"
"    background: rgb(255,153,102);\n"
"    height: 20px;\n"
"    width: 70px;\n"
"    font: bold 12px;\n"
"    border: 1px solid rgb(255,153,102);\n"
"    border-radius: 4px;\n"
"}\n"
"QPushButton::hover {\n"
"    background: rgb(255,128,6);\n"
"    border: 1px solid rgb(255,153,102);\n"
"}\n"
"QPushButton::pressed {\n"
"    background: rgb(255,128,6);\n"
"    border: 1px solid rgb(255,153,102);\n"
"}")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("pause.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pauseBtn.setIcon(icon1)
        self.pauseBtn.setObjectName("pauseBtn")
        self.horizontalLayout_1.addWidget(self.pauseBtn)
        self.stopBtn = QtWidgets.QPushButton(self.dockWidgetContents_3)
        self.stopBtn.setStyleSheet("QPushButton {\n"
"    color: #2c2c2c;\n"
"    background: rgb(255,153,102);\n"
"    height: 20px;\n"
"    width: 70px;\n"
"    font: bold 12px;\n"
"    border: 1px solid rgb(255,153,102);\n"
"    border-radius: 4px;\n"
"}\n"
"QPushButton::hover {\n"
"    background: rgb(255,128,6);\n"
"    border: 1px solid rgb(255,153,102);\n"
"}\n"
"QPushButton::pressed {\n"
"    background: rgb(255,128,6);\n"
"    border: 1px solid rgb(255,153,102);\n"
"}")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("stop.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.stopBtn.setIcon(icon2)
        self.stopBtn.setObjectName("stopBtn")
        self.horizontalLayout_1.addWidget(self.stopBtn)
        self.verticalLayout_2.addLayout(self.horizontalLayout_1)
        self.dockWidget_3.setWidget(self.dockWidgetContents_3)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.dockWidget_3)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Media Player"))
        self.dockWidget_3.setWindowTitle(_translate("MainWindow", "Control Panel"))
        self.curTimeLabel.setText(_translate("MainWindow", "current"))
        self.endTimeLabel.setText(_translate("MainWindow", "end"))
        self.urlLineEdit.setPlaceholderText(_translate("MainWindow", "rtsp://host:port/path"))
        self.playBtn.setText(_translate("MainWindow", "Play"))
        self.pauseBtn.setText(_translate("MainWindow", "Pause"))
        self.stopBtn.setText(_translate("MainWindow", "Stop"))
