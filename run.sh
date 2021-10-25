#!/bin/bash

/usr/bin/docker run --rm \
--name=convertible-bond-remind \
--net=tomato \
-v /usr/share/zoneinfo/Asia/Shanghai:/etc/localtime:ro \
-v /opt/tomato/python/convertible-bond-remind:/app \
python3:latest \
python main.py
