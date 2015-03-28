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
        filename = QtGui.QFileDialog.getOpenFileName(self, 'Pick an Excel file', os.getenv('HOME'),
                                                     "Excel Files (*.xls *.xlsx)")

        # Change the screen only if a file was selected
        if filename:
            self.selectedFileLabel.setText("Selected - {filename}".format(filename = filename))
            self.pickFileBtn.setText('Change file?')
            self.startBtn.setEnabled(True)  # Activate the button that begins the process

    def beginProcess(self):
        """
		Begin writing the DB behind the scenes, clear the screen and when done transform the screen to the query interface.
		"""

        # TODO: Everything in the comment above :)
        pass


    def initUI(self):
        """
		Main function for initializing & designing the UI
		"""

        self.header = QtGui.QLabel("XQL", self)
        self.header.move(25, 0)

        self.pickFileBtn = QtGui.QPushButton("Pick a file!", self)
        self.pickFileBtn.move(25, 35)

        self.selectedFileLabel = QtGui.QLabel('',
                                              self)  # Show nothing for now, will be initialized after user picks a file
        self.selectedFileLabel.move(25, 65)
        self.selectedFileLabel.resize(650, 25)  # Adjust the height so it will show the whole file

        self.pickFileBtn.clicked.connect(self.openFile)

        self.startBtn = QtGui.QPushButton("Go!", self)
        self.startBtn.setEnabled(False)  # Disabled when we begin
        self.startBtn.move(25, 100)

        self.setGeometry(300, 300, 650, 650)
        self.setWindowTitle("XQL")
        self.show()


app = QtGui.QApplication(sys.argv)
w = MainWidget()
sys.exit(app.exec_())

