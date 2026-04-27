import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    parameters=[{'frame_id':'oak-d-base-frame',
                 'subscribe_rgbd':True,
                 'subscribe_odom_info':True,
                 'approx_sync':False,
                 'wait_imu_to_init':True}]

    remappings=[('imu', '/imu/waveshare_filtered')]
    
    return LaunchDescription([

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(
                get_package_share_directory('depthai_examples'), 'launch'),
                '/stereo_inertial_node.launch.py']),
            launch_arguments={
                'depth_aligned': 'false',
                'enableRviz': 'false',
                'monoResolution': '400p'
            }.items(),
        ),

        Node(
            package='imu',
            executable='imu_node',
            name='imu_waveshare',
            parameters=[{   
                'port_name': '/dev/ttyUSB0',
                'frame_id': 'base_imu_link'
            }]
        ),
        
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '-0.02', '0', '0', '0', '1.0',
                       'oak-d-base-frame', 'base_imu_link'],
            output='screen'
        ),

        Node(
            package='imu_filter_madgwick', 
            executable='imu_filter_madgwick_node', 
            output='screen',
            parameters=[{
                'use_mag': False,
                'world_frame': 'enu',
                'publish_tf': False,
                'gain': 0.1
            }],
            remappings=[
                ('imu/data_raw', '/imu/data'),
                ('imu/data', '/imu/waveshare_filtered')
            ]
        ),

        Node(   
            package='rtabmap_sync', executable='rgbd_sync', output='screen',
            parameters=parameters,
            remappings=[('rgb/image', '/right/image_rect'),
                        ('rgb/camera_info', '/right/camera_info'),
                        ('depth/image', '/stereo/depth')]),

        Node(
            package='rtabmap_odom', executable='rgbd_odometry', output='screen',
            parameters=parameters,
            remappings=remappings),

        Node(
            package='rtabmap_slam', executable='rtabmap', output='screen',
            parameters=parameters,
            remappings=remappings,
            arguments=['-d']),

        Node(
            package='rtabmap_viz', executable='rtabmap_viz', output='screen',
            parameters=parameters,
            remappings=remappings)
    ])
