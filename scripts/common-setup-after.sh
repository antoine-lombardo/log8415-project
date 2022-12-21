#!/bin/bash

# Run the python app
sudo apt install python3-pip -y
pip3 install -r /app/requirements.txt
nohup python3 /app/app.py &