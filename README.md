## Demo

```bash
cd ~
mkdir -p ./mqtt_ws/src
cd mqtt_ws/src
git clone https://github.com/integemjack/mqtt
cd mqtt
sudo apt install python3-pip -y
sudo apt install ros-melodic-rosbridge-library -y
sudo pip3 install dev-requirements.txt
cd ~/mqtt_ws
catkin_make
cd devel
source setup.bash
pip3 install rospkg
chmod +x ~/mqtt_ws
```

# 启动

## 终端 1

```bash
cd ~/mqtt_ws/src/mqtt/scripts/
roslaunch mqtt_bridge demo.launch
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
