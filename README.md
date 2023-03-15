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

cd ~
wget https://www.raoyunsoft.com/opencv/opencv-3.4.16/opencv-3.4.16.zip
unzip opencv-3.4.16.zip
cd opencv-3.4.16
mkdir build
cd build
cmake ..
make -j4
sudo make install

sudo apt install libopencv-dev=3.2.0+dfsg-4ubuntu0.1


mkdir -p ~/apriltag_ws/src
cd ~/apriltag_ws/src
git clone https://github.com/AprilRobotics/apriltag.git
git clone https://github.com/AprilRobotics/apriltag_ros.git
cd ~/apriltag_ws
rosdep install --from-paths src --ignore-src -r -y
catkin_make
catkin_make_isolated

chmod +x -R ~/apriltag_ws
cd ~/apriltag_ws/devel_isolated
source setup.bash

roslaunch apriltag_ros continuous_detection.launch
```
