import typing
import numpy as np

import tractor

import panda_py
import panda_py.controllers
from panda_py_remote.core.utils import convert_libfranka_state_to_robot_state
from panda_py_remote.server.controllers.context import ControlContext
from panda_py_remote.core.constants import DEFAULT_JOINT_STIFFNESS, DEFAULT_DAMPING_DATA

class JointPosition(ControlContext):
    def __init__(self,
                 context: tractor.Context,
                 panda: panda_py.Panda,
                 stiffness: np.ndarray[tuple[typing.Literal[7], typing.Literal[1]], np.dtype[np.float64]] = DEFAULT_JOINT_STIFFNESS,
                 damping: np.ndarray[tuple[typing.Literal[7], typing.Literal[1]], np.dtype[np.float64]] = DEFAULT_DAMPING_DATA,
                 filter_coeff: float = 1.0,
                 control_frequency: int = 1000
                 ):
        
        self.controller = panda_py.controllers.JointPosition(
            stiffness=stiffness,
            damping=damping,
            filter_coeff=filter_coeff
        )
        
        super().__init__(panda=panda, context=context, controller=self.controller, control_frequency=control_frequency)
    
    def read_setpoint(self):
        msg = self.try_receive()
        if msg is None:
            return
        position = np.array(msg["position"])
        velocity = np.array(msg["velocity"])
        self.controller.set_control(position, velocity)
        
