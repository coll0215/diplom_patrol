import os
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    return LaunchDescription([

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(
                    get_package_share_directory('depthai_ros_driver'),
                    'launch',
                    'camera.launch.py'
                )
            ),
            launch_arguments={
                'camera_model': 'OAK-D-LITE',
                'pointcloud.enable': 'true',
                'use_rviz': 'true'
            }.items()
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0.0', '0.0', '0.0', '0.0', '0.0', '0.0', '1.0',
                       'world', 'base_link'],
            output='screen'
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0.0', '0.0', '1.75', '0.0', '0.0', '1.0', '0.0',
                       'base_link', 'oak-d-base-frame'],
            output='screen'
        ),
    ])
