#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from config import *

from gevent import monkey
monkey.patch_socket()

ITUNES_COUNTRY_CODE = {
    'Canada': 'ca', 'Uruguay (English)': 'uy_en', 'Turkmenistan': 'tm', 'Lithuania': 'lt', 'Cambodia': 'kh', 'Germany (English)': 'de_en', 'Turkey (English)': 'tr_en', 'Micronesia': 'fm', 'Argentina': 'ar', 'Bolivia': 'bo', 'Burkina Faso': 'bf', 'Ghana': 'gh', 'Saudi Arabia': 'sa', 'Panama (English)': 'pa_en', 'Dominican Republic (English)': 'do_en', 'Japan': 'jp', 'Cape Verde': 'cv', 'Slovenia': 'si', 'Guatemala': 'gt', 'Zimbabwe': 'zw', 'Belize (Spanish)': 'bz_es', 'Jordan': 'jo', 'St. Lucia': 'lc', 'Dominica': 'dm', 'Liberia': 'lr', 'Netherlands': 'nl', 'Russia (English)': 'ru_en', 'Pakistan': 'pk', 'Netherlands (English)': 'nl_en', 'Tanzania': 'tz', 'Vietnam': 'vn', 'S\xc3\xa3o Tom\xc3\xa9 and Pr\xc3\xadncipe': 'st', 'Dominica (English)': 'dm_en', 'Mauritania': 'mr', 'Seychelles': 'sc', 'New Zealand': 'nz', 'Yemen': 'ye', 'Jamaica': 'jm', 'Malaysia (English)': 'my_en', 'Albania': 'al', 'Macau': 'mo', 'Korea (English)': 'kr_en', 'India': 'in', 'Azerbaijan': 'az', 'United Arab Emirates': 'ae', 'Kenya': 'ke', 'Tajikistan': 'tj', 'Nicaragua (English)': 'ni_en', 'Turkey': 'tr', 'Japan (English)': 'jp_en', 'Czech Republic': 'cz', 'Luxembourg (English)': 'lu_en', 'Solomon Islands': 'sb', 'Switzerland (French)': 'ch_fr', 'Palau': 'pw', 'Mongolia': 'mn', 'France': 'fr', 'Bermuda': 'bm', 'Slovakia': 'sk', 'Sweden (English)': 'se_en', 'Peru': 'pe', 'Indonesia (English)': 'id_en', 'Norway': 'no', 'Malawi': 'mw', 'Benin': 'bj', 'Macau (English)': 'mo_en', 'Brazil (English)': 'br_en', 'Singapore': 'sg', 'China': 'cn', 'Armenia': 'am', 'Suriname (English)': 'sr_en', 'Dominican Republic': 'do', 'Luxembourg (French)': 'lu_fr', 'Hong Kong (English)': 'hk_en', 'Ukraine': 'ua', 'Bahrain': 'bh', 'Cayman Islands': 'ky', 'Portugal (English)': 'pt_en', 'Finland': 'fi', 'Mauritius': 'mu', 'Sweden': 'se', 'Belarus': 'by', 'British Virgin Islands': 'vg', 'Mali': 'ml', 'Russia': 'ru', 'Bulgaria': 'bg', 'United States': 'us', 'Romania': 'ro', 'Angola': 'ao', 'Chad': 'td', 'China (English)': 'cn_en', 'Cyprus': 'cy', 'Brunei Darussalam': 'bn', 'Qatar': 'qa', 'Malaysia': 'my', 'Austria': 'at', 'Latvia': 'lv', 'Mozambique': 'mz', 'Uganda': 'ug', 'Hungary': 'hu', 'Niger': 'ne', 'El Salvador (English)': 'sv_en', 'Brazil': 'br',
    'Costa Rica (English)': 'cr_en', 'Singapore (English)': 'sg_en', 'Kuwait': 'kw', 'Panama': 'pa', 'Costa Rica': 'cr', 'Luxembourg': 'lu', 'St. Kitts and Nevis': 'kn', 'Bahamas': 'bs', 'Ireland': 'ie', 'Italy (English)': 'it_en', 'Italy': 'it', 'Nigeria': 'ng', 'Taiwan (English)': 'tw_en', 'Ecuador': 'ec', 'Australia': 'au', 'Algeria': 'dz', 'El Salvador': 'sv', 'Finland (English)': 'fi_en', 'Argentina (English)': 'ar_en', 'Turks and Caicos': 'tc', 'Chile': 'cl', 'Belgium': 'be', 'Thailand': 'th', 'Belgium (English)': 'be_en', 'Hong Kong': 'hk', 'Sierra Leone': 'sl', 'Switzerland (Italian)': 'ch_it', 'Oman': 'om', 'St. Vincent and The Grenadines': 'vc', 'Gambia': 'gm', 'Philippines': 'ph', 'Uzbekistan': 'uz', 'Moldova': 'md', 'Paraguay (English)': 'py_en', 'Croatia': 'hr', 'Guatemala (English)': 'gt_en', 'Guinea-Bissau': 'gw', 'Switzerland': 'ch', 'Grenada': 'gd', 'Spain (English)': 'es_en', 'Belize': 'bz', 'Portugal': 'pt', 'Estonia': 'ee', 'Uruguay': 'uy', 'South Africa': 'za', 'Lebanon': 'lb', 'France (English)': 'fr_en', 'Tunisia': 'tn', 'United States (Spanish)': 'us_es', 'Antigua and Barbuda': 'ag', 'Spain': 'es', 'Colombia': 'co', 'Norway (English)': 'no_en', 'Vietnam (English)': 'vn_en', 'Taiwan': 'tw', 'Fiji': 'fj', 'Barbados': 'bb', 'Madagascar': 'mg', 'Belgium (French)': 'be_fr', 'Bhutan': 'bt', 'Nepal': 'np', 'Malta': 'mt', 'Honduras (English)': 'hn_en', 'Chile (English)': 'cl_en', 'Suriname': 'sr', 'Anguilla': 'ai', 'Venezuela': 've', 'Swaziland': 'sz', 'Israel': 'il', 'Lao': 'la', 'Indonesia': 'id', 'Iceland': 'is', 'Canada (French)': 'ca_fr', 'Senegal': 'sn', 'Papua New Guinea': 'pg', 'Thailand (English)': 'th_en', 'Trinidad and Tobago': 'tt', 'Germany': 'de', 'Denmark': 'dk', 'Kazakhstan': 'kz', 'Poland': 'pl', 'Ecuador (English)': 'ec_cn', 'Kyrgyzstan': 'kg', 'Montserrat': 'ms', 'Macedonia': 'mk', 'Mexico (English)': 'mx_en', 'Sri Lanka': 'lk', 'Korea': 'kr', 'Guyana': 'gy', 'Colombia (English)': 'co_en', 'Venezuela (English)': 've_en', 'Honduras': 'hn', 'Mexico': 'mx', 'Egypt': 'eg', 'Nicaragua': 'ni', 'Denmark (English)': 'dk_en', 'Switzerland (English)': 'ch_en', 'Austria (English)': 'at_en', 'United Kingdom': 'gb', 'Congo': 'cg', 'Greece': 'gr', 'Paraguay': 'py', 'Namibia': 'na', 'Bolivia (English)': 'bo_en', 'Botswana': 'bw'}

if TEST_ON_US:
    ITUNES_COUNTRY_CODE = {'United States': 'us'}

ITUNES_PODCAST_GENRE_CODE = {
    'Arts': 1301,
    'Business': 1321,
    'Comedy': 1303,
    'Education': 1304,
    'Games & Hobbies': 1323,
    'Government & Organizations': 1325,
    'Health': 1307,
    'Kids & Family': 1305,
    'Music': 1310,
    'News & Politics': 1311,
    'Religion & Spirituality': 1314,
    'Science & Medicine': 1315,
    'Society & Culture': 1324,
    'Sports & Recreation': 1316,
    'TV & Film': 1309,
    'Technology': 1318
}

from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import *

Engine = create_engine('mysql+mysqldb://%s:%s@%s/%s' %
                       (DB_USER, DB_PASS, DB_HOST, DB_NAME), encoding='utf-8', echo=False, pool_recycle=3600)
Base = declarative_base()
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=Engine)


class Podcast(Base):
    __tablename__ = 'itunes'
    # from itunes
    pid = Column(Integer, primary_key=True)
    country = Column(String(16), index=True)
    genre = Column(Integer, index=True)
    __table_args__ = (Index('country_genre', "country", "genre"), )
    title = Column(TEXT)
    authorId = Column(Integer)
    authorName = Column(TEXT)
    feedUrl = Column(TEXT)
    cover30 = Column(TEXT)
    releaseDate = Column(DateTime)
    trackCount = Column(Integer)
    skip = Column(Integer)  # should we skip it?
    wellFormed = Column(Integer)  # content of feedUrl is well-formed?
    parsedDate = Column(DateTime)  # when this feedUrl is parsed.
    description = Column(TEXT)
    lang = Column(String(16), index=True)


class Cache(Base):
    __tablename__ = 'cache'
    mykey = Column(String(255), primary_key=True)
    tag = Column(String(16), index=True)
    value = Column(MEDIUMTEXT)
    updateDate = Column(DateTime)


Podcast.metadata.create_all(Engine)
Cache.metadata.create_all(Engine)

import gevent
from gevent.pool import Pool
import random
import requests
import os
import urllib2


def make_combination(shuffle=False):
    comb = []
    for country in ITUNES_COUNTRY_CODE.values():
        if country.find('_') != -1:
            continue
        for genre in ITUNES_PODCAST_GENRE_CODE.values():
            comb.append((country, genre))
    if shuffle:
        random.shuffle(comb)
    else:
        comb.sort(lambda x, y: cmp(x[0], y[0]))
    return comb


def down_index(comb):
    pool = Pool(size=8)
    URL = 'http://itunes.apple.com/%s/genre/id%d?mt=2'
    session = Session()
    now = dt.datetime.now()
    expireDate = now - dt.timedelta(days=CACHE_EXPIRE_DAYS)
    for (country, genre) in comb:
        def f(country, genre):
            index_key = 'idx_%s_%d' % (country, genre)
            cr = session.query(Cache).filter_by(
                mykey=index_key, tag='index').first()
            if cr and cr.updateDate > expireDate:
                # print('DOWN INDEX CACHED. (%s, %d)' % (country, genre))
                return
            print('DOWN INDEX. (%s, %d)' % (country, genre))
            url = URL % (country, genre)
            res = requests.get(url)
            if res.status_code != 200:
                print('DOWN INDEX FAILED. url = %s code = %d' %
                      (url, res.status_code))
                return
            value = res.text.encode('utf-8')
            if cr:
                cache = cr
            else:
                cache = Cache(
                    mykey=index_key, tag='index')
            cache.value = value
            cache.updateDate = now
            session.add(cache)
            session.commit()
        g = gevent.spawn(f, country, genre)
        pool.add(g)

    pool.join()
    session.commit()
    session.close()

from bs4 import BeautifulSoup
import re


def func_on_comb(comb, f):
    for (country, genre) in comb:
        f(country, genre)


def parse_index_1(country, genre):
    session = Session()
    index_key = 'idx_%s_%d' % (country, genre)
    r = session.query(Cache).filter_by(mykey=index_key, tag='index').first()
    if not r:
        print('INDEX NOT EXISTED. (%s, %d)' % (country, genre))
        return
    data = r.value
    bs = BeautifulSoup(data)
    pds = bs.select('div[id="selectedcontent"] ul li a')
    print('PARSE INDEX (%s, %d)' % (country, genre))
    pids = set()
    for pd in pds:
        title = pd.get_text().encode('utf-8')
        link = pd.attrs['href']
        m = re.search(r'/id(\d+)\?mt=2', link)
        try:
            pid = int(m.groups(1)[0])
        except:
            print('PARSE INDEX FAILED. link = %s' % (link))
            continue
        # print(link, pid)
        if pid in pids:
            continue
        pids.add(pid)
        r = session.query(Podcast).filter_by(pid=pid).first()
        if not r:
            r = Podcast(
                pid=pid, country=country, genre=genre, title=title)
        else:
            r.country = country
            r.genre = genre
            r.title = title
        session.add(r)
    session.commit()
    session.close()


import datetime as dt
import json as json_lib


def down_lookup_1(country, genre):
    session = Session()
    pids = [u.pid for u in session.query(Podcast).filter_by(
        country=country, genre=genre)]
    pool = Pool(size=4)
    now = dt.datetime.now()
    expireDate = now - dt.timedelta(days=CACHE_EXPIRE_DAYS)

    def f(pid):
        lookup_key = 'lookup_%d' % (pid)
        cr = session.query(Cache).filter_by(
            mykey=lookup_key, tag='lookup').first()
        if cr and cr.updateDate > expireDate:
            # print('DOWN LOOKUP CACHED. pid = %d' % (pid))
            return
        print('DOWN LOOKUP. pid = %d' % pid)
        url = 'http://itunes.apple.com/lookup?id=%d' % (pid)
        res = requests.get(url)
        if res.status_code != 200:
            print("DOWN LOOKUP FAILED. url = %s code = %d" %
                  (url, res.status_code))
            return
        # print(res.encoding)
        value = res.text.encode('utf-8')
        if cr:
            cache = cr
        else:
            cache = Cache(
                mykey=lookup_key, tag='lookup')
        cache.value = value
        cache.updateDate = now
        session.add(cache)
        session.commit()

    for pid in pids:
        g = gevent.spawn(f, pid)
        pool.add(g)
    pool.join()
    session.commit()
    session.close()


def parse_lookup_1(country, genre):
    session = Session()
    rs = [u for u in session.query(
        Podcast).filter_by(country=country, genre=genre)]
    pool = Pool(size=32)

    def f(r):
        pid = r.pid
        lookup_key = 'lookup_%d' % (pid)
        cr = session.query(Cache).filter_by(
            mykey=lookup_key, tag='lookup').first()
        if not cr:
            print('LOOKUP NOT EXISTED. pid = %d' % (pid))
            return
        print('PARSE LOOKUP. pid = %d' % (pid))
        json = json_lib.loads(cr.value)
        if json['resultCount'] != 1:
            if json['resultCount'] != 0:
                print('PARSE LOOKUP FAILED. result count %d. pid = %d' %
                      (json['resultCount'], pid))
            session.add(r)
            sesson.commit()
            return
        data = json['results'][0]
        # some issues when comparing datetime.
        if not FORCE_PARSE_LOOKUP and r.trackCount == data['trackCount']:
            # print('PARSE LOOKUP CACHED. pid = %d' % (pid))
            return
        # genreIds = map(lambda x: int(x), data['genreIds'])
        # genres = data['genres']
        if 'artworkUrl30' in data:
            r.cover30 = data['artworkUrl30']
        if 'releaseDate' in data:
            r.releaseDate = data['releaseDate']
        if 'trackCount' in data:
            r.trackCount = data['trackCount']
        if 'feedUrl' in data:
            r.feedUrl = data['feedUrl']
        if 'artistId' in data:
            r.authorId = data['artistId']
        if 'artistName' in data:
            r.authorName = data['artistName'].encode('utf-8')
        session.add(r)
        session.commit()

    for r in rs:
        g = gevent.spawn(f, r)
        pool.add(g)
    pool.join()
    session.commit()
    session.close()


def down_feed_1(country, genre):
    session = Session()
    rs = [u for u in session.query(
        Podcast).filter_by(country=country, genre=genre)]
    pool = Pool(size=8)
    now = dt.datetime.now()

    def f(r):
        if r.skip:
            return
        pid = r.pid
        feed_key = 'feed_%d' % (pid)
        cr = session.query(Cache).filter_by(
            mykey=feed_key, tag='feed').first()
        # 如果itunes里面有releaseDate并且缓存更新时间大于releaseDate.
        if cr and (not r.releaseDate or cr.updateDate >= r.releaseDate):
            # print('DOWN FEED CACHED. pid = %d' % pid)
            return
        url = r.feedUrl
        print('DOWN FEED. pid = %d. url = %s' % (pid, url))
        try:
            res = requests.get(url, timeout=10)
        except:
            print('DOWN FEED FAILED. CONNECTION ERROR. pid = %d, url = %s' %
                  (pid, url))
            session.add(r)
            return
        if res.status_code != 200:
            print('DOWN FEED FAILED. pid = %d, url = %s http-code = %d' %
                 (pid, url, res.status_code))
            if res.status_code in (403, 404):
                r.skip = 1
            session.add(r)
            return
        value = res.text.encode('utf-8')
        if len(value) > (1 << 23):
            r.skip = 1
            session.add(r)
            return
        if cr:
            cache = cr
        else:
            cache = Cache(
                mykey=feed_key, tag='feed')
        cache.value = value
        cache.updateDate = now
        session.add(cache)
        session.commit()

    for r in rs:
        g = gevent.spawn(f, r)
        pool.add(g)
    pool.join()
    session.commit()
    session.close()


import feedparser
import xml.dom.minidom


def extract_detail(r, now, data):
    detail = {'lang': '',
              'desc': ''}
    try:
        dom = xml.dom.minidom.parseString(data)
        d = dom.getElementsByTagName(
            'description') or dom.getElementsByTagName('itunes:summary')
        if d:
            detail['desc'] = d[0].firstChild.data
        d = dom.getElementsByTagName('language')
        if d:
            detail['lang'] = d[0].firstChild.data
    except:
        d = feedparser.parse(data)
        feed = d['feed']
        if 'description' in feed:
            detail['desc'] = feed['description']
        if 'summary' in feed:
            detail['desc'] = feed['summary']
        if 'language' in feed:
            detail['lang'] = feed['language']
    r.description = detail['desc'].encode('utf-8').strip()
    r.lang = detail['lang'].encode('utf-8').strip()
    r.wellFormed = 1
    r.parsedDate = now


def parse_feed_1(country, genre):
    session = Session()
    rs = [u for u in session.query(Podcast).filter_by(
        country=country, genre=genre)]
    pool = Pool(size=32)
    now = dt.datetime.now()

    def f(r):
        pid = r.pid
        feed_key = 'feed_%d' % (pid)
        cr = session.query(Cache).filter_by(
            mykey=feed_key, tag='feed').first()
        if not cr:
            print('FEED NOT EXISTED. pid = %d' % (pid))
            return
        if not FORCE_PARSE_FEED and r.parsedDate and r.parsedDate >= cr.updateDate:
            # print('PARSE FEED CACHED. pid = %d' % (pid))
            return
        print('PARSE FEED. pid = %d' % (pid))
        value = cr.value
        try:
            extract_detail(r, now, value)
        except Exception as e:
            print('PARSE FEED FAILED. error = %s' % (e))
            return
        session.add(r)
        session.commit()

    for r in rs:
        g = gevent.spawn(f, r)
        pool.add(g)
    pool.join()
    session.commit()
    session.close()

if __name__ == '__main__':
    comb = make_combination()
    down_index(comb)
    func_on_comb(comb, parse_index_1)
    func_on_comb(comb, down_lookup_1)
    func_on_comb(comb, parse_lookup_1)
    func_on_comb(comb, down_feed_1)
    func_on_comb(comb, parse_feed_1)
