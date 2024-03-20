# 树莓派折腾笔记

开机设置

```bash
#设置硬盘拓展和VNC等
sudo raspi-config
sudo passwd root 
#切换清华源
#参考 https://mirrors.tuna.tsinghua.edu.cn/help/raspbian/
sudo update
```

设置ssh免密登录

```bash
mkdir .ssh
touch authorized_keys
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDbsjp97dJBOzzGcW3kyLKYMHzV6Ay5W9ayfJAcsO/YZXz7TtAedikl0QKCpMyd5U3T/aIlVQ944OxNgo1j0EHxqyzg8YVgCL1rHCFTXdJqS+ClNbHdNzkxbxtClzl1LhVyzPkSd/w2hr6RR2Fx1kIeY2Qu6zC4oalS12mzAEntFT5Obxz0VIIoT2bO5F+Hr0Vai+QJo3+jZSQbhVan6ePAYoFrqYa1QtVjtc7yNODTAlYU57mbsefvTmmJ+4P/17l1HNnSV+n42bOeLxTr/7bRihwtyqbU0bn/BzUfufRs2HFmi2ejCBtabX28oiuo5oG/0jPDy/KSese7J5ICVUy7
```

设置自动挂载硬盘

```bash
#查看硬盘uuid
sudo blkid
sudo vim /etc/fstab
#添加以下内容
UUID="567CE2CF7CE2A8C7"	/mnt/share/mdisk1	ntfs-3g	defaults	0	0
```

设置samba

```bash
sudo apt install samba samba-common-bin
sudo vim /etc/samba/smb.conf
添加
[pishare]
	path = /mnt/share
	writeable = Yes
	create mask = 0777
	directory mask = 0777
	public = no

#测试配置文件是否有误
testparm
#添加用户
sudo smbpasswd -a ly
sudo systemctl restart smbd

vps
//127.0.0.1/pishare     /mnt/share      cifs    credentials=/root/.smbcredentials,uid=1000,gid=1000,iocharset=utf8 0 0

#/root/.smbcredentials
username=ly
password=1114
```

安装xray

```bash
#找最新版本链接 https://github.com/XTLS/Xray-core/releases
mkdir xray
cd xray
wget https://github.com/XTLS/Xray-core/releases/download/v1.5.5/Xray-linux-arm64-v8a.zip
unzip Xray-linux-arm64-v8a.zip

sudo cp xray /usr/local/bin
sudo chmod +x /usr/local/bin/xray

sudo mkdir -p /usr/local/share/xray/
sudo cp ./*.dat /usr/local/share/xray/

sudo mkdir -p /usr/local/etc/xray/
sudo touch /usr/local/etc/xray/config.json

sudo mkdir -p /var/log/xray
sudo touch /var/log/xray/access.log
sudo touch /var/log/xray/error.log

#编辑config.json
sudo vim /usr/local/etc/xray/config.json

sudo touch /etc/systemd/system/xray.service
#添加

[Unit]
Description=Xray Service
Documentation=https://github.com/xtls
After=network.target nss-lookup.target

[Service]
User=root
CapabilityBoundingSet=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
AmbientCapabilities=CAP_NET_ADMIN CAP_NET_BIND_SERVICE
NoNewPrivileges=true
ExecStart=/usr/local/bin/xray run -config /usr/local/etc/xray/config.json
Restart=on-failure
RestartPreventExitStatus=23
LimitNPROC=10000
LimitNOFILE=1000000

[Install]
WantedBy=multi-user.target

sudo systemctl enable --now xray
sudo systemctl status xray
```



安装docker

```bash
curl -fsSL get.docker.com | sudo sh
sudo cat /etc/group | grep docker
#sudo groupadd docker 如果找不到docker就添加一个组
sudo gpasswd -a ${USER} docker
sudo systemctl restart docker
exit # 更新组信息也可以 #newgrp - docker

sudo vim /etc/docker/daemon.json
{
    "registry-mirrors" : [
    "https://registry.docker-cn.com",
    "http://hub-mirror.c.163.com",
    "https://docker.mirrors.ustc.edu.cn",
    "https://cr.console.aliyun.com",
    "https://mirror.ccs.tencentyun.com"
  ]
}

sudo systemctl daemon-reload
sudo systemctl restart docker
docker info
```

```bash
docker pull mariadb:latest
docker run --name=nextcloud_db -e MYSQL_ROOT_PASSWORD=1114 -d -p 33306:3306 --restart=always mariadb

docker pull linuxserver/nextcloud:latest

sudo mkdir -p /usr/local/etc/nextcloud/data
sudo mkdir -p /usr/local/etc/nextcloud/config

docker run -d   --name=nextcloud   -e PUID=1000   -e PGID=1000   -e TZ=Asia/Shanghai   -p 8443:443   --restart unless-stopped   -v /usr/local/etc/nextcloud/config:/config   -v /usr/local/etc/nextcloud/data:/data  -v /mnt/share:/mnt/share  --link nextcloud_db:db  linuxserver/nextcloud:latest

```

openwrt

```bash
sudo ip link set eth0 promisc on

docker pull sulinggg/openwrt:rpi4

docker network create -d macvlan --subnet=192.168.1.0/24 --gateway=192.168.1.1 --subnet=fe80::dbbe:fb4:d6b4:f640/64 --gateway=fe80::7eb5:9bff:feb9:d8d4 -o parent=eth0 macnet803

docker run --restart unless-stopped --name openwrt -d --network macnet803 --privileged sulinggg/openwrt:rpi4 /sbin/init


docker network create -d macvlan --subnet=192.168.0.0/24 --gateway=192.168.0.1 --subnet=fe80::f66d:2fff:fea2:7e12/64 --gateway=fe80::f66d:2fff:fea2:7e12 -o parent=eth0 xdr5480

docker run --restart unless-stopped --name openwrt -d --network xdr5480 --privileged sulinggg/openwrt:rpi4 /sbin/init

docker exec -it openwrt bash

vim /etc/config/network
#修改lan设置
config interface 'lan'
        option type 'bridge'
        option ifname 'eth0'
        option proto 'static'
        option netmask '255.255.255.0'
        option ip6assign '60'
        option ipaddr '192.168.1.200'
        option gateway '192.168.1.1'
        option dns '192.168.1.1
#重启网络
/etc/init.d/network restart

#在 “网络 - 接口 - Lan - 修改” 界面中，勾选下方的 “忽略此接口（不在此接口提供 DHCP 服务）”，并“保存&应用”。
#在 “网络 - 接口 - lan - 物理设置”界面中取消勾选桥接街口
#自定义策略中添加 iptables -t nat -I POSTROUTING -o eth0 -j MASQUERADE
#或者 iptables -t nat -I POSTROUTING -j MASQUERADE
```

unifreq/openwrt-aarch64

```
docker pull unifreq/openwrt-aarch64

docker run --restart unless-stopped --name openwrt2 -d --network xdr5480 --privileged unifreq/openwrt-aarch64 /sbin/init
```





qbittorrent

```

[Unit]
Description=qBittorrent Enhanced Edition Service

Documentation=man:qbittorrent-nox(1)
After=network.target

[Service]
Type=simple
PrivateTmp=false
User=qbtuser
LimitNOFILE=32768
ExecStart=/usr/bin/qbittorrent-nox
TimeoutSec=120

[Install]
WantedBy=multi-user.target

sudo systemctl daemon-reload
sudo systemctl enable --now qbittorrent-enhanced-nox
sudo systemctl status qbittorrent-enhanced-nox
```

aria2

```
docker pull p3terx/aria2-pro:latest

docker run -d \
    --name aria2-pro \
    --restart unless-stopped \
    --log-opt max-size=1m \
    -e PUID=$UID \
    -e PGID=$GID \
    -e UMASK_SET=022 \
    -e RPC_SECRET=1114 \
    -e RPC_PORT=6800 \
    -e LISTEN_PORT=6888 \
    -p 6800:6800 \
    -p 6888:6888 \
    -p 6888:6888/udp \
    -v $PWD/aria2/config:/config \
    -v $PWD/aria2/downloads:/downloads \
    p3terx/aria2-pro:latest
    
docker pull p3terx/ariang:latest
docker run -d \
    --name ariang \
    --log-opt max-size=1m \
    --restart unless-stopped \
    -p 6880:6880 \
    p3terx/ariang:latest
    
docker run -d \
    --name aria2-pro \
    --restart unless-stopped \
    --log-opt max-size=1m \
    --network host \
    -e PUID=$UID \
    -e PGID=$GID \
    -e UMASK_SET=022 \
    -e RPC_SECRET=1114 \
    -e RPC_PORT=6800 \
    -e LISTEN_PORT=6888 \
    -v $PWD/aria2/config:/config \
    -v $PWD/aria2/downloads:/downloads \
    p3terx/aria2-pro:latest

docker run --rm \
    --name aria2-pro \
    --log-opt max-size=1m \
    --network host \
    -e PUID=$UID \
    -e PGID=$GID \
    -e UMASK_SET=022 \
    -e RPC_SECRET=1114 \
    -e RPC_PORT=6800 \
    -e LISTEN_PORT=6888 \
    -v $PWD/aria2/config:/config \
    -v $PWD/aria2/downloads:/downloads \
    p3terx/aria2-pro:latest
    
docker run --rm \
    --name ariang \
    --log-opt max-size=1m \
    --network host \
    p3terx/ariang:latest
```





风扇控制服务 /etc/systemd/system/fan.service

```
[Unit]
Description=smart fan

After=network.target

[Service]
Type=simple
User=root
LimitNOFILE=32768
ExecStart=/usr/bin/python3 /usr/local/etc/fan.py
TimeoutSec=120

[Install]
WantedBy=multi-user.target
```



xray客户端配置(主要用于反向代理)

```json
{
  "policy": {
    "system": {
      "statsOutboundUplink": true,
      "statsOutboundDownlink": true
    }
  },
  "log": {
    "access": "",
    "error": "",
    "loglevel": "warning"
  },
  "reverse":{
        "bridges":[
      {
        "tag":"bridge", // 关于 A 的反向代理标签，在路由中会用到
        "domain":"private.cloud.com" // A 和 B 反向代理通信的域名，可以自己取一个，可以不是自己购买的域名，但必须跟下面 B 中的 reverse 配置的域名一致
      }
    ]
  },
  "inbounds": [
    {
      "tag": "socks",
      "port": 10808,
      "listen": "0.0.0.0",
      "protocol": "socks",
      "sniffing": {
        "enabled": true,
        "destOverride": [
          "http",
          "tls"
        ]
      },
      "settings": {
        "auth": "noauth",
        "udp": true,
        "allowTransparent": false
      }
    },
    {
      "tag": "http",
      "port": 10809,
      "listen": "0.0.0.0",
      "protocol": "http",
      "sniffing": {
        "enabled": true,
        "destOverride": [
          "http",
          "tls"
        ]
      },
      "settings": {
        "udp": false,
        "allowTransparent": false
      }
    },
    {
      "port": 10810,
      "protocol": "vless",
      "settings": {
        "udp": true,
        "clients": [
          {
            "id": "3893b879-4791-4bdc-b672-0e48c19274a1",
            "alterId": 0,
            "email": "t@t.tt",
            "flow": ""
          }
        ],
        "decryption": "none",
        "allowTransparent": false
      },
      "streamSettings": {
        "network": "tcp"
      }
    },
    {
      "tag": "api",
      "port": 1560,
      "listen": "127.0.0.1",
      "protocol": "dokodemo-door",
      "settings": {
        "udp": false,
        "address": "127.0.0.1",
        "allowTransparent": false
      }
    }
  ],
  "outbounds": [
    {
      "tag": "proxy",
      "protocol": "vless",
      "settings": {
        "vnext": [
          {
            "address": "172.64.148.127",
            "port": 443,
            "users": [
              {
                "id": "8944659a-7c4b-4e07-a931-da0989dd9b4b",
                "alterId": 0,
                "email": "t@t.tt",
                "security": "auto",
                "encryption": "none",
                "flow": ""
              }
            ]
          }
        ]
      },
      "streamSettings": {
        "network": "ws",
        "security": "tls",
        "tlsSettings": {
          "allowInsecure": false,
          "serverName": "www.airwall.xyz"
        },
        "wsSettings": {
          "path": "/bzbews",
          "headers": {
            "Host": "www.airwall.xyz"
          }
        }
      },
      "mux": {
        "enabled": true,
        "concurrency": 8
      }
    },
    {
        "tag": "tunnel",
      "protocol": "vless",
      "settings": {
        "vnext": [
          {
            "address": "172.64.148.127",
            "port": 443,
            "users": [
              {
                "id": "8944659a-7c4b-4e07-a931-da0989dd9b4b",
                "alterId": 0,
                "email": "t@t.tt",
                "security": "auto",
                "encryption": "none",
                "flow": ""
              }
            ]
          }
        ]
      },
      "streamSettings": {
        "network": "ws",
        "security": "tls",
        "tlsSettings": {
          "allowInsecure": false,
          "serverName": "www.airwall.xyz"
        },
        "wsSettings": {
          "path": "/reverse",
          "headers": {
            "Host": "www.airwall.xyz"
          }
        }
      },
      "mux": {
        "enabled": true,
        "concurrency": 8
      }
    },
    {
      "tag": "direct",
      "protocol": "freedom",
      "settings": {}
    },
    {
      "tag": "block",
      "protocol": "blackhole",
      "settings": {
        "response": {
          "type": "http"
        }
      }
    }
  ],
  "stats": {},
  "api": {
    "tag": "api",
    "services": [
      "StatsService"
    ]
  },
  "routing": {
    "domainStrategy": "IPIfNonMatch",
    "domainMatcher": "linear",
    "rules": [
      {
        "type": "field",
        "inboundTag": [
          "api"
        ],
        "outboundTag": "api",
        "enabled": true
      },
      {
        "type": "field",
        "outboundTag": "direct",
        "domain": [
          "domain:example-example.com",
          "domain:example-example2.com"
        ],
        "enabled": true
      },
      {
        "type": "field",
        "outboundTag": "block",
        "domain": [
          "geosite:category-ads-all"
        ],
        "enabled": true
      },
      {
        "type": "field",
        "outboundTag": "direct",
        "domain": [
          "geosite:cn"
        ],
        "enabled": true
      },
      {
        "type": "field",
        "outboundTag": "direct",
        "ip": [
          "geoip:private",
          "geoip:cn"
        ],
        "enabled": true
      },
      {
        "type":"field",
        "inboundTag":[
          "bridge"
        ],
        "domain":[
          "full:private.cloud.com"
        ],
        "outboundTag":"tunnel"
      },
      {
        "type":"field",
        "inboundTag":[
          "bridge"
        ],
        "outboundTag":"direct"
      },
      {
        "type": "field",
        "port": "0-65535",
        "outboundTag": "proxy",
        "enabled": true
      }
    ]
  }
}
```



xray服务端配置

```json
{
    "log": {
        "loglevel": "warning"
    },
    "reverse": { //这是 B 的反向代理设置，必须有下面的 portals 对象
        "portals": [
            {
                "tag": "portal",
                "domain": "private.cloud.com" // 必须和上面 A 设定的域名一样
            }
        ]
    },
    "inbounds": [
        {
            "listen": "0.0.0.0",
            "port": 443,
            "protocol": "vless",
            "settings": {
                "clients": [
                    {
                        "id": "11d7ccf2-51be-4aa9-a8ec-ea2045e43fb2", //此处改为你的UUID
                        "level": 0,
                        "email": "admin@v2rayssr.com", //此处为邮箱地址，随便修改
                        "flow": "xtls-rprx-direct"
                    }
                ],
                "decryption": "none",
                "fallbacks": [
                    {
                        "path": "/bzbews",
                        "dest": 31297,
                        "xver": 1
                    },
                    {
                        "path": "/reverse",
                        "dest": 31298,
                        "xver": 1
                    },
                    {
                        "dest": 8001 // http 1.1 端口
                    },
                    {
                        "alpn": "h2",
                        "dest": 8002 // http2 端口此处为回落端口，若更改，请更改后面Nginx的相应配置
                    }
                ]
            },
            "streamSettings": {
                "network": "tcp",
                "security": "xtls",
                "xtlsSettings": {
                    "serverName": "www.airwall.xyz", //修改为你的域名
                    "alpn": [
                        "h2",
                        "http/1.1"
                    ],
                    "certificates": [
                        {
                            "certificateFile": "/www/server/panel/vhost/cert/www.airwall.xyz/fullchain.pem", //修改为你的域名
                            "keyFile": "/www/server/panel/vhost/cert/www.airwall.xyz/privkey.pem" //修改为你的域名
                        }
                    ]
                }
            }
        },
        {
            "port": 31297,
            "listen": "0.0.0.0",
            "protocol": "vless",
            "tag": "VLESSWS",
            "settings": {
                "clients": [
                    {
                        "id": "8944659a-7c4b-4e07-a931-da0989dd9b4b",
                        "email": "www.airwall.xyz_VLESS_WS"
                    }
                ],
                "decryption": "none"
            },
            "streamSettings": {
                "network": "ws",
                "security": "none",
                "wsSettings": {
                    "acceptProxyProtocol": true,
                    "path": "/bzbews"
                }
            }
        },
        {
            "port": 31298,
            "listen": "0.0.0.0",
            "protocol": "vless",
            "tag": "tunnel",
            "settings": {
                "clients": [
                    {
                        "id": "8944659a-7c4b-4e07-a931-da0989dd9b4b",
                        "email": "www.airwall.xyz_VLESS_WS"
                    }
                ],
                "decryption": "none"
            },
            "streamSettings": {
                "network": "ws",
                "security": "none",
                "wsSettings": {
                    "acceptProxyProtocol": true,
                    "path": "/reverse"
                }
            }
        },
        {
            "port": 31301,
            "listen": "127.0.0.1",
            "protocol": "vless",
            "tag": "VLESSGRPC",
            "settings": {
                "clients": [
                    {
                        "id": "8944659a-7c4b-4e07-a931-da0989dd9b4b",
                        "add": "www.airwall.xyz",
                        "email": "www.airwall.xyz_VLESS_gRPC"
                    }
                ],
                "decryption": "none"
            },
            "streamSettings": {
                "network": "grpc",
                "grpcSettings": {
                    "serviceName": "bzbegrpc"
                }
            }
        },
        {
            // 接受 C 的inbound
            "tag": "pissh", // 标签，路由中用到
            "port": 22222,
            // 开放 80 端口，用于接收外部的 HTTP 访问 
            "protocol": "dokodemo-door",
            "settings": {
                "address": "127.0.0.1",
                "port": 22,
                "network": "tcp"
            }
        },
        {
            "tag": "nextclouds", 
            "port": 8443,
            "protocol": "dokodemo-door",
            "settings": {
                "address": "127.0.0.1",
                "port": 8443, 
                "network": ["tcp", "udp"]
            }
        },
        {
            "tag": "samba", 
            "port": 445,
            "protocol": "dokodemo-door",
            "settings": {
                "address": "127.0.0.1",
                "port": 445, 
                "network": ["tcp", "udp"]
            }
        }
    ],
    "outbounds": [
        {
            "protocol": "freedom",
            "settings": {}
        }
    ]
    ,
    "routing": {
        "rules": [
            { //路由规则，接收 C 请求后发给 A
                "type": "field",
                "inboundTag": [
                    "pissh",  "nextclouds", "samba"
                ],
                "outboundTag": "portal"
            },
            { //路由规则，让 B 能够识别这是 A 主动发起的反向代理连接
                "type": "field",
                "inboundTag": [
                    "tunnel"
                ],
                "domain": [
                    "full:private.cloud.com"
                ],
                "outboundTag": "portal"
            }
        ]
    }
}
```

风扇控制 fan.py

```python
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

```

