# 打新债邮件提醒

部署到自有服务器配合CRON定时任务使用。

①运行错误不发送系统邮件：

```shell
00 11 * * * /opt/tomato/python/convertible-bond-remind/run.sh
```

②运行错误发送系统邮件：

```shell
00 11 * * * /opt/tomato/python/convertible-bond-remind/run.sh >/dev/null 2>&1
```

