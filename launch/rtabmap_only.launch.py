from launch import LaunchDescription
from launch_ros.actions import Node

def generate_launch_description():
    return LaunchDescription([
        Node(
            package='rtabmap_odom',
            executable='rgbd_odometry',
            name='rgbd_odometry',
            output='screen',
            parameters=[{
                'frame_id': 'oak_rgb_camera_frame',
                'odom_frame_id': 'odom',
                'publish_tf': True,
                'approx_sync': False,
                'approx_sync_max_interval': 0.05,  
                'queue_size': 30,
                'wait_for_transform': 0.5,
                
                'rgbd_odometry': {
                    'Odom/Strategy': '1',
                    'Odom/FilteringStrategy': '1',
                    'Odom/InlierDistance': 0.1,
                    'Odom/MinInliers': 5,          
                    'Odom/FeatureType': '6',
                    'Odom/FeatureCount': 1500,
                    'Odom/Guided': 'true',
                    'Vis/CorType': '1',
                    'Vis/FlowWinSize': 21,
                    'Vis/FlowMaxLevel': 4,
                    'Vis/FeatureType': '6',
                    'Vis/FeatureCount': 1500,
                }
            }],
            remappings=[
                ('rgb/image', '/oak/rgb/image_raw'),
                ('rgb/camera_info', '/oak/rgb/camera_info'),
                ('depth/image', '/oak/stereo/image_raw'),
            ]
        ),
        
        # Статические трансформации
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 'odom', 'oak_rgb_camera_frame']
        ),
        Node(
            package='tf2_ros',
            executable='static_transform_publisher',
            arguments=['0', '0', '0', '0', '0', '0', 
                       'oak_rgb_camera_frame', 'oak_rgb_camera_optical_frame']
        ),
    ])
