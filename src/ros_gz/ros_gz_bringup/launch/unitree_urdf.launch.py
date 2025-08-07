from launch import LaunchDescription
from launch.actions import ExecuteProcess
from launch_ros.actions import Node
import os

def generate_launch_description():

    urdf_file = "/home/jiawen/h12project_ws/src/ros_gz/ros_gz_description/models/unitree_h1_2/unitree_h1_2.urdf"

    return LaunchDescription([
        # 启动 Gazebo
        ExecuteProcess(
            cmd=['ign', 'gazebo', '-v', '4', '-r', 'empty.sdf'],
            output='screen'
        ),

        # 发布 TF 和 joint states
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            arguments=[urdf_file]
        ),

        # 插入模型进 Gazebo
        Node(
            package='ros_gz_sim',
            executable='create',
            arguments=['-name', 'unitree_h1_2', '-file', urdf_file, '-z', '1.0'],
            output='screen'
        )
    ])

