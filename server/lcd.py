from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
from PIL import ImageDraw, ImageFont
import socket

def get_lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "None"

# 创建 I2C 设备
serial = i2c(port=0, address=0x3c)

# 创建 SSD1306 OLED 设备
device = ssd1306(serial)

# 创建画布并在画布上绘制
with canvas(device) as draw:
    draw.text((20, 20), "IP Address:", fill="white")
    draw.text((20, 30), get_lan_ip(), fill="white")