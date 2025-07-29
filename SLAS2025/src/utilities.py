from copy import deepcopy


class XbotType():
    def __init__(self, bot_type: str, id: int):
        self.bot_type = bot_type
        self.id = id


class PlanarStateSLAS():
    def __init__(self, xbot_list: list[XbotType]):
        self.state_dict = {}
        self.set_state(xbot_list)

    def set_state(self, bots: XbotType):
        self.state_dict["pp"] = bots[0]
        self.state_dict["wp"] = bots[1]
        self.state_dict["sv"] = bots[2]
        self.state_dict["sw"] = bots[3]

    def get_id_positions(self) -> list[int]:
        return [self.state_dict["pp"].id,
                self.state_dict["wp"].id,
                self.state_dict["sw"].id,
                self.state_dict["sv"].id]

    def swap_pipetting(self):
        temp_pp = deepcopy(self.state_dict["pp"])
        temp_wp = deepcopy(self.state_dict["wp"])

        self.state_dict["pp"] = deepcopy(temp_wp)
        self.state_dict["wp"] = deepcopy(temp_pp)

    def swap_full(self):
        temp_pp = deepcopy(self.state_dict["pp"])
        temp_wp = deepcopy(self.state_dict["wp"])
        temp_sw = deepcopy(self.state_dict["sw"])
        temp_sv = deepcopy(self.state_dict["sv"])

        if temp_pp.bot_type == "well" and temp_wp.bot_type == "vial":
            self.state_dict["sw"] = deepcopy(temp_pp)
            self.state_dict["sv"] = deepcopy(temp_wp)
        elif temp_pp.bot_type == "vial" and temp_wp.bot_type == "well":
            self.state_dict["sv"] = deepcopy(temp_pp)
            self.state_dict["sw"] = deepcopy(temp_wp)
        else:
            raise ValueError("Uh Oh can't swap cause of type issue.")

        self.state_dict["pp"] = deepcopy(temp_sv)
        self.state_dict["wp"] = deepcopy(temp_sw)
