#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from tf2_ros import StaticTransformBroadcaster
from geometry_msgs.msg import TransformStamped
import yaml
import os

class TagMapPublisher(Node):
    def __init__(self):
        super().__init__('tag_map_publisher')
        
        # Параметры
        self.declare_parameter('tags_file', 'tags_map.yaml')
        self.declare_parameter('world_frame', 'map_vo')
        self.declare_parameter('publish_rate', 1.0)
        self.declare_parameter('static_prefix', 'map_')  
        
        self.tags_file = self.get_parameter('tags_file').value
        self.world_frame = self.get_parameter('world_frame').value
        self.publish_rate = self.get_parameter('publish_rate').value
        self.static_prefix = self.get_parameter('static_prefix').value
        
        self.get_logger().info('Tag map publisher started')
        self.get_logger().info(f'Loading tags from: {self.tags_file}')
        self.get_logger().info(f'Static tag prefix: {self.static_prefix}')
        
        self.static_broadcaster = StaticTransformBroadcaster(self)
        
        self.load_and_publish_tags()
        
        self.create_timer(1.0/self.publish_rate, self.republish_tags)
    
    def load_and_publish_tags(self):
        if not os.path.exists(self.tags_file):
            self.get_logger().error(f'Tags file {self.tags_file} not found!')
            return
        
        try:
            with open(self.tags_file, 'r') as f:
                data = yaml.safe_load(f)
            
            self.tags_data = data
            transforms = []
            
            for tag_frame, tag_data in data['tags'].items():
                if ':' in tag_frame:
                    prefix, tag_id = tag_frame.split(':')
                    static_frame = f"{self.static_prefix}{prefix}:{tag_id}"  
                else:
                    static_frame = f"{self.static_prefix}{tag_frame}"
                
                self.get_logger().info(f'Loading tag: {tag_frame} -> {static_frame}')
                
                t = TransformStamped()
                t.header.stamp = self.get_clock().now().to_msg()
                t.header.frame_id = self.world_frame
                t.child_frame_id = static_frame
                
                # Позиция
                t.transform.translation.x = float(tag_data['position']['x'])
                t.transform.translation.y = float(tag_data['position']['y'])
                t.transform.translation.z = float(tag_data['position']['z'])
                
                # Ориентация
                t.transform.rotation.x = float(tag_data['orientation']['x'])
                t.transform.rotation.y = float(tag_data['orientation']['y'])
                t.transform.rotation.z = float(tag_data['orientation']['z'])
                t.transform.rotation.w = float(tag_data['orientation']['w'])
                
                transforms.append(t)
                
                self.get_logger().info(
                    f'  → Position: ({t.transform.translation.x:.3f}, '
                    f'{t.transform.translation.y:.3f}, '
                    f'{t.transform.translation.z:.3f})'
                )
            
            self.static_broadcaster.sendTransform(transforms)
            self.get_logger().info(f'Published {len(transforms)} static transforms with prefix "{self.static_prefix}"')
            
        except Exception as e:
            self.get_logger().error(f'Failed to load tags: {e}')
    
    def republish_tags(self):
        if hasattr(self, 'tags_data'):
            transforms = []
            for tag_frame, tag_data in self.tags_data['tags'].items():
                if ':' in tag_frame:
                    prefix, tag_id = tag_frame.split(':')
                    static_frame = f"{self.static_prefix}{prefix}:{tag_id}"
                else:
                    static_frame = f"{self.static_prefix}{tag_frame}"
                
                t = TransformStamped()
                t.header.stamp = self.get_clock().now().to_msg()
                t.header.frame_id = self.world_frame
                t.child_frame_id = static_frame
                
                t.transform.translation.x = float(tag_data['position']['x'])
                t.transform.translation.y = float(tag_data['position']['y'])
                t.transform.translation.z = float(tag_data['position']['z'])
                
                t.transform.rotation.x = float(tag_data['orientation']['x'])
                t.transform.rotation.y = float(tag_data['orientation']['y'])
                t.transform.rotation.z = float(tag_data['orientation']['z'])
                t.transform.rotation.w = float(tag_data['orientation']['w'])
                
                transforms.append(t)
            
            self.static_broadcaster.sendTransform(transforms)
            self.get_logger().debug(f'Republished {len(transforms)} transforms')


def main(args=None):
    rclpy.init(args=args)
    node = TagMapPublisher()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('Shutting down...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
