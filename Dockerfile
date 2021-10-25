FROM python:latest
WORKDIR /app

RUN sed -i "s@http://deb.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list
RUN apt-get update && \
    apt-get install -y \
    sendmail
RUN rm -rf /var/lib/apt/lists/*

RUN pip config set global.index-url http://mirrors.aliyun.com/pypi/simple
RUN pip config set install.trusted-host mirrors.aliyun.com
RUN pip install pip -U

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
