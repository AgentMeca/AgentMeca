from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication, QObject, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
from backend.backend import MainRack, Centrifuge
from frontend import customWidgets, MainWindow, SetupWindow, ProgressWindow
from mecademicpy.robot import CommunicationError, Robot
import os
import re
import numpy as np
from time import sleep

class SetupWindow(QtWidgets.QMainWindow, SetupWindow.Ui_MainWindow):
    def __init__(self, rack, centrifuge, *args, **kwargs):
        self.rack = rack
        self.centrifuge = centrifuge
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        self.pushButton.clicked.connect(self.save_position)
        self.defaul_pick = [[57.7950,186.1550,80.7050,-0.0000,-0.0000,-90.0000],
                            [25.9600,186.1550,80.7050,-0.0000,0.0000,-90.0000], 
                            [-6.2800,186.1550,80.7050,-0.0000,0.0000,-90.0000], 
                            [58.4135,236.8031,81.7342,0.0000,-0.1620,90.0000], 
                            [26.9986,238.5881,81.6454,-0.0000,-0.1620,90.0000], 
                            [-4.9963,237.1381,81.5549,-0.0000,-0.1620,90.0000]]
        self.defaul_place = [[256.7045,21.9299,87.1742,46.7246,-20.3339,71.8831],
                            [278.0817,-13.5350,87.2791,0.0000,-50.0000,0.0000],
                            [258.6920,-48.0219,86.2246,-44.8992,-24.8455,-67.5270],
                            [217.0611,-48.6621,84.6120,-44.2944,22.9473,66.5995],
                            [196.4375,-14.0050,84.0717,-1.0921,49.9949,0.8365],
                            [217.4994,22.6281,84.6470,45.5804,23.3668,-67.3643]]

        self.pushButtonAllPosition.clicked.connect(self._save_defaults)


    def save_position(self):
        if self.cent_pos_1.text():
            pos = self._text_to_list(self.cent_pos_1.text())
            self.centrifuge.update_position(0, pos)
            pick_dir = self.pick_dir_1.currentText()
            print(pick_dir)
            self.rack.rack_pick_dir[0] = True if pick_dir == 'Regular' else False

        if self.cent_pos_2.text():
            pos = self._text_to_list(self.cent_pos_2.text())
            self.centrifuge.update_position(1, pos)
            pick_dir = self.pick_dir_2.currentText()
            print(pick_dir)
            self.rack.rack_pick_dir[1] = True if pick_dir == 'Regular' else False

        if self.cent_pos_3.text():
            pos = self._text_to_list(self.cent_pos_3.text())
            self.centrifuge.update_position(2, pos)
            pick_dir = self.pick_dir_3.currentText()
            self.rack.rack_pick_dir[2] = True if pick_dir == 'Regular' else False

        if self.cent_pos_4.text():
            pos = self._text_to_list(self.cent_pos_4.text())
            self.centrifuge.update_position(3, pos)
            pick_dir = self.pick_dir_4.currentText()
            self.rack.rack_pick_dir[3] = True if pick_dir == 'Regular' else False

        if self.cent_pos_5.text():
            pos = self._text_to_list(self.cent_pos_5.text())
            self.centrifuge.update_position(4, pos)
            pick_dir = self.pick_dir_5.currentText()
            self.rack.rack_pick_dir[4] = True if pick_dir == 'Regular' else False

        if self.cent_pos_6.text():
            pos = self._text_to_list(self.cent_pos_6.text())
            self.centrifuge.update_position(5, pos)
            pick_dir = self.pick_dir_6.currentText()
            self.rack.rack_pick_dir[5] = True if pick_dir == 'Regular' else False

        if self.rack_pos_1.text():
            pos = self._text_to_list(self.rack_pos_1.text())
            self.rack.update_position(0, pos)
            pick_dir = self.pick_dir_1.currentText()
            self.rack.rack_pick_dir[0] = True if pick_dir == 'Regular' else False

        if self.rack_pos_2.text():
            pos = self._text_to_list(self.rack_pos_2.text())
            self.rack.update_position(1, pos)
            pick_dir = self.pick_dir_2.currentText()
            self.rack.rack_pick_dir[1] = True if pick_dir == 'Regular' else False
            
        if self.rack_pos_3.text():
            pos = self._text_to_list(self.rack_pos_3.text())
            self.rack.update_position(2, pos)
            pick_dir = self.pick_dir_3.currentText()
            self.rack.rack_pick_dir[2] = True if pick_dir == 'Regular' else False

        if self.rack_pos_4.text():
            pos = self._text_to_list(self.rack_pos_4.text())
            self.rack.update_position(3, pos)
            pick_dir = self.pick_dir_4.currentText()
            self.rack.rack_pick_dir[3] = True if pick_dir == 'Regular' else False

        if self.rack_pos_5.text():
            pos = self._text_to_list(self.rack_pos_5.text())
            self.rack.update_position(4, pos)
            pick_dir = self.pick_dir_5.currentText()
            self.rack.rack_pick_dir[4] = True if pick_dir == 'Regular' else False

        if self.rack_pos_6.text():
            pos = self._text_to_list(self.rack_pos_6.text())
            self.rack.update_position(5, pos)
            pick_dir = self.pick_dir_6.currentText()
            self.rack.rack_pick_dir[5] = True if pick_dir == 'Regular' else False

    
    def _save_defaults(self):
        for i, pos in enumerate(self.defaul_pick):
            self.rack.update_position(i, pos)
        
        for i, pos in enumerate(self.defaul_place):
            self.centrifuge.update_position(i, pos)

        self.rack.rack_pick_dir[0] = False
        self.rack.rack_pick_dir[1] = False
        self.rack.rack_pick_dir[2] = False


    def _text_to_list(self, text):
        text = re.sub('[()]', '', text)
        text_split = text.split(',')
        num_list = [float(i) for i in text_split]
        return num_list
        

class ProgressWindowApp(QtWidgets.QMainWindow, ProgressWindow.Ui_MainWindow):
    def __init__(self, rack, centrifuge, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)
        self.progressBar.setValue(0)
        self.label.setText("Starting the centrifuge")
        self.move(346, 250)
        

    def start_progress(self):
        self.progressBar.setValue(0)
        self.label.setText("Starting the centrifuge")
        QCoreApplication.processEvents()
        sleep(5)
        self.label.setText("Processing Samples")
        for i in range(100):
            self.progressBar.setValue(i+1)
            sleep(0.1)
            QCoreApplication.processEvents()

    def unload_cent(self):
        self.label.setText("Unloading Vials")
        QCoreApplication.processEvents()

    def close_window(self):
        self.close()


class Application(QtWidgets.QMainWindow, MainWindow.Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        QtWidgets.QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

        ### Frontend setup ###
        
        self.setStyleSheet("background-color:white")

        current_dir = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))
        pixmap_logo = QPixmap(os.path.join(parent_dir, 'frontend/images/mecademic-logo.png'))
        pixmap_logo = pixmap_logo.scaledToWidth(400)
        self.logo.setPixmap(pixmap_logo)
        self.buttonAutoMode.setCheckable(True)
        self.buttonCentrifuge.setEnabled(False)

        ### Backend setup ###
        self.robot = Robot()
        self.rack = MainRack(6)
        self.centrifuge = Centrifuge(6)
        self.autoThread = None
        self.autoWorker = None

        ### Setup Window Setup ###
        self.setup_window = SetupWindow(self.rack, self.centrifuge)

        self.actionSetup.triggered.connect(self.open_setup)

        ### Progress Window Setup ###
        self.progress_window = ProgressWindowApp(self.rack, self.centrifuge)

        ### Button connections ###

        self.LoadButton.clicked.connect(self.load_centrifuge)
        self.RackSelection.button_list[0].clicked.connect(lambda: self.toggle_select_vial(0))
        self.RackSelection.button_list[1].clicked.connect(lambda: self.toggle_select_vial(1))
        self.RackSelection.button_list[2].clicked.connect(lambda: self.toggle_select_vial(2))
        self.RackSelection.button_list[3].clicked.connect(lambda: self.toggle_select_vial(3))
        self.RackSelection.button_list[4].clicked.connect(lambda: self.toggle_select_vial(4))
        self.RackSelection.button_list[5].clicked.connect(lambda: self.toggle_select_vial(5))

        self.buttonCentrifuge.clicked.connect(self.start_centrifuge)
        self.buttonRobot.clicked.connect(self.connect_to_robot)
        self.buttonAutoMode.clicked.connect(self.buttonAutoFunction)


    def open_setup(self):
        self.setup_window.show()

    def open_progress(self):
        self.progress_window.show()
        self.progress_window.start_progress()

    def unload_window(self):
        self.progress_window.unload_cent()

    def toggle_select_vial(self, n):
        self.rack.vial_selected[n] = not self.rack.vial_selected[n]

    def connect_to_robot(self):
        if not self.robot.IsConnected():
            try:
                self.robot.Connect()
                self.robot.ActivateAndHome()
                self.robot.WaitHomed()
                self.buttonRobot.setStyleSheet("background-color:rgba(0,255,0,255)")
            except CommunicationError as e:
                print(e)
        else:
            self.robot.Disconnect()
            self.buttonRobot.setStyleSheet("background-color:rgba(0,0,0,125)")

    def load_centrifuge(self):
        # Check centrifuge status
        if not self.centrifuge.cent_status:
            msgbox = QtWidgets.QMessageBox()
            msgbox.setIcon(QtWidgets.QMessageBox.Information)
            msgbox.setText("Centrifuge is not ready to be loaded.")
            msgbox.setWindowTitle("Centrifuge Warning")
            msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

            msgbox.exec()
            return

        if True in self.centrifuge.rack_status:
            msgbox = QtWidgets.QMessageBox()
            msgbox.setIcon(QtWidgets.QMessageBox.Information)
            msgbox.setText("There are still vials in the centrifuge.")
            msgbox.setWindowTitle("Centrifuge Warning")
            msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

            msgbox.exec()
            return
        # Check selected vials status
        if not (True in self.rack.vial_selected):
            msgbox = QtWidgets.QMessageBox()
            msgbox.setIcon(QtWidgets.QMessageBox.Information)
            msgbox.setText("Please select one or multiple vials before loading.")
            msgbox.setWindowTitle("Rack Warning")
            msgbox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)

            msgbox.exec()
            return
        
        # Disable all buttons during loading
        self.LoadButton.setEnabled(False)
        self.buttonAutoMode.setEnabled(False)
        self.buttonCentrifuge.setEnabled(False)
        self.buttonRobot.setEnabled(False)
        self.RackSelection.disableButtons()
        QCoreApplication.processEvents()

        # Load them in the centrifuge
        self.robot.SetJointVel(40)
        self.robot.SetCartLinVel(30)
        self.robot.GripperOpen()

        for i, st in enumerate(self.rack.vial_selected):
            if st:
                self.robot.MoveJoints(90, 0, 0, 0, 0, 0)
                self.RackStatusDisplay.turn_vial_off(i)
                # Picking
                pick_point = self.rack.rack_position[i]
                if self.rack.rack_pick_dir[i]:
                    self.pick_reg(pick_point)
                else:
                    self.pick_front(pick_point)

                self.robot.MoveJoints(0, 0, 0, 0, 45, 0)

                place_point = self.centrifuge.rack_position[i]
                if self.rack.rack_pick_dir[i]:
                    self.place_reg(place_point)
                else:
                    self.place_front(place_point)
                
                # UI stuff
                cp = self.robot.SetCheckpoint(50)
                cp.wait()
                self.RackSelection.button_list[i].setChecked(False)
                self.RackSelection.button_list[i]._on_pressed_col_change()
                self.RackSelection.button_list[i].setEnabled(False)
                self.CentStatusDisplay.toggle_led(i)
                QCoreApplication.processEvents()

        self.robot.MoveJoints(0, 0, 0, 0, 0, 0)
        self.buttonCentrifuge.setEnabled(True)


    def pick_reg(self, point):
        self.robot.SetTRF(49, 0, 14, 0, -90, 0)
        self.robot.SetWRF(*point)
        self.robot.MovePose(-16, 0, 30, 0, 0, 0)
        self.robot.MovePose(-16, 0, 0, 0, 0, 0)      # Approach, modify this depending on the orientation
        self.robot.MoveLin(0, 0, 0, 0, 0, 0)        # Pick
        self.robot.GripperClose()
        self.robot.Delay(1)
        self.robot.MoveLin(0, 0, 120, 0, 0, 0)


    def pick_front(self, point):
        self.robot.SetTRF(30, 0, 17, -180, 0, -180)
        self.robot.SetWRF(*point)
        self.robot.MovePose(0, 0, 20, 0, 0, 0)
        self.robot.MoveLin(0, 0, 0, 0, 0, 0)
        self.robot.GripperClose()
        self.robot.Delay(0.5)
        self.robot.MoveLin(0, 0, 100, 0, 0, 0)

    def place_reg(self, point):
        self.robot.SetTRF(49, 0, 14, 0, -90, 0)
        self.robot.SetWRF(*point)
        self.robot.MovePose(0, 0, 80, 0, 0, 0)
        self.robot.MoveLin(0, 0, 0, 0, 0, 0)
        self.robot.GripperOpen()
        self.robot.Delay(0.5)
        self.robot.MoveLin(-30, 0, 0, 0, 0, 0)

    def place_front(self, point):
        self.robot.SetTRF(30, 0, 17, -180, 0, -180)
        self.robot.SetWRF(*point)
        self.robot.MovePose(0, 0, 80, 0, 0, 0)
        self.robot.MoveLin(0, 0, 0, 0, 0, 0)
        self.robot.GripperOpen()
        self.robot.Delay(0.5)
        self.robot.MoveLin(0, 0, 80, 0, 0 ,0)

    def ret_pick_front(self, point):
        self.robot.SetTRF(30, 0, 17, -180, 0, -180)
        self.robot.SetWRF(*point)
        self.robot.MovePose(0, 0, 80, 0, 0, 0)
        self.robot.MoveLin(0, 0, 0, 0, 0, 0)
        self.robot.GripperClose()
        self.robot.Delay(0.5)
        self.robot.MoveLin(0, 0, 80, 0, 0 ,0)

    def ret_pick_reg(self, point):
        self.robot.SetTRF(49, 0, 14, 0, -90, 0)
        self.robot.SetWRF(*point)
        self.robot.MovePose(-30, 0, 0, 0, 0, 0)
        self.robot.MoveLin(0, 0, 0, 0, 0, 0)
        self.robot.GripperClose()
        self.robot.Delay(0.5)
        self.robot.MoveLin(0, 0, 80, 0, 0, 0)

    def ret_place_front(self, point):
        self.robot.SetTRF(30, 0, 17, -180, 0, -180)
        self.robot.SetWRF(*point)
        self.robot.MovePose(0, 0, 100, 0, 0, 0)
        self.robot.MoveLin(0, 0, 0, 0, 0, 0)
        self.robot.GripperOpen()
        self.robot.Delay(0.5)
        self.robot.MoveLin(0, 0, 20, 0, 0, 0)

    def ret_place_reg(self, point):
        self.robot.SetTRF(49, 0, 14, 0, -90, 0)
        self.robot.SetWRF(*point)
        self.robot.MovePose(0, 0, 120, 0, 0, 0)
        self.robot.MoveLin(0, 0, 0, 0, 0, 0)        # Pick
        self.robot.GripperOpen()
        self.robot.Delay(0.5)
        self.robot.MoveLin(-16, 0, 0, 0, 0, 0)      # Approach, modify this depending on the orientation
        self.robot.MoveLin(-16, 0, 30, 0, 0, 0)

    def start_centrifuge(self):
        self.buttonCentrifuge.setEnabled(False)
        self.open_progress()
        sleep(2)
        self.unload_window()

        ### Place back the vials ###
        self.robot.SetJointVel(40)
        self.robot.SetCartLinVel(25)
        self.robot.GripperOpen()
        
        for i, st in enumerate(self.rack.vial_selected):
            if st:
                self.robot.MoveJoints(0, 0, 0, 0, 0, 0)
                pick_point = self.centrifuge.rack_position[i]
                if self.rack.rack_pick_dir[i]:
                    self.ret_pick_reg(pick_point)
                else:
                    self.ret_pick_front(pick_point)

                self.robot.MoveJoints(0, 0, 0, 0, 45, 0)

                place_point = self.rack.rack_position[i]
                if self.rack.rack_pick_dir[i]:
                    self.ret_place_reg(place_point)
                else:
                    self.ret_place_front(place_point)

                cp = self.robot.SetCheckpoint(42)
                cp.wait()
                self.RackSelection.button_list[i].setEnabled(True)
                self.RackSelection.button_list[i].setChecked(False)
                self.RackStatusDisplay.turn_vial_on(i)
                self.rack.vial_selected[i] = False
                self.CentStatusDisplay.toggle_led(i)
                QCoreApplication.processEvents()

        self.robot.MoveJoints(90, 0, 0, 0, 0, 0)
        self.centrifuge.cent_status = True
        self.progress_window.close_window()
        self.buttonAutoMode.setEnabled(True)
        self.buttonRobot.setEnabled(True)
        self.LoadButton.setEnabled(True)
        self.RackSelection.enableButtons()


    def startAutoMode(self):
        self.RackSelection.disableButtons()
        self.buttonRobot.setEnabled(False)
        self.buttonCentrifuge.setEnabled(False)
        self.LoadButton.setEnabled(False)
        self.autoThread = QThread()
        self.autoWorker = AutoModeWorker(self.robot, self.rack, self.centrifuge)
        self.autoWorker.moveToThread(self.autoThread)
        self.autoThread.started.connect(self.autoWorker.run)
        self.autoWorker.finished.connect(self.autoThread.quit)
        self.autoWorker.finished.connect(self.autoWorker.deleteLater)
        self.autoWorker.finished.connect(self.RackSelection.enableButtons)
        self.autoWorker.finished.connect(lambda: self.buttonRobot.setEnabled(True))
        self.autoWorker.finished.connect(lambda: self.buttonCentrifuge.setEnabled(True))
        self.autoWorker.finished.connect(lambda: self.LoadButton.setEnabled(True))
        self.autoThread.finished.connect(self.autoThread.deleteLater)

        self.autoThread.start()

    def buttonAutoFunction(self):
        if self.buttonAutoMode.isChecked():
            self.startAutoMode()
        else:
            self.autoWorker.toggleFinish()


    def closeEvent(self, event):
        self.robot.Disconnect()
        super().closeEvent(event)


    ### Test functions ###
    def print_data(self):
        print(self.centrifuge.rack_position[0])


class AutoModeWorker(QObject):
    finished = pyqtSignal()

    def __init__(self, robot, rack, cent):
        super().__init__()
        self.robot = robot
        self.rack = rack
        self.cent = cent


    def run(self):
        self.goFlag = True
        self.robot.SetJointVel(40)
        self.robot.SetCartLinVel(25)
        while(self.goFlag):
            for rack_pos, pick_dir, cent_pos in zip(self.rack.rack_position, self.rack.rack_pick_dir, self.cent.rack_position):
                # Pick from the rack
                self.robot.MoveJoints(90, 0, 0, 0, 0, 0)
                if pick_dir:
                    self.pick_reg(rack_pos)
                else:
                    self.pick_front(rack_pos)

                self.robot.MoveJoints(0, 0, 0, 0, 45, 0)

                # Drop in the centrifuge
                if pick_dir:
                    self.place_reg(cent_pos)
                else:
                    self.place_front(cent_pos)

            # Wait a bit
            cp = self.robot.SetCheckpoint(82)
            cp.wait()
            self.robot.MoveJoints(0, 0, 0, 0, 0, 0)
            cp = self.robot.SetCheckpoint(82)
            cp.wait()
            sleep(3)

            for rack_pos, pick_dir, cent_pos in zip(self.rack.rack_position, self.rack.rack_pick_dir, self.cent.rack_position):
                # Pick from centrifuge
                self.robot.MoveJoints(0, 0, 0, 0, 45, 0)
                if pick_dir:
                    self.ret_pick_reg(cent_pos)
                else:
                    self.ret_pick_front(cent_pos)
                # Place back in rack
                self.robot.MoveJoints(0, 0, 0, 0, 45, 0)

                if pick_dir:
                    self.ret_place_reg(rack_pos)
                else:
                    self.ret_place_front(rack_pos)
                
            
            cp = self.robot.SetCheckpoint(82)
            cp.wait()
            self.robot.MoveJoints(0, 0, 0, 0, 0, 0)

        self.finished.emit()


    def toggleFinish(self):
        self.goFlag = False


    def pick_reg(self, point):
        self.robot.SetTRF(49, 0, 14, 0, -90, 0)
        self.robot.SetWRF(*point)
        self.robot.MovePose(-16, 0, 30, 0, 0, 0)
        self.robot.MovePose(-16, 0, 0, 0, 0, 0)      # Approach, modify this depending on the orientation
        self.robot.MoveLin(0, 0, 0, 0, 0, 0)        # Pick
        self.robot.GripperClose()
        self.robot.Delay(1)
        self.robot.MoveLin(0, 0, 120, 0, 0, 0)


    def pick_front(self, point):
        self.robot.SetTRF(30, 0, 17, -180, 0, -180)
        self.robot.SetWRF(*point)
        self.robot.MovePose(0, 0, 20, 0, 0, 0)
        self.robot.MoveLin(0, 0, 0, 0, 0, 0)
        self.robot.GripperClose()
        self.robot.Delay(0.5)
        self.robot.MoveLin(0, 0, 100, 0, 0, 0)

    def place_reg(self, point):
        self.robot.SetTRF(49, 0, 14, 0, -90, 0)
        self.robot.SetWRF(*point)
        self.robot.MovePose(0, 0, 80, 0, 0, 0)
        self.robot.MoveLin(0, 0, 0, 0, 0, 0)
        self.robot.GripperOpen()
        self.robot.Delay(0.5)
        self.robot.MoveLin(-30, 0, 0, 0, 0, 0)

    def place_front(self, point):
        self.robot.SetTRF(30, 0, 17, -180, 0, -180)
        self.robot.SetWRF(*point)
        self.robot.MovePose(0, 0, 80, 0, 0, 0)
        self.robot.MoveLin(0, 0, 0, 0, 0, 0)
        self.robot.GripperOpen()
        self.robot.Delay(0.5)
        self.robot.MoveLin(0, 0, 80, 0, 0 ,0)

    def ret_pick_front(self, point):
        self.robot.SetTRF(30, 0, 17, -180, 0, -180)
        self.robot.SetWRF(*point)
        self.robot.MovePose(0, 0, 80, 0, 0, 0)
        self.robot.MoveLin(0, 0, 0, 0, 0, 0)
        self.robot.GripperClose()
        self.robot.Delay(0.5)
        self.robot.MoveLin(0, 0, 80, 0, 0 ,0)

    def ret_pick_reg(self, point):
        self.robot.SetTRF(49, 0, 14, 0, -90, 0)
        self.robot.SetWRF(*point)
        self.robot.MovePose(-30, 0, 0, 0, 0, 0)
        self.robot.MoveLin(0, 0, 0, 0, 0, 0)
        self.robot.GripperClose()
        self.robot.Delay(0.5)
        self.robot.MoveLin(0, 0, 80, 0, 0, 0)

    def ret_place_front(self, point):
        self.robot.SetTRF(30, 0, 17, -180, 0, -180)
        self.robot.SetWRF(*point)
        self.robot.MovePose(0, 0, 100, 0, 0, 0)
        self.robot.MoveLin(0, 0, 0, 0, 0, 0)
        self.robot.GripperOpen()
        self.robot.Delay(0.5)
        self.robot.MoveLin(0, 0, 20, 0, 0, 0)

    def ret_place_reg(self, point):
        self.robot.SetTRF(49, 0, 14, 0, -90, 0)
        self.robot.SetWRF(*point)
        self.robot.MovePose(0, 0, 120, 0, 0, 0)
        self.robot.MoveLin(0, 0, 0, 0, 0, 0)        # Pick
        self.robot.GripperOpen()
        self.robot.Delay(0.5)
        self.robot.MoveLin(-16, 0, 0, 0, 0, 0)      # Approach, modify this depending on the orientation
        self.robot.MoveLin(-16, 0, 30, 0, 0, 0)