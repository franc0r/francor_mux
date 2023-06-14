import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, qos_profile_sensor_data, qos_profile_system_default

from geometry_msgs.msg import Twist

class FrancorMux(Node):

  def __init__(self):
    super().__init__('map_repub_node')

    self.vel_in_1_topic = "/joy_vel/cmd_vel"
    self.vel_in_1_qos = "sensor_data"

    self.vel_in_2_topic = "/nav_vel/cmd_vel"
    self.vel_in_2_qos = "sensor_data"

    self.vel_in_3_topic = "/todo/cmd_vel"
    self.vel_in_3_qos = "sensor_data"

    self.vel_out_topic = "/cmd_vel"
    self.vel_out_qos = "sensor_data"

    self.rate = 50.0

    self.timeout = 1

    #params

    self.declare_parameter('vel_in_1_topic', self.vel_in_1_topic)
    self.declare_parameter('vel_in_1_qos', self.vel_in_1_qos)
    self.declare_parameter('vel_in_2_topic', self.vel_in_2_topic)
    self.declare_parameter('vel_in_2_qos', self.vel_in_2_qos)
    self.declare_parameter('vel_in_3_topic', self.vel_in_3_topic)
    self.declare_parameter('vel_in_3_qos', self.vel_in_3_qos)
    self.declare_parameter('vel_out_topic', self.vel_out_topic)
    self.declare_parameter('vel_out_qos', self.vel_out_qos)
    self.declare_parameter('rate', 50.0)
    self.declare_parameter('timeout', 1)

    self.vel_in_1_topic = self.get_parameter('vel_in_1_topic').get_parameter_value().string_value
    self.vel_in_1_qos = self.get_parameter('vel_in_1_qos').get_parameter_value().string_value
    self.vel_in_2_topic = self.get_parameter('vel_in_2_topic').get_parameter_value().string_value
    self.vel_in_2_qos = self.get_parameter('vel_in_2_qos').get_parameter_value().string_value
    self.vel_in_3_topic = self.get_parameter('vel_in_3_topic').get_parameter_value().string_value
    self.vel_in_3_qos = self.get_parameter('vel_in_3_qos').get_parameter_value().string_value
    self.vel_out_topic = self.get_parameter('vel_out_topic').get_parameter_value().string_value
    self.vel_out_qos = self.get_parameter('vel_out_qos').get_parameter_value().string_value

    self.rate = self.get_parameter('rate').get_parameter_value().double_value

    self.timeout = self.get_parameter('timeout').get_parameter_value().integer_value

    #print params
    self.get_logger().info("###########################################")
    self.get_logger().info("Parameters: ")
    self.get_logger().info("vel_in_1_topic: " + self.vel_in_1_topic)
    self.get_logger().info("vel_in_1_qos:   " + self.vel_in_1_qos)
    self.get_logger().info("vel_in_2_topic: " + self.vel_in_2_topic)
    self.get_logger().info("vel_in_2_qos:   " + self.vel_in_2_qos)
    self.get_logger().info("vel_in_3_topic: " + self.vel_in_3_topic)
    self.get_logger().info("vel_in_3_qos:   " + self.vel_in_3_qos)
    self.get_logger().info("vel_out_topic:  " + self.vel_out_topic)
    self.get_logger().info("vel_out_qos:    " + self.vel_out_qos)
    self.get_logger().info("rate:           " + str(self.rate))
    self.get_logger().info("timeout:        " + str(self.timeout))
    self.get_logger().info("###########################################")

    #subs
    qos = qos_profile_system_default
    if self.vel_in_1_qos == "sensor_data":
      qos = qos_profile_sensor_data
    self.sub_vel_in_1 = self.create_subscription(Twist, self.vel_in_1_topic, self.vel_in_1_callback, qos)

    qos = qos_profile_system_default
    if self.vel_in_2_qos == "sensor_data":
      qos = qos_profile_sensor_data
    self.sub_vel_in_2 = self.create_subscription(Twist, self.vel_in_2_topic, self.vel_in_2_callback, qos)

    qos = qos_profile_system_default
    if self.vel_in_3_qos == "sensor_data":
      qos = qos_profile_sensor_data
    self.sub_vel_in_3 = self.create_subscription(Twist, self.vel_in_3_topic, self.vel_in_3_callback, qos)

    #pub
    qos = qos_profile_system_default
    if self.vel_out_qos == "sensor_data":
      qos = qos_profile_sensor_data
    self.pub_vel_out = self.create_publisher(Twist, self.vel_out_topic, qos)

    #timer
    self.timer = self.create_timer(1.0/self.rate, self.timer_callback)


    self.last_vel_in_1 = Twist()
    self.time_vel_in_1 = self.get_clock().now()
    self.last_vel_in_2 = Twist()
    self.time_vel_in_2 = self.get_clock().now()
    self.last_vel_in_3 = Twist()
    self.time_vel_in_3 = self.get_clock().now()

  def timer_callback(self):
    #check all last vels and times publish the histes prio only with recent msg
    if (self.get_clock().now() - self.time_vel_in_1).to_msg().sec < self.timeout:
      self.pub_vel_out.publish(self.last_vel_in_1)
    elif (self.get_clock().now() - self.time_vel_in_2).to_msg().sec < self.timeout:
      self.pub_vel_out.publish(self.last_vel_in_2)
    elif (self.get_clock().now() - self.time_vel_in_3).to_msg().sec < self.timeout:
      self.pub_vel_out.publish(self.last_vel_in_3)
    else:
      #empty msg
      self.pub_vel_out.publish(Twist())


  def vel_in_1_callback(self, msg: Twist):
    self.last_vel_in_1 = msg
    self.time_vel_in_1 = self.get_clock().now()
  
  def vel_in_2_callback(self, msg: Twist):
    self.last_vel_in_2 = msg
    self.time_vel_in_2 = self.get_clock().now()

  def vel_in_3_callback(self, msg: Twist):
    self.last_vel_in_3 = msg
    self.time_vel_in_3 = self.get_clock().now()




def main(args=None):
  rclpy.init(args=args)

  mux_node = FrancorMux()

  try:
    rclpy.spin(mux_node)
  except KeyboardInterrupt:
    pass

  mux_node.destroy_node()
  rclpy.shutdown()


if __name__ == '__main__':
  main()