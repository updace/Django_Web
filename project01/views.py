import json
import hashlib
import requests
from django.db.models.expressions import result
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from TestModel.models import *
from pydub import AudioSegment
from django.db import connection
import markdown
import qianfan
import webbrowser
from django.http import HttpResponse


def trans_m4a_to_other(filepath, hz, name):
    song = AudioSegment.from_file(filepath)
    song.export("C:/Users/Administrator/Desktop/music/mp3/" + name + "." + str(hz), format=str(hz))


def music_page(request):
    return render(request, 'music.html')


def download_music(request):
    print("11111")
    url = request.GET.get('url')
    myfiles = requests.get(url)
    # name = input("请输入重命名的名字：")
    # open('C:/Users/Administrator/Desktop/music/m4a/' + name + '.m4a', 'wb').write(myfiles.content)
    # trans_m4a_to_other('C:/Users/Administrator/Desktop/music/m4a/' + name + '.m4a', "MP3", name)
    result = '111'
    response = JsonResponse({'result': result})
    return response


# 登录界面
def login(request):
    # s="# 111"
    # print(markdown.markdown(s))
    name = request.POST.get('Name')
    password = request.POST.get('Password')
    print(name, password)

    # 以用户名查询数据库，如果用户名不存在，提示用户名不存在，如果用户名存在但密码不存在提示密码错误，如果密码正确则跳转到主界面（目前以翻译界面代替）
    # 做非空处理
    if name is not None or password is not None:
        q = Account.objects.filter(username=name).values("username", "password")
        # 用户存在
        if q:
            u = q[0]["username"]
            p = q[0]["password"]
            print(q[0]["username"])
            print(q[0]["password"])

            # 账号密码一直
            if u is not None and p is not None and name == u and password == p:
                return redirect("/main/")
            else:
                return render(request, "login.html")
        else:
            return render(request, "login.html")
    else:
        return render(request, "login.html")


# 注册界面
def register(request):
    # 要用name属性，不能用id属性！！！
    name = request.POST.get('Name')
    password = request.POST.get('Password')
    password_again = request.POST.get('Password_again')
    print(name, password, password_again)

    # 查询数据库，看用户名有没有重复，有重复直接返回用户已经存在，不允许注册同名用户！！！
    q = Account.objects.filter(username=name)

    # 不为空则，写入数据库
    if name is not None and password is not None and password_again is not None:
        a = Account(username=name, password=password)
        a.save()
        # 返回登录界面
        return redirect("/")

    # 查询数据库，看有没有相同的账号存在，如果有就给出提示，并不让注册（AJax)

    # 检查两次输入的密码是否一致，如果不是，就提示两次输入的密码不一致提示重新输入(前端实现)

    # 都检查无误将用户名和密码写入数据库，弹窗提醒登录成功！并返回登录界面

    # 用用户名区分不同的账号（数据库的主键），当用户输入用户名后查询数据库判断有没有同名账号，如果有就不让注册
    return render(request, "register.html")


# 翻译
def ai(question):
    # 获取token
    Tk_url = "https://aip.baidubce.com/oauth/2.0/token?client_id=Jaq24UTU9cl9DY9nFnEE5K6s&client_secret=ERNtSbLSFXMXA8H4kSN6pUCp2hgwaX1s&grant_type=client_credentials"
    payload = json.dumps("")
    Tk_headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", Tk_url, headers=Tk_headers, data=payload)
    token = str(response.json().get("access_token"))

    url = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/ernie-3.5-8k-0701?access_token=" + token
    headers = {
        'content-type': 'application/json',
    }
    payload = json.dumps(
        {
            "messages":
                [
                    {
                        "role": "user",
                        "content": question
                    }
                ]
        }
    )
    response = requests.request("POST", url, headers=headers, data=payload)
    result = json.loads(response.text)
    print(result["result"])
    return result["result"]


#
def ai_page(request):
    return render(request, "yiyan.html")


@csrf_exempt
def answer(request):
    que = request.POST.get('question')
    result = ai(que)

    response = JsonResponse({'result': markdown.markdown(result)})
    return response


# 翻译页面
def translate_page(request):
    return render(request, "translate.html")


# MD5加密
def md5_encrypt(data):
    md5 = hashlib.md5()
    md5.update(data.encode('utf-8'))
    return md5.hexdigest()


# 百度翻译
def baidu_translate(text, source, target):
    url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
    appid = '20240307001986172'
    key = 'iNI__jOysGRicVgGVWfp'
    rand = '11'
    sign = md5_encrypt(appid + text + rand + key)
    query = {
        'q': text,
        'from': source,
        'to': target,
        'appid': appid,
        'salt': rand,
        'sign': sign
    }
    get = requests.get(url, params=query)
    # print(get.status_code)
    dic = json.loads(get.text)  # 解析有效的JSON字符串并将其转换为Python字典
    print(dic['trans_result'][0]['dst'])  # trans_result数组
    return dic['trans_result'][0]['dst']


# 获取前端输入数据，进行翻译，并返回到前端
@csrf_exempt
def trans_func(request):
    # 获取textarea输入
    content = request.POST.get('content')
    print(content)

    # 解析源语言和目标语言
    source = request.POST.get('source_lang')
    target = request.POST.get('target_lang')

    # 返回翻译结果，输出到网页
    result = baidu_translate(content, source, target)
    # print(result)
    # print(type(result))
    response = JsonResponse({'result': result})
    return response


# 要加下面一句请求，否则服务器拒收
@csrf_exempt
def search(request):
    print('111')
    question = request.POST.get('question')

    t = baidu_translate(question, 'zh', 'en')

    url = "https://cn.bing.com/search?mkt=zh-cn&pc=LNVB&FORM=LNOVCH&q="
    webbrowser.open(url + t)
    result = 'ss'
    response = JsonResponse({'result': result})
    return response


def toutiao_hottop():
    # 头条热榜
    url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc&_signature=_02B4Z6wo00f01I-Pl9gAAIDAuKtThA1bExyPq5NAAET7a7mfwqCFLgw7GJ58uIZ--9Ndne.RucHvHUgiurQcQbuEs5KUHVRhbdgUnbXV9dJYEP0s.2YF6n4If1CkcE28.dcHdcfJsUUWCn5yf0"

    get = requests.get(url)

    js = json.loads(get.text)

    s = js['data']

    for i in s:
        print(i['Title'])
        print(i['Url'])


def weibo_hottop():
    # 微博热榜
    url = "https://weibo.com/ajax/statuses/mineBand"

    header = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh,zh-CN;q=0.9,en;q=0.8",
        "client-version": "v2.46.22",
        "cookie": "SINAGLOBAL=9488690630316.621.1720757688318; SCF=AlQtRoYeJUWJuhShcrudguDlDHMGsGKuUmvmvH-9mBs1GMcMKeRI4dbCw2WLka6Hq31xxmYoH_aykDbxMKoLJfA.; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWa7Zwmzm4e685UVY0aKcJB5JpX5KMhUgL.FoMcSK-7So-7S0M2dJLoIpXLxK-L1-zLBK5LxKqL1--L1-e4S0zfS0241h57SBtt; ULV=1725277832968:4:1:1:6787032062709.948.1725277832917:1723801918789; ALF=1731742949; SUB=_2A25KFM-1DeRhGeFI7lcR9ivMzDuIHXVpaE19rDV8PUJbkNANLRHakW1NfRHklGrR9Bh0OnWKnko5LQ_4-42fstje; PC_TOKEN=c53c742f36; XSRF-TOKEN=a-rUWmGSZBa6OVR5-gic8BUB; WBPSESS=KoI2RxkVo4tCZ07sE--ZjWCxbG4uQJhD9wLVtTNQz52jL4Igr1kM6lnuHz_Goqgzh-JmaplDBZ43Lp68Te8T8wmkh4AZUmEkLhmOQYqbJInulQfjsET4Ba9QFCXut6ejaMyXq8WzGVInuorvHoXDzQ==",
        "priority": "u=1, i",
        "referer": "https://weibo.com/hot/mine",
        "sec-ch-ua": "\"Chromium\";v=\"130\", \"Microsoft Edge\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "server-version": "v2024.10.17.1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "x-requested-with": "XMLHttpRequest",
        "x-xsrf-token": "a-rUWmGSZBa6OVR5-gic8BUB"
    }

    get = requests.get(url, headers=header)

    js = json.loads(get.text)

    realtime = js['data']['realtime']

    count = 0

    for i in realtime:
        print(count, '：', i['word'])
        count = count + 1


# 热搜榜
def hot_topic(request):
    return HttpResponse("<a href='https://www.runoob.com/'>菜鸟教程</a>")


# 主界面
def main_page(request):
    return render(request, "main.html")
