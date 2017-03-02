#!/usr/bin/env bash
cd $(dirname "$0")
yum install python3
pip3 install -r requirements.txt
python3 setup.py build install