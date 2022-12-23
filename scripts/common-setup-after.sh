#!/bin/bash

# Run the Flask app, logs will be located in /app/logs.txt
sudo apt install python3-pip -y
cd /app
pip3 install -r requirements.txt
nohup python3 -u app.py > logs.txt 2>&1 &