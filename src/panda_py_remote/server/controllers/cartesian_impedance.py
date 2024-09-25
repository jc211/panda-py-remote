import typing
import numpy as np

import tractor

import panda_py
import panda_py.controllers
from panda_py_remote.core.utils import convert_libfranka_state_to_robot_state
from panda_py_remote.server.controllers.context import ControlContext
from panda_py_remote.core.constants import DEFAULT_CARTESIAN_IMPEDANCE

class CartesianImpedance(ControlContext):
    def __init__(self,
                 context: tractor.Context,
                 panda: panda_py.Panda,
                 impedance: np.ndarray[tuple[typing.Literal[6], typing.Literal[6]], np.dtype[np.float64]] = DEFAULT_CARTESIAN_IMPEDANCE,
                 damping_ratio: float = 1,
                 nullspace_stiffness: float = 0.5,
                 filter_coeff: float = 1,
                 control_frequency: int = 1000
                 ):
        
        self.controller = panda_py.controllers.CartesianImpedance(
            impedance=impedance,
            damping_ratio=damping_ratio,
            nullspace_stiffness=nullspace_stiffness,
            filter_coeff=filter_coeff
        )
        
        super().__init__(panda=panda, context=context, controller=self.controller, control_frequency=control_frequency)
    
    def read_setpoint(self):
        msg = self.try_receive()
        if msg is None:
            return
        position = np.array(msg["position"])
        orientation = np.array(msg["orientation"])
        q_nullspace = np.array(msg["q_nullspace"])
        self.controller.set_control(position, orientation, q_nullspace)
        
