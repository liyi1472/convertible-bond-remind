import requests
import json
import datetime
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.header import Header
import configparser

def main():
    # 邮件数据
    mailContents = {'buy':[], 'sell':[]}
    # 文件数据
    fileContents = {'buy':[], 'sell':[]}
    # 数据分拣
    today = str(datetime.date.today())
    #  - 申购日期
    for line in fetchNewBuy():
        if line[0:10] > today:
            # 未来数据
            fileContents['buy'].append(line + "\n")
        elif line[0:10] == today:
            # 今日数据, 定时发送
            mailContents['buy'].append(line)
        else:
            pass
    #  - 上市日期
    for line in fetchNewSell():
        if line[0:10] > today:
            # 未来数据
            fileContents['sell'].append(line + "\n")
        elif line[0:10] == today:
            # 今日数据, 定时发送
            mailContents['sell'].append(line)
        else:
            pass

    # 保存数据
    writeFile('data/db-buy.txt', fileContents['buy'])
    writeFile('data/db-sell.txt', fileContents['sell'])
    # 发送邮件
    sendmail(mailContents)

# 获取最新数据
def fetchNew():
    # 获取数据项: 债券代码, 债券简称, 信用评级, 申购日期, 上市日期
    columns = 'SECURITY_CODE,SECURITY_NAME_ABBR,RATING,VALUE_DATE,LISTING_DATE'
    url = "http://datacenter-web.eastmoney.com/api/data/v1/get?sortColumns=PUBLIC_START_DATE&sortTypes=-1&pageSize=50&pageNumber=1&reportName=RPT_BOND_CB_LIST&columns=" + columns
    request = requests.get(url)
    data = request.json()
    return data['result']['data']

# 获取最新申购数据
def fetchNewBuy():
    contents = []
    today = str(datetime.date.today())
    for converDebt in fetchNew():
        if converDebt['VALUE_DATE'][0:10] < today:
            break
        record = converDebt['VALUE_DATE'][0:10] + ','
        record += converDebt['SECURITY_NAME_ABBR'] + ' ('
        record += converDebt['SECURITY_CODE'] + '),'
        record += converDebt['RATING']
        contents.append(record)
    return contents

# 获取最新上市数据
def fetchNewSell():
    contents = []
    today = str(datetime.date.today())
    for converDebt in fetchNew():
        if converDebt['LISTING_DATE'] is None:
            continue
        if converDebt['LISTING_DATE'][0:10] < today:
            break
        record = converDebt['LISTING_DATE'][0:10] + ','
        record += converDebt['SECURITY_NAME_ABBR'] + ' ('
        record += converDebt['SECURITY_CODE'] + '),'
        record += converDebt['RATING']
        contents.append(record)
    return contents

# 读取本地文件
def readFile(filename):
    f = Path(filename)
    fileContents = []
    if f.exists():
        f = open(filename)
        for line in f.readlines():
            fileContents.append(line.strip('\n'))
        f.close()
    return fileContents

# 写入本地文件
def writeFile(filename, fileContents):
    fileContents.sort()
    f = open(filename, 'w')
    f.writelines(fileContents)
    f.close()

# 发送邮件提醒
def sendmail(mailContents):
    if mailContents['buy'] or mailContents['sell']:
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
        #  - 申购新债
        if mailContents['buy']:
            mailMsg += '<table><thead><tr><th>申购日期</th><th>债券简称及代码</th><th>信用评级</th></tr></thead><tbody>'
            for converDebt in mailContents['buy']:
                line = converDebt.split(',')
                line[0] = line[0].replace('-', '年', 1)
                line[0] = line[0].replace('-', '月') + '日'
                mailMsg += '<tr><td>' + line[0] + '</td><td>' + line[1] + '</td><td>' + line[2] + '</td></tr>'
            mailMsg += '</tbody></table>'
            if mailContents['sell']:
                mailMsg += '<br>'
        #  - 上市新债
        if mailContents['sell']:
            mailMsg += '<table><thead><tr><th>上市日期</th><th>债券简称及代码</th><th>信用评级</th></tr></thead><tbody>'
            for converDebt in mailContents['buy']:
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
        subject = prefix + today
        if mailContents['buy']:
            subject += '打新提醒'
            if converDebt:
                subject += '&'
        if mailContents['sell']:
            subject += '上市提醒'
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
        log('[' + str(datetime.datetime.now())[0:19] + '] [CANCEL] 取消向发送邮件')

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