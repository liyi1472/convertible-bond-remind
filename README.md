# 打新债邮件提醒

部署到自有服务器配合CRON定时任务使用。

```shell
00 09 * * * /opt/tomato/python/convertible-bond-remind/run.sh >/dev/null 2>&1
```



## Bug

限制 Python 版本在 3.9 以下，否则会导致 SMTP 出现间歇性的 SSL 未知错误。

![](python-version-bug(1).png)

回滚 Python 版本为 3.9.7 以后问题消失：

![](python-version-bug(2).png)
