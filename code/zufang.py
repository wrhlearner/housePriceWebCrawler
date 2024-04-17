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
outputFilename = districtName + '租房'

# 加个header以示尊敬
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Referer': 'https://gz.lianjia.com/zufang/yuexiu/'}

# 新建一个会话
sess = requests.session()
sess.get(headers['Referer'], headers=headers)

# url示例：https://sz.lianjia.com/ershoufang/luohuqu/pg2/
url = headers['Referer'] + "pg{}/#contentlist"

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
    house_num = re.findall('<span class="content__title--hl">(.*?)</span>', html)[0].strip()
    # new web: <span class="content__title--hl">5208</span>
    # old web: <span> 9527 </span>
    print('💚{}: 租房房源共计「{}」套'.format(key_, house_num))
    time.sleep(1)
    # 页面限制🚫 每个行政区只能获取最多100页共计3000条房源信息
    total_page = int(math.ceil(min(3000, int(house_num)) / 30.0))
    for i in tqdm(range(total_page), desc=key_):
        # wait forever to avoid network issue
        while True:
            html = sess.get(url.format(i+1)).text
            soup = BeautifulSoup(html, 'lxml')
            info_collect = soup.find_all(class_="content__list--item--main")
            if len(info_collect):
                break
        for info in info_collect:
            info = str(info).replace('\n', '')
            info_dic = {}
            # 房源的标题
            info_dic['title'] = re_match('<a class="twoline" href.*?target="_blank">(.*?)</a>', str(info))
            if info_dic['title'] is None:
                info_dic['title'] = re_match('<a href=.*?target="_blank">(.*?)</a>', str(info))
            ########### info des ###########
            info_des = re_match('<p class="content__list--item--des">(.*?)</p>', str(info))
            info_des_pos = re_match('<a href=.*?target="_blank">(.*?)</a><i>', info_des)
            if info_des_pos:
                # 行政区
                info_dic['area'] = re_match('(.*?)</a>-<a', info_des_pos)
                # 位置
                info_dic['position'] = re_match('</a>-<a href=.*?target="_blank">(.*?)</a>', info_des_pos)
                # 小区
                info_dic['community'] = info_des_pos.split('>')[-1]
            else:
                # 剩余房屋
                info_dic['room left'] = re_match('<span class="room__left">(.*?)</span>', info_des)
            info_des_i = re_match('<i>/</i>(.*?)</span>', info_des)
            if info_des_i:
                info_des_output = re.split('<i>/</i>', info_des_i)
                # 面积
                info_dic['size'] = info_des_output[0].strip()
                # 朝向
                info_dic['orientation'] = info_des_output[1].strip()
                # 房间
                info_dic['room'] = re.split('<span class="hide">', info_des_output[2])[0].strip()
                # 楼层
                info_dic['floor'] = info_des_output[3].replace(' ', '')
            ########### info bottom oneline ###########
            info_bottom = re_match('<p class="content__list--item--bottom oneline">(.*?)</p>', str(info)).replace('\n', '')
            info_bottom_output = re.split('<i class="content__item__tag--', info_bottom)
            for infoIndex in range(1, len(info_bottom_output)):
                tag = info_bottom_output[infoIndex].split('">')[0]
                info_dic[tag] = info_bottom_output[infoIndex].split('">')[1].split('</i>')[0]
            ########### info brand oneline ###########
            info_brand = re_match('<p class="content__list--item--brand oneline">(.*?)</p>', str(info)).replace(' ', '')
            info_dic['brand'] = re_match('<spanclass="brand">(.*?)</span>', info_brand)
            info_dic['time online'] = re_match('<spanclass="content__list--item--timeoneline">(.*?)</span>', info_brand)

            # 月租
            info_dic['price'] = re_match('<span class="content__list--item-price"><em>(.*?)</em>', str(info))
            # 存入DataFrame
            if data.empty:
                data = pd.DataFrame(info_dic, index=[0])
            else:
                data = pd.concat([data, pd.DataFrame([info_dic])], ignore_index=True)

if not data.empty:
    data.to_excel(os.path.join('./data', outputFilename + '.xlsx'), index=False)

