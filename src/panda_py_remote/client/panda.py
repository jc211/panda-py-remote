from contextlib import AsyncExitStack
import logging
import typing


import tractor

import numpy as np

from panda_py_remote.client.controllers.joint_position import JointPosition
from panda_py_remote.core.constants import DEFAULT_CARTESIAN_IMPEDANCE, DEFAULT_DAMPING_DATA, DEFAULT_JOINT_STIFFNESS
from panda_py_remote.core.utils import RobotState
import panda_py_remote.server.endpoints as endpoints
from panda_py_remote.client.controllers.cartesian_impedance import CartesianImpedance

_logger = logging.getLogger('pandaclient')
_logger.setLevel(logging.DEBUG)
_logger.addHandler(logging.StreamHandler())

class Panda:
    def __init__(self, 
                 address: str):
        
        self.address = address
        self._exit_stack = None
        self._portal = None

    async def __aenter__(self):
        self._exit_stack = AsyncExitStack()
        self._root_actor = await self._exit_stack.enter_async_context(
            tractor.open_root_actor(
                registry_addrs=[(self.address, 1616)],
            )
        )
        _logger.debug("Waiting for remote actor")
        self._portal = await self._exit_stack.enter_async_context(
            tractor.wait_for_actor("panda", registry_addr=(self.address, 1616))
        ) 
        _logger.debug("Remote actor found")
        return self
    
    async def __aexit__(self, exc_type, exc, tb):
        _logger.debug("Exiting")
        if self._exit_stack:
            await self._exit_stack.__aexit__(exc_type, exc, tb)
    
    async def login(self, username: str, password: str):
        assert self._portal is not None
        await self._portal.run(endpoints.login, username=username, password=password)
    
    async def take_control(self, force: bool = False):
        assert self._portal is not None
        return await self._portal.run(endpoints.take_control, force=force)
    
    async def unlock(self) -> None:
        assert self._portal is not None
        return await self._portal.run(endpoints.unlock)

    async def lock(self) -> None:
        assert self._portal is not None
        return await self._portal.run(endpoints.lock)
    
    async def activate_fci(self) -> None:
        assert self._portal is not None
        return await self._portal.run(endpoints.activate_fci)
    
    async def deactivate_fci(self) -> None:
        assert self._portal is not None
        return await self._portal.run(endpoints.deactivate_fci)
    
    async def get_state(self) -> RobotState:
        assert self._portal is not None
        state = await self._portal.run(endpoints.get_state)
        return RobotState.from_dict(state)
    
    async def read_once(self) -> RobotState:
        assert self._portal is not None
        state = await self._portal.run(endpoints.read_once)
        return RobotState.from_dict(state)
    
    async def get_orientation(self, scalar_first: bool = False) -> np.ndarray[tuple[typing.Literal[4], typing.Literal[1]], np.dtype[np.float64]]:
        assert self._portal is not None
        res = await self._portal.run(endpoints.get_orientation, scalar_first=scalar_first)
        return np.array(res)
    
    async def get_pose(self) -> np.ndarray[tuple[typing.Literal[4], typing.Literal[4]], np.dtype[np.float64]]:
        assert self._portal is not None
        res = await self._portal.run(endpoints.get_pose)
        return np.array(res).reshape(4, 4)
    
    async def get_position(self) -> np.ndarray[tuple[typing.Literal[3], typing.Literal[1]], np.dtype[np.float64]]:
        """
                  Current end-effector position in robot base frame.
        """
        assert self._portal is not None
        res = await self._portal.run(endpoints.get_position)
        return np.array(res)
        
    async def move_to_joint_position(self, 
                                     waypoints: list[np.ndarray[tuple[typing.Literal[7], typing.Literal[1]], np.dtype[np.float64]]], 
                                     speed_factor: float = 0.2, 
                                     dq_threshold: float = 0.001, 
                                     success_threshold: float = 0.01):
        assert self._portal is not None      
        waypoints = [waypoint.tolist() for waypoint in waypoints] 
        return await self._portal.run(endpoints.move_to_joint_position, waypoints=waypoints, speed_factor=speed_factor, dq_threshold=dq_threshold, success_threshold=success_threshold)
    
    
    def start_cartesian_impedance_controller(self, 
                                  impedance: np.ndarray[tuple[typing.Literal[6], typing.Literal[6]], np.dtype[np.float64]] = DEFAULT_CARTESIAN_IMPEDANCE,
                                  damping_ratio: float = 1.0, 
                                  nullspace_stiffness: float = 0.5, 
                                  filter_coeff: float = 1.0, 
                                  control_freq: int = 1000) -> 'CartesianImpedance':
        assert self._portal is not None
        return CartesianImpedance(self._portal, impedance=impedance, damping_ratio=damping_ratio, nullspace_stiffness=nullspace_stiffness, filter_coeff=filter_coeff, control_freq=control_freq)
    
    def start_joint_position_controller(self,
                                        stiffness: np.ndarray[tuple[typing.Literal[7], typing.Literal[1]], np.dtype[np.float64]] = DEFAULT_JOINT_STIFFNESS,
                                        damping: np.ndarray[tuple[typing.Literal[7], typing.Literal[1]], np.dtype[np.float64]] = DEFAULT_DAMPING_DATA,
                                        filter_coeff: float = 1.0,
                                        control_freq: int = 1000) -> JointPosition:
        assert self._portal is not None
        return JointPosition(self._portal, stiffness=stiffness, damping=damping, filter_coeff=filter_coeff, control_freq=control_freq)