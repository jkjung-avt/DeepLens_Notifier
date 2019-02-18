#! /bin/bash
#
# start-up script for DeepLens Notifier agent

source /opt/intel/computer_vision_sdk/bin/setupvars.sh
sleep 10
cd /home/aws_cam/project/DeepLens_Notifier
source ./setvars.sh
python3 ./agent.py
