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
list1 = ['地址','位置','哪','去']
listtoolong = ['你','我','他','想','的','要']
listtoolong_find = 0
listlocation_find =0

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
    jerry.train("C:\\Users\\MA303\Desktop\\Chatbot\\fb_Chatbot\\chat\\jerry_DB.json") 
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
    global listlocation_find
    global listtoolong_find
    global list1
    global listtoolong
    for i in range(4):
        print (listlocation_find)
        listlocation_find = recevied_message.find(list1[i])
        print("after==")
        print (listlocation_find)
        if listlocation_find >= 0 :
            for r in range(5):
                listtoolong_find = recevied_message.find(listtoolong[r])
                if listtoolong_find >= 0:
                    l = listtoolong_find +1
                    recevied_message = recevied_message[:listtoolong_find] + recevied_message[l:]
                    print(recevied_message)
            response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"https://www.google.com.tw/maps/search/"+recevied_message,}})
            status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
            pprint(status.json())
    if recevied_message=="查詢google圖片":
        response_msg = json.dumps({"recipient":{"id":fbid},"message":{"text":"以下是您搜尋的地點"}})
        status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
        post_facebook_image(fbid)
    if recevied_message == "旅遊" :
        response_msg = json.dumps({"recipient":{"id":fbid},"message":{
            "text":"旅遊選擇如下",
            "quick_replies":[
                {
                    "content_type":"text",
                    "title":"台北",
                    "payload":"<PICK_TPE>"
                },
                {
                    "content_type":"text",
                    "title":"宜蘭",
                    "payload":"<PICK_IL>"
                },
                {
                    "content_type":"location"
                }
                
                ]}})
        status = requests.post(post_message_url, headers={"Content-Type": "application/json"},data=response_msg)
        pprint(status.json())
    else :
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
                    post_facebook_message(message['sender']['id'], message['message']['text'])

        return HttpResponse()    

                      