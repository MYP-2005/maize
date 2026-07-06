# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MaizeDesider_GPT1.ui'
##
## Created by: Qt User Interface Compiler version 6.10.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QCheckBox, QComboBox, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1000, 694)
        Form.setStyleSheet(u"QWidget { font-family: \"Microsoft YaHei\"; font-size: 10pt; }\n"
"QGroupBox { font-weight: bold; border: 1px solid #B8B8B8; border-radius: 6px; margin-top: 10px; padding: 8px; }\n"
"QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 4px; }\n"
"QLineEdit, QComboBox { min-height: 26px; }\n"
"QPushButton { min-height: 30px; padding: 4px 12px; }\n"
"QLabel#imageLabelLeft, QLabel#imageLabelRight { background-color: #FAFAFA; border: 1px solid #B8B8B8; }\n"
"QLabel#colorLabel { background-color: white; border: 1px solid black; }")
        self.mainHorizontalLayout = QHBoxLayout(Form)
        self.mainHorizontalLayout.setSpacing(14)
        self.mainHorizontalLayout.setObjectName(u"mainHorizontalLayout")
        self.mainHorizontalLayout.setContentsMargins(16, 16, 16, 16)
        self.leftPanelLayout = QVBoxLayout()
        self.leftPanelLayout.setObjectName(u"leftPanelLayout")
        self.groupBox_ColorFeature = QGroupBox(Form)
        self.groupBox_ColorFeature.setObjectName(u"groupBox_ColorFeature")
        self.gridLayout_ColorFeature = QGridLayout(self.groupBox_ColorFeature)
        self.gridLayout_ColorFeature.setObjectName(u"gridLayout_ColorFeature")
        self.label_H = QLabel(self.groupBox_ColorFeature)
        self.label_H.setObjectName(u"label_H")
        self.label_H.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_ColorFeature.addWidget(self.label_H, 0, 0, 1, 1)

        self.lineEdit_H = QLineEdit(self.groupBox_ColorFeature)
        self.lineEdit_H.setObjectName(u"lineEdit_H")

        self.gridLayout_ColorFeature.addWidget(self.lineEdit_H, 0, 1, 1, 1)

        self.label_S = QLabel(self.groupBox_ColorFeature)
        self.label_S.setObjectName(u"label_S")
        self.label_S.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_ColorFeature.addWidget(self.label_S, 1, 0, 1, 1)

        self.lineEdit_S = QLineEdit(self.groupBox_ColorFeature)
        self.lineEdit_S.setObjectName(u"lineEdit_S")

        self.gridLayout_ColorFeature.addWidget(self.lineEdit_S, 1, 1, 1, 1)

        self.label_V = QLabel(self.groupBox_ColorFeature)
        self.label_V.setObjectName(u"label_V")
        self.label_V.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_ColorFeature.addWidget(self.label_V, 2, 0, 1, 1)

        self.lineEdit_V = QLineEdit(self.groupBox_ColorFeature)
        self.lineEdit_V.setObjectName(u"lineEdit_V")

        self.gridLayout_ColorFeature.addWidget(self.lineEdit_V, 2, 1, 1, 1)

        self.label_DOCI = QLabel(self.groupBox_ColorFeature)
        self.label_DOCI.setObjectName(u"label_DOCI")
        self.label_DOCI.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_ColorFeature.addWidget(self.label_DOCI, 3, 0, 1, 1)

        self.lineEdit_DOCI = QLineEdit(self.groupBox_ColorFeature)
        self.lineEdit_DOCI.setObjectName(u"lineEdit_DOCI")

        self.gridLayout_ColorFeature.addWidget(self.lineEdit_DOCI, 3, 1, 1, 1)

        self.colorLabel = QLabel(self.groupBox_ColorFeature)
        self.colorLabel.setObjectName(u"colorLabel")
        self.colorLabel.setMinimumSize(QSize(96, 96))
        self.colorLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_ColorFeature.addWidget(self.colorLabel, 0, 2, 4, 1)


        self.leftPanelLayout.addWidget(self.groupBox_ColorFeature)

        self.groupBox_ShapeFeature = QGroupBox(Form)
        self.groupBox_ShapeFeature.setObjectName(u"groupBox_ShapeFeature")
        self.gridLayout_ShapeFeature = QGridLayout(self.groupBox_ShapeFeature)
        self.gridLayout_ShapeFeature.setObjectName(u"gridLayout_ShapeFeature")
        self.label_Length = QLabel(self.groupBox_ShapeFeature)
        self.label_Length.setObjectName(u"label_Length")
        self.label_Length.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_ShapeFeature.addWidget(self.label_Length, 0, 0, 1, 1)

        self.lineEdit_Length = QLineEdit(self.groupBox_ShapeFeature)
        self.lineEdit_Length.setObjectName(u"lineEdit_Length")

        self.gridLayout_ShapeFeature.addWidget(self.lineEdit_Length, 0, 1, 1, 1)

        self.label_Width = QLabel(self.groupBox_ShapeFeature)
        self.label_Width.setObjectName(u"label_Width")
        self.label_Width.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_ShapeFeature.addWidget(self.label_Width, 1, 0, 1, 1)

        self.lineEdit_Width = QLineEdit(self.groupBox_ShapeFeature)
        self.lineEdit_Width.setObjectName(u"lineEdit_Width")

        self.gridLayout_ShapeFeature.addWidget(self.lineEdit_Width, 1, 1, 1, 1)

        self.label_Area = QLabel(self.groupBox_ShapeFeature)
        self.label_Area.setObjectName(u"label_Area")
        self.label_Area.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_ShapeFeature.addWidget(self.label_Area, 2, 0, 1, 1)

        self.lineEdit_Area = QLineEdit(self.groupBox_ShapeFeature)
        self.lineEdit_Area.setObjectName(u"lineEdit_Area")

        self.gridLayout_ShapeFeature.addWidget(self.lineEdit_Area, 2, 1, 1, 1)


        self.leftPanelLayout.addWidget(self.groupBox_ShapeFeature)

        self.groupBox_ManualFeature = QGroupBox(Form)
        self.groupBox_ManualFeature.setObjectName(u"groupBox_ManualFeature")
        self.gridLayout_ManualFeature = QGridLayout(self.groupBox_ManualFeature)
        self.gridLayout_ManualFeature.setObjectName(u"gridLayout_ManualFeature")
        self.label_Yield = QLabel(self.groupBox_ManualFeature)
        self.label_Yield.setObjectName(u"label_Yield")
        self.label_Yield.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_ManualFeature.addWidget(self.label_Yield, 0, 0, 1, 1)

        self.lineEdit_Yield = QLineEdit(self.groupBox_ManualFeature)
        self.lineEdit_Yield.setObjectName(u"lineEdit_Yield")

        self.gridLayout_ManualFeature.addWidget(self.lineEdit_Yield, 0, 1, 1, 2)

        self.label_Hweight = QLabel(self.groupBox_ManualFeature)
        self.label_Hweight.setObjectName(u"label_Hweight")
        self.label_Hweight.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_ManualFeature.addWidget(self.label_Hweight, 1, 0, 1, 1)

        self.lineEdit_Hweight = QLineEdit(self.groupBox_ManualFeature)
        self.lineEdit_Hweight.setObjectName(u"lineEdit_Hweight")

        self.gridLayout_ManualFeature.addWidget(self.lineEdit_Hweight, 1, 1, 1, 2)

        self.label_Vol = QLabel(self.groupBox_ManualFeature)
        self.label_Vol.setObjectName(u"label_Vol")
        self.label_Vol.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_ManualFeature.addWidget(self.label_Vol, 2, 0, 1, 1)

        self.lineEdit_Vol = QLineEdit(self.groupBox_ManualFeature)
        self.lineEdit_Vol.setObjectName(u"lineEdit_Vol")

        self.gridLayout_ManualFeature.addWidget(self.lineEdit_Vol, 2, 1, 1, 1)

        self.checkBox_Vol = QCheckBox(self.groupBox_ManualFeature)
        self.checkBox_Vol.setObjectName(u"checkBox_Vol")

        self.gridLayout_ManualFeature.addWidget(self.checkBox_Vol, 2, 2, 1, 1)

        self.label_Tweight = QLabel(self.groupBox_ManualFeature)
        self.label_Tweight.setObjectName(u"label_Tweight")
        self.label_Tweight.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_ManualFeature.addWidget(self.label_Tweight, 3, 0, 1, 1)

        self.lineEdit_Tweight = QLineEdit(self.groupBox_ManualFeature)
        self.lineEdit_Tweight.setObjectName(u"lineEdit_Tweight")

        self.gridLayout_ManualFeature.addWidget(self.lineEdit_Tweight, 3, 1, 1, 1)

        self.checkBox_Tweight = QCheckBox(self.groupBox_ManualFeature)
        self.checkBox_Tweight.setObjectName(u"checkBox_Tweight")

        self.gridLayout_ManualFeature.addWidget(self.checkBox_Tweight, 3, 2, 1, 1)


        self.leftPanelLayout.addWidget(self.groupBox_ManualFeature)

        self.groupBox_Prediction = QGroupBox(Form)
        self.groupBox_Prediction.setObjectName(u"groupBox_Prediction")
        self.gridLayout_Prediction = QGridLayout(self.groupBox_Prediction)
        self.gridLayout_Prediction.setObjectName(u"gridLayout_Prediction")
        self.label_N = QLabel(self.groupBox_Prediction)
        self.label_N.setObjectName(u"label_N")
        self.label_N.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_Prediction.addWidget(self.label_N, 0, 0, 1, 1)

        self.lineEdit_N = QLineEdit(self.groupBox_Prediction)
        self.lineEdit_N.setObjectName(u"lineEdit_N")

        self.gridLayout_Prediction.addWidget(self.lineEdit_N, 0, 1, 1, 1)

        self.label_Nue = QLabel(self.groupBox_Prediction)
        self.label_Nue.setObjectName(u"label_Nue")
        self.label_Nue.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_Prediction.addWidget(self.label_Nue, 1, 0, 1, 1)

        self.lineEdit_Nue = QLineEdit(self.groupBox_Prediction)
        self.lineEdit_Nue.setObjectName(u"lineEdit_Nue")

        self.gridLayout_Prediction.addWidget(self.lineEdit_Nue, 1, 1, 1, 1)


        self.leftPanelLayout.addWidget(self.groupBox_Prediction)


        self.mainHorizontalLayout.addLayout(self.leftPanelLayout)

        self.rightPanelLayout = QVBoxLayout()
        self.rightPanelLayout.setObjectName(u"rightPanelLayout")
        self.groupBox_ImageImport = QGroupBox(Form)
        self.groupBox_ImageImport.setObjectName(u"groupBox_ImageImport")
        self.gridLayout_ImageImport = QGridLayout(self.groupBox_ImageImport)
        self.gridLayout_ImageImport.setObjectName(u"gridLayout_ImageImport")
        self.label_ImageFolder = QLabel(self.groupBox_ImageImport)
        self.label_ImageFolder.setObjectName(u"label_ImageFolder")

        self.gridLayout_ImageImport.addWidget(self.label_ImageFolder, 0, 0, 1, 1)

        self.folderPathLineEdit = QLineEdit(self.groupBox_ImageImport)
        self.folderPathLineEdit.setObjectName(u"folderPathLineEdit")

        self.gridLayout_ImageImport.addWidget(self.folderPathLineEdit, 0, 1, 1, 1)

        self.selectFolderBtn = QPushButton(self.groupBox_ImageImport)
        self.selectFolderBtn.setObjectName(u"selectFolderBtn")

        self.gridLayout_ImageImport.addWidget(self.selectFolderBtn, 0, 2, 1, 1)

        self.label_ImageSearch = QLabel(self.groupBox_ImageImport)
        self.label_ImageSearch.setObjectName(u"label_ImageSearch")

        self.gridLayout_ImageImport.addWidget(self.label_ImageSearch, 1, 0, 1, 1)

        self.imageComboBox = QComboBox(self.groupBox_ImageImport)
        self.imageComboBox.setObjectName(u"imageComboBox")
        self.imageComboBox.setEditable(True)

        self.gridLayout_ImageImport.addWidget(self.imageComboBox, 1, 1, 1, 1)

        self.loadImageBtn = QPushButton(self.groupBox_ImageImport)
        self.loadImageBtn.setObjectName(u"loadImageBtn")

        self.gridLayout_ImageImport.addWidget(self.loadImageBtn, 1, 2, 1, 1)


        self.rightPanelLayout.addWidget(self.groupBox_ImageImport)

        self.groupBox_ImageDisplay = QGroupBox(Form)
        self.groupBox_ImageDisplay.setObjectName(u"groupBox_ImageDisplay")
        self.gridLayout_ImageDisplay = QGridLayout(self.groupBox_ImageDisplay)
        self.gridLayout_ImageDisplay.setObjectName(u"gridLayout_ImageDisplay")
        self.imageLabelLeft = QLabel(self.groupBox_ImageDisplay)
        self.imageLabelLeft.setObjectName(u"imageLabelLeft")
        self.imageLabelLeft.setMinimumSize(QSize(300, 360))
        self.imageLabelLeft.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_ImageDisplay.addWidget(self.imageLabelLeft, 0, 0, 1, 1)

        self.imageLabelRight = QLabel(self.groupBox_ImageDisplay)
        self.imageLabelRight.setObjectName(u"imageLabelRight")
        self.imageLabelRight.setMinimumSize(QSize(300, 360))
        self.imageLabelRight.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_ImageDisplay.addWidget(self.imageLabelRight, 0, 1, 1, 1)


        self.rightPanelLayout.addWidget(self.groupBox_ImageDisplay)

        self.groupBox_Action = QGroupBox(Form)
        self.groupBox_Action.setObjectName(u"groupBox_Action")
        self.gridLayout_Action = QGridLayout(self.groupBox_Action)
        self.gridLayout_Action.setObjectName(u"gridLayout_Action")
        self.extractColorBtn = QPushButton(self.groupBox_Action)
        self.extractColorBtn.setObjectName(u"extractColorBtn")

        self.gridLayout_Action.addWidget(self.extractColorBtn, 0, 0, 1, 1)

        self.predictBtn = QPushButton(self.groupBox_Action)
        self.predictBtn.setObjectName(u"predictBtn")

        self.gridLayout_Action.addWidget(self.predictBtn, 0, 1, 1, 1)

        self.exportExcelBtn = QPushButton(self.groupBox_Action)
        self.exportExcelBtn.setObjectName(u"exportExcelBtn")

        self.gridLayout_Action.addWidget(self.exportExcelBtn, 0, 2, 1, 1)

        self.statusLabel = QLabel(self.groupBox_Action)
        self.statusLabel.setObjectName(u"statusLabel")

        self.gridLayout_Action.addWidget(self.statusLabel, 1, 0, 1, 3)


        self.rightPanelLayout.addWidget(self.groupBox_Action)


        self.mainHorizontalLayout.addLayout(self.rightPanelLayout)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"\u7389\u7c73\u7c7d\u7c92\u989c\u8272\u63d0\u53d6\u4e0e\u6c2e\u542b\u91cf\u9884\u6d4b\u7cfb\u7edf", None))
        self.groupBox_ColorFeature.setTitle(QCoreApplication.translate("Form", u"\u989c\u8272\u7279\u5f81", None))
        self.label_H.setText(QCoreApplication.translate("Form", u"\u8272\u5ea6 H", None))
        self.label_S.setText(QCoreApplication.translate("Form", u"\u9971\u548c\u5ea6 S", None))
        self.label_V.setText(QCoreApplication.translate("Form", u"\u660e\u5ea6 V", None))
        self.label_DOCI.setText(QCoreApplication.translate("Form", u"DOCI", None))
        self.colorLabel.setText(QCoreApplication.translate("Form", u"\u989c\u8272", None))
        self.groupBox_ShapeFeature.setTitle(QCoreApplication.translate("Form", u"\u7c7d\u7c92\u5f62\u6001\u7279\u5f81", None))
        self.label_Length.setText(QCoreApplication.translate("Form", u"\u957f\u5ea6 mm", None))
        self.label_Width.setText(QCoreApplication.translate("Form", u"\u5bbd\u5ea6 mm", None))
        self.label_Area.setText(QCoreApplication.translate("Form", u"\u9762\u79ef mm\u00b2", None))
        self.groupBox_ManualFeature.setTitle(QCoreApplication.translate("Form", u"\u4ea7\u91cf\u4e0e\u8003\u79cd\u6570\u636e", None))
        self.label_Yield.setText(QCoreApplication.translate("Form", u"\u5355\u682a\u4ea7\u91cf g/\u682a", None))
        self.lineEdit_Yield.setPlaceholderText(QCoreApplication.translate("Form", u"\u70d8\u5e72\u540e\u5355\u682a\u7c7d\u7c92\u4ea7\u91cf", None))
        self.label_Hweight.setText(QCoreApplication.translate("Form", u"\u767e\u7c92\u91cd g", None))
        self.label_Vol.setText(QCoreApplication.translate("Form", u"\u767e\u7c92\u4f53\u79ef ml", None))
        self.checkBox_Vol.setText(QCoreApplication.translate("Form", u"\u4f53\u79ef\u6362\u7b97", None))
        self.label_Tweight.setText(QCoreApplication.translate("Form", u"\u5bb9\u91cd g/ml", None))
        self.checkBox_Tweight.setText(QCoreApplication.translate("Form", u"\u5bb9\u91cd\u6362\u7b97", None))
        self.groupBox_Prediction.setTitle(QCoreApplication.translate("Form", u"\u6a21\u578b\u9884\u6d4b\u7ed3\u679c", None))
        self.label_N.setText(QCoreApplication.translate("Form", u"\u7c7d\u7c92\u6c2e\u542b\u91cf N%", None))
        self.label_Nue.setText(QCoreApplication.translate("Form", u"\u6c2e\u6548\u7387 NUEg", None))
        self.groupBox_ImageImport.setTitle(QCoreApplication.translate("Form", u"\u56fe\u7247\u5bfc\u5165\u4e0e\u641c\u7d22", None))
        self.label_ImageFolder.setText(QCoreApplication.translate("Form", u"\u56fe\u7247\u6587\u4ef6\u5939", None))
        self.folderPathLineEdit.setPlaceholderText(QCoreApplication.translate("Form", u"\u8bf7\u9009\u62e9\u56fe\u7247\u6240\u5728\u6587\u4ef6\u5939", None))
        self.selectFolderBtn.setText(QCoreApplication.translate("Form", u"\u9009\u62e9\u6587\u4ef6\u5939", None))
        self.label_ImageSearch.setText(QCoreApplication.translate("Form", u"\u641c\u7d22/\u9009\u62e9\u56fe\u7247", None))
        self.imageComboBox.setPlaceholderText(QCoreApplication.translate("Form", u"\u53ef\u8f93\u5165\u7f16\u53f7", None))
        self.loadImageBtn.setText(QCoreApplication.translate("Form", u"\u5bfc\u5165\u56fe\u7247", None))
        self.groupBox_ImageDisplay.setTitle(QCoreApplication.translate("Form", u"\u56fe\u7247\u663e\u793a\u533a", None))
        self.imageLabelLeft.setText(QCoreApplication.translate("Form", u"\u5de6\u76ee\u76f8\u673a", None))
        self.imageLabelRight.setText(QCoreApplication.translate("Form", u"\u53f3\u76ee\u76f8\u673a", None))
        self.groupBox_Action.setTitle(QCoreApplication.translate("Form", u"\u7a0b\u5e8f\u64cd\u4f5c", None))
        self.extractColorBtn.setText(QCoreApplication.translate("Form", u"\u63d0\u53d6\u989c\u8272\u7279\u5f81", None))
        self.predictBtn.setText(QCoreApplication.translate("Form", u"\u9884\u6d4b\u6c2e\u542b\u91cf", None))
        self.exportExcelBtn.setText(QCoreApplication.translate("Form", u"\u5bfc\u51fa Excel", None))
        self.statusLabel.setText(QCoreApplication.translate("Form", u"\u72b6\u6001\uff1a\u7b49\u5f85\u5bfc\u5165\u56fe\u7247", None))
    # retranslateUi

