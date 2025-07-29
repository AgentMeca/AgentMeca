# Microscope Demo Application Launcher

Launches the PyQt5 GUI for microhandling demo.

## Prerequisites
- Python 3.7 or later
- `pyqt5`, `mecademicpy`, `opencv-python` installed

## Files
- `mainApp.py`: Main entrypoint setting up UI and robot logic.

## Running
```bash
cd Demo_Microscope/Application
python mainApp.py
```

## Configuration
- Adjust robot connection parameters directly in `mainApp.py` (default `Connect()`).

## Workflow
1. **Pick Sample**: Selects and picks a random sample.
2. **Microscope View**: Displays live video; joystick controls robot pose.
3. **Return Sample**: Places the sample back in the tray.
4. **Automode**: Automates full pick-present-return cycle.
