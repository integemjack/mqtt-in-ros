#!/usr/bin/env python3

import time
import subprocess

# 设置温度阈值和风扇转速范围
temperature_threshold = 50  # 温度阈值，根据实际情况进行调整
fan_speed_min = 0           # 最低风扇转速
fan_speed_max = 255         # 最高风扇转速
temp_max = 70

while True:
    # 获取当前温度
    temperature_output = subprocess.check_output("cat /sys/devices/virtual/thermal/thermal_zone0/temp", shell=True)
    temperature = int(temperature_output) / 1000  # 转换为摄氏度

    relative_speed = int((fan_speed_max - fan_speed_min) / temp_max * temperature)
    print('relative_speed: ', end='')
    print(relative_speed, end='')
    print(", temperature: ", end='')
    print(temperature)
    subprocess.run("echo {} > /sys/devices/pwm-fan/target_pwm".format(relative_speed), shell=True)

    # 等待一段时间后再次监测温度
    time.sleep(5)  # 根据需要调整休眠时间