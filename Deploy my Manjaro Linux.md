# Deploy my Manjaro Linux 

## Windows:

### Set Linux's efi:

```powershell
bcdedit /set "{bootmgr}" path \EFI\Manjaro\grubx64.efi
```

### Set UTC time:

```powershell
Reg add HKLM\SYSTEM\CurrentControlSet\Control\TimeZoneInformation /v RealTimeIsUniversal /t REG_DWORD /d 1
```

## Manjaro Linux:

### Set mirrors:

```shell
sudo pacman-mirrors -i -c China -m rank
sudo pacman -Syy
sudo pacman -Syu
```

### Add archlinuxcn resources:

```shell
sudo vim /etc/pacman.conf
```

#### Append:

```
[archlinuxcn]  
SigLevel = Optional TrustedOnly  
Server = https://mirrors.ustc.edu.cn/archlinuxcn/$arch  
```

```shell
sudo pacman -Syy
sudo pacman -S archlinuxcn-keyring
```

#### If install archlinuxcn-keyring failure:

```shell
pacman -Syu haveged 
systemctl start haveged 
systemctl enable haveged 
rm -rf /etc/pacman.d/gnupg 
pacman-key --init 
pacman-key --populate manjaro
pacman-key --populate archlinuxcn  
```

### Install some software:

```shell
sudo pacman -S vim yay 
sudo pacman -S wewechat electronic-wechat deepin-wine-tim
sudo pacman -S wps-office ttf-wps-fonts
sudo pacman -S netease-cloud-music
sudo pacman -S codebolcks
sudo pacman -S jdk-openjdk intellij-idea-ultimate-edition pycharm-professionial 
```

### Clean trash:

```shell
sudo pacman -R $(pacman -Qdtq)
sudo pacman -Scc
```

### Install Chinese input method:

```shell
sudo pacman -S fcitx-im fcitx-configtool fcitx-sunpinyin
sudo vim /etc/profile
```

#### Append:

```
export GTK2_RC_FILES="$HOME/.gtkrc-2.0"
export LC_CTYPE=en_US.UTF-8
export XMODIFIERS=@im=fcitx
export GTK_IM_MODULE=fcitx
export QT_IM_MODULE=fcitx
export XIM_PROGRAM=fcitx
export XIM=fcitx
```

```shell
reboot
```

### Set time:

```shell
#may not be necessary
sudo timedatectl set-local-rtc true
```

### Cross GFW :

#### Install shadowsocks:

```shell
sudo pip3 install shadowsocks
#edit the openssl.py
sudo vim /usr/lib/python3.7/site-packages/shadowsocks/crypto/openssl.py
```

>Modify cleanup into reset：
>line 52: libcrypto.EVP_CIPHER_CTX_cleanup.argtypes = (c_void_p,) 
>to libcrypto.EVP_CIPHER_CTX_reset.argtypes = (c_void_p,)
>line 111: libcrypto.EVP_CIPHER_CTX_cleanup(self._ctx) 
>to libcrypto.EVP_CIPHER_CTX_reset(self._ctx)

```shell
cd ~
mkdir crossgfw
cd crossgfw
vim ssconfig.json
```

```json
{
    "server":"1.1.1.1",
    "server_port":1024,
    "local_address": "127.0.0.1",
    "local_port":1080,
    "password":"",
    "timeout":600,
    "method":"aes-256-cfb"
}
```

#### Install genpac:

```shell
sudo pip install -U genpac
cd ~/crossgfw
touch pac
genpac --format=pac --pac-proxy="SOCKS5 127.0.0.1:1080" > pac
```

#### Install privoxy:

```shell
sudo pacman -S privoxy
cd ~/crossgfw
vim privoxyconfig
```

```
listen-address 127.0.0.1:8228
forward-socks5 / 127.0.0.1:1080 .
```

```shell
sudo vim /etc/profile
```

Append:

```
export http_proxy=http://127.0.0.1:8228
export https_proxy=http://127.0.0.1:8228
export ftp_proxy=http://127.0.0.1:8228
```

```shell
vim run.sh
```

```shell
#!/bin/bash
sslocal -c ssconfig.json -d start
privoxy privoxyconfig
genpac --format=pac --pac-proxy="SOCKS5 127.0.0.1:1080" > pac
echo 'listen-address 127.0.0.1:8228
forward-socks5 / 127.0.0.1:1080 .' > privoxyconfig 
curl https://zfl9.github.io/gfwlist2privoxy/gfwlist.action >> privoxyconfig
```

```shell
reboot
```

#### Build an applications on desktop:

```
[Desktop Entry]
Comment[en_US]=cross the great firewall
Comment=cross the great firewall
Exec=sudo ./run.sh
GenericName[en_US]=cross the great firewall
GenericName=cross the great firewall
Icon=
MimeType=
Name[en_US]=crossgfw
Name=crossgfw
Path=/home/yang/Documents/crossgfw
StartupNotify=true
Terminal=true
TerminalOptions=
Type=Application
X-DBUS-ServiceName=
X-DBUS-StartupType=
X-KDE-SubstituteUID=false
X-KDE-Username=
```

### Use git:

```shell
ssh-keygen -t rsa -C "you@email"
git remote add origin git@github.com:yang-233/DeployManjaroLinux.git
git pull origin master
```

