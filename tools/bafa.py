import socket
import threading
import time
import logging
import paramiko
from wakeonlan import send_magic_packet

apiKey = ""
topic = ""
pcmac = ""
pcip = ""
pwd = ""
user = ""

MAX_TRY = 5
# 初始化一个logger
def getLogger():
    name = ".".join(__file__.split(".")[:-1])
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    while logger.hasHandlers():
        for i in logger.handlers:
            logger.removeHandler(i)

    logFile = name + ".log"
    fileHandler = logging.FileHandler(logFile, mode="w", encoding='utf-8')
    consoleHandler = logging.StreamHandler()
    fmt = logging.Formatter("[%(asctime)s | \"%(filename)s\" line %(lineno)s | %(levelname)s]  %(message)s",
                           datefmt="%Y-%m-%d %H:%M:%S")
    fileHandler.setFormatter(fmt)
    consoleHandler.setFormatter(fmt)

    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)
    return logger

# 解析返回结果
def parseRecv(msg):
    res = {}
    msg = msg.decode("utf8")
    items = msg.strip().split("&")
    for item in items:
        arr = item.split("=")
        if len(arr) == 2:
            key, value = arr
            res[key] = value
    return res

def turnOn():
    send_magic_packet(pcmac)

def turnOff():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(pcip, username=user, password=pwd)
    stdin, stdout, stderr = client.exec_command('shutdown -s -f -c "小爱将在 5 秒内关闭这个电脑" -t 5')  
    if client is not None:
        client.close()
        del client, stdin, stdout, stderr

# 订阅主题 可以是多个
def subscripte(tryNum=0):
    if tryNum == MAX_TRY:
        logger.error(f"connect num bigger than MAX_TRY : {MAX_TRY}")
        exit(-1)
    
    # 创建socket
    tcpClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ip = 'bemfa.com'
    port = 8344
    tcpClientSocket.connect((ip, port))
    sub = "cmd=1&uid=" + apiKey + "&topic=" + topic + "\r\n"
    try:
        tcpClientSocket.send(sub.encode("utf-8"))
        recv = parseRecv(tcpClientSocket.recv(1024))
        if recv["res"] == "1":
            logger.info("connect sucess!")
            return tcpClientSocket
    except:
        time.sleep(30)
        logger.warning(f"connect num : {tryNum + 1}")
        subscripte(tryNum + 1)

# 心跳
def keepAlive(tcpClientSocket):
    num = 0
    keeplive = 'ping\r\n'
    while True:
        try:
            tcpClientSocket.send(keeplive.encode("utf-8"))
            num += 1
            if num == 60:
                logger.info("send ping")
                num = 0

        except Exception as e:
            logger.warning(f"send ping error!")
            logger.error(e)
            tcpClientSocket = subscripte()
            
        time.sleep(60)      

if __name__ == "__main__":
    logger = getLogger()
    tcpClientSocket = subscripte()

    # 保持心跳
    t = threading.Thread(target=keepAlive, args=(tcpClientSocket,))
    t.start()

    # 接受指令
    while True:
        # 接收服务器发送过来的数据
        try:
            recv = tcpClientSocket.recv(1024)

            recv = parseRecv(recv)
            res = recv.get("res", "null")
            msg = recv.get("msg", "null")

            if res != "null" or msg == "null":
                continue

            logger.info(f"get message : {msg}")
            if msg == "on": #开机
                logger.info("turn on pc")
                t = threading.Thread(target=turnOn)
                t.start()
            elif msg == "off": # 关机
                logger.info("turn off pc")
                t = threading.Thread(target=turnOff)
                t.start()
        except Exception as e:
            logger.warning(f"get message error!")
            logger.error(e)
            tcpClientSocket = subscripte()