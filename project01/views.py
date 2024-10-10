import json
import hashlib
import requests
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import markdown
import qianfan


# 登录界面
def login(request):
    name = request.POST.get('Name')
    password = request.POST.get('Password')
    print(name, password)

    # 以用户名查询数据库，如果用户名不存在，提示用户名不存在，如果用户名存在但密码不存在提示密码错误，如果密码正确则跳转到主界面（目前以翻译界面代替）

    # name 和 password 字段是字符串类型
    if name == "222" and password == "222":
        return redirect("/translate/")
    else:
        return render(request, "login.html", {'name': name, 'password': password})


# 注册界面
def register(request):
    # 要用name属性，不能用id属性！！！
    name = request.POST.get('Name')
    password = request.POST.get('Password')
    password_again = request.POST.get('Password_again')
    print(name, password, password_again)

    # 查询数据库，看有没有相同的账号存在，如果有就给出提示，并不让注册

    # 检查两次输入的密码是否一致，如果不是，就提示两次输入的密码不一致提示重新输入

    # 都检查无误将用户名和密码写入数据库，弹窗提醒登录成功！并返回登录界面

    # 用用户名区分不同的账号（数据库的主键），当用户输入用户名后查询数据库判断有没有同名账号，如果有就不让注册
    return render(request, "register.html")


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


def ai_page(request):
    return render(request, "yiyan.html")


@csrf_exempt
def answer(request):
    que = request.POST.get('question')
    result = ai(que)

    response = JsonResponse({'result': result})
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
