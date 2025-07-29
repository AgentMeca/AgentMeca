This repo contains the code for the demo showcased at SALS 2022.

# Demo Description
A robot is tending to a simulated centrifuge for vials. The centrifuge and racks have fixed positions but in real life a vision system might be needed to find the positions of the vials.

## UI
The UI has three windows:
* Main Window
* Setup Window
* Progress Window

#### Main Window
The main window is used to connect to the robot, select vials to load and unload the centrifuge, keep track of the centrifuge and rack status, and start the auto-mode.

#### Setup Window
The setup window is used to set the points for the rack and centrifuge as well as the pick direction for each pair.

#### Progress Window
The progress window is only there to simulate the processing of the samples by the centrifuge.


# Work left
While the demo is functionnal, there is a lot of work left to do especially concerning the error handling. I would have to add a lot of Try/Except for all the robot movements and robot connections. This has not been done for time constraints and because it is not production code.
