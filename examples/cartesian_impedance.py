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
        print(state)
        x0 = await panda.get_position()
        q0 = await panda.get_orientation()
        
        async with panda.start_cartesian_impedance_controller(control_freq=1000) as ctrl:
            while await ctrl.ok():
                
                x_d = x0.copy()
                x_d[1] += 0.1 * np.sin(ctrl.get_time())
                await ctrl.set_control(x_d, q0)

        
if __name__ == "__main__":
    trio.run(main)
    