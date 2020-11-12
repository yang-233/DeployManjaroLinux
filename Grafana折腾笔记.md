# Grafana折腾

```shell
# 以下默认使用root执行
apt-get install -y docker.io
docker pull prom/node-exporter
docker pull prom/prometheus
docker pull grafana/grafana
# 安装nvidia-container-tools 
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)

curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -

curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
sudo apt-get update
sudo apt-get install -y nvidia-docker2
sudo systemctl restart docker
# 测试是否装好了
sudo docker run --rm --gpus all nvidia/cuda:11.0-base nvidia-smi

docker pull nvidia/dcgm-exporter
```

```shell
# 启动node-exporter
docker run --name node-exporter -d -p 9100:9100 \
  -v "/proc:/host/proc:ro" \
  -v "/sys:/host/sys:ro" \
  -v "/:/rootfs:ro" \
  prom/node-exporter
# 访问测试是否成功
netstat -anpt
http://192.168.91.132:9100/metrics
```

```shell
# 启动prometheus 端口及路径自己设置
mkdir /opt/prometheus
cd /opt/prometheus/
vim prometheus.yml

global:
  scrape_interval:     10s
  evaluation_interval: 10s
 
scrape_configs:

  - job_name: linux
    static_configs:
      - targets: ['172.17.0.1:9100']
        labels:
          instance: pi1

      - targets: ['172.21.15.34:9100']
        labels:
          instance: 1080ti
        
      - targets: ['172.21.15.155:9100']
        labels:
          instance: 1070ti

  - job_name: gpu
    scrape_interval: 3s
    scrape_timeout: 3s
    static_configs:

      - targets: ['172.21.15.34:9400']
        labels:
          instance: 1080ti_0
      
      - targets: ['172.21.15.34:9401']
        labels:
          instance: 1080ti_1

      - targets: ['172.21.15.155:9400']
        labels:
          instance: 1070ti
          
# 因为node_exporter 和 prometheus不在一个docker中，则需要通过宿主机网卡来查询
# 配置文件要填绝对路径
docker run  --name prometheus -d \
  -p 9090:9090 \
  -v /opt/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml  \
  prom/prometheus
 
# 查看是否启动成功
netstat -anpt
http://localhost:9090/graph

# 如果没有up要等等
http://192.168.91.132:9090/targets
```

```
# 启动grafana
mkdir /opt/grafana-storage
chmod 777 -R /opt/grafana-storage
因为grafana用户会在这个目录写入文件，直接设置777，比较简单粗暴

docker run -d -p 3000:3000 --name=grafana -v /opt/grafana-storage:/var/lib/grafana grafana/grafana-arm32v7-linux
```

```shell
docker run -d --gpus all --rm -p 9400:9400 nvidia/dcgm-exporter
## 分开两个比较好 端口映射不要写错了
docker run --name gpu0_exporter -d --gpus "device=0" --rm -p 9400:9400 nvidia/dcgm-exporter
docker run --name gpu1_exporter -d --gpus "device=1" --rm -p 9401:9400 nvidia/dcgm-exporter
```

