import enum
from sys import orig_argv
from turtle import position
import msgspec
import msgspec

class Errors(msgspec.Struct):
    cartesian_motion_generator_acceleration_discontinuity: bool = False
    cartesian_motion_generator_elbow_limit_violation: bool = False
    cartesian_motion_generator_elbow_sign_inconsistent: bool = False
    cartesian_motion_generator_joint_acceleration_discontinuity: bool = False
    cartesian_motion_generator_joint_position_limits_violation: bool = False
    cartesian_motion_generator_joint_velocity_discontinuity: bool = False
    cartesian_motion_generator_joint_velocity_limits_violation: bool = False
    cartesian_motion_generator_start_elbow_invalid: bool = False
    cartesian_motion_generator_velocity_discontinuity: bool = False
    cartesian_motion_generator_velocity_limits_violation: bool = False
    cartesian_position_limits_violation: bool = False
    cartesian_position_motion_generator_invalid_frame: bool = False
    cartesian_position_motion_generator_start_pose_invalid: bool = False
    cartesian_reflex: bool = False
    cartesian_velocity_profile_safety_violation: bool = False
    cartesian_velocity_violation: bool = False
    communication_constraints_violation: bool = False
    controller_torque_discontinuity: bool = False
    force_control_safety_violation: bool = False
    force_controller_desired_force_tolerance_violation: bool = False
    instability_detected: bool = False
    joint_motion_generator_acceleration_discontinuity: bool = False
    joint_motion_generator_position_limits_violation: bool = False
    joint_motion_generator_velocity_discontinuity: bool = False
    joint_motion_generator_velocity_limits_violation: bool = False
    joint_move_in_wrong_direction: bool = False
    joint_p2p_insufficient_torque_for_planning: bool = False
    joint_position_limits_violation: bool = False
    joint_position_motion_generator_start_pose_invalid: bool = False
    joint_reflex: bool = False
    joint_velocity_violation: bool = False
    max_goal_pose_deviation_violation: bool = False
    max_path_pose_deviation_violation: bool = False
    power_limit_violation: bool = False
    self_collision_avoidance_violation: bool = False
    start_elbow_sign_inconsistent: bool = False
    tau_j_range_violation: bool = False
    
    @staticmethod
    def from_dict(msg):
        return Errors(
            cartesian_motion_generator_acceleration_discontinuity=msg["cartesian_motion_generator_acceleration_discontinuity"],
            cartesian_motion_generator_elbow_limit_violation=msg["cartesian_motion_generator_elbow_limit_violation"],
            cartesian_motion_generator_elbow_sign_inconsistent=msg["cartesian_motion_generator_elbow_sign_inconsistent"],
            cartesian_motion_generator_joint_acceleration_discontinuity=msg["cartesian_motion_generator_joint_acceleration_discontinuity"],
            cartesian_motion_generator_joint_position_limits_violation=msg["cartesian_motion_generator_joint_position_limits_violation"],
            cartesian_motion_generator_joint_velocity_discontinuity=msg["cartesian_motion_generator_joint_velocity_discontinuity"],
            cartesian_motion_generator_joint_velocity_limits_violation=msg["cartesian_motion_generator_joint_velocity_limits_violation"],
            cartesian_motion_generator_start_elbow_invalid=msg["cartesian_motion_generator_start_elbow_invalid"],
            cartesian_motion_generator_velocity_discontinuity=msg["cartesian_motion_generator_velocity_discontinuity"],
            cartesian_motion_generator_velocity_limits_violation=msg["cartesian_motion_generator_velocity_limits_violation"],
            cartesian_position_limits_violation=msg["cartesian_position_limits_violation"],
            cartesian_position_motion_generator_invalid_frame=msg["cartesian_position_motion_generator_invalid_frame"],
            cartesian_position_motion_generator_start_pose_invalid=msg["cartesian_position_motion_generator_start_pose_invalid"],
            cartesian_reflex=msg["cartesian_reflex"],
            cartesian_velocity_profile_safety_violation=msg["cartesian_velocity_profile_safety_violation"],
            cartesian_velocity_violation=msg["cartesian_velocity_violation"],
            communication_constraints_violation=msg["communication_constraints_violation"],
            controller_torque_discontinuity=msg["controller_torque_discontinuity"],
            force_control_safety_violation=msg["force_control_safety_violation"],
            force_controller_desired_force_tolerance_violation=msg["force_controller_desired_force_tolerance_violation"],
            instability_detected=msg["instability_detected"],
            joint_motion_generator_acceleration_discontinuity=msg["joint_motion_generator_acceleration_discontinuity"],
            joint_motion_generator_position_limits_violation=msg["joint_motion_generator_position_limits_violation"],
            joint_motion_generator_velocity_discontinuity=msg["joint_motion_generator_velocity_discontinuity"],
            joint_motion_generator_velocity_limits_violation=msg["joint_motion_generator_velocity_limits_violation"],
            joint_move_in_wrong_direction=msg["joint_move_in_wrong_direction"],
            joint_p2p_insufficient_torque_for_planning=msg["joint_p2p_insufficient_torque_for_planning"],
            joint_position_limits_violation=msg["joint_position_limits_violation"],
            joint_position_motion_generator_start_pose_invalid=msg["joint_position_motion_generator_start_pose_invalid"],
            joint_reflex=msg["joint_reflex"],
            joint_velocity_violation=msg["joint_velocity_violation"],
            max_goal_pose_deviation_violation=msg["max_goal_pose_deviation_violation"],
            max_path_pose_deviation_violation=msg["max_path_pose_deviation_violation"],
            power_limit_violation=msg["power_limit_violation"],
            self_collision_avoidance_violation=msg["self_collision_avoidance_violation"],
            start_elbow_sign_inconsistent=msg["start_elbow_sign_inconsistent"],
            tau_j_range_violation=msg["tau_j_range_violation"]
        )

class RobotMode(enum.Enum):
    kOther = 0
    kIdle = 1
    kMove = 2
    kGuiding = 3
    kReflex = 4
    kUserStopped = 5
    kAutomaticErrorRecovery = 6

class Duration(msgspec.Struct):
    seconds: int
    nanoseconds: int

class RobotState(msgspec.Struct):
    EE_T_K: list[float]
    F_T_EE: list[float]
    F_x_Cee: list[float]
    F_x_Cload: list[float]
    F_x_Ctotal: list[float]
    I_ee: list[float]
    I_load: list[float]
    I_total: list[float]
    K_F_ext_hat_K: list[float]
    O_F_ext_hat_K: list[float]
    O_T_EE: list[float]
    O_T_EE_c: list[float]
    O_T_EE_d: list[float]
    O_dP_EE_c: list[float]
    O_dP_EE_d: list[float]
    O_ddP_EE_c: list[float]
    cartesian_collision: list[float]
    cartesian_contact: list[float]
    control_command_success_rate: float
    current_errors: Errors
    ddelbow_c: list[float]
    ddq_d: list[float]
    delbow_c: list[float]
    dq: list[float]
    dq_d: list[float]
    dtau_J: list[float]
    dtheta: list[float]
    elbow: list[float]
    elbow_c: list[float]
    elbow_d: list[float]
    joint_collision: list[float]
    joint_contact: list[float]
    last_motion_errors: Errors
    m_ee: float
    m_load: float
    m_total: float
    q: list[float]
    q_d: list[float]
    robot_mode: RobotMode
    tau_J: list[float]
    tau_J_d: list[float]
    tau_ext_hat_filtered: list[float]
    theta: list[float]
    time: float
    
    @staticmethod
    def from_dict(msg):
        return RobotState(
            EE_T_K=msg["EE_T_K"],
            F_T_EE=msg["F_T_EE"],
            F_x_Cee=msg["F_x_Cee"],
            F_x_Cload=msg["F_x_Cload"],
            F_x_Ctotal=msg["F_x_Ctotal"],
            I_ee=msg["I_ee"],
            I_load=msg["I_load"],
            I_total=msg["I_total"],
            K_F_ext_hat_K=msg["K_F_ext_hat_K"],
            O_F_ext_hat_K=msg["O_F_ext_hat_K"],
            O_T_EE=msg["O_T_EE"],
            O_T_EE_c=msg["O_T_EE_c"],
            O_T_EE_d=msg["O_T_EE_d"],
            O_dP_EE_c=msg["O_dP_EE_c"],
            O_dP_EE_d=msg["O_dP_EE_d"],
            O_ddP_EE_c=msg["O_ddP_EE_c"],
            cartesian_collision=msg["cartesian_collision"],
            cartesian_contact=msg["cartesian_contact"],
            control_command_success_rate=msg["control_command_success_rate"],
            current_errors=Errors().from_dict(msg["current_errors"]),
            ddelbow_c=msg["ddelbow_c"],
            ddq_d=msg["ddq_d"],
            delbow_c=msg["delbow_c"],
            dq=msg["dq"],
            dq_d=msg["dq_d"],
            dtau_J=msg["dtau_J"],
            dtheta=msg["dtheta"],
            elbow=msg["elbow"],
            elbow_c=msg["elbow_c"],
            elbow_d=msg["elbow_d"],
            joint_collision=msg["joint_collision"],
            joint_contact=msg["joint_contact"],
            last_motion_errors=Errors().from_dict(msg["last_motion_errors"]),
            m_ee=msg["m_ee"],
            m_load=msg["m_load"],
            m_total=msg["m_total"],
            q=msg["q"],
            q_d=msg["q_d"],
            robot_mode=RobotMode(msg["robot_mode"]),
            tau_J=msg["tau_J"],
            tau_J_d=msg["tau_J_d"],
            tau_ext_hat_filtered=msg["tau_ext_hat_filtered"],
            theta=msg["theta"],
            time=msg["time"]
        )