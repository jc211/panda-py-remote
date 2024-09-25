import ssl
import trio
import httpx
import tractor
import typing
import logging

_logger = logging.getLogger('watchdog')
_logger.setLevel(logging.INFO)
_logger.addHandler(logging.StreamHandler())

async def ping(address, timeout=0.1):
    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    async with httpx.AsyncClient(verify=ctx) as client:
        try:
            response = await client.get(address, timeout=httpx.Timeout(timeout))
            return response.status_code == 200
        except httpx.ConnectError:
            return False
        except httpx.ConnectTimeout:
            return False
    return False


class Watchdog:

    def __init__(self, seconds_between_pings=1.0, seconds_to_ping_timeout=0.1):
        self.seconds_between_pings = seconds_between_pings
        self.seconds_to_ping_timeout = seconds_to_ping_timeout
        self.state_changed = trio.lowlevel.ParkingLot()
        self.connected = False
        self.process_started = False
        
    
    def get_state(self):
        return {
            "connected": self.connected,
            "process_started": self.process_started
            }

    def notify_state_changed(self):
        self.state_changed.unpark_all()

    async def state_iter(self):
        yield self.get_state()
        while True:
            await self.state_changed.park()
            yield self.get_state()

    async def start_and_monitor_process(self, process_func: typing.Callable, kwargs):
        seconds_between_retry = 1.0
        while True:
            try:
                async with tractor.open_nursery() as nursery:
                    portal = await nursery.run_in_actor(process_func, **kwargs)
                    _logger.info("Started process")
                    self.process_started = True
                    self.notify_state_changed()
                    await portal.result()
                    _logger.info("Process exited")
            except Exception as e:
                    _logger.info(f"Process threw an error: {e}")
            
            _logger.info(f"Retrying in {seconds_between_retry} seconds")
            await trio.sleep(seconds_between_retry)

    async def run(self, address:str, process_func: typing.Callable, kwargs):
        self.address = address

        _logger.info("Watchdog started. Awaiting connection from the robot. Please ensure the Ethernet cable is connected to the robot.")
        while True:
            self.connected = await ping(self.address, self.seconds_to_ping_timeout)
            while not self.connected:
                await trio.sleep(self.seconds_between_pings)
                _logger.info("Waiting for connection to %s", self.address)
                self.connected = await ping(self.address, self.seconds_to_ping_timeout)
            _logger.info("Connected to %s", self.address)
            self.notify_state_changed()
        
            async with trio.open_nursery() as nursery:
                nursery.start_soon(self.start_and_monitor_process, process_func, kwargs)
                while self.connected:
                    self.connected = await ping(self.address, self.seconds_to_ping_timeout)
                    await trio.sleep(self.seconds_between_pings)
                nursery.cancel_scope.cancel()
                self.process_started = False
                self.notify_state_changed()
                _logger.info("Process disconnected")
                
            _logger.info("Disconnected from %s", self.address)
            self.notify_state_changed()
            
