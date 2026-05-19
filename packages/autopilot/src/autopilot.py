#!/usr/bin/env python3

import rospy
from duckietown_msgs.msg import Twist2DStamped
from duckietown_msgs.msg import FSMState
from duckietown_msgs.msg import AprilTagDetectionArray


class Autopilot:

    def __init__(self):

        # Initialize ROS node
        rospy.init_node('autopilot_node', anonymous=True)

        # Robot state
        self.robot_state = "LANE_FOLLOWING"

        # Your Duckiebot name
        self.robot_name = "mybota002417"

        # Shutdown hook
        rospy.on_shutdown(self.clean_shutdown)

        # ==================================================
        # Publishers
        # ==================================================

        self.cmd_vel_pub = rospy.Publisher(
            '/' + self.robot_name + '/car_cmd_switch_node/cmd',
            Twist2DStamped,
            queue_size=1
        )

        self.state_pub = rospy.Publisher(
            '/' + self.robot_name + '/fsm_node/mode',
            FSMState,
            queue_size=1
        )

        # ==================================================
        # Subscriber
        # ==================================================

        rospy.Subscriber(
            '/' + self.robot_name + '/apriltag_detector_node/detections',
            AprilTagDetectionArray,
            self.tag_callback,
            queue_size=1
        )

        rospy.loginfo("Autopilot node started!")

        rospy.spin()

    # ======================================================
    # AprilTag Detection Callback
    # ======================================================

    def tag_callback(self, msg):

        if self.robot_state != "LANE_FOLLOWING":
            return

        self.move_robot(msg.detections)

    # ======================================================
    # Clean Shutdown
    # ======================================================

    def clean_shutdown(self):

        rospy.loginfo("System shutting down. Stopping robot...")
        self.stop_robot()

    # ======================================================
    # Stop Robot
    # ======================================================

    def stop_robot(self):

        cmd_msg = Twist2DStamped()

        cmd_msg.header.stamp = rospy.Time.now()
        cmd_msg.v = 0.0
        cmd_msg.omega = 0.0

        self.cmd_vel_pub.publish(cmd_msg)

    # ======================================================
    # Change FSM State
    # ======================================================

    def set_state(self, state):

        self.robot_state = state

        state_msg = FSMState()

        state_msg.header.stamp = rospy.Time.now()
        state_msg.state = state

        self.state_pub.publish(state_msg)

    # ======================================================
    # Main Robot Logic
    # ======================================================

    def move_robot(self, detections):

        if len(detections) == 0:
            return

        for detection in detections:

            tag_id = detection.tag_id

            rospy.loginfo("Detected Tag ID: {}".format(tag_id))

            # ==========================================
            # LEFT TURN
            # ==========================================

            if tag_id == 48:

                rospy.loginfo("LEFT TURN DETECTED")

                self.set_state("NORMAL_JOYSTICK_CONTROL")

                self.execute_left_turn()

                self.set_state("LANE_FOLLOWING")

            # ==========================================
            # RIGHT TURN
            # ==========================================

            elif tag_id == 50:

                rospy.loginfo("RIGHT TURN DETECTED")

                self.set_state("NORMAL_JOYSTICK_CONTROL")

                self.execute_right_turn()

                self.set_state("LANE_FOLLOWING")

            # ==========================================
            # STOP SIGN
            # ==========================================

            elif tag_id == 163:

                rospy.loginfo("STOP SIGN DETECTED")

                self.set_state("NORMAL_JOYSTICK_CONTROL")

                self.stop_robot()

                rospy.sleep(3)

                self.set_state("LANE_FOLLOWING")

    # ======================================================
    # Execute Left Turn
    # ======================================================

    def execute_left_turn(self):

        cmd = Twist2DStamped()

        cmd.v = 0.25
        cmd.omega = 4.0

        start_time = rospy.Time.now().to_sec()

        while rospy.Time.now().to_sec() - start_time < 1.5:

            cmd.header.stamp = rospy.Time.now()

            self.cmd_vel_pub.publish(cmd)

            rospy.sleep(0.1)

        self.stop_robot()

    # ======================================================
    # Execute Right Turn
    # ======================================================

    def execute_right_turn(self):

        cmd = Twist2DStamped()

        cmd.v = 0.25
        cmd.omega = -4.0

        start_time = rospy.Time.now().to_sec()

        while rospy.Time.now().to_sec() - start_time < 1.5:

            cmd.header.stamp = rospy.Time.now()

            self.cmd_vel_pub.publish(cmd)

            rospy.sleep(0.1)

        self.stop_robot()


# ==========================================================
# Main
# ==========================================================

if __name__ == '__main__':

    try:
        autopilot_instance = Autopilot()

    except rospy.ROSInterruptException:
        pass
