#!/bin/bash

pkill -9 python
sleep 3
cd /home/pi && python driver2.py
