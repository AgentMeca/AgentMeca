"""
Force Control Examples for ATI Force/Torque Sensors with Meca500

This module provides practical examples of force control applications using
ATI Force/Torque sensors with the Mecademic Meca500 robot. Includes implementations
for polishing, grinding, assembly, and other force-guided operations.

Applications included:
- Force-controlled surface approach
- Constant force polishing/grinding
- Force-limited insertion tasks
- Compliant contact operations

Author: Mecademic Integration Team
Version: 2.0
Updated: 2024
"""

import time
import math
from typing import List, Tuple, Optional
from netft_sensor import NetFTSensor

try:
    from mecademicpy import Robot
    MECADEMIC_AVAILABLE = True
except ImportError:
    print("Warning: mecademicpy not available. Robot control examples will not work.")
    MECADEMIC_AVAILABLE = False


class ForceController:
    """
    Force control system for Meca500 robot with ATI sensors.
    
    Provides high-level force control functions for common applications
    including surface approach, constant force operations, and compliance.
    """
    
    def __init__(self, robot_ip: str, sensor_ip: str):
        """
        Initialize force controller.
        
        Args:
            robot_ip (str): IP address of Meca500 robot
            sensor_ip (str): IP address of ATI sensor
        """
        self.robot_ip = robot_ip
        self.sensor_ip = sensor_ip
        
        # Initialize components
        self.robot = None
        self.sensor = None
        
        # Control parameters
        self.max_velocity = 10.0  # mm/s
        self.force_threshold = 0.5  # N
        self.control_frequency = 50  # Hz
        
        # Safety limits
        self.max_force = 50.0  # N
        self.max_torque = 5.0  # Nm
        
        # Control state
        self.emergency_stop = False
        
    def connect(self) -> bool:
        """
        Connect to robot and sensor.
        
        Returns:
            bool: True if both connections successful
        """
        try:
            # Connect to robot
            if MECADEMIC_AVAILABLE:
                self.robot = Robot()
                self.robot.Connect(self.robot_ip)
                self.robot.ActivateRobot()
                self.robot.Home()
                
                # Set velocity control parameters
                self.robot.SetVelTimeout(0.05)  # 50ms timeout
                print(f"✓ Connected to robot at {self.robot_ip}")
            
            # Connect to sensor
            self.sensor = NetFTSensor(self.sensor_ip)
            if self.sensor.connect():
                self.sensor.start_streaming(1000)
                time.sleep(1)  # Allow stabilization
                self.sensor.set_bias()
                print(f"✓ Connected to sensor at {self.sensor_ip}")
                return True
            else:
                print("✗ Failed to connect to sensor")
                return False
                
        except Exception as e:
            print(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from robot and sensor."""
        if self.sensor:
            self.sensor.disconnect()
        
        if self.robot and MECADEMIC_AVAILABLE:
            self.robot.MoveVelTrf([0, 0, 0, 0, 0, 0])  # Stop movement
            self.robot.DeactivateRobot()
            self.robot.Disconnect()
        
        print("Disconnected from robot and sensor")
    
    def check_safety_limits(self) -> bool:
        """
        Check if current forces are within safety limits.
        
        Returns:
            bool: True if safe, False if limits exceeded
        """
        force_data = self.sensor.get_force()
        
        # Check force limits
        force_magnitude = math.sqrt(sum(f*f for f in force_data[:3]))
        if force_magnitude > self.max_force:
            print(f"Force limit exceeded: {force_magnitude:.2f} N > {self.max_force} N")
            return False
        
        # Check torque limits
        torque_magnitude = math.sqrt(sum(t*t for t in force_data[3:]))
        if torque_magnitude > self.max_torque:
            print(f"Torque limit exceeded: {torque_magnitude:.3f} Nm > {self.max_torque} Nm")
            return False
        
        return True
    
    def emergency_stop_check(self):
        """Emergency stop if safety limits exceeded."""
        if not self.check_safety_limits():
            self.emergency_stop = True
            if self.robot and MECADEMIC_AVAILABLE:
                self.robot.MoveVelTrf([0, 0, 0, 0, 0, 0])
            print("EMERGENCY STOP: Safety limits exceeded!")


class SurfaceApproach(ForceController):
    """
    Force-controlled surface approach operations.
    
    Slowly approach a surface until contact force is detected,
    useful for automated contact operations and surface detection.
    """
    
    def approach_surface_z(self, target_force: float = 5.0, 
                          approach_velocity: float = 2.0,
                          max_distance: float = 50.0) -> bool:
        """
        Approach surface in Z direction until target force is reached.
        
        Args:
            target_force (float): Target contact force in Newtons
            approach_velocity (float): Approach velocity in mm/s
            max_distance (float): Maximum approach distance in mm
            
        Returns:
            bool: True if surface contact achieved, False if failed
        """
        if not (self.robot and self.sensor and MECADEMIC_AVAILABLE):
            print("Robot and sensor must be connected")
            return False
        
        print(f"Starting surface approach: target force = {target_force:.1f} N")
        
        start_time = time.time()
        distance_traveled = 0.0
        
        try:
            while distance_traveled < max_distance and not self.emergency_stop:
                # Get current force
                force_data = self.sensor.get_force()
                current_force = abs(force_data[2])  # Z-axis force
                
                # Check safety limits
                self.emergency_stop_check()
                if self.emergency_stop:
                    break
                
                # Check if target force reached
                if current_force >= target_force:
                    # Stop movement
                    self.robot.MoveVelTrf([0, 0, 0, 0, 0, 0])
                    print(f"✓ Surface contact achieved: {current_force:.2f} N")
                    return True
                
                # Continue approach
                velocity = [0, 0, -approach_velocity, 0, 0, 0]  # Move down
                self.robot.MoveVelTrf(velocity)
                
                # Update distance traveled
                dt = 1.0 / self.control_frequency
                distance_traveled += approach_velocity * dt
                
                # Display progress
                print(f"Force: {current_force:5.2f} N, Distance: {distance_traveled:5.1f} mm", end='\r')
                
                time.sleep(dt)
            
            # Stop movement
            self.robot.MoveVelTrf([0, 0, 0, 0, 0, 0])
            
            if distance_traveled >= max_distance:
                print(f"\n✗ Maximum approach distance reached: {max_distance} mm")
                return False
            
            return False
            
        except Exception as e:
            print(f"\nSurface approach error: {e}")
            if self.robot:
                self.robot.MoveVelTrf([0, 0, 0, 0, 0, 0])
            return False


class ConstantForceControl(ForceController):
    """
    Constant force control for polishing and grinding operations.
    
    Maintains constant contact force while following a trajectory,
    compensating for surface variations and tool wear.
    """
    
    def __init__(self, robot_ip: str, sensor_ip: str):
        super().__init__(robot_ip, sensor_ip)
        
        # PID controller parameters for force control
        self.kp_force = 0.5   # Proportional gain
        self.ki_force = 0.01  # Integral gain  
        self.kd_force = 0.05  # Derivative gain
        
        # PID state variables
        self.force_error_integral = 0.0
        self.previous_force_error = 0.0
    
    def constant_force_polishing(self, target_force: float = 10.0,
                               polishing_trajectory: List[List[float]] = None,
                               lateral_velocity: float = 5.0) -> bool:
        """
        Perform constant force polishing operation.
        
        Args:
            target_force (float): Target polishing force in Newtons
            polishing_trajectory (List): List of [x, y] positions for polishing path
            lateral_velocity (float): Lateral movement velocity in mm/s
            
        Returns:
            bool: True if polishing completed successfully
        """
        if not polishing_trajectory:
            # Default linear polishing path
            polishing_trajectory = [[i, 0] for i in range(0, 100, 5)]
        
        print(f"Starting constant force polishing: target force = {target_force:.1f} N")
        
        try:
            for i, position in enumerate(polishing_trajectory):
                if self.emergency_stop:
                    break
                
                print(f"Polishing point {i+1}/{len(polishing_trajectory)}: ({position[0]:.1f}, {position[1]:.1f})")
                
                # Move to lateral position (maintain Z force control)
                if not self._move_with_force_control(position[0], position[1], 
                                                   target_force, lateral_velocity):
                    print(f"Failed to reach position {position}")
                    return False
                
                # Dwell time for polishing action
                self._maintain_force(target_force, duration=2.0)
            
            print("✓ Polishing operation completed")
            return True
            
        except Exception as e:
            print(f"Polishing error: {e}")
            return False
    
    def _move_with_force_control(self, target_x: float, target_y: float,
                               target_force: float, lateral_velocity: float) -> bool:
        """
        Move to target X,Y position while maintaining Z force.
        
        Args:
            target_x (float): Target X position in mm
            target_y (float): Target Y position in mm  
            target_force (float): Target Z force in Newtons
            lateral_velocity (float): Lateral movement velocity in mm/s
            
        Returns:
            bool: True if position reached successfully
        """
        if not (self.robot and self.sensor and MECADEMIC_AVAILABLE):
            return False
        
        # Get current position
        current_pose = self.robot.GetPose()
        current_x, current_y = current_pose[0], current_pose[1]
        
        # Calculate movement vector
        dx = target_x - current_x
        dy = target_y - current_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < 1.0:  # Already at target
            return True
        
        # Normalize movement direction
        vx = (dx / distance) * lateral_velocity
        vy = (dy / distance) * lateral_velocity
        
        start_time = time.time()
        movement_time = distance / lateral_velocity
        
        while time.time() - start_time < movement_time and not self.emergency_stop:
            # Force control in Z direction
            force_data = self.sensor.get_force()
            current_force = abs(force_data[2])  # Z-axis force
            
            # PID force control
            vz = self._calculate_force_correction(current_force, target_force)
            
            # Apply combined velocity command
            velocity = [vx, vy, vz, 0, 0, 0]
            self.robot.MoveVelTrf(velocity)
            
            # Safety check
            self.emergency_stop_check()
            
            time.sleep(1.0 / self.control_frequency)
        
        # Stop movement
        self.robot.MoveVelTrf([0, 0, 0, 0, 0, 0])
        return True
    
    def _maintain_force(self, target_force: float, duration: float = 2.0):
        """
        Maintain constant force for specified duration.
        
        Args:
            target_force (float): Target force in Newtons
            duration (float): Duration to maintain force in seconds
        """
        start_time = time.time()
        
        while time.time() - start_time < duration and not self.emergency_stop:
            force_data = self.sensor.get_force()
            current_force = abs(force_data[2])
            
            # Force correction
            vz = self._calculate_force_correction(current_force, target_force)
            
            # Apply Z velocity only
            velocity = [0, 0, vz, 0, 0, 0]
            self.robot.MoveVelTrf(velocity)
            
            # Safety check
            self.emergency_stop_check()
            
            time.sleep(1.0 / self.control_frequency)
    
    def _calculate_force_correction(self, current_force: float, target_force: float) -> float:
        """
        Calculate velocity correction using PID control.
        
        Args:
            current_force (float): Current measured force
            target_force (float): Target force setpoint
            
        Returns:
            float: Z velocity correction in mm/s
        """
        # PID control for force
        error = target_force - current_force
        
        # Integral term
        self.force_error_integral += error
        
        # Derivative term
        error_derivative = error - self.previous_force_error
        self.previous_force_error = error
        
        # PID output
        output = (self.kp_force * error + 
                 self.ki_force * self.force_error_integral +
                 self.kd_force * error_derivative)
        
        # Limit output velocity
        max_correction = 5.0  # mm/s
        return max(-max_correction, min(max_correction, output))


class ForceGuidedInsertion(ForceController):
    """
    Force-guided insertion operations for assembly tasks.
    
    Provides compliant insertion with force and torque monitoring
    for peg-in-hole and similar assembly operations.
    """
    
    def compliant_insertion(self, insertion_depth: float = 20.0,
                          max_insertion_force: float = 20.0,
                          max_lateral_force: float = 5.0) -> bool:
        """
        Perform compliant insertion with force monitoring.
        
        Args:
            insertion_depth (float): Target insertion depth in mm
            max_insertion_force (float): Maximum allowable insertion force
            max_lateral_force (float): Maximum allowable lateral force
            
        Returns:
            bool: True if insertion completed successfully
        """
        print(f"Starting compliant insertion: depth = {insertion_depth:.1f} mm")
        
        if not (self.robot and self.sensor and MECADEMIC_AVAILABLE):
            return False
        
        insertion_velocity = 1.0  # mm/s - slow for compliance
        depth_achieved = 0.0
        
        try:
            while depth_achieved < insertion_depth and not self.emergency_stop:
                force_data = self.sensor.get_force()
                
                # Monitor forces
                fz = abs(force_data[2])  # Insertion force
                fx, fy = abs(force_data[0]), abs(force_data[1])  # Lateral forces
                
                # Check force limits
                if fz > max_insertion_force:
                    print(f"Insertion force exceeded: {fz:.2f} N")
                    break
                
                if fx > max_lateral_force or fy > max_lateral_force:
                    print(f"Lateral force exceeded: Fx={fx:.2f}, Fy={fy:.2f} N")
                    # Apply lateral compliance
                    self._apply_lateral_compliance(force_data)
                
                # Continue insertion
                velocity = [0, 0, -insertion_velocity, 0, 0, 0]
                self.robot.MoveVelTrf(velocity)
                
                # Update depth
                depth_achieved += insertion_velocity / self.control_frequency
                
                print(f"Depth: {depth_achieved:5.1f} mm, Force: Fz={fz:5.2f} N", end='\r')
                
                time.sleep(1.0 / self.control_frequency)
            
            # Stop movement
            self.robot.MoveVelTrf([0, 0, 0, 0, 0, 0])
            
            if depth_achieved >= insertion_depth:
                print(f"\n✓ Insertion completed: {depth_achieved:.1f} mm")
                return True
            else:
                print(f"\n✗ Insertion stopped early: {depth_achieved:.1f} mm")
                return False
                
        except Exception as e:
            print(f"\nInsertion error: {e}")
            if self.robot:
                self.robot.MoveVelTrf([0, 0, 0, 0, 0, 0])
            return False
    
    def _apply_lateral_compliance(self, force_data: List[float]):
        """
        Apply lateral compliance based on force feedback.
        
        Args:
            force_data (List[float]): Current force/torque readings
        """
        # Compliance gains
        compliance_gain = 0.1  # mm/s per Newton
        
        # Calculate lateral velocity corrections
        vx = -force_data[0] * compliance_gain  # Opposite to force direction
        vy = -force_data[1] * compliance_gain
        
        # Apply lateral compliance movement
        velocity = [vx, vy, 0, 0, 0, 0]
        self.robot.MoveVelTrf(velocity)
        
        # Brief compliance movement
        time.sleep(0.1)


# Example usage and demonstration functions
def demo_surface_approach():
    """Demonstration of surface approach functionality."""
    robot_ip = "192.168.0.100"
    sensor_ip = "192.168.1.100"
    
    print("=== Surface Approach Demo ===")
    
    approach = SurfaceApproach(robot_ip, sensor_ip)
    
    if approach.connect():
        # Perform surface approach
        success = approach.approach_surface_z(target_force=5.0, 
                                            approach_velocity=2.0)
        
        if success:
            print("Surface approach completed successfully")
        else:
            print("Surface approach failed")
        
        approach.disconnect()
    else:
        print("Failed to connect to robot and sensor")


def demo_constant_force_polishing():
    """Demonstration of constant force polishing."""
    robot_ip = "192.168.0.100"
    sensor_ip = "192.168.1.100"
    
    print("=== Constant Force Polishing Demo ===")
    
    polisher = ConstantForceControl(robot_ip, sensor_ip)
    
    if polisher.connect():
        # Define polishing path
        polishing_path = [
            [0, 0], [10, 0], [20, 0], [30, 0],
            [30, 10], [20, 10], [10, 10], [0, 10]
        ]
        
        # Perform polishing operation
        success = polisher.constant_force_polishing(target_force=8.0,
                                                   polishing_trajectory=polishing_path,
                                                   lateral_velocity=3.0)
        
        if success:
            print("Polishing operation completed successfully")
        else:
            print("Polishing operation failed")
        
        polisher.disconnect()
    else:
        print("Failed to connect to robot and sensor")


def demo_compliant_insertion():
    """Demonstration of compliant insertion."""
    robot_ip = "192.168.0.100"
    sensor_ip = "192.168.1.100"
    
    print("=== Compliant Insertion Demo ===")
    
    inserter = ForceGuidedInsertion(robot_ip, sensor_ip)
    
    if inserter.connect():
        # Perform insertion
        success = inserter.compliant_insertion(insertion_depth=15.0,
                                              max_insertion_force=15.0,
                                              max_lateral_force=3.0)
        
        if success:
            print("Insertion completed successfully")
        else:
            print("Insertion failed")
        
        inserter.disconnect()
    else:
        print("Failed to connect to robot and sensor")


if __name__ == "__main__":
    print("ATI Force Control Examples")
    print("1. Surface Approach Demo")
    print("2. Constant Force Polishing Demo")
    print("3. Compliant Insertion Demo")
    
    choice = input("Select demo (1-3): ")
    
    if choice == "1":
        demo_surface_approach()
    elif choice == "2":
        demo_constant_force_polishing()
    elif choice == "3":
        demo_compliant_insertion()
    else:
        print("Invalid selection")