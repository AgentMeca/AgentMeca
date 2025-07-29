import mainApp
from PyQt5 import QtWidgets


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = mainApp.Application()
    window.show()
    sys.exit(app.exec_())