#!/bin/bash

# Run the python app
sudo apt install python3-pip -y
cd /app
pip3 install -r requirements.txt
nohup python3 -u app.py > logs.txt 2>&1 &