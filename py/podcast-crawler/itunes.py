#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from gevent import monkey
monkey.patch_socket()

ITUNES_COUNTRY_CODE = {
    'Canada': 'ca', 'Uruguay (English)': 'uy_en', 'Turkmenistan': 'tm', 'Lithuania': 'lt', 'Cambodia': 'kh', 'Germany (English)': 'de_en', 'Turkey (English)': 'tr_en', 'Micronesia': 'fm', 'Argentina': 'ar', 'Bolivia': 'bo', 'Burkina Faso': 'bf', 'Ghana': 'gh', 'Saudi Arabia': 'sa', 'Panama (English)': 'pa_en', 'Dominican Republic (English)': 'do_en', 'Japan': 'jp', 'Cape Verde': 'cv', 'Slovenia': 'si', 'Guatemala': 'gt', 'Zimbabwe': 'zw', 'Belize (Spanish)': 'bz_es', 'Jordan': 'jo', 'St. Lucia': 'lc', 'Dominica': 'dm', 'Liberia': 'lr', 'Netherlands': 'nl', 'Russia (English)': 'ru_en', 'Pakistan': 'pk', 'Netherlands (English)': 'nl_en', 'Tanzania': 'tz', 'Vietnam': 'vn', 'S\xc3\xa3o Tom\xc3\xa9 and Pr\xc3\xadncipe': 'st', 'Dominica (English)': 'dm_en', 'Mauritania': 'mr', 'Seychelles': 'sc', 'New Zealand': 'nz', 'Yemen': 'ye', 'Jamaica': 'jm', 'Malaysia (English)': 'my_en', 'Albania': 'al', 'Macau': 'mo', 'Korea (English)': 'kr_en', 'India': 'in', 'Azerbaijan': 'az', 'United Arab Emirates': 'ae', 'Kenya': 'ke', 'Tajikistan': 'tj', 'Nicaragua (English)': 'ni_en', 'Turkey': 'tr', 'Japan (English)': 'jp_en', 'Czech Republic': 'cz', 'Luxembourg (English)': 'lu_en', 'Solomon Islands': 'sb', 'Switzerland (French)': 'ch_fr', 'Palau': 'pw', 'Mongolia': 'mn', 'France': 'fr', 'Bermuda': 'bm', 'Slovakia': 'sk', 'Sweden (English)': 'se_en', 'Peru': 'pe', 'Indonesia (English)': 'id_en', 'Norway': 'no', 'Malawi': 'mw', 'Benin': 'bj', 'Macau (English)': 'mo_en', 'Brazil (English)': 'br_en', 'Singapore': 'sg', 'China': 'cn', 'Armenia': 'am', 'Suriname (English)': 'sr_en', 'Dominican Republic': 'do', 'Luxembourg (French)': 'lu_fr', 'Hong Kong (English)': 'hk_en', 'Ukraine': 'ua', 'Bahrain': 'bh', 'Cayman Islands': 'ky', 'Portugal (English)': 'pt_en', 'Finland': 'fi', 'Mauritius': 'mu', 'Sweden': 'se', 'Belarus': 'by', 'British Virgin Islands': 'vg', 'Mali': 'ml', 'Russia': 'ru', 'Bulgaria': 'bg', 'United States': 'us', 'Romania': 'ro', 'Angola': 'ao', 'Chad': 'td', 'China (English)': 'cn_en', 'Cyprus': 'cy', 'Brunei Darussalam': 'bn', 'Qatar': 'qa', 'Malaysia': 'my', 'Austria': 'at', 'Latvia': 'lv', 'Mozambique': 'mz', 'Uganda': 'ug', 'Hungary': 'hu', 'Niger': 'ne', 'El Salvador (English)': 'sv_en', 'Brazil': 'br',
    'Costa Rica (English)': 'cr_en', 'Singapore (English)': 'sg_en', 'Kuwait': 'kw', 'Panama': 'pa', 'Costa Rica': 'cr', 'Luxembourg': 'lu', 'St. Kitts and Nevis': 'kn', 'Bahamas': 'bs', 'Ireland': 'ie', 'Italy (English)': 'it_en', 'Italy': 'it', 'Nigeria': 'ng', 'Taiwan (English)': 'tw_en', 'Ecuador': 'ec', 'Australia': 'au', 'Algeria': 'dz', 'El Salvador': 'sv', 'Finland (English)': 'fi_en', 'Argentina (English)': 'ar_en', 'Turks and Caicos': 'tc', 'Chile': 'cl', 'Belgium': 'be', 'Thailand': 'th', 'Belgium (English)': 'be_en', 'Hong Kong': 'hk', 'Sierra Leone': 'sl', 'Switzerland (Italian)': 'ch_it', 'Oman': 'om', 'St. Vincent and The Grenadines': 'vc', 'Gambia': 'gm', 'Philippines': 'ph', 'Uzbekistan': 'uz', 'Moldova': 'md', 'Paraguay (English)': 'py_en', 'Croatia': 'hr', 'Guatemala (English)': 'gt_en', 'Guinea-Bissau': 'gw', 'Switzerland': 'ch', 'Grenada': 'gd', 'Spain (English)': 'es_en', 'Belize': 'bz', 'Portugal': 'pt', 'Estonia': 'ee', 'Uruguay': 'uy', 'South Africa': 'za', 'Lebanon': 'lb', 'France (English)': 'fr_en', 'Tunisia': 'tn', 'United States (Spanish)': 'us_es', 'Antigua and Barbuda': 'ag', 'Spain': 'es', 'Colombia': 'co', 'Norway (English)': 'no_en', 'Vietnam (English)': 'vn_en', 'Taiwan': 'tw', 'Fiji': 'fj', 'Barbados': 'bb', 'Madagascar': 'mg', 'Belgium (French)': 'be_fr', 'Bhutan': 'bt', 'Nepal': 'np', 'Malta': 'mt', 'Honduras (English)': 'hn_en', 'Chile (English)': 'cl_en', 'Suriname': 'sr', 'Anguilla': 'ai', 'Venezuela': 've', 'Swaziland': 'sz', 'Israel': 'il', 'Lao': 'la', 'Indonesia': 'id', 'Iceland': 'is', 'Canada (French)': 'ca_fr', 'Senegal': 'sn', 'Papua New Guinea': 'pg', 'Thailand (English)': 'th_en', 'Trinidad and Tobago': 'tt', 'Germany': 'de', 'Denmark': 'dk', 'Kazakhstan': 'kz', 'Poland': 'pl', 'Ecuador (English)': 'ec_cn', 'Kyrgyzstan': 'kg', 'Montserrat': 'ms', 'Macedonia': 'mk', 'Mexico (English)': 'mx_en', 'Sri Lanka': 'lk', 'Korea': 'kr', 'Guyana': 'gy', 'Colombia (English)': 'co_en', 'Venezuela (English)': 've_en', 'Honduras': 'hn', 'Mexico': 'mx', 'Egypt': 'eg', 'Nicaragua': 'ni', 'Denmark (English)': 'dk_en', 'Switzerland (English)': 'ch_en', 'Austria (English)': 'at_en', 'United Kingdom': 'gb', 'Congo': 'cg', 'Greece': 'gr', 'Paraguay': 'py', 'Namibia': 'na', 'Bolivia (English)': 'bo_en', 'Botswana': 'bw'}

TEST = True
if TEST:
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
from config import *

Engine = create_engine('mysql+mysqldb://%s:%s@%s/%s' %
                       (DB_USER, DB_PASS, DB_HOST, DB_NAME), encoding='utf-8', echo=False, pool_recycle=3600)
Base = declarative_base()
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=Engine)


class Podcast(Base):
    __tablename__ = 'itunes'
    # from itunes
    pid = Column(Integer, primary_key=True)
    lang = Column(String(16), index=True)
    genre = Column(Integer, index=True)
    title = Column(TEXT)
    checkDate = Column(DateTime)
    authorId = Column(Integer)
    authorName = Column(TEXT)
    feedUrl = Column(TEXT)
    cover30 = Column(TEXT)
    releaseDate = Column(DateTime)
    trackCount = Column(Integer)
    # from feed
    # subtitle = Column(TEXT)
    # description = Column(TEXT)
    # cover = Column(TEXT)
    # email = Column(TEXT)
    # link = Column(TEXT)
    # category = Column(TEXT)


class Cache(Base):
    __tablename__ = 'cache'
    mykey = Column(String(255), primary_key=True)
    tag = Column(String(16), index=True)
    value = Column(MEDIUMTEXT)


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
    for (country, genre) in comb:
        def f(country, genre):
            index_key = 'idx_%s_%d' % (country, genre)
            r = session.query(Cache).filter_by(
                mykey=index_key, tag='index').first()
            if r:
                # print('CACHE INDEX. (%s, %d)' % (country, genre))
                return
            print('HANDLE INDEX. (%s, %d)' % (country, genre))
            url = URL % (country, genre)
            r = requests.get(url)
            if r.status_code != 200:
                print('GET INDEX FAILED. url = %s, code = %d' %
                      (url, r.status_code))
                return
            value = r.text.encode('utf-8')
            cache = Cache(
                mykey=index_key, tag='index', value=value)
            session.add(cache)
            try:
                session.commit()
            except:
                print(
                    'INSERT INDEX FAILED. key = %s, value size = %d' % (
                        index_key, len(value)))
        g = gevent.spawn(f, country, genre)
        pool.add(g)
    pool.join()
    session.close()

from bs4 import BeautifulSoup
import re


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
        r = session.query(Podcast.pid).filter_by(pid=pid).first()
        if r or pid in pids:
            continue
        pids.add(pid)
        r = Podcast(
            pid=pid, lang=country, genre=genre, title=title)
        session.add(r)
    session.commit()
    session.close()


def parse_index(comb):
    for (country, genre) in comb:
        parse_index_1(country, genre)

import datetime as dt
import json as json_lib


def down_lookup_1(country, genre):
    session = Session()
    pids = [u.pid for u in session.query(Podcast).filter_by(
        lang=country, genre=genre)]
    pool = Pool(size=8)

    def f(pid):
        lookup_key = 'lookup_%d' % (pid)
        r = session.query(Cache).filter_by(
            mykey=lookup_key, tag='lookup').first()
        if r:
            # print('CACHE LOOKUP. pid = %d' % (pid))
            return
        print('HANDLE LOOKUP pid = %d' % pid)
        url = 'http://itunes.apple.com/lookup?id=%d' % (pid)
        res = requests.get(url)
        if res.status_code != 200:
            print("GET LOOKUP FAILED. url = %s, code = %d" %
                  (url, res.status_code))
            return
        # print(res.encoding)
        value = res.text.encode('utf-8')
        cache = Cache(mykey=lookup_key, tag='lookup', value=value)
        session.add(cache)
        try:
            session.commit()
        except:
            print('INSERT LOOKUP FAILED. key = %s, value size = %d' %
                  (lookup_key, len(value)))

    for pid in pids:
        g = gevent.spawn(f, pid)
        pool.add(g)
    pool.join()
    session.close()


def down_lookup(comb):
    for (country, genre) in comb:
        down_lookup_1(country, genre)


def parse_lookup_1(country, genre):
    session = Session()
    rs = [u for u in session.query(
        Podcast).filter_by(lang=country, genre=genre)]
    pool = Pool(size=8)

    def f(r):
        if r.checkDate:
            return
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
                print('FAILED. result count %d. pid = %d' %
                      (json['resultCount'], pid))
            r.checkDate = dt.datetime.today()
            session.add(r)
            sesson.commit()
            return
        data = json['results'][0]
        genreIds = map(lambda x: int(x), data['genreIds'])
        genres = data['genres']
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
        r.checkDate = dt.datetime.today()
        session.add(r)
        session.commit()

    for r in rs:
        g = gevent.spawn(f, r)
        pool.add(g)
    pool.join()
    session.close()


def parse_lookup(comb):
    for (country, genre) in comb:
        parse_lookup_1(country, genre)

if __name__ == '__main__':
    comb = make_combination()
    # down_index(comb)
    # parse_index(comb)
    # down_lookup(comb)
    # parse_lookup(comb)
