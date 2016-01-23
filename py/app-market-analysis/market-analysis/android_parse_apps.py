#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from app_fact import AppFact
import config as CF

dir_prefix_format = 'data/android_apps_response_%s'
request_url_format = 'http://api3.coolchuan.com/appdownloadurl?start=%d&limit=%d'
DEBUG = True
import urllib2

CATEGORY = {
    "android":{
        "app":{
        # "app_all": "全部应用",
        "app_金融理财": "金融理财",
        "app_通信社交": "通信社交",
        "app_网购支付": "网购支付",
        "app_系统安全": "系统安全",
        "app_生活休闲": "生活休闲",
        "app_桌面壁纸": "桌面壁纸",
        "app_新闻资讯": "新闻资讯",
        "app_摄影美化": "摄影美化",
        "app_影音图像": "影音图像",
        "app_学习办公": "学习办公",
        "app_地图旅游": "地图旅游",
        "app_健康医疗": "健康医疗"
        },
        "game": {
        # "game_all": "全部游戏",
        "game_休闲益智": "休闲益智",
        "game_体育竞速": "体育竞速",
        "game_动作格斗": "动作格斗",
        "game_卡片棋牌": "卡片棋牌",
        "game_策略游戏": "策略游戏",
        "game_经营养成": "经营养成",
        "game_网络游戏": "网络游戏",
        "game_角色扮演": "角色扮演",
        "game_飞行射击": "飞行射击"
        }
}}

APP_CATEGORIES = CATEGORY['android']['app'].values()
GAME_CATEGORIES = CATEGORY['android']['game'].values()

ASCII_NAMES = {'系统安全' : 'system',
               '桌面壁纸' : 'desktop',
               '金融理财' : 'finance',
               '通信社交' : 'social',
               '网购支付' : 'payment',
               '生活休闲' : 'life',
               '新闻资讯' : 'news',
               '摄影美化' : 'photo',
               '影音图像' : 'vid&pic',
               '学习办公' : 'study',
               '地图旅游' : 'travel',
               '健康医疗' : 'health',
               '休闲益智' : 'casual',
               '体育竞速' : 'sports',
               '动作格斗' : 'fights',
               '卡片棋牌' : 'cards',
               '策略游戏' : 'strategy',
               '经营养成' : 'bizgame',
               '网络游戏' : 'netgame',
               '角色扮演' : 'RPG',
               '飞行射击' : 'flight&shoot'
               }
APP_BIG_CATEGORIES = {}
for c in APP_CATEGORIES:
    APP_BIG_CATEGORIES[c] = (ASCII_NAMES[c], [c])
GAME_BIG_CATEGORIES = {}
for c in GAME_CATEGORIES:
    GAME_BIG_CATEGORIES[c] = (ASCII_NAMES[c], [c])

# APP_BIG_CATEGORIES = {
#     '工具': ('Tool', ['系统安全', '桌面壁纸', '摄影美化', '影音图像', '学习办公', '生活休闲', '地图旅游']),
#     '媒体': ('Media', ['新闻资讯']),
#     '社交': ('Social', ['通信社交']),
#     '商业': ('Buss', ['金融理财', '网购支付']),
# }
# GAME_BIG_CATEGORIES = {
#     '卡牌': ('Card', ['卡片棋牌','策略游戏']),
#     '休闲': ('Causal', ['休闲益智']),
#     '其他': ('Misc', ['体育竞速', '动作格斗', '经营养成', '网络游戏', '角色扮演', '飞行射击']),
# }



import time
def get_response_file(date, page):
    dir_prefix = dir_prefix_format % date
    if not os.path.exists(dir_prefix):
        os.mkdir(dir_prefix)
    if True:
        start = page * CF.ANDROID_INTERVAL
        limit = CF.ANDROID_INTERVAL
        url = request_url_format % (start, limit)
        f = '%s/page-%d.json' % (dir_prefix, page)
        if os.path.exists(f):
            # print '%s already exists' % f
            return
        print 'start download %s' % f
        s = time.time()
        response = urllib2.urlopen(url)
        data = response.read()
        with open(f, 'w') as fh:
            fh.write(data)
        print '%s downloaded.(%.2f sec)' % (f, time.time() - s)

import json
MARKETS = ('baidu', 'yingyongbao', '360', 'anzhuoshichang', 'wandoujia')
# http://www.zhihu.com/question/27882551
# MARKETS = ('baidu', 'yingyongbao', '360', 'anzhuoshichang', 'wandoujia', 'anzhi', 'yingyonghui')
cs = set()
def parse_log_file(fname):
    data = open(fname).read()
    # print fname
    js = json.loads(data)
    data = js['data']
    afs = []
    for app in data:
        af = AppFact()
        af.processed = 0
        af.ads = ''
        def fill_app_fact(af, app):
            af.type = 'android'
            af.category = app['app_category']
            af.bundleId = app['app_id']
            if 'app_name' not in app: af.title = af.bundleId
            else: af.title = app['app_name']
            af.rank = app['rank']
            markets = app['app_data_market']
            af.urls = []
            af.markets = []
            af.versions = []
            for m in markets:
                name = m['market_name']
                version = m['version']
                url = m['app_downloadurl']
                if name in MARKETS and version and url:
                    af.markets.append(name)
                    af.versions.append(version)
                    af.urls.append(url)
            cs.add(af.category)
        try:
            fill_app_fact(af, app)
            afs.append(af)
        except Exception as e:
            if DEBUG:
                print '*****ERROR: invalid json data*****'
                print app
    return afs

def read_afs(date, limit = None):
    dir_prefix = dir_prefix_format % date
    afs = []
    app = 0
    game = 0
    for page in range(CF.ANDROID_PAGE_NUM):
        f = '%s/page-%d.json' % (dir_prefix, page)
        get_response_file(date, page)
        afs0 = parse_log_file(f)
        for af in afs0:
            if af.category in APP_CATEGORIES:
                app += 1
            elif af.category in GAME_CATEGORIES:
                game += 1
        afs.extend(afs0)
        if limit and len(afs) >= limit: break
        if app > CF.ANDROID_APP_TOPN and game > CF.ANDROID_GAME_TOPN: break
        # print 'app = %s, game = %s' % (app, game)
    return afs

def test():
    date = '20151028'
    afs = read_afs(date)
    for af in afs[:10]:
        print af.rank, af.title, af.category, af.bundleId

if __name__ == '__main__':
    test()
