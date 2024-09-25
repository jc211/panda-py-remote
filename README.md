<div align="center"><img alt="panda-py Logo" src="https://raw.githubusercontent.com/JeanElsner/panda-py/main/logo.jpg" /></div>

<h1 align="center">panda-py-remote</h1>

[panda_py](https://github.com/JeanElsner/panda-py) made remote! 


## Getting started

To get started, first run `server.py` on a computer connected to the robot:

```sh
# Run the server script with the specified network interface and robot IP
python scripts/server.py [network_interface] [robot_ip]

# Alternatively, if using pixi (https://pixi.sh)
# To install pixi: curl -fsSL https://pixi.sh/install.sh | bash
pixi run server eno1 172.16.0.2
```


Replace `eno1` with the network interface you want to use. You can use `ifconfig` to find available network interfaces.

Next, from any computer that can reach the server, run the client. This library uses asynchronous calls to the robot with `async` and `await`. It leverages the [trio](https://trio.readthedocs.io/en/stable/) event loop and [tractor](https://github.com/goodboy/tractor) for streaming and RPC.

```python
import numpy as np
import trio
from panda_py_remote import Panda

async def main():
    server_ip = "1.1.1.1" # your server's ip here
    panda_username = "username" # your robot's username
    panda_password = "password" # your robot's password
    
    async with Panda(server_ip) as panda:
        await panda.login(panda_username, panda_password)
        await panda.take_control(force=True)
        await panda.unlock()
        await panda.activate_fci()
        await panda.move_to_joint_position(
            [np.array([0.0, -np.pi/4, 0.0, -3*np.pi/4, 0.0, np.pi/2, 0.0])],
        )
        state = await panda.read_once()
        x0 = await panda.get_position()
        q0 = await panda.get_orientation()
        
        async with panda.start_cartesian_impedance_controller(control_freq=1000) as ctrl:
            while await ctrl.ok():
                x_d = x0.copy()
                x_d[1] += 0.1 * np.sin(ctrl.get_time())
                last_state = ctrl.get_state()
                await ctrl.set_control(x_d, q0)

        
if __name__ == "__main__":
    trio.run(main)
```