"""
根据CPU温度开启与关闭树莓派风扇
"""
import time, os
import RPi.GPIO as GPIO
import logging

GPIO_OUT = 14
START_TEMP = 63
CLOSE_TEMP = 50
DELAY_TIME = 15
LOG_PATH = '/var/log/fan_control.log'

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',  # 日志格式
                    datefmt='%Y-%m-%d %H:%M:%S',  # 时间格式
                    filename=LOG_PATH,  # 日志的输出路径
                    filemode='w')  # 追加模式

def get_temp():
    """
    获取树莓派CPU温度, 读取/sys/class/thermal/thermal_zone0/temp内容, 除1000就是温度
    :return: float
    """
    with open("/sys/class/thermal/thermal_zone0/temp", 'r') as f:
        temperature = float(f.read()) / 1000
    return temperature

class FanController(object):

    def __init__(self, GPIO_OUT=14) -> None:
        self.fan_state = False # 默认风扇未开启
        self.temp = -1 # 初始cpu温度
        self.GPIO_OUT = GPIO_OUT # 默认操控GPIO14
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(GPIO_OUT, GPIO.OUT, initial=GPIO.HIGH) # 初始化为高电平 即关闭风扇

    def open_fan(self):
        """
        开启风扇
        :param temp: 树莓派CPU温度
        :return:
        """
        # PNP型三极管基极施加低电平时才导通电路, NPN型三极管相反
        self.fan_state = True
        GPIO.output(GPIO_OUT, GPIO.LOW)

    def close_fan(self):
        """
        关闭风扇
        :param temp: 树莓派CPU温度
        :return:
        """
        # 基级施加高电平
        self.fan_state = False
        GPIO.output(GPIO_OUT, GPIO.HIGH)

    def running(self):
        try:
            while True:
                temp = get_temp()
                # 温度大于START_TEMP开启风扇， 低于CLOSE_TEMP关闭风扇
                info = ""
                if self.fan_state: # 风扇处于打开状态
                    if temp < CLOSE_TEMP:
                        self.close_fan()
                        info = ('power off fan, temp is %s' % temp)
                    else:
                        info = ('fan is running, temp is %s' % temp)
                else: # 风扇处于关闭状态
                    if temp > START_TEMP: # 打开风扇
                        info = ('power on fan, temp is %s' % temp)
                        self.open_fan()
                    else:
                        info = ('fan is closed, temp is %s' % temp)

                logging.info(info)
                print(info) # debug
                time.sleep(DELAY_TIME)

        except Exception as e:
            print(e)
            self.close_fan() # 出现异常先关风扇
            GPIO.cleanup()
            logging.error(e)

if __name__ == '__main__':
    os.environ["TZ"] = 'Asia/Shanghai'
    time.tzset()
    logging.info('started control fan...')
    fan = FanController()
    fan.running()
    fan.close_fan()
    GPIO.cleanup()
    logging.info('quit started control fan...')
