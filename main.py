import requests
import json
import datetime
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import configparser

def main():
    # 本地数据
    fileContents = readFile()
    # 最新数据
    newContents = fetchNew()
    # 数据合并
    contents = fileContents
    for line in newContents:
        contents.append(line)
    # 数据去重
    contents = set(contents)
    # 邮件数据
    mailContents = []
    # 数据分拣
    fileContents = []
    today = str(datetime.date.today())
    for line in contents:
        if line[0:10] == today:
            # 今日数据, 00:00发送
            mailContents.append(line)
        elif line[0:10] > today:
            # 未来数据
            fileContents.append(line + "\n")
        else:
            pass
    # 发送邮件
    sendmail(mailContents)
    # 保存数据
    writeFile(fileContents)

# 获取最新数据
def fetchNew():
    url = "http://datacenter-web.eastmoney.com/api/data/v1/get?sortColumns=PUBLIC_START_DATE&sortTypes=-1&pageSize=10&pageNumber=1&reportName=RPT_BOND_CB_LIST&columns=SECURITY_CODE,SECURITY_NAME_ABBR,VALUE_DATE,RATING"
    request = requests.get(url)
    data = request.json()
    data = data['result']['data']
    contents = []
    for converDebt in data:
        record = converDebt['VALUE_DATE'][0:10] + ','
        record += converDebt['SECURITY_NAME_ABBR'] + ' ('
        record += converDebt['SECURITY_CODE'] + '),'
        record += converDebt['RATING']
        contents.append(record)
    return contents

# 读取本地文件
def readFile():
    f = Path('data.txt')
    fileContents = []
    if f.exists():
        f = open('data.txt')
        for line in f.readlines():
            fileContents.append(line.strip('\n'))
        f.close()
    return fileContents

# 写入本地文件
def writeFile(fileContents):
    fileContents.sort()
    f = open('data.txt', 'w')
    f.writelines(fileContents)
    f.close()

# 发送邮件提醒
def sendmail(mailContents):
    if mailContents:
        # 初始化配置
        config = configparser.ConfigParser()
        config.read('config.ini')
        smtpServer = config.get('SMTP', 'HOST')
        smtpPort = config.getint('SMTP', 'PORT')
        sender = config.get('SMTP', 'SENDER')
        password = config.get('SMTP', 'PASSWD')
        receiver = config.get('SMTP', 'RECEIVER')
        prefix = config.get('SMTP', 'PREFIX')
        # 邮件内容
        mailMsg = '<style>'
        mailMsg += 'table{border-collapse:collapse;}'
        mailMsg += 'th,td{border:1px solid black;text-align:center;padding:3px 5px;}'
        mailMsg += '</style>'
        mailMsg += '<table><thead><tr><th>申购日期</th><th>债券简称及代码</th><th>信用评级</th></tr></thead><tbody>'
        for converDebt in mailContents:
            line = converDebt.split(',')
            line[0] = line[0].replace('-', '年', 1)
            line[0] = line[0].replace('-', '月') + '日'
            mailMsg += '<tr><td>' + line[0] + '</td><td>' + line[1] + '</td><td>' + line[2] + '</td></tr>'
        mailMsg += '</tbody></table>'
        # plain文本格式 / html超文本格式
        message = MIMEText(mailMsg, 'html', 'utf-8')
        # 邮件标题
        today = str(datetime.date.today())
        today = today.replace('-', '年', 1)
        today = today.replace('-', '月') + '日'
        subject = prefix + today + '打新提醒'
        message['Subject'] = Header(subject, 'utf-8')
        # 发送地址
        message['From'] = sender
        # 接收地址
        message['To'] = receiver
        # 正式发送
        smtp = smtplib.SMTP_SSL(smtpServer, smtpPort)
        try:
            smtp.login(sender, password)
            smtp.sendmail(sender, receiver, message.as_string())
            log('[' + str(datetime.datetime.now())[0:19] + '] [OK] 向"' + receiver + '"发送邮件成功')
        except smtplib.SMTPException:
            log('[' + str(datetime.datetime.now())[0:19] + '] [Error] 向"' + receiver + '"发送邮件失败')
        finally:
            smtp.quit()
    else:
        # 邮件内容为空
        log('[' + str(datetime.datetime.now())[0:19] + '] [CANCEL] 取消向"' + receiver + '"发送邮件')

# 写入日志
def log(log):
    currentMonth = str(datetime.date.today())[0:7] + '-log'
    logFile = open('logs/' + currentMonth + '.txt', 'a')
    logFile.write(log + "\n")

# 测试函数
def test():
    pass
test()

# 主函数入口
main()