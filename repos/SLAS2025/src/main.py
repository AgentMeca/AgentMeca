from MecaPlanar import MecaPlanar, PlanarMotorMove
from mecademicpy.robot import Robot
from utilities import *
from constants import *
from pmclib import pmc_types


# Robot setup and activation
pipette = Robot()
vials = Robot()
well = Robot()

pipette.Connect(PIPETTE_IP)
vials.Connect(VIAL_IP)
well.Connect(WELL_IP)

pipette.ResetError()
vials.ResetError()
well.ResetError()

pipette.ActivateAndHome()
vials.ActivateAndHome()
well.ActivateAndHome()
pipette.WaitHomed()
vials.WaitHomed()
well.WaitHomed()

pipette.ClearMotion()
vials.ClearMotion()
well.ClearMotion()

pipette.ResumeMotion()
vials.ResumeMotion()
well.ResumeMotion()

pipette.MoveJoints(*PIPETTE_SAFE_POS)
vials.MoveJoints(*VIALS_SAFE_POS)
well.MoveJoints(*WELL_SAFE_POS)


# Planar setup and activation
planar = MecaPlanar()
planar.connect(ip=PMC_IP)
planar.initialize()


wells1 = XbotType('well', 1)
wells2 = XbotType('well', 3)
vials1 = XbotType('vial', 4)
vials2 = XbotType('vial', 2)
planar.define_stereotype(pmc_types.MOVERTYPE.M3_06,
                         1,
                         size_pos_x=0.070,
                         size_neg_x=-0.070)
planar.assign_stereotype(1, 1)
planar.assign_stereotype(3, 1)

state = PlanarStateSLAS([vials1, wells1, vials2, wells2])

# Move everything to starting position
planar.send_auto_move_command(4, state.get_id_positions(), X_POS, Y_POS)
planar.wait_multiple_move_done(state.get_id_positions())

# Main loop
debug_count = 0
swap_side = 'R'
while True:
    pass
    # Robot pipettes the vials
    pipette.StartProgram(PIPETTING_VIAL_PROG)

    # Robots start swapping parts
    if swap_side == 'R':
        vials.StartProgram(SWAP_VIAL_RIGHT)
        well.StartProgram(SWAP_WELL_RIGHT)
        swap_side = 'L'
    else:
        vials.StartProgram(SWAP_VIAL_LEFT)
        well.StartProgram(SWAP_WELL_LEFT)
        swap_side = 'R'

    pipette.WaitIdle()

    # Xbots swap pipette
    state.swap_pipetting()
    swap1 = []
    swap2 = []
    for m1, m2 in zip(M1, M2):
        swap1.append(PlanarMotorMove(
            state.get_id_positions()[1], m1[0], m1[1]))
        swap1.append(PlanarMotorMove(
            state.get_id_positions()[0], m2[0], m2[1]))

    planar.send_multi_linear_commands(swap1)
    planar.send_multi_linear_commands(swap2)
    planar.wait_multiple_move_done(state.get_id_positions()[:2])

    # Xbot starts spinny
    planar.send_rotation(state.get_id_positions()[1])

    # Robot pipettes well plate
    pipette.StartProgram(PIPETTING_WELL_PROG)
    pipette.WaitIdle()

    # Wait for robot and spin to be done
    planar.wait_move_done(state.get_id_positions()[1])

    # Wait for other robots to be done
    vials.WaitIdle()
    well.WaitIdle()

    # Full swap
    state.swap_full()
    planar.send_auto_move_command(4, state.get_id_positions(), X_POS, Y_POS)
    planar.wait_multiple_move_done(state.get_id_positions())

    debug_count += 1
    if debug_count >= 5:
        break
