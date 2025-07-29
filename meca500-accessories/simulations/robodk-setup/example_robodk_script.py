#!/usr/bin/env python3
"""
RoboDK Programming Example for Mecademic Meca500
===============================================

This script demonstrates how to program a Mecademic Meca500 robot using RoboDK API.
It includes examples for basic movements, pick and place operations, and robot control.

Requirements:
- RoboDK installed with Mecademic license
- Python 3.x with robodk package installed
- Meca500 robot model loaded in RoboDK workspace

Installation:
pip install robodk

Author: Generated for Mecademic Robot Integration
Date: 2025
"""

from robodk.robolink import *    # RoboDK API
from robodk.robomath import *    # Robot math toolbox
import time
import sys

# Configuration Constants
ROBOT_NAME = 'Meca500'  # Default robot name in RoboDK
DEFAULT_SPEED = 100     # mm/s for linear movements
DEFAULT_JOINT_SPEED = 15  # deg/s for joint movements
APPROACH_DISTANCE = 50  # mm above target for approach movements

class Meca500Controller:
    """
    Controller class for Mecademic Meca500 robot using RoboDK API
    """
    
    def __init__(self, robot_name=ROBOT_NAME):
        """
        Initialize connection to RoboDK and get robot reference
        
        Args:
            robot_name (str): Name of the robot in RoboDK workspace
        """
        self.RDK = None
        self.robot = None
        self.robot_name = robot_name
        self.connect_to_robodk()
    
    def connect_to_robodk(self):
        """
        Establish connection to RoboDK and get robot reference
        """
        try:
            # Connect to RoboDK
            self.RDK = Robolink()
            
            # Check if RoboDK is running
            if not self.RDK.Valid():
                raise Exception("RoboDK is not running or not accessible")
            
            # Get robot by name
            self.robot = self.RDK.Item(self.robot_name, ITEM_TYPE_ROBOT)
            
            if not self.robot.Valid():
                raise Exception(f"Robot '{self.robot_name}' not found in RoboDK workspace")
            
            print(f"Successfully connected to robot: {self.robot_name}")
            
            # Set default speeds
            self.robot.setSpeed(DEFAULT_SPEED)  # Linear speed in mm/s
            self.robot.setZoneData(5)  # Rounding/blending radius in mm
            
        except Exception as e:
            print(f"Error connecting to RoboDK: {e}")
            sys.exit(1)
    
    def get_robot_status(self):
        """
        Get current robot status and joint positions
        
        Returns:
            dict: Robot status information
        """
        try:
            joints = self.robot.Joints()
            pose = self.robot.Pose()
            
            return {
                'joints': joints.tolist(),
                'pose': pose,
                'position': pose.Pos(),
                'orientation': pose.Euler_2_Pose()[1]
            }
        except Exception as e:
            print(f"Error getting robot status: {e}")
            return None
    
    def move_to_home(self):
        """
        Move robot to home position (all joints at 0 degrees)
        """
        try:
            home_joints = [0, 0, 0, 0, 0, 0]  # All joints at 0 degrees
            print("Moving to home position...")
            self.robot.MoveJ(home_joints)
            print("Home position reached")
        except Exception as e:
            print(f"Error moving to home: {e}")
    
    def move_joints(self, joint_angles):
        """
        Move robot to specified joint angles
        
        Args:
            joint_angles (list): List of 6 joint angles in degrees [J1, J2, J3, J4, J5, J6]
        """
        try:
            if len(joint_angles) != 6:
                raise ValueError("Joint angles must be a list of 6 values")
            
            print(f"Moving to joint angles: {joint_angles}")
            self.robot.MoveJ(joint_angles)
            print("Joint movement completed")
        except Exception as e:
            print(f"Error in joint movement: {e}")
    
    def move_linear(self, target_pose):
        """
        Move robot linearly to target pose
        
        Args:
            target_pose: Target pose (can be Mat object or target item)
        """
        try:
            print("Executing linear movement...")
            self.robot.MoveL(target_pose)
            print("Linear movement completed")
        except Exception as e:
            print(f"Error in linear movement: {e}")
    
    def create_target(self, name, x, y, z, rx=0, ry=0, rz=0):
        """
        Create a target in RoboDK workspace
        
        Args:
            name (str): Name of the target
            x, y, z (float): Position coordinates in mm
            rx, ry, rz (float): Rotation angles in degrees
            
        Returns:
            Target item or None if failed
        """
        try:
            # Create pose matrix
            pose = transl(x, y, z) * rotz(rz * pi/180) * roty(ry * pi/180) * rotx(rx * pi/180)
            
            # Create target in RoboDK
            target = self.RDK.AddTarget(name)
            target.setPose(pose)
            
            print(f"Target '{name}' created at position ({x}, {y}, {z})")
            return target
        except Exception as e:
            print(f"Error creating target: {e}")
            return None
    
    def pick_and_place_demo(self):
        """
        Demonstrate a simple pick and place operation
        """
        try:
            print("\n=== Starting Pick and Place Demo ===")
            
            # Define pick and place positions (adjust as needed)
            pick_pos = [300, 100, 200]      # Pick position [x, y, z] in mm
            place_pos = [300, -100, 200]    # Place position [x, y, z] in mm
            
            # Create targets
            pick_target = self.create_target("Pick_Target", *pick_pos)
            place_target = self.create_target("Place_Target", *place_pos)
            
            if not pick_target or not place_target:
                raise Exception("Failed to create targets")
            
            # 1. Move to home position
            self.move_to_home()
            time.sleep(1)
            
            # 2. Move to pick approach position
            pick_approach = self.create_target("Pick_Approach", 
                                             pick_pos[0], pick_pos[1], pick_pos[2] + APPROACH_DISTANCE)
            self.move_linear(pick_approach)
            time.sleep(0.5)
            
            # 3. Move down to pick position
            self.move_linear(pick_target)
            time.sleep(0.5)
            
            # Simulate gripper close
            print("Closing gripper (simulated)")
            time.sleep(1)
            
            # 4. Move up from pick position
            self.move_linear(pick_approach)
            time.sleep(0.5)
            
            # 5. Move to place approach position
            place_approach = self.create_target("Place_Approach", 
                                              place_pos[0], place_pos[1], place_pos[2] + APPROACH_DISTANCE)
            self.move_linear(place_approach)
            time.sleep(0.5)
            
            # 6. Move down to place position
            self.move_linear(place_target)
            time.sleep(0.5)
            
            # Simulate gripper open
            print("Opening gripper (simulated)")
            time.sleep(1)
            
            # 7. Move up from place position
            self.move_linear(place_approach)
            time.sleep(0.5)
            
            # 8. Return to home
            self.move_to_home()
            
            print("=== Pick and Place Demo Completed ===\n")
            
        except Exception as e:
            print(f"Error in pick and place demo: {e}")
    
    def circular_path_demo(self, center_x=300, center_y=0, center_z=200, radius=50, num_points=8):
        """
        Demonstrate circular path movement
        
        Args:
            center_x, center_y, center_z (float): Center of circle in mm
            radius (float): Radius of circle in mm
            num_points (int): Number of points on circle
        """
        try:
            print(f"\n=== Starting Circular Path Demo ===")
            print(f"Center: ({center_x}, {center_y}, {center_z}), Radius: {radius}mm")
            
            # Create circular path points
            for i in range(num_points + 1):  # +1 to close the circle
                angle = i * 2 * pi / num_points
                
                # Calculate point on circle
                x = center_x + radius * cos(angle)
                y = center_y + radius * sin(angle)
                z = center_z
                
                # Create target
                target_name = f"Circle_Point_{i}"
                target = self.create_target(target_name, x, y, z)
                
                if target:
                    if i == 0:
                        # First point - use joint movement
                        self.robot.MoveJ(target)
                    else:
                        # Subsequent points - use linear movement
                        self.robot.MoveL(target)
                    
                    time.sleep(0.2)  # Brief pause between movements
            
            print("=== Circular Path Demo Completed ===\n")
            
        except Exception as e:
            print(f"Error in circular path demo: {e}")
    
    def speed_test_demo(self):
        """
        Demonstrate different movement speeds
        """
        try:
            print("\n=== Starting Speed Test Demo ===")
            
            # Define test positions
            pos1 = [300, 100, 200]
            pos2 = [300, -100, 200]
            
            # Create targets
            target1 = self.create_target("Speed_Test_1", *pos1)
            target2 = self.create_target("Speed_Test_2", *pos2)
            
            # Test different speeds
            speeds = [50, 100, 200]  # mm/s
            
            for speed in speeds:
                print(f"Testing speed: {speed} mm/s")
                self.robot.setSpeed(speed)
                
                self.move_linear(target1)
                time.sleep(0.5)
                self.move_linear(target2)
                time.sleep(0.5)
            
            # Reset to default speed
            self.robot.setSpeed(DEFAULT_SPEED)
            print("=== Speed Test Demo Completed ===\n")
            
        except Exception as e:
            print(f"Error in speed test demo: {e}")
    
    def run_full_demo(self):
        """
        Run complete demonstration of robot capabilities
        """
        try:
            print("Starting Meca500 RoboDK Programming Demo")
            print("=" * 50)
            
            # Display robot status
            status = self.get_robot_status()
            if status:
                print(f"Current robot position: {[round(x, 2) for x in status['position']]}")
                print(f"Current joint angles: {[round(x, 2) for x in status['joints']]}")
            
            # Run demonstrations
            self.pick_and_place_demo()
            self.circular_path_demo()
            self.speed_test_demo()
            
            # Return to home
            self.move_to_home()
            
            print("All demonstrations completed successfully!")
            
        except Exception as e:
            print(f"Error in full demo: {e}")
    
    def cleanup(self):
        """
        Clean up resources and close connections
        """
        try:
            if self.robot and self.robot.Valid():
                # Return to home position
                self.move_to_home()
            
            print("Cleanup completed")
        except Exception as e:
            print(f"Error during cleanup: {e}")

def main():
    """
    Main function to run the Meca500 programming example
    """
    print("Mecademic Meca500 RoboDK Programming Example")
    print("=" * 50)
    
    # Create controller instance
    controller = Meca500Controller()
    
    try:
        # Run demonstration
        controller.run_full_demo()
    
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    finally:
        # Clean up
        controller.cleanup()
        print("Program finished")

if __name__ == "__main__":
    main()