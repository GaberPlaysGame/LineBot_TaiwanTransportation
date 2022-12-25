from transitions.extensions import GraphMachine
from functools import partial


class FSMModel(GraphMachine):
    fsm_filename = 'FSM_diagram.png'
    state = ""

    def __init__(self, **machine_configs):
        self.machine = GraphMachine(model=self, **machine_configs)
        self.state = 'default'
    def state_MRT_Taipei(self, event):
        print("Change to MRT Taipei state.\n")
        self.state = 'Taipei'
        return True
    def state_MRT_Taichung(self, event):
        print("Change to MRT Taichung state.\n")
        self.state = 'Taichung'
        return True
    def state_MRT_Tainan(self, event):
        print("Change to MRT Tainan state.\n")
        self.state = 'Tainan'
        return True
    def state_MRT_Kaoshiung(self, event):
        print("Change to MRT Kaoshiung state.\n")
        self.state = 'Kaohsiung'
        return True
    def state_default(self, event):
        print("Change to default state.\n")
        self.state = 'default'
        return True