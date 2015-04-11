from PyQt4 import QtGui, QtCore
from XqlDbWriter import DBWriter
import sys
import os, datetime, XqlQueryManager


class MainWidget(QtGui.QMainWindow):
    """
    Main window class - Events, widgets and general design.
    """


    def __init__(self):
        super(MainWidget, self).__init__()

        self.initUI()

    def openFile(self):
        """
        Handler for the 'open file' button. User picks a file and
        """

        # Make sure when user begins searching for a file that start button is disabled & path label is empty .
        # Fixes a bug that when user picks a file and clicks "Change File", he can pick an invalid file and press "Go!", since the button was enabled by the previous upload.
        self.startBtn.setEnabled(False)
        self.filePathLabel.setText("")
        self.file_path = QtGui.QFileDialog.getOpenFileName(self, 'Pick an Excel file', os.getenv(get_os_env()),
                                                     "Excel Files (*.xls *.xlsx)")

        self.file_path = str(self.file_path) # Convert QString to str

        # Change the screen only if a file was selected
        if self.file_path:
            self.filePathLabel.setText("Selected {file_path}".format(file_path = self.file_path))
            self.browseBtn.setText('Change file?')
            self.startBtn.setEnabled(True)  # Activate the button that begins the process
            self.tabWidget.setToolTip("Press the 'Go!' button to begin working")

    def beginProcess(self):
        """
        Begin writing the DB behind the scenes, clear the screen and when done transform the screen to the query interface.
        """
        self.writer = DBWriter(self.file_path)
        self.writer.write_to_db()

        self.startBtn.setEnabled(False) # Once DB has been initialized, user shouldn't be able to click this button to init again.
        self.tabWidget.setEnabled(True) # The tabs can now be used
        self.tabWidget.setToolTip("") # Cancel the tooltip that instructs user to pick a file.



    def initUI(self):
        """
        Main function for initializing & designing the UI
        """

        self.setGeometry(100, 100, 1250, 850)
        self.setWindowTitle("XQL")

        self.centralWidget = QtGui.QWidget(self)

        # Vertical & Horizontal layout objects
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.centralWidget)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setContentsMargins(-1, -1, 0, -1)
        self.horizontalLayout_2 = QtGui.QHBoxLayout()

        # Button for browsing files
        self.browseBtn = QtGui.QPushButton("Browse", self.centralWidget)
        self.browseBtn.setMaximumSize(QtCore.QSize(100, 25))
        self.horizontalLayout_2.addWidget(self.browseBtn)
        self.browseBtn.clicked.connect(self.openFile) # Open file dialog event

        self.filePathLabel = QtGui.QLabel("", self) # Show nothing until initialized with a file.
        self.horizontalLayout_2.addWidget(self.filePathLabel)

        self.horizontalLayout.addLayout(self.horizontalLayout_2)

        self.startBtn = QtGui.QPushButton("Go!", self.centralWidget)
        self.startBtn.setEnabled(False)
        self.startBtn.setMaximumSize(QtCore.QSize(100, 25))

        self.startBtn.clicked.connect(self.beginProcess) # Once clicked we begin writing the db behind the scenes.

        self.horizontalLayout.addWidget(self.startBtn)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        # Tabs
        self.tabWidget = QtGui.QTabWidget(self.centralWidget)
        self.tabWidget.setEnabled(False)
        self.tabWidget.setToolTip("<html><body>Pick a file to begin XQLing!</body></html>")

        self.queryTab = QtGui.QWidget()
        self.tabWidget.addTab(self.queryTab, "Query")
        self.advancedTab = QtGui.QWidget()
        self.tabWidget.addTab(self.advancedTab, "Advanced")  

        self.setCentralWidget(self.centralWidget)

        self.verticalLayout_2.addWidget(self.tabWidget)

        self.initQueryUI() # Initialize the query area, which is disabled until the user creates the DB.
        self.initAdvancedUI()

        # Menu bar
        self.menubar = QtGui.QMenuBar(self.centralWidget)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1130, 25))
        self.menuAbout = QtGui.QMenu("About", self.menubar)
        self.actionAbout_XQL = QtGui.QAction("About XQL", self)
        self.menuAbout.addAction(self.actionAbout_XQL)
        self.menubar.addAction(self.menuAbout.menuAction())

        self.setMenuBar(self.menubar)

        self.setStyleSheet("""
            .QMainWindow {
                background-color: green;
            }

            .QPushButton {
                border-radius: 10px;
                font-family: Arial;
                color: #ffffff;
                font-size: 10px;
                background: #2086C3;
                padding: 6px 15px 6px 15px;
                text-decoration: none;
            }

            .QPushButton:hover {
                background: #26A0E8;
                text-decoration: none;
            }

            .QPushButton:pressed {
                background: #1D303D;
                text-decoration: none;
            }

            .QPushButton:disabled {
                background: gray;
                text-decoration: none;
            }

            .QPushButton:focus {
                outline: 0;
            }

            """)

        self.show()

    def initQueryUI(self):
        """
        Initialize the query UI (table & SQL query text input) 
        Called once the user picks an Excel file and transforms the Excel to a DB.
        """
        self.verticalLayout = QtGui.QVBoxLayout(self.queryTab)
        self.horizontalLayout_6 = QtGui.QHBoxLayout()

        # Buttons above the textbox
        self.execButton = QtGui.QPushButton("Execute (F5)", self.queryTab)
        self.execButton.setMaximumSize(QtCore.QSize(100, 25))
        self.execButton.clicked.connect(self.sendQuery)
        self.horizontalLayout_6.addWidget(self.execButton)

        self.stopButton = QtGui.QPushButton("Stop", self.queryTab)
        self.stopButton.setMaximumSize(QtCore.QSize(100, 25))
        self.horizontalLayout_6.addWidget(self.stopButton)

        self.pushButton_5 = QtGui.QPushButton("Show Next", self.queryTab)
        self.pushButton_5.setMaximumSize(QtCore.QSize(100, 25))
        self.horizontalLayout_6.addWidget(self.pushButton_5)

        self.pushButton_6 = QtGui.QPushButton("Show All", self.queryTab)
        self.pushButton_6.setMaximumSize(QtCore.QSize(100, 25))
        self.horizontalLayout_6.addWidget(self.pushButton_6)

        self.verticalLayout.addLayout(self.horizontalLayout_6)

        # Textbox
        self.queryTextEdit = QtGui.QPlainTextEdit(self.queryTab)
        self.verticalLayout.addWidget(self.queryTextEdit)

        # Table
        self.tableWidget = QtGui.QTableWidget(self.queryTab)
        self.tableWidget.setColumnCount(15)
        self.tableWidget.setRowCount(555)
        self.verticalLayout.addWidget(self.tableWidget)

        self.verticalLayout.setStretch(2, 1)

    def initAdvancedUI(self):
        """

        initialize the Advanced tab UI

        """

        #TODO
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.advancedTab)

        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        pass

    def sendQuery(self):
        """
        Sends the query and populates the TableWidget with the results
        """

        query = str(self.queryTextEdit.toPlainText())

        self.query_manager = XqlQueryManager.XqlQuery(self.writer.cursor, query)

        headers = self.query_manager.headers

        data = self.query_manager.get_results()

        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setRowCount(len(data))

        self.tableWidget.setHorizontalHeaderLabels(headers)

        for row_num, row_value in enumerate(data):
            for col_num, item in enumerate(data[row_num]):
                self.tableWidget.setItem(row_num, col_num, QtGui.QTableWidgetItem(str(item)))


def get_os_env():
    """
    Get the proper os environment variable, depending on the OS
    """
    # Linux
    if os.name == 'posix':
        return 'HOME'

    # Windows    
    elif os.name == 'nt':
        return 'USERPROFILE'
    else:
        # TODO: Deal with other systems
        raise Exception("What OS are you using......")


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    
    w = MainWidget()
    sys.exit(app.exec_())
