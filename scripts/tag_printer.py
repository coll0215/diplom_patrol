#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from tf2_ros import Buffer, TransformListener
import tf2_geometry_msgs
import yaml
import os
from datetime import datetime
from geometry_msgs.msg import PoseStamped
import numpy as np

class TagRecorder(Node):
    def __init__(self):
        super().__init__('tag_recorder')
        
        self.declare_parameter('output_file', 'tags_map.yaml')
        self.declare_parameter('world_frame', 'map_vo')
        self.declare_parameter('camera_frame', 'oak_rgb_camera_optical_frame')
        self.declare_parameter('tag_prefix', 'tag36h11:')
        self.declare_parameter('known_tags', [0, 1, 2, 3, 4, 5, 6]) 
        
        self.output_file = self.get_parameter('output_file').value
        self.world_frame = self.get_parameter('world_frame').value
        self.camera_frame = self.get_parameter('camera_frame').value
        self.tag_prefix = self.get_parameter('tag_prefix').value
        self.known_tags = self.get_parameter('known_tags').value
        
        self.tf_buffer = Buffer()
        self.tf_listener = TransformListener(self.tf_buffer, self)
        
        self.tags = {}
        
        self.get_logger().info('Tag recorder started')
        self.get_logger().info(f'Output file: {self.output_file}')
        self.get_logger().info(f'Map frame: {self.world_frame}')
        self.get_logger().info(f'Camera frame: {self.camera_frame}')
        self.get_logger().info(f'Looking for tags: {[f"{self.tag_prefix}{tid}" for tid in self.known_tags]}')
        
        self.create_timer(2.0, self.check_known_tags)
        
        self.create_timer(10.0, self.save_tags)
    
    def convert_to_serializable(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, dict):
            return {key: self.convert_to_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_to_serializable(item) for item in obj]
        else:
            return obj
        
    def check_known_tags(self):
        
        for tag_id in self.known_tags:
            tag_frame = f"{self.tag_prefix}{tag_id}"
            
            if tag_frame in self.tags:
                continue
                
            if self.tf_buffer.can_transform(self.camera_frame, tag_frame, rclpy.time.Time()):
                self.get_logger().info(f'Found transform for {tag_frame}')
                
                try:
                    tag_to_camera = self.tf_buffer.lookup_transform(
                        self.camera_frame,
                        tag_frame,
                        rclpy.time.Time()
                    )
                    
                    camera_to_world = self.tf_buffer.lookup_transform(
                        self.world_frame,
                        self.camera_frame,
                        rclpy.time.Time()
                    )
                    
                    tag_pose_in_camera = PoseStamped()
                    tag_pose_in_camera.header.frame_id = self.camera_frame
                    tag_pose_in_camera.header.stamp = self.get_clock().now().to_msg()
                    tag_pose_in_camera.pose.position.x = tag_to_camera.transform.translation.x
                    tag_pose_in_camera.pose.position.y = tag_to_camera.transform.translation.y
                    tag_pose_in_camera.pose.position.z = tag_to_camera.transform.translation.z
                    tag_pose_in_camera.pose.orientation = tag_to_camera.transform.rotation
                    
                    tag_pose_in_world = tf2_geometry_msgs.do_transform_pose(
                        tag_pose_in_camera.pose,
                        camera_to_world
                    )
                    
                    self.tags[tag_frame] = self.convert_to_serializable({
                        'id': tag_id,
                        'frame': tag_frame,
                        'position': {
                            'x': tag_pose_in_world.position.x,
                            'y': tag_pose_in_world.position.y,
                            'z': tag_pose_in_world.position.z,
                        },
                        'orientation': {
                            'x': tag_pose_in_world.orientation.x,
                            'y': tag_pose_in_world.orientation.y,
                            'z': tag_pose_in_world.orientation.z,
                            'w': tag_pose_in_world.orientation.w,
                        },
                        'recorded_at': datetime.now().isoformat()
                    })
                    
                    self.get_logger().info(
                        f'Recorded {tag_frame} in world:\n'
                        f'Position: ({tag_pose_in_world.position.x:.3f}, '
                        f'{tag_pose_in_world.position.y:.3f}, '
                        f'{tag_pose_in_world.position.z:.3f})'
                    )
                    
                except Exception as e:
                    self.get_logger().warn(f'Failed to transform {tag_frame}: {e}')
    
    def save_tags(self):
        if not self.tags:
            self.get_logger().info('No tags saved yet')
            return
            
        try:
            data = {
                'world_frame': self.world_frame,
                'camera_frame': self.camera_frame,
                'tags': self.tags,
                'metadata': {
                    'count': len(self.tags),
                    'last_saved': datetime.now().isoformat(),
                }
            }
            
            with open(self.output_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, allow_unicode=True)
            
            self.get_logger().info(f'Saved {len(self.tags)} tags to {self.output_file}')
            
        except Exception as e:
            self.get_logger().error(f'Failed to save: {e}')


def main(args=None):
    rclpy.init(args=args)
    node = TagRecorder()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down...')
        node.save_tags()
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
