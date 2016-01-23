#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import config as CF
import pymongo
from pymongo import MongoClient
import run_apps as RA
import ads_feat_detector as AFD
from android_parse_apps import APP_BIG_CATEGORIES, GAME_BIG_CATEGORIES, APP_CATEGORIES, GAME_CATEGORIES
import pprint as PP
import os
from config import transform_ads
import android_export_channel as AEC

client = MongoClient(CF.MONGO_URL)
db = client.market_analysis

category_actions = [
    ('all' , lambda t: t.find({},)), # sort = [('rank', pymongo.ASCENDING)])),

    ('android_top' , lambda t: t.find({'type':'android'}, sort = [('rank', pymongo.ASCENDING)])),
    ('ios_top' , lambda t: t.find({'type':'ios'}, sort = [('rank', pymongo.ASCENDING)])),
    ('android_top300' , lambda t: t.find({'type': 'android'}, limit = 300,  sort = [('rank', pymongo.ASCENDING)])),
    # 一些应用没有任何类别，我们放在非游戏分类下面.
    ('android_app_top' , lambda t: t.find({'type':'android', 'category' : {'$in' : APP_CATEGORIES + ['']}}, sort = [('rank', pymongo.ASCENDING)])),
    ('android_game_top',  lambda t: t.find({'type':'android', 'category' : {'$in' : GAME_CATEGORIES}}, sort = [('rank', pymongo.ASCENDING)])),
    ('android_app_top300' , lambda t: t.find({'type':'android', 'category' : {'$in' : APP_CATEGORIES + ['']}}, limit = 300, sort = [('rank', pymongo.ASCENDING)])),
    ('android_game_top300', lambda t: t.find({'type':'android', 'category' : {'$in' : GAME_CATEGORIES}}, limit = 300, sort = [('rank', pymongo.ASCENDING)])),
]

category_texts = {
    'android_top': 'Android整体市场',
    'ios_top': 'iOS整体市场',
    'android_top300': 'Android市场Top300',
    'android_app_top': 'Android非游戏类',
    'android_app_top300': 'Android非游戏类Top300',
    'android_game_top': 'Android游戏类',
    'android_game_top300' : 'Android游戏类Top300'
}

# for category in APP_CATEGORIES + GAME_CATEGORIES:
#     key = 'android_%s' % category
#     category_actions.append((key, lambda t: t.find({'type': 'android', 'category': category})))
# for category in APP_CATEGORIES:
#     key = 'android_%s' % category
#     category_texts[key] = 'Android市场非游戏类: %s' % (category)
# for category in GAME_CATEGORIES:
#     key = 'android_%s' % category
#     category_texts[key] = 'Android市场游戏类: %s' % (category)

class F:
    def __init__(self, value):
        self.v = value
    def __call__(self, t):
        return t.find({'type': 'android', 'category': {'$in': self.v}})

# for idx, category in enumerate(APP_BIG_CATEGORIES):
#     v = APP_BIG_CATEGORIES[category]
#     key = 'android_%s' % v[0]
#     category_actions.append((key, F(v[1])))
#     category_texts[key] = 'Android市场非游戏类: %s' % (category)

# for category in GAME_BIG_CATEGORIES:
#     v = GAME_BIG_CATEGORIES[category]
#     key = 'android_%s' % v[0]
#     category_actions.append((key, F(v[1])))
#     category_texts[key] = 'Android市场游戏类: %s' % (category)

category_action_mapping = {}
for (k, v) in category_actions:
    category_action_mapping[k] = v

def get_apps_by_category(date, category):
    f = category_action_mapping[category]
    table = db['apps_run_%s' % date]
    return f(table)

def save_to_apps_ads_history(date):
    apps = get_apps_by_category(date, 'all')
    RA.drop_apps_ads_by_date(db, date)
    docs = []
    for app in apps:
        doc = RA.make_app_ads_doc(app['type'], app['bundleId'], date, app['ads'], app['title'])
        docs.append(doc)
        if len(docs) > 1000:
            print 'saving 1000 docs...'
            RA.insert_new_apps_ads(db, docs)
            docs = []
    if len(docs):
        print 'saving %d docs...'  % (len(docs))
        RA.insert_new_apps_ads(db, docs)
        docs = []

def get_sdk_kind(ad): return ad.split('.')[0]
def get_sdk_name(ad): return ad.split('.')[1]
def invalid_ad(ad): return ad in ('EDECODE', 'EF2BIG', 'EDOWNLOAD', 'ENOSRC', '')

def compute_delta(doc, ads):
    # assert(doc is None)
    if doc is None: return []
    ads0 = doc['ads'].split(';')
    ads0 = filter(lambda x: not invalid_ad(x), ads0)
    ads0 = transform_ads(ads0)
    delta = []
    for ad in ads:
        if not ad in ads0:
            sdk = get_sdk_name(ad)
            delta.append('+' + sdk)
    for ad in ads0:
        if not ad in ads:
            sdk = get_sdk_name(ad)
            delta.append('-' + sdk)
    return delta

def gen_category_detail_view(date, category, limit = None):
    apps = get_apps_by_category(date, category)
    r = 0
    view = []
    # before = CF.days_before(date, CF.RUN_INTERVAL_DAYS)
    before = CF.months_before(date, 1)
    for app in apps:
        r +=1
        if limit and r > limit: break
        doc = RA.get_apps_ads_by_date(db, app['type'], app['bundleId'], before)
        raw_ads = app['ads'].split(';')
        ads = filter(lambda x: not invalid_ad(x), raw_ads)
        ads = transform_ads(ads)
        delta = compute_delta(doc, ads)
        simple_ads = map(lambda x: get_sdk_name(x), ads)
        if not ads: delta = []; ads = simple_ads = raw_ads
        view.append((app['bundleId'], app['title'], ads, simple_ads, delta))
    return view

def gen_category_general_counter(date, category, limit = None):
    mapping = CF.ANDROID_ADS_FEAT_MAPPING if category.startswith('android') else CF.IOS_ADS_FEAT_MAPPING
    counter = zero_counter(category)
    apps = get_apps_by_category(date, category)
    r = 0
    for app in apps:
        r += 1
        if limit and r > limit: break
        raw_ads = app['ads'].split(';')
        ads = filter(lambda x: not invalid_ad(x), raw_ads)
        ads = transform_ads(ads)
        counter['@SUM'] += 1
        if not ads:
            counter['@NOSDK'] += 1
            if 'EDECODE' in raw_ads: counter['@EDECODE'] += 1
            elif 'EF2BIG' in raw_ads: counter['@EF2BIG'] += 1
            elif 'EDOWNLOAD' in raw_ads: counter['@EDOWNLOAD'] += 1
            elif 'ENOSRC' in raw_ads: counter['@ENOSRC'] += 1
            continue
        s = set()
        for ad in ads:
            kind = get_sdk_kind(ad)
            name = get_sdk_name(ad)
            counter[kind][name] += 1
            s.add(kind)
        for kind in s:
            counter[kind]['@SUM'] += 1
    return counter

def save_category_general_counter(date, category, counter):
    RA.insert_new_apps_stat(db, category, date, counter)

def zero_counter(category):
    mapping = CF.ANDROID_ADS_FEAT_MAPPING if category.startswith('android') else CF.IOS_ADS_FEAT_MAPPING
    counter = {}
    counter['@SUM'] = 0
    counter['@NOSDK'] = 0
    counter['@EDECODE'] = 0
    counter['@EF2BIG'] = 0
    counter['@EDOWNLOAD'] = 0
    counter['@ENOSRC'] = 0
    for kind in mapping.keys():
        counter[kind] = {}
        counter[kind]['@SUM'] = 0
        counter[kind]['@NOSDK'] = 0
        for sdk in mapping[kind].keys():
            counter[kind][sdk] = 0
    return counter

def gen_category_general_view(date, category, counter):
    counters = [counter]
    dates = [date]
    for i in range(CF.REPORT_BACKTRACE_NUMBER):
        # date0 = CF.days_before(date, (i+1)*CF.RUN_INTERVAL_DAYS)
        date0 = CF.months_before(date, (i+1))
        counter0 = RA.get_apps_stat_by_date(db, category, date0)
        if counter0 is None: counter0 = zero_counter(category)
        dates.append(date0)
        counters.append(counter0)
    mapping = CF.ANDROID_ADS_FEAT_MAPPING if category.startswith('android') else CF.IOS_ADS_FEAT_MAPPING
    view = {}
    view['@SUM'] = map(lambda x: x['@SUM'], counters)
    view['@NOSDK'] = map(lambda x: x['@NOSDK'], counters)
    view['@EDECODE'] = map(lambda x: x['@EDECODE'], counters)
    view['@EF2BIG'] = map(lambda x: x['@EF2BIG'], counters)
    view['@EDOWNLOAD'] = map(lambda x: x['@EDOWNLOAD'], counters)
    view['@ENOSRC'] = map(lambda x: x['@ENOSRC'], counters)
    for kind in mapping.keys():
        view[kind] = {}
        view[kind]['@SUM'] = map(lambda x: x[kind]['@SUM'], counters)
        # temporary.
        vs = []
        for sdk in mapping[kind].keys():
            vs.append((sdk, counter[kind][sdk]))
        vs.sort(lambda x,y : -cmp(x[1], y[1]))
        cs = []
        for v in vs:
            (sdk, ct0) = v
            t0 = map(lambda x: x[kind][sdk], counters)
            t1 = map(lambda x: x[kind][sdk] * 100.0 / x[kind]['@SUM'] if x[kind]['@SUM'] != 0 else 0, counters)
            cs.append((sdk, t0, t1))
        view[kind]['@COL'] = cs
    return view

import matplotlib.pyplot as plt
import numpy as np
# def write_bar_image(fname, labels, values):
#     N = len(labels)
#     if N > 10:
#         labels = labels[:10]
#         values = values[:10]
#         N = 10
#     ind = np.arange(N)  # the x locations for the groups
#     width = 0.4       # the width of the bars
#     fig, ax = plt.subplots()
#     rect = ax.bar(ind, values, width, color='blue', alpha = 0.4)
#     # add some text for labels, title and axes ticks
#     ax.set_xticks(ind+width * 0.5)
#     ax.set_xticklabels(labels)
#     def autolabel(rects):
#         # attach some text labels
#         for i, rect in enumerate(rects):
#             height = rect.get_height()
#             ax.text(rect.get_x()+rect.get_width()/2., 0.9*height, '%.2f'%values[i],
#                     ha='center', va='bottom')
#     autolabel(rect)
#     plt.savefig(fname)
#     plt.close()

# def write_trend_image(fname, dates, sdks, values):
#     N = CF.REPORT_BACKTRACE_NUMBER + 1
#     xs = np.arange(N)
#     plt.xticks(xs, dates)
#     for i, sdk in enumerate(sdks):
#         vs = values[i]
#         plt.plot(xs, vs, label = sdk)
#     plt.legend(loc = 'upper left')
#     plt.savefig(fname)
#     plt.close()


import pygal
def write_bar_image(fname, labels, values):
    N = len(labels)
    if N > 10:
        labels = labels[:10]
        values = values[:10]
        N = 10
    c = pygal.Bar(human_readable = True, legend_at_bottom = True, print_values = True)
    c.value_formatter = lambda x : '%.2f%%' % (x)
    for (i, v) in enumerate(labels):
        c.add(v, values[i])
    # c.render_to_png(fname)
    c.render_to_file(fname)

def write_trend_image(fname, dates, sdks, values):
    N = CF.REPORT_BACKTRACE_NUMBER + 1
    c = pygal.Line(human_readable = True, legend_at_bottom = True)
    c.x_labels = dates
    for i, sdk in enumerate(sdks):
        vs = values[i]
        c.add(sdk, vs)
    # c.render_to_png(fname)
    c.render_to_file(fname)

def bar_image_name(category, kind): return 'images/%s_%s_bar.svg' % (category, kind)
def trend_image_name(category, kind): return 'images/%s_%s_trend.svg' % (category, kind)

def gen_images_from_view(date, category, view):
    dir = 'report/%s/' % (date)
    if not os.path.exists(dir + '/images'):
        os.makedirs(dir + '/images')
    dates = [date[4:]]
    for i in range(CF.REPORT_BACKTRACE_NUMBER):
        # date0 = CF.days_before(date, (i+1)* CF.RUN_INTERVAL_DAYS)
        date0 = CF.months_before(date, (i+1))
        dates.append(date0[4:])
    for kind in view.keys():
        if kind.startswith('@'): continue
        if view[kind]['@SUM'][0] == 0: continue # no data at all.
        ds = view[kind]['@COL']
        labels = []
        values = []
        for d in ds:
            (sdk, vs, ps) = d
            if vs[0] == 0: continue
            labels.append(sdk)
            values.append(ps[0])
        if len(labels) <= 2: continue
        f1 = os.path.join(dir, bar_image_name(category, kind))
        # with plt.xkcd():
        write_bar_image(f1, labels, values)

        labels = []
        values = []
        for d in ds:
            (sdk, vs, ps) = d
            if all(map(lambda x: x==0, vs)): continue
            labels.append(sdk)
            values.append(ps[::-1])
        f2 = os.path.join(dir, trend_image_name(category, kind))
        # with plt.xkcd():
        write_trend_image(f2, dates[::-1], labels, values)

def generate_index_file(date, limit = None):
    dir = 'report/%s' % (date)
    if not os.path.exists(dir):
        os.makedirs(dir)
    os.system('rm -rf %s/images/' % dir)
    ARD_lines = []
    ARD_lines.append("# Android市场竞品报告(%s)" % date)
    ARD_lines.append('[下载详细报告](%s_android_detail.xls)\n' % date)
    IOS_lines = []
    IOS_lines.append('# iOS市场竞品报告(%s)' % date)
    IOS_lines.append('[下载详细报告](%s_ios_detail.xls)\n' % date)
    for (k, v) in category_actions:
        if k == 'all': continue
        if k.startswith('android'):
            lines = ARD_lines
            ads_feat_mapping = CF.ANDROID_ADS_FEAT_MAPPING
            sdk_texts = CF.ANDROID_SDK_TEXTS
            kind_texts = CF.ANDROID_KIND_TEXTS
            UMSDKS = CF.ANDROID_UMSDKS
        else:
            lines = IOS_lines
            ads_feat_mapping = CF.IOS_ADS_FEAT_MAPPING
            sdk_texts = CF.IOS_SDK_TEXTS
            kind_texts = CF.IOS_KIND_TEXTS
            UMSDKS = CF.IOS_UMSDKS
        category = k
        print 'generate view of %s' % (category)
        counter = gen_category_general_counter(date, category, limit)
        view = gen_category_general_view(date, category, counter)
        print 'generate image of %s' % (category)
        gen_images_from_view(date, category, view) # 产生各种图片
        print 'generate um_cross of %s' % (category)
        um_cross = um_cross_counter(date, category)
        no_sum = view['@SUM'][0]
        no_sdk = view['@NOSDK'][0]
        no_edecode = view['@EDECODE'][0]
        no_ef2big = view['@EF2BIG'][0]
        no_edownload = view['@EDOWNLOAD'][0]
        no_enosrc = view['@ENOSRC'][0]
        lines.append("## %s(%d)" % (category_texts[category], no_sum))
        if no_enosrc: lines.append('%d App未在已知市场上发布\n' % no_enosrc)
        if no_sdk : lines.append("%d App未检测到集成任何SDK, 其中\n" % no_sdk)
        if no_edecode: lines.append("- %d App无法解压缩apk\n" % no_edecode)
        if no_ef2big: lines.append("- %d App的apk文件过大(>256MB)\n" % no_ef2big)
        if no_edownload: lines.append("- %d App无法下载apk\n" % no_edownload)
        if um_cross['@SUM']:
            lines.append('### 友盟SDK集成重合度\n')
            lines.append('- 集成友盟SDK: %d App, 集成友盟所有SDK: %d App\n' % (um_cross['@SUM'], um_cross['@ALL']))
            # if um_cross['top']:
            #     lines.append('- 高度集成友盟SDK的App有:\n')
            #     for app in um_cross['top']:
            #         lines.append('  - %s(%s)\n' % (app['title'], app['bundleId']))
            for sdk in UMSDKS:
                s = um_cross[sdk]['@SUM']
                lines.append('- 集成%s: %d App' % (sdk_texts[sdk], s))
                for sdk2 in UMSDKS:
                    if sdk == sdk2: continue
                    v = um_cross[sdk][sdk2]
                    lines.append('    - 没有集成%s: %d App(%.2f)' %(sdk_texts[sdk2], v, 0 if s == 0 else v * 100.0 / s))
                lines.append('')
        for kind in ads_feat_mapping:
            kind_text = kind_texts[kind]
            v = view[kind]['@SUM'][0]
            lines.append('### *%s/%s(%d)*\n' % (kind, kind_text, v))
            ds = view[kind]['@COL']
            for d in ds:
                (sdk, vs, ps) = d
                sdk_text = ''
                if sdk in sdk_texts:
                    sdk_text = '(%s)' % sdk_texts[sdk]
                lines.append('- %s%s : %d(%.2f %%)' % (sdk, sdk_text, vs[0], ps[0]))
            f = bar_image_name(category, kind)
            txt = ''
            if os.path.exists(dir + '/' + f):
                f = f.replace('.svg', '.png')
                txt += '![](%s) ' % f
            f = trend_image_name(category, kind)
            if os.path.exists(dir + '/' + f):
                f = f.replace('.svg', '.png')
                txt += '![](%s) ' %f
            if txt: lines.append('\n%s' % txt)
            lines.append('\n')
    with open(dir + '/android_index.md', 'w') as fh:
        fh.writelines(map(lambda x : x + '\n', ARD_lines))
    with open(dir + '/ios_index.md', 'w') as fh:
        fh.writelines(map(lambda x: x + '\n', IOS_lines))
    with open(dir + '/tohtml', 'w') as fh:
        fh.write('pandoc --toc -s --ascii -o android_index.html android_index.md\n')
        fh.write('pandoc --toc -s --ascii -o ios_index.html ios_index.md\n')
    os.system('chmod +x %s/tohtml' % dir)

import pyExcelerator as PYE
def generate_excel_file(date, t = 'android', limit = None):
    dir = 'report/%s' % (date)
    if not os.path.exists(dir):
        os.makedirs(dir)
    book = PYE.Workbook()
    for (k, v) in category_actions:
        if not k.startswith(t): continue
        category = k
        print 'genrate view of %s' % category
        view = gen_category_detail_view(date, category)
        sheet = book.add_sheet(category)
        for row, values in enumerate(view):
            col = 0
            for i in range(len(values)):
                if i in (2,): continue
                v = values[i]
                if isinstance(v, list):
                    v = ';'.join(v)
                sheet.write(row, col, v)
                col += 1
    f = dir + '/%s_%s_detail.xls' % (date, t)
    book.save(f)

def save_to_apps_stat_history(date):
    for (k, v) in category_actions:
        if k == 'all': continue
        print "save view of '%s'" % (k)
        counter = gen_category_general_counter(date, k)
        save_category_general_counter(date, k, counter)


def um_cross_counter(date, category):
    SDKS = CF.ANDROID_UMSDKS if category.startswith('android') else CF.IOS_UMSDKS
    apps = get_apps_by_category(date, category)
    counter = {'@SUM' : 0, '@ALL' : 0}
    for sdk in SDKS:
        counter[sdk] = {'@SUM': 0}
        for sdk2 in SDKS:
            if sdk2 == sdk: continue
            counter[sdk][sdk2] = 0
    counter['top'] = []
    for app in apps:
        raw_ads = app['ads'].split(';')
        ads = filter(lambda x: not invalid_ad(x), raw_ads)
        ads = transform_ads(ads)
        ads = filter(lambda x: x in SDKS, map(lambda x: get_sdk_name(x), ads))
        if not ads: continue
        counter['@SUM'] += 1
        if len(ads) == len(SDKS):
            counter["@ALL"] += 1
        if len(ads) >= (len(SDKS) - 1):
            counter['top'].append(app)
        for sdk in SDKS:
            if not sdk in ads: continue
            counter[sdk]['@SUM'] += 1
            for sdk2 in SDKS:
                if sdk == sdk2: continue
                if not sdk2 in ads: counter[sdk][sdk2] += 1
    return counter

def test():
    limit = 100
    date = '20151028'
    # save_to_apps_ads_history(date)
    # save_to_apps_stat_history(date)

    category = 'android_top'
    # view = gen_category_detail_view(date, category, limit)
    # PP.pprint(view)

    # counter = gen_category_general_counter(date, category, limit)
    # view = gen_category_general_view(date, category, counter)
    # PP.pprint(counter)
    # PP.pprint(view)

    # gen_images_from_view(date, category, view)
    # generate_index_file(date, limit)
    um_cross = um_cross_counter(date, category)
    PP.pprint(um_cross)

import sys
def main():
    date = sys.argv[1]
    save_to_apps_ads_history(date)
    save_to_apps_stat_history(date)
    generate_index_file(date)
    generate_excel_file(date, 'android')
    generate_excel_file(date, 'ios')
    AEC.export(date, 5000)
    os.system('cd report; tar czvf %s.tgz %s; cd ..' % (date, date))

if __name__ == '__main__':
    #test()
    main()
