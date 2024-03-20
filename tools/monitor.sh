#!/bin/bash

cd /home/ly/tools/

# 进程挂了直接重启
status=`ps aux | grep bafa.py | grep -v grep | wc -l`
if [ $status -eq 0 ]
then
    nohup /home/ly/miniconda3/bin/python bafa.py >> run_bafa.log 2>&1 &
fi

# 如果进程挂了就重启
status=`ps aux | grep jupyter-lab | grep -v grep | wc -l`
if [ $status -eq 0 ]
then
    nohup /home/ly/miniconda3/bin/jupyter-lab --no-browser --ip 0.0.0.0 --port 8888 > log/jupyter.log 2>&1 &
fi

# ddns 进程
/usr/bin/python3 ./ddns.py