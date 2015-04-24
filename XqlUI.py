from PyQt4 import QtGui, QtCore
from XqlDbWriter import DBWriter
import sys
import os
import XqlQueryManager


class MainWidget(QtGui.QMainWindow):
    """
    Main window class - Events, widgets and general design.
    """

    def __init__(self):
        super(MainWidget, self).__init__()
        self.initUI()

    def initUI(self):
        """
        Initializing & designing the UI
        """

        self.showMaximized()
        self.setWindowTitle("XQL")

        self.centralWidget = QtGui.QWidget(self)

        # Main Vertical & Horizontal layout objects
        self.mainHorizontalLayout = QtGui.QHBoxLayout(self.centralWidget)
        self.mainVerticalLayout = QtGui.QVBoxLayout()
        self.sideTreeLayout = QtGui.QHBoxLayout()

        self.mainHorizontalLayout.addLayout(self.sideTreeLayout)
        self.mainHorizontalLayout.addLayout(self.mainVerticalLayout)
        
        self.treeWidget = QtGui.QTreeWidget(self.centralWidget)
        self.sideTreeLayout.addWidget(self.treeWidget) 
        self.treeWidget.setMaximumSize(QtCore.QSize(250, 16777215))
        treeHeader = QtGui.QTreeWidgetItem(["Files"])
        self.treeWidget.setHeaderItem(treeHeader)

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
        self.mainVerticalLayout.addLayout(self.horizontalLayout)

        # Tabs
        self.tabWidget = QtGui.QTabWidget(self.centralWidget)
        self.tabWidget.setEnabled(False)
        self.tabWidget.setToolTip("<html><body>Pick a file to begin XQLing!</body></html>")

        self.queryTab = QtGui.QWidget()
        self.tabWidget.addTab(self.queryTab, "Query")
        self.advancedTab = QtGui.QWidget()
        self.tabWidget.addTab(self.advancedTab, "Advanced")  

        self.setCentralWidget(self.centralWidget)

        self.mainVerticalLayout.addWidget(self.tabWidget)

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

        self.initStyleSheet()
        self.show()

    def initStyleSheet(self):
        """
        Run setStyleSheet() with our CSS code
        """
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

    def addFileToTree(self, xql_db_obj):
        """
        Adds an Excel file to the side bar Tree Widget.
        """

        tree_root_file = QtGui.QTreeWidgetItem(self.treeWidget, [xql_db_obj.name])

        for table in xql_db_obj.tables:
            tree_table_obj = QtGui.QTreeWidgetItem(tree_root_file, [table.name])
            
            for col_name, col_type in table.headers.iteritems():
                tree_header_obj = QtGui.QTreeWidgetItem(tree_table_obj, ["{col_name} ({col_type})".format(col_name = col_name, col_type = col_type)])


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

        self.showMoreBtn = QtGui.QPushButton("Show Next", self.queryTab)
        self.showMoreBtn.setMaximumSize(QtCore.QSize(100, 25))
        self.showMoreBtn.clicked.connect(self.get_more_results)
        self.horizontalLayout_6.addWidget(self.showMoreBtn)
        self.showMoreBtn.setEnabled(False)

        self.showAllBtn = QtGui.QPushButton("Show All", self.queryTab)
        self.showAllBtn.setMaximumSize(QtCore.QSize(100, 25))
        self.showAllBtn.clicked.connect(self.get_all_results)
        self.horizontalLayout_6.addWidget(self.showAllBtn)
        self.showAllBtn.setEnabled(False)

        self.verticalLayout.addLayout(self.horizontalLayout_6)

        # Textbox
        self.queryTextEdit = QtGui.QPlainTextEdit(self.queryTab)
        self.verticalLayout.addWidget(self.queryTextEdit)

        # Table
        self.tableWidget = QtGui.QTableWidget(self.queryTab)
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setRowCount(1)
        self.verticalLayout.addWidget(self.tableWidget)

        self.verticalLayout.setStretch(2, 1)

    def initAdvancedUI(self):
        """
        initialize the Advanced tab UI
        """

        self.options_grid = QtGui.QGridLayout()

        self.advUiVerticalLayout1 = QtGui.QVBoxLayout(self.advancedTab)
        self.advUiHorizontalLayout1 = QtGui.QHBoxLayout()
        self.advUiHorizontalLayout2 = QtGui.QHBoxLayout()
        self.advUiEmptyHorizontalLayout = QtGui.QHBoxLayout()

        self.date_formats = {"DD/MM/YYYY H:M:S": "%d/%m/%Y %H:%M:%S",
                             "MM/DD/YYYY H:M:S": "%m/%d/%Y %H:%M:%S",
                             "YYYY/MM/DD H:M:S": "%Y/%m/%d %H:%M:%S",
                             "DD/MM/YYYY": "%d/%m/%Y",}

        #Date Format input
        self.date_format_label = QtGui.QLabel("Date Format: ")
        self.date_format_label.setMaximumSize(QtCore.QSize(100, 25))

        self.date_format_lstbox = QtGui.QComboBox()
        self.date_format_lstbox.setMaximumSize(QtCore.QSize(100, 25))

        self.date_format_lstbox.addItems(self.date_formats.keys())
        self.date_format_lstbox.setCurrentIndex(self.date_formats.keys().index("DD/MM/YYYY H:M:S")) #Default
        self.date_format_lstbox.setMaximumSize(QtCore.QSize(150, 30))  

        #Rows to return input
        self.results_to_return_label = QtGui.QLabel("Rows to return: ") 
        self.results_to_return_label.setMaximumSize(QtCore.QSize(100, 25))

        self.results_to_return_text = QtGui.QLineEdit('20')
        self.results_to_return_text.setMaximumSize(QtCore.QSize(150, 30))
        positive_int_regex = QtCore.QRegExp("^\d+$")
        self.positive_int_validator = QtGui.QRegExpValidator(positive_int_regex) #Validation - must be positive int
        self.results_to_return_text.setValidator(self.positive_int_validator)
        self.results_to_return_text.textChanged.connect(self.check_state)
        self.results_to_return_text.textChanged.emit(self.results_to_return_text.text())

        self.advUiHorizontalLayout1.addWidget(self.date_format_label)
        self.advUiHorizontalLayout1.addWidget(self.date_format_lstbox)

        self.advUiVerticalLayout1.addLayout(self.advUiHorizontalLayout1)

        self.advUiHorizontalLayout2.addWidget(self.results_to_return_label)
        self.advUiHorizontalLayout2.addWidget(self.results_to_return_text)

        self.advUiVerticalLayout1.addLayout(self.advUiHorizontalLayout2)

        self.spacer = QtGui.QSpacerItem(1, 1, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)

        self.advUiEmptyHorizontalLayout.addItem(self.spacer)
        self.advUiVerticalLayout1.addLayout(self.advUiEmptyHorizontalLayout)

        self.verticalLayout.setStretch(2, 1)

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

    def beginProcess(self):
        """
        Begin writing the DB behind the scenes, clear the screen and when done transform the screen to the query interface.
        """
        self.writer = DBWriter(self.file_path)
        self.writer.write_to_db()

        self.startBtn.setEnabled(False) # Once DB has been initialized, user shouldn't be able to click this button to init again.
        self.tabWidget.setEnabled(True) # The tabs can now be used
        self.tabWidget.setToolTip("") # Cancel the tooltip that instructs user to pick a file.

        xql_db = self.writer.XqlDB
        self.addFileToTree(xql_db)

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
        """
        Key event for executing a query
        """
        if event.key() == QtCore.Qt.Key_F5:
            self.sendQuery()

    def sendQuery(self):
        """
        Sends the query and populates the TableWidget with the results
        if partial_results is True, it returns results_to_return results, otherwise it returns everything
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
                results_to_return = int(results_to_return_text)


            self.query_manager = XqlQueryManager.XqlQuery(self.writer.cursor, query, results_to_return, python_date_format)

            headers = self.query_manager.headers
            data = self.query_manager.get_results()

            self.add_items_to_table(self.tableWidget, data, True, self.query_manager.headers)

    def add_items_to_table(self, tableWidget, data, first = False, headers = ''):
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

        self.check_awaiting_results() # Enable "show more" if we have more results to bring

    def get_more_results(self):
        """
        Check if there are any results left, and fetch them.
        """

        data = self.query_manager.get_results()
        self.add_items_to_table(self.tableWidget, data)
        self.check_awaiting_results() # Check if we have more results to bring, and alter the "show more button"

    def get_all_results(self):
        """
        Fetches all results
        """

        data = self.query_manager.get_results(True)
        self.add_items_to_table(self.tableWidget, data)
        self.check_awaiting_results()

    def check_awaiting_results(self):
        """
        Modify the "show all/more" buttons state - set enabled if query manager has more results, disable if not.
        """
        if self.query_manager.has_awaiting_results:
            self.showMoreBtn.setEnabled(True)
            self.showAllBtn.setEnabled(True)
        else:
            self.showMoreBtn.setEnabled(False)
            self.showAllBtn.setEnabled(False)

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
