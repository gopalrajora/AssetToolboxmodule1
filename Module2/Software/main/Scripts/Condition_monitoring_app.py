import sys
import qdarkstyle
import os
import shutil

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from PySide2 import *
import pandas as pd
import xlrd
from openpyxl import load_workbook
from openpyxl.utils import *
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import json

sys.path.append("..")
from chart.lib.main_condition_monitoring import *

class SingleCheckProxyModel(QIdentityProxyModel):

    def __init__(self, model, parent=None):
        super().__init__(parent)
        model.itemChanged.connect(self.checkSingleCheck)
        self.setSourceModel(model)
        self.currentItemChecked = None

    def checkSingleCheck(self, item):
        if self.currentItemChecked:
            self.currentItemChecked.setCheckState(Qt.Unchecked)
        if item.checkState(): # Allows the user to uncheck then check the same item
            self.currentItemChecked = item
        else:
            self.currentItemChecked = None

class ChecklistDialog(QtWidgets.QDialog):

    def __init__(
            self,
            name,
            stringlist=None,
            checked=False,
            icon=None,
            parent=None,
    ):
        super(ChecklistDialog, self).__init__(parent)

        self.name = name
        self.icon = icon
        self.choices = ""
        self.model = QtGui.QStandardItemModel()
        self.listView = QListView()

        for string in stringlist:
            item = QtGui.QStandardItem(string)
            item.setCheckable(True)
            item.setEditable(False)
            check = (QtCore.Qt.Checked if checked else QtCore.Qt.Unchecked)
            item.setCheckState(check)
            self.model.appendRow(item)

        self.listView.setModel(SingleCheckProxyModel(self.model))
        self.listView.setCurrentIndex(self.model.index(0, 0))

        self.okButton = QPushButton('OK')
        self.cancelButton = QPushButton('Cancel')

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addWidget(self.okButton)
        hbox.addWidget(self.cancelButton)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.listView)
        vbox.addLayout(hbox)
        self.setWindowTitle(self.name)
        if self.icon:
            self.setWindowIcon(self.icon)

        self.okButton.clicked.connect(self.onAccepted)
        self.cancelButton.clicked.connect(self.reject)

    def onAccepted(self):
        if self.listView.selectedIndexes().__len__() != 1:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('Please select only one field')
            msg.setWindowTitle("Error")
            msg.exec_()
            return
        checked = self.model.match(
            self.model.index(0, 0), QtCore.Qt.CheckStateRole,
            QtCore.Qt.Checked, -1,
            QtCore.Qt.MatchExactly | QtCore.Qt.MatchRecursive)
        for index in checked:
            item = self.model.itemFromIndex(index)
            item = self.model.itemFromIndex(index)
            self.choices = item.text()

        if self.choices == "":
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Error")
            msg.setInformativeText('Please select only one field')
            msg.setWindowTitle("Error")
            msg.exec_()
            return
        else:
            self.accept()


class Example(QtWidgets.QDialog):

    def __init__(self):
        super().__init__()

        self.initUI()

        self.selectedVariables = ""


    def initUI(self):

        self.modelpath1 = ""
        self.modelpath2 = ""

        # path for xlsx, csv, xls file
        self.filepath2 = ""

        self.totalVLayout = QVBoxLayout(self)
        self.totalVLayout.setObjectName(u"totalVLayout")
        self.totalVLayout.setContentsMargins(20, 20, 20, 20)
        self.totalVLayout.setSpacing(15)

        self.logoTitleHLayout = QHBoxLayout()
        self.logoTitleHLayout.setSpacing(10)
        self.logoTitleHLayout.setObjectName(u"fileBrowse1HLayout")

        self.lblLogo = QLabel(self)
        pixmap = QPixmap('static/resources/logo_white.png')
        self.lblLogo.setPixmap(pixmap)
        self.lblLogo.setScaledContents(True)
        self.lblLogo.setMaximumHeight(50)
        self.lblLogo.setMaximumWidth(300)
        self.logoTitleHLayout.addWidget(self.lblLogo)

        self.lblTitle = QLabel(self)
        self.lblTitle.setText("Condition Monitoring for Transformers")
        self.lblTitle.setAlignment(Qt.AlignCenter)
        self.lblTitle.setFont(QFont("Arial", 18))
        self.logoTitleHLayout.addWidget(self.lblTitle)

        self.totalVLayout.addLayout(self.logoTitleHLayout)

        self.VEntryLayout = QVBoxLayout(self)
        self.VEntryLayout.setObjectName(u"VEntryLayout")

        self.firstVLayout = QVBoxLayout()
        self.firstVLayout.setSpacing(10)

        self.fileBrowseHLayout1 = QHBoxLayout()
        self.fileBrowseHLayout1.setSpacing(10)
        self.fileBrowseHLayout1.setObjectName(u"fileBrowseHLayout1")
        self.filePathLineEdit1 = QLineEdit(self)
        self.filePathLineEdit1 .setObjectName(u"txtFilePath1")
        self.filePathLineEdit1 .setReadOnly(True)

        self.fileBrowseHLayout1.addWidget(self.filePathLineEdit1)

        self.fileOpenBtn1 = QPushButton(self)
        self.fileOpenBtn1.setObjectName(u"btnBrowse1")
        self.fileOpenBtn1.setMinimumSize(QSize(80, 0))
        self.fileOpenBtn1.setText("Browse")
        self.fileOpenBtn1.clicked.connect(self.btnBrowse1_clicked)

        self.fileBrowseHLayout1.addWidget(self.fileOpenBtn1)


        self.firstLabel1 = QLabel(self)
        self.firstLabel1.setText(" Model Path")

        self.firstVLayout.addWidget(self.firstLabel1)
        self.firstVLayout.addLayout(self.fileBrowseHLayout1)

        self.fileBrowseHLayout2 = QHBoxLayout()
        self.fileBrowseHLayout2.setSpacing(10)
        self.fileBrowseHLayout2.setObjectName(u"fileBrowseHLayout2")
        self.filePathLineEdit3 = QLineEdit(self)
        self.filePathLineEdit3 .setObjectName(u"txtFilePath2")
        self.filePathLineEdit3 .setReadOnly(True)

        self.fileBrowseHLayout2.addWidget(self.filePathLineEdit3)

        self.fileOpenBtn2 = QPushButton(self)
        self.fileOpenBtn2.setObjectName(u"btnBrowse1")
        self.fileOpenBtn2.setMinimumSize(QSize(80, 0))
        self.fileOpenBtn2.setText("Browse")
        self.fileOpenBtn2.clicked.connect(self.btnBrowse3_clicked)

        self.fileBrowseHLayout2.addWidget(self.fileOpenBtn2)


        self.firstLabel2 = QLabel(self)
        self.firstLabel2.setText(" Threshold Configuration Path")

        self.firstVLayout.addWidget(self.firstLabel2)
        self.firstVLayout.addLayout(self.fileBrowseHLayout2)



        self.firstLabel = QLabel(self)
        self.firstLabel.setText(" Input file Path")
        self.firstVLayout.addWidget(self.firstLabel)

        self.fileBrowseHLayout = QHBoxLayout()
        self.fileBrowseHLayout.setSpacing(10)
        self.fileBrowseHLayout.setObjectName(u"fileBrowseHLayout")

        self.firstVLayout.addLayout(self.fileBrowseHLayout)
        self.VEntryLayout.addLayout(self.firstVLayout)

        self.selectComponentVariableHLayout = QHBoxLayout()
        self.selectComponentVariableHLayout.setSpacing(15)
        self.selectComponentVariableHLayout.setObjectName(u"selectComponentVariableHLayout")
        self.filePathLineEdit2 = QLineEdit(self)
        self.filePathLineEdit2.setObjectName(u"txtFilePath")
        self.filePathLineEdit2.setReadOnly(True)

        self.fileBrowseHLayout.addWidget(self.filePathLineEdit2)

        self.fileOpenBtn2 = QPushButton(self)
        self.fileOpenBtn2.setObjectName(u"btnBrowse")
        self.fileOpenBtn2.setMinimumSize(QSize(80, 0))
        self.fileOpenBtn2.setText("Browse")
        self.fileOpenBtn2.clicked.connect(self.btnBrowse2_clicked)

        self.fileBrowseHLayout.addWidget(self.fileOpenBtn2)

        self.firstVLayout.addLayout(self.fileBrowseHLayout)

        secondVLayout = QVBoxLayout()
        secondVLayout.setSpacing(10)
        secondLabel = QLabel(self)
        secondLabel.setText(" Variables Selections")
        secondVLayout.addWidget(secondLabel)

        self.treeWidget1 = QTreeWidget(self)
        __qtreewidgetitem = QTreeWidgetItem(self.treeWidget1)
        __qtreewidgetitem.setCheckState(0, Qt.Checked)
        __qtreewidgetitem1 = QTreeWidgetItem(__qtreewidgetitem)
        __qtreewidgetitem1.setCheckState(0, Qt.Checked)
        __qtreewidgetitem4 = QTreeWidgetItem(__qtreewidgetitem)
        __qtreewidgetitem4.setCheckState(0, Qt.Checked)
        self.treeWidget1.setObjectName(u"twDynamic1")
        self.treeWidget1.header().setVisible(True)

        self.treeWidget1.itemClicked.connect(self.treeWidget1_onItemClicked)

        self.treeWidget1.headerItem().setText(0, "Current (A)")
        self.treeWidget2 = QTreeWidget(self)

        __qtreewidgetitem = QTreeWidgetItem(self.treeWidget2)
        __qtreewidgetitem.setCheckState(0, Qt.Checked)
        __qtreewidgetitem1 = QTreeWidgetItem(__qtreewidgetitem)
        __qtreewidgetitem1.setCheckState(0, Qt.Checked)
        __qtreewidgetitem4 = QTreeWidgetItem(__qtreewidgetitem)
        __qtreewidgetitem4.setCheckState(0, Qt.Checked)
        self.treeWidget2.setObjectName(u"twDynamic2")

        self.treeWidget2.header().setVisible(True)
        self.treeWidget2.itemClicked.connect(self.treeWidget2_onItemClicked)
        self.treeWidget2.headerItem().setText(0, "Oil Temperature (ºC)")

        self.treeWidget3 = QTreeWidget(self)
        __qtreewidgetitem = QTreeWidgetItem(self.treeWidget3)
        __qtreewidgetitem.setCheckState(0, Qt.Checked)
        __qtreewidgetitem1 = QTreeWidgetItem(__qtreewidgetitem)
        __qtreewidgetitem1.setCheckState(0, Qt.Checked)
        __qtreewidgetitem4 = QTreeWidgetItem(__qtreewidgetitem)
        __qtreewidgetitem4.setCheckState(0, Qt.Checked)
        self.treeWidget3.setObjectName(u"twDynamic3")
        self.treeWidget3.header().setVisible(True)
        self.treeWidget3.itemClicked.connect(self.treeWidget3_onItemClicked)
        self.treeWidget3.headerItem().setText(0, "Winding Temperature (ºC)")

        treeviewHLayout = QHBoxLayout()
        treeviewHLayout.addWidget(self.treeWidget1)
        treeviewHLayout.addWidget(self.treeWidget2)
        treeviewHLayout.addWidget(self.treeWidget3)

        secondVLayout.addLayout(treeviewHLayout)

        self.selectComponentVariableHLayout.addLayout(secondVLayout)

        self.firstVLayout.addLayout(self.selectComponentVariableHLayout)
        self.VEntryLayout.addLayout(self.firstVLayout)

        self.totalVLayout.addLayout(self.VEntryLayout)

        self.pteLog = QPlainTextEdit(self)
        self.pteLog.setObjectName(u"pteLog")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pteLog.sizePolicy().hasHeightForWidth())
        self.pteLog.setSizePolicy(sizePolicy)
        self.pteLog.setFixedHeight(70)

        self.totalVLayout.addWidget(self.pteLog)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setSpacing(10)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)

        self.btnGenerate = QPushButton()
        self.btnGenerate.setText("Generate Result")
        self.btnGenerate.setObjectName(u"btnGenerate")
        self.btnGenerate.clicked.connect(self.btnGenerate_clicked)

        self.horizontalLayout_3.addWidget(self.btnGenerate)

        self.btnShow = QPushButton()
        self.btnShow.setObjectName(u"btnShow")
        self.btnShow.setText("Show Result")
        self.btnShow.clicked.connect(self.btnShow_clicked)
        self.horizontalLayout_3.addWidget(self.btnShow)

        self.totalVLayout.addLayout(self.horizontalLayout_3)

        self.configs = []
        self.componentField = ""
        self.variables = []

        self.setGeometry(0, 0, 800, 640)
        self.setWindowTitle('WP 5.1 Tools')

    @pyqtSlot()
    def treeWidget1_onItemClicked(self, item, column):

        topItem = self.treeWidget1.topLevelItem(0)

        for i in reversed(range(topItem.childCount())):
            topItem.child(i).setCheckState(0, Qt.Unchecked)
        item.setCheckState(0,Qt.Checked)

    @pyqtSlot()
    def treeWidget2_onItemClicked(self, item, column):

        topItem = self.treeWidget2.topLevelItem(0)

        for i in reversed(range(topItem.childCount())):
            topItem.child(i).setCheckState(0, Qt.Unchecked)
        item.setCheckState(0,Qt.Checked)

    @pyqtSlot()
    def treeWidget3_onItemClicked(self, item, column):

        topItem = self.treeWidget3.topLevelItem(0)

        for i in reversed(range(topItem.childCount())):
            topItem.child(i).setCheckState(0, Qt.Unchecked)
        item.setCheckState(0,Qt.Checked)

    @pyqtSlot()
    def btnBrowse1_clicked(self):
        qfd = QFileDialog()
        path = ""
        filter = "All Files(*.*)"
        title = "Open file"
        f = QFileDialog.getOpenFileName(qfd, title, path, filter)
        print(f)
        self.modelpath1 = f[0]
        self.filePathLineEdit1.setText(f[0])

    @pyqtSlot()
    def btnBrowse3_clicked(self):
        qfd = QFileDialog()
        path = ""
        filter = "All Files(*.*)"
        title = "Open file"
        f = QFileDialog.getOpenFileName(qfd, title, path, filter)
        print(f)
        self.modelpath2 = f[0]
        self.filePathLineEdit3.setText(f[0])

    @pyqtSlot()
    def btnBrowse2_clicked(self):

        qfd = QFileDialog()
        path = ""
        filter = "Excel Files(*.xls *.xlsx *.xlsm *.csv)"
        title = "Open file"
        f = QFileDialog.getOpenFileName(qfd, title, path, filter)
        print(f)
        if f[0] != "":
            self.filePathLineEdit2.setText(f[0])
        else:
            return
        if self.pteLog.toPlainText() == "":
            self.pteLog.setPlainText("Browse file")
        else:
            self.pteLog.setPlainText(self.pteLog.toPlainText() + "\nBrowse file")

        self.filepath2 = self.filePathLineEdit2.text()
        self.clearDynamicTree(self.treeWidget1)
        self.clearDynamicTree(self.treeWidget2)
        self.clearDynamicTree(self.treeWidget3)

        filename, file_extension = os.path.splitext(self.filepath2)

        if file_extension == ".csv":
            self.readCSVFile(self.filepath2)
        elif file_extension == ".xls":
            self.readXLSFile(self.filepath2)
        else:
            self.readXLSFile(self.filepath2)

    def clearDynamicTree(self, treeWidget):

        selectAllItem = treeWidget.topLevelItem(0)
        componentsItem = selectAllItem.child(0)
        variablesItem = treeWidget.topLevelItem(0)
        for i in reversed(range(componentsItem.childCount())):
            componentsItem.removeChild(componentsItem.child(i))
        for i in reversed(range(variablesItem.childCount())):
            variablesItem.removeChild(variablesItem.child(i))
        self.componentField = ""


    def displayTreeWidgetCon(self, headers, selectedHeader, treeWidget):
        topItem = treeWidget.topLevelItem(0)
        for head in headers:
            item_1 = QtWidgets.QTreeWidgetItem(topItem)

            if head == selectedHeader:
                item_1.setCheckState(0, QtCore.Qt.Checked)
            else:
                item_1.setCheckState(0, QtCore.Qt.Unchecked)
        for i in range(len(headers)):
            topItem.child(i).setText(0, headers[i])

    def readXLSFile(self, filePath):

        headers = []
        selectedHeader = ""

        self.pteLog.setPlainText(self.pteLog.toPlainText() + "\nReading xls file...")

        csv_reader = pd.read_excel(filePath, nrows=0)

        theaders = csv_reader.columns
        headerTexts = []
        for header in theaders:
            if header != "":
                headerTexts.append(header)

        self.displayTreeWidgetCon(headerTexts, selectedHeader, treeWidget=self.treeWidget1)
        self.treeWidget1.expandAll()
        self.displayTreeWidgetCon(headerTexts, selectedHeader, treeWidget=self.treeWidget2)
        self.treeWidget2.expandAll()
        self.displayTreeWidgetCon(headerTexts, selectedHeader, treeWidget=self.treeWidget3)
        self.treeWidget3.expandAll()

        self.pteLog.setPlainText(self.pteLog.toPlainText() + "\nReading xls file completed")

    def readCSVFile(self, filePath):
        headers = []
        selectedHeader = ""
        self.pteLog.setPlainText(self.pteLog.toPlainText() + "\n Reading csv file...")
        csv_header_1 = pd.read_csv(filePath, sep=";", decimal=",", index_col=0, nrows=0)
        csv_header_2 = pd.read_csv(filePath, index_col=0, nrows=0)
        csv_reader = pd.read_csv(filePath, sep=";",
                                 decimal=",") if csv_header_1.columns.__len__() >= csv_header_2.columns.__len__() else pd.read_csv(
            filePath)
        theaders = csv_reader.columns
        headerTexts = []
        for header in theaders:
            if header != "":
                headerTexts.append(header)

        self.displayTreeWidgetCon(headerTexts, selectedHeader, treeWidget=self.treeWidget1)
        self.treeWidget1.expandAll()
        self.displayTreeWidgetCon(headerTexts, selectedHeader, treeWidget=self.treeWidget2)
        self.treeWidget2.expandAll()
        self.displayTreeWidgetCon(headerTexts, selectedHeader, treeWidget=self.treeWidget3)
        self.treeWidget3.expandAll()
        self.pteLog.setPlainText(self.pteLog.toPlainText() + "\nReading csv file completed")


    def get_checked_item(self, treewidget):
        checked = dict()
        root = treewidget.invisibleRootItem()
        signal_count = root.childCount()
        for i in range(signal_count):
            signal = root.child(i)
            checked_sweeps = list()
            num_children = signal.childCount()

            for n in range(num_children):
                child = signal.child(n)

                if child.checkState(0) == QtCore.Qt.Checked:
                    checked_sweeps.append(child.text(0))

            checked[signal.text(0)] = checked_sweeps
        return checked

    @pyqtSlot()
    def btnGenerate_clicked(self):
        print("Generating Result")

        results_path = './static/results_condition_monitoring/'
        try:
            dirContents = os.listdir(results_path)
        except:
            os.mkdir(results_path)
            dirContents = os.listdir(results_path)


        model_path = self.modelpath1
        model_error_path = self.modelpath2
        input_file_path = self.filepath2

        current_var = self.get_checked_item(self.treeWidget1)[""][0]
        oil_temp_var = self.get_checked_item(self.treeWidget2)[""][0]
        winding_temp_var = self.get_checked_item(self.treeWidget3)[""][0]

        if not len(dirContents) == 0:
            msgBox = QMessageBox()
            deleteButton = msgBox.addButton(self.tr("Delete"), QMessageBox.ActionRole)
            abortButton = msgBox.addButton(QMessageBox.Abort)

            msgBox.setText("The result folder is not empty.")
            msgBox.setInformativeText("Do you want to continue deleting the previous results?")

            msgBox.exec_()
            if msgBox.clickedButton() == deleteButton:
                try:
                    shutil.rmtree(results_path)
                    os.mkdir(results_path)
                except:
                    pass
                generate_prediction_dashboard(model_path, model_error_path, input_file_path, current_var, oil_temp_var,winding_temp_var)
                print("Done")

            elif msgBox.clickedButton() == abortButton:
                print("Abort")

        else:
            generate_prediction_dashboard(model_path, model_error_path, input_file_path, current_var, oil_temp_var,winding_temp_var)
            print("Done")


    def get_checked_item(self, treewidget):
        checked = dict()
        root = treewidget.invisibleRootItem()
        signal_count = root.childCount()
        for i in range(signal_count):
            signal = root.child(i)
            checked_sweeps = list()
            num_children = signal.childCount()

            for n in range(num_children):
                child = signal.child(n)

                if child.checkState(0) == QtCore.Qt.Checked:
                    checked_sweeps.append(child.text(0))

            checked[signal.text(0)] = checked_sweeps
        return checked

    @pyqtSlot()
    def btnShow_clicked(self):
        print("Loading Result")
        os.system("start .\static\\results_condition_monitoring\condition_monitoring.html")


def main():
    app = QApplication(sys.argv)
    ex = Example()
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()