This demo showcases a microhandling application where a Meca500 robot picks random samples from a tray, presents them under a USB microscope, and allows joystick-based fine positioning.

## Prerequisites
- A Meca500 robot connected to the network (default IP auto-detected).
- A USB microscope accessible by OpenCV.
- A joystick/gamepad (Windows only via `windmm.dll`).
- Python 3.7 or later
- Python dependencies:
  ```bash
  pip install mecademicpy pyqt5 opencv-python
  ```

## Configuration
1. **Robot Connection**: In `Application/mainApp.py`, `Robot().Connect()` uses default IP; adjust if needed.
2. **Sample Tray Positions**: Modify `sampletray.SampleTray().positions_wrf` for custom tray layouts.
3. **Joystick**: Ensure Windows and a compatible gamepad; no Linux support via `windmm.dll`.

## Directory Structure
- `Application/`: Main PyQt5 application launcher
- `backend/`: Robot, joystick, and automation thread implementations
- `frontend/`: UI definitions and video player
- `requirements.txt`: Python package list
- `structure.txt`: High-level workflow description

## Running the Demo
```bash
cd Demo_Microscope/Application
python mainApp.py
```
Workflow:
1. **Pick Sample**: Click “Pick Sample” to select a random tray index and move robot to the microscope.
2. **Joystick Control**: Use joystick to fine-adjust sample position under the microscope feed.
3. **Return Sample**: Click “Return Sample” to move the sample back to its tray slot.
4. **Auto Mode**: Toggle “Automode” to run pick-and-place cycles automatically.

## Troubleshooting
- **Camera feed not visible**: Check OpenCV camera indices in the dropdown.
- **Joystick unresponsive**: Windows only; verify drivers and supported gamepad.
- **Robot connection issues**: Confirm network settings and robot availability.
