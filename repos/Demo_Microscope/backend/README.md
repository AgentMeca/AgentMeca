# Microscope Demo Backend API

Core classes for robot control, joystick handling, and auto mode logic.

## Prerequisites
- Python 3.7 or later
- `mecademicpy` installed

## Files
- `sampletray.py`: Defines `SampleTray` with tray slot coordinates.
- `joystick.py`: Low-level joystick input reader (Windows).
- `joystickThread.py`: Thread to poll joystick events and move robot.
- `autoThread.py`: Thread to automate pick-present-return cycles.
- `__init__.py`: Package initializer.

## Usage
Imported by the Application launcher to:
1. Manage sample positions (`SampleTray`).
2. Poll joystick for live robot movement.
3. Run automated sequences in background threads.
