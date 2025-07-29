from mecademicpy.robot import Robot
from zaber_motion import Units, Library, DeviceDbSourceType
from zaber_motion.ascii import Connection

Library.set_device_db_source(
    DeviceDbSourceType.FILE, "./devices-public.sqlite")

# Robot Setup
gripper = Robot()
gluing = Robot()
screwing = Robot()
testing = Robot()

# Zaber Setup
with Connection.open_serial_port("COM5") as connection:
    device_list = connection.detect_devices()
    print("Found {} devices".format(len(device_list)))

    zaber = device_list[0].get_axis(1)
    zaber.home()

    # Activate and home all the robots and move them all in position

    gripper.Connect()
    print('Gripper Robot Connected')
    gripper.SetMonitoringInterval(0.1)
    gluing.Connect('192.168.0.101')
    print('Gluing Robot Connected')
    gluing.SetMonitoringInterval(0.1)
    screwing.Connect('192.168.0.102')
    print('Screwing Robot Connected')
    screwing.SetMonitoringInterval(0.1)
    testing.Connect('192.168.0.103')
    print('Testing Robot Connected')
    testing.SetMonitoringInterval(0.1)

    gripper.ActivateAndHome()
    gluing.ActivateAndHome()
    screwing.ActivateAndHome()
    testing.ActivateAndHome()

    gripper.WaitHomed()
    gluing.WaitHomed()
    screwing.WaitHomed()
    testing.WaitHomed()

    gripper.ResumeMotion()
    gluing.ResumeMotion()
    screwing.ResumeMotion()
    testing.ResumeMotion()

    gripper.MoveJoints(0, -60, 60, 0, 0, 0)
    gluing.MoveJoints(0, -60, 60, 0, 0, 0)
    screwing.MoveJoints(-90, 0, 0, 0, 0, 0)
    testing.MoveJoints(0, -60, 60, 0, 0, 0)

    while True:
        # Move Zaber to first position
        zaber.move_absolute(53.5, Units.LENGTH_MILLIMETRES)

        # Gripper robot picks the bottom and place it on the zaber
        gripper.StartProgram(10)
        cpp = gripper.SetCheckpoint(10)
        cpp.wait()

        # Move Zaber to gluing station
        zaber.move_absolute(228, Units.LENGTH_MILLIMETRES)

        # Start the gluing program
        gluing.StartProgram(10)
        cpg = gluing.SetCheckpoint(10)
        cpg.wait()
        gluing.MoveJoints(0, -60, 60, 0, 0, 0)
        cpg = gluing.SetCheckpoint(10)
        cpg.wait()

        # Move zaber back to the first position
        zaber.move_absolute(53.5, Units.LENGTH_MILLIMETRES)

        # Gripper robot picks top and place it on the bottom
        gripper.StartProgram(20)
        cpp = gripper.SetCheckpoint(20)
        cpp.wait()

        # Move to end position
        zaber.move_absolute(400, Units.LENGTH_MILLIMETRES)

        # Screwing robot screws the screws
        screwing.StartProgram(10)
        cps = screwing.SetCheckpoint(10)
        cps.wait()

        # Testing robot test "tests" the electronics
        testing.StartProgram(10)
        cpt = testing.SetCheckpoint(10)
        cpt.wait()

        # Move back the zaber to the first position
        zaber.move_absolute(53.5, Units.LENGTH_MILLIMETRES)

        # Remove the parts from the zaber
        gripper.StartProgram(30)
        gripper.StartProgram(40)
        cpg = gripper.SetCheckpoint(10)
        cpg.wait()
