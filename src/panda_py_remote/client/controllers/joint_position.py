import typing

import numpy as np
import tractor

from panda_py_remote.client.controllers.context import ControlContext
from panda_py_remote.server import endpoints
from panda_py_remote.core.constants import DEFAULT_JOINT_STIFFNESS, DEFAULT_DAMPING_DATA

class JointPosition(ControlContext):
    def __init__(self, 
                 portal: tractor.Portal,
                 stiffness: np.ndarray[tuple[typing.Literal[7], typing.Literal[1]], np.dtype[np.float64]] = DEFAULT_JOINT_STIFFNESS,
                 damping: np.ndarray[tuple[typing.Literal[7], typing.Literal[1]], np.dtype[np.float64]] = DEFAULT_DAMPING_DATA,
                 filter_coeff: float = 1.0,
                 control_freq: int = 1000
                 ):
        self.stiffness = stiffness
        self.damping = damping
        self.filter_coeff = filter_coeff
        super().__init__(
            portal=portal, 
            endpoint=endpoints.start_joint_position_controller,
            control_freq=control_freq,
            stiffness=stiffness.tolist(),
            damping=damping.tolist(),
            filter_coeff=filter_coeff
            )
     
    async def set_control(self, 
                        position: np.ndarray[tuple[typing.Literal[7], typing.Literal[1]], np.dtype[np.float64]], 
                        velocity: np.ndarray[tuple[typing.Literal[7], typing.Literal[1]], np.dtype[np.float64]] = np.zeros((7, 1))) -> None:

        await self.stream.send({
            "position": position.tolist(),
            "velocity": velocity.tolist()                  
            })
        
   