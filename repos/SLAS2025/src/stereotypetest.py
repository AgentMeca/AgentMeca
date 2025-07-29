from MecaPlanar import MecaPlanar
from constants import *
from pmclib import pmc_types


mp = MecaPlanar()
mp.connect(PMC_IP)
mp.initialize()

mp.define_stereotype(pmc_types.MOVERTYPE.M3_06,
                     1,
                     size_pos_x=0.0675,
                     size_neg_x=-0.0675)

mp.assign_stereotype(1, 1)
