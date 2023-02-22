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
