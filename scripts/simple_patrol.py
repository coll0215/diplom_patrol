#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
import math

class SimplePatrol(Node):
    def __init__(self):
        super().__init__('simple_patrol')
        
        self.waypoints = [
            (0.0, 0.0, 0.0, 1.0),                    
            (-12.57, -12.29, -0.7076278259456135, 0.7065853522027503),
            (0.2, -23.6, 0.007742698271014021, 0.9999700248624875),
            (10.21, -7.47, 0.7077610809732061, 0.70645187540245),
            (-12.9, 18.92, 0.6600577903266339, 0.7512148250860877),
            (0.0, 0.0, 0.0, 1.0),                    
        ]
        
        self.current_wp = 0
        self.action_client = ActionClient(
            self, 
            NavigateToPose, 
            '/a200_0000/navigate_to_pose'
        )
        
        self.get_logger().info('Patrol started, waiting for action server...')
        self.action_client.wait_for_server()
        self.send_next_goal()
    
    def send_next_goal(self):
        if self.current_wp >= len(self.waypoints):
            self.current_wp = 1  
            
        x, y, oz, ow = self.waypoints[self.current_wp]
        
        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = x
        goal_msg.pose.pose.position.y = y
        goal_msg.pose.pose.orientation.z = oz
        goal_msg.pose.pose.orientation.w = ow
        
        self.get_logger().info(f'Sending goal {self.current_wp+1}: ({x:.2f}, {y:.2f})')
        
        send_goal_future = self.action_client.send_goal_async(
            goal_msg,
            feedback_callback=self.feedback_callback
        )
        send_goal_future.add_done_callback(self.goal_response_callback)
    
    def goal_response_callback(self, future):
        goal_handle = future.result()
        if not goal_handle.accepted:
            self.get_logger().error('Goal rejected')
            return
        
        self.get_logger().info('Goal accepted')
        result_future = goal_handle.get_result_async()
        result_future.add_done_callback(self.result_callback)
    
    def result_callback(self, future):
        result = future.result().result
        self.get_logger().info(f'Goal reached!')
        self.current_wp += 1
        self.send_next_goal()
    
    def feedback_callback(self, feedback_msg):
        pass

def main():
    rclpy.init()
    node = SimplePatrol()
    rclpy.spin(node)

if __name__ == '__main__':
    main()
