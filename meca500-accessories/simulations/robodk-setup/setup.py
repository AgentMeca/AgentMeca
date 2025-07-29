#!/usr/bin/env python3
"""
RoboDK Setup Script for Mecademic Meca500
=========================================

This script helps set up the RoboDK environment for Mecademic Meca500 programming.
It verifies installation, configures the workspace, and prepares example projects.

Usage:
    python setup.py [options]

Options:
    --check-install     Check RoboDK installation and API
    --create-workspace  Create sample workspace with Meca500
    --install-deps      Install Python dependencies
    --validate-config   Validate configuration files
    --help             Show this help message

Author: Generated for Mecademic Robot Integration
"""

import sys
import os
import subprocess
import importlib.util
import argparse

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 6):
        print("ERROR: Python 3.6 or higher is required")
        return False
    print(f"✓ Python version: {sys.version}")
    return True

def check_robodk_installation():
    """Check if RoboDK is installed and accessible"""
    try:
        # Try to import RoboDK API
        import robodk.robolink as rl
        import robodk.robomath as rm
        
        print("✓ RoboDK API is available")
        
        # Try to connect to RoboDK
        try:
            RDK = rl.Robolink()
            if RDK.Valid():
                print("✓ RoboDK software is running and accessible")
                return True
            else:
                print("⚠ RoboDK software is not running")
                print("  Please start RoboDK and try again")
                return False
        except Exception as e:
            print(f"⚠ Cannot connect to RoboDK: {e}")
            return False
            
    except ImportError:
        print("✗ RoboDK API not found")
        print("  Install with: pip install robodk")
        return False

def install_dependencies():
    """Install required Python packages"""
    print("Installing Python dependencies...")
    
    try:
        # Check if requirements.txt exists
        if os.path.exists("requirements.txt"):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✓ Dependencies installed successfully")
            return True
        else:
            # Install basic RoboDK package
            subprocess.check_call([sys.executable, "-m", "pip", "install", "robodk"])
            print("✓ RoboDK package installed")
            return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Failed to install dependencies: {e}")
        return False

def create_sample_workspace():
    """Create a sample RoboDK workspace with Meca500"""
    try:
        import robodk.robolink as rl
        import robodk.robomath as rm
        
        print("Creating sample workspace...")
        
        RDK = rl.Robolink()
        
        if not RDK.Valid():
            print("✗ Cannot connect to RoboDK")
            return False
        
        # Clear existing workspace
        RDK.CloseStation()
        
        # Create new station
        station = RDK.AddStation("Meca500_Sample_Workspace")
        
        # Add Meca500 robot from library
        print("  Adding Meca500 robot...")
        robot_file = RDK.getParam("PATH_LIBRARY") + "/Mecademic-Meca500-R3.robot"
        robot = RDK.AddFile(robot_file)
        
        if robot.Valid():
            robot.setName("Meca500")
            print("  ✓ Meca500 robot added")
        else:
            print("  ⚠ Could not add Meca500 robot from library")
            print("    Please add Meca500 manually from RoboDK library")
        
        # Add sample targets
        print("  Adding sample targets...")
        
        # Home position
        home_target = RDK.AddTarget("Home")
        home_joints = [0, 0, 0, 0, 0, 0]
        home_target.setJoints(home_joints)
        
        # Pick position
        pick_target = RDK.AddTarget("Pick")
        pick_pose = rm.transl(300, 100, 200)
        pick_target.setPose(pick_pose)
        
        # Place position  
        place_target = RDK.AddTarget("Place")
        place_pose = rm.transl(300, -100, 200)
        place_target.setPose(place_pose)
        
        print("  ✓ Sample targets created")
        
        # Save station
        station_file = os.path.join(os.getcwd(), "Meca500_Sample.rdk")
        RDK.Save(station_file)
        print(f"  ✓ Workspace saved as: {station_file}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to create workspace: {e}")
        return False

def validate_configuration():
    """Validate configuration files"""
    print("Validating configuration...")
    
    try:
        # Check if config template exists
        if os.path.exists("config_template.py"):
            print("  ✓ Configuration template found")
        else:
            print("  ⚠ Configuration template not found")
            return False
        
        # Try to import and validate config
        if os.path.exists("config.py"):
            print("  ✓ Configuration file found")
            
            # Import config module
            spec = importlib.util.spec_from_file_location("config", "config.py")
            config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config)
            
            # Run validation if available
            if hasattr(config, 'validate_config'):
                errors = config.validate_config()
                if errors:
                    print("  ✗ Configuration validation failed:")
                    for error in errors:
                        print(f"    - {error}")
                    return False
                else:
                    print("  ✓ Configuration validation passed")
            else:
                print("  ⚠ No validation function in config")
        else:
            print("  ⚠ No config.py found")
            print("    Copy config_template.py to config.py and customize")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Configuration validation error: {e}")
        return False

def check_example_files():
    """Check if example files are present"""
    print("Checking example files...")
    
    files_to_check = [
        "example_robodk_script.py",
        "requirements.txt",
        "config_template.py",
        "README.md"
    ]
    
    all_present = True
    for file_name in files_to_check:
        if os.path.exists(file_name):
            print(f"  ✓ {file_name}")
        else:
            print(f"  ✗ {file_name} - Missing")
            all_present = False
    
    return all_present

def run_system_check():
    """Run complete system check"""
    print("RoboDK Meca500 Setup - System Check")
    print("=" * 40)
    
    checks = [
        ("Python Version", check_python_version),
        ("RoboDK Installation", check_robodk_installation),
        ("Example Files", check_example_files),
        ("Configuration", validate_configuration)
    ]
    
    results = {}
    for check_name, check_func in checks:
        print(f"\n{check_name}:")
        results[check_name] = check_func()
    
    print("\n" + "=" * 40)
    print("SYSTEM CHECK SUMMARY:")
    
    all_passed = True
    for check_name, result in results.items():
        status = "PASS" if result else "FAIL"
        print(f"  {check_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        print("\n✓ All checks passed! System is ready for RoboDK programming.")
    else:
        print("\n⚠ Some checks failed. Please address the issues above.")
    
    return all_passed

def show_usage():
    """Show usage instructions"""
    print("""
RoboDK Meca500 Setup Instructions:
=================================

1. System Check:
   python setup.py --check-install

2. Install Dependencies:
   python setup.py --install-deps

3. Create Sample Workspace:
   python setup.py --create-workspace

4. Validate Configuration:
   python setup.py --validate-config

5. Run Example:
   python example_robodk_script.py

For more information, see README.md
""")

def main():
    """Main setup function"""
    parser = argparse.ArgumentParser(description="RoboDK Meca500 Setup Script")
    parser.add_argument("--check-install", action="store_true", 
                       help="Check RoboDK installation and system")
    parser.add_argument("--install-deps", action="store_true",
                       help="Install Python dependencies")
    parser.add_argument("--create-workspace", action="store_true",
                       help="Create sample RoboDK workspace")
    parser.add_argument("--validate-config", action="store_true",
                       help="Validate configuration files")
    parser.add_argument("--all", action="store_true",
                       help="Run all setup steps")
    
    args = parser.parse_args()
    
    # If no arguments provided, show usage
    if not any(vars(args).values()):
        show_usage()
        return
    
    success = True
    
    if args.check_install or args.all:
        success &= run_system_check()
    
    if args.install_deps or args.all:
        print("\nInstalling Dependencies:")
        success &= install_dependencies()
    
    if args.create_workspace or args.all:
        print("\nCreating Sample Workspace:")
        success &= create_sample_workspace()
    
    if args.validate_config or args.all:
        print("\nValidating Configuration:")
        success &= validate_configuration()
    
    if success:
        print("\n✓ Setup completed successfully!")
        print("You can now run: python example_robodk_script.py")
    else:
        print("\n⚠ Setup completed with some issues.")
        print("Please check the error messages above.")

if __name__ == "__main__":
    main()