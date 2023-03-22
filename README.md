## Demo

```bash
cd ~
mkdir -p ./mqtt_ws/src
cd mqtt_ws/src
git clone https://github.com/integemjack/mqtt
cd mqtt
sudo apt install python3-pip -y
sudo apt install ros-melodic-rosbridge-library -y
pip3 install -r dev-requirements.txt
sudo pip3 install -r dev-requirements.txt
cd ~/mqtt_ws
catkin_make
cd devel
source setup.bash
pip3 install rospkg
chmod +x -R ~/mqtt_ws
```

# 启动

## 测试

```bash

roslaunch ros_deep_learning detectnet.ros1.launch input:=csi://0 output:=display://0
# 启动detectnet后打开新的终端运行下面测试信息，看是否可以收到返回的参数

rostopoc list  # 查看可以订阅哪些内容
rostopic echo /detectnet/detections  # 订阅detectnet返回的detections
```

## 终端 1

```bash
roslaunch mqtt_bridge demo.launch # 运行后会将detectnet的参数通过mqtt发给服务器，topic为car
```

## 终端 2

```bash
mosquitto_sub -t '#'
```

# 发送指令输出指令

## 终端 3

```bash
rostopic pub /echo std_msgs/String "data: 'hello'"
rostopic pub /ping std_msgs/Bool "data: true"
```

# 启动 detectnet 方法

```bash
mosquitto_pub -t 'car' -m 'start' # 启动
mosquitto_pub -t 'car' -m 'stop'  # 关闭
```

# vnc server

```bash
sudo apt install x11vnc
x11vnc -passwd gy666661 -display :0 -forever
```

# apriltag

```
# 安装opencv
cd ~
#wget https://www.raoyunsoft.com/opencv/opencv-3.4.16/opencv-3.4.16.zip
#unzip opencv-3.4.16.zip
https://github.com/opencv/opencv/archive/refs/tags/3.4.16.zip
unzip 3.4.16.zip
cd opencv-3.4.16
mkdir build
cd build
cmake ..
make -j4
sudo make install

# 安装opencv必要库
sudo apt install libopencv-dev=3.2.0+dfsg-4ubuntu0.1 -y

# 安装apriltag数据类型库
sudo apt install ros-melodic-apriltag-ros -y

# 编译apriltag
mkdir -p ~/apriltag_ws/src
cd ~/apriltag_ws/src
git clone https://github.com/AprilRobotics/apriltag.git
git clone https://github.com/AprilRobotics/apriltag_ros.git
cd ~/apriltag_ws
rosdep install --from-paths src --ignore-src -r -y
catkin_make
catkin_make_isolated

# 使用前操作
chmod +x -R ~/apriltag_ws
cd ~/apriltag_ws/devel_isolated
source setup.bash

# 运行核心
roslaunch apriltag_ros continuous_detection.launch
```

# usb_cam

```bash
mkdir ~/usb_cam_ws/src
cd ~/usb_cam_ws/src
git clone https://github.com/bosch-ros-pkg/usb_cam.git
cd ~/usb_cam_ws
catkin_make

sudo apt-get install ros-melodic-usb-cam

roslaunch usb_cam usb_cam-test.launch
```

## 修改 /home/nvidia/apriltag_ws/src/apriltag_ros/apriltag_ros/launch/continuous_detection.launch

```
<arg name="camera_name" default="/usb_cam" />
<arg name="camera_frame" default="usb_cam" />   #发布一个坐标系
<arg name="image_topic" default="image_raw" />
```

## 修改 /home/nvidia/apriltag_ws/src/apriltag_ros/apriltag_ros/config/tags.yaml

```json
standalone_tags:
  [
    {id: 1, size: 0.05},
    {id: 2, size: 0.05},
    {id: 22, size: 0.05},
    {id: 45, size: 0.05},

  ]
tag_bundles:
  [
    {
      name: 'my_bundle',
      layout:
        [
          {id: 10, size: 0.05, x: 0.0000, y: 0.0000, z: 0.0, qw: 1.0, qx: 0.0, qy: 0.0, qz: 0.0},
          {id: 22, size: 0.05, x: 0.0000, y: 0.0000, z: 0.0, qw: 1.0, qx: 0.0, qy: 0.0, qz: 0.0},
          {id: 45, size: 0.05, x: 0.0000, y: 0.0000, z: 0.0, qw: 1.0, qx: 0.0, qy: 0.0, qz: 0.0}
        ]
     }
  ]
```

## 运行 apriltag

```bash
roslaunch apriltag_ros continuous_detection.launch

# 查看输出信息
rostopic echo /tag_detections
```
