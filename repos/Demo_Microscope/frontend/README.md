# Microscope Demo Frontend UI

PyQt5 UI components and video player for the microscope demo.

## Prerequisites
- Python 3.7 or later
- `pyqt5`, `opencv-python` installed

## Files
- `ApplicationWindow.ui`: Qt Designer layout for the main window.
- `ApplicationWindow.py`: Generated Python UI wrapper.
- `VideoPlayer.py`: Live camera feed display component.
- `customWidgets.py`: Custom Qt widgets (e.g., status indicators).
- `images/`: Logo and other assets.

## Usage
Imported by the Application launcher; no standalone execution.

To edit UI files:
```bash
pyuic5 ApplicationWindow.ui -o ApplicationWindow.py
```
