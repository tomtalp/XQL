from PyQt4 import QtGui, QtCore
from XqlDbWriter import DBWriter
import sys, time
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

        path = QtGui.QFileDialog.getOpenFileName(self, 'Pick an Excel file', os.getenv(get_os_env()),
                                                     "Excel Files (*.xls *.xlsx)")

        # Change the screen only if a file was selected
        if path:
            self.file_path = str(path) # Convert QString to str
            self.filePathLabel.setText("Selected {file_path}".format(file_path = self.file_path))
            self.browseBtn.setText('Change file?')
            self.startBtn.setEnabled(True)  # Activate the button that begins the process
            self.tabWidget.setToolTip("Press the 'Go!' button to begin working")

    def beginProcessThread(self):
        worker_thread = self.WorkerThread(self)
        worker_thread.start()


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

        self.file_written_lbl = QtGui.QLabel("", self)
        self.horizontalLayout_2.addWidget(self.file_written_lbl)

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

        self.btn_show_more = QtGui.QPushButton("Show Next", self.queryTab)
        self.btn_show_more.setMaximumSize(QtCore.QSize(100, 25))
        self.btn_show_more.clicked.connect(self.get_more_results)
        self.horizontalLayout_6.addWidget(self.btn_show_more)

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
        self.tableWidget.setRowCount(30)
        self.verticalLayout.addWidget(self.tableWidget)

        self.verticalLayout.setStretch(2, 1)

    def initAdvancedUI(self):
        """
        initialize the Advanced tab UI
        """

        self.options_grid = QtGui.QGridLayout()


        self.date_formats = {"DD/MM/YYYY H:M:S": "%d/%m/%Y %H:%M:%S",
                             "MM/DD/YYYY H:M:S": "%m/%d/%Y %H:%M:%S"}

        #Date Format input
        self.date_format_label = QtGui.QLabel("Date Format: ") #Label
        self.date_format_lstbox = QtGui.QComboBox()
        self.date_format_lstbox.addItems(self.date_formats.keys())
        self.date_format_lstbox.setCurrentIndex(self.date_formats.keys().index("DD/MM/YYYY H:M:S")) #Default
        self.date_format_lstbox.setMaximumSize(QtCore.QSize(150, 30))

        #Rows to return input
        self.results_to_return_label = QtGui.QLabel("Rows to return: ") #Label
        self.results_to_return_text = QtGui.QLineEdit('20')
        self.results_to_return_text.setMaximumSize(QtCore.QSize(150, 30))
        self.int_validator = QtGui.QIntValidator() #Validation - must be int
        self.results_to_return_text.setValidator(self.int_validator)
        self.results_to_return_text.textChanged.connect(self.check_state)
        self.results_to_return_text.textChanged.emit(self.results_to_return_text.text())

        self.options_grid.addWidget(self.date_format_label, 1, 0)
        self.options_grid.addWidget(self.date_format_lstbox, 1, 1)

        self.options_grid.addWidget(self.results_to_return_label, 2, 0)
        self.options_grid.addWidget(self.results_to_return_text, 2, 1)

        self.advancedTab.setLayout(self.options_grid)

    def check_state(self, *args, **kwargs):

        """
        Checks the state of results_to_return_text and changes its color accordingly
        """

        sender = self.results_to_return_text
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]

        if state ==QtGui.QIntValidator.Acceptable:
            color = '#c4df9b' #green
        elif state == QtGui.QIntValidator.Intermediate:
            color = '#fff79a' #yellow
        else:
            state = '#f6989d' #red

        sender.setStyleSheet('QLineEdit {{ background-color: {color} }}'.format(color = color))


    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F5:
            self.sendQuery()

    def sendQuery(self):
        """
        Sends the query and populates the TableWidget with the results
        """

        #Get query from user
        query = str(self.queryTextEdit.toPlainText())

        #Make sure query isn't empty
        if query.strip():

            python_date_format = self.date_formats[str(self.date_format_lstbox.currentText())]
            results_to_return_text = self.results_to_return_text.text()
            if not results_to_return_text: #If empty, choose default
                results_to_return = 20
            else:
                results_to_return = abs(int(results_to_return_text))

            self.query_manager = XqlQueryManager.XqlQuery(self.writer.cursor, query, results_to_return, python_date_format)

            headers = self.query_manager.headers
            data = self.query_manager.get_results()

            self.add_items_to_table(self.tableWidget, data, True, self.query_manager.headers)

    def add_items_to_table(self, tableWidget, data, first, headers = ''):
        """
        Adds data to the TableWidget
        """

        #If this is the first time data is added, clear the table of previous data and add header names
        if first:
            current_rows = 0
            tableWidget.clear()
            tableWidget.setColumnCount(len(headers))
            tableWidget.setHorizontalHeaderLabels(headers)
        else:
            current_rows = tableWidget.rowCount()

        #Update amount of rows
        tableWidget.setRowCount(current_rows + len(data))

        #Write the data
        for index, row_value in enumerate(data):
            for col_num, item in enumerate(row_value):
                tableWidget.setItem(index + current_rows, col_num, QtGui.QTableWidgetItem(item))

    def get_more_results(self):

        #data = self.query_manager.get_results()
        data = [('Sid', '45', 'Hello', '24/01/1995'), ('Kra', '1', '43.2')]
        self.add_items_to_table(self.tableWidget, data, False)

        #TODO
        pass

    class WorkerThread(QtCore.QThread):
        def __init__(self, mainWindow):
            super(QtCore.QThread, self).__init__()
            self.mainWindow = mainWindow
        def run(self):
            self.mainWindow.beginProcess()
            return
        def __del__(self):
            self.wait()

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
