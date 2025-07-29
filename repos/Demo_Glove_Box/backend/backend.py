from mecademicpy.robot import Robot
from scipy.spatial.transform import Rotation
import numpy as np


class MainRack():
    def __init__(self, n) -> None:
        self.rack_status = [True]*n       # True if vial is present False if not
        self.rack_position = list()     # List of positions for every rack point
        self.rack_pick_dir = list()
        self.vial_selected = [False]*n

        for i in range(n):
            self.rack_position.append([0,0,0,0,0,0])
            self.rack_pick_dir.append(True)             # True for regular False for front pick
    
    def update_position(self, n, pos):
        self.rack_position[n] = pos

    def update_status(self, n, status):
        self.rack_status[n] = status
    

class Centrifuge():
    def __init__(self, n) -> None:
        self.rack_status = [False]*n        # True if vial is present False if not
        self.rack_position = list()         # List of positions for every rack point
        self.cent_status = True             # True if ready to be loaded
        
        for i in range(n):
            self.rack_position.append([0,0,0,0,0,0])

    def update_position(self, n, pos):
        self.rack_position[n] = pos

    def update_status(self, n, status):
        self.rack_status[n] = status


def projectvector(mov_vect, rot_vect):
    rot_mat = Rotation.from_euler('ZYX', rot_vect)
    rot_mat_num = rot_mat.as_matrix().transpose()
    return np.dot(rot_mat_num, mov_vect)
