FROM python:latest
# 定义工作目录
WORKDIR /app
# 换国内源
RUN sed -i "s@http://deb.debian.org@http://mirrors.aliyun.com@g" /etc/apt/sources.list
RUN rm -rf /var/lib/apt/lists/*
RUN apt-get update
# 安装依赖: 
# ① sendmail (SMTP依赖)
RUN apt-get install -y sendmail
# 清理缓存
RUN rm -rf /var/lib/apt/lists/*
# 换国内源
RUN pip config set global.index-url http://mirrors.aliyun.com/pypi/simple
RUN pip config set install.trusted-host mirrors.aliyun.com
RUN pip install pip -U
# 安装 Python 依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
