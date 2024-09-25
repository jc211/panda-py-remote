import numpy as np

DEFAULT_CARTESIAN_IMPEDANCE = np.array([
    [800,   0,   0,  0,  0,  0],
    [  0, 800,   0,  0,  0,  0],
    [  0,   0, 800,  0,  0,  0],
    [  0,   0,   0, 40,  0,  0],
    [  0,   0,   0,  0, 40,  0],
    [  0,   0,   0,  0,  0, 40]
], dtype=np.float64)

DEFAULT_JOINT_STIFFNESS = np.array([600, 600, 600, 600, 250, 150, 50], dtype=np.float64)

DEFAULT_DAMPING_DATA = np.array([50, 50, 50, 20, 20, 20, 10], dtype=np.float64)

JOINT_POSITION_START = np.array([
    0.0, -np.pi/4, 0.0,   -3 * np.pi/4, 0.0, np.pi/2,  np.pi/4
])