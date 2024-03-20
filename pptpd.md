# LINUX PPTPD 折腾笔记

```shell
# 安装pptpd
apt-get install pptpd
```

```shell
# 设置vpn ip地址池 要和下面的流量转发相匹配
vi /etc/pptpd.conf
localip 192.168.3.1
remoteip 192.168.3.100-200
```

```shell
# 设置DNS
vi /etc/ppp/options-pptpd 
ms-dns 8.8.8.8
ms-dns 4.4.4.4
```

```shell
# 设置用户名和密码
vi /etc/ppp/chap-secrets
usernameForuser1 *  setpassword1here  *
usernameForuser2 *  setpassword2here  *
```

```shell
# 设置流量转发
vi /etc/sysctl.conf
net.ipv4.ip_forward = 1
# 下面这条命令让规则更改生效
sysctl -p
```

```shell
# 更改防火墙规则

#iptables -A INPUT -i eth0 -p tcp --dport 1723 -j ACCEPT
#iptables -A INPUT -i eth0 -p gre -j ACCEPT
#iptables -A FORWARD -i ppp+ -o eth0 -j ACCEPT
#iptables -A FORWARD -i eth0 -o ppp+ -j ACCEPT

# 这两句和下面那一句效果一样 不过更高效
# 注意修改网络设备
iptables -t nat -A POSTROUTING -s 192.168.3.0/24 -o eth0 -j MASQUERADE
iptables -A FORWARD -p tcp --syn -s 192.168.3.0/24 -j TCPMSS --set-mss 1356

# 地址伪装 内网地址通过网卡伪装为外网地址
#iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE


# 可以使用下面命令让规则生效，也可以把上面命令写道/etc/rc.local中
service iptables save
service iptables restart
```

```shell
# 重启pptpd服务
/etc/init.d/pptpd restart
sudo reboot
```

```
# 无屏幕 无键盘配置树莓派

# 树莓派设置自启SSH
在boot下新建一个名为ssh的文件即可

# 树莓派自动连接wifi
在boot盘下新建一个文件，命名为wpa_supplicant.conf

用记事本打开写入以下内容：

country=CN
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
ssid="WiFi-A"
psk="12345678"
key_mgmt=WPA-PSK 
priority=1
}

network={
ssid="WiFi-B"
psk="12345678"
key_mgmt=WPA-PSK
priority=2
scan_ssid=1
}

#ssid:网络的ssid
#psk:密码
#priority:连接优先级，数字越大优先级越高（不可以是负数）
#scan_ssid:连接隐藏WiFi时需要指定该值为1


# 无密码
network={
ssid="你的无线网络名称（ssid）"
key_mgmt=NONE
}

# WEP加密
network={
ssid="你的无线网络名称（ssid）"
key_mgmt=NONE
wep_key0="你的wifi密码"
}

#WPA/WPA2加密
network={
ssid="你的无线网络名称（ssid）"
key_mgmt=WPA-PSK
psk="你的wifi密码"
}
```

```shell
# 调整默认网关优先级 通过metric值来调整无线网卡和有线网卡的优先级
sudo ip route add default via <gateway> dev <interface> metric <val>

# 删除默认网关
sudo route del default gw <gateway>
```

