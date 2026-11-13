"""Step C: navigate on a map saved during Step B.

The launch intentionally starts only the Nav2 servers used in the validated
ComputePathToPose -> FollowPath workflow. It does not start BT Navigator.
No map is bundled: the map argument is required.
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def _validate_map(context):
    map_file = LaunchConfiguration('map').perform(context)
    if not os.path.isabs(map_file) or not os.path.isfile(map_file):
        raise RuntimeError(
            'Step C requires an existing map YAML saved in Step B. '
            'Pass map:=/absolute/path/to/my_map.yaml. '
            f'Not an absolute existing file: {map_file!r}'
        )
    return []


def generate_launch_description():
    share = get_package_share_directory('microroscar_bringup')
    map_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')

    return LaunchDescription([
        DeclareLaunchArgument(
            'map',
            description='Required: absolute path to the map YAML saved in Step B',
        ),
        DeclareLaunchArgument(
            'params_file',
            default_value=os.path.join(share, 'config', 'navigation.yaml'),
            description='Nav2/AMCL parameters',
        ),
        DeclareLaunchArgument(
            'start_agent',
            default_value='true',
            description='Start the micro-ROS UDP agent on port 8090',
        ),
        DeclareLaunchArgument(
            'rviz',
            default_value='true',
            description='Open the packaged navigation RViz view',
        ),
        # Check before starting the Agent, TF broadcasters or Nav2 nodes.
        OpaqueFunction(function=_validate_map),
        Node(
            package='micro_ros_agent',
            executable='micro_ros_agent',
            arguments=['udp4', '--port', '8090', '-v4'],
            condition=IfCondition(LaunchConfiguration('start_agent')),
            output='screen',
        ),
        Node(
            package='microroscar_bringup',
            executable='odom_tf',
            output='screen',
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=[
                '--x', '0', '--y', '0', '--z', '0.10',
                '--roll', '0', '--pitch', '0', '--yaw', '0',
                '--frame-id', 'base_footprint',
                '--child-frame-id', 'laser_frame',
            ],
            output='screen',
        ),
        Node(
            package='nav2_map_server',
            executable='map_server',
            name='map_server',
            parameters=[params_file, {'yaml_filename': map_file}],
            output='screen',
        ),
        Node(
            package='nav2_amcl',
            executable='amcl',
            name='amcl',
            parameters=[params_file],
            output='screen',
        ),
        Node(
            package='nav2_planner',
            executable='planner_server',
            name='planner_server',
            parameters=[params_file],
            output='screen',
        ),
        Node(
            package='nav2_controller',
            executable='controller_server',
            name='controller_server',
            parameters=[params_file],
            output='screen',
        ),
        Node(
            package='nav2_lifecycle_manager',
            executable='lifecycle_manager',
            name='lifecycle_manager_navigation',
            parameters=[{
                'autostart': True,
                'node_names': [
                    'map_server', 'amcl', 'planner_server', 'controller_server',
                ],
            }],
            output='screen',
        ),
        Node(
            package='rviz2',
            executable='rviz2',
            arguments=[
                '-d', os.path.join(share, 'rviz', 'navigation_handoff.rviz'),
            ],
            condition=IfCondition(LaunchConfiguration('rviz')),
            output='screen',
        ),
    ])
