from attr import dataclass
import netifaces
import trio
import tractor
import tyro

from panda_py_remote.server.watchdog import Watchdog
from panda_py_remote.server.endpoints import Panda as PandaS

def get_ip_address(interface: str) -> str:
    addresses = netifaces.ifaddresses(interface)
    return addresses[netifaces.AF_INET][0]['addr']

async def run_panda_server(interface: str, robot_ip: str):
    PandaS.get_instance(robot_ip=robot_ip)
    current_address = get_ip_address(interface)
    print(f"Starting Panda server at {current_address}")
    async with tractor.open_root_actor(
        name='panda',
        registry_addrs=[(current_address, 1616)],
        enable_modules=['panda_py_remote.server.endpoints'],
        loglevel='info',
        debug_mode=False
    ):
        await trio.sleep_forever()

@dataclass
class Params:
    interface: tyro.conf.PositionalRequiredArgs[str]
    robot_ip: tyro.conf.Positional[str] = "172.16.0.2"
    seconds_between_pings: float = 1.0
    seconds_to_ping_timeout: float = 0.1

async def main():
    params = tyro.cli(Params)
    watchdog = Watchdog(
        seconds_between_pings=params.seconds_between_pings,
        seconds_to_ping_timeout=params.seconds_to_ping_timeout
    )
    await watchdog.run(
        f"https://{params.robot_ip}/admin/api/first-start", 
        run_panda_server, 
        {
            "interface": params.interface,
            "robot_ip": params.robot_ip
        }
     )
    
if __name__ == "__main__":
    trio.run(main)
