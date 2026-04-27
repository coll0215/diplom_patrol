import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    parameters=[{
        'frame_id':'oak-d-base-frame',
        'subscribe_rgbd':True,
        'subscribe_odom_info':True,
        'approx_sync':True,
        'wait_imu_to_init':False,
        'queue_size':30
    }]

    remappings=[('imu', '/imu/waveshare_filtered')]

    return LaunchDescription([

        # ============================================
        # 1. КАМЕРА OAK-D LITE
        # ============================================
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
                'pointcloud.enable': 'true',      # depth включен
                'use_rviz': 'true',
                'rectify_rgb': 'true'             # rectified rgb
            }.items()
        ),

        # ============================================
        # 2. СТАТИЧЕСКИЕ ТРАНСФОРМАЦИИ
        # ============================================
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

        # ============================================
        # 3. RTAB-MAP
        # ============================================
        Node(   
            package='rtabmap_sync', 
            executable='rgbd_sync', 
            output='screen',
            parameters=parameters,
            remappings=[
                ('rgb/image', '/oak/rgb/image_rect'),
                ('rgb/camera_info', '/oak/rgb/camera_info'),
                # depth - пока нет, пробуем stereo image
                ('depth/image', '/oak/stereo/image_raw')
            ]
        ),

        Node(
            package='rtabmap_odom', 
            executable='rgbd_odometry', 
            output='screen',
            parameters=parameters,
            remappings=remappings
        ),

        Node(
            package='rtabmap_slam', 
            executable='rtabmap', 
            output='screen',
            parameters=parameters,
            remappings=remappings,
            arguments=['-d']
        ),
    ])
