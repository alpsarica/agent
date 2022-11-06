
import paho.mqtt.client as mqtt
import paho.mqtt.packettypes as packettypes
import time
import json 

import rospy
import rostopic

# Supported message types for ECHO
from ackermann_msgs.msg import *
from diagnostic_msgs.msg import *
from geometry_msgs.msg import *
from nav_msgs.msg import *
from sensor_msgs.msg import *
from std_msgs.msg import *
from tf2_msgs.msg import *
from rosgraph_msgs import *
# from tf2_geometry_msgs.msg import *
# from tf2_sensor_msgs.msg import *

from muto_msgs.srv import *
from muto_msgs.msg import *

  
import agent.ros.converter.json_message_converter as  jconv

class TopicEcho(object):

    def __init__(self, manifest, twin, mqtt_client):
        
        self.topic = manifest.get("topic")
        self.target = manifest.get("target")
        self.filter = manifest.get("filter")
        self.count = manifest.get("count")
        self.action =  manifest.get("action")
        self.mqtt_client = mqtt_client
        self.twin = twin
        self._manifest = manifest
        
        if not manifest.get("rate", "5000") is None:
            self.rate = float(manifest.get("rate", "5000"))
        
        self.lastpublish = time.time()
        
        try:
            ttype, tname,_x = rostopic.get_topic_type(self.topic)
            self.topic = tname
            self.topicType = ttype
        except Exception as e:
            print("Topic is malformed {}".format(e))
            self.topic = manifest.get("topic")
           
        self.sub = None
                
    @property
    def manifest(self):
        return self._manifest

    
    def subscribe(self):
        self.topic_type =  eval(self.topicType.split("/")[1])
        self.sub = rospy.Subscriber(self.topic,
                                    self.topic_type, 
                                    self.on_topic_callback,
                                    queue_size=1)

    def register(self):
        self.twin.save_telemetry(self)

 
    def delete(self):
        self.stop()
        self.twin.delete_telemetry(self)

            
    def start(self):
        self.lastpublish = 0
        self.register()
        self.subscribe()
        
    def stop(self):
        if not self.sub is None:
            self.sub.unregister()
            self.sub = None

            
    def on_topic_callback(self, msg):
        if msg:
            current = time.time()
            diff = (current - self.lastpublish)*1000
            if diff > self.rate:
                self.lastpublish = current
                reply = jconv.convert_ros_message_to_json(msg)
                if not self.target is None and not reply is None:
                    properties= mqtt.Properties(packettypes.PacketTypes.PUBLISH)
                    properties.CorrelationData= bytearray(self.target["correlation"],"utf8")
                    #respond
                    self.mqtt_client.publish(self.target["topic"],reply,properties=properties)
                
