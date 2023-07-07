# 1 启动 usb camera

```bash
cd /home/nvidia/usb_cam_ws/devel && source setup.bash && roslaunch usb_cam usb_cam-test.launch
```

# 2 启动标记程序

```bash
rosrun camera_calibration cameracalibrator.py --size 8x6 --square 0.024 image:=/usb_cam/image_raw camera:=/usb_cam
# 标记图片地址
# https://img-blog.csdnimg.cn/20190417091331789.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2N1bmd1ZGFmYQ==,size_16,color_FFFFFF,t_70
```

# ------------------非必须-------------------------

# 在 /home/nvidia/apriltag_ws/src/apriltag_ros/apriltag_ros/launch/continuous_detection.launch 中添加 tag_sizes

```xml
<launch>
  <!-- set to value="gdbserver localhost:10000" for remote debugging -->
  <arg name="launch_prefix" default="" />

  <!-- configure camera input -->
  <arg name="camera_name" default="/camera_rect" />
  <arg name="image_topic" default="image_rect" />
  <arg name="queue_size" default="1" />

  <!-- apriltag_ros continuous detection node -->
  <node pkg="apriltag_ros" type="apriltag_ros_continuous_node" name="apriltag_ros_continuous_node" clear_params="true" output="screen" launch-prefix="$(arg launch_prefix)">
    <!-- Remap topics from those used in code to those on the ROS network -->
    <remap from="image_rect" to="$(arg camera_name)/$(arg image_topic)" />
    <remap from="camera_info" to="$(arg camera_name)/camera_info" />

    <param name="publish_tag_detections_image" type="bool" value="true" /><!-- default: false -->
    <param name="queue_size" type="int" value="$(arg queue_size)" />

    <!-- load parameters (incl. tag family, tags, etc.) -->
    <rosparam command="load" file="$(find apriltag_ros)/config/settings.yaml"/>
    <rosparam command="load" file="$(find apriltag_ros)/config/tags.yaml"/>

    <!-- 添加下面一行 -->
    <param name="tag_sizes" type="string" value="$(find apriltag_ros)/config/config.yaml"/>
  </node>
</launch>
```

# 将目录内的 2 个文件上传到 /home/nvidia/apriltag_ws/src/apriltag_ros/apriltag_ros/config
