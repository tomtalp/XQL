from PyQt4 import QtGui, QtCore
import sys
import os


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
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Pick an Excel file', os.getenv(get_os_env()),
                                                     "Excel Files (*.xls *.xlsx)")

        # Change the screen only if a file was selected
        if filename:
            self.filePathLabel.setText("Selected {filename}".format(filename = filename))
            self.browseBtn.setText('Change file?')
            self.startBtn.setEnabled(True)  # Activate the button that begins the process

    def beginProcess(self):
        """
        Begin writing the DB behind the scenes, clear the screen and when done transform the screen to the query interface.
        """

        print "Woohooooo!"

        # TODO: Everything in the comment above :)
        pass


    def initUI(self):
        """
        Main function for initializing & designing the UI
        """

        self.setGeometry(200, 200, 1130, 786)
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

        # 
        self.startBtn = QtGui.QPushButton("Go!", self.centralWidget)
        self.startBtn.setEnabled(False)
        self.startBtn.setMaximumSize(QtCore.QSize(100, 25))

        self.startBtn.clicked.connect(self.beginProcess) # Once clicked we begin writing the db behind the scenes.

        self.horizontalLayout.addWidget(self.startBtn)
        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.tabWidget = QtGui.QTabWidget(self.centralWidget)
        self.tabWidget.setEnabled(False)

        self.queryTab = QtGui.QWidget()
        self.tabWidget.addTab(self.queryTab, "Query")

        self.metaDataTab = QtGui.QWidget()
        self.tabWidget.addTab(self.metaDataTab, "Metadata")

        self.setCentralWidget(self.centralWidget)

        self.verticalLayout_2.addWidget(self.tabWidget)

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
