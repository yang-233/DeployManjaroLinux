import requests
import json
import logging

def get_logger():
    name = ".".join(__file__.split(".")[:-1])
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    while logger.hasHandlers():
        for i in logger.handlers:
            logger.removeHandler(i)

    logFile = name + ".log"
    fileHandler = logging.FileHandler(logFile, mode="a", encoding='utf-8')
    consoleHandler = logging.StreamHandler()
    fmt = logging.Formatter("[%(asctime)s | \"%(filename)s\" line %(lineno)s | %(levelname)s]  %(message)s",
                           datefmt="%Y-%m-%d %H:%M:%S")
    fileHandler.setFormatter(fmt)
    consoleHandler.setFormatter(fmt)

    logger.addHandler(fileHandler)
    logger.addHandler(consoleHandler)
    return logger

def get_new_ip():
    # req = requests.get("http://ipv4.icanhazip.com")
    req = requests.get("http://ifconfig.me")

    if req.status_code == 200:
        return req.content.decode("utf8").strip()
    else:
        logger.error("get new ip error")
        exit(-1)

def get_now_ip():
    with open("now_ip.txt", "r") as r:
        return r.readline().strip()

if __name__ == "__main__":
    logger = get_logger()

    zone_id = ""
    api_key = ""
    record_id = ""
    name = ""

    now_ip = get_now_ip()
    new_ip = get_new_ip()

    if now_ip == new_ip:
        logger.info("ip no change!")
        exit()

    url = "https://api.cloudflare.com/client/v4/zones/" + zone_id +"/dns_records/" + record_id
    header = {
        "Authorization" : "Bearer " + api_key,
        "Content-Type" : "application/json"
    }
    data = {
        "type" : "A",
        "name" : name,
        "content" : new_ip,
        "ttl" : 300,
        "proxied": False
    }

    res = requests.put(url, json = data, headers=header)
    body = json.loads(res.text)
    if body["success"]:
        logger.info(f"update dns success! new ip : {new_ip}")
        with open("now_ip.txt", "w") as w:
            w.write(new_ip)
    else:
        logger.error("update dns error!")
