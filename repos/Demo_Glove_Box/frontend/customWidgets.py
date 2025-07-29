from PyQt5.QtWidgets import QFrame, QPushButton, QGridLayout, QWidget, QLabel
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect, Qt
import os.path


class CustomToggleButton(QPushButton):
    def __init__(self, parent=None):
        super(CustomToggleButton, self).__init__(parent)
        self.setCheckable(True)
        self.setStyleSheet("margin: 1px; padding: 7px; background-color:rgba(125,125,125,100); color: black; border-style: solid; border-radius: 3px; border-width: 0.5px; border-color: black;")
        self.setFixedSize(95, 120)
        self.clicked.connect(self._on_pressed_col_change)

    def _on_pressed_col_change(self):
        if self.isChecked():
            self.setStyleSheet("margin: 1px; padding: 7px; background-color:rgba(0,255,0,255); color: black; border-style: solid; border-radius: 3px; border-width: 0.5px; border-color: black;")
        else:
            self.setStyleSheet("margin: 1px; padding: 7px; background-color:rgba(125,125,125,100); color: black; border-style: solid; border-radius: 3px; border-width: 0.5px; border-color: black;")

class StatusImage(QLabel):
    def __init__(self, parent=None):
        super(StatusImage, self).__init__(parent=parent)
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.im_height = 150
        self.pixmap_on = QPixmap(os.path.join(current_dir, 'images/vial.png'))
        self.pixmap_on = self.pixmap_on.scaledToHeight(self.im_height)
        self.pixmap_off = QPixmap(os.path.join(current_dir, 'images/Vial_grey.png'))
        self.pixmap_off = self.pixmap_off.scaledToHeight(self.im_height)

        self.setPixmap(self.pixmap_on)

    def switch_on(self):
        self.setPixmap(self.pixmap_on)

    def switch_off(self):
        self.setPixmap(self.pixmap_off)


class RackStatus(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(RackStatus, self).__init__(parent=parent, *args, **kwargs)
        self.grid = QGridLayout()
        self.rack_list = []
        for i in range(6):
            self.rack_list.append(StatusImage())

        positions = [(i, j) for i in range(2) for j in range(3)]

        for i in range(6):
            self.grid.addWidget(self.rack_list[i], *positions[i], alignment=Qt.AlignCenter)
        self.setLayout(self.grid)

    def turn_vial_off(self, pos):
        self.rack_list[pos].switch_off()

    def turn_vial_on(self, pos):
        self.rack_list[pos].switch_on()

class CentStatus(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(CentStatus, self).__init__(parent=parent, *args, **kwargs)
        self.frame = QFrame(parent)
        self.frame.setGeometry(QRect(150, 120, 400, 400))
        self.framebg = QLabel(parent=self.frame)
        current_dir = os.path.dirname(os.path.realpath(__file__))
        self.bgpath = os.path.join(current_dir, 'images/Centrifuge_Positions.png')
        self.bgpixmap = QPixmap(self.bgpath)
        self.bgpixmap = self.bgpixmap.scaled(400, 400)
        self.framebg.setPixmap(self.bgpixmap)

        self.led_on_path = os.path.join(current_dir, 'images/ring_light.png')
        self.led_off_path = os.path.join(current_dir, 'images/ring_light_grey.png')
        self.led_on_pm = QPixmap(self.led_on_path)
        self.led_on_pm = self.led_on_pm.scaled(30, 30)
        self.led_off_pm = QPixmap(self.led_off_path)
        self.led_off_pm = self.led_off_pm.scaled(30, 30)
        self.led_pos_list = [(50, 100), (185, 25), (320, 100), (320, 250), (185, 325), (50, 250)]

        self.led_list = []
        self.led_state = [False]*6
        for i in range(6):
            self.led_list.append(QLabel(self.frame))
            self.led_list[i].setStyleSheet("background-color: transparent")
            self.led_list[i].setPixmap(self.led_off_pm)
            self.led_list[i].setGeometry(QRect(*self.led_pos_list[i], 50, 50))

    def toggle_led(self, pos):
        if not self.led_state[pos]:
            self.led_list[pos].setPixmap(self.led_on_pm)
            self.led_state[pos] = True
        else:
            self.led_list[pos].setPixmap(self.led_off_pm)
            self.led_state[pos] = False

    def turn_vial_on(self, pos):
        self.led_list[pos].setPixmap(self.led_on_pm)

    def turn_vial_off(self, pos):
        self.led_list[pos].setPixmap(self.led_off_pm)

class RackButtons(QWidget):
    def __init__(self, parent=None, *args, **kwargs):
        super(RackButtons, self).__init__(parent=parent, *args, **kwargs)
        self.grid = QGridLayout()
        self.button_list = []
        for i in range(6):
            self.button_list.append(CustomToggleButton(f"Vial {i+1}"))

        positions = [(i, j) for i in range(2) for j in range(3)]

        for i in range(6):
            self.grid.addWidget(self.button_list[i], *positions[i])
        self.setLayout(self.grid)

    def disableButtons(self):
        for b in self.button_list:
            b.setEnabled(False)

    def enableButtons(self):
        for b in self.button_list:
            b.setEnabled(True)

