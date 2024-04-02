# 安装 Home Assistant Supervised
[参考连接](https://zhuanlan.zhihu.com/p/498773266)
[官方](https://github.com/home-assistant/supervised-installer)

## 更新系统
```
export http_proxy=http://xxxx:
export https_proxy=http://xxxx:

sudo apt update -y
sudo apt upgrade -y
```

## 检查系统版本
```
lsb_release -a
```
[检查连接](https://link.zhihu.com/?target=https%3A//www.home-assistant.io/more-info/unsupported/os)

## 安装NetworkManager

```
# 创建配置目录和文件
sudo mkdir -p /etc/NetworkManager/conf.d/
# 对文件追加内容
sudo touch /etc/NetworkManager/conf.d/100-disable-wifi-mac-randomization.conf
sudo vim /etc/NetworkManager/conf.d/100-disable-wifi-mac-randomization.conf

#追加内容
[connection]
wifi.mac-address-randomization=1

[device]
wifi.scan-rand-mac-address=no


sudo apt install -y network-manager


# 停止ModemManager
sudo systemctl stop ModemManager
# 禁止ModemManager开机自启
sudo systemctl disable ModemManager
```

## 安装apparmor

```
sudo apt install -y apparmor-utils jq software-properties-common apt-transport-https avahi-daemon ca-certificates curl dbus socat

# 使用vim打开/boot/cmdline.txt
sudo vim /boot/cmdline.txt

# 末尾添加
apparmor=1 security=apparmor
```

## 安装OS Agent

[下载连接](https://github.com/home-assistant/os-agent/releases/latest)
```
wget https://github.com/home-assistant/os-agent/releases/download/1.6.0/os-agent_1.6.0_linux_aarch64.deb

sudo dpkg -i os-agent_1.2.2_linux_aarch64.deb

# 其他的依赖
sudo apt-get install \
jq \
wget \
curl \
udisks2 \
libglib2.0-bin \
dbus\
systemd-resolved\
 systemd-journal-remote\
  -y
```

## 安装docker
```
# 下载Docker安装脚本
sudo curl -fsSL https://get.docker.com -o get-docker.sh
# 使用阿里镜像源下载并安装Docker
sudo sh get-docker.sh --mirror Aliyun

sudo usermod -aG docker pi

# 更换源
vim /etc/docker/daemon.json

# 添加
{
    "registry-mirrors":[
    "https://hub-mirror.c.163.com/",
    "https://docker.mirrors.ustc.edu.cn/"]
}
sudo systemctl daemon-reload
sudo systemctl restart docker

sudo reboot
```

## 最终安装ha

```
# 下载deb安装包
wget https://github.com/home-assistant/supervised-installer/releases/latest/download/homeassistant-supervised.deb
# 安装

sudo apt install systemd-resolved systemd-journal-remote
sudo dpkg -i homeassistant-supervised.deb

# 检查是否启动成功
docker ps -a 

# 如果没有 则手动启动
sudo /usr/sbin/hassio-supervisor
```

## 安装 Home Assistant Community Store
[参考连接](https://zhuanlan.zhihu.com/p/482610042)
```

sudo su
wget -O - https://get.hacs.xyz | bash -

```