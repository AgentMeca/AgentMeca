from mecademicpy.robot import Robot
from time import sleep


def pick1(robot):
    robot.MovePose(188.3713,24.6400,94.7630,0.0000,90.0000,0.0000)
    robot.MoveLin(188.3713,24.6400,79.7630,0.0000,90.0000,0.0000)
    robot.GripperClose
    robot.Delay(1)
    robot.MoveLinRelWRF(0,0,30,0,0,0)

def place1(robot):
    robot.MovePose(175.3589,137.8812,94.5631,-89.9999,-0.0003,90.0000)
    robot.MoveLin(175.3589,137.8812,79.5631,-89.9999,-0.0003,90.0000)
    robot.GripperOpen
    robot.Delay(1)
    robot.MoveLinRelWRF(0,0,30,0,0,0)

def pick2(robot):
    robot.MovePose(195.6913,-137.8000,90.9030,-0.0000,90.0000,0.0000)
    robot.MoveLin(195.6913,-137.8000,75.9030,-0.0000,90.0000,0.0000)
    robot.GripperClose
    robot.Delay(2)
    robot.MoveLinRelWRF(0,0,40,0,0,0)

def place2(robot):
    robot.MovePose(121.6163,187.5200,91.8830,0.0000,90.0000,0.0000)
    robot.MoveLin(121.6163,187.5200,76.8830,0.0000,90.0000,0.0000)
    robot.GripperOpen
    robot.Delay(2)
    robot.MoveLinRelWRF(0,0,40,0,0,0)

def pick_back1(robot):
    robot.MovePose(175.3589,137.8812,94.5631,-89.9999,-0.0003,90.0000)
    robot.MoveLin(175.3589,137.8812,79.5631,-89.9999,-0.0003,90.0000)
    robot.GripperClose
    robot.Delay(1)
    robot.MoveLinRelWRF(0,0,30,0,0,0)

def place_back1(robot):
    robot.MovePose(188.3713,24.6400,94.7630,0.0000,90.0000,0.0000)
    robot.MoveLin(188.3713,24.6400,79.7630,0.0000,90.0000,0.0000)
    robot.GripperOpen
    robot.Delay(1)
    robot.MoveLinRelWRF(0,0,30,0,0,0)

def pick_back2(robot):
    robot.MovePose(121.6163,187.5200,91.8830,0.0000,90.0000,0.0000)
    robot.MoveLin(121.6163,187.5200,76.8830,0.0000,90.0000,0.0000)
    robot.GripperClose
    robot.Delay(2)
    robot.MoveLinRelWRF(0,0,40,0,0,0)

def place_back2(robot):
    robot.MovePose(195.6913,-137.8000,90.9030,-0.0000,90.0000,0.0000)
    robot.MoveLin(195.6913,-137.8000,75.9030,-0.0000,90.0000,0.0000)
    robot.GripperOpen
    robot.Delay(2)
    robot.MoveLinRelWRF(0,0,40,0,0,0)
    robot.MoveJoints(90,0,0,0,0,0)

def pick_cover1(robot):
    robot.MoveJoints(0,0,0,0,90,0)
    robot.MovePose(214.0700,-23.8950,51.9300,180.0000,0.0000,180.0000)
    robot.MoveLin(214.0700,-23.8950,46.9300,180.0000,0.0000,180.0000)
    robot.MoveLinRelWRF(0,0,-0.75,0,0,0)
    robot.Delay(0.5)
    robot.MoveLinRelWRF(0,0,30,0,0,0)

def pick_cover2(robot):
    robot.MovePose(202.9425,138.5550,57.9300,-180.0000,-0.0000,90.0000)
    robot.MoveLin(202.9425,138.5550,47.2600,180.0000,-0.0000,90.0000)
    robot.MoveLinRelWRF(0,0,-0.75,0,0,0)
    robot.Delay(0.5)
    robot.MoveLinRelWRF(0,0,30,0,0,0)

def place_cover(robot):
    robot.MovePose(30.5054,-186.1501,92.3399,170.7854,-9.8911,-90.1511)
    robot.MoveLin(30.5054,-186.1501,62.3399,170.7854,-9.8911,-90.1511)
    robot.MoveLinRelTRF(0,0,0,0,0,-10)
    robot.MoveLinRelWRF(0,0,40,0,0,0)

def pick_back_cover(robot):
    robot.MovePose(32.3727,-179.0600,70.2686,170.7854,-9.8911,-90.1511)
    robot.MoveLin(32.3727,-179.0600,60.2686,170.7854,-9.8911,-90.1511)
    robot.MoveLinRelTRF(0,0,0.75,0,0,0)
    robot.Delay(0.5)
    robot.MoveLinRelWRF(0,0,40,0,0,0)

def push_corner1(robot):
    # y
    robot.MovePose(210.9000,-106.6150,52.2000,-180.0000,-0.0000,-180.0000)
    robot.MovePose(210.9000,-106.6150,42.2000,-180.0000,-0.0000,-180.0000)
    robot.MoveLin(210.9000,-101.6150,42.2000,-180.0000,-0.0000,-180.0000)
    robot.MoveLinRelWRF(0,-10,0,0,0,0)
    robot.MoveLinRelWRF(0,0,30,0,0,0)
    # x
    robot.MovePose(155.0550,-21.6900,49.4000,-180.0000,-0.0000,-180.0000)
    robot.MovePose(155.0550,-21.6900,39.4000,-180.0000,-0.0000,-180.0000)
    robot.MoveLin(158.0550,-21.6900,39.4000,-180.0000,-0.0000,-180.0000)
    robot.MoveLinRelWRF(-10,0,0,0,0,0)
    robot.MoveLinRelWRF(0,0,30,0,0,0)

def place_back_cover1(robot):
    robot.MovePose(209.4450,-25.9775,67.6125,-180.0000,-0.0000,-180.0000)
    robot.MoveLin(209.4450,-25.9775,49.6125,-180.0000,-0.0000,-180.0000)
    robot.MoveLinRelTRF(0,0,0,0,0,10)
    robot.MoveLinRelWRF(0,0,40,0,0,0)

def push_corner2(robot):
    # x
    robot.MovePose(120.2075,138.5550,48.5100,180.0000,0.0000,90.0000)
    robot.MoveLin(120.2075,138.5550,38.5100,180.0000,0.0000,90.0000)
    robot.MoveLin(126.6075,138.5550,38.5100,180.0000,0.0000,90.0000)
    robot.MoveLinRelWRF(-10,0,0,0,0,0)
    robot.MoveLinRelWRF(0,0,40,0,0,0)
    # y
    robot.MovePose(202.9425,75.7150,48.6250,180.0000,0.0000,90.0000)
    robot.MoveLin(202.9425,75.7150,38.6250,180.0000,0.0000,90.0000)
    robot.MoveLin(202.9425,81.0150,38.6250,180.0000,0.0000,90.0000)
    robot.MoveLinRelWRF(0,-10,0,0,0,0)
    robot.MoveLinRelWRF(0,0,40,0,0,0)

def place_back_cover2(robot):
    robot.MovePose(201.9025,134.4050,64.6075,180.0000,-0.0000,90.0000)
    robot.MoveLin(201.9025,134.4050,49.6075,180.0000,-0.0000,90.0000)
    robot.MoveLinRelWRF(0,0,0,0,0,10)
    robot.MoveLinRelWRF(0,0,40,0,0,0)


# Setup of the robots
robot1 = Robot()
robot2 = Robot()

robot1.Connect('192.168.0.100')
robot1.ActivateAndHome()
robot1.WaitHomed()
robot1.GripperOpen()

robot2.Connect('192.168.0.101')
robot2.ActivateAndHome()
robot2.WaitHomed()

# Initial movements
robot1.SetJointVel(25)
robot1.SetCartLinVel(30)
robot1.MoveJoints(90,0,0,0,0,0)
cp1 = robot1.SetCheckpoint(100)
cp1.wait()

robot2.SetJointVel(25)
robot2.SetCartLinVel(30)
robot2.SetCartAngVel(50)
robot2.MoveJoints(-90,0,0,0,0,0)
cp2 = robot2.SetCheckpoint(101)
cp2.wait()

# Main loop
while(True):
    #### First plate ####
    pick_cover1(robot2)
    place_cover(robot2)
    cp101 = robot2.SetCheckpoint(101)
    cp101.wait()

    pick1(robot1)
    place1(robot1)
    cp100 = robot1.SetCheckpoint(100)
    cp100.wait()

    sleep(5)

    pick_back1(robot1)
    place_back1(robot1)
    robot1.MoveJoints(90,0,0,0,0,0)
    cp100 = robot1.SetCheckpoint(100)
    cp100.wait()

    push_corner1(robot2)
    pick_back_cover(robot2)
    place_back_cover1(robot2)
    cp101 = robot2.SetCheckpoint(101)
    cp101.wait()

    #### Second plate ####
    pick_cover2(robot2)
    place_cover(robot2)
    cp101 = robot2.SetCheckpoint(101)
    cp101.wait()

    pick2(robot1)
    place2(robot1)
    cp100 = robot1.SetCheckpoint(100)
    cp100.wait()

    sleep(5)

    pick_back2(robot1)
    place_back2(robot1)
    robot1.MoveJoints(90,0,0,0,0,0)
    cp100 = robot1.SetCheckpoint(100)
    cp100.wait()

    push_corner2(robot2)
    pick_back_cover(robot2)
    place_back_cover2(robot2)
    cp101 = robot2.SetCheckpoint(101)
    cp101.wait()

