# Glove Box UI & Math Tests

Simple test scripts to verify custom widgets and rotation logic.

## Prerequisites
- Python 3.7 or later
- PyQt5, scipy installed

## Tests
- `pyqtTests.py`: Launches a window to manually verify `RackStatus` and `CustomToggleButton` behaviors.
  ```bash
  python pyqtTests.py
  ```
- `rot_test.py`: Exercises `scipy.spatial.transform.Rotation` math for coordinate transformations.
  ```bash
  python rot_test.py
  ```

No automated assertions—visual and console inspection.
