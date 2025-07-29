from NetFT import Sensor
from threading import Thread
from queue import Queue
from mecademicpy.robot import Robot
from time import sleep


# MOVEMENT FUNCTIONS AND THREADS
class MoveThread(Thread):
    def __init__(self, threadid, name, counter, robot: Robot, queue: Queue):
        Thread.__init__(self)
        self.threadid = threadid
        self.name = name
        self.counter = counter
        self.robot = robot
        self.queue = queue
        self.vel = 0
        self.direction = [0, 0, 0, 0, 0, 0]

    def move_settings(self, speed=1, direction="z+"):
        self.vel = speed
        if direction.upper() == "Z+":
            self.direction = [0, 0, 1, 0, 0, 0]
        elif direction.upper() == "Z-":
            self.direction = [0, 0, -1, 0, 0, 0]
        elif direction.upper() == "Y+":
            self.direction = [0, 1, 0, 0, 0, 0]
        elif direction.upper() == "Y-":
            self.direction = [0, -1, 0, 0, 0, 0]
        elif direction.upper() == "X+":
            self.direction = [1, 0, 0, 0, 0, 0]
        elif direction.upper() == "X-":
            self.direction = [-1, 0, 0, 0, 0, 0]
        else:
            raise ValueError('The direction is not valid')

    def connect(self, address='192.168.0.100'):
        self.robot.Connect(address)
        self.robot.ActivateRobot()
        self.robot.Home()

    def run(self):
        self.robot.ResumeMotion()
        while(True):
            if not self.queue.empty():
                val = self.queue.get()
                if val == 'stop':
                    deltamove = [10*x*-1.0 for x in self.direction]
                    self.robot.MoveLinRelTRF(*deltamove)
                    self.queue.put('finished')
                    break
            else:
                vel_move = [self.vel*x for x in self.direction]
                self.robot.MoveLinVelTRF(*vel_move)
                sleep(0.001)

# FORCE MONITORING AND THREADS
class _ForceThread(Thread):
    def __init__(self, threadid, name, counter, sensor: Sensor, queue: Queue):
        Thread.__init__(self)
        self.threadid = threadid
        self.name = name
        self.counter = counter
        self.sensor = sensor
        self.queue = queue


class FindSurface(_ForceThread):
    def __init__(self, threadid, name, counter, sensor, queue, force, direction=2):
        super().__init__(threadid, name, counter, sensor, queue)
        self.force = force
        self.direction = direction

    def run(self):
        self.sensor.zero()
        sleep(0.5)
        while(True):
            force = self.sensor.getForce()[self.direction]
            sleep(0.001)
            if (-1.0*force) > self.force:
                self.queue.put('stop')
                break

class ClickDetection(_ForceThread):
    def __init__(self, threadid, name, counter, sensor: Sensor, queue: Queue, max_force, force_delta, direction=2):
        super().__init__(threadid, name, counter, sensor, queue)
        self.max_force = max_force
        self.force_delta = force_delta
        self.direction = direction

    def run(self):
        self.sensor.zero()
        sleep(0.50)
        peak_force = 0
        while(True):
            force = (-1)*self.sensor.getForce()[self.direction]
            if force > self.max_force:
                print("Reached max force")
                self.queue.put('stop')
                break
            if force>peak_force:
                peak_force = force
            force_diff = peak_force-force
            if force_diff > self.force_delta:
                print("Click detected!")
                print(force_diff)
                self.queue.put('stop')
                break


