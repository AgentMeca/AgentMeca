# Glove Box Application Launcher

This module launches the main PyQt5 application for glove-box vial handling.

## Prerequisites
- Python 3.7 or later
- PyQt5, mecademicpy, scipy, requests installed

## Files
- `mainApp.py`: Defines the **Setup**, **Main**, and **Progress** windows, and orchestrates robot commands.
- `main.py`: (if present) alternative entrypoint

## Running
```bash
cd Demo_Glove_Box/Application
python mainApp.py
```

## Configuration
- Edit default pick/place coordinate arrays in `SetupWindow` class.
- Ensure backend and frontend directories are in `PYTHONPATH` or parent directory.

## Workflow
1. **Setup**: Define rack and centrifuge coordinate points.
2. **Main**: Connect to robot(s) and start auto-vial handling.
3. **Progress**: View simulated centrifuge processing.
