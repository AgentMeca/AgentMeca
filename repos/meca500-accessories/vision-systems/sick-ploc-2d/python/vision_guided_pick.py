"""
Vision-Guided Pick Integration for SICK PLOC 2D and Mecademic Robots

This module provides a high-level integration class that combines SICK PLOC 2D Vision System
functionality with Mecademic robot control for automated pick and place operations.

Author: Mecademic Integration Team
Version: 1.0
Compatible with: SICK PLOC2D 4.1+, Meca500-R3/R4, Python 3.7+
"""

import time
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
from vision_controller import VisionController

try:
    import mecademic
    MECADEMIC_AVAILABLE = True
except ImportError:
    MECADEMIC_AVAILABLE = False
    print("Warning: Mecademic package not found. Robot functionality will be limited.")


class VisionGuidedPick:
    """
    High-level integration class combining SICK PLOC 2D vision system with Mecademic robot control.
    
    This class provides methods for vision-guided pick and place operations, including calibration,
    coordinate transformation, and automated workflow execution.
    
    Attributes:
        robot_ip (str): IP address of Mecademic robot
        vision_ip (str): IP address of SICK PLOC 2D system
        robot: Mecademic robot instance
        vision (VisionController): Vision system controller
        vision_ref_frame (np.ndarray): Vision reference frame transformation matrix
        pick_offset (float): Z-axis offset for pick operations (mm)
        place_offset (float): Z-axis offset for place operations (mm)
        speed (float): Robot movement speed percentage
        debug (bool): Enable debug output
    """
    
    def __init__(self, robot_ip: str, vision_ip: str, debug: bool = False):
        """
        Initialize VisionGuidedPick integration system.
        
        Args:
            robot_ip (str): IP address of Mecademic robot
            vision_ip (str): IP address of SICK PLOC 2D vision system
            debug (bool): Enable debug output for troubleshooting
        """
        self.robot_ip = robot_ip
        self.vision_ip = vision_ip
        self.debug = debug
        
        # Initialize components
        self.robot = None
        self.vision = VisionController(vision_ip, debug=debug)
        
        # Transformation and offset parameters
        self.vision_ref_frame = np.eye(4)  # 4x4 identity matrix
        self.pick_offset = 5.0  # Default 5mm pick offset
        self.place_offset = 10.0  # Default 10mm place offset
        self.speed = 25.0  # Default 25% speed
        
        # Status flags
        self.robot_initialized = False
        self.vision_initialized = False
        self.calibrated = False
        
        if self.debug:
            print(f"VisionGuidedPick initialized - Robot: {robot_ip}, Vision: {vision_ip}")
    
    def init_robot(self) -> bool:
        """
        Initialize connection to Mecademic robot.
        
        Returns:
            bool: True if robot initialization successful, False otherwise
        """
        if not MECADEMIC_AVAILABLE:
            print("Error: Mecademic package not available")
            return False
        
        try:
            # Initialize robot connection
            self.robot = mecademic.Robot()
            self.robot.Connect(address=self.robot_ip)
            
            # Wait for connection
            timeout = 10.0
            start_time = time.time()
            while not self.robot.GetStatusRobot().Connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            if not self.robot.GetStatusRobot().Connected:
                if self.debug:
                    print(f"Failed to connect to robot at {self.robot_ip}")
                return False
            
            # Activate and home robot
            self.robot.ActivateRobot()
            self.robot.Home()
            
            # Wait for homing to complete
            self.robot.WaitHomed()
            
            # Set default speed
            self.robot.SetCartLinVel(self.speed)
            self.robot.SetCartAngVel(self.speed)
            
            self.robot_initialized = True
            
            if self.debug:
                print("Robot initialized and homed successfully")
            
            return True
            
        except Exception as e:
            if self.debug:
                print(f"Robot initialization error: {e}")
            return False
    
    def init_vision(self) -> bool:
        """
        Initialize connection to SICK PLOC 2D vision system.
        
        Returns:
            bool: True if vision system initialization successful, False otherwise
        """
        try:
            success = self.vision.connect()
            
            if success:
                # Verify system status
                status = self.vision.get_system_status()
                if status['connected']:
                    self.vision_initialized = True
                    
                    if self.debug:
                        print("Vision system initialized successfully")
                    return True
            
            if self.debug:
                print("Failed to initialize vision system")
            return False
            
        except Exception as e:
            if self.debug:
                print(f"Vision initialization error: {e}")
            return False
    
    def set_vision_ref(self, x: float, y: float, z: float, rx: float, ry: float, rz: float) -> None:
        """
        Set vision reference frame coordinates (calibration point).
        
        This method establishes the transformation between vision coordinates and robot coordinates
        using a reference point that is visible to both systems.
        
        Args:
            x, y, z (float): Robot coordinates of reference point (mm)
            rx, ry, rz (float): Robot orientation of reference point (degrees)
        """
        # Store reference frame coordinates
        self.vision_ref_x = x
        self.vision_ref_y = y
        self.vision_ref_z = z
        self.vision_ref_rx = rx
        self.vision_ref_ry = ry
        self.vision_ref_rz = rz
        
        # Create transformation matrix (simplified - full calibration would use multiple points)
        self.vision_ref_frame = self._create_transform_matrix(x, y, z, rx, ry, rz)
        self.calibrated = True
        
        if self.debug:
            print(f"Vision reference frame set: ({x:.2f}, {y:.2f}, {z:.2f}, {rx:.2f}, {ry:.2f}, {rz:.2f})")
    
    def calibrate_3_point(self, robot_points: List[Tuple[float, float, float]], 
                         vision_points: List[Tuple[float, float]]) -> bool:
        """
        Perform 3-point calibration to establish vision-to-robot coordinate transformation.
        
        Args:
            robot_points (List[Tuple[float, float, float]]): Three robot coordinates (x, y, z)
            vision_points (List[Tuple[float, float]]): Corresponding vision coordinates (x, y)
            
        Returns:
            bool: True if calibration successful, False otherwise
        """
        if len(robot_points) != 3 or len(vision_points) != 3:
            if self.debug:
                print("Error: Exactly 3 points required for calibration")
            return False
        
        try:
            # Convert to numpy arrays
            robot_pts = np.array(robot_points)
            vision_pts = np.array(vision_points)
            
            # Calculate transformation matrix using least squares
            # This is a simplified implementation - production systems may use more sophisticated methods
            
            # Add homogeneous coordinates
            vision_homo = np.column_stack([vision_pts, np.ones(3)])
            
            # Solve for transformation parameters
            transform_x = np.linalg.lstsq(vision_homo, robot_pts[:, 0], rcond=None)[0]
            transform_y = np.linalg.lstsq(vision_homo, robot_pts[:, 1], rcond=None)[0]
            
            # Create transformation matrix
            self.vision_to_robot_transform = np.array([
                [transform_x[0], transform_x[1], transform_x[2]],
                [transform_y[0], transform_y[1], transform_y[2]]
            ])
            
            # Use average Z coordinate for all transformations
            self.average_z = np.mean(robot_pts[:, 2])
            
            self.calibrated = True
            
            if self.debug:
                print("3-point calibration completed successfully")
                print(f"Transformation matrix:\n{self.vision_to_robot_transform}")
            
            return True
            
        except Exception as e:
            if self.debug:
                print(f"Calibration error: {e}")
            return False
    
    def set_offset(self, pick_offset: float, place_offset: Optional[float] = None) -> None:
        """
        Set Z-axis offsets for pick and place operations.
        
        Args:
            pick_offset (float): Pick height offset in mm (positive = above part)
            place_offset (Optional[float]): Place height offset in mm (uses pick_offset if None)
        """
        self.pick_offset = pick_offset
        self.place_offset = place_offset if place_offset is not None else pick_offset
        
        if self.debug:
            print(f"Offsets set - Pick: {self.pick_offset}mm, Place: {self.place_offset}mm")
    
    def set_speed(self, speed: float) -> None:
        """
        Set robot movement speed.
        
        Args:
            speed (float): Speed percentage (1-100)
        """
        self.speed = max(1.0, min(100.0, speed))  # Clamp to 1-100%
        
        if self.robot_initialized and self.robot:
            self.robot.SetCartLinVel(self.speed)
            self.robot.SetCartAngVel(self.speed)
        
        if self.debug:
            print(f"Speed set to {self.speed}%")
    
    def get_count(self, job_id: int) -> Optional[int]:
        """
        Get number of parts detected by vision system.
        
        Args:
            job_id (int): Vision job ID to query
            
        Returns:
            Optional[int]: Number of detected parts, None if query failed
        """
        if not self.vision_initialized:
            if self.debug:
                print("Vision system not initialized")
            return None
        
        return self.vision.get_part_count(job_id)
    
    def pick_index(self, job_id: int, part_index: int) -> bool:
        """
        Pick part at specified index using vision guidance.
        
        Args:
            job_id (int): Vision job ID
            part_index (int): Index of part to pick (1-based)
            
        Returns:
            bool: True if pick operation successful, False otherwise
        """
        if not self._check_system_ready():
            return False
        
        try:
            # Get part coordinates from vision system
            part_data = self.vision.locate_by_index(job_id, part_index)
            if not part_data:
                if self.debug:
                    print(f"Failed to get coordinates for part {part_index}")
                return False
            
            # Transform vision coordinates to robot coordinates
            robot_coords = self._transform_vision_to_robot(part_data['x'], part_data['y'])
            if not robot_coords:
                if self.debug:
                    print("Coordinate transformation failed")
                return False
            
            target_x, target_y, target_z = robot_coords
            target_rz = part_data.get('rz', 0.0)  # Use vision rotation or default to 0
            
            if self.debug:
                print(f"Picking part {part_index} at ({target_x:.2f}, {target_y:.2f}, {target_z:.2f}, rz={target_rz:.2f})")
            
            # Execute pick sequence
            return self._execute_pick(target_x, target_y, target_z, 0, 0, target_rz)
            
        except Exception as e:
            if self.debug:
                print(f"Pick operation error: {e}")
            return False
    
    def place(self, x: float, y: float, z: float, rx: float, ry: float, rz: float) -> bool:
        """
        Place part at specified coordinates.
        
        Args:
            x, y, z (float): Target coordinates (mm)
            rx, ry, rz (float): Target orientation (degrees)
            
        Returns:
            bool: True if place operation successful, False otherwise
        """
        if not self.robot_initialized:
            if self.debug:
                print("Robot not initialized")
            return False
        
        try:
            if self.debug:
                print(f"Placing part at ({x:.2f}, {y:.2f}, {z:.2f}, {rx:.2f}, {ry:.2f}, {rz:.2f})")
            
            # Execute place sequence
            return self._execute_place(x, y, z, rx, ry, rz)
            
        except Exception as e:
            if self.debug:
                print(f"Place operation error: {e}")
            return False
    
    def _check_system_ready(self) -> bool:
        """
        Check if both robot and vision systems are ready for operation.
        
        Returns:
            bool: True if systems are ready, False otherwise
        """
        if not self.robot_initialized:
            if self.debug:
                print("Robot not initialized")
            return False
        
        if not self.vision_initialized:
            if self.debug:
                print("Vision system not initialized")
            return False
        
        if not self.calibrated:
            if self.debug:
                print("System not calibrated")
            return False
        
        return True
    
    def _transform_vision_to_robot(self, vision_x: float, vision_y: float) -> Optional[Tuple[float, float, float]]:
        """
        Transform vision coordinates to robot coordinates.
        
        Args:
            vision_x, vision_y (float): Vision system coordinates
            
        Returns:
            Optional[Tuple[float, float, float]]: Robot coordinates (x, y, z), None if failed
        """
        try:
            if hasattr(self, 'vision_to_robot_transform'):
                # Use 3-point calibration transformation
                vision_homo = np.array([vision_x, vision_y, 1.0])
                robot_x = np.dot(self.vision_to_robot_transform[0], vision_homo)
                robot_y = np.dot(self.vision_to_robot_transform[1], vision_homo)
                robot_z = self.average_z
                
            else:
                # Use simple reference frame transformation (less accurate)
                # This is a simplified transformation - production systems should use proper calibration
                robot_x = self.vision_ref_x + (vision_x * 0.1)  # Scale factor example
                robot_y = self.vision_ref_y + (vision_y * 0.1)
                robot_z = self.vision_ref_z
            
            return (robot_x, robot_y, robot_z)
            
        except Exception as e:
            if self.debug:
                print(f"Coordinate transformation error: {e}")
            return None
    
    def _execute_pick(self, x: float, y: float, z: float, rx: float, ry: float, rz: float) -> bool:
        """
        Execute pick sequence at specified coordinates.
        
        Args:
            x, y, z (float): Target coordinates (mm)
            rx, ry, rz (float): Target orientation (degrees)
            
        Returns:
            bool: True if pick successful, False otherwise
        """
        try:
            # Move to approach position (offset above part)
            approach_z = z + self.pick_offset
            self.robot.MoveCartPoint(x, y, approach_z, rx, ry, rz)
            self.robot.WaitMovementCompletion()
            
            # Move down to pick position
            self.robot.MoveCartPoint(x, y, z, rx, ry, rz)
            self.robot.WaitMovementCompletion()
            
            # Activate gripper (implementation depends on gripper type)
            # This is a placeholder - actual implementation would control specific gripper
            if self.debug:
                print("Gripper activated (placeholder)")
            
            # Small delay for gripper activation
            time.sleep(0.5)
            
            # Move back to approach position
            self.robot.MoveCartPoint(x, y, approach_z, rx, ry, rz)
            self.robot.WaitMovementCompletion()
            
            if self.debug:
                print("Pick sequence completed")
            
            return True
            
        except Exception as e:
            if self.debug:
                print(f"Pick execution error: {e}")
            return False
    
    def _execute_place(self, x: float, y: float, z: float, rx: float, ry: float, rz: float) -> bool:
        """
        Execute place sequence at specified coordinates.
        
        Args:
            x, y, z (float): Target coordinates (mm)
            rx, ry, rz (float): Target orientation (degrees)
            
        Returns:
            bool: True if place successful, False otherwise
        """
        try:
            # Move to approach position (offset above target)
            approach_z = z + self.place_offset
            self.robot.MoveCartPoint(x, y, approach_z, rx, ry, rz)
            self.robot.WaitMovementCompletion()
            
            # Move down to place position
            self.robot.MoveCartPoint(x, y, z, rx, ry, rz)
            self.robot.WaitMovementCompletion()
            
            # Deactivate gripper (implementation depends on gripper type)
            # This is a placeholder - actual implementation would control specific gripper
            if self.debug:
                print("Gripper deactivated (placeholder)")
            
            # Small delay for gripper deactivation
            time.sleep(0.5)
            
            # Move back to approach position
            self.robot.MoveCartPoint(x, y, approach_z, rx, ry, rz)
            self.robot.WaitMovementCompletion()
            
            if self.debug:
                print("Place sequence completed")
            
            return True
            
        except Exception as e:
            if self.debug:
                print(f"Place execution error: {e}")
            return False
    
    def _create_transform_matrix(self, x: float, y: float, z: float, rx: float, ry: float, rz: float) -> np.ndarray:
        """
        Create 4x4 transformation matrix from position and orientation.
        
        Args:
            x, y, z (float): Position coordinates
            rx, ry, rz (float): Rotation angles in degrees
            
        Returns:
            np.ndarray: 4x4 transformation matrix
        """
        # Convert angles to radians
        rx_rad = np.radians(rx)
        ry_rad = np.radians(ry)
        rz_rad = np.radians(rz)
        
        # Create rotation matrices
        Rx = np.array([[1, 0, 0],
                       [0, np.cos(rx_rad), -np.sin(rx_rad)],
                       [0, np.sin(rx_rad), np.cos(rx_rad)]])
        
        Ry = np.array([[np.cos(ry_rad), 0, np.sin(ry_rad)],
                       [0, 1, 0],
                       [-np.sin(ry_rad), 0, np.cos(ry_rad)]])
        
        Rz = np.array([[np.cos(rz_rad), -np.sin(rz_rad), 0],
                       [np.sin(rz_rad), np.cos(rz_rad), 0],
                       [0, 0, 1]])
        
        # Combined rotation matrix
        R = Rz @ Ry @ Rx
        
        # Create 4x4 transformation matrix
        T = np.eye(4)
        T[0:3, 0:3] = R
        T[0:3, 3] = [x, y, z]
        
        return T
    
    def shutdown(self) -> None:
        """
        Safely shutdown robot and vision systems.
        """
        try:
            if self.robot_initialized and self.robot:
                self.robot.DeactivateRobot()
                self.robot.Disconnect()
                if self.debug:
                    print("Robot disconnected")
            
            if self.vision_initialized:
                self.vision.disconnect()
                if self.debug:
                    print("Vision system disconnected")
                    
        except Exception as e:
            if self.debug:
                print(f"Shutdown error: {e}")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown()


# Example usage function
def example_pick_and_place():
    """
    Example demonstrating vision-guided pick and place workflow.
    """
    robot_ip = "192.168.0.100"
    vision_ip = "192.168.0.1"
    
    print("Starting vision-guided pick and place example")
    
    with VisionGuidedPick(robot_ip, vision_ip, debug=True) as app:
        # Initialize systems
        if not app.init_robot():
            print("Failed to initialize robot")
            return
        
        if not app.init_vision():
            print("Failed to initialize vision system")
            return
        
        # Set calibration (example coordinates)
        app.set_vision_ref(100, 50, 25, 0, 0, 0)
        
        # Configure operation parameters
        app.set_offset(5.0)  # 5mm pick offset
        app.set_speed(25.0)  # 25% speed
        
        # Execute pick and place workflow
        job_id = 1
        count = app.get_count(job_id)
        
        if count and count > 0:
            print(f"Found {count} parts to process")
            
            for i in range(1, count + 1):
                print(f"Processing part {i}/{count}")
                
                # Pick part
                if app.pick_index(job_id, i):
                    # Place part at target location
                    target_coords = (-120, 100, 0, 180, 0, 180)
                    if app.place(*target_coords):
                        print(f"Part {i} completed successfully")
                    else:
                        print(f"Failed to place part {i}")
                else:
                    print(f"Failed to pick part {i}")
        else:
            print("No parts detected")
    
    print("Example completed")


if __name__ == "__main__":
    # Run example if script is executed directly
    example_pick_and_place()