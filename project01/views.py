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
    name = input("请输入重命名的名字：")
    open('C:/Users/Administrator/Desktop/music/m4a/' + name + '.m4a', 'wb').write(myfiles.content)
    trans_m4a_to_other('C:/Users/Administrator/Desktop/music/m4a/' + name + '.m4a', "MP3", name)
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


# AI
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


class hot_topic:
    def __init__(self):
        self.title = ''
        self.url = ''


# 定义一维类数组
dataset = [hot_topic() for _ in range(50)]

weibodataset = []


def toutiao_hottop():
    # 头条热榜
    url = "https://www.toutiao.com/hot-event/hot-board/?origin=toutiao_pc&_signature=_02B4Z6wo00f01I-Pl9gAAIDAuKtThA1bExyPq5NAAET7a7mfwqCFLgw7GJ58uIZ--9Ndne.RucHvHUgiurQcQbuEs5KUHVRhbdgUnbXV9dJYEP0s.2YF6n4If1CkcE28.dcHdcfJsUUWCn5yf0"

    get = requests.get(url)

    js = json.loads(get.text)

    s = js['data']
    count = 0

    for i in s:
        # print(count)
        dataset[count].title = i['Title']
        dataset[count].url = i['Url']
        count = count + 1


def weibo_hottop():
    # 微博热榜
    url = "https://weibo.com/ajax/statuses/mineBand"

    header = {
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "zh,zh-CN;q=0.9,en;q=0.8",
        "client-version": "v2.46.23",
        "cookie": "SINAGLOBAL=9488690630316.621.1720757688318; SCF=AlQtRoYeJUWJuhShcrudguDlDHMGsGKuUmvmvH-9mBs1GMcMKeRI4dbCw2WLka6Hq31xxmYoH_aykDbxMKoLJfA.; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWa7Zwmzm4e685UVY0aKcJB5JpX5KMhUgL.FoMcSK-7So-7S0M2dJLoIpXLxK-L1-zLBK5LxKqL1--L1-e4S0zfS0241h57SBtt; ULV=1729822288040:11:7:7:9425830747247.729.1729822288005:1729758112091; ALF=1732970105; SUB=_2A25KJwkpDeRhGeFI7lcR9ivMzDuIHXVpXQThrDV8PUJbkNB-LW71kW1NfRHklF_umqRFKFdH6U1_GleiMGGPHyK0; WBPSESS=KoI2RxkVo4tCZ07sE--ZjWCxbG4uQJhD9wLVtTNQz52jL4Igr1kM6lnuHz_Goqgzh-JmaplDBZ43Lp68Te8T8yWlNlU03Jfk5MArIf0tUDB-lZdiBP32SDMCeNLmXxZtJD0yWyGrOLbjH70zDTvXYQ==; PC_TOKEN=8eafe52929; XSRF-TOKEN=1CwIK2dgqWzJHHiRuRxTSn6s",
        "priority": "u=1, i",
        "referer": "https://weibo.com/hot/mine",
        "sec-ch-ua": "\"Chromium\";v=\"130\", \"Microsoft Edge\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "server-version": "v2024.10.22.1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0",
        "x-requested-with": "XMLHttpRequest",
        "x-xsrf-token": "qiROIFrgVkA-rRd8G-yCczEt"
    }

    get = requests.get(url, headers=header)

    js = json.loads(get.text)

    realtime = js['data']['realtime']

    for i in realtime:
        weibodataset.append(i['word'])


# 热搜榜
def hot_topic(request):
    toutiao_hottop()
    weibo_hottop()
    # 键值对
    data = {
        't0': dataset[0].title,
        'u0': dataset[0].url,
        't1': dataset[1].title,
        'u1': dataset[1].url,
        't2': dataset[2].title,
        'u2': dataset[2].url,
        't3': dataset[3].title,
        'u3': dataset[3].url,
        't4': dataset[4].title,
        'u4': dataset[4].url,
        't5': dataset[5].title,
        'u5': dataset[5].url,
        't6': dataset[6].title,
        'u6': dataset[6].url,
        't7': dataset[7].title,
        'u7': dataset[7].url,
        't8': dataset[8].title,
        'u8': dataset[8].url,
        't9': dataset[9].title,
        'u9': dataset[9].url,

        't10': weibodataset[0],
        't11': weibodataset[1],
        't12': weibodataset[2],
        't13': weibodataset[3],
        't14': weibodataset[4],
        't15': weibodataset[5],
        't16': weibodataset[6],
        't17': weibodataset[7],
        't18': weibodataset[8],
        't19': weibodataset[9],
    }
    # data = {
    #     't0': '百度',
    #     'u0': 'http://www.baidu.com',
    #     't1': '百度',
    #     'u1': 'http://www.baidu.com',
    #     't2': '百度',
    #     'u2': 'http://www.baidu.com',
    #     't3': '百度',
    #     'u3': 'http://www.baidu.com',
    #     't4': '百度',
    #     'u4': 'http://www.baidu.com',
    #     't5': '百度',
    #     'u5': 'http://www.baidu.com',
    # }
    response = JsonResponse(data)
    return response


# 主界面
def main_page(request):
    return render(request, "main.html")