from contextlib import AsyncExitStack

import trio
import tractor

import panda_py
from panda_py import controllers

from panda_py_remote.core.utils import convert_libfranka_state_to_robot_state


class ControlContext:
    def __init__(self, 
                 panda: panda_py.Panda, 
                 context: tractor.Context,
                 controller: controllers.TorqueController, 
                 control_frequency: int = 1000):
        self.dt_ = 1 / control_frequency
        self.t_prev = trio.current_time()
        self.panda = panda
        self.controller = controller
        self.context = context
        self.exit_stack = AsyncExitStack()
    
    async def __aenter__(self):
        self.panda.start_controller(self.controller)
        await self.context.started()
        self.stream = await self.exit_stack.enter_async_context(self.context.open_stream())
        return self
    
    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.exit_stack.aclose()
        self.panda.stop_controller()
    
    async def ok(self):
        self.panda.raise_error()
        elapsed = trio.current_time() - self.t_prev
        if elapsed < self.dt_:
            await trio.sleep(self.dt_ - elapsed)
        self.t_prev = trio.current_time()
        await self.send_state()
        return True

    def try_receive(self):
        try:
            msg = self.stream.receive_nowait()
            return msg
        except trio.WouldBlock:
            return None
    
    async def send_state(self):
        state = self.panda.get_state()
        state = convert_libfranka_state_to_robot_state(state)
        await self.stream.send(state)