import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource

def generate_launch_description():
    rtabmap_common_params = [{'frame_id':'base_link',
                 'subscribe_rgbd':True,
                 'subscribe_odom_info':True,
                 'approx_sync':False,
                 'publish_tf': True,
                 'wait_imu_to_init':True}]
    
  
    remappings = [
        ('imu', '/imu/data_filtered'),
        ('odom', '/odom_vo'),
    ]
    
    return LaunchDescription([

        IncludeLaunchDescription(
            PythonLaunchDescriptionSource([os.path.join(
                get_package_share_directory('depthai_examples'), 'launch'),
                '/stereo_inertial_node.launch.py']),
            launch_arguments={
                'depth_aligned': 'false',
                'enableRviz': 'true',
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
            arguments=['0', '0', '1.65', '0', '0', '0',
                       'base_link', 'base_imu_link'],
            output='screen'
        ),

        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0.0', '0.0', '1.75', '0.0', '0.0', '0.0',
                       'base_link', 'oak-d-base-frame'],
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
                ('imu/data', '/imu/data_filtered'),
            ]
        ),

        Node(   
            package='rtabmap_sync', executable='rgbd_sync', output='screen',
            parameters=rtabmap_common_params,
            remappings=[('rgb/image', '/right/image_rect'),
                        ('rgb/camera_info', '/right/camera_info'),
                        ('depth/image', '/stereo/depth')]),

        Node(
            package='rtabmap_odom',
            executable='rgbd_odometry',
            name='rgbd_odometry',
            output='screen',
            parameters=rtabmap_common_params + [{'odom_frame_id': 'odom_vo'}],
            remappings=[
                ('imu', '/imu/data_filtered'),
                ('odom', '/odom_vo'),
            ]
        ),

        Node(
            package='rtabmap_slam',
            executable='rtabmap',
            name='rtabmap',
            output='screen',
            parameters=rtabmap_common_params + [{'odom_frame_id': 'odom_vo', 'map_frame_id': 'map_vo'}],
            remappings=remappings,
            arguments=['--delete_db_on_start']   
        ),

        Node(
            package='rtabmap_viz',
            executable='rtabmap_viz',
            output='screen',
            parameters=rtabmap_common_params,
            remappings=remappings
        )
    ])