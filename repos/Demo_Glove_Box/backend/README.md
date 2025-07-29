# Glove Box Backend API

Provides core data models for rack and centrifuge status and coordinates.

## Prerequisites
- Python 3.7 or later
- `mecademicpy`, `scipy`, `numpy`

## Files
- `backend.py`: Defines:
  - `MainRack`: tracks vial presence and pick directions
  - `Centrifuge`: tracks centrifuge slot status
  - `projectvector()`: helper for coordinate transformations

## Usage
This module is imported by the Application launcher to:
1. Maintain rack/centrifuge positions
2. Update status and pick directions dynamically

Example:
```python
from backend.backend import MainRack, Centrifuge
rack = MainRack(6)
cent = Centrifuge(6)
rack.update_position(0, [x,y,z,rx,ry,rz])
```
