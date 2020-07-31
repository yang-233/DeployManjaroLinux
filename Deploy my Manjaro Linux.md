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
sudo pacman -S gvim yay 
sudo pacman -S wewechat electronic-wechat deepin-wine-tim
sudo pacman -S wps-office ttf-wps-fonts
sudo pacman -S netease-cloud-music
sudo pacman -S codebolcks
sudo pacman -S jdk-openjdk intellij-idea-ultimate-edition pycharm-professionial 
```

### Modify the vim's setting:

```shell
sudo vim /etc/vimrc
```

```
"显示行号
set nu

"启动时隐去援助提示
set shortmess=atI

"语法高亮
syntax on

"使用vim的键盘模式
"set nocompatible

"不需要备份
set nobackup

"没有保存或文件只读时弹出确认
set confirm

"鼠标可用
set mouse=a

"tab缩进
set tabstop=4
set shiftwidth=4
set expandtab
set smarttab

"文件自动检测外部更改
set autoread

"c文件自动缩进
set cindent

"自动对齐
set autoindent

"智能缩进
set smartindent

"高亮查找匹配
set hlsearch

"背景色
set background=dark

"显示匹配
set showmatch

"显示标尺，就是在右下角显示光标位置
set ruler

"去除vi的一致性
set nocompatible

"允许折叠
set foldenable
"""""""""""""""""设置折叠"""""""""""""""""""""
"
"根据语法折叠
set fdm=syntax

"手动折叠
"set fdm=manual

"设置键盘映射，通过空格设置折叠
nnoremap <space> @=((foldclosed(line('.')<0)?'zc':'zo'))<CR>
""""""""""""""""""""""""""""""""""""""""""""""
"不要闪烁
set novisualbell

"启动显示状态行
set laststatus=2

"浅色显示当前行
autocmd InsertLeave * se nocul

"用浅色高亮当前行
autocmd InsertEnter * se cul

"显示输入的命令
set showcmd

"被分割窗口之间显示空白
set fillchars=vert:/

set fillchars=stl:/

set fillchars=stlnc:/
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
cd /etc
mkdir proxy
cd proxy
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
cd /etc/proxy
genpac --format=pac --pac-proxy="SOCKS5 127.0.0.1:1080" > pac
```

#### Install privoxy:

```shell
sudo pacman -S privoxy
cd ~/crossgfw
vim privoxyconfig
```

```
#the config
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
cd /etc/proxy
sslocal -c ssconfig.json -d start
privoxy privoxyconfig
```

#### AutoStart:

```shell
cd /etc
sudo vim rc.local
```

append:

```shell
#!/bin/bash
sslocal -c /etc/proxy/ssconfig.json -d start
privoxy /etc/proxy/privoxyconfig
```

```shell
sudo chmor a+x rc.local
cd /etc/systemd/system/
sudo vim rc-local.service
```

append:

```
[Unit]
Description=/etc/rc.local Compatibility

[Service]
Type=oneshot
ExecStart=/etc/rc.local
TimeoutSec=0
StandardInput=tty
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

#### Update config:

```shell
cd /etc/proxy
sudo vim update.sh
```

```shell
#!/bin/bash
genpac --format=pac --pac-proxy="SOCKS5 127.0.0.1:1080" > pac
echo 'listen-address 127.0.0.1:8228
forward-socks5 / 127.0.0.1:1080 .' > privoxyconfig 
curl https://zfl9.github.io/gfwlist2privoxy/gfwlist.action >> privoxyconfig
```

```
sudo chmod a+x update.sh
```

Build an application on desktop:

```
[Desktop Entry]
Comment[en_US]=update config
Comment=update config
Exec=sudo /etc/proxy/update.sh
GenericName[en_US]=update config
GenericName=update config
Icon=preferences-web-browser-shortcuts
MimeType=
Name[en_US]=Update
Name=Update
Path=/etc/proxy
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
git config --global user.email "you@email"
git config --global user.name "yang"
git remote add origin git@github.com:yang-233/DeployManjaroLinux.git
git pull origin master
git push origin master
```

### Grub rescue:

```
grub rescue> 
#viewing settings
set 
#list all disk partitions
ls
#view all partitions in turn
#like 
ls (sd0,gpt3)
#find the ext file system and change the settings
set root=sdo,gpt3
set prefix=(sd0,gpt3)/boot/grub
#now, we can boot
insmod normal
normal
```

```shell
#after entering the linux system
sudo update-grub
sudo grub-install /dev/sda
```

### Set Konsole Theme:

```shell
cp Dracula.colorscheme ~/.local/share/konsole
#Go to Konsole > Settings > Edit Current Profile… > Appearance tab
```

### V2Ray:

```shell
source < (curl -sL https://git.io/fNgqx)
```

### Crossover:

```shell
sudo pacman -Syu base-devel --needed
yaourt -S lib32-nss-mdns
```

### OneDrive:

```shell
#install
sudo pacman -S curl sqlite dmd
git clone https://github.com/abraunegg/onedrive.git
cd onedrive
make clean; make;
sudo make install

#run
systemctl enable onedrive@<username>.service
systemctl start onedrive@<username>.service
systemctl status onedrive@username.service
#uninstall
sudo make uninstall
# delete the application state
rm -rf ~/.config/onedrive
```

### 中文字体：

```
sudo pacman -S 
wqy-microhei 
ttf-dejavu 
wqy-zenhei 
wqy-microhei
adobe-source-han-serif-cn-fonts
adobe-source-han-serif-tw-fonts 
adobe-source-han-sans-cn-fonts 
adobe-source-han-sans-tw-fonts

wqy-zenhei
wqy-bitmapfont
ttf-arphic-ukai
ttf-arphic-uming
opendesktop-fonts 
ttf-hannom	

#AUR 
ttf-tw
ttf-twcns-fonts
noto-fonts-sc
noto-fonts-tc
ttf-ms-win8-zh_cnAUR 
ttf-ms-win8-zh_twAUR 
ttf-ms-win10-zh_cnAUR 
ttf-ms-win10-zh_twAUR 

```
### Install jupyter:
```
pip instsall jupyter
pip install jupyter_nbextensions_configurator jupyter_contrib_nbextensions
jupyter contrib nbextension install --user
jupyter nbextensions_configurator enable --user
```
### Git record password
```
git config --global credential.helper store
```

### Set jupyter lab envs
```
#run this command for every env
conda install ipykernel
conda activate ***
python -m ipykernel install --user --name *** --display-name "Python (***)"
```

