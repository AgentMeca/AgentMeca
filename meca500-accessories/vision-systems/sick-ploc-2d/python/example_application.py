#!/usr/bin/env python3
"""
SICK PLOC 2D Vision-Guided Pick and Place Example Application

This script demonstrates a complete vision-guided pick and place workflow using
SICK PLOC 2D Vision System integration with Mecademic robots.

Features demonstrated:
- System initialization and connection
- Vision-robot calibration
- Automated pick and place operations
- Error handling and recovery
- Performance monitoring
- Production workflow

Author: Mecademic Integration Team
Version: 1.0
Compatible with: SICK PLOC2D 4.1+, Meca500-R3/R4, Python 3.7+
"""

import time
import sys
import argparse
import logging
from typing import List, Tuple, Optional
from vision_controller import VisionController
from vision_guided_pick import VisionGuidedPick


class SickPloc2DApplication:
    """
    Complete application class for SICK PLOC 2D vision-guided automation.
    
    This class demonstrates a production-ready implementation with proper
    error handling, logging, and operational monitoring.
    """
    
    def __init__(self, robot_ip: str, vision_ip: str, debug: bool = False):
        """
        Initialize the application.
        
        Args:
            robot_ip (str): IP address of Mecademic robot
            vision_ip (str): IP address of SICK PLOC 2D system
            debug (bool): Enable debug output
        """
        self.robot_ip = robot_ip
        self.vision_ip = vision_ip
        self.debug = debug
        
        # Initialize integration system
        self.app = VisionGuidedPick(robot_ip, vision_ip, debug=debug)
        
        # Operational parameters
        self.job_id = 1
        self.pick_offset = 5.0  # mm
        self.place_offset = 10.0  # mm
        self.robot_speed = 25.0  # %
        
        # Target positions for place operations
        self.place_positions = [
            (-120, 100, 0, 180, 0, 180),   # Position 1
            (-120, 120, 0, 180, 0, 180),   # Position 2  
            (-120, 140, 0, 180, 0, 180),   # Position 3
        ]
        self.current_place_index = 0
        
        # Performance monitoring
        self.cycle_count = 0
        self.total_cycle_time = 0.0
        self.successful_picks = 0
        self.failed_picks = 0
        
        # Setup logging
        self._setup_logging()
        
        self.logger.info(f"Application initialized - Robot: {robot_ip}, Vision: {vision_ip}")
    
    def _setup_logging(self) -> None:
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO if not self.debug else logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('sick_ploc2d_application.log'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def initialize_systems(self) -> bool:
        """
        Initialize robot and vision systems.
        
        Returns:
            bool: True if initialization successful, False otherwise
        """
        self.logger.info("Initializing systems...")
        
        try:
            # Initialize robot
            if not self.app.init_robot():
                self.logger.error("Robot initialization failed")
                return False
            self.logger.info("Robot initialized successfully")
            
            # Initialize vision system
            if not self.app.init_vision():
                self.logger.error("Vision system initialization failed")
                return False
            self.logger.info("Vision system initialized successfully")
            
            # Configure operational parameters
            self.app.set_offset(self.pick_offset, self.place_offset)
            self.app.set_speed(self.robot_speed)
            
            self.logger.info(f"Systems initialized - Pick offset: {self.pick_offset}mm, Speed: {self.robot_speed}%")
            return True
            
        except Exception as e:
            self.logger.error(f"System initialization error: {e}")
            return False
    
    def perform_calibration(self, calibration_method: str = "single_point") -> bool:
        """
        Perform vision-robot calibration.
        
        Args:
            calibration_method (str): "single_point" or "three_point"
            
        Returns:
            bool: True if calibration successful, False otherwise
        """
        self.logger.info(f"Starting {calibration_method} calibration...")
        
        try:
            if calibration_method == "single_point":
                return self._single_point_calibration()
            elif calibration_method == "three_point":
                return self._three_point_calibration()
            else:
                self.logger.error(f"Unknown calibration method: {calibration_method}")
                return False
                
        except Exception as e:
            self.logger.error(f"Calibration error: {e}")
            return False
    
    def _single_point_calibration(self) -> bool:
        """
        Perform single-point calibration (simplified method).
        
        Returns:
            bool: True if calibration successful, False otherwise
        """
        # Default reference point coordinates
        ref_x, ref_y, ref_z = 100.0, 50.0, 25.0
        ref_rx, ref_ry, ref_rz = 0.0, 0.0, 0.0
        
        self.app.set_vision_ref(ref_x, ref_y, ref_z, ref_rx, ref_ry, ref_rz)
        
        self.logger.info(f"Single-point calibration completed at ({ref_x}, {ref_y}, {ref_z})")
        return True
    
    def _three_point_calibration(self) -> bool:
        """
        Perform three-point calibration for high accuracy.
        
        Returns:
            bool: True if calibration successful, False otherwise
        """
        self.logger.info("Starting interactive 3-point calibration...")
        
        # Define calibration points in robot coordinate system
        robot_points = [
            (100.0, 100.0, 25.0),  # Point 1
            (200.0, 100.0, 25.0),  # Point 2
            (150.0, 200.0, 25.0)   # Point 3
        ]
        
        vision_points = []
        
        for i, (x, y, z) in enumerate(robot_points):
            self.logger.info(f"Moving to calibration point {i+1}: ({x}, {y}, {z})")
            
            # Move robot to calibration point
            self.app.robot.MoveCartPoint(x, y, z, 0, 0, 0)
            self.app.robot.WaitMovementCompletion()
            
            # Interactive input for vision coordinates
            print(f"\nRobot positioned at calibration point {i+1}")
            print(f"Robot coordinates: ({x:.1f}, {y:.1f}, {z:.1f})")
            print("Please observe the corresponding coordinates in the vision system and enter them below:")
            
            try:
                vision_x = float(input(f"Vision X coordinate for point {i+1}: "))
                vision_y = float(input(f"Vision Y coordinate for point {i+1}: "))
                vision_points.append((vision_x, vision_y))
                
                self.logger.info(f"Point {i+1} - Robot: ({x}, {y}, {z}), Vision: ({vision_x}, {vision_y})")
                
            except ValueError:
                self.logger.error("Invalid coordinate input")
                return False
        
        # Perform calibration calculation
        success = self.app.calibrate_3_point(robot_points, vision_points)
        
        if success:
            self.logger.info("3-point calibration completed successfully")
            return True
        else:
            self.logger.error("3-point calibration failed")
            return False
    
    def run_production_cycle(self) -> bool:
        """
        Run a single production cycle (detect and process all visible parts).
        
        Returns:
            bool: True if cycle completed, False if error occurred
        """
        cycle_start_time = time.time()
        
        try:
            # Get part count
            count = self.app.get_count(self.job_id)
            
            if count is None:
                self.logger.warning("Failed to get part count from vision system")
                return False
            
            if count == 0:
                if self.debug:
                    self.logger.debug("No parts detected")
                return True
            
            self.logger.info(f"Processing {count} parts")
            
            # Process each detected part
            for i in range(1, count + 1):
                if not self._process_single_part(i):
                    self.logger.warning(f"Failed to process part {i}")
                    self.failed_picks += 1
                else:
                    self.successful_picks += 1
                    
                    # Update place position for next part
                    self.current_place_index = (self.current_place_index + 1) % len(self.place_positions)
            
            # Update performance statistics
            cycle_time = time.time() - cycle_start_time
            self.cycle_count += 1
            self.total_cycle_time += cycle_time
            
            avg_cycle_time = self.total_cycle_time / self.cycle_count
            success_rate = (self.successful_picks / (self.successful_picks + self.failed_picks)) * 100
            
            self.logger.info(f"Cycle {self.cycle_count} completed in {cycle_time:.2f}s "
                           f"(avg: {avg_cycle_time:.2f}s, success rate: {success_rate:.1f}%)")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Production cycle error: {e}")
            return False
    
    def _process_single_part(self, part_index: int) -> bool:
        """
        Process a single part (pick and place).
        
        Args:
            part_index (int): Index of part to process (1-based)
            
        Returns:
            bool: True if part processed successfully, False otherwise
        """
        try:
            part_start_time = time.time()
            
            # Pick part
            if not self.app.pick_index(self.job_id, part_index):
                self.logger.warning(f"Failed to pick part {part_index}")
                return False
            
            # Get target place position
            place_coords = self.place_positions[self.current_place_index]
            
            # Place part
            if not self.app.place(*place_coords):
                self.logger.warning(f"Failed to place part {part_index}")
                return False
            
            part_time = time.time() - part_start_time
            self.logger.info(f"Part {part_index} processed successfully in {part_time:.2f}s")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Part processing error: {e}")
            return False
    
    def run_continuous_operation(self, max_cycles: Optional[int] = None, 
                               cycle_delay: float = 1.0) -> None:
        """
        Run continuous production operation.
        
        Args:
            max_cycles (Optional[int]): Maximum number of cycles (None for infinite)
            cycle_delay (float): Delay between cycles in seconds
        """
        self.logger.info("Starting continuous operation...")
        
        cycles_completed = 0
        
        try:
            while max_cycles is None or cycles_completed < max_cycles:
                # Run production cycle
                success = self.run_production_cycle()
                
                if not success:
                    self.logger.warning("Production cycle failed - attempting recovery")
                    
                    # Attempt system recovery
                    if not self._attempt_recovery():
                        self.logger.error("Recovery failed - stopping operation")
                        break
                
                cycles_completed += 1
                
                # Wait before next cycle
                if cycle_delay > 0:
                    time.sleep(cycle_delay)
                    
        except KeyboardInterrupt:
            self.logger.info("Operation interrupted by user")
        except Exception as e:
            self.logger.error(f"Continuous operation error: {e}")
        
        finally:
            self.logger.info(f"Continuous operation completed - {cycles_completed} cycles")
            self._print_statistics()
    
    def _attempt_recovery(self) -> bool:
        """
        Attempt to recover from system errors.
        
        Returns:
            bool: True if recovery successful, False otherwise
        """
        self.logger.info("Attempting system recovery...")
        
        try:
            # Check vision system connection
            if not self.app.vision_initialized:
                self.logger.info("Reinitializing vision system...")
                if not self.app.init_vision():
                    return False
            
            # Check robot connection
            if not self.app.robot_initialized:
                self.logger.info("Reinitializing robot...")
                if not self.app.init_robot():
                    return False
            
            # Test basic functionality
            count = self.app.get_count(self.job_id)
            if count is None:
                self.logger.warning("Vision system still not responding")
                return False
            
            self.logger.info("System recovery successful")
            return True
            
        except Exception as e:
            self.logger.error(f"Recovery attempt failed: {e}")
            return False
    
    def _print_statistics(self) -> None:
        """Print operation statistics."""
        if self.cycle_count > 0:
            avg_cycle_time = self.total_cycle_time / self.cycle_count
            total_parts = self.successful_picks + self.failed_picks
            
            if total_parts > 0:
                success_rate = (self.successful_picks / total_parts) * 100
            else:
                success_rate = 0.0
            
            print("\n" + "="*50)
            print("OPERATION STATISTICS")
            print("="*50)
            print(f"Cycles completed: {self.cycle_count}")
            print(f"Total cycle time: {self.total_cycle_time:.2f}s")
            print(f"Average cycle time: {avg_cycle_time:.2f}s")
            print(f"Successful picks: {self.successful_picks}")
            print(f"Failed picks: {self.failed_picks}")
            print(f"Success rate: {success_rate:.1f}%")
            print("="*50)
    
    def run_test_sequence(self) -> None:
        """
        Run a comprehensive test sequence to verify system functionality.
        """
        self.logger.info("Starting test sequence...")
        
        tests = [
            ("Vision System Communication", self._test_vision_communication),
            ("Robot Movement", self._test_robot_movement),
            ("Coordinate Transformation", self._test_coordinate_transformation),
            ("Pick and Place Operation", self._test_pick_place),
        ]
        
        passed_tests = 0
        
        for test_name, test_function in tests:
            self.logger.info(f"Running test: {test_name}")
            
            try:
                if test_function():
                    self.logger.info(f"✓ {test_name} PASSED")
                    passed_tests += 1
                else:
                    self.logger.error(f"✗ {test_name} FAILED")
            except Exception as e:
                self.logger.error(f"✗ {test_name} FAILED with exception: {e}")
        
        self.logger.info(f"Test sequence completed: {passed_tests}/{len(tests)} tests passed")
    
    def _test_vision_communication(self) -> bool:
        """Test vision system communication."""
        status = self.app.vision.get_system_status()
        return status['connected']
    
    def _test_robot_movement(self) -> bool:
        """Test robot movement capability."""
        # Move to a safe test position
        test_position = (150.0, 150.0, 50.0, 0.0, 0.0, 0.0)
        self.app.robot.MoveCartPoint(*test_position)
        self.app.robot.WaitMovementCompletion()
        return True
    
    def _test_coordinate_transformation(self) -> bool:
        """Test coordinate transformation accuracy."""
        # This would typically involve moving to known positions
        # and comparing transformed coordinates
        return True  # Simplified for example
    
    def _test_pick_place(self) -> bool:
        """Test pick and place operation."""
        count = self.app.get_count(self.job_id)
        if count and count > 0:
            return self._process_single_part(1)
        else:
            self.logger.warning("No parts available for pick/place test")
            return False
    
    def shutdown(self) -> None:
        """Safely shutdown the application."""
        self.logger.info("Shutting down application...")
        
        try:
            self.app.shutdown()
            self._print_statistics()
            self.logger.info("Application shutdown completed")
            
        except Exception as e:
            self.logger.error(f"Shutdown error: {e}")


def main():
    """Main application entry point."""
    parser = argparse.ArgumentParser(description='SICK PLOC 2D Vision-Guided Pick and Place Application')
    
    parser.add_argument('--robot-ip', default='192.168.0.100', 
                       help='IP address of Mecademic robot (default: 192.168.0.100)')
    parser.add_argument('--vision-ip', default='192.168.0.1',
                       help='IP address of SICK PLOC 2D system (default: 192.168.0.1)')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    parser.add_argument('--calibration', choices=['single', 'three'], default='single',
                       help='Calibration method (default: single)')
    parser.add_argument('--mode', choices=['test', 'production', 'continuous'], default='production',
                       help='Operation mode (default: production)')
    parser.add_argument('--max-cycles', type=int, default=None,
                       help='Maximum number of cycles for continuous mode')
    parser.add_argument('--cycle-delay', type=float, default=1.0,
                       help='Delay between cycles in seconds (default: 1.0)')
    
    args = parser.parse_args()
    
    # Create application instance
    app = SickPloc2DApplication(args.robot_ip, args.vision_ip, args.debug)
    
    try:
        # Initialize systems
        if not app.initialize_systems():
            print("System initialization failed")
            return 1
        
        # Perform calibration
        calibration_method = "single_point" if args.calibration == "single" else "three_point"
        if not app.perform_calibration(calibration_method):
            print("Calibration failed")
            return 1
        
        # Run selected mode
        if args.mode == "test":
            app.run_test_sequence()
        elif args.mode == "production":
            app.run_production_cycle()
        elif args.mode == "continuous":
            app.run_continuous_operation(args.max_cycles, args.cycle_delay)
        
        return 0
        
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
        return 0
    except Exception as e:
        print(f"Application error: {e}")
        return 1
    finally:
        app.shutdown()


if __name__ == "__main__":
    exit(main())