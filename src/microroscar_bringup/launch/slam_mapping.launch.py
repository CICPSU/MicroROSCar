import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node

def generate_launch_description():

    pkg_share = get_package_share_directory('microroscar_bringup')
    slam_share = get_package_share_directory('slam_toolbox')

    slam_config = os.path.join(pkg_share, 'config', 'slam.yaml')
    slam_launch = os.path.join(
        slam_share, 'launch', 'online_sync_launch.py'
    )

    odom_tf = Node(
        package='microroscar_bringup',
        executable='odom_tf',
        output='screen'
    )

    lidar_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        arguments=[
            '--x', '0',
            '--y', '0',
            '--z', '0.10',
            '--roll', '0',
            '--pitch', '0',
            '--yaw', '0',
            '--frame-id', 'base_footprint',
            '--child-frame-id', 'laser_frame'
        ],
        output='screen'
    )

    slam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(slam_launch),
        launch_arguments={
            'slam_params_file': slam_config,
            'use_sim_time': 'false'
        }.items()
    )

    return LaunchDescription([
        odom_tf,
        lidar_tf,
        TimerAction(period=3.0, actions=[slam])
    ])
