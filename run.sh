#!/bin/bash

docker run -it --rm \
--name=convertible-bond-remind \
--net=tomato \
-v /opt/tomato/python/convertible-bond-remind:/app \
python3:latest \
python main.py