#!/usr/bin/env python3

# Import Dependencies
import rospy 
from turtlesim.msg import Pose
from std_msgs.msg import Float64
import math

class DistanceReader:
    def __init__(self):
        
        # Initialize the node
        rospy.init_node('turtlesim_distance_node', anonymous=True)

        # Subscriber to turtle pose
        rospy.Subscriber("/turtle1/pose", Pose, self.callback)

        # Publisher for total distance
        self.distance_publisher = rospy.Publisher('/turtle_dist', Float64, queue_size=10)

        rospy.loginfo("Initialized turtlesim distance node!")

        # Store previous position
        self.prev_x = None
        self.prev_y = None

        # Total distance travelled
        self.total_distance = 0.0

        # Keep node running
        rospy.spin()

    def callback(self, msg):
        
        rospy.loginfo("Turtle Position: x=%f y=%f", msg.x, msg.y)

        # First reading (initialize previous position)
        if self.prev_x is None and self.prev_y is None:
            self.prev_x = msg.x
            self.prev_y = msg.y
            return

        # Calculate distance between previous and current position
        dx = msg.x - self.prev_x
        dy = msg.y - self.prev_y
        distance = math.sqrt(dx**2 + dy**2)

        # Add to total distance
        self.total_distance += distance

        # Create and publish message
        dist_msg = Float64()
        dist_msg.data = self.total_distance
        self.distance_publisher.publish(dist_msg)

        rospy.loginfo("Total Distance Travelled: %f", self.total_distance)

        # Update previous position
        self.prev_x = msg.x
        self.prev_y = msg.y


if __name__ == '__main__': 
    try: 
        DistanceReader()
    except rospy.ROSInterruptException: 
        pass
