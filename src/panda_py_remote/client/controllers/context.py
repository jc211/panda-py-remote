from contextlib import AsyncExitStack
import typing

import tractor
import trio

from panda_py_remote.core.domain import RobotState

class ControlContext:
    def __init__(self, 
                 portal: tractor.Portal,
                 endpoint: typing.Callable,
                 control_freq: int = 100,
                 **kwargs
                 ):
        self.exit_stack = AsyncExitStack()
        self.portal = portal
        self.control_freq = control_freq
        self._dt = 1/control_freq
        self.last_state = None
        self.actor_ctx = self.portal.open_context(endpoint, **kwargs)
        
    def get_time(self):
        return trio.current_time() - self.t_start
        
    async def __aenter__(self):
        self.t_prev = trio.current_time()
        self.t_start = self.t_prev
        self.portal_ctx, self.last_state = await self.exit_stack.enter_async_context(self.actor_ctx)
        self.stream = await self.exit_stack.enter_async_context(self.portal_ctx.open_stream(allow_overruns=True))
        return self

    async def __aexit__(self, exc_type, exc, tb):
        await self.exit_stack.aclose()  

    def get_state(self):
        return self.last_state
    
    def try_receive(self):
        try:
            msg = self.stream.receive_nowait()
            return msg
        except trio.WouldBlock:
            return None
        
    def _read_last_state(self):
        msg = self.try_receive()
        if msg is None:
            return
        self.last_state = RobotState.from_dict(msg)

    async def ok(self):
        elapsed = trio.current_time() - self.t_prev
        if elapsed < self._dt:
            await trio.sleep(self._dt - elapsed)
        self.t_prev = trio.current_time()
        self._read_last_state()
        return True
    