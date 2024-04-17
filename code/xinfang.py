from bs4 import BeautifulSoup
import pandas as pd
# from pyecharts.charts import Scatter
from tqdm import tqdm
import math
import requests
import lxml
import re
import time
import os
# from pyecharts.charts import Scatter
# from pyecharts import options as opts

# 区名
districtName = '越秀区'
area_dic = {
            districtName :'yuexiu'
            # '天宁区':'tianningqu',
            # '钟楼区':'zhonglouqu',
            # '新北区':'xinbeiqu',
            # '武进区':'wujinqu',
            # '金坛区':'jintanqu'
            }

# 保存文件名
outputFilename = districtName + '新房'

# 加个header以示尊敬
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Referer': 'https://gz.fang.lianjia.com/loupan/' + area_dic[districtName] + '/'}

# 新建一个会话
sess = requests.session()
sess.get(headers['Referer'], headers=headers)

# url示例：https://gz.fang.lianjia.com/loupan/liwan/pg2/#liwan
url = headers['Referer'] + "pg{}/#{}"

# 当正则表达式匹配失败时，返回默认值（errif）
def re_match(re_pattern, string, errif=None):
    try:
        return re.findall(re_pattern, string)[0].strip()
    except IndexError:
        return errif

# 新建一个DataFrame存储信息
data = pd.DataFrame()

for key_, value_ in area_dic.items():
    # 获取该行政区下房源记录数
    start_url = headers['Referer'] + '{}/'.format(value_)
    html = sess.get(start_url).text
    house_num = re.findall('<span class="value ">(.*?)</span>', html)[0].strip()
    # new web: <span class="content__title--hl">5208</span>
    # old web: <span> 9527 </span>
    print('💚{}: 新房房源共计「{}」套'.format(key_, house_num))
    time.sleep(1)
    # 页面限制🚫 每个行政区只能获取最多100页共计3000条房源信息
    total_page = int(math.ceil(int(house_num) / 10.0))
    for i in tqdm(range(total_page), desc=key_):
        while True:
            html = sess.get(url.format(i+1, area_dic[districtName])).text
            soup = BeautifulSoup(html, 'lxml')
            info_collect = soup.find_all(class_="resblock-desc-wrapper")
            if len(info_collect):
                break
        for info in info_collect:
            info = str(info).replace('\n', '')
            info_dic = {}
            ############## resblock-name ##############
            info_name = re_match('<div class="resblock-name">(.*?)</div>', str(info)).replace('\n', '')
            info_dic['title'] = re_match('<.*?target="_blank">(.*?)</a>', str(info_name))
            info_dic['type'] = re_match('</a><span class="resblock-type" style=.*?>(.*?)</span>', str(info_name))
            info_dic['status'] = re_match('</span><span class="sale-status" style=.*?>(.*?)</span>', str(info_name))
            ############## resblock-location ##############
            info_location = re_match('<div class="resblock-location"><span>(.*?)</div>', str(info)).replace('\n', '')
            info_dic['area'] = re_match('(.*?)</span>', str(info_location))
            info_dic['position'] = re_match('<span>(.*?)</span>', str(info_location))
            info_dic['street'] = re_match('<a data-other-action=.*?target="_blank">(.*?)</a>', str(info_location))
            ############## resblock-room ##############
            info_room = re_match('</div><a class="resblock-room" data-other-action=.*?>(.*?)</a>', str(info))
            if info_room:
                info_room_output = re.split('</span><i class="split">/</i><span>', info_room)
                for room_index in range(len(info_room_output)):
                    tag = 'room type ' + str(room_index + 1)
                    if room_index == 0:
                        info_dic[tag] = info_room_output[room_index].split('<span>')[1]
                    elif room_index == (len(info_room_output) - 1):
                        info_dic[tag] = info_room_output[room_index].split('</span>')[0]
                    else:
                        info_dic[tag] = info_room_output[room_index]
            ############## resblock-area ##############
            info_area = re_match('<div class="resblock-area">(.*?)</div>', str(info))
            info_dic['size'] = re_match('<span>(.*?)</span>', str(info_area))
            ############## resblock-agent ##############
            info_dic['agent'] = re_match('<span class="ke-agent-sj-name">新房顾问：(.*?)</span>', str(info))
            ############## resblock-tag ##############
            info_tag = re_match('<div class="resblock-tag">(.*?)</div><div class="resblock-price">', str(info))
            info_tag_output = re.split('</span><span>', info_tag)
            for tag_index in range(len(info_tag_output)):
                tag = 'tag ' + str(tag_index + 1)
                if tag_index == 0:
                    info_dic[tag] = info_tag_output[tag_index].split('<span>')[1]
                elif tag_index == (len(info_tag_output) - 1):
                    info_dic[tag] = info_tag_output[tag_index].split('</span>')[0]
                else:
                    info_dic[tag] = info_tag_output[tag_index]
            ############## resblock-price ##############
            info_price = re_match('<div class="resblock-price">(.*?)</div><div class="resblock-follow"', str(info))
            info_dic['average price'] = re_match('<span class="number">(.*?)</span>', str(info_price))
            info_dic['total price'] = re_match('<div class="second">(.*?)</span>', str(info_price))
            # 存入DataFrame
            if data.empty:
                data = pd.DataFrame(info_dic, index=[0])
            else:
                data = pd.concat([data, pd.DataFrame([info_dic])], ignore_index=True)

if not data.empty:
    data.to_excel(os.path.join('./data', outputFilename + '.xlsx'), index=False)

