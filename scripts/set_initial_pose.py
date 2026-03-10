#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseWithCovarianceStamped
from tf_transformations import quaternion_from_euler
import time

class InitialPoseSetter(Node):
    def __init__(self):
        super().__init__('initial_pose_setter')
        
        self.declare_parameter('namespace', 'a200_0000')
        self.declare_parameter('x', 0.0)
        self.declare_parameter('y', 0.0)
        self.declare_parameter('yaw', 0.0)
        
        namespace = self.get_parameter('namespace').value
        self.x = self.get_parameter('x').value
        self.y = self.get_parameter('y').value
        self.yaw = self.get_parameter('yaw').value
        
        self.initial_pose_topic = f'/{namespace}/initialpose'
        self.pub = self.create_publisher(PoseWithCovarianceStamped, self.initial_pose_topic, 10)
        
        # Публикуем несколько раз с интервалом
        self.timer = self.create_timer(2.0, self.publish_pose)
        self.count = 0
        self.max_publishes = 5
        
    def publish_pose(self):
        if self.count < self.max_publishes:
            msg = PoseWithCovarianceStamped()
            msg.header.frame_id = 'map'
            msg.header.stamp = self.get_clock().now().to_msg()
            
            msg.pose.pose.position.x = self.x
            msg.pose.pose.position.y = self.y
            msg.pose.pose.position.z = 0.0
            
            q = quaternion_from_euler(0, 0, self.yaw)
            msg.pose.pose.orientation.x = q[0]
            msg.pose.pose.orientation.y = q[1]
            msg.pose.pose.orientation.z = q[2]
            msg.pose.pose.orientation.w = q[3]
            
            msg.pose.covariance = [0.1]*36
            
            self.pub.publish(msg)
            self.get_logger().info(f'Published initial pose {self.count+1}/{self.max_publishes}')
            self.count += 1
        else:
            self.timer.cancel()
            self.get_logger().info('Done setting initial pose')

def main():
    rclpy.init()
    node = InitialPoseSetter()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
