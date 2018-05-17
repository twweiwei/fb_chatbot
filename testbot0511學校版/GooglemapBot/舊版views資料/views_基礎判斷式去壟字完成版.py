# yomamabot/fb_yomamabot/views.py
import json, requests, random, re
from pprint import pprint
import os

from django.views import generic
from django.http.response import HttpResponse

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
from hanziconv import HanziConv
from django.conf import settings
from fb_Chatbot.googlemap.mapAPI import G_center, G_zoom, request87
#  ------------------------ Fill this with your page access token! -------------------------------
PAGE_ACCESS_TOKEN = "EAAEQtzvtPZCYBALeH5PVSZA8EZBgkoOmvDZCXY1ft7S7jZB3hOeEnOzNAFkYtYgVtFxXtqwjVphpcZAXFTyXaBlzp739myROFJpGS6b4SoHiUn4UAoWbUK79bqy5MoWjxpCgf6UHRtj6ZB0Y1aO6jZC6ZBiBkUZA4B0yUROJEqLVWaVQZDZD"
VERIFY_TOKEN = "20171013" 
# list1 = ['地址','位置','哪','去']
# listtoolong = ['你','我','他','想','的','要']
# listtoolong_find = 0
# listlocation_find =0
dict={'location':["去","往哪","哪","位置","地址","地點","方向","怎麼走","走"],
    'toilet':["廁所","尿","大便","拉屎","屎","撇條","排遺","排泄","便便","便所","化妝室","洗手間"],
    "toolong":["你","我","他","想","要","請問","的","是","有","嗎","在","裡","怎麼","如何","沒有","哩","勒","呢","啊","能","很","真","可以","方式","資訊","不","給","甚麼","什麼","那","多少"],
    "營業時間":["營業時間","幾點關門","幾點","入場","關門","時間","開始","開放","幾號"],
    "電話":["電話","專線","號碼","連絡","聯絡"],
    "介紹":["簡介","特色","高度","長度","多高","多長","歷史","介紹","內容","文化","活動","官網","網站","資訊","限時","外送","附近"],
    "價錢":["價格","票價","多少錢","錢","貴","便宜","花費","費用","花"],
    "wifi":["wifi","WIFI","網路","上網","無線"],
    "菜單":["菜單","餐點","低消","飲料","葷","素","蛋奶素","食物"],
    "評價":["評價","好吃","好玩","有趣"],
    "充電":["插座","充電","電源","電","手機"],
    "乘車":["搭乘","搭","車子","公車","捷運","站","到","多久","多少時間"]}
a=0
a2=0
a3=0
a4=0
a5=0
a6=0
a7=0
a8=0
a9=0
a10=0
a11=0
chr=0
toolong=0
a=len(dict["toilet"])
a2=len(dict["location"])
a3=len(dict["營業時間"])
a4=len(dict["電話"])
a5=len(dict["介紹"])
a6=len(dict["wifi"])
a7=len(dict["菜單"])
a8=len(dict["評價"])
a9=len(dict["充電"])
a10=len(dict["乘車"])
a11=len(dict["價錢"])
toolong=len(dict["toolong"])
# def Profile_facebook_message(fbid):
#     user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid 
#     user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':PAGE_ACCESS_TOKEN} 
#     user_details = requests.get(user_details_url, user_details_params).json() 
#     profile_message_url="https://graph.facebook.com/v2.6/me/messenger_profile?access_token=%s"%PAGE_ACCESS_TOKEN
#     getstart_msg = json.dumps({
#     "get_started":{
#     "payload":"<GET_STARTED_PAYLOAD>"
#         },
#         "message":{"text":"hellow"}
#     })
#     status = requests.post(profile_message_url, headers={"Content-Type": "application/json"},data=getstart_msg)

def post_facebook_image(fbid):
    G_center
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    response_msg = json.dumps({
        "recipient":{"id":fbid},
        "message":{
        "attachment":{
        "type":"image","payload":{"url":request87}}}})
    status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    # pprint(status.json())
# Helper function
def post_facebook_message(fbid, recevied_message):
    jerry = ChatBot("jerry",storage_adapter="chatterbot.storage.SQLStorageAdapter",database=os.path.join(settings.BASE_DIR,'fb_Chatbot/chat/test'))
    jerry.set_trainer(ChatterBotCorpusTrainer)
    jerry.train("C:\\Users\\MA303\\Desktop\\Chatbot\\fb_Chatbot\\chat\\jerry_DB.json") 
    # C:\Users\MA303\Desktop\Chatbot\fb_Chatbot\chat
    tokens = re.sub(r"[^a-zA-Z0-9\s]",' ',recevied_message).lower().split()
    joke_text = ''
    # print (recevied_message)
    # print (type (recevied_message))
    # print (tokens)
    # print (type (tokens))
    y = jerry.get_response(recevied_message)
    y = HanziConv.toTraditional(y.text)
    print(y)
    joke_text = y
    user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid 
    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':PAGE_ACCESS_TOKEN} 
    user_details = requests.get(user_details_url, user_details_params).json() 
    joke_text = 'Yo ..! ' + joke_text
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=%s'%PAGE_ACCESS_TOKEN
    # global listlocation_find
    # global listtoolong_find
    # global list1
    # global listtoolong
    # for i in range(4):
    #     print (listlocation_find)
    #     listlocation_find = recevied_message.find(list1[i])
    #     print("after==")
    #     print (listlocation_find)
    #     if listlocation_find >= 0 :
    #         for r in range(5):
    #             listtoolong_find = recevied_message.find(listtoolong[r])
    #             if listtoolong_find >= 0:
    #                 l = listtoolong_find +1
    #                 recevied_message = recevied_message[:listtoolong_find] + recevied_message[l:]
    #                 print(recevied_message)
    #         response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"https://www.google.com.tw/maps/search/"+recevied_message,}})
    #         status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    #         pprint(status.json())
    str=recevied_message
    ans=0
    for h in range(toolong):
        if str.find(dict["toolong"][h])>=0 :
            dle = str.find(dict["toolong"][h])
            dle_long=len(dict["toolong"][h])
            dle2=dle+dle_long
            str=str[:dle]+str[dle2:]
    for i in range(a):
        if str.find(dict["toilet"][i])>=0 and ans<=0:
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"您附近的廁所有以下這些"}})
            status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
            ans=ans+1
    for i10 in range(a10):
        if str.find(dict["乘車"][i10])>=0 and ans<=0:
            dle = str.find(dict["乘車"][i10])
            dle_long=len(dict["乘車"][i10])
            dle2=dle+dle_long
            str=str[:dle]+str[dle2:]
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是"+str+"的交通資訊"}})
            status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
            ans=ans+1
    for i11 in range(a11):
        if str.find(dict["價錢"][i11])>=0 and ans<=0:
            dle = str.find(dict["價錢"][i11])
            dle_long=len(dict["價錢"][i11])
            dle2=dle+dle_long
            str=str[:dle]+str[dle2:]
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是"+str+"的價錢資訊"}})
            status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
            ans=ans+1
    for i2 in range(a2):
        if str.find(dict["location"][i2])>=0 and ans<=0:
            dle = str.find(dict["location"][i2])
            dle_long=len(dict["location"][i2])
            dle2=dle+dle_long
            str=str[:dle]+str[dle2:]
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是"+str+"的位置資訊"}})
            status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
            print("https://www.google.com.tw/maps/search/"+str)
            ans=ans+1
    for i3 in range(a3):
        if str.find(dict["營業時間"][i3])>=0 and ans<=0:
            dle = str.find(dict["營業時間"][i3])
            dle_long=len(dict["營業時間"][i3])
            dle2=dle+dle_long
            str=str[:dle]+str[dle2:]
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":str+"的營業時間是"}})
            status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
            ans=ans+1
    for i4 in range(a4):
        if str.find(dict["電話"][i4])>=0 and ans<=0:
            dle = str.find(dict["電話"][i4])
            dle_long=len(dict["電話"][i4])
            dle2=dle+dle_long
            str=str[:dle]+str[dle2:]
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":str+"的電話是"}})
            status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
            ans=ans+1
    for i5 in range(a5):
        if str.find(dict["介紹"][i5])>=0 and ans<=0:
            dle = str.find(dict["介紹"][i5])
            dle_long=len(dict["介紹"][i5])
            dle2=dle+dle_long
            str=str[:dle]+str[dle2:]
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是"+str+"的相關資訊"}})
            status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
            ans=ans+1
    for i6 in range(a6):
        if str.find(dict["wifi"][i6])>=0 and ans<=0:
            dle = str.find(dict["wifi"][i6])
            dle_long=len(dict["wifi"][i6])
            dle2=dle+dle_long
            str=str[:dle]+str[dle2:]
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是"+str+"的wifi資訊"}})
            status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
            ans=ans+1
            
    for i7 in range(a7):
        if str.find(dict["菜單"][i7])>=0 and ans<=0:
            dle = str.find(dict["菜單"][i7])
            dle_long=len(dict["菜單"][i7])
            dle2=dle+dle_long
            str=str[:dle]+str[dle2:]
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是"+str+"的菜單資訊"}})
            status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
            ans=ans+1
    for i8 in range(a8):
        if str.find(dict["評價"][i8])>=0 and ans<=0:
            dle = str.find(dict["評價"][i8])
            dle_long=len(dict["評價"][i8])
            dle2=dle+dle_long
            str=str[:dle]+str[dle2:]
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是"+str+"的評價資訊"}})
            status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
            ans=ans+1
    for i9 in range(a9):
        if str.find(dict["充電"][i9])>=0 and ans<=0:
            dle = str.find(dict["充電"][i9])
            dle_long=len(dict["充電"][i9])
            dle2=dle+dle_long
            str=str[:dle]+str[dle2:]
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是充電資訊"}})
            status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
            ans=ans+1

            
    print(str)
    if recevied_message=="查詢google圖片"and ans<=0:
        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是您搜尋的地點"}})
        status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
        post_facebook_image(fbid)
        ans=ans+1
    # if recevied_message == "旅遊" and ans<=0:
    #     response_msg = json.dumps({"recipient":{"id":fbid},"message":{
    #         "text":"旅遊選擇如下",
    #         "quick_replies":[
    #             {
    #                 "content_type":"text",
    #                 "title":"台北",
    #                 "payload":"<PICK_TPE>"
    #             },
    #             {
    #                 "content_type":"text",
    #                 "title":"宜蘭",
    #                 "payload":"<PICK_IL>"
    #             },
    #             {
    #                 "content_type":"location"
    #             }
                
    #             ]}})
    #     status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
    #     pprint(status.json())
    #     ans=ans+1
    if ans<=0:
        response_msg = json.dumps({"recipient":{"id":fbid}, "message":{
        "text":joke_text,}})
        status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
        pprint(status.json())

# Create your views here.
class ChatbotView(generic.View):
    def get(self, request, *args, **kwargs):
        if self.request.GET['hub.verify_token'] == VERIFY_TOKEN:
            return HttpResponse(self.request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')
        
    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    # Post function to handle Facebook messages
    def post(self, request, *args, **kwargs):
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        faketext="你好"
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        # print(incoming_message)
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events 
                if 'message' in message:
                    # Print the message to the terminal
                    # pprint(message)    
                    # Assuming the sender only sends text. Non-text messages like stickers, audio, pictures
                    # are sent as attachments and must be handled accordingly. 
                    if 'text' in message['message']:
                        post_facebook_message(message['sender']['id'], message['message']['text'])
                    else:
                        print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
                        pass

        return HttpResponse()    

                      