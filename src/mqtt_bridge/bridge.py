from abc import ABCMeta
from typing import Optional, Type, Dict, Union

import inject
import paho.mqtt.client as mqtt
import rospy
import yaml
import subprocess,os
import signal

from .util import lookup_object, extract_values, populate_instance


def create_bridge(factory: Union[str, "Bridge"], msg_type: Union[str, Type[rospy.Message]], topic_from: str,
                  topic_to: str, frequency: Optional[float] = None, **kwargs) -> "Bridge":
    """ generate bridge instance using factory callable and arguments. if `factory` or `meg_type` is provided as string,
     this function will convert it to a corresponding object.
    """
    if isinstance(factory, str):
        factory = lookup_object(factory)
    if not issubclass(factory, Bridge):
        raise ValueError("factory should be Bridge subclass")
    if isinstance(msg_type, str):
        msg_type = lookup_object(msg_type)
    if not issubclass(msg_type, rospy.Message):
        raise TypeError(
            "msg_type should be rospy.Message instance or its string"
            "reprensentation")
    return factory(
        topic_from=topic_from, topic_to=topic_to, msg_type=msg_type, frequency=frequency, **kwargs)


class Bridge(object, metaclass=ABCMeta):
    """ Bridge base class """
    _mqtt_client = inject.attr(mqtt.Client)
    _serialize = inject.attr('serializer')
    _deserialize = inject.attr('deserializer')
    _extract_private_path = inject.attr('mqtt_private_path_extractor')


class RosToMqttBridge(Bridge):
    """ Bridge from ROS topic to MQTT

    bridge ROS messages on `topic_from` to MQTT topic `topic_to`. expect `msg_type` ROS message type.
    """

    def __init__(self, topic_from: str, topic_to: str, msg_type: rospy.Message, frequency: Optional[float] = None):
        self._topic_from = topic_from
        self._topic_to = self._extract_private_path(topic_to)
        self._last_published = rospy.get_time()
        self._interval = 0 if frequency is None else 1.0 / frequency
        rospy.Subscriber(topic_from, msg_type, self._callback_ros)

    def _callback_ros(self, msg: rospy.Message):
        rospy.loginfo("ROS received from {}".format(self._topic_from))
        now = rospy.get_time()
        if now - self._last_published >= self._interval:
            self._publish(msg)
            self._last_published = now

    def _publish(self, msg: rospy.Message):
        rospy.loginfo("MQTT send from {}".format(self._topic_to))
        # rospy.loginfo(yaml.dump(msg))
        payload = self._serialize(yaml.dump(msg)) # extract_values(msg))
        self._mqtt_client.publish(topic=self._topic_to, payload=payload)


class MqttToRosBridge(Bridge):
    """ Bridge from MQTT to ROS topic

    bridge MQTT messages on `topic_from` to ROS topic `topic_to`. MQTT messages will be converted to `msg_type`.
    """

    def __init__(self, topic_from: str, topic_to: str, msg_type: Type[rospy.Message],
                 frequency: Optional[float] = None, queue_size: int = 10):
        self._topic_from = self._extract_private_path(topic_from)
        self._topic_to = topic_to
        self._msg_type = msg_type
        self._queue_size = queue_size
        self._last_published = rospy.get_time()
        self._interval = None if frequency is None else 1.0 / frequency
        # Adding the correct topic to subscribe to
        self._mqtt_client.subscribe(self._topic_from)
        self._mqtt_client.message_callback_add(
            self._topic_from, self._callback_mqtt)
        
        if self._topic_to != "":
            self._publisher = rospy.Publisher(
                self._topic_to, self._msg_type, queue_size=self._queue_size)

    def _callback_mqtt(self, client: mqtt.Client, userdata: Dict, mqtt_msg: mqtt.MQTTMessage):
        """ callback from MQTT """
        rospy.loginfo("MQTT received from {}".format(mqtt_msg.topic))
        rospy.loginfo(mqtt_msg.payload)
        now = rospy.get_time()

        if mqtt_msg.payload == b'start':
            cmd = "cd ~/ros_workspace/devel && source setup.bash && roslaunch ros_deep_learning detectnet.ros1.launch input:=csi://0 output:=display://0"
            rospy.loginfo(cmd)
            self.proc = subprocess.call(cmd, shell=True, stdout=rospy.loginfo, stderr=rospy.loginfo) #, preexec_fn=os.setsid)
            # print(os.getpid())
            # os.system(cmd)
            # print("second time get pid ")
            # print(os.getpid())
            rospy.loginfo("started!")

        if mqtt_msg.payload == b'stop':
            if self.proc:
                self.proc.terminate()
                self.proc.wait()
                os.killpg(self.proc.pid, signal.SIGTERM) 
                rospy.loginfo("stoped!")
            else:
                rospy.loginfo("no ros to stop...")

        if self._topic_to != "":
            if self._interval is None or now - self._last_published >= self._interval:
                try:
                    ros_msg = self._create_ros_message(mqtt_msg)
                    self._publisher.publish(ros_msg)
                    self._last_published = now
                except Exception as e:
                    rospy.logerr(e)

    def _create_ros_message(self, mqtt_msg: mqtt.MQTTMessage) -> rospy.Message:
        """ create ROS message from MQTT payload """
        # Hack to enable both, messagepack and json deserialization.
        if self._serialize.__name__ == "packb":
            msg_dict = self._deserialize(mqtt_msg.payload, raw=False)
        else:
            msg_dict = self._deserialize(mqtt_msg.payload)
        return populate_instance(msg_dict, self._msg_type())


__all__ = ['create_bridge', 'Bridge', 'RosToMqttBridge', 'MqttToRosBridge']
