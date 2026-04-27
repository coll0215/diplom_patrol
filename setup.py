from setuptools import find_packages, setup
import os
from glob import glob

package_name = 'my_robot_package'

def get_mesh_files():
    mesh_files = []
    for root, dirs, files in os.walk('meshes'):
        for file in files:
            full_path = os.path.join(root, file)
            mesh_files.append(full_path)
    return mesh_files

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(exclude=['test']),
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
        (os.path.join('share', package_name, 'config/robots'), ['config/robots/robot.yaml']),
        (os.path.join('share', package_name, 'config/a200'), glob('config/a200/*.yaml')),
        (os.path.join('share', package_name, 'config/gazebo'), glob('config/gazebo/*.config')),
        (os.path.join('share', package_name, 'rviz'), glob('rviz/*.rviz')),
        (os.path.join('share', package_name, 'maps'), glob('maps/*.*')),
        (os.path.join('share', package_name, 'config'), glob('config/*.yaml')),
        (os.path.join('share', package_name, 'worlds'), glob('worlds/*.sdf')),
    ] + [(os.path.join('share', package_name, os.path.dirname(f)), [f]) for f in get_mesh_files()],
    scripts=['scripts/simple_patrol.py', 'scripts/tag_printer.py', 'scripts/tag_map_publisher.py'], 
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='coll0215',
    maintainer_email='coll0215@todo.todo',
    description='Patrol robot package',
    license='MIT',
    tests_require=['pytest'],
)
