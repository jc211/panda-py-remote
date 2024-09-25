import functools
from re import S
import typing
import msgspec
import numpy as np
import trio
import tractor
import panda_py
from panda_py_remote.server.controllers.joint_position import JointPosition
from panda_py_remote.server.desk import Desk
from panda_py_remote.server.controllers.cartesian_impedance import CartesianImpedance
from panda_py_remote.core.utils import RobotState, convert_libfranka_state_to_robot_state
from panda_py_remote.core.constants import DEFAULT_CARTESIAN_IMPEDANCE, DEFAULT_DAMPING_DATA, DEFAULT_JOINT_STIFFNESS

class Panda:
    _instance = None
    
    def __init__(self, robot_ip: str = "172.16.0.2"):
        self.robot_ip = robot_ip
        self.desk = Desk(robot_ip)
        self.robot = None
    
    def get_robot(self) -> panda_py.Panda:
        if self.robot is None:
            self.robot = panda_py.Panda(self.robot_ip)
        return self.robot
      
    @classmethod
    def get_instance(cls, robot_ip: str = "172.16.0.2"):
        if cls._instance is None:
            cls._instance = cls(robot_ip)
        return cls._instance
    
      
def get_server():
    server = Panda.get_instance()
    return server

async def login(username: str, password: str):
    self = get_server()
    await self.desk.login(username=username, password=password)

async def unlock():
    self = get_server()
    with trio.move_on_after(40) as ctx:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(self.desk.wait_for_brakes_to_open)
            await self.desk.unlock()
    if ctx.cancel_called:
        raise Exception("Unlocking timed out")

async def lock():
    self = get_server()
    with trio.move_on_after(40) as ctx:
        async with trio.open_nursery() as nursery:
            nursery.start_soon(self.desk.wait_for_brakes_to_close)
            await self.desk.lock()
    if ctx.cancel_called:
        raise Exception("Locking timed out")

async def activate_fci():
    self = get_server()
    return await self.desk.activate_fci()

async def deactivate_fci():
    self = get_server()
    return await self.desk.deactivate_fci()

async def take_control(force: bool = False):
    self = get_server()
    return await self.desk.take_control(force)

async def get_state() -> RobotState:
    self = get_server()
    return convert_libfranka_state_to_robot_state(self.get_robot().get_state())

async def read_once() -> RobotState:
    self = get_server()
    self.get_robot().raise_error()
    state = self.get_robot().get_robot().read_once()
    return convert_libfranka_state_to_robot_state(state)

async def move_to_joint_position(waypoints: list[np.ndarray[tuple[typing.Literal[7], typing.Literal[1]], np.dtype[np.float64]]], speed_factor: float = 0.2, dq_threshold: float = 0.001, success_threshold: float = 0.01):
    self = get_server()
    robot = self.get_robot()
    robot.raise_error()
    f = functools.partial(robot.move_to_joint_position, waypoints=waypoints, speed_factor=speed_factor, dq_threshold=dq_threshold, success_threshold=success_threshold)
    await trio.to_thread.run_sync(f) # If the safety button is pressed, this blocks forever
    robot.raise_error()

async def get_orientation(scalar_first: bool = False) -> np.ndarray[tuple[typing.Literal[4], typing.Literal[1]], np.dtype[np.float64]]:
    self = get_server()
    robot = self.get_robot()
    q = robot.get_orientation(scalar_first=scalar_first)
    return q.tolist()

async def get_pose() -> np.ndarray[tuple[typing.Literal[4], typing.Literal[4]], np.dtype[np.float64]]:
    self = get_server()
    robot = self.get_robot()
    res = robot.get_pose()
    return res.flatten().tolist()

async def get_position() -> np.ndarray[tuple[typing.Literal[3], typing.Literal[1]], np.dtype[np.float64]]:
    """
                Current end-effector position in robot base frame.
    """
    self = get_server()
    robot = self.get_robot()
    res = robot.get_position()
    return res.tolist()
    
@tractor.context
async def start_cartesian_impedance_controller( 
                            ctx: tractor.Context, 
                            impedance: list[float] = DEFAULT_CARTESIAN_IMPEDANCE.tolist(),
                            damping_ratio: float = 1.0,
                            nullspace_stiffness: float = 0.5,
                            filter_coeff: float = 1.0,
                            control_freq: int = 1000):
        self = get_server()
        assert len(impedance) == 36
        impedance_np = np.asarray(impedance, dtype=np.float64).reshape(6, 6)
        
        async with CartesianImpedance(
            panda=self.get_robot(),
            context=ctx,
            impedance = impedance_np,
            damping_ratio=damping_ratio,
            nullspace_stiffness=nullspace_stiffness,
            filter_coeff=filter_coeff,
            control_frequency=control_freq
        ) as ctrl:
            while await ctrl.ok():
                ctrl.read_setpoint()
                
@tractor.context
async def start_joint_position_controller( 
                            ctx: tractor.Context, 
                            stiffness: np.ndarray[tuple[typing.Literal[7], typing.Literal[1]], np.dtype[np.float64]] = DEFAULT_JOINT_STIFFNESS,
                            damping: np.ndarray[tuple[typing.Literal[7], typing.Literal[1]], np.dtype[np.float64]] = DEFAULT_DAMPING_DATA,
                            filter_coeff: float = 1.0,
                            control_freq: int = 1000):
        self = get_server()

        async with JointPosition(
            panda=self.get_robot(),
            context=ctx,
            stiffness = stiffness,
            damping=damping,
            filter_coeff=filter_coeff,
            control_frequency=control_freq
        ) as ctrl:
            while await ctrl.ok():
                ctrl.read_setpoint()