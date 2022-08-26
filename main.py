'''
Time: 2022/08/18 14:19:21
Author: Yuzhouxing
GitHub: https://github.com/yuzhouxing-git
Project: Fishc
Version: V1.0
File: main.py
Software: python3.7.4
'''

import requests
import re
import hashlib
import time

# 获取formhash的函数
def getFormhash(cookies, headers):
    url = "https://fishc.com.cn/member.php?mod=logging&action=login"
    response = requests.get(url,headers=headers,cookies=cookies)
    if response.status_code == 200:
        response.encoding = "gbk"
        cookies.update(requests.utils.dict_from_cookiejar(response.cookies))
        formhash = re.findall(r'<input type="hidden" name="formhash" value="(.+)" />',response.text)[0]
        return {'code':0,'formhash':formhash,'cookies':cookies}
    else:
        return {'code':1}

# 登录函数
def login(username, password, question, answer, formhash, cookies, headers):
    url = "https://fishc.com.cn/member.php?mod=logging&action=login&loginsubmit=yes&loginhash=LuRQW&inajax=1"
    questionDict = {
        "":"0",
        "母亲的名字":"1",
        "爷爷的名字":"2",
        "父亲出生的城市":"3",
        "您其中一位老师的名字":"4",
        "您个人计算机的型号":"5",
        "您最喜欢的餐馆名称":"6",
        "驾驶执照最后四位数字":"7"
    }

    # md5加密
    md5 = hashlib.md5()
    md5.update(password.encode("utf-8"))
    password = md5.hexdigest()

    # 安全提问处理
    questionid = questionDict[question]

    # post提交数据
    data = {
        "formhash":formhash,
        "referer":"https://fishc.com.cn/",
        "username":username.encode('gbk'),
        "password":password,
        "questionid":questionid,
        "answer":answer.encode("gbk"),
        "cookietime":"2592000"
    }

    response = requests.post(url,headers=headers,data=data,cookies=cookies)
    if response.status_code == 200:
        response.encoding = "gbk"
        cookies.update(requests.utils.dict_from_cookiejar(response.cookies))
        # 判断是否登录成功
        if "欢迎您回来" in response.text:
            return {'code':0,'cookies':cookies}
        else:
            return {'code':1}
    else:
        return {'code':1}

# 签到函数
def sign(formhash, cookies, headers):
    url = "https://fishc.com.cn/plugin.php?id=k_misign:sign&operation=qiandao&format=text&formhash=%s" % formhash
    response = requests.get(url,headers=headers,cookies=cookies)
    if response.status_code == 200:
        response.encoding = "gbk"
        return {'code':0,'text':response.text}
    else:
        return {'code':1}

# 保存日志
def saveLog(msg):
    with open('sign.log','a') as f:
        f.write(time.ctime()+"  "+msg+"\n")

# 主函数
def main(username, password, question, answer):
    # 初始化变量
    cookies = {}
    headers = {
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }

    # 获取登录formhash
    res = getFormhash(cookies, headers)
    if res['code'] == 0:
        formhash = res['formhash']
        cookies = res['cookies']
    else:
        return username+'登录formhash获取失败'

    # 登录
    res = login(username,password,question,answer,formhash,cookies, headers)
    if res['code'] == 0:
        cookies = res['cookies']
    else:
        return username+'登录失败'

    # 获取签到formhash
    res = getFormhash(cookies, headers)
    if res['code'] == 0:
        formhash = res['formhash']
        cookies = res['cookies']
    else:
        return username+'签到formhash获取失败'

    # 签到
    res = sign(formhash, cookies, headers)
    if res['code'] == 0:
        return username+re.findall(r'<root><!\[CDATA\[(.+)\]\]></root>',res['text'])[0]
    else:
        return username+'签到失败'

# 用户名和密码设置
username = "用户名"
password = "密码"
# 安全提问的名称,无安全提问可设置为空
question = ""
# 安全提问的答案,无安全提问可设置为空
answer = ""
# 签到并保存日志
saveLog(main(username,password,question,answer))
