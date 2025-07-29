from scipy.spatial.transform import Rotation
import numpy as np


#176.1681,-115.5000,132.3339,1.0047,41.2785,-0.2306

#191.7180,89.5500,107.4340,0.0000,-0.0000,0
#191.7180,89.5500,107.4340,0.0000,-0.0000,180
rot_vect = [160.5217,-8.3275,112.2682]
rot_vect.reverse()

rot_mat = Rotation.from_euler('ZYX', rot_vect)
rot_mat_num = rot_mat.as_matrix()


