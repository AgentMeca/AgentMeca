# Glove Box Frontend UI

PyQt5-based UI definitions for glove-box demo.

## Prerequisites
- Python 3.7 or later
- PyQt5 installed

## Files
- `.ui` files: Qt Designer layouts for `MainWindow`, `SetupWindow`, and `ProgressWindow`.
- `MainWindow.py`, `SetupWindow.py`, `ProgressWindow.py`: Generated Python UI wrappers.
- `customWidgets.py`: Custom Qt widgets (e.g., `RackStatus`, `CustomToggleButton`).
- `images/`: Icons and schematic images used in the UI.

## Usage
This package is imported by the Application launcher.
No standalone execution.

To edit UI:
```bash
pyuic5 SetupWindow.ui -o SetupWindow.py
```  
Repeat for other `.ui` files.
