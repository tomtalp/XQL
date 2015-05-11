from PyQt4 import QtGui, QtCore
from XqlDbWriter import DBWriter
import XqlQueryManager
import XqlParser
import os

class LoadingGif(object):
    """
    A custom object for managing QtGui.QMovie objects playing .gif images
    """

    def __init__(self, gif_target_label, target_widget):
        self.loading_gif_path = "loading.gif"
        self.gif_target_label = gif_target_label
        self.target_widget = target_widget

        self.movie = QtGui.QMovie(self.loading_gif_path, QtCore.QByteArray(), target_widget)
        size = self.movie.scaledSize()

        self.movie.setCacheMode(QtGui.QMovie.CacheAll)
        self.movie.setSpeed(100)

        self.gif_target_label.setMovie(self.movie)
        
    def play_gif(self):
        """
        Start the QMovie object
        """
        self.movie.start()

    def stop_gif(self):
        """
        Stop the QMovie object & delete the unnecessary Qt objects
        """
        self.movie.stop()
        self.movie.deleteLater()
        self.gif_target_label.setText(" ")

class LoadingDialog(QtGui.QDialog):
    """
    Custom QDialog for the loading dialog shown when user uploads a file
    """

    def __init__(self):
        super(LoadingDialog, self).__init__()

        self.__close_flag = False # Set to True when called by the close() method, so we know this isn't a user initiated close

        self.setWindowTitle("Xql - Loading")
        self.loading_gif_label_for_dialog = QtGui.QLabel("")
        self.loading_dialog_msg = QtGui.QLabel("We're preparing your file, hang tight!")

        self.loading_layout_for_dialog = QtGui.QVBoxLayout()
        self.loading_layout_for_dialog.addWidget(self.loading_dialog_msg)
        self.loading_layout_for_dialog.addWidget(self.loading_gif_label_for_dialog)

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

        self.setLayout(self.loading_layout_for_dialog)
        self.setFixedSize(300, 100)

        # Center the dialog in the middle of the screen
        dialog_size = self.size()
        desktop_size = QtGui.QDesktopWidget().screenGeometry()
        top_pos = (desktop_size.height()/2) - (dialog_size.height()/2)
        left_pos = (desktop_size.width()/2) - (dialog_size.width()/2)
        self.move(left_pos, top_pos)

    def show(self):
        """
        Override the QDialog "show" method - Show the dialog & play the gif
        """
        self.loading_gif = LoadingGif(self.loading_gif_label_for_dialog, self)
        self.loading_gif.play_gif()
        super(LoadingDialog, self).show()

    def close(self):
        """
        Override the QDialog "close" method - Close the dialog & stop the gif
        """
        self.loading_gif.stop_gif()

        self.__close_flag = True
        super(LoadingDialog, self).close()

    def closeEvent(self, event):
        """
        Ignore the close event sent by users clicking "X", and accept only when event is trigger from within the code.
        """
        if self.__close_flag:
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, event):
        """
        Ignore the close trigger fired when user clicks "Escape"
        """
        if event.key() == QtCore.Qt.Key_Escape:
            pass

class ErrorMessageBox(QtGui.QMessageBox):
    """
    Custom QMessageBox for errors
    """
    def __init__(self, target_widget, full_error = None, window_title = "XQL Error", short_error = "XQL has found an error...", unexpected_error = False):
        super(ErrorMessageBox, self).__init__(target_widget)

        self.window_title = window_title
        self.short_error = short_error
        self.full_error = full_error
        self.unexpected_error = unexpected_error
        
        if self.unexpected_error:
            self.short_error = "An unexpected error has occurred... Please contact us on GitHub with the error details so we can solve it!"

        self.init_dialog()

        self.show()

    def init_dialog(self):
        """
        Initialize the error dialog
        """
        self.setWindowTitle(self.window_title)
        self.setText(self.short_error)
        if self.full_error:
            self.setDetailedText(self.full_error)

class WritingThread(QtCore.QThread):
    """
    Seperate thread for writing excel files to the DB.
    """

    playLoadingSignal = QtCore.pyqtSignal()
    stopLoadingSignal = QtCore.pyqtSignal()
    addToTreeSignal = QtCore.pyqtSignal(XqlParser.XqlDB)

    def __init__(self, main_window):
        QtCore.QThread.__init__(self)
        self.main_window = main_window

    def run(self):
        self.main_window.beginProcess()

class XqlMainWidget(QtGui.QMainWindow):
    """
    Main window class - Events, widgets and general design.
    """
    UnicodeSignal = QtCore.pyqtSignal()

    def __init__(self):
        super(XqlMainWidget, self).__init__()
        self.UnicodeSignal.connect(self.show_unicode_popup_error)
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
        self.mainVerticalLayout = QtGui.QVBoxLayout() # Main window - contains the query textbox, table widget & buttons etc.
        self.sideBarLayout = QtGui.QVBoxLayout() # Contains tree widget & upload progress list.

        self.mainHorizontalLayout.addLayout(self.sideBarLayout)
        self.mainHorizontalLayout.addLayout(self.mainVerticalLayout)
        
        self.treeWidget = QtGui.QTreeWidget(self.centralWidget)
        self.sideBarLayout.addWidget(self.treeWidget) 
        self.treeWidget.setMaximumSize(QtCore.QSize(225, 16777215))
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

        self.loading_label = QtGui.QLabel("", self)
        self.horizontalLayout_2.addWidget(self.loading_label)

        self.horizontalLayout.addLayout(self.horizontalLayout_2)

        self.startBtn = QtGui.QPushButton("Go!", self.centralWidget)
        self.startBtn.setEnabled(False)
        self.startBtn.setMaximumSize(QtCore.QSize(100, 25))

        self.startBtn.clicked.connect(self.beginProcessThread) # Once clicked we begin writing the db behind the scenes.

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

        self.tabsVerticalLayout = QtGui.QVBoxLayout(self.queryTab)
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

        self.writer = None # Set the reference to the writer obj to none     

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

    def show_unicode_popup_error(self):
        """
        Show an error dialog regarding sheets with Unicode characters and close the loading-dialog.
        Requires an independant function that'll be connected with signals to the external DbWriting thread (because we can't show a dialog from an external thread in the Qt thread)
        """
        if self.loading_dialog:
            self.loading_dialog.close()

        err = ErrorMessageBox(target_widget = self, short_error = "Sheet names cannot contain Unicode characters!", full_error = "Please make sure all your sheet names contain ASCII characters.")


    def addFileToTree(self, xql_db_obj):
        """
        Adds an Excel file to the side bar Tree Widget.
        """

        for schema in xql_db_obj.schemas:
            if not schema.processed: #Make sure it hasn't been added yet
                tree_schema_obj = QtGui.QTreeWidgetItem(self.treeWidget, [schema.name])
                tree_schema_obj.setExpanded(True)

                for table in schema.tables:
                    tree_table_obj = QtGui.QTreeWidgetItem(tree_schema_obj, [table.name])
                    tree_table_obj.setExpanded(True)
                    for col_name, col_type in table.headers.iteritems():
                        tree_header_obj = QtGui.QTreeWidgetItem(tree_table_obj, ["{col_name} ({col_type})".format(col_name = col_name, col_type = col_type)])
                schema.processed = True

    def initQueryButtons(self):
        """
        Initialize query buttons for execution & results fetching
        """
        
        self.horizontalLayout_6 = QtGui.QHBoxLayout()

        self.execButton = QtGui.QPushButton("Execute (F5)", self.queryTab)
        self.execButton.setMaximumSize(QtCore.QSize(100, 25))
        self.execButton.clicked.connect(self.sendQuery)
        self.horizontalLayout_6.addWidget(self.execButton)

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

        self.tabsVerticalLayout.addLayout(self.horizontalLayout_6)

    def initQueryTextBox(self):
        """
        Initialize the query textbox
        """
        self.queryTextEdit = QtGui.QPlainTextEdit(self.queryTab)
        self.tabsVerticalLayout.addWidget(self.queryTextEdit)
    
    def initResultsTable(self):
        """
        Initialize the table widget
        """
        self.tableWidget = QtGui.QTableWidget(self.queryTab)
        self.tableWidget.setEditTriggers(QtGui.QAbstractItemView.NoEditTriggers)
        self.tableWidget.setColumnCount(1)
        self.tableWidget.setRowCount(1)
        self.tabsVerticalLayout.addWidget(self.tableWidget)

    def initQueryUI(self):
        """
        Initialize the query UI (table & SQL query text input) 
        """                     
        self.initQueryButtons()
        self.initQueryTextBox()
        self.initResultsTable()
       
        self.tabsVerticalLayout.setStretch(2, 1)

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

        self.tabsVerticalLayout.setStretch(2, 1)

    def openFile(self):
        """
        Handler for the 'open file' button. User picks a file and
        """

        paths = QtGui.QFileDialog.getOpenFileNames(self, 'Pick Excel File(s)', os.getenv(get_os_env()),
                                                     "Excel Files (*.xls *.xlsx)")

        # Change the screen only if a file was selected
        if paths:
            try:
                self.file_paths = [str(path) for path in paths] # Convert QString to str    
            except UnicodeEncodeError, e:
                err = ErrorMessageBox(target_widget = self, short_error = "Please select a file with a valid name!", full_error = "Your file name must be ASCII characters only!")
            else:                   
                self.filePathLabel.setText("Selected {file_paths}".format(file_paths = ', '.join([os.path.basename(str(path)) for path in self.file_paths])))
                self.browseBtn.setText('Change file?')
                self.startBtn.setEnabled(True)  # Activate the button that begins the process
                self.tabWidget.setToolTip("Press the 'Go!' button to begin working")

    def beginProcessThread(self):
        """
        Create signals & start the writing thread
        """
        self.writing_thread = WritingThread(self)
        self.loading_dialog = LoadingDialog() # Will be used for the loading dialog presented to the user when file is uploaded.

        #Signals
        self.writing_thread.playLoadingSignal.connect(self.loading_dialog.show)
        self.writing_thread.stopLoadingSignal.connect(self.loading_dialog.close)
        self.writing_thread.addToTreeSignal.connect(self.addFileToTree)

        self.writing_thread.start()

    def beginProcess(self):
        """
        Write the DB & show the loading dialog.
        """      

        self.writing_thread.playLoadingSignal.emit()

        # Check whether a DB has already been created.
        # If not, begin by creating the database
        if not self.writer:
            try:
                self.create_db()
                self.db_creation_complete()
            except UnicodeError:
                self.UnicodeSignal.emit()
        
        # If we enter this else, this isn't the first time an Excel has been loaded, and all we need to do is add the new file
        # to the existing database.
        else:
            #If db has already been created, add new schemas
            self.writer.add_xls(self.file_paths) #Adds them to the XqlDB
            self.writer.write_to_db()
            self.db_creation_complete()

    def create_db(self):
        """
        Create a database from the Excel file.
        """
        self.writer = DBWriter(self.file_paths)
        self.writer.write_to_db()      

    def db_creation_complete(self):
        """
        Modify the GUI once the DB has been loaded
        """
        
        self.writing_thread.stopLoadingSignal.emit()
        
        xql_db = self.writer.XqlDB
        self.writing_thread.addToTreeSignal.emit(xql_db)

        self.tabWidget.setEnabled(True) # The tabs can now be used
        self.tabWidget.setToolTip("") # Cancel the tooltip that instructs user to pick a file.

        self.startBtn.setEnabled(False) # Disable the "Go!" button until user picks a new file.

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
        query = unicode(self.queryTextEdit.toPlainText())

        #Make sure query isn't empty
        if query.strip():

            python_date_format = self.date_formats[str(self.date_format_lstbox.currentText())]
            results_to_return_text = self.results_to_return_text.text()
            if not results_to_return_text: #If empty, choose default
                results_to_return = 20
            else:
                results_to_return = int(results_to_return_text)

            try:
                self.query_manager = XqlQueryManager.XqlQuery(self.writer.cursor, query, results_to_return, python_date_format)
                headers = self.query_manager.headers
                data = self.query_manager.get_results()
                self.add_items_to_table(self.tableWidget, data, True, self.query_manager.headers)

            except XqlQueryManager.XqlInvalidQuery, invalid_query_error:
                err = ErrorMessageBox(target_widget = self, short_error = invalid_query_error.msg)

            except Exception, e:
                err = ErrorMessageBox(target_widget = self, unexpected_error = True, full_error = e.message)   
                     
            
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
