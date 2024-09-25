import typing

import numpy as np
import tractor

from panda_py_remote.client.controllers.context import ControlContext
from panda_py_remote.server import endpoints
from panda_py_remote.core.constants import DEFAULT_CARTESIAN_IMPEDANCE, JOINT_POSITION_START

class CartesianImpedance(ControlContext):
    def __init__(self, 
                 portal: tractor.Portal,
                 impedance: np.ndarray[tuple[typing.Literal[6], typing.Literal[6]], np.dtype[np.float64]] = DEFAULT_CARTESIAN_IMPEDANCE,
                 damping_ratio: float = 1.0, 
                 nullspace_stiffness: float = 0.5, 
                 filter_coeff: float = 1.0, 
                 control_freq: int = 100
                 ):
        self.impedance = impedance
        self.damping_ratio = damping_ratio
        self.nullspace_stiffness = nullspace_stiffness
        self.filter_coeff = filter_coeff
        super().__init__(
            portal=portal, 
            endpoint=endpoints.start_cartesian_impedance_controller,
            control_freq=control_freq,
            impedance=impedance.flatten().tolist(),
            nullspace_stiffness=nullspace_stiffness,
            damping_ratio=damping_ratio,
            filter_coeff=filter_coeff
            )
     
    async def set_control(self, 
                        position: np.ndarray[tuple[typing.Literal[3], typing.Literal[1]], np.dtype[np.float64]], 
                        orientation: np.ndarray[tuple[typing.Literal[4], typing.Literal[1]], np.dtype[np.float64]], 
                        q_nullspace: np.ndarray[tuple[typing.Literal[7], typing.Literal[1]], np.dtype[np.float64]] = JOINT_POSITION_START) -> None:
        
        await self.stream.send({
            "position": position.flatten().tolist(),
            "orientation": orientation.flatten().tolist(),
            "q_nullspace": q_nullspace.flatten().tolist()
        })
   