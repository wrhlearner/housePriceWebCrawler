from bs4 import BeautifulSoup
import pandas as pd
from pyecharts.charts import Scatter
from tqdm import tqdm
import math
import requests
import lxml
import re
import time
from pyecharts.charts import Scatter
from pyecharts import options as opts

area_dic = {
            # '荔湾区二手':'liwanershou'
            # '越秀区二手':'yuexiuershou'
            # '荔湾区':'liwanqu'
            # '越秀区':'yuexiuqu'
            # '钟楼区':'zhonglouqu',
            # '新北区':'xinbeiqu',
            # '武进区':'wujinqu',
            # '金坛区':'jintanqu'
            }

# 加个header以示尊敬
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        # 'Referer': 'https://gz.lianjia.com/ershoufang/liwan/'}
        'Referer': 'https://gz.lianjia.com/ershoufang/yuexiu/'}
        # 'Referer': 'https://gz.fang.lianjia.com/loupan/liwan/'}
        # 'Referer': 'https://gz.fang.lianjia.com/loupan/liwan-yuexiu/#yuexiu/'}

# 新建一个会话
sess = requests.session()
# sess.get('https://gz.lianjia.com/ershoufang/liwan/', headers=headers)
sess.get('https://gz.lianjia.com/ershoufang/yuexiu/', headers=headers)
# sess.get('https://gz.fang.lianjia.com/loupan/liwan/', headers=headers)
# sess.get('https://gz.fang.lianjia.com/loupan/liwan-yuexiu/#yuexiu/', headers=headers)

# url示例：https://sz.lianjia.com/ershoufang/luohuqu/pg2/
# url = 'https://gz.lianjia.com/ershoufang/liwan/{}/pg{}/'
url = 'https://gz.lianjia.com/ershoufang/yuexiu/{}/pg{}/'
# url = 'https://gz.fang.lianjia.com/loupan/liwan/{}/pg{}/'
# url = 'https://gz.fang.lianjia.com/loupan/liwan-yuexiu/#yuexiu/{}/pg{}/'

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
    # start_url = 'https://gz.lianjia.com/ershoufang/liwan/{}/'.format(value_)
    start_url = 'https://gz.lianjia.com/ershoufang/yuexiu/{}/'.format(value_)
    # start_url = 'https://gz.fang.lianjia.com/loupan/liwan/{}/'.format(value_)
    # start_url = 'https://gz.fang.lianjia.com/loupan/liwan-yuexiu/#yuexiu/{}/'.format(value_)
    html = sess.get(start_url).text
    house_num = re.findall('共找到<span> (.*?) </span>套.*二手房', html)[0].strip()
    print('💚{}: 二手房源共计「{}」套'.format(key_, house_num))
    time.sleep(1)
    # 页面限制🚫 每个行政区只能获取最多100页共计3000条房源信息
    total_page = int(math.ceil(min(3000, int(house_num)) / 30.0))
    for i in tqdm(range(total_page), desc=key_):
        html = sess.get(url.format(value_, i+1)).text
        soup = BeautifulSoup(html, 'lxml')
        info_collect = soup.find_all(class_="info clear")

        for info in info_collect:
            info_dic = {}
            # 行政区
            info_dic['area'] = key_
            # 房源的标题
            info_dic['title'] = re_match('target="_blank">(.*?)</a><!--', str(info))
            # 小区名
            info_dic['community'] = re_match('xiaoqu.*?target="_blank">(.*?)</a>', str(info))
            # 位置
            info_dic['position'] = re_match('<a href.*?target="_blank">(.*?)</a>.*?class="address">', str(info))
            # 税相关，如房本满5年
            info_dic['tax'] = re_match('class="taxfree">(.*?)</span>', str(info))
            # 总价
            info_dic['total_price'] = re_match('class="totalPrice"><span>(.*?)</span>万', str(info))
            # 单价
            info_dic['unit_price'] = float(re_match('data-price="(.*?)"', str(info)))

            # 匹配房源标签信息，通过|切割
            # 包括面积，朝向，装修等信息
            icons = re.findall('class="houseIcon"></span>(.*?)</div>', str(info))[0].strip().split('|')
            info_dic['hourseType'] = icons[0].strip()
            info_dic['hourseSize'] = float(icons[1].replace('平米', ''))
            info_dic['direction'] = icons[2].strip()
            info_dic['fitment'] = icons[3].strip()

            # 存入DataFrame
            if data.empty:
                data = pd.DataFrame(info_dic, index=[0])
            else:
                data = pd.concat([data, pd.DataFrame([info_dic])], ignore_index=True)

if not data.empty:
    name = 'liwanershou'
    # districtName = 'yuexiuershou'
    # districtName = 'liwanqu'
    # districtName = 'yuexiuqu'
    filename = name + '.xlsx'
    data.to_excel(filename, index=False)

