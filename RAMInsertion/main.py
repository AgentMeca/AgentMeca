from forceFunctions import FindSurface, MoveThread, ClickDetection
from mecademicpy.robot import Robot
from NetFT import Sensor
from queue import Queue
from time import sleep


sensor = Sensor('192.168.0.101')
q = Queue()
robot = Robot()

#fs = FindSurface(1, 'FindSurface', 1, sensor, q, 15)
cd = ClickDetection(1, 'Click', 2, sensor, q, 80, 5)
move = MoveThread(2, 'Move', 2, robot, q)
move.connect()
move.move_settings(speed=5)


#First insertion
robot.StartOfflineProgram(11)
cp = robot.SetCheckpoint(10)
cp.wait()


#MODIFY POINT 1 FOR CLICK DETECTION
print("Moving to point 1")
robot.MoveJoints(112.965,13.578,17.458,0,58.964,74.973)

print('Starting Thread')
#fs.start()
cd.start()
move.start()

while q.empty():
    sleep(1)

print(q.get())

cd.join()
move.join()

with q.mutex:
    q.queue.clear()

#MODIFY POINT 2 FOR CLICK DETECTION
print("Moving to point 2")
robot.MoveJoints(74.164,10.85,20.824,0,58.326,36.172)

cd = ClickDetection(1, 'Click', 2, sensor, q, 80, 8)
move = MoveThread(2, 'Move', 2, robot, q)
move.move_settings(speed=5)

print('Starting Thread')
#fs.start()
cd.start()
move.start()

while q.empty():
    sleep(1)

print(q.get())



sleep(3)
robot.Disconnect()