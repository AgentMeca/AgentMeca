# SLAS2025
Documentation to use the SLAS2025 demo. The prerequisits are:
- Being able to use Windows Remote Desktop and have the proper IP address (or being able to change it).
- Download and install the Planar Motor Tool software. The installer is on the google drive.


## How to start the demo
### Remote desktop into the mini PC
The info for the mini pc can be found on the comapny's google drive. Use Windows Remote Desktop to get in the mini PC.

### Xbots setup
The first step is to use the Planar Motor Tool to make sure the correct xbots IDs are associated with the correct xbots type (vials or well plates). This can be done by changing the following lines in the [main.py](src/main.py) file. You can change the IDs in the followig lines:

```
wells1 = XbotType('well', 1)
wells2 = XbotType('well', 3)
vials1 = XbotType('vial', 4)
vials2 = XbotType('vial', 2)
```
The number in each function should correspond the an id associated with an xbot. From the Planar Motor Tool and looking at the xbots, make sure the id and types match by only changing the id. Do not change anything else bu the number in the arguments.

### Starting position
The starting position is to have parts on all the xbots (the positions of the xbots do not matter). Then for the well plate racks, put a well plate on the back one. For the vials rack, put 6 vials in the two back rows.

### Starting the script
To start the script, first use the terminal to navigate to the folder where this file is located. Then activate the virtual environment using:
```
.\venv\Scripts\activate
```
Once the virtual environment is active and the physical setup is done, launch the main script using:
```
python .\src\main.py
```

## In case of error
If there is an error and the program stops, make sure to re-do the physical setup before launching the script again.

## Modifying the robot programs
There is a backup of the robot programs on the google drive in the trade show folder. The programs themselves are stored on the robots and the name of the programs are listed as constants in the [contants.py](src/constants.py) file. If there are points that need to be ajusted, this can be done directly on the robots using the MecaPortal. The IP addresses of the robots are available in the same constants.py file.
