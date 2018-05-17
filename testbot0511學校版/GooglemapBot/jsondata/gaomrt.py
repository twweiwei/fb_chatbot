#1 高雄捷運

import json
import time
with open('MRT_Kaohsiung.json', 'r', encoding="utf-8") as f:
    data = json.load(f)

mylocation = '西子灣' #使用者的input，即使用者的現在捷運站位置
mydirection = '大寮' #使用者的input，即使用者欲抵達的捷運站位置；若mylocation為橘線只能輸入'西子灣'或'大寮'，為紅線則只能輸入'南崗山'或'小港'，但'美麗島'是四種都能輸入
mytime = '07' #使用者的input，即使用者欲搭車的時間；需輸入整點
today = time.strftime("%A") #抓使用者的現在時間(星期)
#print(today)

a = len(data) #計算整個json檔有幾筆資料，一站有六筆資料, 共38站；a=228(38*6)
#print(a)

print('以下為往【'+mydirection+'】方向之班次在【'+mytime+'點】停靠【'+mylocation+'站】之時刻表：\n')

for i in range(a): #i=第幾筆資料
    #找出使用者的現在位置(228取6)
    if data[i]['StationName']['Zh_tw'] == mylocation: 
        #判斷捷運的方向(6取3)
        if data[i]['DestinationStationName']['Zh_tw'] == mydirection:
            #print(data[i]['StationName']['Zh_tw'], i)
            b = len(data[i]['Timetables']) #b=總班次
            for j in range(b):
            #print(b)
                #禮拜一到四、禮拜五和假日的時刻表不同，故要去判斷今天是星期幾(3取1)
                if today == ('Monday' or 'Tuesday' or 'Wednesday' or 'Thursday'):
                    if i % 3 == 0:
                        x = data[i]['Timetables'][j]['ArrivalTime'].find(mytime)
                        if 2 > x >= 0:
                            print('第', data[i]['Timetables'][j]['Sequence'], '班車: ', data[i]['Timetables'][j]['ArrivalTime'])
                    else:
                        break
                elif today == ('Saturday' or 'Sunday'):
                    if i % 3 == 1:
                        x = data[i]['Timetables'][j]['ArrivalTime'].find(mytime)
                        if 2 > x >= 0:
                            print('第', data[i]['Timetables'][j]['Sequence'], '班車: ', data[i]['Timetables'][j]['ArrivalTime'])
                    else:
                        break
                else:
                    if i % 3 == 2:
                        x = data[i]['Timetables'][j]['ArrivalTime'].find(mytime)
                        if 2 > x >= 0:
                            print('第', data[i]['Timetables'][j]['Sequence'], '班車: ', data[i]['Timetables'][j]['ArrivalTime'])
                    else:
                        break

                        
#note

#2018.02.01 13:00
#一個站會有三筆資料，分別放星期一到四、假日和星期五的時刻表，因此需要先確定使用者當天的日期，才能知道要用哪張時刻表 (Done, 2018.02.01 22:00)
#方法: 第i筆除三，若餘數零為平日，餘數一為假日，餘數二為星期五
#一天至少會有140班車，最優化是只列出使用者當時時間一個小時內的車次，或是詢問使用者的想知道的車次時間範圍 (Done, 2018.02.01 23:13)
#不能直接用data[0]，要用mylocation去尋找stationName (Done, 2018.02.01 19:44)

#2018.02.01 19:44
#因為有方向性，所以一個站應該是有六筆資料，因此需要詢問使用者是要往哪個方向 (Done, 2018.02.01 20:00)
#Direction=營運路線方向描述(0去, 1回)
#DestinationStaionID=目的站車站代號

#2018.02.23 14:24
#串聯的時候，可以用結巴讓使用者直接用一句話取代三個input
#願景：票價