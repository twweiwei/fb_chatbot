from django.shortcuts import render
from django.views import generic
from django.http.response import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from hanziconv import HanziConv
from django.conf import settings
from urllib.parse import quote
import json, requests, re, random, os, sys, string
import urllib.request
import jieba
import jieba.posseg
import jieba.analyse
import importlib
import googlemaps
import time
import os.path
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import urllib.parse
import html5lib
import urllib3
pd.set_option('display.max_columns', 500)
pd.set_option('display.max_rows', 500)
# from flask import Flask, request, session, g, redirect, url_for, abort, \
#     render_template, flash 
# 結巴所在目錄
# sys.path.append(r'd:\moyege\work\@project\1221google_map\chatbot\chatbot\lib\site-packages')

# Create your views here.

#學妹
PAGE_ACCESS_TOKEN = "EAAGVzPZCla0sBAH5ZCh9ZCB3FR1gvZAVNZAMPTDZAhWud5dAp2AMkXvqjLiDnAMOWPZB0KZC7jv5YGL4E46cluqVpYlNZB0TtqOpyTnxZBSir5hcOBLxLZChPEocYCWD1uQ0rgUodZAPm6f3MXyC3DRfQGAP90D1H0Rwns7huXvCZCwYCzwZDZD"
#旅遊小幫手
# PAGE_ACCESS_TOKEN = "EAAEQtzvtPZCYBAFKK7masLlbQnRaw8zrWRpUYvUzycUJSHyI35fzebLdNg6dOdpeLnpMiuSgTfBVxZCbNl37hqQxnGYqEFmhVlSmNZCBTpplXE6t7cxD9EGZAkaSZCWCqbyszAtfXobXvWKVGa65nZChKZAufAjcq0JNAEspnoyXQZDZD"
user_url = os.path.dirname(os.path.abspath("views.py"))

web_id = '1785453378183306' #這個是粉專的id 要改這個程式才不會連自己說的話都接收 學妹

# web_id = '1778286295798129' #這個是粉專的id 要改這個程式才不會連自己說的話都接收 jerry

sys.setrecursionlimit(2000)
#print(sys.getrecursionlimit())

# # 對應關鍵字直接回覆
# jokes = {
#          'stupid': ["""Yo' Mama is so stupid, she needs a recipe to make ice cubes.""",
#                     """Yo' Mama is so stupid, she thinks DNA is the National Dyslexics Association."""]}

# 建立除冗字與相關類型判斷關鍵字之字典
dict = {"location":["去","往哪","在哪裡","在哪","哪","位置","地址","地點","方向","怎麼走","走","哪裡"],
        "toilet":["廁所","尿","肛門","幽門","大小號","大小便","大便","拉屎","屎","撇條","排遺","排泄","便便",
                  "便所","化妝室","洗手間","大號","小號","尿急","棒賽","尿尿","放尿","噓噓","廁","尬賽","烙賽",
                  "肚子不舒服","月經","姨媽","肚子痛","米田共","想吐","糞","拉希","拉稀","腸胃","霸豆","巴豆",
                  "翔","小便","腹瀉","腹脹","上吐下瀉","嘔吐","肚子有點痛","肚子疼","脹","吐","瀉"],
        "營業時間":["營業時間","幾點關門","幾點","入場","關門","開門","開店","開始","開放","幾號"],
        "電話":["電話","專線","號碼","連絡","聯絡","聯絡方式","客服"],
        "介紹":["簡介","特色","高度","長度","多高","多長","歷史","介紹","內容","文化","活動","官網","資訊","限時","外送","票價","網站","網址","網頁"],
        "價錢":["價格","多少錢","錢","很貴","貴不貴","便宜","花費","費用"],
        "wifi":["wifi","WIFI","Wifi","網路","上網","無線","Wi-Fi"],
        "菜單":["菜單","餐點","低消","飲料","葷","素","蛋奶素","食物","美食","menu","Menu","MENU",'飲料',"吃","喝","好吃的"],
        "評價":["評價","好吃","好玩","有趣"],
        "充電":["插座","充電","電源","電","手機"],
        "公車":["公車","公車站","搭公車","坐公車","公車站牌"],
        "plane":["飛機", "航班", "延誤"],
        "高捷":["高捷","高雄捷運"],
        "高鐵":["高鐵","高速鐵路","高鐵票","高鐵的票"],
        "台鐵":["台鐵","臺鐵","火車","台灣鐵路","臺灣鐵路","莒光號","自強號","普悠瑪","坐太魯閣","搭太魯閣","台鐵票","臺鐵票","火車票"],
        "問題":["沒問題了","我還有問題","我有建議要說","Jerry能幫你什麼"],
        "演唱會":["演唱會"],
        "ATM":["ATM","atm","Atm","轉帳","領錢","提款","金融卡"],
        "你好":["你好","早安","午安","晚安","哈囉","嗨","呦","你可以幹嘛","測試","test","hi","hello","哈摟","回答","你可以做什麼"],
        "weather":["天氣","氣溫","溫度","會熱","會冷","很冷","很熱","會下雨","氣象"],
        "Ubike":["Ubike","ubike","UBike","UBIKE","YouBike","YOUBIKE","Youbike","微笑單車"],
        "北捷":["北捷","台北捷運","臺北捷運","捷運","MRT","Mrt","mrt"]}

idcheck={} #判斷是否為多輪問答用
idrecevied_message = {} #將recevied_message用id的方式儲存才不會被其他使用者影響
idontknow_check = ''
longlat={}
# D1, D2, D3, D4, D5, D6, D7, D8, D9, D10, D11= 0
# toolong = 0
# 指定變數為字典內各項的元素數量，以逐步檢測
# toolong = len(dict["unnecessary"])
D1 = len(dict["toilet"])
# D2 = len(dict["乘車"]) 沒用了
D3 = len(dict["價錢"])
D4 = len(dict["location"])
D5 = len(dict["營業時間"])
D6 = len(dict["電話"])
D7 = len(dict["介紹"])
D8 = len(dict["wifi"])
D9 = len(dict["菜單"])
D10 = len(dict["評價"])
D11 = len(dict["充電"])
D12 = len(dict["plane"])
D13 = len(dict["高捷"])
D14 = len(dict["高鐵"])
D15 = len(dict["台鐵"])
D16 = len(dict["你好"])
D17 = len(dict["問題"])
# D18 = len(dict["演唱會"]) #暫時不用
D19 = len(dict["ATM"])
D20 = len(dict["Ubike"])
D21 = len(dict["weather"])
D22 = len(dict["公車"])
D23=len(dict["北捷"])
# 將toolong檔案內文字轉換
# ?
toolongf_v = [line.strip().encode('utf-8') for line in open(user_url+r'\GooglemapBot\toolong.txt',encoding = 'utf8').readlines()]
idd=''
toiletlat=''
toiletlong=''
vba = []
nba = {}
ncityba = {}
wrongcheck = {}
seq=0
seq_2=0
seq_4=0
firsttime={}
user_payload=''
address_add_num = 0
else_add_num = 0
weather_num = 0
bus_num = 0
cityshiannum = 0
seq_check = {}
seq_check2 = {}
seq_check3 = {}
seq_check4 = {}
weather_today = time.strftime("%H")
last_word = {}
bus_chinese = ''
bus_diraction = ''
ture_nba = {}
check_peijietime = 0
jj = {}
Gmap_num = {}
Departure = ''
MRT_direction = {}

class GMBotView(generic.View):
        # 在class based views 里面，args 有两个元素，一个是self, 第二个才是request
        # *args是接受很多的值，在Python叫做tuple。
        # **kwargs是接受dictionary。

    def get(self, request, *args, **kwargs):

        # Verify Token = botprojecttest
        if self.request.GET['hub.verify_token'] == 'botprojecttest':
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')

    # The get method is the same as before.. omitted here for brevity
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    # 將接收到的文字內容以Json形式讀取，而後轉為字串
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))

        global toiletlat,toiletlong,idd,seq,seq_2,seq_3,user_payload,seq_4
        # user_details_url_test = "https://graph.facebook.com/v2.6/me/messenger_profile?access_token="+PAGE_ACCESS_TOKEN
        # user_details_params_test = {'fields':'first_name,last_name,profile_pic,get_started,greeting', 'access_token':PAGE_ACCESS_TOKEN}
        # user_details_test = requests.get(user_details_url_test, user_details_params_test).json()
        if 'message' in incoming_message['entry'][0]['messaging'][0]:
            if 'attachments' in incoming_message['entry'][0]['messaging'][0]['message']:
                if 'payload' in incoming_message['entry'][0]['messaging'][0]['message']['attachments'][0]:
                    if 'coordinates' in incoming_message['entry'][0]['messaging'][0]['message']['attachments'][0]['payload']:
                        seq = incoming_message['entry'][0]['messaging'][0]['message']['seq']
                        # print(seq)
                        # print('if外的seqif外的seqif外的seqif外的seqif外的seqif外的seq')
                        if seq != seq_2:
                            toiletlat=incoming_message['entry'][0]['messaging'][0]['message']['attachments'][0]['payload']['coordinates']['lat']
                            toiletlong=incoming_message['entry'][0]['messaging'][0]['message']['attachments'][0]['payload']['coordinates']['long']
                            seq_2 = seq
                            # print(seq, seq_2)
                            # print('內的seq內的seq內的seq內的seq內的seq內的seq內的seq內的seq')
                        # latlist.append(toiletlat)
                        # longlist.append(toiletlong)
        if 'message' in incoming_message['entry'][0]['messaging'][0]:
            if 'quick_reply' in incoming_message['entry'][0]['messaging'][0]['message']:
                print("seq and seq_4\n\n")
                print(seq,seq_4)
                print("seq and seq_4\n\n")
                # if seq != seq_4 :
                print("有進seqseqseqseqseq")
                user_payload=incoming_message['entry'][0]['messaging'][0]['message']['quick_reply']['payload']
                    # seq_4 = seq

        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                if 'message' in message:

                    # Print the message to the terminal

                    if 'text' in message ['message']:
                        # 顯示message此JSON檔內容
                            # {'timestamp':__, //作用未知
                            #  'message': 
                            #       {'mid': '__', //會變動，作用未知
                            #        'text': '__', //收到傳送的message訊息
                            #        'is_echo': True, //固定為True，作用未知
                            #        'app_id': __, //連結到的應用程式編號
                            #        'seq': __}, //會變動，作用未知
                            # 'sender': {'id': '__'}, //粉專ID
                            # 'recipient': {'id': '__'}} //訊息傳送者ID
                            # {'error': {
                            #   'code': 100, //固定，作用未知
                            #   'error_subcode': 2018001, //固定，作用未知
                            #   'message': '(#100) No matching user found', //固定，作用未知
                            #   'type': 'OAuthException', //固定，作用未知
                            #   'fbtrace_id': '__'}} //會變動，作用未知
                        # print(message)

                        # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                        # are sent as attachments and must be handled accordingly.
                        idd = message['sender']['id']
                        if idd != web_id:
                            seq_check.update({idd:incoming_message['entry'][0]['messaging'][0]['message']['seq']})
                        if idd != web_id and idd not in seq_check2:
                            seq_check2.update({idd:'0'})
                            wrongcheck.update({idd: 0 })
                            Gmap_num.update({idd: 0 })
                        if idd != web_id and seq_check[idd] != seq_check2[idd]:
                            print("\n\n\n")
                            print(incoming_message)
                            print("上面是incoming message上面是incoming message上面是incoming message\n\n\n")
                            # 避免傳送到自己的文字 idd=自己粉專id
                            seq_check2.update({idd:seq_check[idd]})
                            post_facebook_message_text(message['sender']['id'], message['message']['text'])                          
                            print(idd)
                            if idd in seq_check2:
                                print(seq_check[idd], seq_check2[idd])
                            print("裡面的seq裡面的seq裡面的seq裡面的seq裡面的seq裡面的seq裡面的seq")
                    elif toiletlong!='':
                        # 可以接收文字以外訊息 kkk是無意義文字
                        idd=message['sender']['id']
                        if idd != web_id:
                            seq_check3.update({idd:incoming_message['entry'][0]['messaging'][0]['message']['seq']})
                        if idd!=web_id and idd not in seq_check4:
                            seq_check4.update({idd:'0'})
                        if idd != web_id and seq_check3[idd] != seq_check4[idd]:
                            longlat.update({idd:[toiletlong,toiletlat]})
                            print(longlat, "這是longlat")
                            seq_check4.update({idd:seq_check3[idd]})
                            post_facebook_message_text(message['sender']['id'], 'kkk')
                            print("非文字唷")

        return HttpResponse()
# @app.route(API_ROOT + FB_WEBHOOK, methods=['POST'])
# def fb_handle_message(self, request, *args, **kwargs):
#     message_entries = json.loads(request.data.decode('utf8'))['entry']
#     for entry in message_entries:
#         messagings = entry['messaging']
#         for message in messagings:
#             sender = message['sender']['id']
#             if message.get('message'):
#                 text = message['message']['text']
#                 print("{} says {}".format(sender, text))
#                 message2=text
#     return message2


# 檢測冗字(JIEBA) 將輸入文字斷成詞語
def jieba_check(long_sentence):
    allba = []
    idontknow_reply = ["1","2","3","4","5","6","7"]
    global vba,nba,user_url
    
    jieba.load_userdict(user_url+r"\GooglemapBot\jieba.txt")
    vocabulary = jieba.posseg.cut(long_sentence)

    for iba in vocabulary:
        allba.append((iba.word))
        print(iba.word,iba.flag)
        if iba.flag == 'vbuy':
            vba.append(('買'))
            print(vba, "這是vba")
        if  iba.flag == 'ns':
            nba.update({idd:iba.word})
            print(nba)
            print("這裡是nba這裡是nba這裡是nba這裡是nba這裡是nba這裡是nba這裡是nba這裡是nba這裡是nba")
        if iba.flag == 'ncity':
            ncityba.update({idd:iba.word})
            print(ncityba)
        if iba.flag == 'n':
            ture_nba.update({idd:iba.word})

    return allba

startstation=''
endstation=''
stationtime=''
thsr_start={}
thsr_end={}
thsr_time_arrive=''
thsr_time_depart={}
Train_Departure={}
Train_Destination={}
Train_DepartTime={}
Train_ArriveTime=''
address_add_name = '' #給建議用
address_add_text = '' #給建議用
# def getstart(fbid,recevied_message,post_message_url):

#     if idd in firsttime:
#         print("用過了拉用過了拉")
#     else:
#         firsttime.update({idd:['used']})
#         response_msg = json.dumps({"recipient":{"id":fbid},"message":{"greeting":[
#         {
#              "locale":"default",
#              "text":"Hello!",
#         },
#         {
#             "locale":"zh_TW",
#             "text":"哈囉哈囉你好挖"
#         }
#         ]
#         }, 
#         "get_started":{"payload":"<GET_STARTED_PAYLOAD>"}
#         })
#         status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
def check_dict(fbid, recevied_message):
    global vba, nba, user_payload, idontknow_check, seq_check, seq_check2,last_word
    ans = 0
    # recevied_message = ""
    post_message_url = 'https://graph.facebook.com/v3.0/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    
    # # 檢測冗字
    # for t in range(toolong):
    #     if recevied_message.find(dict["unnecessary"][t]) >= 0 :
    #         dle = recevied_message.find(dict["unnecessary"][t])
    #         dle_long = len(dict["unnecessary"][t])
    #         dle2 = dle + dle_long
    #         recevied_message = recevied_message[:dle] + recevied_message[dle2:]

    # sentence = jieba_check(recevied_message)
    #結巴會怪怪澳改(在哪ˋ)
    # getstart(fbid,recevied_message,post_message_url)
    sentence_ba=[]
    sentence_ba=jieba_check(recevied_message)
    sentence=recevied_message

    print(idcheck,"這是idcheck")
    print(nba,"這是nba")
    print(recevied_message,"這是recevied_message")
    print(idrecevied_message,"這是idrecevied_message")
    print(ans,"這是ans")
    print(longlat,"這是longlat")
    print(Gmap_num,"這是Gmap_num")
    print("又重來了又重來了又重來了又重來了又重來了又重來了又重來了又重來了又重來了")
    # 檢測是否為多輪回答
    if idd in idcheck:
        #要把二次傳的訊息加到idd裡面喔喔喔喔喔喔喔喔喔
        print("進idcheck了進idcheck了進idcheck了進idcheck了進idcheck了進idcheck了")
        idrecevied_message.update({idd:recevied_message})
        print("\n\n\n")
        print(idcheck,"這是idcheck裡的idcheck")
        print(nba,"這是nba")
        print(recevied_message,"這是idcheck裡的recevied_message")
        print(idrecevied_message,"這是idcheck裡的idrecevied_message")
        print(ans,"這是idcheck裡的ans")
        print(longlat,"這是idcheck裡的longlat")
        print(Gmap_num,"這是idcheck裡的Gmap_num")
        print("\n\n\n")

        #廁所(收到使用者位置後)--------------------------------------------------徹底完成了 除了師大toilet json檔
        for i1 in range(D1):
            if idd in idcheck:
                if idcheck[idd].find(dict["toilet"][i1]) >= 0 and ans <= 0:
                    toilet(idd,post_message_url)
                    ans += 2

        # 高捷多輪回答----------------目標縮小為台北後就沒再更新了
        for i13 in range(D13):
            if idd in idcheck:
                if idcheck[idd].find(dict["高捷"][i13]) >= 0 and ans<=0:
                    kao(i13,fbid,post_message_url,recevied_message)
                    ans += 2

        # 高鐵多輪回答------------------------------------------------------------徹底完成了
        for i14 in range(D14):
            if idd in idcheck:
                if idcheck[idd].find(dict["高鐵"][i14]) >= 0 and ans<=0 and '買' not in vba:
                    thsr(fbid,post_message_url,recevied_message)
                    ans += 2

        # 臺鐵多輪回答------------------------------------------------------------徹底完成了
        for i15 in range(D15):
            if idd in idcheck:
                if idcheck[idd].find(dict["台鐵"][i15]) >= 0 and ans<=0 and '買' not in vba:
                    tra(fbid,post_message_url,recevied_message)
                    ans += 2

        #ATM多輪回答------------------------------------------------------------徹底完成了
        for i19 in range(D19):
            if idd in idcheck:
                if idcheck[idd].find(dict["ATM"][i19]) >= 0 and ans <= 0:
                    print("進idcheck的ATM了進idcheck的ATM了進idcheck的ATM了進idcheck的ATM了")
                    ATM(idd,post_message_url)
                    ans += 2

        #天氣多輪回答-----------------------------------------------------------徹底完成了
        for i21 in range(D21):
            if idd in idcheck:
                if idcheck[idd].find(dict["weather"][i21]) >= 0 and ans <= 0:
                    weather(idd,post_message_url,idrecevied_message[idd])
                    ans += 2

        #WIFI多輪回答-----------------------------------------------------------徹底完成了
        for i8 in range(D8):
            if idd in idcheck:
                if idcheck[idd].find(dict["wifi"][i8]) >= 0 and ans<=0:
                    wifi(idd, post_message_url)
                    ans += 2

        #公車多輪回答-----------------------------------------------------------徹底完成了
        for i22 in range(D22):
            if idd in idcheck:
                if idcheck[idd].find(dict["公車"][i22]) >= 0 and ans<=0:
                    bus(fbid, post_message_url, idrecevied_message[idd])
                    ans += 2

        #Ubike多輪回答----------------------------------------------------------徹底完成了
        for i20 in range(D20):
            if idd in idcheck:
                if idcheck[idd].find(dict["Ubike"][i20]) >= 0 and ans<=0:
                    print("進idcheck的ubike了進idcheck的ubike了進idcheck的ubike了進idcheck的ubike了")
                    ubike(idd, post_message_url)
                    ans += 2

        #北捷多輪回答------------------------------------------------------------徹底完成了
        for i23 in range(D23):
            if idd in idcheck:
                if idcheck[idd].find(dict["北捷"][i23]) >= 0 and ans<=0:
                    peijie(idd, post_message_url, idrecevied_message[idd])
                    ans += 2

        #評價多輪回答
        for i10 in range(D10):
            if idd in idcheck:
                if idcheck[idd].find(dict["評價"][i10]) >= 0 and ans<=0:
                    if idd in nba:
                        message_contents(idd,nba[idd],4,'評價')
                    else:
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"看來我還沒去這個地方過欸...還是你可以告訴人家那是哪裡呢(∩´﹏`∩)","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        delete_everything(idd)
                    ans += 2

        for i5 in range(D5):
            if idd in idcheck:
                if idcheck[idd].find(dict["營業時間"][i5]) >= 0 and ans<=0:
                    if idd in nba:
                        message_contents(idd,nba[idd],3,'營業時間')
                    else:
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"看來我還沒去這個地方過欸...還是你可以告訴人家那是哪裡呢(∩´﹏`∩)","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        delete_everything(idd)
                    ans += 2

        for i6 in range(D6):
            if idd in idcheck:
                if idcheck[idd].find(dict["電話"][i6]) >= 0 and ans<=0:
                    if idd in nba:
                        message_contents(idd,nba[idd],1,'電話')
                    else:
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"看來我還沒去這個地方過欸...還是你可以告訴人家那是哪裡呢(∩´﹏`∩)","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        delete_everything(idd)
                    ans += 2

        for i3 in range(D3):
            if idd in idcheck:
                if idcheck[idd].find(dict["價錢"][i3]) >= 0 and ans<=0:
                    if idd in nba:

                        message_contents(idd,nba[idd],5,'網站')
                    else:
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"看來我還沒去這個地方過欸...還是你可以告訴人家那是哪裡呢(∩´﹏`∩)","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        delete_everything(idd)
                    ans += 2

        for i11 in range(D11):
            if idd in idcheck:
                if idcheck[idd].find(dict["充電"][i11]) >= 0 and ans<=0:
                    if idd in nba:
                        message_contents(idd,nba[idd],5,'網站')
                    else:
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"看來我還沒去這個地方過欸...還是你可以告訴人家那是哪裡呢(∩´﹏`∩)","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        delete_everything(idd)
                    ans += 2

        for i7 in range(D7):
            if idd in idcheck:
                if idcheck[idd].find(dict["介紹"][i7]) >= 0 and ans<=0:
                    if idd in nba:
                        message_contents(idd,nba[idd],5,'網站')
                    else:
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"看來我還沒去這個地方過欸...還是你可以告訴人家那是哪裡呢(∩´﹏`∩)","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        delete_everything(idd)
                    ans += 2

        for i4 in range(D4):
            if idd in idcheck:
                if idcheck[idd].find(dict["location"][i4]) >= 0 and ans<=0:
                    if idd in nba:
                        message_contents(fbid,nba[idd],2,'地址')
                        delete_everything(idd)
                    else:
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"看來我還沒去這個地方過欸...還是你可以告訴人家那是哪裡呢(∩´﹏`∩)","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        delete_everything(idd)
                    ans += 2

        if idd in idcheck:
            if idcheck[idd] == "我有建議要說" and ans <= 0:
                global address_add_num,else_add_num,address_add_name,address_add_text
                if user_payload != '' and user_payload != '<suggestion_inanyQ>':
                    if address_add_name != '' and address_add_text == '':
                        address_add_text = recevied_message
                        response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"謝謝你告訴我，等我去過這個地方，下次就能回答你啦！但我可不會因為這樣就認定你是全天下最好的人喔！"}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        response_msg = json.dumps({"recipient":{"id":1502184393150744},"message":{"text":"廢物趙豬豬，有人說地點建議:\n地點:" + address_add_name+"\n詳細資訊:"+address_add_text}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        response_msg = json.dumps({"recipient":{"id":2115912511770517},"message":{"text":"杜杜，有人說地點建議:\n地點:" + address_add_name+"\n詳細資訊:"+address_add_text}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        anyQuestion(fbid,post_message_url)
                        delete_everything(fbid)
                        user_payload = ''
                        address_add_num = 0
                        ans += 2
                    elif address_add_text == '' and address_add_name == '' and address_add_num == 1:
                        address_add_num = 2
                        address_add_name = recevied_message
                        response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"有沒有其他描述可以告訴我呢？"}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        last_word.update({idd:recevied_message})
                    elif user_payload=='<adress_suggest>' and address_add_name == '' and address_add_text == '' and address_add_num == 0:
                        address_add_num = 1
                        response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"是什麼地點啊？快告訴人家嘛！"}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    elif user_payload=='<else_suggest>':
                        if else_add_num==1:
                            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"謝謝你的建議！但、但我可不會因為這樣就認定你是全天下最好的人喔！"}})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                            response_msg = json.dumps({"recipient":{"id":1502184393150744},"message":{"text":"帥哥，有人說其他建議:\n" + recevied_message}})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                            response_msg = json.dumps({"recipient":{"id":2115912511770517},"message":{"text":"杜杜，有人說其他建議:\n" + recevied_message}})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                            anyQuestion(fbid,post_message_url)
                            delete_everything(fbid)
                            user_payload = ''
                            else_add_num = 0
                            ans += 2
                        else:
                            else_add_num+=1
                            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"我還不夠好嗎……那快跟人家說你的想法吧！"}})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                elif user_payload == '<suggestion_inanyQ>':
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"謝謝你的建議！但、但我可不會因為這樣就認定你是全天下最好的人喔！"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":1502184393150744},"message":{"text":"廢物趙豬豬，有人說建議:\n" + recevied_message}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":2115912511770517},"message":{"text":"杜杜，有人說建議:\n" + recevied_message}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    anyQuestion(fbid,post_message_url)
                    delete_everything(fbid)
                    ans += 2

                else:
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"謝謝你的建議！但、但我可不會因為這樣就認定你是全天下最好的人喔！"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":1502184393150744},"message":{"text":"廢物趙豬豬，有人說其他建議:\n" + recevied_message}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":2115912511770517},"message":{"text":"廢物ㄇㄇ的杜杜，有人說其他建議:\n" + recevied_message}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    anyQuestion(fbid,post_message_url)
                    delete_everything(fbid)
                    ans += 2








    else:
        #回答完問題後檢測使用者是否繼續問
        if recevied_message == "沒問題了":
            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"對我刮目相看了吧( ◠‿◠ )"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            ans += 1
            recevied_message = ''
        elif recevied_message == "我還有問題":
            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"還有什麼問題呢？真不知道你沒有我該怎麼辦吶(ˊ艸ˋ)"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            ans += 1
            recevied_message = ''
        elif recevied_message == "我有建議要說":
            print("進我有建議要說進我有建議要說進我有建議要說進我有建議要說")
            idcheck.update({idd:recevied_message})
            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"我是不會輸給其他人的，快跟我說你的建議嘛！"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"當、當然我絕對不是為了你喔！"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            print(idcheck)
            ans += 1
            recevied_message = ''
        elif recevied_message == "學妹能幫你什麼？":
            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"吶，我的夢想是幫助大家解決即時性的問題，所以如果你有什麼需要，都可以問我喔！等、等等你不要誤會喔！我才沒有總是第一個回覆你呢٩(ŏ﹏ŏ、)۶\n哼！少臭美了！快去下面網址看我多厲害啦！\nhttps://www.facebook.com/%E8%A1%8C%E5%8B%95%E5%AD%B8%E5%A6%B9Aya%E5%8F%B0%E7%A7%91%E5%8F%B0%E5%A4%A7%E8%B6%B4%E8%B6%B4%E8%B5%B0%E6%A9%9F%E5%99%A8%E4%BA%BA-1785453378183306/?modal=admin_todo_tour"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            ans += 1
            recevied_message = ''
        
        # 檢測有無查廁所類別需求關鍵字
        for i1 in range(D1):
            for b1 in range(len(sentence_ba)):
                if dict["toilet"][i1]==sentence_ba[b1] and ans <= 0:
                    idcheck.update({idd:dict["toilet"][i1]})
                    print("else的廁所else的廁所else的廁所else的廁所else的廁所")
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"嗯？難道是不舒服嗎？快告訴我你的位置吧！我幫你找找看！","quick_replies":[
                        # {
                        #      "content_type":"text",
                        #      "title":"搜尋",
                        #      "payload":"<POSTBACK_PAYLOAD>"
                        # },
                        {
                            "content_type":"location",
                            "title":"傳送地點"
                        },
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1
                    b1 = len(sentence_ba)

        # 檢測有無查wifi類別需求關鍵字
        for i8 in range(D8):
            for b8 in range(len(sentence_ba)):
                if dict["wifi"][i8]==sentence_ba[b8] and ans <= 0:
                    idcheck.update({idd:dict["wifi"][i8]})
                    #message_contents(fbid,sentence,5,'網站，或許能給你一些幫助')
                    #anyQuestion(fbid,post_message_url)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"真是的！如果因為斷網而已讀我，我就不理你囉！快告訴我你的位置吧！","quick_replies":[
                        {
                            "content_type":"location"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1
                    b8 = len(sentence_ba)

        # 檢測有無查ATM類別需求關鍵字
        for i19 in range(D19):
            for b19 in range(len(sentence_ba)):
                if dict["ATM"][i19]==sentence_ba[b19] and ans <= 0:
                    idcheck.update({idd:dict["ATM"][i19]})
                    #message_contents(fbid,sentence,5,'網站，或許能給你一些幫助')
                    #anyQuestion(fbid,post_message_url)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"如果要結帳才發現錢包沒錢還真是尷尬呢，好險有我幫你吧！快告訴我你的位置吧！","quick_replies":[
                        {
                            "content_type":"location"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1
                    b19 = len(sentence_ba)

        # 檢測有無查店家評價類別需求關鍵字
        for i10 in range(D10):
            for b10 in range(len(sentence_ba)):
                if dict["評價"][i10] == sentence_ba[b10] and ans <= 0 and idd in nba:
                    print("進else評價了進else評價了進else評價了進else評價了")
                    message_contents(fbid,nba[idd],4,'評價')
                    b10 = len(sentence_ba)
                    ans += 1
                elif dict["評價"][i10] == sentence_ba[b10] and ans <= 0 and idd not in nba:#看不懂使用者打哪裡或是使用者沒打
                    idcheck.update({idd:sentence_ba[b10]})
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你想問哪裡的評價呢?"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"那、那個你能跟我說更多資訊嘛？","quick_replies":[
                    #     {
                    #          "content_type":"text",
                    #          "title":"是",
                    #          "payload":"<QA_YES>"
                    #     },
                    #     {
                    #          "content_type":"text",
                    #          "title":"下次吧",
                    #          "payload":"<QA_NO>"
                    #     }
                    #     ]}})
                    # status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b10 = len(sentence_ba)
                    ans += 1

        # 檢測有無查位置類別需求關鍵字（內容物為判斷地點位置）
        for i4 in range(D4):
            for b4 in range(len(sentence_ba)):
                if dict["location"][i4]==sentence_ba[b4] and ans <= 0:
                    print("進else的Location進else的Location進else的Location進else的Location")
                    if idd in nba:
                        response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"下面就是" + nba[idd] + "的位置資訊喔！\n" + "https://www.google.com.tw/maps/search/" + nba[idd]}})
                        # status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        message_contents(fbid,nba[idd],2,'地址')
                        ans += 1

                    elif recevied_message == "學妹知道這個地方在哪裡嗎" and ans <= 0:
                        idcheck.update({idd:dict["location"][i4]})
                        response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你想知道什麼地方的位置資訊呢?"}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        ans += 1

                    elif recevied_message != '去程':
                        print(recevied_message)
                        print("else的location的非去程")
                        response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"嗯？我找不到這個地方欸！該不會你弄錯了吧？"}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        ans += 1

        # 接收到高捷
        for i13 in range(D13):
            for b13 in range(len(sentence_ba)):
                if dict["高捷"][i13]==sentence_ba[b13] and ans <= 0:
                    idcheck.update({idd:dict["高捷"][i13]})
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要在哪裡上車呢？讓我猜猜看！是美麗島嗎？還是西子灣呢(๑´ڡ`๑)"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1

        # 接收到高鐵
        for i14 in range(D14):
            for b14 in range(len(sentence_ba)):
                if dict["高鐵"][i14]==sentence_ba[b14] and ans <= 0 and ('買' in vba or '票' in recevied_message or '價' in recevied_message):
                    idcheck.update({idd:dict["高鐵"][i14]})
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"討、討厭，高鐵的票怎麼有這麼多價格啊？我才不是不知道票價，只、只是太複雜了需要一點時間理解！你先去官網看看啦！等我研究完，以後就能回答你了！\nhttps://irs.thsrc.com.tw/IMINT/"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1
                    anyQuestion(fbid,post_message_url)
                    delete_everything(fbid)
                    vba = []

                if dict["高鐵"][i14]==sentence_ba[b14] and ans <= 0:
                    print('沒有買的高鐵沒有買的高鐵沒有買的高鐵沒有買的高鐵沒有買的高鐵')
                    idcheck.update({idd:dict["高鐵"][i14]})
                    print(recevied_message)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要在哪裡上車呢？我、我才不是要跟你偶遇什麼的喔！"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1

        # 接收到台鐵
        for i15 in range(D15):
            for b15 in range(len(sentence_ba)):
                if dict["台鐵"][i15]==sentence_ba[b15] and ans <= 0 and ('買' in vba or '票' in recevied_message or '價' in recevied_message):
                    idcheck.update({idd:dict["台鐵"][i15]})
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"我、我才不是不知道怎麼買票呢！只是還沒買過而已！總之先給你官網，你之後要教人家買喔(ಠ^ಠ)\nhttp://railway.hinet.net/Foreign/TW/index.html"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1
                    anyQuestion(fbid,post_message_url)
                    delete_everything(fbid)
                    vba = []

                if dict["台鐵"][i15]==sentence_ba[b15] and ans <= 0:
                    idcheck.update({idd:dict["台鐵"][i15]})
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"學長要在哪裡上車呢？讓我猜猜看！是台北嗎？還是南港呢(๑´ڡ`๑)"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1


    # 檢測有無查營業時間類別需求關鍵字
        for i5 in range(D5):
            for b5 in range(len(sentence_ba)):
                if dict["營業時間"][i5]==sentence_ba[b5] and ans <= 0 and idd in nba:
                    idcheck.update({idd:sentence_ba[b5]})
                    message_contents(fbid,nba[idd],3,'營業時間')
                    b5 = len(sentence_ba)
                    ans += 1
                elif dict["營業時間"][i5]==sentence_ba[b5] and ans <= 0 and idd not in nba:
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"聽不太懂你說什麼欸，我以為自己很了解你的……"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"還，還是你可以告訴人家更多資訊嗎٩(◦`꒳´◦)۶","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b5 = len(sentence_ba)
                    ans += 1

    # 檢測有無查營業電話類別需求關鍵字
        for i6 in range(D6):               
            for b6 in range(len(sentence_ba)):
                if dict["電話"][i6] == sentence_ba[b6] and ans <= 0 and idd in nba:
                    idcheck.update({idd:sentence_ba[b6]})
                    message_contents(fbid,nba[idd],1,'電話')
                    b6 = len(sentence_ba)
                    ans += 1

                elif recevied_message == "學妹知道這個地方的電話嗎" and ans <= 0:
                    idcheck.update({idd:"電話"})
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你想知道哪裡的電話呢？"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1

                elif dict["電話"][i6] == sentence_ba[b6] and ans <= 0 and idd not in nba:
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"聽不太懂你問哪裡的電話欸，我以為自己很了解你的……"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"還，還是你可以告訴人家更多資訊呢(∩´﹏`∩)","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b6 = len(sentence_ba)
                    ans += 1

        # 檢測有無查店家介紹類別需求關鍵字
        # 未完成實際內容
        for i7 in range(D7):
            for b7 in range(len(sentence_ba)):
                if dict["介紹"][i7] == sentence_ba[b7] and ans <= 0 and idd in nba:
                    idcheck.update({idd:sentence_ba[b7]})
                    message_contents(fbid,nba[idd],5,'網站，或許能給你一些幫助')
                    # anyQuestion(fbid,post_message_url)
                    # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的菜單資訊"}})
                    # status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b7 = len(sentence_ba)
                    ans += 1
                elif dict["介紹"][i7] == sentence_ba[b7] and ans <= 0 and idd not in nba:
                    idcheck.update({idd:sentence_ba[b7]})
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"聽不太懂你問哪裡的介紹欸，我以為自己很了解你的……"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"還，還是你可以告訴人家更多資訊呢(∩´﹏`∩)?","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b7 = len(sentence_ba)
                    ans += 1
     
        # 檢測有無查店家菜單資訊類別需求關鍵字      
        for i9 in range(D9):
            for b9 in range(len(sentence_ba)):
                if dict["菜單"][i9] == sentence_ba[b9] and ans <= 0 and idd in nba:
                    recipe_query(fbid, post_message_url, nba[idd])
                    b9 = len(sentence_ba)
                    ans += 1
                elif dict["菜單"][i9] == sentence_ba[b9] and ans <= 0 and idd not in nba:
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"我手邊明明有這麼多菜單，卻還是找不到你說的那家店欸，難道是我知道的還不夠多嘛_(:з」∠)_"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"如、如果可以的話，你能告訴人家更多資訊嘛？","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b10 = len(sentence_ba)
                    ans += 1


        # 檢測有無查充電類別需求關鍵字
        # 未完成實際內容     
        for i11 in range(D11):
            for b11 in range(len(sentence_ba)):
                if dict["充電"][i11] == sentence_ba[b11] and ans <= 0 and idd in nba:
                    idcheck.update({idd:sentence_ba[b11]})
                    message_contents(fbid,nba[idd],5,'網站，或許能給你一些幫助')
                    b11 = len(sentence_ba)
                    # anyQuestion(fbid,post_message_url)
                    # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是充電資訊"}})
                    # status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1
                elif dict["充電"][i11] == sentence_ba[b11] and ans <= 0 and idd not in nba:
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"聽不太懂你想問什麼欸，難道是我太笨嘛:("}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"那、那可以請你告訴人家更多資訊嘛……？","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b11 = len(sentence_ba)
                    ans += 1

        # 檢測有無查價類別需求關鍵字
        # 未完成實際內容
        for i3 in range(D3):
            for b3 in range(len(sentence_ba)):
                if dict["價錢"][i3]==sentence_ba[b3] and ans <= 0 and idd in nba:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"我也不知道" + nba[idd] + "的價位欸，可是我可以給你他們的菜單參考一下！"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    recipe_query(fbid, post_message_url, nba[idd])
                    anyQuestion(fbid,post_message_url)
                    delete_everything(fbid)
                    # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + sentence + "的菜單資訊"}})
                    # status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b3 = len(sentence_ba)
                    ans += 1
                elif dict["價錢"][i3]==sentence_ba[b3] and ans <= 0 and idd not in nba:
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"我明明知道很多店家的資訊，卻還是找不到你說的那家店欸，難道是我知道的還不夠多嘛……"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"還是你可以告訴人家更多資訊呢(∩´﹏`∩)","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"是",
                             "payload":"<QA_YES>"
                        },
                        {
                             "content_type":"text",
                             "title":"下次吧",
                             "payload":"<QA_NO>"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    b3 = len(sentence_ba)
                    ans += 1

        #天氣
        for i21 in range(D21):
            for b21 in range(len(sentence_ba)):
                if dict["weather"][i21]==sentence_ba[b21] and ans <= 0:
                    idcheck.update({idd:dict["weather"][i21]})
                    if (5 <= int(weather_today) < 17):
                        wave(fbid, post_message_url)
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"朋友問我為什麼今天看起來特別高興，當然是因為天氣很好啊！才不是因為你喔！"}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        wave(fbid, post_message_url)
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"啊、所以你想知道什麼時段的天氣呢？","quick_replies":[
                            {
                                 "content_type":"text",
                                 "title":"現在",
                                 "payload":"<weather_now>"
                            },
                            {
                                 "content_type":"text",
                                 "title":"今晚至明晨",
                                 "payload":"<weather_tomorrow_day>"
                            },
                            {
                                 "content_type":"text",
                                 "title":"明天早上",
                                 "payload":"<weather_tomorrow_night>"
                            }
                            ]}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    else :
                        response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"朋友問我為什麼今天看起來特別高興，當然是因為天氣很好啊！才不是因為你喔！啊、所以你想知道什麼時段的天氣呢？","quick_replies":[
                            {
                                 "content_type":"text",
                                 "title":"現在",
                                 "payload":"<weather_now>"
                            },
                            {
                                 "content_type":"text",
                                 "title":"明天早上",
                                 "payload":"<weather_tomorrow_day>"
                            },
                            {
                                 "content_type":"text",
                                 "title":"明天晚上",
                                 "payload":"<weather_tomorrow_night>"
                            }
                            ]}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    if fbid in nba:
                        del nba[fbid]
                    ans += 1

        #公車
        for i22 in range(D22):
            for b22 in range(len(sentence_ba)):
                if dict["公車"][i22]==sentence_ba[b22] and ans <= 0:
                    idcheck.update({idd:dict["公車"][i22]})
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"聽說搭284會坐到屁股爛掉呢，開玩笑的～你今天要坐哪一路公車呢？"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1

        #Ubike
        for i20 in range(D20):
            for b20 in range(len(sentence_ba)):
                if dict["Ubike"][i20]==sentence_ba[b20] and ans <= 0:
                    idcheck.update({idd:dict["Ubike"][i20]})
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"快告訴我你的位置或是想查的地點吧(・ω・)","quick_replies":[
                        {
                            "content_type":"location"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1

        #北捷
        for i23 in range(D23):
            for b23 in range(len(sentence_ba)):
                if dict["北捷"][i23]==sentence_ba[b23] and ans <= 0:
                    idcheck.update({idd:dict["北捷"][i23]})
                    jj.update({idd: 0 })
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你也是每天搭捷運上下學嗎？才不是想更了解你呢！快告訴我你要查詢的站名吧！"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1


        #你好
        for i16 in range(D16):
            for b16 in range(len(sentence_ba)):
                if dict["你好"][i16] == sentence_ba[b16] and ans <= 0:
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你好，今天有什麼即時性問題要問我的嗎？我可不會輕易被問倒喔< (￣︶￣)>","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"我想上廁所",
                             "payload":"<i_dont_know>"
                        },
                        {
                             "content_type":"text",
                             "title":"我要搭公車",
                             "payload":"<i_dont_know>"
                        },
                        {
                             "content_type":"text",
                             "title":"我需要領錢",
                             "payload":"<i_dont_know>"
                        },
                        {
                             "content_type":"text",
                             "title":"沒事，只是想跟學妹聊聊天",
                             "payload":"<i_dont_know>"
                        }
                        ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    ans += 1

    if user_payload != '':
        if user_payload == '<QA_YES>':
            idcheck.update({idd:"我有建議要說"})
            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"說吧！我是不會輸給其他人的！當、當然我絕對不是為了你喔！","quick_replies":[
                {
                     "content_type":"text",
                     "title":"地點",
                     "payload":"<adress_suggest>"
                },
                {
                     "content_type":"text",
                     "title":"其他建議",
                     "payload":"<else_suggest>"
                }
                ]}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        elif user_payload=='<QA_NO>':
            last_word.update({idd:'下次吧'})
            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"那下次一定要跟人家說喔，約好囉(ˋ•̀ω•́ˊ)ﾒ"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            user_payload=''
            anyQuestion(fbid,post_message_url)

    print(ans)
    print("ans是多少呢ans是多少呢ans是多少呢ans是多少呢ans是多少呢ans是多少呢ans是多少呢")
    if ans == 0:
        return 0

#--------------------------------------------(以下為各種函數)----------------------------------------------------

# 建立可回應至FB之函數(文字)
def post_facebook_message_text(fbid, recevied_message):

    # 抓取傳送者名稱
    # 使用：user_details['first_name']
    global last_word
    user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':PAGE_ACCESS_TOKEN}
    user_details = requests.get(user_details_url, user_details_params).json()
    post_message_url = 'https://graph.facebook.com/v3.0/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    i_dont_know_num = random.randint(1,4)

    if recevied_message == "是" or recevied_message == "地點" or recevied_message == "其他建議":
        last_word.update({fbid:recevied_message})
    if fbid not in last_word:
        last_word[fbid] = ''
    print(recevied_message,last_word)
    print("有來有來")

    if check_dict(fbid, recevied_message) == 0 :
        if recevied_message != last_word[fbid] and recevied_message != '' and recevied_message != 'kkk':
            print('\n\n\n\n\n')
            print(recevied_message)
            print('中間中間')
            print(last_word)
            print('\n\n\n\n\n')
            random_response = random.choice(['我聽不太懂你說什麼欸，還是你想聊聊別的呢？','嗯？我不太懂你的意思欸，換個問法嘛～','我、我可不是覺得你說的話在我的知識範圍外喔！只是想跟你聊聊其他東西而已！','我不太了解你說的東西欸，還是我們來聊聊別的？','我不擅長這個話題啦！講講別的東西嘛！'])
            if i_dont_know_num == 1 and recevied_message != "沒事，只是想跟學妹聊聊天":
                response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":random_response,"quick_replies":[
                    {
                         "content_type":"text",
                         "title":"我想上廁所",
                         "payload":"<i_dont_know>"
                    },
                    {
                         "content_type":"text",
                         "title":"我要搭公車",
                         "payload":"<i_dont_know>"
                    },
                    {
                         "content_type":"text",
                         "title":"我需要領錢",
                         "payload":"<i_dont_know>"
                    },
                    {
                         "content_type":"text",
                         "title":"沒事，只是想跟學妹聊聊天",
                         "payload":"<i_dont_know>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            elif i_dont_know_num == 2 and recevied_message != "沒事，只是想跟學妹聊聊天":
                response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":random_response,"quick_replies":[
                    {
                         "content_type":"text",
                         "title":"我想知道今天的天氣如何",
                         "payload":"<i_dont_know>"
                    },
                    {
                         "content_type":"text",
                         "title":"學妹知道這個地方的評價嗎",
                         "payload":"<i_dont_know>"
                    },
                    {
                         "content_type":"text",
                         "title":"學妹知道這個地方的電話嗎",
                         "payload":"<i_dont_know>"
                    },
                    {
                         "content_type":"text",
                         "title":"沒事，只是想跟學妹聊聊天",
                         "payload":"<i_dont_know>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            elif i_dont_know_num == 3 and recevied_message != "沒事，只是想跟學妹聊聊天":
                response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":random_response,"quick_replies":[
                    {
                         "content_type":"text",
                         "title":"我想搭高鐵",
                         "payload":"<i_dont_know>"
                    },
                    {
                         "content_type":"text",
                         "title":"我想搭火車",
                         "payload":"<i_dont_know>"
                    },
                    {
                         "content_type":"text",
                         "title":"學妹知道這個地方在哪裡嗎",
                         "payload":"<i_dont_know>"
                    },
                    {
                         "content_type":"text",
                         "title":"沒事，只是想跟學妹聊聊天",
                         "payload":"<i_dont_know>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            elif i_dont_know_num == 4 and recevied_message != "沒事，只是想跟學妹聊聊天":
                response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":random_response,"quick_replies":[
                    {
                         "content_type":"text",
                         "title":"我想搭高鐵",
                         "payload":"<i_dont_know>"
                    },
                    {
                         "content_type":"text",
                         "title":"我想搭捷運",
                         "payload":"<i_dont_know>"
                    },
                    {
                         "content_type":"text",
                         "title":"我想找廁所",
                         "payload":"<i_dont_know>"
                    },
                    {
                         "content_type":"text",
                         "title":"沒事，只是想跟學妹聊聊天",
                         "payload":"<i_dont_know>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            if recevied_message == "沒事，只是想跟學妹聊聊天":
                response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"真、真是的，在胡言亂語什麼嘛！我才沒有覺得開心喔(*´艸`*)"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            if fbid in last_word:
                del last_word[fbid]
            delete_everything(fbid)
        

    # FUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUCK!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # ===UnboundLocalError: local variable 'response_text' referenced before assignment.===
    # 碼神建議:在前面已經使用的時候，未進行變數的宣告。>> 未進入判斷後進行的宣告

    # post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    # response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"text":check_dict(recevied_message)}})
    # status = requests.post(post_message_url, headers = {"Content-Type": "application/json"},data = response_msg)

    # print(status.json())

# "recipient":{
  #   "id":"1254459154682919"
  # },
  # "message":{
  #   "attachment":{
  #     "type":"image", 
  #     "payload":{
  #       "url":"http://www.messenger-rocks.com/image.jpg", 
  #       "is_reusable":true

def post_facebook_message_media(fbid, imgurl):
    post_message_url = 'https://graph.facebook.com/v3.0/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
    response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":{"type":"image", "payload":{"url":imgurl}}}})
    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"},data = response_msg)
    # print(status.json())

# Google Static Maps
def GMap_map(center):

    endpoint = "https://maps.googleapis.com/maps/api/staticmap?"
    GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'

    G_center = center.replace(' ', '+')
    G_zoom = "16"
    G_size = "250x250"
    G_markers = "color:red%7C"+ G_center

    nav_request = 'center={}&zoom={}&size={}&markers={}&key={}'.format(G_center, G_zoom, G_size, G_markers, GM_API_KEY)
    G_request = endpoint + nav_request
    return G_request

# Google Places API Web Service Search
def GMap_place_search(center):
    # Google Places API Web Service Search

    endpoint = "https://maps.googleapis.com/maps/api/place/textsearch/json?"
    GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'

    G_query = center.replace(' ', '+')
    G_language = 'zh-TW'

    # 輸出中文地址
    nav_request = 'query={}&language={}&key={}'.format(G_query, G_language, GM_API_KEY)
    # 輸出英文地址
    # nav_request = 'query={}&key={}'.format(G_query, GM_API_KEY)

    request = endpoint + nav_request
    respone = urllib.request.urlopen(request).read()
    directions = json.loads(respone.decode('utf-8'))

    results = directions['results']
    # response = results[0]['name'] + '的地址是：' + results[0]['formatted_address']
    response = results[0]['formatted_address']

    # print (results[0]['name'] + '的地址是：' + results[0]['formatted_address'])
    return response



#高捷涵數
def kao(i13,fbid,post_message_url,recevied_message):
    global stationtime,startstation,endstation

    kaostation=['南岡山','橋頭火車站','橋頭糖廠','青埔','都會公園','後勁','楠梓加工區','油廠國小','世運','左營',
                '生態園區','巨蛋','凹子底','後驛','高雄車站','美麗島','中央公園','三多商圈','獅甲','凱旋',
                '前鎮高中','草衙','高雄國際機場','小港','西子灣','鹽埕埔','市議會','美麗島','信義國小',
                '文化中心','五塊厝','技擊館','衛武營','鳳山西站','鳳山','大東','鳳山國中','大寮']
    kaotime=['00','01','02','03','04','05','06','07','08','09',
            '10','11','12','13','14','15','16','17','18','19',
            '20','21','22','23','24']

    if stationtime=='' and endstation!='':
        kk=0
        for Kaohour in range(25):
            if recevied_message ==kaotime[Kaohour]:                            
                stationtime=recevied_message
                with open(user_url+r'\GooglemapBot\jsondata\時刻表\MRT_Kaohsiung.json', 'r', encoding="utf-8") as f:
                    dataKaoMRT = json.load(f)
                today = time.strftime("%A")
                Kaoa = len(dataKaoMRT)
                response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'下面是往【'+endstation+'】方向之班次在【'+stationtime+'點】停靠【'+startstation+'站】的時刻表喔！\n'}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

                print('下面是往【'+endstation+'】方向之班次在【'+stationtime+'點】停靠【'+startstation+'站】的時刻表喔！\n')
                for Kaoi in range(Kaoa): #i=第幾筆資料
                    #找出使用者的現在位置(228取6)
                    if dataKaoMRT[Kaoi]["StationName"]["Zh_tw"] == startstation: 
                        #判斷捷運的方向(6取3)
                        if dataKaoMRT[Kaoi]["DestinationStationName"]["Zh_tw"] == endstation:
                            Kaob = len(dataKaoMRT[Kaoi]["Timetables"]) #b=總班次
                            for Kaoj in range(Kaob):
                                #禮拜一到四、禮拜五和假日的時刻表不同，故要去判斷今天是星期幾(3取1)
                                if today == ('Monday' or 'Tuesday' or 'Wednesday' or 'Thursday'):
                                    if Kaoi % 3 == 0:
                                        Kaox = dataKaoMRT[Kaoi]['Timetables'][Kaoj]['ArrivalTime'].find(stationtime)
                                        if 2 > Kaox >= 0:
                                            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'第'+ str(dataKaoMRT[Kaoi]['Timetables'][Kaoj]['Sequence'])+'班車: '+ str(dataKaoMRT[Kaoi]['Timetables'][Kaoj]['ArrivalTime'])}})
                                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                            print('第', dataKaoMRT[Kaoi]['Timetables'][Kaoj]['Sequence'], '班車: ', dataKaoMRT[Kaoi]['Timetables'][Kaoj]['ArrivalTime'])
                                    else:
                                        break

                                elif today == ('Saturday' or 'Sunday'):
                                    if Kaoi % 3 == 1:
                                        Kaox = dataKaoMRT[Kaoi]['Timetables'][Kaoj]['ArrivalTime'].find(stationtime)
                                        if 2 > Kaox >= 0:
                                            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"第"+ str(dataKaoMRT[Kaoi]["Timetables"][Kaoj]["Sequence"])+"班車: "+ str(dataKaoMRT[Kaoi]["Timetables"][Kaoj]["ArrivalTime"])}})
                                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                            print('第', dataKaoMRT[Kaoi]['Timetables'][Kaoj]['Sequence'], '班車: ', dataKaoMRT[Kaoi]['Timetables'][Kaoj]['ArrivalTime'])
                                    else:
                                        break

                                else:
                                    if Kaoi % 3 == 2:
                                        Kaox = dataKaoMRT[Kaoi]['Timetables'][Kaoj]['ArrivalTime'].find(stationtime)
                                        if 2 > Kaox >= 0:
                                            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'第'+ str(dataKaoMRT[Kaoi]['Timetables'][Kaoj]['Sequence'])+'班車: '+ str(dataKaoMRT[Kaoi]['Timetables'][Kaoj]['ArrivalTime'])}})
                                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                                            print('第', dataKaoMRT[Kaoi]['Timetables'][Kaoj]['Sequence'], '班車: ', dataKaoMRT[Kaoi]['Timetables'][Kaoj]['ArrivalTime'])
                                    else:
                                        break
                last_word.update({fbid:idrecevied_message[fbid]})
                anyQuestion(fbid,post_message_url)
                delete_everything(fbid)               
            else:
                if kk == 24:
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"真是的，你的時間是不是打錯了啊( -`д´-)"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                kk+=1


    if endstation=='' and startstation!='':
        kaonumber=len(kaostation)
        kk=0
        for kao in range(kaonumber):
            if recevied_message == kaostation[kao]: 
                endstation=recevied_message
                response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你想搭大約幾點的車啊？"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            else:
                if kk == kaonumber-1:
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"真是的，你的站名是不是打錯了啊( -`д´-)"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                kk+=1
    if startstation=='':
        kaonumber=len(kaostation)
        kk=0
        for kao in range(kaonumber): 
            if recevied_message == kaostation[kao]:
                startstation=recevied_message
                response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"那要往哪個方向呢？"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            else:
                if kk == kaonumber-1:
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"真是的，你的站名是不是打錯了啊( -`д´-)"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                kk+=1


#高鐵函數
def thsr(fbid,post_message_url,recevied_message):
    global thsr_start,thsr_end,thsr_time_depart,thsr_time_arrive,last_word, idrecevied_message

    thsrstation=['南港','台北','板橋','桃園','新竹','苗栗','台中','彰化','雲林','嘉義',
                '台南','左營']
    thsrtime = ['00','01','02','03','04','05','06','07','08','09',
                '10','11','12','13','14','15','16','17','18','19',
                '20','21','22','23','24']

    if fbid in idrecevied_message:
        idrecevied_message[fbid] = changeword(idrecevied_message[fbid],1)
    print("changeword完的recevied_messagechangeword完的recevied_messagechangeword完的recevied_message")
    if fbid not in thsr_time_depart and fbid in thsr_end:
        kk=0
        for thsrhour in range(25):
            if thsrtime[thsrhour] in idrecevied_message[fbid]:                            
                thsr_time_depart.update({fbid:thsrtime[thsrhour]})
                thsr_time_arrive=''
                print(idcheck[fbid])
                print(idrecevied_message[fbid])
                print(thsr_start[fbid])
                print(thsr_end[fbid])
                print(thsr_time_depart[fbid])
                print("高鐵要的資料高鐵要的資料高鐵要的資料高鐵要的資料高鐵要的資料")
                HSR_url = "http://ptx.transportdata.tw/MOTC/v2/Rail/THSR/DailyTimetable/Today?$format=JSON"
                HSR_data = request(HSR_url)
                # with open(user_url+r'\GooglemapBot\jsondata\時刻表\HSR_180227.json', 'r', encoding="utf-8") as f:
                #     data = json.load(f)
                today = time.strftime("%A")
                thsra = len(HSR_data)
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'下面是【出發時間】為【'+thsr_time_depart[fbid]+'點】'+'從【'+thsr_start[fbid]+'】前往【'+thsr_end[fbid]+'】的所有班次喔！\n'}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'車次　出發時間　抵達時間'}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                print('車次\t'+'出發時間\t'+'抵達時間')

                list1 = []
                list2 = []
                list3 = []
                list4 = []
                 
                for thsri in range(thsra):
                    thsrb = len(HSR_data[thsri]['StopTimes']) #計算第i班高鐵有幾個停靠站
                    for thsrj in range(thsrb): #第i班列車的StopTimes(時刻表)裡的第j筆資料
                        if HSR_data[thsri]['StopTimes'][thsrj]['StationName']['Zh_tw'] == thsr_start[fbid]: #該班次會在上車車站停靠
                            thsrk = thsrj + 1
                            for thsrk in range(thsrk,thsrb):
                                if HSR_data[thsri]['StopTimes'][thsrk]['StationName']['Zh_tw'] == thsr_end[fbid]: #該班次會在下車車站停靠
                                    if thsr_time_arrive.strip() == '': #以下車時間的空值與否來判斷出發時間是否有值，並以此時間作為搜尋條件
                                        thsrm = HSR_data[thsri]['StopTimes'][thsrj]['ArrivalTime'].find(thsr_time_depart[fbid]) #在data[i]['StopTimes'][j]['ArrivalTime']裡找尋和depart_time相符的值在第幾位，並存到m
                                        #print(m)
                                        if 2 > thsrm >= 0: #若無符合內容，m會等於-1，反之為0或1
                                            list1.append(str(HSR_data[thsri]['DailyTrainInfo']['TrainNo'])) #將車次號碼存到list1；因為車號是int，故需轉為str
                                            list2.append(HSR_data[thsri]['StopTimes'][thsrj]['DepartureTime']) #將上車車站的出發時間存到list2
                                            list3.append(HSR_data[thsri]['StopTimes'][thsrk]['ArrivalTime']) #將下車車站的抵達時間存到list3
                                    elif thsr_time_depart[fbid].strip() == '': #以上車時間的空值與否來判斷抵達時間是否有值，並以此時間作為搜尋條件
                                        thsrm = HSR_data[thsri]['StopTimes'][thsrk]['ArrivalTime'].find(thsr_time_arrive)
                                        #print(m)
                                        if 2 > thsrm >= 0:
                                            list1.append(str(HSR_data[thsri]['DailyTrainInfo']['TrainNo']))
                                            list2.append(HSR_data[thsri]['StopTimes'][thsrj]['DepartureTime'])
                                            list3.append(HSR_data[thsri]['StopTimes'][thsrk]['ArrivalTime'])
                                    else: #若兩者皆有值，便以出發時間作為搜尋條件
                                        thsrm = data[thsri]['StopTimes'][thsrj]['ArrivalTime'].find(thsr_time_depart[fbid])
                                        #print(m)
                                        if 2 > thsrm >= 0:
                                            list1.append(str(HSR_data[thsri]['DailyTrainInfo']['TrainNo']))
                                            list2.append(HSR_data[thsri]['StopTimes'][thsrj]['DepartureTime'])
                                            list3.append(HSR_data[thsri]['StopTimes'][thsrk]['ArrivalTime'])                                                       
                thsrc = len(list1)

                if thsrc == 0:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"這個時間好像沒車了欸..."}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    last_word.update({fbid:idrecevied_message[fbid]})
                    anyQuestion(fbid,post_message_url)
                    delete_everything(fbid)
                    if fbid in thsr_start:
                        del thsr_start[fbid]
                    if fbid in thsr_end:
                        del thsr_end[fbid]
                    if fbid in thsr_time_depart:
                        del thsr_time_depart[fbid]

                else:
                        
                    for thsrx in range(thsrc):
                        list4.append(list2[thsrx]+list3[thsrx]+list1[thsrx])

                    for thsry in range(thsrc):
                        list4.sort()
                        wave(fbid, post_message_url)
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":list4[thsry][10:]+'   '+list4[thsry][0:5]+'   '+list4[thsry][5:10]}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        print(list4[thsry][10:]+'\t',list4[thsry][0:5]+'\t',list4[thsry][5:10])

                    last_word.update({fbid:idrecevied_message[fbid]})
                    anyQuestion(fbid,post_message_url)
                    delete_everything(fbid)
                    if fbid in thsr_start:
                        del thsr_start[fbid]
                    if fbid in thsr_end:
                        del thsr_end[fbid]
                    if fbid in thsr_time_depart:
                        del thsr_time_depart[fbid]

                print(idcheck)
                print(idrecevied_message)
                print(thsr_start)
                print(thsr_end)
                print(thsr_time_depart)
                print("高鐵完後的資料高鐵完後的資料高鐵完後的資料高鐵完後的資料高鐵完後的資料")
                
            else:
                if kk == 24:
                    wave(fbid, post_message_url)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"真是的，你的時間是不是打錯了啊( -`д´-)"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                kk+=1

    elif fbid not in thsr_end and fbid in thsr_start:
        thsrnumber=len(thsrstation)
        kk=0
        for thsr in range(thsrnumber):
            if thsrstation[thsr] in idrecevied_message[fbid]: 
                thsr_end.update({fbid:thsrstation[thsr]})
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你想搭大約幾點的車啊？"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            else:
                if kk == thsrnumber-1:
                    wave(fbid, post_message_url)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"真是的，你的站名是不是打錯了啊( -`д´-)"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                kk+=1

    elif fbid not in thsr_start:
        thsrnumber=len(thsrstation)
        kk=0
        for thsr in range(thsrnumber): 
            if thsrstation[thsr] in idrecevied_message[fbid]:
                thsr_start.update({fbid:thsrstation[thsr]})
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要在哪裡下車啊？搞不好等等會遇到你也說不定呢～"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            else:
                if kk == thsrnumber-1:
                    wave(fbid, post_message_url)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"真是的，你的站名是不是打錯了啊( -`д´-)"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                kk+=1


#臺鐵函數
def tra(fbid,post_message_url,recevied_message):
    global Train_Departure, Train_Destination, Train_DepartTime, Train_ArriveTime, idcheck, idrecevied_message, last_word

    trastation=['基隆','新豐','員林','永康','三坑','竹北','永靖','大橋','八堵','北新竹',
    '社頭','臺南','七堵','新竹','田中','保安','百福','三姓橋','二水','仁德','五堵','香山',
    '林內','中洲','汐止','崎頂','石榴','大湖','汐科','竹南','斗六','路竹','南港','造橋',
    '斗南','岡山','松山','豐富','石龜','橋頭','臺北','苗栗','大林','楠梓','萬華','南勢',
    '民雄','新左營','板橋','銅鑼','嘉北','左營','浮洲','三義','嘉義','高雄','樹林','泰安',
    '水上','鳳山','南樹林','后里','南靖','後庄','山佳','豐原','後壁','九曲堂','鶯歌','潭子',
    '新營','六塊厝','桃園','太原','柳營','屏東','內壢','臺中','林鳳營','中壢','大慶','隆田','埔心',
    '烏日','拔林','楊梅','新烏日','善化','富岡','成功','南科','新富','彰化','新市','北湖','花壇',
    '湖口','大村','基隆','談文','大山','後龍','龍港','白沙屯','新埔','通霄','苑裡','日南','大甲',
    '臺中港','清水','沙鹿','龍井','大肚','追分','彰化','八堵','羅東','南平','暖暖','冬山','鳳林',
    '四腳亭','新馬','萬榮','瑞芳','蘇澳新站','光復','猴硐','永樂','大富','三貂嶺','東澳','富源',
    '牡丹','南澳','瑞穗','雙溪','武塔','三民','貢寮','漢本','玉里','福隆','和平','東里','石城',
    '和仁','東竹','大里','崇德','富里','大溪','新城','池上','龜山','景美','海端','外澳','北埔',
    '關山','頭城','花蓮','瑞和','頂埔','吉安','瑞源','礁溪','志學','鹿野','四城','平和','山里',
    '宜蘭','壽豐','臺東','二結','豐田','中里','蘇澳新','蘇澳','屏東','歸來','麟洛','西勢','竹田',
    '潮州','崁頂','南州','鎮安','林邊','佳冬','東海','枋寮','加祿','內獅','枋山','古莊','大武',
    '瀧溪','金崙','太麻里','知本','康樂','臺東','三貂嶺','大華','十分','望古','嶺腳','平溪','菁桐','新竹',
    '北新竹','千甲','新莊','竹中','上員','榮華','竹東','橫山','九讚頭','合興','富貴','內灣','二水','源泉',
    '濁水','龍泉','集集','水里','車埕','成功','追分','中洲','長榮大學','沙崙','竹中','六家','瑞芳','海科館',
    '八斗子']
    train_time=['00','01','02','03','04','05','06','07','08','09',
    '10','11','12','13','14','15','16','17','18','19',
    '20','21','22','23','24']

    if fbid in idrecevied_message:
        idrecevied_message[fbid] = changeword(idrecevied_message[fbid],1)
        idrecevied_message[fbid] = changeword(idrecevied_message[fbid],3)#台鐵json是這個"臺"

    print(Train_Departure)
    print(Train_Destination)
    print(Train_DepartTime)
    print(Train_ArriveTime)
    print("火車每次剛進來時資料")

    if fbid not in Train_DepartTime and fbid in Train_Destination:
        kk=0
        for trahour in range(25):
            if fbid in idrecevied_message:
                if train_time[trahour] in idrecevied_message[fbid]:
                    Train_DepartTime.update({fbid:train_time[trahour]})
                    print(Train_Departure)
                    print(Train_Destination)
                    print(Train_DepartTime)
                    print(Train_ArriveTime)
                    print("火車全部收齊後的資料")
                    Train_url = "http://ptx.transportdata.tw/MOTC/v2/Rail/TRA/DailyTimetable/Today?$format=JSON"
                    Train_data = request(Train_url)
                    # with open(user_url+r'\GooglemapBot\jsondata\時刻表\Train_180223.json', 'r', encoding="utf-8") as f:
                    #     Train_data = json.load(f)                    

                    Train_list1 = []
                    Train_list2 = []
                    Train_list3 = []
                    Train_list4 = []
                    Train_list5 = []
                    Train_list6 = []
                    Train_list7 = []
                    Train_list8 = []
                    Train_list9 = []

                    for i in range(len(Train_data)):
                        b = len(Train_data[i]["StopTimes"]) #計算第i班高鐵有幾個停靠站
                        #print(b)
                        for j in range(len(Train_data[i]["StopTimes"])): #第i班列車的StopTimes(時刻表)裡的第j筆資料
                            if Train_data[i]["StopTimes"][j]["StationName"]["Zh_tw"] == Train_Departure[fbid]: #該班次會在上車車站停靠
                                k = j + 1
                                for k in range(k,b):
                                    if Train_data[i]["StopTimes"][k]["StationName"]["Zh_tw"] == Train_Destination[fbid]: #該班次會在下車車站停靠
                                        if Train_ArriveTime.strip() == '': #以下車時間的空值與否來判斷出發時間是否有值，並以此時間作為搜尋條件
                                            m = Train_data[i]["StopTimes"][j]["ArrivalTime"].find(Train_DepartTime[fbid]) #在data[i]['StopTimes'][j]['ArrivalTime']裡找尋和depart_time相符的值在第幾位，並存到m
                                            #print(m)
                                            if 2 > m >= 0: #若無符合內容，m會等於-1，反之為0或1
                                                Train_list1.append(str(Train_data[i]["DailyTrainInfo"]["TrainNo"])) #將車次號碼存到list1；因為車號是int，故需轉為str
                                                Train_list2.append(Train_data[i]["StopTimes"][j]["DepartureTime"]) #將上車車站的出發時間存到list2
                                                Train_list3.append(Train_data[i]["StopTimes"][k]["ArrivalTime"]) #將下車車站的抵達時間存到list3
                                                Train_list4.append(Train_data[i]['DailyTrainInfo']['TrainTypeName']['Zh_tw'])
                                                Train_list5.append(Train_data[i]['DailyTrainInfo']['WheelchairFlag'])
                                                Train_list6.append(Train_data[i]['DailyTrainInfo']['PackageServiceFlag'])
                                                Train_list7.append(Train_data[i]['DailyTrainInfo']['DiningFlag'])
                                                Train_list8.append(Train_data[i]['DailyTrainInfo']['BikeFlag'])
                                                Train_list9.append(Train_data[i]['DailyTrainInfo']['BreastFeedingFlag'])
                                        elif Train_DepartTime[fbid].strip() == "": #以上車時間的空值與否來判斷抵達時間是否有值，並以此時間作為搜尋條件
                                            m = Train_data[i]["StopTimes"][k]["ArrivalTime"].find(Train_ArriveTime)
                                            #print(m)
                                            if 2 > m >= 0:
                                                Train_list1.append(str(Train_data[i]["DailyTrainInfo"]["TrainNo"]))
                                                Train_list2.append(Train_data[i]["StopTimes"][j]["DepartureTime"])
                                                Train_list3.append(Train_data[i]["StopTimes"][k]["ArrivalTime"])
                                                Train_list4.append(Train_data[i]['DailyTrainInfo']['TrainTypeName']['Zh_tw'])
                                                Train_list5.append(Train_data[i]['DailyTrainInfo']['WheelchairFlag'])
                                                Train_list6.append(Train_data[i]['DailyTrainInfo']['PackageServiceFlag'])
                                                Train_list7.append(Train_data[i]['DailyTrainInfo']['DiningFlag'])
                                                Train_list8.append(Train_data[i]['DailyTrainInfo']['BikeFlag'])
                                                Train_list9.append(Train_data[i]['DailyTrainInfo']['BreastFeedingFlag'])
                                        else: #若兩者皆有值，便以出發時間作為搜尋條件
                                            m = Train_data[i]["StopTimes"][j]["ArrivalTime"].find(Train_DepartTime[fbid])
                                            #print(m)
                                            if 2 > m >= 0:
                                                Train_list1.append(str(Train_data[i]["DailyTrainInfo"]["TrainNo"]))
                                                Train_list2.append(Train_data[i]["StopTimes"][j]["DepartureTime"])
                                                Train_list3.append(Train_data[i]["StopTimes"][k]["ArrivalTime"]) 
                                                Train_list4.append(Train_data[i]['DailyTrainInfo']["TrainTypeName"]['Zh_tw'])
                                                Train_list5.append(Train_data[i]['DailyTrainInfo']['WheelchairFlag'])
                                                Train_list6.append(Train_data[i]['DailyTrainInfo']['PackageServiceFlag'])
                                                Train_list7.append(Train_data[i]['DailyTrainInfo']['DiningFlag'])
                                                Train_list8.append(Train_data[i]['DailyTrainInfo']['BikeFlag'])
                                                Train_list9.append(Train_data[i]['DailyTrainInfo']['BreastFeedingFlag'])

                    Train_dict = {"車次":Train_list1, "車種":Train_list4 , "開車時間":Train_list2, "抵達時間":Train_list3, 
                                  "輪椅":Train_list5, "行李":Train_list6, "餐車":Train_list7, "自行車":Train_list8, "哺乳室":Train_list9}  
                    columns = ["車次", "車種", "開車時間", "抵達時間", "輪椅", "行李", "餐車", "自行車", "哺乳室"]

                    print(Train_dict)
                    if len(Train_dict["車次"]) == 0:
                        wave(fbid, post_message_url)
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"這時間好像沒有車欸……"}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        last_word.update({fbid:Train_DepartTime[fbid]})
                        anyQuestion(fbid,post_message_url)
                        delete_everything(fbid)
                        Train_ArriveTime=''
                        if fbid in Train_Departure:
                            del Train_Departure[fbid]
                        if fbid in Train_Destination:
                            del Train_Destination[fbid]
                        if fbid in Train_DepartTime:
                            del Train_DepartTime[fbid]

                    else :
                        if Train_ArriveTime.strip() == "":
                            print("以下是["+Train_DepartTime[fbid] +"點]"+"從["+Train_Departure[fbid]+"]前往["+Train_Destination[fbid]+"]的所有班次喔！\n")
                            wave(fbid, post_message_url)
                            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是["+Train_DepartTime[fbid] +"點]"+"從["+Train_Departure[fbid]+"]前往["+Train_Destination[fbid]+"]的所有班次喔！\n"}})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        elif Train_DepartTime[fbid].strip() == "":
                            print("以下是["+Train_ArriveTime+"點]"+"從["+Train_Departure[fbid]+"]抵達["+Train_Destination[fbid]+"]的所有班次喔！\n")
                        else:
                            print("以下是["+Train_DepartTime[fbid] +"點]"+"從["+Train_Departure[fbid]+"]前往["+Train_Destination[fbid]+"]的所有班次喔！\n")
                            print("車次"+"  "+"車種"+"  "+"開車時間"+"  "+"抵達時間")
                            print(Train_DepartTime)
                        wave(fbid, post_message_url)
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"車次　車種　開車時間　抵達時間"}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        for x in range(len(Train_dict["車次"])):
                            print(Train_dict['車次'][x],Train_dict['車種'][x],Train_dict['開車時間'][x],Train_dict['抵達時間'][x])
                            wave(fbid, post_message_url)
                            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":Train_dict['車次'][x]+"  "+Train_dict['車種'][x]+"  "+Train_dict['開車時間'][x]+"  "+Train_dict['抵達時間'][x]}})
                            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)


                        last_word.update({fbid:Train_DepartTime[fbid]})
                        anyQuestion(fbid,post_message_url)
                        delete_everything(fbid)
                        Train_ArriveTime=''
                        if fbid in Train_Departure:
                            del Train_Departure[fbid]
                        if fbid in Train_Destination:
                            del Train_Destination[fbid]
                        if fbid in Train_DepartTime:
                            del Train_DepartTime[fbid]

                    print(idcheck)
                    print(idrecevied_message)
                    print(Train_Departure)
                    print(Train_Destination)
                    print(Train_DepartTime)
                    print(last_word)
                    print("台鐵完後的資料台鐵完後的資料台鐵完後的資料台鐵完後的資料台鐵完後的資料")
                        
                else:
                    if kk == 24:
                        wave(fbid, post_message_url)
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"真是的，你的時間可能打錯了啦( -`д´-)"}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    kk+=1

    elif fbid not in Train_Destination and fbid in Train_Departure:
        tranumber=len(trastation)
        kk=0
        for tra in range(tranumber):
            if trastation[tra] in idrecevied_message[fbid]: 
                Train_Destination.update({fbid:trastation[tra]})
                print(Train_Destination)
                print("上面是結束站")
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你想搭大約幾點的車呢？"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            else:
                if kk == tranumber - 1:
                    wave(fbid, post_message_url)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"真是的，你的站名是不是打錯了啊( -`д´-)"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                kk+=1
                
    elif fbid not in Train_Departure:
        tranumber=len(trastation)
        kk=0
        for tra in range(tranumber): 
            if trastation[tra] in idrecevied_message[fbid]:
                Train_Departure.update({fbid:trastation[tra]})
                print(Train_Departure)
                print("上面是開始站")
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要在哪裡下車啊？說不定等等我會碰地出現在你身後喔，開玩笑的啦～"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            else:
                if kk == tranumber - 1:
                    wave(fbid, post_message_url)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"真是的，你的站名是不是打錯了啊( -`д´-)"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                kk+=1


def GMap_placeid(store_id):
    GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'
    G_language = 'zh-TW'

    dt_nav_request = 'placeid={}&language={}&key={}'.format(store_id, G_language, GM_API_KEY)
    dt_request = "https://maps.googleapis.com/maps/api/place/details/json?" + dt_nav_request
    dt_request_trans = urllib.parse.quote(dt_request, safe = string.printable)
    respone = urllib.request.urlopen(dt_request_trans).read()
    
    dt_directions = json.loads(respone.decode('utf-8'))
    result = dt_directions['result']

    # google可抓取類別：名稱(0)、電話(1)、地址(2)、營業時間(3)、評價(4)、網站(5)、googlemap頁面(6)

    P_name = result['name']

    if 'formatted_phone_number' in result :
        P_phone = result['formatted_phone_number']
    else :
        P_phone = '這個地點目前沒有電話的資訊欸(ಠ_ಠ)'

    if 'formatted_address' in result :
        P_address = result['formatted_address']
    else :
        P_address = '這個地點目前沒有地址的資訊欸(ಠ_ಠ)'

    # 營業時間回傳值為list
    if 'opening_hours' in result :
        P_time = ''
        for i in range(0,7):
            P_time += result['opening_hours']['weekday_text'][i] + '\n'
    else :
        P_time = '這個地點目前沒有營業時間的資訊欸(ಠ_ಠ)'

    if 'rating' in result :
        P_grade = str(result['rating'])
    else :
        P_grade = '這個地點目前沒有評價的資訊欸(ಠ_ಠ)'

    if 'website' in result :
        P_web = result['website']
    else :
        P_web = '這個地點目前沒有網站的資訊欸(ಠ_ಠ)'

    P_GMweb = result['url']

    id_response = [ P_name, P_phone, P_address, P_time, P_grade, P_web, P_GMweb]

    return id_response


# Google Places API Web Service Search
# Google Places API Web Service Details
def GMap_place_detailssearch(center, fbid, post_message_url):
    ### id search
    GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'

    global  longlat

    G_query = center.replace(' ', '+')
    G_language = 'zh-TW'

    id_nav_request = 'query={}&language={}&key={}'.format(G_query, G_language, GM_API_KEY)
    id_request = "https://maps.googleapis.com/maps/api/place/textsearch/json?" + id_nav_request

    # url中不可包含中文等無法處理之字→需轉換成「%XX」
    # urllib.parse.quote(string, safe='/', encoding=None, errors=None)
    # https://www.zhihu.com/question/22899135       https://docs.python.org/3/library/urllib.parse.html#url-quoting。    
    request_trans = urllib.parse.quote(id_request, safe = string.printable)
    respone = urllib.request.urlopen(request_trans).read()
    id_directions = json.loads(respone.decode('utf-8'))

    id_results = id_directions['results']

    if len(id_results) != 0 :#只有一個地點

        # 回傳地點經緯度
        geometry = id_results[0]['geometry']
        location = geometry['location']
        place = [location['lat'], location['lng']]

        # 回復地點ID
        place_id = id_results[0]['place_id']

        dt_nav_request = 'placeid={}&language={}&key={}'.format(place_id, G_language, GM_API_KEY)
        dt_request = "https://maps.googleapis.com/maps/api/place/details/json?" + dt_nav_request
        dt_request_trans = urllib.parse.quote(dt_request, safe = string.printable)
        
        respone = urllib.request.urlopen(dt_request_trans).read()
        dt_directions = json.loads(respone.decode('utf-8'))

        result = dt_directions['result']
         # google可抓取類別：名稱(0)、電話(1)、地址(2)、營業時間(3)、評價(4)、網站(5)、googlemap頁面(6)

        P_name = result['name']

        if 'formatted_phone_number' in result :
            P_phone = result['formatted_phone_number']
        else :
            P_phone = '這個地點目前沒有電話的資訊欸(ಠ_ಠ)'

        if 'formatted_address' in result :
            P_address = result['formatted_address']
        else :
            P_address = '這個地點目前沒有地點的資訊欸(ಠ_ಠ)'

        # 營業時間回傳值為list
        if 'opening_hours' in result :
            P_time = ''
            for i in range(0,7):
                P_time += result['opening_hours']['weekday_text'][i] + '\n'
        else :
            P_time = '這個地點目前沒有營業時間的資訊欸(ಠ_ಠ)'

        if 'rating' in result :
            P_grade = str(result['rating'])
        else :
            P_grade = '這個地點目前沒有評價的資訊欸(ಠ_ಠ)'

        if 'website' in result :
            P_web = result['website']
        else :
            P_web = '這個地點目前沒有網站的資訊欸(ಠ_ಠ)'

        P_GMweb = result['url']

        response = [ P_name, P_phone, P_address, P_time, P_grade, P_web, P_GMweb , place]
        
        return response

    else:#有多個地點或是找不到
        
        if Gmap_num[fbid] == 0:
            return '1'

        if fbid in longlat:
            user = str(longlat[fbid][1])+', '+str(longlat[fbid][0])
            user_location = GMap_place_detailssearch(user, fbid, post_message_url)[7]
        ### rada search

            rada_location = str(user_location[0]) + ',' + str(user_location[1])
            radius = 1000

            rada_nav_request = 'location={}&radius={}&keyword={}&key={}'.format(rada_location, radius,  G_query, GM_API_KEY)
            rada_request = "https://maps.googleapis.com/maps/api/place/radarsearch/json?" + rada_nav_request

            rada_request_trans = urllib.parse.quote(rada_request, safe = string.printable)
            respone = urllib.request.urlopen(rada_request_trans).read()
            rada_directions = json.loads(respone.decode('utf-8'))

        
            if len(rada_directions['results']) == 0:
                # warntext = "您所在的區域附近500公尺內暫時沒有你想搜尋的店家喔"
                return '0'
            else:
                # query_long = len(rada_directions['results'])
                # if len(rada_directions['results']) > 5:
                #     query_long = 5
                T_name = ''
                T_phone = ''
                T_address = ''
                T_time = ''
                T_grade = ''
                T_web = ''
                T_GMweb = ''

                # for i in range(query_long):
                store_id = rada_directions['results'][0]['place_id']
                T_name = str(GMap_placeid(store_id)[0]) + '\n'
                T_phone = str(GMap_placeid(store_id)[0]) + "的電話是：" + str(GMap_placeid(store_id)[1])
                T_address = str(GMap_placeid(store_id)[0]) + "的地址是：" + str(GMap_placeid(store_id)[2])
                T_time = str(GMap_placeid(store_id)[0]) + "的營業時間是：\n" + str(GMap_placeid(store_id)[3])
                T_grade = str(GMap_placeid(store_id)[0]) + "的評分是：" + str(GMap_placeid(store_id)[4])
                T_web = str(GMap_placeid(store_id)[0]) + "的網站是：" + str(GMap_placeid(store_id)[5])
                T_GMweb = str(GMap_placeid(store_id)[0]) + "的Google Map搜尋結果是：" + str(GMap_placeid(store_id)[6])

                T_response = [T_name,T_phone,T_address,T_time,T_grade,T_web,T_GMweb]
                print(T_response)
                print("上面是TTTTTTTTTTTTTTTTTTT_response")
                return T_response

def message_contents(fbid, sentence, mci, mcs):

    global Gmap_num, longlat, nba, idcheck
    
    mcj=''
    post_message_url = 'https://graph.facebook.com/v3.0/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN

    if fbid in longlat:
        # google可抓取類別：名稱(0)、電話(1)、地址(2)、營業時間(3)、評價(4)、網站(5)、googlemap頁面(6)
        #GMap_place_detailssearch(sentence, fbid, post_message_url)[0]的[0]就是指名稱
        if GMap_place_detailssearch(sentence, fbid, post_message_url) == '0' :
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"我好像找不到這個地方欸，還是你能告訴我更多資訊呢？","quick_replies":[
                {
                     "content_type":"text",
                     "title":"是",
                     "payload":"<QA_YES>"
                },
                {
                     "content_type":"text",
                     "title":"下次吧",
                     "payload":"<QA_NO>"
                }
                ]}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            print(nba)
            print("最後的nba最後的nba最後的nba最後的nba最後的nba最後的nba最後的nba")

        elif GMap_place_detailssearch(sentence, fbid, post_message_url) != '0':
            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":GMap_place_detailssearch(sentence, fbid, post_message_url)[mci]}})
            # # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"輸入的文字為：" + sentence}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            
            if mci == 5:
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"給你" + sentence + "的網址，希望能幫助到你！"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            if mci == 2:
                post_facebook_message_media(fbid, GMap_map(nba[idd]))
            anyQuestion(fbid,post_message_url)
            mcj = GMap_place_detailssearch(sentence, fbid, post_message_url)[mci]
            delete_everything(fbid)
            if fbid in Gmap_num:
                del Gmap_num[fbid]
            toiletlat=''
            toiletlong=''
            print(mcj)
    else:
        if GMap_place_detailssearch(sentence, fbid, post_message_url) == '1':#有多個地點或是找不到
            print("這裡應該是問的地方有多個地點")
            if Gmap_num[fbid] == 0:
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'你問的地方有許多據點，選擇一個位置，讓我告訴你附近據點的資訊吧！',"quick_replies":[
                    {
                    "content_type":"location"
                    }
                ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                Gmap_num[fbid] += 1
                if mci == 1:
                    idcheck.update({fbid:"電話"})
                elif mci == 2:
                    idcheck.update({fbid:"地址"})
                elif mci == 3:
                    idcheck.update({fbid:"營業時間"})
                elif mci == 4:
                    idcheck.update({fbid:"評價"})


            elif Gmap_num[fbid] > 0 and fbid not in longlat:
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'你要按下面的傳送位置鈕啊！不然我怎麼看得懂嘛！',"quick_replies":[
                    {
                    "content_type":"location"
                    }
                ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        else:
            print("這裡是問的地方只有一個地方所以直接給答案")

            if mci == 1 or mci == 3 or mci == 4:
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":GMap_place_detailssearch(sentence, fbid, post_message_url)[0]+"的"+mcs+'是\n'}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            elif mci == 2:
                wave(fbid, post_message_url)
                if fbid in nba:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是" + nba[fbid] + "的位置資訊，\n" + "https://www.google.com.tw/maps/search/" + nba[fbid]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                else:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你想問的是哪裡的位置呢？"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                post_facebook_message_media(fbid, GMap_map(nba[idd]))
            
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":GMap_place_detailssearch(sentence, fbid, post_message_url)[mci]}})
            # # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"輸入的文字為：" + sentence}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            
            anyQuestion(fbid,post_message_url)
            mcj=GMap_place_detailssearch(sentence, fbid, post_message_url)[mci]
            print(mcj, "這是mcj")
            delete_everything(fbid)
            if fbid in Gmap_num:
                del Gmap_num[fbid]



def anyQuestion(fbid,post_message_url):
    wave(fbid, post_message_url)
    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'還有什麼想問我的嗎？',"quick_replies":[
        {
            "content_type":"text",
            "title":"沒問題了",
            "payload":"<POSTBACK_PAYLOAD>",
        },
        {
            "content_type":"text",
            "title":"我還有問題",
            "payload":"<POSTBACK_PAYLOAD>",
        },
        {
            "content_type":"text",
            "title":"我有建議要說",
            "payload":"<suggestion_inanyQ>",
        },
        {
            "content_type":"text",
            "title":"學妹能幫你什麼？",
            "payload":"<POSTBACK_PAYLOAD>",
        }
        ]}})
    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)



#wifi函數
def wifi(fbid, post_message_url):
    with open(user_url+r'\GooglemapBot\jsondata\wifi.json', 'r', encoding="utf-8") as f:
        wifidata = json.load(f)
    gmaps = googlemaps.Client(key='AIzaSyBa-fjzE3tQFWlybQD_cFfSlMsdks4AvxQ')

    global  longlat, toiletlat, toiletlong, wrongcheck
    wifians = 0
    wifinum = 0
    abc = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    j = 1
    addressmap = ''
    if fbid in longlat:
        wifiaddress=[]
        wifiaddress=[str(longlat[fbid][1])+', '+str(longlat[fbid][0])]
        a = longlat[fbid][1]
        b = longlat[fbid][0]

        long = len(wifidata)
        wave(fbid, post_message_url)
        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'這附近有Wifi的地方有這些喔！'}})
        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

        for i in range(long):
            if ((float(wifidata[i]['LATITUDE'])-a)**2+(float(wifidata[i]['LONGITUDE'])-b)**2) < 0.000020295025:    #0.00000901度 = 1公尺 500m
                #print(wifidata[i]['Name']+'，地址是'+wifidata[i]['Address'])
                wifians = wifians + 1
                if j == 1:
                    wave(fbid, post_message_url)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'1. 你傳送的位置'}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                j += 1
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":abc[j-2]+'. '+wifidata[i]['NAME']+'，地址是'+wifidata[i]['ADDR']}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                wifinum+=1 #地圖用
                wifiaddress.append(wifidata[i]['ADDR'])
        if wifians == 0 :
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'這附近似乎沒有地方有Wifi欸……還是你可以告訴人家更多資訊呢(∩´﹏`∩)？',"quick_replies":[
            {
                 "content_type":"text",
                 "title":"是",
                 "payload":"<QA_YES>"
            },
            {
                 "content_type":"text",
                 "title":"下次吧",
                 "payload":"<QA_NO>"
            }
            ]}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            wrongcheck.update({fbid:-1})
        if wifinum != 0:
            addressmap=soptsoptmap(wifinum,wifiaddress)
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":{"type":"image", "payload":{"url":addressmap}}}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"},data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'上面都是附近有wifi的地方喔！圖片裡的藍點為相對應編號的位置。'}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            wrongcheck.update({fbid:-1})

        wifians = 0
        toiletlat=''
        toiletlong=''
        last_word.update({fbid:idrecevied_message[fbid]})
        anyQuestion(fbid,post_message_url)
        delete_everything(fbid)


    elif wrongcheck[fbid] >= 0 :
        wave(fbid, post_message_url)
        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'按下傳送地點，我才會知道在哪裡哦！',"quick_replies":[
        # {
        #     "content_type":"text",
        #     "title":"搜尋",
        #     "payload":"<POSTBACK_PAYLOAD>",
        # },
            {
            "content_type":"location"
            }
        ]}})
        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        
        if fbid in wrongcheck:
            wrongcheck[fbid] += 1

#廁所函數
def toilet(fbid, post_message_url):
    with open(user_url+r'\GooglemapBot\jsondata\toilet.json', 'r', encoding="utf-8") as f:
        toiletdata = json.load(f)
    gmaps = googlemaps.Client(key='AIzaSyBa-fjzE3tQFWlybQD_cFfSlMsdks4AvxQ')

    global  longlat,toiletlat, toiletlong, wrongcheck
    abc = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    toiletans = 0
    toiletnum = 0
    j = 1
    addressmap=''

    if fbid in longlat:
        toiletaddress=[]
        toiletaddress=[str(longlat[fbid][1])+', '+str(longlat[fbid][0])]
        a = longlat[fbid][1]
        b = longlat[fbid][0]
        long = len(toiletdata)

        for i in range(long):
            if ((float(toiletdata[i]['Latitude'])-a)**2+(float(toiletdata[i]['Longitude'])-b)**2) < 0.000003247204:    #0.00000901度 = 1公尺 500m
                print(toiletdata[i]['Name']+'，地址是'+toiletdata[i]['Address'])
                toiletans=toiletans+1
                if j==1:
                    wave(fbid, post_message_url)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'1. 你傳送的位置'}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                j=j+1
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":abc[j - 2]+'. '+toiletdata[i]['Name']+'，地址是'+toiletdata[i]['Address']}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                toiletnum+=1 #地圖用
                toiletaddress.append(toiletdata[i]['Latitude']+', '+toiletdata[i]['Longitude'])
                print("這是兩百公尺的答案")
        if toiletans == 0 :
            for i in range(long):
                if ((float(toiletdata[i]['Latitude'])-a)**2+(float(toiletdata[i]['Longitude'])-b)**2) < 0.000020295025:    #0.00000901度 = 1公尺 500m
                    print("因為兩百公尺內沒有 所以找五百公尺")
                    print(toiletdata[i]['Name']+'，地址是'+toiletdata[i]['Address'])
                    toiletans=toiletans+1
                    if j==1:
                        wave(fbid, post_message_url)
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'1. 你傳送的位置'}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    j=j+1
                    wave(fbid, post_message_url)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":abc[j - 2]+'. '+toiletdata[i]['Name']+'，地址是'+toiletdata[i]['Address']}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    toiletnum+=1 #地圖用
                    toiletaddress.append(toiletdata[i]['Latitude']+', '+toiletdata[i]['Longitude'])
                    print("這是五百公尺的答案")
            if toiletans == 0 :
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'這附近似乎沒有廁所欸……還是你可以跟我說這附近哪裡有廁所？',"quick_replies":[
                {
                     "content_type":"text",
                     "title":"是",
                     "payload":"<QA_YES>"
                },
                {
                     "content_type":"text",
                     "title":"下次吧",
                     "payload":"<QA_NO>"
                }
                ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                wrongcheck.update({fbid:-1})
        if toiletnum != 0:
            addressmap=soptsoptmap(toiletnum,toiletaddress)
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":{"type":"image", "payload":{"url":addressmap}}}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"},data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'上面是所有附近廁所的地址喔！圖片為相對應編號的位置。'}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            wrongcheck.update({fbid:-1})
            anyQuestion(fbid,post_message_url)

        last_word.update({fbid:idrecevied_message[fbid]})
        delete_everything(fbid)
        toiletans=0
        toiletlat=''
        toiletlong=''
        
    elif wrongcheck[fbid] >= 0 :
        wave(fbid, post_message_url)
        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'按下傳送地點，我才會知道在哪裡哦！',"quick_replies":[
        # {
        #     "content_type":"text",
        #     "title":"搜尋",
        #     "payload":"<POSTBACK_PAYLOAD>",
        # },
            {
            "content_type":"location",
            "title":"傳送地點"
            }
        ]}})
        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

        if fbid in wrongcheck:
            wrongcheck[fbid] += 1


def ATM(fbid, post_message_url):
    with open(user_url+r'\GooglemapBot\jsondata\post_atm.json', 'r', encoding="utf-8") as f:
        atmdata = json.load(f)
    gmaps = googlemaps.Client(key='AIzaSyBa-fjzE3tQFWlybQD_cFfSlMsdks4AvxQ')
    global  longlat, toiletlat, toiletlong, wrongcheck
    abc = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    atmans = 0
    atmnum = 0
    j = 1
    addressmap=''
    print("進ATM了進ATM了進ATM了進ATM了進ATM了進ATM了進ATM了")

    if fbid in longlat:
        atmaddress=[]
        atmaddress=[str(longlat[fbid][1])+', '+str(longlat[fbid][0])]
        a = longlat[fbid][1]
        b = longlat[fbid][0]

        long = len(atmdata)

        for i in range(long):
            if ((float(atmdata[i]['緯度'])-a)**2+(float(atmdata[i]['經度'])-b)**2) < 0.000020295025:    #0.00000901度 = 1公尺 500m
                print(atmdata[i]['局名']+'，地址是'+atmdata[i]['郵局地址'])
                atmans=atmans+1
                if j==1:
                    wave(fbid, post_message_url)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'1. 你傳送的位置'}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                j=j+1
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":abc[j - 2]+'. '+atmdata[i]['局名']+'，地址是'+atmdata[i]['郵局地址']}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                atmnum+=1 #地圖用
                atmaddress.append(atmdata[i]['郵局地址'])
        if atmans==0 :
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'這附近似乎沒有ATM欸……還是你可以告訴人家更多資訊呢(∩´﹏`∩)？',"quick_replies":[
            {
                 "content_type":"text",
                 "title":"是",
                 "payload":"<QA_YES>"
            },
            {
                 "content_type":"text",
                 "title":"下次吧",
                 "payload":"<QA_NO>"
            }
            ]}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            wrongcheck.update({fbid:-1})

        if atmnum!=0:
            addressmap=soptsoptmap(atmnum,atmaddress)
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":{"type":"image", "payload":{"url":addressmap}}}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"},data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'上面是所有附近ATM的地址喔！圖片為相對應編號的位置。'}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            anyQuestion(fbid,post_message_url)
            wrongcheck.update({fbid:-1})
        atmans=0
        last_word.update({fbid:idrecevied_message[fbid]})
        delete_everything(fbid)
        toiletlat=''
        toiletlong=''

    elif wrongcheck[fbid] >= 0:
        wave(fbid, post_message_url)
        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'按下傳送地點，我才會知道在哪裡哦！',"quick_replies":[
            {
            "content_type":"location"
            }
        ]}})
        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
    
    if fbid in wrongcheck:
        wrongcheck[fbid] += 1

#換字函數
def changeword(recevied_message, check_city):
    ls = list(recevied_message)
    print(ls)
    if check_city == 1:
        for icw in range(len(ls)):

            if ls[icw] == '臺':
                ls[icw] = '台'
            if ls[icw] == '點' or ls[icw] == '鐘' or ls[icw] == '的' or ls[icw] == '吧' or ls[icw] == '哦' or ls[icw] == '喔' or ls[icw] == '～' or ls[icw] == '~':
                ls[icw] = ''

            if icw == len(ls)-1 and icw == 0:#ls只有一個字
                if ls[icw] == '1':
                    ls[icw] = '01'
                if ls[icw] == '2' or ls[icw] == '二':
                    ls[icw] = '02'
                if ls[icw] == '3' or ls[icw] == '三':
                    ls[icw] = '03'
                if ls[icw] == '4' or ls[icw] == '四':
                    ls[icw] = '04'
                if ls[icw] == '5' or ls[icw] == '五':
                    ls[icw] = '05'
                if ls[icw] == '6' or ls[icw] == '六':
                    ls[icw] = '06'
                if ls[icw] == '7' or ls[icw] == '七':
                    ls[icw] = '07'
                if ls[icw] == '8' or ls[icw] == '八':
                    ls[icw] = '08'
                if ls[icw] == '9' or ls[icw] == '九':
                    ls[icw] = '09'
            elif icw == len(ls)-1 and icw != 0:#到了最後一個字而且ls不只一個字
                if ls[icw] == '1' and ls[icw-1] == '0':
                    ls[icw-1] = ''
                if (ls[icw] == '1' or ls[icw] == '一') and ls[icw-1] != '1' and ls[icw-1] != '2':
                    ls[icw] = '01'
                if (ls[icw] == '2' or ls[icw] == '二' or ls[icw] == '兩') and ls[icw-1] != '1' and ls[icw-1] != '2':
                    ls[icw] = '02'
                if (ls[icw] == '3' or ls[icw] == '三') and ls[icw-1] != '1' and ls[icw-1] != '2':
                    ls[icw] = '03'
                if (ls[icw] == '4' or ls[icw] == '四') and ls[icw-1] != '1' and ls[icw-1] != '2':
                    ls[icw] = '04'
                if (ls[icw] == '5' or ls[icw] == '五') and ls[icw-1] != '1' and ls[icw-1] != '2':
                    ls[icw] = '05'
                if (ls[icw] == '6' or ls[icw] == '六') and ls[icw-1] != '1' and ls[icw-1] != '2':
                    ls[icw] = '06'
                if (ls[icw] == '7' or ls[icw] == '七') and ls[icw-1] != '1' and ls[icw-1] != '2':
                    ls[icw] = '07'
                if (ls[icw] == '8' or ls[icw] == '八') and ls[icw-1] != '1' and ls[icw-1] != '2':
                    ls[icw] = '08'
                if (ls[icw] == '9' or ls[icw] == '九') and ls[icw-1] != '1' and ls[icw-1] != '2':
                    ls[icw] = '09'
                if ls[icw] == '' and len(ls) != 2:#最後一個字是空的 可能是'點'
                    if (ls[icw-1] == '1' or ls[icw-1] == '一') and ls[icw-2] != '1' and ls[icw-2] != '2':
                        ls[icw-1] = '01'
                    if (ls[icw-1] == '2' or ls[icw-1] == '二' or ls[icw-1] == '兩') and ls[icw-2] != '1' and ls[icw-2] != '2':
                        ls[icw-1] = '02'
                    if (ls[icw-1] == '3' or ls[icw-1] == '三') and ls[icw-2] != '1' and ls[icw-2] != '2':
                        ls[icw-1] = '03'
                    if (ls[icw-1] == '4' or ls[icw-1] == '四') and ls[icw-2] != '1' and ls[icw-2] != '2':
                        ls[icw-1] = '04'
                    if (ls[icw-1] == '5' or ls[icw-1] == '五') and ls[icw-2] != '1' and ls[icw-2] != '2':
                        ls[icw-1] = '05'
                    if (ls[icw-1] == '6' or ls[icw-1] == '六') and ls[icw-2] != '1' and ls[icw-2] != '2':
                        ls[icw-1] = '06'
                    if (ls[icw-1] == '7' or ls[icw-1] == '七') and ls[icw-2] != '1' and ls[icw-2] != '2':
                        ls[icw-1] = '07'
                    if (ls[icw-1] == '8' or ls[icw-1] == '八') and ls[icw-2] != '1' and ls[icw-2] != '2':
                        ls[icw-1] = '08'
                    if (ls[icw-1] == '9' or ls[icw-1] == '九') and ls[icw-2] != '1' and ls[icw-2] != '2':
                        ls[icw-1] = '09'
                    if ls[icw-1] == '' and len(ls) != 3:#最後兩個字都是空的
                        if (ls[icw-2] == '1' or ls[icw-2] == '一') and ls[icw-3] != '1' and ls[icw-3] != '2':
                            ls[icw-2] = '01'
                        if (ls[icw-2] == '2' or ls[icw-2] == '二' or ls[icw-2] == '兩') and ls[icw-3] != '1' and ls[icw-3] != '2':
                            ls[icw-2] = '02'
                        if (ls[icw-2] == '3' or ls[icw-2] == '三') and ls[icw-3] != '1' and ls[icw-3] != '2':
                            ls[icw-2] = '03'
                        if (ls[icw-2] == '4' or ls[icw-2] == '四') and ls[icw-3] != '1' and ls[icw-3] != '2':
                            ls[icw-2] = '04'
                        if (ls[icw-2] == '5' or ls[icw-2] == '五') and ls[icw-3] != '1' and ls[icw-3] != '2':
                            ls[icw-2] = '05'
                        if (ls[icw-2] == '6' or ls[icw-2] == '六') and ls[icw-3] != '1' and ls[icw-3] != '2':
                            ls[icw-2] = '06'
                        if (ls[icw-2] == '7' or ls[icw-2] == '七') and ls[icw-3] != '1' and ls[icw-3] != '2':
                            ls[icw-2] = '07'
                        if (ls[icw-2] == '8' or ls[icw-2] == '八') and ls[icw-3] != '1' and ls[icw-3] != '2':
                            ls[icw-2] = '08'
                        if (ls[icw-2] == '9' or ls[icw-2] == '九') and ls[icw-3] != '1' and ls[icw-3] != '2':
                            ls[icw-2] = '09'

                elif ls[icw] == '':
                    print("有進來ㄇ")
                    if (ls[icw-1] == '1' or ls[icw-1] == '一'):
                        ls[icw-1] = '01'
                    if (ls[icw-1] == '2' or ls[icw-1] == '二' or ls[icw-1] == '兩'):
                        ls[icw-1] = '02'
                    if (ls[icw-1] == '3' or ls[icw-1] == '三'):
                        ls[icw-1] = '03'
                    if (ls[icw-1] == '4' or ls[icw-1] == '四'):
                        ls[icw-1] = '04'
                    if (ls[icw-1] == '5' or ls[icw-1] == '五'):
                        ls[icw-1] = '05'
                    if (ls[icw-1] == '6' or ls[icw-1] == '六'):
                        ls[icw-1] = '06'
                    if (ls[icw-1] == '7' or ls[icw-1] == '七'):
                        ls[icw-1] = '07'
                    if (ls[icw-1] == '8' or ls[icw-1] == '八'):
                        ls[icw-1] = '08'
                    if (ls[icw-1] == '9' or ls[icw-1] == '九'):
                        ls[icw-1] = '09'
                    print(ls[icw-1], ls[icw],"進來後")
            elif icw == 0 and icw != len(ls)-1:#第一個字而且ls不只一個字
                if ls[icw] == '下' and ls[icw+1] == '午' and len(ls) == 5:
                    ls[icw] = ''
                    ls[icw+1] = ''
                    if ls[icw+2] == '1' and ls[icw+3] == '0':
                        ls[icw+2] = '2'
                        ls[icw+3] = '2'
                    elif ls[icw+2] == '1' and ls[icw+3] == '1' or ls[icw+2] == '十' and ls[icw+3] == '一':
                        ls[icw+2] = '2'
                        ls[icw+3] = '3'
                    elif ls[icw+2] == '1' and ls[icw+3] == '2' or ls[icw+2] == '十' and ls[icw+3] == '二':
                        ls[icw+2] = '0'
                        ls[icw+3] = '0'
                if ls[icw] == '下' and ls[icw+1] == '午' and len(ls) == 4:
                    ls[icw] = ''
                    ls[icw+1] = ''
                    if ls[icw+2] == '一':
                        ls[icw+2] = '1'
                    if ls[icw+2] == '二' or ls[icw+2] == '兩':
                        ls[icw+2] = '2'
                    if ls[icw+2] == '三':
                        ls[icw+2] = '3'
                    if ls[icw+2] == '四':
                        ls[icw+2] = '4'
                    if ls[icw+2] == '五':
                        ls[icw+2] = '5'
                    if ls[icw+2] == '六':
                        ls[icw+2] = '6'
                    if ls[icw+2] == '七':
                        ls[icw+2] = '7'
                    if ls[icw+2] == '八':
                        ls[icw+2] = '8'
                    if ls[icw+2] == '九':
                        ls[icw+2] = '9'
                    if ls[icw+2] == '十':
                        ls[icw+2] = '22'
                    if ls[icw+2] == '0' or ls[icw+2] == '1' or ls[icw+2] == '2' or ls[icw+2] == '3' or ls[icw+2] == '4' or ls[icw+2] == '5' or ls[icw+2] == '6' or ls[icw+2] == '7' or ls[icw+2] == '8' or ls[icw+2] == '9': 
                        ls[icw+2] = str(int(ls[icw+2])+12)
                if ls[icw] == '晚' and ls[icw+1] == '上' and len(ls) == 5:
                    ls[icw] = ''
                    ls[icw+1] = ''
                    if ls[icw+2] == '1' and ls[icw+3] == '0':
                        ls[icw+2] = '2'
                        ls[icw+3] = '2'
                    elif ls[icw+2] == '1' and ls[icw+3] == '1' or ls[icw+2] == '十' and ls[icw+3] == '一':
                        ls[icw+2] = '2'
                        ls[icw+3] = '3'
                    elif ls[icw+2] == '1' and ls[icw+3] == '2' or ls[icw+2] == '十' and ls[icw+3] == '二':
                        ls[icw+2] = '0'
                        ls[icw+3] = '0'
                if ls[icw] == '晚' and ls[icw+1] == '上' and len(ls) == 4:
                    ls[icw] = ''
                    ls[icw+1] = ''
                    if ls[icw+2] == '一':
                        ls[icw+2] = '1'
                    if ls[icw+2] == '二' or ls[icw+2] == '兩':
                        ls[icw+2] = '2'
                    if ls[icw+2] == '三':
                        ls[icw+2] = '3'
                    if ls[icw+2] == '四':
                        ls[icw+2] = '4'
                    if ls[icw+2] == '五':
                        ls[icw+2] = '5'
                    if ls[icw+2] == '六':
                        ls[icw+2] = '6'
                    if ls[icw+2] == '七':
                        ls[icw+2] = '7'
                    if ls[icw+2] == '八':
                        ls[icw+2] = '8'
                    if ls[icw+2] == '九':
                        ls[icw+2] = '9'
                    if ls[icw+2] == '十':
                        ls[icw+2] = '22'
                    if ls[icw+2] == '0' or ls[icw+2] == '1' or ls[icw+2] == '2' or ls[icw+2] == '3' or ls[icw+2] == '4' or ls[icw+2] == '5' or ls[icw+2] == '6' or ls[icw+2] == '7' or ls[icw+2] == '8' or ls[icw+2] == '9':
                        ls[icw+2] = str(int(ls[icw+2])+12)
                    
                if ls[icw] == '0' and (ls[icw+1] == '1' or ls[icw+1] == '2' or ls[icw+1] == '3' or ls[icw+1] == '4' or ls[icw+1] == '5' or ls[icw+1] == '6' or ls[icw+1] == '7' or ls[icw+1] == '8' or ls[icw+1] == '9'):
                    ls[icw] = ''
                if ls[icw] == '1' and ls[icw+1] != '0' and ls[icw+1] != '1' and ls[icw+1] != '2' and ls[icw+1] != '3' and ls[icw+1] != '4' and ls[icw+1] != '5' and ls[icw+1] != '6' and ls[icw+1] != '7' and ls[icw+1] != '8' and ls[icw+1] != '9':
                    ls[icw] = '01'
                if ls[icw] == '2' and ls[icw+1] != '0' and ls[icw+1] != '1' and ls[icw+1] != '2' and ls[icw+1] != '3' and ls[icw+1] != '4':
                    ls[icw] = '02'
                if ls[icw] == '3':
                    ls[icw] = '03'
                if ls[icw] == '4':
                    ls[icw] = '04'
                if ls[icw] == '5':
                    ls[icw] = '05'
                if ls[icw] == '6':
                    ls[icw] = '06'
                if ls[icw] == '7':
                    ls[icw] = '07'
                if ls[icw] == '8':
                    ls[icw] = '08'
                if ls[icw] == '9':
                    ls[icw] = '09'
                # if ls[icw] == '十':
                #     ls[icw] = '10'
                if ls[icw] == '十' and ls[icw+1] == '一':
                    ls[icw] = '11'
                    ls[icw+1] = ''
                if ls[icw] == '十' and ls[icw+1] == '二':
                    ls[icw] = '12'
                    ls[icw+1] = ''
                if ls[icw] == '十' and ls[icw+1] == '三':
                    ls[icw] = '13'
                    ls[icw+1] = ''
                if ls[icw] == '十' and ls[icw+1] == '四':
                    ls[icw] = '14'
                    ls[icw+1] = ''
                if ls[icw] == '十' and ls[icw+1] == '五':
                    ls[icw] = '15'
                    ls[icw+1] = ''
                if ls[icw] == '十' and ls[icw+1] == '六':
                    ls[icw] = '16'
                    ls[icw+1] = ''
                if ls[icw] == '十' and ls[icw+1] == '七':
                    ls[icw] = '17'
                    ls[icw+1] = ''
                if ls[icw] == '十' and ls[icw+1] == '八':
                    ls[icw] = '18'
                    ls[icw+1] = ''
                if ls[icw] == '十' and ls[icw+1] == '九':
                    ls[icw] = '19'
                    ls[icw+1] = ''
                if ls[icw] == '二' and ls[icw+1] == '十':
                    ls[icw] = '20'
                    ls[icw+1] = ''
                if ls[icw] == '早' and ls[icw+1] == '上':
                    ls[icw] = ''
                    ls[icw+1] = ''
                if ls[icw] == '上' and ls[icw+1] == '午':
                    ls[icw] = ''
                    ls[icw+1] = ''

            if icw == len(ls)-3:
                if ls[icw] == '火' and ls[icw+1] == '車' and ls[icw+2] == '站':
                    ls[icw] = ''
                    ls[icw+1] = ''
                    ls[icw+2] = ''
            if icw == len(ls)-2:
                if ls[icw] == '車' and ls[icw+1] == '站':
                    ls[icw] = ''
                    ls[icw+1] = ''
        
        recevied_message = ''.join(ls)

    elif check_city == 2:
        if recevied_message == '基隆' or recevied_message == '台北' or recevied_message == '新北' or recevied_message == '桃園' or recevied_message == '台中' or recevied_message == '台南' or recevied_message == '高雄': 
            recevied_message += '市'
        elif recevied_message == '苗栗' or recevied_message == '彰化' or recevied_message == '南投' or recevied_message == '雲林' or recevied_message == '宜蘭' or recevied_message == '花蓮' or  recevied_message == '台東' or recevied_message == '屏東' or recevied_message == '連江' or recevied_message == '金門' or recevied_message == '澎湖': 
            recevied_message += '縣'

    elif check_city == 3:
        for icw in range(len(ls)):
            if ls[icw] == '台':
                ls[icw] = '臺'
        recevied_message = ''.join(ls)

    print(recevied_message,"這是changerword完的成果")
    return recevied_message


def soptsoptmap(toiletnum,toiletaddress):
    # 多地點地圖顯示
    from urllib.parse import quote
    import urllib.request
    import json, string
        
    endpoint = "https://maps.googleapis.com/maps/api/staticmap?"
    GM_API_KEY = 'AIzaSyA35lPzOmBYaGtsGnu1BtuZiWqZcLpYdQk'

    abc = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']

    # G_center = center.replace(' ', '+')

    num = toiletnum+1

    if num >= 1:
        
    #     G_zoom = "16"
    #     G_size = "250x250"
        G_size = "1000x1000"
        nav_request = 'size={}'.format(G_size)
    #     nav_request = 'zoom={}&size={}'.format(G_zoom, G_size)
    #     nav_request = ""
        
        for i in range(0,num):
            address=toiletaddress[i]
            G_center = address.replace(' ', '+')
            if i == 0:
                G_MarkerLabel = "1" + "%7C"
                G_markers = "color:red%7C" + "label:" + G_MarkerLabel + "%7C" + G_center
            else:
                G_MarkerLabel = abc[i - 1] + "%7C"
    #           G_markers = "size:tiny%7c" + "color:red%7C"+ "label:" + G_MarkerLabel + G_center
                G_markers = "color:blue%7C"+ "label:" + G_MarkerLabel + "%7C" + G_center
            nav = '&markers={}'.format(G_markers)
            nav_request = nav_request + nav
        
        nav_request = nav_request + '&key=' + GM_API_KEY

    request_trans = urllib.parse.quote(nav_request, safe = string.printable)    
    G_request = endpoint + request_trans
    return (G_request)

#天氣函數
def weather(fbid, post_message_url,recevied_message):

    global weather_num,user_payload,wrongcheck,nba,ncityba,cityshiannum,weather_today,last_word
    print("\n\n")
    print(user_payload)
    print("進去前的payload")

    print("\n\n")

    taiwanCity=["台北","基隆","新北","桃園","新竹","苗栗","台中",
                "彰化","南投","雲林","嘉義","宜蘭","花蓮","台東",
                "台南","高雄","屏東","連江","金門","澎湖",
                "台北市","基隆市","新北市","桃園市","新竹市","新竹縣","苗栗縣","台中市",
                "彰化縣","南投縣","雲林縣","嘉義市","嘉義縣","宜蘭縣","花蓮縣","台東縣",
                "台南市","高雄市","屏東縣","連江縣","金門縣","澎湖縣"]

    #1.判斷使用者要查的時間 若回得不對就繼續問
    if idrecevied_message[fbid] != "現在" and  idrecevied_message[fbid] != "明天早上" and idrecevied_message[fbid] != "明天晚上" and idrecevied_message[fbid] != "今晚至明晨" and wrongcheck[fbid] == 0:
        wave(fbid, post_message_url)
        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"咦？人家好像看不懂欸～"}})
        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        if (5 <= int(weather_today) < 17):
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"可以再說一次嗎？","quick_replies":[
                {
                     "content_type":"text",
                     "title":"現在",
                     "payload":"<weather_now>"
                },
                {
                     "content_type":"text",
                     "title":"今晚至明晨",
                     "payload":"<weather_tomorrow_day>"
                },
                {
                     "content_type":"text",
                     "title":"明天早上",
                     "payload":"<weather_tomorrow_night>"
                }
                ]}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        else :
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"可以再說一次嗎？","quick_replies":[
                {
                     "content_type":"text",
                     "title":"現在",
                     "payload":"<weather_now>"
                },
                {
                     "content_type":"text",
                     "title":"明天早上",
                     "payload":"<weather_tomorrow_day>"
                },
                {
                     "content_type":"text",
                     "title":"明天晚上",
                     "payload":"<weather_tomorrow_night>"
                }
                ]}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
    #2.收到使用者要問的時間後才會進來
    else:
        print("下面喔喔喔喔喔喔喔喔喔喔喔喔喔")
        print(weather_num)
        print(cityshiannum)
        print("上面喔喔喔喔喔喔喔喔喔喔喔喔喔")

        #3.接收完整縣市訊息
        if weather_num == 0:
            if fbid in ncityba: #確定nba[fbid]有東西 不然會有error
                ncityba[fbid] = changeword(ncityba[fbid], 1)#把臺改台
                print(ncityba[fbid])
                print("changeword111111111111111111111111111111111111111111111111111")
            #4.防止使用者打縣市以外的東西
            if wrongcheck[fbid] == 0:
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你是想問哪一個縣市的天氣呢？"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            #5.判斷有沒有接收到縣市
            if fbid in ncityba and wrongcheck[fbid] >= 1:
                #6.如果是新竹或嘉義就要再進來判斷是縣還是市
                print(ncityba)
                print("上面市ncityba上面市ncityba上面市ncityba上面市ncityba上面市ncityba")
                if ncityba[fbid] in taiwanCity and cityshiannum == 0:
                    if ncityba[fbid] == "新竹" or ncityba[fbid] == "嘉義":
                        wave(fbid, post_message_url)
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"是縣還是市呢？","quick_replies":[
                            {
                                 "content_type":"text",
                                 "title":"縣",
                                 "payload":user_payload
                            },
                            {
                                 "content_type":"text",
                                 "title":"市",
                                 "payload":user_payload
                            }
                            ]}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        cityshiannum += 1
                    else:
                        weather_num+=1
                        ncityba[fbid] = changeword(ncityba[fbid], 2)
                        print(ncityba[fbid])
                        print("changeword22222222222222222222222222222222222222222222222222222222222222")
                elif idrecevied_message[fbid] != "縣" and idrecevied_message[fbid] != "市":
                    wave(fbid, post_message_url)
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"這好像不是縣市吧...?","quick_replies":[
                        {
                             "content_type":"text",
                             "title":"縣",
                             "payload":user_payload
                        },
                        {
                             "content_type":"text",
                             "title":"市",
                             "payload":user_payload
                        }
                            ]}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                elif idrecevied_message[fbid] == "縣" or idrecevied_message[fbid] == "市":
                    ncityba[fbid] = ncityba[fbid]+recevied_message
                    print(ncityba[fbid])
                    weather_num+=1
                    print("家ˋ一家一家一")
            #5-1如果使用者打得不是縣市就會一直在這裡
            elif wrongcheck[fbid] >= 1:
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"嗯？你是不是都沒認真看我說什麼(｡ŏ_ŏ)"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"跟我說你想查的縣市嘛"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            
            if fbid in wrongcheck:
                wrongcheck[fbid] += 1

        # 一切資訊都收到後weather_num變1 就會近來開始執行天氣的程式
        if weather_num == 1:
            print('\n\n\n')
            print(user_payload)
            print("payload")
            print('\n\n\n')


            resWeather = requests.get("https://www.cwb.gov.tw/V7/forecast/taiwan/Keelung_City.htm")
            resWeather.encoding = 'utf8'

            with open(user_url+r'\GooglemapBot\jsondata\Weather.json', 'r', encoding="utf-8") as f:
                data = json.load(f)

            headers = {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
                "accept-encoding": "gzip, deflate, br",
                "upgrade-insecure-requests": "1",
                "user-agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
            }
            city = ncityba[fbid]
            a = len(data)
            today = time.strftime("%H")

            for i in range(a):
                if data[i]['City']['Zh_tw'] == city:
                    resWeather = requests.get(data[i]['Web'])
                    resWeather.encoding = 'utf8'
                    web = BeautifulSoup(resWeather.text)
                    weather = web.findAll("img")

            # print(web.text,"這是天氣的web")
            if user_payload=="<weather_now>":
                time1 = web.select('table')[0]('th')[5].text
                temperature1 = web.select('table')[0]('td')[0].text#溫度
                weather1 = weather[0].attrs["alt"]#天氣狀況
                comfort1 = web.select('table')[0]('td')[2].text#舒適度
                rain1 = web.select('table')[0]('td')[3].text#降雨機率
                print(time1,'\n\t氣溫：', temperature1+"℃", "\n\t天氣狀況：", weather1, '\n\t舒適度：', comfort1, '\n\t降雨機率：', rain1)
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":city + "的天氣狀況如下:"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":time1 + '\n\t氣溫：' + temperature1 + "℃" + "\n\t天氣狀況：" + weather1 + '\n\t舒適度：' + comfort1 + '\n\t降雨機率：' + rain1}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            elif user_payload =="<weather_tomorrow_day>":
                time2 = web.select('table')[0]('th')[6].text
                temperature2 = web.select('table')[0]('td')[4].text
                weather2 = weather[1].attrs["alt"]
                comfort2 = web.select('table')[0]('td')[6].text
                rain2 = web.select('table')[0]('td')[7].text
                print(time2,'\n\t氣溫：', temperature2+"℃", "\n\t天氣狀況：", weather2, '\n\t舒適度：', comfort2, '\n\t降雨機率：', rain2)
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":city + "的天氣狀況如下:"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":time2 + '\n\t氣溫：' + temperature2 + "℃" + "\n\t天氣狀況：" + weather2 + '\n\t舒適度：' + comfort2 + '\n\t降雨機率：' + rain2}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            elif user_payload=="<weather_tomorrow_night>":
                time3 = web.select('table')[0]('th')[7].text
                temperature3 = web.select('table')[0]('td')[8].text
                weather3 = weather[2].attrs["alt"]
                comfort3 = web.select('table')[0]('td')[10].text
                rain3 = web.select('table')[0]('td')[11].text
                print(time3,'\n\t氣溫：', temperature3+"℃", "\n\t天氣狀況：", weather3, '\n\t舒適度：', comfort3, '\n\t降雨機率：', rain3)
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":city + "的天氣狀況如下:"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":time3 + '\n\t氣溫：' + temperature3 + "℃" + "\n\t天氣狀況：" + weather3 + '\n\t舒適度：' + comfort3 + '\n\t降雨機率：' + rain3}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            else :#確保就算payload怪怪的至少能回答(payload怪怪的話進不去上面的if判斷時間)
                time1 = web.select('table')[0]('th')[5].text
                time2 = web.select('table')[0]('th')[6].text
                time3 = web.select('table')[0]('th')[7].text
                #time4 = time1.split(" ")
                #print(time1)

                #溫度
                temperature1 = web.select('table')[0]('td')[0].text
                temperature2 = web.select('table')[0]('td')[4].text
                temperature3 = web.select('table')[0]('td')[8].text

                #天氣狀況
                #weather1 = web.select('table')[0]('img')[0].text
                #print(weather1)
                #weather1 = weather1.split(" ")

                #舒適度
                comfort1 = web.select('table')[0]('td')[2].text
                comfort2 = web.select('table')[0]('td')[6].text
                comfort3 = web.select('table')[0]('td')[10].text

                #降雨機率
                rain1 = web.select('table')[0]('td')[3].text
                rain2 = web.select('table')[0]('td')[7].text
                rain3 = web.select('table')[0]('td')[11].text
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":city + "的天氣狀況如下:"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":time1 + '\n\t氣溫：' + temperature1 + "℃" + "\n\t天氣狀況：" + weather1 + '\n\t舒適度：' + comfort1 + '\n\t降雨機率：' + rain1}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":time2 + '\n\t氣溫：' + temperature2 + "℃" + "\n\t天氣狀況：" + weather2 + '\n\t舒適度：' + comfort2 + '\n\t降雨機率：' + rain2}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":time3 + '\n\t氣溫：' + temperature3 + "℃" + "\n\t天氣狀況：" + weather3 + '\n\t舒適度：' + comfort3 + '\n\t降雨機率：' + rain3}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

            last_word.update({fbid:idrecevied_message[fbid]})
            anyQuestion(fbid,post_message_url)
            delete_everything(fbid)
            user_payload = ''
            weather_num = 0

            print (nba)
            print("執行完的nba執行完的nba執行完的nba執行完的nba執行完的nba執行完的nba執行完的nba")

def bus(fbid, post_message_url, recevied_message):
    # bus_chinese = "650" #使用者輸入, 284有error
    global wrongcheck,bus_num,bus_chinese,bus_diraction,last_word
    i = 0
    bus_go = ''
    bus_back = ''

    if bus_num == 0:
        if wrongcheck[fbid] == 0:
            bus_chinese = recevied_message

            bus_url = urllib.parse.quote(bus_chinese) #將中文的車碼轉成URL的格式 eg.紅2→%E7%B4%852
            bus_web = "http://pda.5284.com.tw/MQS/businfo2.jsp?routename="+bus_url

            bus_res = requests.get(bus_web)
            bus_res.encoding = "utf8"
            bus_soup = BeautifulSoup(bus_res.text, "lxml")
            print(bus_soup.text)
            print("busbusbusbusbusbus")
            bus_go = bus_soup.find("td","ttegotitle").text

            bus_back = bus_soup.find("td","ttebacktitle").text
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"想知道去程還是回程呢？","quick_replies":[
                {
                     "content_type":"text",
                     "title":bus_go.strip(),
                     "payload":"<bus_go>"
                },
                {
                     "content_type":"text",
                     "title":bus_back.strip(),
                     "payload":"<bus_back>"
                }
                    ]}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

            # bus_chinese = idrecevied_message[fbid]
            # print(bus_chinese)
        elif idrecevied_message[fbid] == "去程" or idrecevied_message[fbid] == "回程" or user_payload == "<bus_go>" or user_payload == "<bus_back>":
            if user_payload == "<bus_go>" or idrecevied_message[fbid] == "去程":
                bus_diraction = "去程"
                bus_num += 1
            elif user_payload == "<bus_back>" or idrecevied_message[fbid] == "回程":
                bus_diraction = "回程"
                bus_num += 1
            else :
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你是不是打錯字了啊？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":bus_go.strip(),
                         "payload":"<bus_go>"
                    },
                    {
                         "content_type":"text",
                         "title":bus_back.strip(),
                         "payload":"<bus_back>"
                    }
                        ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
             #去程(bus_go)或返程(bus_back)，請用quick reply顯示
            
            
            print("有加到喔喔喔喔")
        elif wrongcheck[fbid] >= 1:
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你是不是打錯字了啊？","quick_replies":[
                {
                     "content_type":"text",
                     "title":bus_go.strip(),
                     "payload":"<bus_go>"
                },
                {
                     "content_type":"text",
                     "title":bus_back.strip(),
                     "payload":"<bus_back>"
                }
                    ]}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        
        if fbid in wrongcheck:
            wrongcheck[fbid] += 1

    if bus_num >= 1:
        print("\n\n")
        print(bus_chinese)
        print(bus_diraction)
        print("\n\n")
        bus_url = urllib.parse.quote(bus_chinese) #將中文的車碼轉成URL的格式 eg.紅2→%E7%B4%852
        bus_web = "http://pda.5284.com.tw/MQS/businfo2.jsp?routename="+bus_url

        bus_res = requests.get(bus_web)
        bus_res.encoding = "utf8"
        bus_soup = BeautifulSoup(bus_res.text, "lxml")
        #print(bus_soup)
        print("\n\n\n")
        print(bus_soup.find("td", "ttegotitle"))
        print("bus_soup")
        print("\n\n\n")
        #去程回程資料
        if bus_soup.find("td", "ttegotitle"):
            # bus_go = bus_soup.find("td", "ttegotitle").text
            # bus_back = bus_soup.find("td", "ttebacktitle").text
            #3是去程,4是返程
            if bus_diraction == "去程":
                i = 3 
            elif bus_diraction == "回程":
                i = 4

            #顯示表格data fra
            # pd.read_html(bus_web)[i]
            print(str(pd.read_html(bus_web)[i]))
            # print("trytry")
            # print(read_html(bus_web)[i])
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"下面是公車的時刻表喔！"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":str(pd.read_html(bus_web)[i])}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        else :
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"嗯？你是不是搞錯站名啦？最近有一些公車為了配合政策所以改名囉～\nhttp://www.pto.gov.taipei/News_Content.aspx?n=D065CCB1467288C8&sms=72544237BBE4C5F6&s=897510FCEA8F37DE"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        bus_num = 0
        last_word.update({fbid:idrecevied_message[fbid]})
        recevied_message = " "
        delete_everything(fbid)
        anyQuestion(fbid,post_message_url)

    #pandas.showallword

#取得網頁json
def request(url):
    headers = {'user-agent':'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_3) AppleWebKit/604.5.6 (KHTML, like Gecko) Version/11.0.3 Safari/604.5.6'}
    http = urllib3.PoolManager()
    res = http.request('GET', url, headers = headers)
    res_dict = json.loads(res.data.decode('UTF-8'))
    return res_dict

#ubike函數
def ubike(fbid, post_message_url):

    Ubike_url1 = "http://ptx.transportdata.tw/MOTC/v2/Bike/Station/Taipei?$format=JSON"
    Ubike_data1 = request(Ubike_url1)
    #print(Ubike_data1)
    Ubike_url2 = "http://ptx.transportdata.tw/MOTC/v2/Bike/Availability/Taipei?$format=JSON"
    Ubike_data2 = request(Ubike_url2)
    #print(Ubike_data2)

    global  longlat,toiletlat, toiletlong, wrongcheck, last_word

    if fbid in longlat:
        Ubike_UserPosition_a = longlat[fbid][1]
        Ubike_UserPosition_b = longlat[fbid][0]
        Ubike_Stop2 = []
        Ubike_Address2 = []
        Ubike_Rent2 = []
        Ubike_Return2 = []
        print('站牌 可借車數 可還車數')
        wave(fbid, post_message_url)
        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'站牌　可借車數　可還車數'}})
        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

        for i in range(len(Ubike_data1)):
            if ((Ubike_data1[i]["StationPosition"]["PositionLat"]-Ubike_UserPosition_a)**2+(Ubike_data1[i]["StationPosition"]["PositionLon"]-Ubike_UserPosition_b)**2) < 0.000020295025:    #0.00000901度 = 1公尺
                print(Ubike_data1[i]["StationName"]["Zh_tw"], Ubike_data2[i]['AvailableRentBikes'], Ubike_data2[i]['AvailableReturnBikes'])
                # wave(fbid, post_message_url)
                # response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":str(Ubike_data1[i]["StationName"]["Zh_tw"])+"    "+ str(Ubike_data2[i]['AvailableRentBikes'])+"    "+str(Ubike_data2[i]['AvailableReturnBikes'])}})
                # status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                Ubike_Stop2.append(Ubike_data1[i]["StationName"]["Zh_tw"])
                Ubike_Address2.append(Ubike_data1[i]["StationAddress"]["Zh_tw"]) #地址沒有output
                Ubike_Rent2.append(Ubike_data2[i]["AvailableRentBikes"])
                Ubike_Return2.append(Ubike_data2[i]["AvailableReturnBikes"])

        Ubike_dict2 = {"站牌": Ubike_Stop2, "可借車數": Ubike_Rent2, "可還車數": Ubike_Return2}
        bike_df2 = pd.DataFrame(Ubike_dict2)
        print(bike_df2)
        if len(Ubike_Stop2) == 0:
            print("他找的地方沒ubike")
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'這附近似乎沒有Ubike欸……還是你知道那附近哪裡有Ubike可以跟我說說嗎？',"quick_replies":[
            {
                 "content_type":"text",
                 "title":"是",
                 "payload":"<QA_YES>"
            },
            {
                 "content_type":"text",
                 "title":"下次吧",
                 "payload":"<QA_NO>"
            }
            ]}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

            last_word.update({fbid:idrecevied_message[fbid]})
            toiletlat=''
            toiletlong=''
            delete_everything(fbid)
            anyQuestion(fbid,post_message_url)

        else:
            for bikei in range(len(Ubike_Stop2)):
                print(Ubike_Stop2[bikei], Ubike_Rent2[bikei], Ubike_Return2[bikei], bikei, len(Ubike_Stop2))
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":Ubike_Stop2[bikei] + '    ' + str(Ubike_Rent2[bikei]) + '    ' + str(Ubike_Return2[bikei])}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

            last_word.update({fbid:idrecevied_message[fbid]})
            toiletlat=''
            toiletlong=''
            delete_everything(fbid)
            anyQuestion(fbid,post_message_url)

    elif wrongcheck[fbid] >= 0 :
        wave(fbid, post_message_url)
        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'按下傳送地點，我才會知道在哪裡哦！',"quick_replies":[
        # {
        #     "content_type":"text",
        #     "title":"搜尋",
        #     "payload":"<POSTBACK_PAYLOAD>",
        # },
            {
            "content_type":"location",
            "title":"傳送地點"
            }
        ]}})
        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
        if fbid in wrongcheck:
            wrongcheck[fbid] += 1

#菜單函數
def recipe_query(fbid, post_message_url, restaurant):
    global last_word,idrecevied_message
    with open(user_url+r'\GooglemapBot\jsondata\menu.json', 'r', encoding="utf-8") as f:
        menudata = json.load(f)

    jsonlong = len(menudata)

    storename_final = ''

    restaurant_query = 'q={}'.format(restaurant.replace(' ', '+'))
    query_url = 'https://menubar.tw/search?' + urllib.parse.quote(restaurant_query, safe = string.printable)
    
    storecount = 0
    for i in range(jsonlong):
        menu_string = ''
        if restaurant == menudata[i]['StoreName'] or restaurant == menudata[i]['StoreType']:
            wave(fbid, post_message_url)
            if storecount == 0:
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":menudata[i]['StoreName']+"的菜單是"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            if 'url3' in menudata[i]['Menu'][0]:
                print("有url3有url3有url3有url3有url3有url3有url3")
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":{"type":"image", "payload":{"url":menudata[i]['Menu'][0]['url3']}}}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"},data = response_msg)
            if 'url2' in menudata[i]['Menu'][0]:
                print("有url2有url2有url2有url2有url2有url2有url2")
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":{"type":"image", "payload":{"url":menudata[i]['Menu'][0]['url2']}}}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"},data = response_msg)
            if 'url' in menudata[i]['Menu'][0]:
                print("有url有url有url有url有url有url有url")
                print(menudata[i]['Menu'][0]['url'])
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid}, "message":{"attachment":{"type":"image", "payload":{"url":menudata[i]['Menu'][0]['url']}}}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"},data = response_msg)
            storecount += 1

    if storecount == 0:

        headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7,zh-CN;q=0.6,ja;q=0.5',
            'Connection': 'keep-alive',
            'Cookie': 'connect.sid=s%3A7DMyh3BHjlt-NyrewTnZSYKQX7nA40Bp.kGy3QL9WN1h0aNdh95jenBbLDM6YmUg8l6h9ZlchP7g; _ga=GA1.2.2000943914.1524469648; _gid=GA1.2.1645056648.1524469648',
            'Host': 'menubar.tw',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }

        origin_res = requests.get(query_url, headers = headers)
        origin_soup = BeautifulSoup(origin_res.text, 'html.parser')


        if restaurant in origin_soup.select('div.card-body')[1].select('h4')[0].select('a')[0].select('span')[0].text and restaurant != "三餐" and  restaurant != "一餐" and origin_soup.select('li.breadcrumb-item.active')[0].select('b')[0].text != str(0):
            print(origin_soup.select('div.card-body')[1].select('h4')[0].select('a')[0].select('span')[0].text)
            links =  [a.attrs.get('href') for a in origin_soup.select('div.card-body')[1].select('h4')[0].select('a')]

            menu_links = 'https://menubar.tw' + str(links).strip("'[]'")

            print(menu_links)

            res = requests.get(menu_links, headers = headers)
            soup = BeautifulSoup(res.text, 'html.parser')

            name = []
            price = []
            td_count = 1
            for i in soup.select('table')[1].select('tr'):
                if i.select('td') != '': 
                    for k in i.select('td'):
                        if td_count%2 ==1:
                            name.append(k.text.strip(" \n"))
                        else:
                            price.append(k.text.strip(" \n"))
                        td_count +=1

            menu_dict = { "name": name, "price & note" : price}
            menu_query_df =  pd.DataFrame(menu_dict, columns=['name', 'price & note'])
    
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"下面是"+restaurant+"的菜單喔～"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":menu_links}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":str(menu_query_df)}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            if fbid in idrecevied_message:
                last_word.update({fbid:idrecevied_message[fbid]})
            anyQuestion(fbid, post_message_url)
            delete_everything(fbid)
        else :
            warntext = "沒有結果喔"
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":'我還不知道這家店欸……還是你可以告訴人家更多資訊呢(∩´﹏`∩)？',"quick_replies":[
            {
                 "content_type":"text",
                 "title":"是",
                 "payload":"<QA_YES>"
            },
            {
                 "content_type":"text",
                 "title":"下次吧",
                 "payload":"<QA_NO>"
            }
            ]}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            if fbid in idrecevied_message:
                last_word.update({fbid:idrecevied_message[fbid]})
            anyQuestion(fbid, post_message_url)
            delete_everything(fbid)

    else:
        if fbid in idrecevied_message:
            last_word.update({fbid:idrecevied_message[fbid]})
        anyQuestion(fbid, post_message_url)
        delete_everything(fbid)
        # return menu_json_df

#北捷函數
def peijie(fbid, post_message_url, recevied_message):

    global user_payload, check_peijietime, user_url, jj, Departure, MRT_direction, last_word

    with open(user_url+r'\GooglemapBot\jsondata\MRT_ID.json', "r", encoding="utf-8") as g: #encoding="utf-8"
        MRT_ID = json.load(g)

    all_peijie = ["南港軟體園區","東湖","葫洲","大湖公園","內湖","文德","港墘","西湖","劍南路","大直","松山機場","中山國中","科技大樓","六張犁","麟光","辛亥","萬芳醫院","萬芳社區","木柵","動物園",
                  "頂埔","永寧","土城","海山","亞東醫院","府中","板橋","新埔","江子翠","龍山寺","西門","台北車站","北車","善導寺","忠孝新生","忠孝復興","忠孝敦化","國父紀念館","市政府","永春","後山埤","昆陽","南港","南港展覽館",
                  "新店","新店區公所","七張","大坪林","景美","萬隆","公館","台電大樓","中正紀念堂","小南門","北門","松江南京","南京復興","台北小巨蛋","南京三民","松山",
                  "南勢角","景安","永安市場","頂溪","古亭","東門","行天宮","中山國小","民權西路","大橋頭","台北橋","菜寮","三重","先嗇宮","頭前庄","新莊","輔大","丹鳳","迴龍","三重國小","三和國中","徐匯中學","三民高中","蘆洲",
                  "象山","台北101","世貿","信義安和","大安","大安森林公園","東門","中正紀念堂","台大醫院","中山","雙連","民權西路","圓山","劍潭","士林","芝山","明德","石牌","唭哩岸","奇岸","北投","復興崗","忠義","關渡","竹圍","紅樹林","淡水"]

    MRT_BR = ["南港軟體園區","東湖","葫洲","大湖公園","內湖","文德","港墘","西湖","劍南路","大直","松山機場","中山國中","科技大樓","六張犁","麟光","辛亥","萬芳醫院","萬芳社區","木柵","動物園"]
    MRT_BL = ["頂埔","永寧","土城","海山","亞東醫院","府中","板橋","新埔","江子翠","龍山寺","西門","台北車站","善導寺","忠孝新生","忠孝復興","忠孝敦化","國父紀念館","市政府","永春","後山埤","昆陽","南港","南港展覽館"]
    MRT_G = ["新店","新店區公所","七張","大坪林","景美","萬隆","公館","台電大樓","古亭","中正紀念堂","小南門","西門","北門","中山","松江南京","南京復興","台北小巨蛋","南京三民","松山"]
    MRT_O = ["南勢角","景安","永安市場","頂溪","古亭","東門","忠孝新生","松江南京","行天宮","中山國小","民權西路","大橋頭","台北橋","菜寮","三重","先嗇宮","頭前庄","新莊","輔大","丹鳳","迴龍","三重國小","三和國中","徐匯中學","三民高中","蘆洲"]
    MRT_R = ["象山","台北101/世貿","信義安和","大安","大安森林公園","東門","中正紀念堂","台大醫院","台北車站","中山","雙連","民權西路","圓山","劍潭","士林","芝山","明德","石牌","唭哩岸","奇岸","北投","復興崗","忠義","關渡","竹圍","紅樹林","淡水"]

    MRT_list1 = []
    MRT_list2 = []
    MRT_df = []
    MRT_DepartureID = ''
    MRT_Finish = ''

    # MRT_Departure = changeword(MRT_Departure, 1)
    
    if jj[fbid] == 0:
        Departure = changeword(recevied_message, 1)
        if Departure == '台北':
            Departure += '車站'
        if Departure == '北車':
            Departure = '台北車站'
        print(Departure)
        print("changeword下changeword下changeword下changeword下changeword下")
        if Departure in all_peijie:
            print("rup4x96xk77777777777777777777777777777777")
            if Departure  == '台北車站':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"北車真得是一個巨型迷宮呢！話又說回來，你是要搭哪個方向的車呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往南港展覽館站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往頂埔站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往淡水站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往象山站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj[fbid] += 1
            elif Departure  == '南港展覽館':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭板南線還是文湖線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往頂埔站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往動物園站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj[fbid] += 1
            elif Departure  == '中正紀念堂':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭綠線還是紅線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往松山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往新店站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往淡水站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往象山站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj[fbid] += 1
            elif Departure  == '古亭':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭綠線還是黃線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往松山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往新店站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往蘆洲站、迴龍站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南勢角站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj[fbid] += 1
            elif Departure  == '西門':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"西門是一個適合約會的地方喔！你可不要誤會！我才沒有在暗指什麼喔！快跟我說你要搭哪個方向的車啦！","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往松山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往新店站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南港展覽館站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往頂埔站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj[fbid] += 1
            elif Departure  == '民權西路':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭紅線還是黃線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往淡水站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往象山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往蘆洲站、迴龍站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南勢角站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj[fbid] += 1
            elif Departure  == '松江南京':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭綠線還是黃線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往松山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往新店站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往蘆洲站、迴龍站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南勢角站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj[fbid] += 1
            elif Departure  == '忠孝新生':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭藍線還是黃線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往南港展覽館站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往頂埔站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往蘆洲站、迴龍站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南勢角站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj[fbid] += 1
            elif Departure  == '東門':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭紅線還是黃線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往淡水站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往象山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往蘆洲站、迴龍站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南勢角站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj[fbid] += 1
            elif Departure  == '中山':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭綠線還是紅線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往松山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往新店站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往淡水站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往象山站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj[fbid] += 1
            elif Departure  == '南京復興':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭綠線還是棕線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往松山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往新店站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南港展覽館站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往動物園站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj[fbid] += 1
            elif Departure  == '忠孝復興':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭板南線還是文湖線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往頂埔站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南港展覽館站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往動物園站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj[fbid] += 1
            elif Departure  == '大安':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要往紅線還是棕線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往淡水站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往象山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南港展覽館站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往動物園站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj[fbid] += 1
            elif Departure in MRT_BL:
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"東區有很多很酷的店呢！話說你要搭乘哪個方向的車呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往南港展覽館站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往頂埔站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj[fbid] += 1
            elif Departure in MRT_G:
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"松山下車的話就可以去彩虹橋散步喔！話說你要搭乘哪個方向的車呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往松山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往新店站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj[fbid] += 1
            elif Departure in MRT_O:
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"三和夜市很熱鬧喔，下次可以一起去逛逛喔！話說你要搭乘哪個方向的車呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往蘆洲站、迴龍站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南勢角站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj[fbid] += 1
            elif Departure in MRT_R:
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"聽說象山在五月有螢火蟲出沒喔！話說你要搭乘哪個方向的車呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往淡水站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往象山站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj[fbid] += 1
            #文湖線無時刻表
            elif Departure in MRT_BR:
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"文湖線是無人自動駕駛系統，班次密集且會依狀況加發列車，所以沒有時刻表喔！"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                anyQuestion(fbid,post_message_url)
                jj[fbid] += 1
        elif Departure not in all_peijie and jj[fbid] == 0:
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"我好像沒聽過這個捷運站欸，要不要換個說法看看呢？"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
    elif jj[fbid] == 1:
        MRT_Departure = Departure
        MRT_direction.update({fbid:recevied_message})
    else:
        MRT_Departure = Departure

    print(user_payload)
    print("上面是userpayload上面是userpayload上面是userpayload上面是userpayload上面是userpayload上面是userpayload")
    if fbid in MRT_direction:
        if check_peijietime >= 1:
            MRT_Time = changeword(recevied_message, 1)
            print(MRT_Time, "changeword過後的mrt time")

            #時間打錯
            if ("01" in MRT_Time) or ("02" in MRT_Time) or ("03" in MRT_Time) or ("04" in MRT_Time) or ("05" in MRT_Time):
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"捷運的發車時間為早上六點至晚上十二點，所以這個時間捷運已經沒有營業了喔！"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                MRT_Finish = "N"
            elif "06" not in MRT_Time and "07" not in MRT_Time and "08" not in MRT_Time and "09" not in MRT_Time and "10" not in MRT_Time and "11" not in MRT_Time and "12" not in MRT_Time and "13" not in MRT_Time and "14" not in MRT_Time and "15" not in MRT_Time and "16" not in MRT_Time and "17" not in MRT_Time and "18" not in MRT_Time and "19" not in MRT_Time and "20" not in MRT_Time and "21" not in MRT_Time and "22" not in MRT_Time and "23" not in MRT_Time and "00" not in MRT_Time:
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你說的時間好像不存在吧？"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                MRT_Finish = "N"
            else:
                if "06" in MRT_Time:
                    MRT_Time = "06"
                if "07" in MRT_Time:
                    MRT_Time = "07"
                if "08" in MRT_Time:
                    MRT_Time = "08"
                if "09" in MRT_Time:
                    MRT_Time = "09"
                if "10" in MRT_Time:
                    MRT_Time = "10"
                if "11" in MRT_Time:
                    MRT_Time = "11"
                if "12" in MRT_Time:
                    MRT_Time = "12"
                if "13" in MRT_Time:
                    MRT_Time = "13"
                if "14" in MRT_Time:
                    MRT_Time = "14"
                if "15" in MRT_Time:
                    MRT_Time = "15"
                if "16" in MRT_Time:
                    MRT_Time = "16"
                if "17" in MRT_Time:
                    MRT_Time = "17"
                if "18" in MRT_Time:
                    MRT_Time = "18"
                if "19" in MRT_Time:
                    MRT_Time = "19"
                if "20" in MRT_Time:
                    MRT_Time = "20"
                if "21" in MRT_Time:
                    MRT_Time = "21"
                if "22" in MRT_Time:
                    MRT_Time = "22"
                if "23" in MRT_Time:
                    MRT_Time = "23"
                if "00" in MRT_Time:
                    MRT_Time = "00"

                print(MRT_Time)
                print(MRT_Finish) 
                print(MRT_direction)
                print(MRT_Departure)
                print("MRT所有資料MRT所有資料MRT所有資料MRT所有資料MRT所有資料MRT所有資料MRT所有資料") 
                #處理json檔名問題（雙線車站需特別處理）
                for i in range(len(MRT_ID)): #len(MRT_ID)=95
                    if MRT_ID[i]["Name"] == MRT_Departure:
                        if MRT_ID[i]["Over"] == "Y": #判斷是否為雙線車站(共十二站是)
                            if ((MRT_direction[fbid] == MRT_ID[i]["Dic"][0]["Dic1"]) or (MRT_direction[fbid] == MRT_ID[i]["Dic"][0]["Dic2"])):
                                MRT_DepartureID = user_url+r'\\GooglemapBot\\jsondata\\MRT\\'+MRT_ID[i]["ID"]+'.json'
                        else:
                            MRT_DepartureID = user_url+r'\\GooglemapBot\\jsondata\\MRT\\'+MRT_ID[i]["ID"]+'.json'
                print(MRT_DepartureID)
                print("上面是MRTdepartureid上面是MRTdepartureid上面是MRTdepartureid上面是MRTdepartureid上面是MRTdepartureid")

                if MRT_DepartureID != '':
                    with open(MRT_DepartureID, "r", encoding="utf-8") as g2: #encoding="utf-8"
                        MRT_Data = json.load(g2)

                    for j in range(len(MRT_Data["Timetables"])):
                        if MRT_Data["Timetables"][j]["Direction"] == MRT_direction[fbid]:
                            for k in range(len(MRT_Data["Timetables"][j]["Schedule"][0]["Departures"])):
                                MRT_m = MRT_Data["Timetables"][j]["Schedule"][0]["Departures"][k]["Time"].find(MRT_Time)
                                if 2 > MRT_m >= 0:
                                    MRT_list1.append(MRT_Data["Timetables"][j]["Schedule"][0]["Departures"][k]["Time"])
                                    MRT_list2.append("往"+MRT_Data["Timetables"][j]["Schedule"][0]["Departures"][k]["Dst"])
                                    MRT_Finish = "Y"
                      
                    if MRT_Finish == "Y":
                    #建立 data frame
                        MRT_dict = {"時間":MRT_list1, "方向":MRT_list2}
                        MRT_df = pd.DataFrame(MRT_dict, columns = ["時間", "方向"])

                        print(MRT_df)
                        wave(fbid, post_message_url)
                        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":str(MRT_df)}})
                        status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                        check_peijietime = 0
                        anyQuestion(fbid,post_message_url)
                        last_word.update({fbid:idrecevied_message[fbid]})
                        delete_everything(fbid)
                        if fbid in idcheck:
                            del idcheck[fbid]
                        if fbid in MRT_direction:
                            del MRT_direction[fbid]
                        if fbid in jj:
                            del jj[fbid]
                else:
                    response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"我好像好像有點頭昏了，可以請你再從新問一次嗎？(∩´﹏`∩)"}})
                    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                    check_peijietime = 0
                    anyQuestion(fbid,post_message_url)
                    last_word.update({fbid:idrecevied_message[fbid]})
                    if fbid in idcheck:
                        del idcheck[fbid]
                    if fbid in MRT_direction:
                        del MRT_direction[fbid]
                    if fbid in jj:
                        del jj[fbid]


        elif MRT_direction[fbid] == "往南港展覽館站" or MRT_direction[fbid] == "往頂埔站" or MRT_direction[fbid] == "往松山站" or MRT_direction[fbid] == "往新店站" or MRT_direction[fbid] == "往蘆洲站、迴龍站" or MRT_direction[fbid] == "往南勢角站" or MRT_direction[fbid] == "往淡水站" or MRT_direction[fbid] == "往象山站":
            print("進userpayload進userpayload進userpayload進userpayload進userpayload進userpayload")
            
            #南港展覽館、南京復興、忠孝復興和大安因為雙線車站，故需做雙重判斷
            if (((MRT_Departure == "南港展覽館") and (MRT_direction[fbid] == "往動物園站")) or ((MRT_Departure == "南京復興") and (MRT_direction[fbid] == "往南港展覽館站")) or ((MRT_Departure == "南京復興") and (MRT_direction[fbid] == "往動物園站")) or ((MRT_Departure == "忠孝復興") and (MRT_direction[fbid] == "往動物園站")) or ((MRT_Departure == "大安") and (MRT_direction[fbid] == "往南港展覽館站")) or ((MRT_Departure == "大安") and (MRT_direction[fbid] == "往動物園站"))):
                print("文湖線是無人自動駕駛系統，班次密集且會依狀況加發列車，所以沒有時刻表喔！")
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"文湖線是無人自動駕駛系統，班次密集且會依狀況加發列車，所以沒有時刻表喔！"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

                
            #忠孝復興往南港展覽館有兩條路線，故須和使用者做確認
            if MRT_Departure == "忠孝復興" and (MRT_direction[fbid] == "往南港展覽館站"):
                print("以下為板南線的時刻表；至於文湖線，因為它是無人自動駕駛系統，班次密集且會依狀況加發列車，所以沒有時刻表喔！")
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下為板南線的時刻表；至於文湖線，因為它是無人自動駕駛系統，班次密集且會依狀況加發列車，所以沒有時刻表喔！"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你想知道大約幾點的車呢？"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            check_peijietime += 1
            jj[fbid] += 1
        elif MRT_direction[fbid] != "往南港展覽館站" and MRT_direction[fbid] != "往頂埔站" and MRT_direction[fbid] != "往松山站" and MRT_direction[fbid] != "往新店站" and MRT_direction[fbid] != "往蘆洲站、迴龍站" and MRT_direction[fbid] != "往南勢角站" and MRT_direction[fbid] != "往淡水站" and MRT_direction[fbid] != "往象山站" and MRT_direction[fbid] != "往動物園站" and check_peijietime == 0:
            wave(fbid, post_message_url)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"好像沒這個方向吧？"}})
            status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
            if MRT_Departure  == '台北車站':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"所以你是要搭哪個方向的車呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往南港展覽館站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往頂埔站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往淡水站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往象山站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj.update({fbid:1})
            elif MRT_Departure  == '南港展覽館':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭板南線還是文湖線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往頂埔站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往動物園站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj.update({fbid:1})
            elif MRT_Departure  == '中正紀念堂':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭綠線還是紅線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往松山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往新店站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往淡水站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往象山站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj.update({fbid:1})
            elif MRT_Departure  == '古亭':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭綠線還是黃線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往松山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往新店站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往蘆洲站、迴龍站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南勢角站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj.update({fbid:1})
            elif MRT_Departure  == '西門':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"所以你是要搭哪個方向的車呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往松山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往新店站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南港展覽館站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往頂埔站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj.update({fbid:1})
            elif MRT_Departure  == '民權西路':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭紅線還是黃線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往淡水站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往象山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往蘆洲站、迴龍站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南勢角站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj.update({fbid:1})
            elif MRT_Departure  == '松江南京':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭綠線還是黃線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往松山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往新店站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往蘆洲站、迴龍站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南勢角站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj.update({fbid:1})
            elif MRT_Departure  == '忠孝新生':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭藍線還是黃線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往南港展覽館站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往頂埔站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往蘆洲站、迴龍站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南勢角站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj.update({fbid:1})
            elif MRT_Departure  == '東門':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭紅線還是黃線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往淡水站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往象山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往蘆洲站、迴龍站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南勢角站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj.update({fbid:1})
            elif MRT_Departure  == '中山':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭綠線還是紅線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往松山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往新店站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往淡水站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往象山站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj.update({fbid:1})
            elif MRT_Departure  == '南京復興':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭綠線還是棕線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往松山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往新店站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南港展覽館站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往動物園站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj.update({fbid:1})
            elif MRT_Departure  == '忠孝復興':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要搭板南線還是文湖線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往頂埔站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南港展覽館站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往動物園站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj.update({fbid:1})
            elif MRT_Departure  == '大安':
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"你要往紅線還是棕線呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往淡水站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往象山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南港展覽館站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往動物園站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj.update({fbid:1})
            elif MRT_Departure in MRT_BL:
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"所以你是要搭哪個方向的車呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往南港展覽館站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往頂埔站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj.update({fbid:1})
            elif MRT_Departure in MRT_G:
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"所以你是要搭哪個方向的車呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往松山站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往新店站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj.update({fbid:1})
            elif MRT_Departure in MRT_O:
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"所以你是要搭哪個方向的車呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往蘆洲站、迴龍站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往南勢角站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj.update({fbid:1})
            elif MRT_Departure in MRT_R:
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"所以你是要搭哪個方向的車呢？","quick_replies":[
                    {
                         "content_type":"text",
                         "title":"往淡水站",
                         "payload":"<GET_DIRECTION>"
                    },
                    {
                         "content_type":"text",
                         "title":"往象山站",
                         "payload":"<GET_DIRECTION>"
                    }
                    ]}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                jj.update({fbid:1})
            #文湖線無時刻表
            elif MRT_Departure in MRT_BR:
                wave(fbid, post_message_url)
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"文湖線是無人自動駕駛系統，班次密集且會依狀況加發列車，所以沒有時刻表喔！"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
                anyQuestion(fbid,post_message_url)
                jj.update({fbid:1})
            else:
                response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"我看不懂這個站欸，可以換個說法嗎?"}})
                status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

def wave(fbid, post_message_url):
    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"mark_seen"})
    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)
    response_msg = json.dumps({"recipient":{"id":fbid},"sender_action":"typing_on"})
    status = requests.post(post_message_url, headers = {"Content-Type": "application/json"}, data = response_msg)

def delete_everything(fbid):
    global idcheck, idrecevied_message, nba, ncityba, wrongcheck, seq_check2, seq_check4 ,longlat

    if fbid in idcheck:
        del idcheck[fbid]
    if fbid in idrecevied_message:
        del idrecevied_message[fbid]
    if fbid in nba:
        del nba[fbid]
    if fbid in ncityba:
        del ncityba[fbid]
    if fbid in wrongcheck:
        del wrongcheck[fbid]
    if fbid in seq_check2:
        del seq_check2[fbid]
    if fbid in seq_check4:
        del seq_check4[fbid]
    if fbid in longlat:
        del longlat[fbid]

    print (idcheck, "這是執行完刪掉後的idcheck")
    print (idrecevied_message, "這是執行完刪掉後的idrecevied_message")
    print (nba, "這是執行完刪掉後的nba")
    print (ncityba, "這是執行完刪掉後的ncityba")
    print (wrongcheck, "這是執行完刪掉後的wrongcheck")
    print (seq_check2, "這是執行完刪掉後的seq_check2")
    print (seq_check4, "這是執行完刪掉後的seq_check4")
    print (longlat, "這是執行完刪掉後的longlat")

