from MecaPlanar import MecaPlanar
from utilities import PlanarStateSLAS, XbotType
from constants import *


mp = MecaPlanar()
mp.connect()
mp.initialize()

print(mp.get_num_xbots())
print(mp.get_xbot_ids())


vials1 = XbotType('vial', 1)
vials2 = XbotType('vial', 4)
wells1 = XbotType('well', 3)
wells2 = XbotType('well', 2)


print("pp wp sw sv")
print("w  v  w  v")
state = PlanarStateSLAS([vials1, wells1, vials2, wells2])


mp.send_auto_move_command(4, state.get_id_positions(), X_POS, Y_POS)
mp.wait_multiple_move_done(state.get_id_positions())
state.swap_pipetting()
mp.start_macro(151, state.get_id_positions()[0])
mp.start_macro(150, state.get_id_positions()[1])
mp.wait_multiple_move_done(state.get_id_positions()[:2])
state.swap_full()
mp.send_auto_move_command(4, state.get_id_positions(), X_POS, Y_POS)
mp.wait_multiple_move_done(state.get_id_positions())
state.swap_pipetting()
mp.start_macro(151, state.get_id_positions()[0])
mp.start_macro(150, state.get_id_positions()[1])
mp.wait_multiple_move_done(state.get_id_positions()[:2])
mp.start_macro(160, state.get_id_positions()[1])
mp.wait_move_done(state.get_id_positions()[1])
