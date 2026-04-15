import sys
from builtins import IndexError
import qdarkstyle
import os
from datetime import datetime as dt
import shutil
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2 import *
import pandas as pd
import glob
from openpyxl import load_workbook
from openpyxl.utils import *
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import json
import pandas as pd
import numpy as np
import ActionFinderModule as afm
import tools5dot2
import main_cluster_maker as mcm


from pathlib import Path

from functools import partial
from scen_gen import update_table

ROOT_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class ActionTools(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.afmodule = None
        #self.afmodule = afm.ActionFinder()

    def initUI(self):
        self.totalVLayout = QVBoxLayout(self)
        self.totalVLayout.setObjectName(u"totalVLayout")
        self.totalVLayout.setContentsMargins(20, 20, 20, 20)
        self.totalVLayout.setSpacing(15)
        # scrollbar = QScrollArea(widgetResizable=True)
        # scrollbar.setWidget(self)
        self.logoTitleHLayout = QHBoxLayout()
        self.logoTitleHLayout.setSpacing(10)
        self.logoTitleHLayout.setObjectName(u"fileBrowse1HLayout")

        self.lblLogo = QLabel(self)
        pixmap = QPixmap(os.path.join(ROOT_PATH, 'HTML_ASSETS/resources/logo_white.png'))
        self.lblLogo.setPixmap(pixmap)
        self.lblLogo.setScaledContents(True)
        self.lblLogo.setMaximumHeight(50)
        self.lblLogo.setMaximumWidth(300)
        self.logoTitleHLayout.addWidget(self.lblLogo)

        self.lblTitle = QLabel(self)
        self.lblTitle.setText("Action Finder Tool")
        self.lblTitle.setAlignment(Qt.AlignCenter)
        self.lblTitle.setFont(QFont("Arial", 20, QFont.Bold))
        self.logoTitleHLayout.addWidget(self.lblTitle)

        self.totalVLayout.addLayout(self.logoTitleHLayout)

        self.VEntryLayout = QVBoxLayout(self)
        self.VEntryLayout.setAlignment(Qt.AlignTop)
        self.VEntryLayout.setObjectName(u"VEntryLayout")

        configFileLayout = QVBoxLayout()
        configFileLayout.setAlignment(Qt.AlignTop)
        configFileLayout.setSpacing(10)
        configFileLabel = QLabel(self)
        configFileLabel.setText(" Select Folder with CSV Files")
        configFileLayout.addWidget(configFileLabel)

        configFileBrowseHLayout = QHBoxLayout()
        configFileBrowseHLayout.setAlignment(Qt.AlignTop)
        configFileBrowseHLayout.setSpacing(10)
        configFileBrowseHLayout.setObjectName(u"configFileBrowseHLayout")

        self.configFilePath = QLineEdit(self)
        self.configFilePath.setObjectName(u"configFilePath")
        self.configFilePath.setReadOnly(True)

        configFileBrowseHLayout.addWidget(self.configFilePath)

        configFileBrowseBtn = QPushButton(self)
        configFileBrowseBtn.setObjectName(u"configFileBrowseBtn")
        configFileBrowseBtn.setMinimumSize(QSize(80, 0))
        configFileBrowseBtn.setText("Load File")
        configFileBrowseBtn.clicked.connect(self.configFileBrowseBtnClicked)

        configFileBrowseHLayout.addWidget(configFileBrowseBtn)
        configFileLayout.addLayout(configFileBrowseHLayout)

        self.totalVLayout.addLayout(configFileLayout)

        self.pteLog = QPlainTextEdit(self)
        self.pteLog.setObjectName(u"pteLog")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.pteLog.sizePolicy().hasHeightForWidth())
        self.pteLog.setSizePolicy(sizePolicy)
        self.pteLog.setMinimumSize(QSize(0, 200))
        self.pteLog.setMaximumSize(QSize(16777215, 400))

        self.totalVLayout.addWidget(self.pteLog)

        self.btnClearSettings = QPushButton(self)
        self.btnClearSettings.setObjectName(u"btnClearSettings")
        self.btnClearSettings.setText("Clear")
        # self.btnClearSettings.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.btnClearSettings.clicked.connect(self.clearSettingsFunc)

        self.btnSaveSetting = QPushButton(self)
        self.btnSaveSetting.setObjectName(u"btnSaveSetting")
        self.btnSaveSetting.setText("Save Setting")
        self.btnSaveSetting.clicked.connect(self.btnSaveSetting_clicked)

        self.horizontalLayout_31 = QHBoxLayout()
        self.horizontalLayout_31.setSpacing(20)
        self.horizontalLayout_31.setObjectName(u"horizontalLayout_31")
        self.horizontalLayout_31.setContentsMargins(20, -1, 20, -1)

        self.horizontalLayout_31.addWidget(self.btnClearSettings)
        self.horizontalLayout_31.addWidget(self.btnSaveSetting)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(20)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(20, -1, 20, -1)

        self.btnGenerate = QPushButton(self)
        self.btnGenerate.setObjectName(u"btnGenerate")
        self.btnGenerate.clicked.connect(self.btnGenerate_clicked)
        self.horizontalLayout_3.addWidget(self.btnGenerate)

        self.btnShow = QPushButton(self)
        self.btnShow.setObjectName(u"btnShow")
        self.btnShow.clicked.connect(self.btnShow_clicked)
        self.horizontalLayout_3.addWidget(self.btnShow)

        self.totalVLayout.addLayout(self.horizontalLayout_31)
        self.totalVLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi()

        self.config = []

        self.setGeometry(0, 0, 800, 640)
        self.setWindowTitle('S.A.M.T. - Actions')
        self.show()

    def retranslateUi(self):
        self.btnGenerate.setText(QCoreApplication.translate("Form", u"Generate Results", None))
        self.btnShow.setText(QCoreApplication.translate("Form", u"Show Results", None))

    @pyqtSlot()
    def clearSettingsFunc(self):

        self.config = []
        self.configFilePath.clear()

        self.pteLog.setPlainText("")

    def closeEvent(self, event):
        pass
        # if os.path.isfile("./config.cfg"):
        #     os.remove("./config.cfg")

    def configFileBrowseBtnClicked(self):
        folderPath = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folderPath:
            self.configFilePath.setText(folderPath)

            self.folderPath = folderPath

           
            self.pteLog.setPlainText(self.pteLog.toPlainText() + "\nReference scenario file loaded...")

        else:
            return

    @pyqtSlot()
    def btnSaveSetting_clicked(self):
        pass

    def loadSetting(self):
        pass

    @pyqtSlot()
    def btnGenerate_clicked(self):
        print("Generating Result")
        for filename in glob.glob(os.path.join(self.folderPath, "*.csv")):
            self.afmodule = afm.ActionFinder(indicator_filename=filename, qtable_filename='../files/Q_learning_approach.xlsx')
            self.afmodule.calculateHML()
            self.afmodule.calculateAllPossibleAction()
            self.afmodule.findingAction()
            self.afmodule.actions_to_csv()
            self.afmodule.actions_to_html()
            self.afmodule.compute_flexibility()
            self.afmodule.flexibility_to_csv()
            self.pteLog.setPlainText(self.pteLog.toPlainText() + "\nResult Generated")

        pass

    @pyqtSlot()
    def btnShow_clicked(self):
        print("Show Result")

        self.afmodule.show()
        self.pteLog.setPlainText(self.pteLog.toPlainText() + "\nGenerated Actions File Created")

        pass


class Tools52(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.totalVLayout = QVBoxLayout(self)
        self.totalVLayout.setObjectName(u"totalVLayout")
        self.totalVLayout.setContentsMargins(20, 20, 20, 20)
        self.totalVLayout.setSpacing(15)
        # scrollbar = QScrollArea(widgetResizable=True)
        # scrollbar.setWidget(self)
        self.logoTitleHLayout = QHBoxLayout()
        self.logoTitleHLayout.setSpacing(10)
        self.logoTitleHLayout.setObjectName(u"fileBrowse1HLayout")

        self.lblLogo = QLabel(self)
        pixmap = QPixmap(os.path.join(ROOT_PATH, 'HTML_ASSETS/resources/logo_white.png'))
        self.lblLogo.setPixmap(pixmap)
        self.lblLogo.setScaledContents(True)
        self.lblLogo.setMaximumHeight(50)
        self.lblLogo.setMaximumWidth(300)
        self.logoTitleHLayout.addWidget(self.lblLogo)

        self.lblTitle = QLabel(self)
        self.lblTitle.setText("Tool 5.2")
        self.lblTitle.setAlignment(Qt.AlignCenter)
        self.lblTitle.setFont(QFont("Arial", 20, QFont.Bold))
        self.logoTitleHLayout.addWidget(self.lblTitle)

        self.totalVLayout.addLayout(self.logoTitleHLayout)

        self.VEntryLayout = QVBoxLayout(self)
        self.VEntryLayout.setAlignment(Qt.AlignTop)
        self.VEntryLayout.setObjectName(u"VEntryLayout")

        configFileLayout = QVBoxLayout()
        configFileLayout.setAlignment(Qt.AlignTop)
        configFileLayout.setSpacing(10)
        configFileLabel = QLabel(self)
        configFileLabel.setText(" Select Folder with CSV Files")
        configFileLayout.addWidget(configFileLabel)

        configFileBrowseHLayout = QHBoxLayout()
        configFileBrowseHLayout.setAlignment(Qt.AlignTop)
        configFileBrowseHLayout.setSpacing(10)
        configFileBrowseHLayout.setObjectName(u"configFileBrowseHLayout")

        self.configFilePath = QLineEdit(self)
        self.configFilePath.setObjectName(u"configFilePath")
        self.configFilePath.setReadOnly(True)

        configFileBrowseHLayout.addWidget(self.configFilePath)

        configFileBrowseBtn = QPushButton(self)
        configFileBrowseBtn.setObjectName(u"configFileBrowseBtn")
        configFileBrowseBtn.setMinimumSize(QSize(80, 0))
        configFileBrowseBtn.setText("Load File")
        configFileBrowseBtn.clicked.connect(self.configFileBrowseBtnClicked)

        configFileBrowseHLayout.addWidget(configFileBrowseBtn)
        configFileLayout.addLayout(configFileBrowseHLayout)

        self.totalVLayout.addLayout(configFileLayout)

        self.pteLog = QPlainTextEdit(self)
        self.pteLog.setObjectName(u"pteLog")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.pteLog.sizePolicy().hasHeightForWidth())
        self.pteLog.setSizePolicy(sizePolicy)
        self.pteLog.setMinimumSize(QSize(0, 200))
        self.pteLog.setMaximumSize(QSize(16777215, 400))

        self.totalVLayout.addWidget(self.pteLog)

        self.btnClearSettings = QPushButton(self)
        self.btnClearSettings.setObjectName(u"btnClearSettings")
        self.btnClearSettings.setText("Clear")
        # self.btnClearSettings.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.btnClearSettings.clicked.connect(self.clearSettingsFunc)

        self.btnSaveSetting = QPushButton(self)
        self.btnSaveSetting.setObjectName(u"btnSaveSetting")
        self.btnSaveSetting.setText("Save Setting")
        self.btnSaveSetting.clicked.connect(self.btnSaveSetting_clicked)

        self.horizontalLayout_31 = QHBoxLayout()
        self.horizontalLayout_31.setSpacing(20)
        self.horizontalLayout_31.setObjectName(u"horizontalLayout_31")
        self.horizontalLayout_31.setContentsMargins(20, -1, 20, -1)

        self.horizontalLayout_31.addWidget(self.btnClearSettings)
        self.horizontalLayout_31.addWidget(self.btnSaveSetting)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(20)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(20, -1, 20, -1)

        self.btnGenerate = QPushButton(self)
        self.btnGenerate.setObjectName(u"btnGenerate")
        self.btnGenerate.clicked.connect(self.btnGenerate_clicked)
        self.horizontalLayout_3.addWidget(self.btnGenerate)

        self.btnShow = QPushButton(self)
        self.btnShow.setObjectName(u"btnShow")
        self.btnShow.clicked.connect(self.btnShow_clicked)
        self.horizontalLayout_3.addWidget(self.btnShow)

        self.totalVLayout.addLayout(self.horizontalLayout_31)
        self.totalVLayout.addLayout(self.horizontalLayout_3)

        self.retranslateUi()

        self.config = []

        self.setGeometry(0, 0, 800, 640)
        self.setWindowTitle('WP 5.3 Tools')
        self.show()

    def retranslateUi(self):
        self.btnGenerate.setText(QCoreApplication.translate("Form", u"Generate Result", None))
        self.btnShow.setText(QCoreApplication.translate("Form", u"Show Result", None))

    @pyqtSlot()
    def clearSettingsFunc(self):

        self.config = []
        self.configFilePath.clear()

        self.pteLog.setPlainText("")

    def closeEvent(self, event):
        pass
        # if os.path.isfile("./config.cfg"):
        #     os.remove("./config.cfg")

    def configFileBrowseBtnClicked(self):
        folderPath = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folderPath:
            self.configFilePath.setText(folderPath)

            self.folderPath = folderPath
            
            self.pteLog.setPlainText(self.pteLog.toPlainText() + "\nReference scenario file loaded...")

        else:
            return

    @pyqtSlot()
    def btnSaveSetting_clicked(self):
        pass

    def loadSetting(self):
        pass

    @pyqtSlot()
    def btnGenerate_clicked(self):
        print("Generating Result")

        pass

        self.pteLog.setPlainText(self.pteLog.toPlainText() + "\nResult Generated")
        
        mcm.input_data_2(self.folderPath)

        pass

    @pyqtSlot()
    def btnShow_clicked(self):
        print("Show Result")

        folder_name = self.folderPath.split('/')[-1] if len(self.folderPath.split('/')) != 0 else self.folderPath.split('\\')[-1]

        output_path = os.path.join(
            os.path.abspath(
                os.path.join(
                    os.getcwd(),
                    os.pardir
                )
            ),
            'Result',
            'Clustering and Table',
            folder_name
        )

        mcm.show(output_path)
        pass

        self.pteLog.setPlainText(self.pteLog.toPlainText() + "\nGenerated Actions File Created")

        pass


class Example(QWidget):

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.totalVLayout = QVBoxLayout(self)
        self.totalVLayout.setObjectName(u"totalVLayout")
        self.totalVLayout.setContentsMargins(20, 20, 20, 20)
        self.totalVLayout.setSpacing(15)
        # scrollbar = QScrollArea(widgetResizable=True)
        # scrollbar.setWidget(self)
        self.logoTitleHLayout = QHBoxLayout()
        self.logoTitleHLayout.setSpacing(10)
        self.logoTitleHLayout.setObjectName(u"fileBrowse1HLayout")

        self.lblLogo = QLabel(self)
        pixmap = QPixmap(os.path.join(ROOT_PATH, 'HTML_ASSETS/resources/logo_white.png'))
        self.lblLogo.setPixmap(pixmap)
        self.lblLogo.setScaledContents(True)
        self.lblLogo.setMaximumHeight(50)
        self.lblLogo.setMaximumWidth(300)
        self.logoTitleHLayout.addWidget(self.lblLogo)

        self.lblTitle = QLabel(self)
        self.lblTitle.setText("Smart Asset Management Tool")
        self.lblTitle.setAlignment(Qt.AlignCenter)
        self.lblTitle.setFont(QFont("Arial", 20, QFont.Bold))
        self.logoTitleHLayout.addWidget(self.lblTitle)

        self.totalVLayout.addLayout(self.logoTitleHLayout)

        self.VEntryLayout = QVBoxLayout(self)
        self.VEntryLayout.setAlignment(Qt.AlignTop)
        self.VEntryLayout.setObjectName(u"VEntryLayout")

        configFileLayout = QVBoxLayout()
        configFileLayout.setAlignment(Qt.AlignTop)
        configFileLayout.setSpacing(10)
        configFileLabel = QLabel(self)
        configFileLabel.setText(" Select Config File")
        configFileLayout.addWidget(configFileLabel)

        configFileBrowseHLayout = QHBoxLayout()
        configFileBrowseHLayout.setAlignment(Qt.AlignTop)
        configFileBrowseHLayout.setSpacing(10)
        configFileBrowseHLayout.setObjectName(u"configFileBrowseHLayout")

        self.configFilePath = QLineEdit(self)
        self.configFilePath.setObjectName(u"configFilePath")
        self.configFilePath.setReadOnly(True)

        configFileBrowseHLayout.addWidget(self.configFilePath)

        configFileBrowseBtn = QPushButton(self)
        configFileBrowseBtn.setObjectName(u"configFileBrowseBtn")
        configFileBrowseBtn.setMinimumSize(QSize(80, 0))
        configFileBrowseBtn.setText("Load File")
        configFileBrowseBtn.clicked.connect(self.configFileBrowseBtnClicked)

        configFileBrowseHLayout.addWidget(configFileBrowseBtn)
        configFileLayout.addLayout(configFileBrowseHLayout)

        self.totalVLayout.addLayout(configFileLayout)


        scenarioLayout = QGridLayout()

        verticalLayoutRegin = QVBoxLayout()
        verticalLayoutRegin.setAlignment(Qt.AlignTop)
        verticalLayoutRegin.setObjectName(u"verticalLayoutScenario")
        scenarioLabel = QLabel(self)
        scenarioLabel.setText("Select Number of Scenarios")
        verticalLayoutRegin.addWidget(scenarioLabel)

        self.scenarioCB = QComboBox()
        self.scenarioCB.addItems(map(str, [5, 10, 15, 20, 25]))
        self.scenarioCB.currentTextChanged.connect(self.onScenarioChanged)
        self.year = 5

        verticalLayoutRegin.addWidget(self.scenarioCB)

        scenarioLayout.addLayout(verticalLayoutRegin, 0, 0)

        verticalLayout_1 = QVBoxLayout()
        verticalLayout_1.setAlignment(Qt.AlignTop)
        verticalLayout_1.setObjectName(u"verticalLayout")
        label_1 = QLabel(self)
        label_1.setText("Name of Assets:")
        verticalLayout_1.addWidget(label_1)

        self.nameAssetsEdit = QLineEdit(self)
        self.nameAssetsEdit.setObjectName(u"nameAssetsEdit")
        self.nameAssetsEdit.textChanged.connect(self.onAssetsChange)

        verticalLayout_1.addWidget(self.nameAssetsEdit)

        scenarioLayout.addLayout(verticalLayout_1, 0, 1)

        scenarioLayout.setColumnStretch(0, 1)
        scenarioLayout.setColumnStretch(1, 2)

        self.totalVLayout.addLayout(scenarioLayout)

        self.pteLog = QPlainTextEdit(self)
        self.pteLog.setObjectName(u"pteLog")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.pteLog.sizePolicy().hasHeightForWidth())
        self.pteLog.setSizePolicy(sizePolicy)
        self.pteLog.setMinimumSize(QSize(0, 200))
        self.pteLog.setMaximumSize(QSize(16777215, 400))

        self.totalVLayout.addWidget(self.pteLog)

        self.btnClearSettings = QPushButton(self)
        self.btnClearSettings.setObjectName(u"btnClearSettings")
        self.btnClearSettings.setText("Clear")
        # self.btnClearSettings.setSizePolicy(QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed))
        self.btnClearSettings.clicked.connect(self.clearSettingsFunc)

        self.btnSaveSetting = QPushButton(self)
        self.btnSaveSetting.setObjectName(u"btnSaveSetting")
        self.btnSaveSetting.setText("Save Settings")
        self.btnSaveSetting.clicked.connect(self.btnSaveSetting_clicked)

        self.horizontalLayout_31 = QHBoxLayout()
        self.horizontalLayout_31.setSpacing(20)
        self.horizontalLayout_31.setObjectName(u"horizontalLayout_31")
        self.horizontalLayout_31.setContentsMargins(20, -1, 20, -1)

        self.horizontalLayout_31.addWidget(self.btnClearSettings)
        self.horizontalLayout_31.addWidget(self.btnSaveSetting)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(20)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(20, -1, 20, -1)

        self.btnGenerate = QPushButton(self)
        self.btnGenerate.setObjectName(u"btnGenerate")
        self.btnGenerate.clicked.connect(self.btnGenerate_clicked)
        self.horizontalLayout_3.addWidget(self.btnGenerate)

        self.btnShow = QPushButton(self)
        self.btnShow.setObjectName(u"btnShow")
        self.btnShow.clicked.connect(self.btnShow_clicked)
        self.horizontalLayout_3.addWidget(self.btnShow)

        self.totalVLayout.addLayout(self.horizontalLayout_31)
        self.totalVLayout.addLayout(self.horizontalLayout_3)

        self.btnTools = QPushButton(self)
        self.btnTools.setObjectName(u"btnTools")
        self.btnTools.setText("Run Tools 5.2")
        self.btnTools.setStyleSheet("background-color: red; font-size:22px;")
        self.btnTools.clicked.connect(self.btnTools_clicked)

        self.totalVLayout.addWidget(self.btnTools)

        self.btnTools = QPushButton(self)
        self.btnTools.setObjectName(u"btnActionTools")
        self.btnTools.setText("Run Action Tools")
        self.btnTools.setStyleSheet("background-color: red; font-size:22px;")
        self.btnTools.clicked.connect(self.btnActions_clicked)

        self.totalVLayout.addWidget(self.btnTools)

        self.retranslateUi()

        self.config = []
        self.assets = None

        self.setGeometry(0, 0, 800, 640)
        self.setWindowTitle('WP 5.3 Tools')
        self.show()

    def retranslateUi(self):
        self.btnGenerate.setText(QCoreApplication.translate("Form", u"Generate Result", None))
        self.btnShow.setText(QCoreApplication.translate("Form", u"Show Result", None))

    @pyqtSlot()
    def clearSettingsFunc(self):

        self.config = []
        self.configFilePath.clear()

        self.pteLog.setPlainText("")

    def closeEvent(self, event):
        pass
        # if os.path.isfile("./config.cfg"):
        #     os.remove("./config.cfg")

    def onScenarioChanged(self, text):
        self.year = int(text)

    def onAssetsChange(self):
        self.assets = self.nameAssetsEdit.text()

    def configFileBrowseBtnClicked(self):
        filePath, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*)")
        if filePath:
            self.configFilePath.setText(filePath)

            filename, file_extension = os.path.splitext(filePath)
            print(file_extension)
            with open(filePath, 'r') as f:
                self.config = json.load(f)
            self.pteLog.setPlainText(self.pteLog.toPlainText() + "\nReference scenario file loaded...")
            self.pteLog.setPlainText(
                self.pteLog.toPlainText() + "\n" + json.dumps(self.config, indent=4, sort_keys=True))

        else:
            return

    @pyqtSlot()
    def btnSaveSetting_clicked(self):
        pass

    def loadSetting(self):
        pass

    def value_error_dialog(self):
        dlg = QMessageBox(self)
        dlg.setGeometry(400, 400, 400, 150)
        dlg.setWindowTitle("Error")
        dlg.setText("Variables not found in Configuration file\n Do you want to open Configuration File?")
        dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        button = dlg.exec_()

        if button == QMessageBox.Yes:
            path_conf_file= "../files/ConfigurationFile.csv"
            os.system(f"start EXCEL.EXE {path_conf_file}")

    def name_of_asset_not_entered(self):
        dlg = QMessageBox(self)
        dlg.setGeometry(400, 400, 400, 150)
        dlg.setWindowTitle("Error")
        dlg.setText("Please enter the name of assets")
        dlg.exec_()

    @pyqtSlot()
    def btnGenerate_clicked(self):
        if self.assets == None or self.assets == '':
            self.name_of_asset_not_entered()
            return

        for config in self.config:
            path_ref_file = config["path"]
            path_conf_file= "../files/ConfigurationFile.csv"
            years = self.year
            var_list = config["variables"]
            var_time = ""
            var_name = config["index"]

            try:
                update_table(path_ref_file,path_conf_file, years,var_list,var_time,var_name, self.assets)
            except IndexError:
                self.value_error_dialog()
                return

            print("Generating Result")

        wp52_output_path = os.path.join("../Result/Result from tools5.2", self.assets)
        os.makedirs(wp52_output_path, exist_ok=True)


        print(tools5dot2.tool5dot2_calculate(self.config, 
                                             file_name=self.assets,
                                             years=self.year, 
                                             save_results_to=wp52_output_path))


    @pyqtSlot()
    def btnShow_clicked(self):
        print("Show Result")
        pass

    @pyqtSlot()
    def btnTools_clicked(self):
        print("Run Tools 5.2")

        self.w = Tools52()
        self.w.show()
        pass

    @pyqtSlot()
    def btnActions_clicked(self):
        print("Run Action Tools")

        self.w = ActionTools()
        self.w.show()
        pass


def main():
    app = QApplication(sys.argv)

    ex = Example()
    app.setStyleSheet(qdarkstyle.load_stylesheet(palette=qdarkstyle.DarkPalette()))
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
