name="car$1"

echo "car: $name"

sudo echo $name > /machineId



# install ros

sudo sh -c 'echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -sc) main" > /etc/apt/sources.list.d/ros-latest.list'

sudo apt install curl -y
curl -s https://raw.githubusercontent.com/ros/rosdistro/master/ros.asc | sudo apt-key add -

sudo apt update
sudo apt install ros-melodic-desktop-full -y

echo "source /opt/ros/melodic/setup.bash" >> ~/.bashrc
source ~/.bashrc

sudo apt install python-rosdep python-rosinstall python-rosinstall-generator python-wstool build-essential -y
sudo apt install python-rosdep -y
sudo apt install ros-melodic-image-transport ros-melodic-vision-msgs -y

sudo rosdep init
rosdep update


# install imagenet

cd ~
sudo apt-get install git cmake -y
git clone --recursive https://github.com/dusty-nv/jetson-inference ~/jetson-inference
cd ~/jetson-inference
mkdir -p ~/jetson-inference/build
cd ~/jetson-inference/build
cmake ../
make -j$(nproc)
sudo make install
sudo ldconfig


# test ros
mkdir -p ~/ros_workspace/src
git clone https://github.com/dusty-nv/ros_deep_learning ~/ros_workspace/src/ros_deep_learning
cd ~/ros_workspace
sudo apt install python-catkin-tools -y
catkin_make
cd ~/ros_workspace/devel
source ./setup.bash

# 如果catkin_make 不存在时
# sudo apt install python-catkin-tools

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

# install mqtt
mkdir -p ~/mqtt_ws/src
git clone https://github.com/integemjack/mqtt ~/mqtt_ws/src/mqtt
cd ~/mqtt_ws/src/mqtt
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


sudo mv ~/mqtt_ws/src/mqtt/server/connect.service /etc/systemd/system/connect.service
sudo systemctl enable connect
sudo systemctl start connect


# install jupyter
sudo apt install jupyter -y
sudo jupyter notebook --generate-config
sudo sed -i "s/#c.NotebookApp.ip = 'localhost'/c.NotebookApp.ip = '0.0.0.0'/g" /root/.jupyter/jupyter_notebook_config.py
sudo sed -i "s/#c.NotebookApp.open_browser = True/c.NotebookApp.open_browser = False/g" /root/.jupyter/jupyter_notebook_config.py

# install jupyter lab
sudo su
cd /home/nvidia
pip3 install virtualenv
virtualenv myenv
source myenv/bin/activate
pip3 install jupyterlab
jupyter lab --generate-config
sed -i "s/#c.ServerApp.ip = 'localhost'/c.ServerApp.ip = '0.0.0.0'/g" /root/.jupyter/jupyter_lab_config.py
sed -i "s/#c.ServerApp.open_browser = False/c.ServerApp.open_browser = False/g" /root/.jupyter/jupyter_lab_config.py