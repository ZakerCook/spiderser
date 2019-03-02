import requests
import json
import time
import re
import pymysql


#获取地点经纬度
def u_place(city,place):
    url = 'https://apis.map.qq.com/jsapi?'

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36',
        'Referer': 'http://www.gpsspg.com/iframe/maps/qq_181109.htm?mapi=2'
    }

    params = {
        'qt':'poi',
        'wd':city+place,
        'key':'FBOBZ-VODWU-C7SVF-B2BDI-UK3JE-YBFUS'
    }

    response = requests.get(url=url,params=params,headers=header)
    json_t = response.json()
    Jpoint = json_t['detail']['pois'][0]['pointx']
    Wpoint = json_t['detail']['pois'][0]['pointy']
    return Jpoint,Wpoint

pageSize = 30
#获取店铺信息
def get_restaurants(longitude,latitude,page):
    params = {
        'extras[]':'activities',
        'extras[]':'tags',
        'terminal':'h5',
        'latitude':latitude,
        'longitude':longitude,
        'limit':pageSize,
        'offset':int((page-1)*pageSize)
    }

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36',
        'Cookie':'这里填入cookie值',

    }

    home_url = 'https://h5.ele.me/restapi/shopping/v3/restaurants?'

    response = requests.get(url=home_url,params=params,headers=header)
    # print(json.loads(response.text))
    return json.loads(response.text)


#获取附近店铺总数量
def get_shop_count(longitude,latitude):
    c_url = 'https://h5.ele.me/restapi/shopping/v2/restaurant/category?'
    param = {
        'longitude':longitude,
        'latitude':latitude
    }
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36',
        'Cookie': 'ubt_ssid=49lfrco993xvbgk1o8ndd6821op53sgo_2019-02-18;perf_ssid=n041w5merbcy6eok6uvf4hg20n5wg9nq_2019-02-18;'
                  '_utrace=1cbec626f80b0ce5422997a6e82bec72_2019-02-18; cna=PGnxFP1O3EYCAXTi8byHT8GK;',
    }

    resp = requests.get(url=c_url,params=param,headers=headers)
    count = resp.json()[0]['count']
    print(count)
    return count


#获取需求的数据
shop_info = {}
def get_data(response,checkad):
    for items in response['items']:
        shop_info['id'] = items['restaurant']['id']
        shop_info['name'] = items['restaurant']['name']
        print(items['restaurant']['address'])
        if checkad in items['restaurant']['address']:
            shop_info['address'] = items['restaurant']['address']
        else:
            continue
        shop_info['phone'] = items['restaurant']['phone']
        #纬度
        shop_info['latitude'] = str(items['restaurant']['latitude'])
        #经度
        shop_info['longitude'] = str(items['restaurant']['longitude'])
        #店铺评价分数
        shop_info['rating'] = str(items['restaurant']['rating'])
        #做出评价人数
        shop_info['rating_count'] = str(items['restaurant']['rating_count'])
        #最近一个月订单量
        shop_info['recent_order_num'] = str(items['restaurant']['recent_order_num'])
        #配送费
        fee = items['restaurant']['piecewise_agent_fee']['tips'].split('¥')[-1]
        shop_info['delivery_free'] = fee
        yield shop_info

# 数据插入到数据库中
def add_to_data(item):
    conn = pymysql.connect(host='localhost', port=3306, user='root', passwd='123456', db='db_eleme', charset='utf8')
    cursor = conn.cursor()
    cursor.execute("select count(*) from dpinfo where r_id='%s'"%item['id'])
    da = cursor.fetchone()
    print('da:'+str(da))
    if da[0]:
        print('已存在于数据库中')
    else:
        cursor.execute("insert into dpinfo(r_id,r_name,r_address,r_phone,r_latitude,r_longitude,r_rating,r_rating_count,r_recent_order_num,r_delivery_free)"
                    "value('%s','%s','%s','%s','%.5f','%s','%s','%s','%s','%s')"%(item['id'],item['name'],item['address'],
                                                                         item['phone'],item['latitude'],item['longitude'],
                                                                         item['rating'],item['rating_count'],item['recent_order_num'],
                                                                         item['delivery_free']))
    conn.commit()
    cursor.close()


def add_to_csv(item):
    with open(r'D:\wm.csv','a',encoding='utf-8') as f:
        f.write('------'.join(item.values())+'\n')


if __name__ == '__main__':

    checkad = input('请输入城市名称')
    address = input('请输入地点 eg:xxx县xxx小区')
    x,y = u_place(checkad,address)
    count = get_shop_count(x,y)

    #总页数
    total_page,divpage = divmod(count,pageSize)
    if not divpage==0:
        total_page +=1

    for p in range(1,total_page+1):
        print('第%d页数据'%p)
        r = get_restaurants(x,y,p)
        for j in get_data(r,checkad):
            print(j)
            # add_to_data(j)
            add_to_csv(j)
        time.sleep(1)

