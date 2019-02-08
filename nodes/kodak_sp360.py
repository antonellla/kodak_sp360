#!/usr/bin/env python
# Simple ROS node for grabbing images over an MJPEG stream from a Kodak SP360 camera.
#
# Needs: re-connecting to camera URL after wi-fi disconnect

import rospy
import urllib
from sensor_msgs.msg import Image
import cv2
import numpy as np
from cv_bridge import CvBridge


class Kodak360Streamer:
    '''Grabs MJPEG stream from Kodak SP360 URL, parses images as cv images,
       converts cv images to ROS images and publishes them on a ROS topic.'''

    def __init__(self, hostname, port):
        self.hostname = hostname
        self.port = port
        self.cam_url = 'http://' + hostname + ':' + str(port)

        self.image_pub = rospy.Publisher('/kodak/image', Image, queue_size=1)
        self.bridge = CvBridge()

        # Open MJPEG stream from camera at default URL
        rospy.loginfo("Connecting to camera...")
        self.camera_stream = urllib.urlopen(self.cam_url)
        rospy.loginfo("Camera connected.")

        jpg_start = '\xff\xd8'
        jpg_end = '\xff\xd9'

        bytes = ''
        while not rospy.is_shutdown():
            bytes += self.camera_stream.read(1024)
            a = bytes.find(jpg_start)
            b = bytes.find(jpg_end)

            if a != -1 and b != -1:
                jpg = bytes[a:b+2]
                bytes = bytes[b+2:]
                cv_img = cv2.imdecode(np.fromstring(jpg, dtype=np.uint8), cv2.IMREAD_COLOR)

                # Convert CV image to ROS image and publish to topic
                ros_img = self.bridge.cv2_to_imgmsg(cv_img, "bgr8")
                self.image_pub.publish(ros_img)



def main():
    '''Creates ROS node for grabbing images from MJPEG stream from
    Kodak SP360 camera, and publishing on a ROS topic.'''

    rospy.init_node("kodak_sp360_streamer")

    args = { 'hostname': '172.16.0.254',
             'port': 9176}

    kodak_sp360 = Kodak360Streamer(**args)

    rospy.spin()


if __name__ == "__main__":
    main()
