##################################################################
# XQL - A tool for querying Excel files via SQL.
#
# Visit our GitHub page at https://github.com/tomtalp/XQL
# Feel free to contact us with any questions & suggestions.
# You are more than welcome to contribute and help us improve the project!
#
#
# Built by Sidney Feiner & Tom Talpir, 2015.
#
##################################################################

from PyQt4 import QtGui
import XqlUI
import sys

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)  
    xql = XqlUI.XqlMainWidget()
    sys.exit(app.exec_())