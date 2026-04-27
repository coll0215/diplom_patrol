import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch.conditions import IfCondition

def generate_launch_description():
    pkg_my_robot = get_package_share_directory('my_robot_package')
    
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    namespace = LaunchConfiguration('namespace', default='a200_0000')
    setup_path = LaunchConfiguration('setup_path', 
        default='/home/igsp-01/coll0215_ws/src/my_robot_package/generated')
    start_rviz = LaunchConfiguration('start_rviz', default='true')
    speed_mask_file = LaunchConfiguration('speed_mask', 
        default='/home/igsp-01/coll0215_ws/src/my_robot_package/maps/speed_mask.yaml')
    
    params_file = LaunchConfiguration('params_file', 
        default=os.path.join(pkg_my_robot, 'config', 'a200', 'filter_common.yaml'))
    
    param_substitutions = {
        'use_sim_time': use_sim_time,
        'yaml_filename': speed_mask_file
    }
    
    
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_my_robot, 'launch', 'simulation.launch.py'])
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'world': 'warehouse',
            'setup_path': setup_path,
            'rviz': 'false',
        }.items()
    )
    
    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_my_robot, 'launch', 'localization.launch.py'])
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'setup_path': setup_path,
            'namespace': namespace,
        }.items()
    )
    
    navigation = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_my_robot, 'launch', 'nav2.launch.py'])
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'setup_path': setup_path,
        }.items()
    )
    
    filter_mask_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='speed_filter_mask_server',
        namespace=namespace,
        parameters=[
            params_file,
            {
                'yaml_filename': speed_mask_file,
                'topic_name': 'speed_filter_mask'
            }
        ],
        output='screen'
    )

    filter_info_server = Node(
        package='nav2_map_server',
        executable='costmap_filter_info_server',
        name='speed_costmap_filter_info_server',
        namespace=namespace,
        parameters=[params_file],
        output='screen'
    )

    filter_lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_speed_zone',
        namespace=namespace,
        parameters=[{'use_sim_time': use_sim_time},
                    {'autostart': True},
                    {'node_names': ['speed_filter_mask_server', 'speed_costmap_filter_info_server']}],
        output='screen'
    )
    
    rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution([pkg_my_robot, 'launch', 'view_navigation.launch.py'])
        ),
        launch_arguments={
            'namespace': namespace,
            'use_sim_time': use_sim_time,
        }.items(),
        condition=IfCondition(start_rviz)
    )
    
    return LaunchDescription([
        DeclareLaunchArgument('use_sim_time', default_value='true'),
        DeclareLaunchArgument('namespace', default_value='a200_0000'),
        DeclareLaunchArgument('setup_path', 
            default_value='/home/igsp-01/coll0215_ws/src/my_robot_package/generated'),
        DeclareLaunchArgument('start_rviz', default_value='true'),
        DeclareLaunchArgument('speed_mask', 
            default_value='/home/igsp-01/coll0215_ws/src/my_robot_package/maps/speed_mask.yaml'),
        DeclareLaunchArgument('params_file', 
            default_value=os.path.join(pkg_my_robot, 'config', 'a200', 'filter_common.yaml')),
        
        gazebo,
        localization,
        filter_mask_server,
        filter_info_server,
        filter_lifecycle_manager,
        navigation,
        rviz
    ])
