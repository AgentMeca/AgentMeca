from frontend.customWidgets import RackStatus, StatusImage, CustomToggleButton
from PyQt5.QtWidgets import QApplication, QGridLayout, QLabel, QPushButton, QWidget

class Apptest(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.initUI()

    def initUI(self):
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.rs = RackStatus()
        self.button = CustomToggleButton()
        self.test_flag = True

        self.grid.addWidget(self.rs)
        self.grid.addWidget(self.button)

        self.button.clicked.connect(self.on_pressed)

    def on_pressed(self):
        if self.test_flag:
            self.rs.rack_list[0].switch_off()
            self.test_flag = False
        else:
            self.rs.rack_list[0].switch_on()
            self.test_flag = True


app = QApplication([])

apptest = Apptest()
apptest.show()
#blah = QLabel("Yo mama")
#blah.show()
#im_test = StatusImage()
#im_test.show()
#rs = RackStatus()
#rs.show()


app.exec_()
