import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, OpaqueFunction
from launch.actions import IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node


ARGUMENTS = [
    DeclareLaunchArgument('use_sim_time', default_value='true',
                          choices=['true', 'false'],
                          description='use_sim_time'),
    DeclareLaunchArgument('world', default_value='warehouse',
                          description='Gazebo World'),
    DeclareLaunchArgument('auto_start', default_value='true',
                          choices=['true', 'false'],
                          description='Auto-start Gazebo simulation'),
]


def gz_launch(context, *args, **kwargs):

    pkg_my_robot = get_package_share_directory('my_robot_package')
    pkg_ros_gz_sim = get_package_share_directory('ros_gz_sim')

    gz_sim_launch = PathJoinSubstitution(
        [pkg_ros_gz_sim, 'launch', 'gz_sim.launch.py'])

    # ИСПРАВЛЕНО: путь к gui.config в твоём пакете
    gui_config = PathJoinSubstitution(
        [pkg_my_robot, 'config', 'gazebo', 'gui.config'])

    auto_start_option = ''
    auto_start = LaunchConfiguration('auto_start').perform(context)
    if (auto_start == 'true'):
        auto_start_option = ' -r'

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([gz_sim_launch]),
        launch_arguments=[
            ('gz_args', [LaunchConfiguration('world'),
                         '.sdf',
                         auto_start_option,
                         ' -v 4',
                         ' --gui-config ',
                         gui_config])
        ]
    )

    return [gz_sim]


def generate_launch_description():

    pkg_my_robot = get_package_share_directory('my_robot_package')

    packages_paths = [os.path.join(p, 'share') for p in os.getenv('AMENT_PREFIX_PATH').split(':')]

    gz_sim_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH',
        value=[
            os.path.join(pkg_my_robot, 'worlds') + ':',
            os.path.join(pkg_my_robot, 'meshes') + ':',
            ':' + ':'.join(packages_paths)])

    clock_bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        name='clock_bridge',
        output='screen',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock'
        ]
    )

    ld = LaunchDescription(ARGUMENTS)
    ld.add_action(gz_sim_resource_path)
    ld.add_action(OpaqueFunction(function=gz_launch))
    ld.add_action(clock_bridge)
    return ld
