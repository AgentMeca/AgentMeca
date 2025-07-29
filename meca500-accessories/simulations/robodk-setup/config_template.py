#!/usr/bin/env python3
"""
RoboDK Configuration Template for Mecademic Meca500
==================================================

This file contains configuration parameters for RoboDK programming with Meca500.
Copy this file to 'config.py' and modify the values according to your setup.

Usage:
1. Copy this file: cp config_template.py config.py
2. Edit config.py with your specific settings
3. Import in your scripts: from config import *

Author: Generated for Mecademic Robot Integration
"""

# =============================================================================
# ROBOT CONFIGURATION
# =============================================================================

# Robot identification
ROBOT_NAME = "Meca500"              # Name of robot in RoboDK workspace
ROBOT_MODEL = "Meca500-R3"          # Specific robot model
ROBOT_IP = "192.168.0.100"          # Default Meca500 IP address

# =============================================================================
# MOVEMENT PARAMETERS
# =============================================================================

# Speed settings (adjust based on application requirements)
DEFAULT_LINEAR_SPEED = 100          # mm/s - Linear movement speed
DEFAULT_JOINT_SPEED = 15            # deg/s - Joint movement speed
DEFAULT_ACCELERATION = 50           # % - Acceleration as percentage of maximum

# Movement precision
ZONE_DATA = 5                       # mm - Rounding/blending radius
APPROACH_DISTANCE = 50              # mm - Distance for approach movements
RETRACT_DISTANCE = 50               # mm - Distance for retract movements

# Safety limits
MAX_LINEAR_SPEED = 500              # mm/s - Maximum allowed linear speed
MAX_JOINT_SPEED = 30                # deg/s - Maximum allowed joint speed
MIN_APPROACH_HEIGHT = 10            # mm - Minimum approach height above target

# =============================================================================
# WORKSPACE LIMITS
# =============================================================================

# Workspace boundaries (in mm, relative to robot base)
WORKSPACE_LIMITS = {
    'x_min': -260,      # Minimum X coordinate
    'x_max': 260,       # Maximum X coordinate
    'y_min': -260,      # Minimum Y coordinate  
    'y_max': 260,       # Maximum Y coordinate
    'z_min': -110,      # Minimum Z coordinate
    'z_max': 360        # Maximum Z coordinate
}

# Safe zones (areas where robot should operate)
SAFE_ZONES = {
    'pick_zone': {
        'x_range': [200, 350],
        'y_range': [50, 200],
        'z_range': [100, 300]
    },
    'place_zone': {
        'x_range': [200, 350],
        'y_range': [-200, -50],
        'z_range': [100, 300]
    }
}

# =============================================================================
# TOOL CONFIGURATION
# =============================================================================

# Tool Center Point (TCP) definition
TCP_OFFSET = {
    'x': 0.0,           # mm - X offset from flange
    'y': 0.0,           # mm - Y offset from flange  
    'z': 100.0,         # mm - Z offset from flange (tool length)
    'rx': 0.0,          # deg - Rotation about X axis
    'ry': 0.0,          # deg - Rotation about Y axis
    'rz': 0.0           # deg - Rotation about Z axis
}

# Gripper configuration (if applicable)
GRIPPER_CONFIG = {
    'type': 'MEGP25',           # Gripper model
    'close_signal': 'DO1',      # Digital output for close command
    'open_signal': 'DO2',       # Digital output for open command
    'grip_force': 20,           # % - Gripping force percentage
    'grip_timeout': 2.0         # seconds - Timeout for grip operations
}

# =============================================================================
# REFERENCE FRAMES
# =============================================================================

# Base reference frame (world coordinates)
BASE_FRAME = {
    'name': 'World',
    'x': 0.0,
    'y': 0.0, 
    'z': 0.0,
    'rx': 0.0,
    'ry': 0.0,
    'rz': 0.0
}

# Work object frames (define coordinate systems for different work areas)
WORK_FRAMES = {
    'table_frame': {
        'name': 'Table',
        'x': 300.0,         # mm - Table center X
        'y': 0.0,           # mm - Table center Y
        'z': 0.0,           # mm - Table height
        'rx': 0.0,          # deg - Table rotation X
        'ry': 0.0,          # deg - Table rotation Y
        'rz': 0.0           # deg - Table rotation Z
    },
    'conveyor_frame': {
        'name': 'Conveyor',
        'x': 400.0,         # mm - Conveyor position X
        'y': -200.0,        # mm - Conveyor position Y
        'z': 50.0,          # mm - Conveyor height
        'rx': 0.0,          # deg - Conveyor rotation X
        'ry': 0.0,          # deg - Conveyor rotation Y
        'rz': 0.0           # deg - Conveyor rotation Z
    }
}

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================

# Pick and place application
PICK_PLACE_CONFIG = {
    'pick_positions': [
        {'x': 300, 'y': 100, 'z': 200, 'rx': 0, 'ry': 0, 'rz': 0},
        {'x': 350, 'y': 100, 'z': 200, 'rx': 0, 'ry': 0, 'rz': 0}
    ],
    'place_positions': [
        {'x': 300, 'y': -100, 'z': 200, 'rx': 0, 'ry': 0, 'rz': 0},
        {'x': 350, 'y': -100, 'z': 200, 'rx': 0, 'ry': 0, 'rz': 0}
    ],
    'cycle_time_target': 10.0,  # seconds - Target cycle time
    'safety_pause': 0.5         # seconds - Pause between operations
}

# Path planning settings
PATH_CONFIG = {
    'smoothing': True,              # Enable path smoothing
    'collision_check': True,        # Enable collision detection
    'optimize_speed': True,         # Optimize for speed
    'max_deviation': 1.0,          # mm - Maximum path deviation
    'corner_radius': 5.0           # mm - Corner rounding radius
}

# =============================================================================
# COMMUNICATION SETTINGS
# =============================================================================

# RoboDK connection settings
ROBODK_CONFIG = {
    'host': 'localhost',            # RoboDK host address
    'port': 20500,                  # Default RoboDK port
    'timeout': 10.0,                # seconds - Connection timeout
    'auto_update': True,            # Enable automatic updates
    'simulation_speed': 1.0         # Simulation speed multiplier
}

# Robot connection settings (for online programming)
ROBOT_CONNECTION = {
    'ip_address': ROBOT_IP,
    'port': 10000,                  # Default Mecademic port
    'timeout': 5.0,                 # seconds - Communication timeout
    'retry_count': 3,               # Number of connection retries
    'enable_online': False          # Enable online programming by default
}

# =============================================================================
# LOGGING AND DEBUGGING
# =============================================================================

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',                # DEBUG, INFO, WARNING, ERROR
    'file': 'robodk_meca500.log',   # Log file name
    'console': True,                # Enable console logging
    'max_size': 10,                 # MB - Maximum log file size
    'backup_count': 5               # Number of backup log files
}

# Debug settings
DEBUG_CONFIG = {
    'enable_debug': False,          # Enable debug mode
    'step_mode': False,             # Enable step-by-step execution
    'show_targets': True,           # Show targets in RoboDK
    'simulation_only': True,        # Run in simulation mode only
    'verbose_output': False         # Enable verbose console output
}

# =============================================================================
# SAFETY CONFIGURATION
# =============================================================================

# Safety limits and monitoring
SAFETY_CONFIG = {
    'enable_limits': True,          # Enable safety limit checking
    'emergency_stop': 'DI1',        # Emergency stop input signal
    'safety_zone_check': True,      # Enable safety zone monitoring
    'collision_sensitivity': 0.8,   # Collision detection sensitivity (0-1)
    'force_limit': 50,              # N - Maximum force limit
    'torque_limit': 5               # Nm - Maximum torque limit
}

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def validate_position(x, y, z):
    """
    Validate if position is within workspace limits
    
    Args:
        x, y, z (float): Position coordinates in mm
        
    Returns:
        bool: True if position is valid, False otherwise
    """
    return (WORKSPACE_LIMITS['x_min'] <= x <= WORKSPACE_LIMITS['x_max'] and
            WORKSPACE_LIMITS['y_min'] <= y <= WORKSPACE_LIMITS['y_max'] and
            WORKSPACE_LIMITS['z_min'] <= z <= WORKSPACE_LIMITS['z_max'])

def get_safe_approach_height(z):
    """
    Calculate safe approach height for given Z coordinate
    
    Args:
        z (float): Target Z coordinate in mm
        
    Returns:
        float: Safe approach height in mm
    """
    return max(z + APPROACH_DISTANCE, WORKSPACE_LIMITS['z_min'] + MIN_APPROACH_HEIGHT)

def check_speed_limits(linear_speed, joint_speed):
    """
    Check if speeds are within safe limits
    
    Args:
        linear_speed (float): Linear speed in mm/s
        joint_speed (float): Joint speed in deg/s
        
    Returns:
        tuple: (is_valid, adjusted_linear_speed, adjusted_joint_speed)
    """
    is_valid = True
    
    if linear_speed > MAX_LINEAR_SPEED:
        linear_speed = MAX_LINEAR_SPEED
        is_valid = False
    
    if joint_speed > MAX_JOINT_SPEED:
        joint_speed = MAX_JOINT_SPEED
        is_valid = False
    
    return is_valid, linear_speed, joint_speed

# =============================================================================
# CONFIGURATION VALIDATION
# =============================================================================

def validate_config():
    """
    Validate configuration parameters
    
    Returns:
        list: List of validation errors (empty if all valid)
    """
    errors = []
    
    # Check workspace limits
    if WORKSPACE_LIMITS['x_min'] >= WORKSPACE_LIMITS['x_max']:
        errors.append("Invalid X workspace limits")
    
    if WORKSPACE_LIMITS['y_min'] >= WORKSPACE_LIMITS['y_max']:
        errors.append("Invalid Y workspace limits")
    
    if WORKSPACE_LIMITS['z_min'] >= WORKSPACE_LIMITS['z_max']:
        errors.append("Invalid Z workspace limits")
    
    # Check speed limits
    if DEFAULT_LINEAR_SPEED > MAX_LINEAR_SPEED:
        errors.append("Default linear speed exceeds maximum")
    
    if DEFAULT_JOINT_SPEED > MAX_JOINT_SPEED:
        errors.append("Default joint speed exceeds maximum")
    
    # Check approach distance
    if APPROACH_DISTANCE < MIN_APPROACH_HEIGHT:
        errors.append("Approach distance less than minimum height")
    
    return errors

# Run validation when module is imported
if __name__ == "__main__":
    errors = validate_config()
    if errors:
        print("Configuration validation errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("Configuration validation passed")