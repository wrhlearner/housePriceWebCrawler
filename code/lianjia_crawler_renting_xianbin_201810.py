import requests
import csv
from bs4 import BeautifulSoup
import re 
import datetime
import json

url_base = 'https://sh.lianjia.com/zufang/jiading/pg'  ###这是嘉定的
ids_rented = []  ###设为全局变量，用来保存已经爬下来的已出租房源的id，后面将用于判断是否已经爬过了，id不在列表里的话就继续爬

def get_detail_info(url_detail):
    
    back = {}
    res = requests.get(url_detail)
    soup_detail = BeautifulSoup(res.text, 'lxml')
    
    if len(soup_detail.find_all(class_ = 'tips decoration')) > 0:
        back['decoration'] = soup_detail.find_all(class_ = 'tips decoration')[0].contents[0]    
    else:
        back['decoration'] = 'Not Sure'      ###装修类型
    
    back['room_price'] = soup_detail.find_all(class_ = 'total')[0].contents[0] ###房间的价格
    back['room_square'] = soup_detail.find_all(class_ = 'zf-room')[0].find_all('p')[0].contents[1].strip('平米') ###房间的面积
    back['room_type'] = soup_detail.find_all(class_ = 'zf-room')[0].find_all('p')[1].contents[1].split(' ')[0]  ###房间的户型
    back['room_floor'] = soup_detail.find_all(class_ = 'zf-room')[0].find_all('p')[2].contents[1].split(' ')[0]   ###房间所在楼层
    back['room_TotalFloor'] = re.sub("\D", "", soup_detail.find_all(class_ = 'zf-room')[0].find_all('p')[2].contents[1]) ###建筑的楼层数
    back['room_orientation'] = soup_detail.find_all(class_ = 'zf-room')[0].find_all('p')[3].contents[1]  ###房间朝向
    back['room_metro'] = soup_detail.find_all(class_ = 'zf-room')[0].find_all('p')[4].contents[1]  ###附近地铁
    back['room_district'] = soup_detail.find_all(class_ = 'zf-room')[0].find_all('p')[5].find_all('a')[0].contents[0] ###所在小区
    back['room_district_id'] = re.sub('\D', '', soup_detail.find_all(class_ = 'zf-room')[0].find_all('p')[5].a['href'])  ###所在小区id
    back['room_location1'] = soup_detail.find_all(class_ = 'zf-room')[0].find_all('p')[6].find_all('a')[0].contents[0] ###所在行政区
    back['room_location2'] = soup_detail.find_all(class_ = 'zf-room')[0].find_all('p')[6].find_all('a')[1].contents[0] ###所在片区
    
    back['HowManyDays'] = re.sub("\D", "", soup_detail.find_all(class_ = 'zf-room')[0].find_all('p')[7].contents[1]) ###挂牌时间
    today=datetime.date.today()
    result_date = today + datetime.timedelta(days = - int(back['HowManyDays']))
    back['post_date'] = result_date.strftime('%Y-%m-%d')
        
    back['method_rent'] = soup_detail.find_all(class_ = 'base')[0].find_all('li')[0].contents[-1]  ###出租模式
    back['method_payment'] = soup_detail.find_all(class_ = 'base')[0].find_all('li')[1].contents[-1].strip()  ###付款方式
    back['room_condition'] = soup_detail.find_all(class_ = 'base')[0].find_all('li')[2].contents[-1]    ###目前状态
    back['method_heat'] = soup_detail.find_all(class_ = 'base')[0].find_all('li')[3].contents[-1]  ###供暖方式
    
    back['count_recent7days'] = soup_detail.find_all(class_ = 'count')[0].contents[0]         ###最近七天看房次数
    back['count_total'] = soup_detail.find_all(class_ = 'totalCount')[0].span.contents[0]     ###历史看房次数
    
    if len(soup_detail.find_all(class_ = 'se')) > 0:
        ###是否有衣橱
        if 'tags' in soup_detail.find_all(class_ = 'se')[0].find_all('li')[0]['class']:
            back['if_wardrobe'] = 1
        else:
            back['if_wardrobe'] = 0

        ###是否有桌椅
        if 'tags' in soup_detail.find_all(class_ = 'se')[0].find_all('li')[1]['class']:
            back['if_table'] = 1
        else:
            back['if_table'] = 0

        ###是否有电视
        if 'tags' in soup_detail.find_all(class_ = 'se')[0].find_all('li')[2]['class']:
            back['if_tv'] = 1
        else:
            back['if_tv'] = 0

        ###是否有冰箱
        if 'tags' in soup_detail.find_all(class_ = 'se')[0].find_all('li')[3]['class']:
            back['if_refrigerator'] = 1
        else:
            back['if_refrigerator'] = 0

        ###是否有洗衣机
        if 'tags' in soup_detail.find_all(class_ = 'se')[0].find_all('li')[4]['class']:
            back['if_washmachine'] = 1
        else:
            back['if_washmachine'] = 0

        ###是否有空调
        if 'tags' in soup_detail.find_all(class_ = 'se')[0].find_all('li')[5]['class']:
            back['if_aircondition'] = 1
        else:
            back['if_aircondition'] = 0

        ###是否有热水器
        if 'tags' in soup_detail.find_all(class_ = 'se')[0].find_all('li')[6]['class']:
            back['if_hotwater'] = 1
        else:
            back['if_hotwater'] = 0

        ###是否有微波炉
        if 'tags' in soup_detail.find_all(class_ = 'se')[0].find_all('li')[7]['class']:
            back['if_microwave'] = 1
        else:
            back['if_microwave'] = 0

        ###是否有暖气
        if 'tags' in soup_detail.find_all(class_ = 'se')[0].find_all('li')[8]['class']:
            back['if_heat'] = 1
        else:
            back['if_heat'] = 0

        ###是否有网络
        if 'tags' in soup_detail.find_all(class_ = 'se')[0].find_all('li')[9]['class']:
            back['if_wlan'] = 1
        else:
            back['if_wlan'] = 0

        ###是否有天然气
        if 'tags' in soup_detail.find_all(class_ = 'se')[0].find_all('li')[10]['class']:
            back['if_gas'] = 1
        else:
            back['if_gas'] = 0   
            
    
    
    return back

for i in range(41):

    print(i+1)
    rooms = []
    rooms_rented = []
    url_page = url_base + str(i+1)
    res = requests.get(url_page)
    soup = BeautifulSoup(res.text, 'lxml')

    n = 0
    for info in soup.find_all(class_ = 'house-lst')[0].contents:
        
        n = n + 1
        if len(info.find_all(class_ = 'ziroomTag zufang_ziroom')) > 0:
            continue ###判断是不是自如的房源，如果是的话就跳过。自如的房源数据结构不一样，还是单独写个脚本爬比较好
            
        room = {}
        room['id'] = info['data-housecode'] ###房子的唯一编码
        
        YearType = info.find_all(class_ = 'con')[0].contents[4]  ###房子的结构类型
        if len(re.sub('\D', '', YearType)) > 0:
            room['building_year'] = re.sub('\D', '', YearType)
            room['building_type'] = re.sub('\d', '', YearType).strip('年建')
        else:
            room['building_year'] = 0
            room['building_type'] = YearType
        
        time_update = info.find_all(class_ ='price-pre')[0].contents[0].split(' ')[0].split('.') ###上次价格的更新信息
        room['time_update'] =  '-'.join(time_update)
        
        ###获取房子的详细信息
        url_room = info.find_all(class_ = 'info-panel')[0].h2.contents[0]['href'] ###房子的url
        back = get_detail_info(url_detail = url_room)
        room.update(back)       
        print('online_' + str(n))
        print(url_room)
        
        rooms.append(room)
        
        
        ####下面要获取已出租房源的信息
        url_rented_list = 'https://sh.lianjia.com/zufang/housestat?hid=' + room['id'] + '&rid=' + room['room_district_id']
        rr = requests.get(url_rented_list)
        rented_list = json.loads(rr.text)
        
        if 'bizcircleSold' in rented_list['data']:
            for rented_biz in rented_list['data']['bizcircleSold']:
                room_rented = {}

                ### 先判断是不是自如的房源，是的话跳过。然后判断该房源是不是已经爬过了，是的话跳过
                if rented_biz['source'] == 'ziroom':
                    continue
                elif rented_biz['houseId'] in ids_rented:
                    continue
                else:
                    ids_rented.append(rented_biz['houseId'])
                    room_rented['id'] = rented_biz['houseId']
                    room_rented['transDate'] = rented_biz['transDate']

                    url_rented = rented_biz['house_url']
                    back = get_detail_info(url_detail = url_rented)
                    room_rented.update(back)
                    print('rented_bizcircle')
                    print(url_rented)

                    room_rented['room_square'] = rented_biz['area'] ###对于已出租房源，从详细页面里面获取的面积有时候比较奇怪，用json里的覆盖

                    rooms_rented.append(room_rented)
        
        if 'resblockSold' in rented_list['data']:
            for rented_res in rented_list['data']['resblockSold']:
                room_rented = {}
                if rented_res['source'] == 'ziroom':
                    continue
                elif rented_res['houseId'] in ids_rented:
                    continue
                else:
                    ids_rented.append(rented_res['houseId'])
                    room_rented['id'] = rented_res['houseId']
                    room_rented['transDate'] = rented_res['transDate']

                    url_rented = rented_res['house_url']
                    back = get_detail_info(url_detail = url_rented)
                    room_rented.update(back)
                    print('rented_resblock')
                    print(url_rented)

                    room_rented['room_square'] = rented_biz['area'] ###对于已出租房源，从详细页面里面获取的面积有时候比较奇怪，用json里的覆盖

                    rooms_rented.append(room_rented) 
    
    headings = ['HowManyDays', 'building_type', 'building_year', 'count_recent7days', 'count_total', 'decoration', 'id', 'if_aircondition', 
                'if_gas', 'if_heat', 'if_hotwater', 'if_microwave', 'if_refrigerator', 'if_table', 'if_tv', 'if_wardrobe', 'if_washmachine',
               'if_wlan', 'method_heat', 'method_payment', 'method_rent', 'post_date', 'room_TotalFloor', 'room_condition', 'room_district', 
                'room_district_id', 'room_floor', 'room_location1', 'room_location2', 'room_metro', 'room_orientation', 'room_price',
                'room_square', 'room_type', 'time_update']
    
    with open('house_online.csv', 'a+', encoding = 'utf-8') as on:
                on_csv = csv.DictWriter(on, headings)
                on_csv.writerows(rooms)
                
    
    
    headings = ['HowManyDays', 'count_recent7days', 'count_total', 'decoration', 'id', 'if_aircondition', 
                'if_gas', 'if_heat', 'if_hotwater', 'if_microwave', 'if_refrigerator', 'if_table', 'if_tv', 'if_wardrobe', 'if_washmachine',
               'if_wlan', 'method_heat', 'method_payment', 'method_rent', 'post_date', 'room_TotalFloor', 'room_condition', 'room_district', 
                'room_district_id', 'room_floor', 'room_location1', 'room_location2', 'room_metro', 'room_orientation', 'room_price',
                'room_square', 'room_type', 'transDate']
    
    with open('house_sold.csv', 'a+', encoding = 'utf-8') as so:
                so_csv = csv.DictWriter(so, headings)
                so_csv.writerows(rooms_rented)


