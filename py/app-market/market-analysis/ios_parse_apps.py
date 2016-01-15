#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import os
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from app_fact import AppFact
import config as CF

# 只挑选应用类别, 游戏类通常太大.
# generals = ['应用','游戏']
generals = ['应用',]
details = ['书籍, 商业, 教育, 娱乐, 财经, 健康, 生活, 旅行, 医疗, 音乐, 导航, 新闻, 摄影, 效率, 参考, 社交, 体育, 美食, 工具, 天气'.split(', '),
    '角色扮演, 休闲娱乐, 射击游戏, 益智游戏, 棋牌天地, 情景游戏, 冒险游戏, 策略游戏, 模拟经营, 动作游戏, 体育竞技, 竞速游戏, 格斗游戏, 儿童教育'.split(', ')]
page_num = 20
dir_prefix_format = 'data/ios_apps_response_%s'
DEBUG = False

def get_response_files(date):
    dir_prefix = dir_prefix_format % date
    if not os.path.exists(dir_prefix):
        os.mkdir(dir_prefix)

    for i in range(len(generals)):
        g = generals[i]
        ds = details[i]
        for d in ds:
            for pg in range(page_num):
                f = 'ios_apps_request/%s/%s-%d.pp' % (g, d, pg)
                out = '%s/%s-%s-%d.log' % (dir_prefix, g, d, pg)
                if os.path.exists(out):
                    # print '%s already exists' % (out)
                    continue
                cmd = "curl -A 'PPHelperNS/2.2.4 CFNetwork/711.1.16 Darwin/14.0.0' --data-binary @'%s' -o '%s' http://mobileup.25pp.com/index.php" % (f, out)
                os.system(cmd)

"""
class Software < BinData::Record
  endian :little

  uint32 :recordid
  uint8 :adsite
  uint8 :resources_type
  uint8 :k
  uint32 :device
  stringz :buId
  stringz :version
  stringz :download_url
  uint32 :url_crc
  stringz :title
  stringz :file_size
  uint32 :catid
  stringz :category
  stringz :thumb_url
  uint8 :stars
  uint32 :downloads
  uint32 :comment_num
  uint32 :update_time
end

class PLog < BinData::Record
  endian :little
  uint32 :file_length
  uint32 :a
  uint16 :b
  uint8 :c
  uint16 :d
  uint8 :e
  uint32 :f
  uint32 :soft_length

  array :softwares,:initial_length => :soft_length, :type => :software

end
"""

import struct
def struct_unpack(fmt, data, offset):
    # first character indicates endian.
    endian = fmt[0]
    saved_fmt = ''
    data_offset = offset
    data_size = 0
    results = []
    for i in range(1, len(fmt)):
        if fmt[i] == 'Z':
            if saved_fmt:
                # print endian + saved_fmt, struct.calcsize(endian + saved_fmt)
                result = struct.unpack_from(endian + saved_fmt, data, data_offset)
                results.extend(result)
                data_offset += struct.calcsize(endian + saved_fmt)
                saved_fmt = ''
            pos = data[data_offset:].find(chr(0x0))
            assert(pos != -1)
            s = data[data_offset:data_offset + pos]
            # print s
            data_offset += pos + 1
            results.append(s)
        else:
            saved_fmt += fmt[i]
    if saved_fmt:
        # print endian + saved_fmt, struct.calcsize(endian + saved_fmt)
        result = struct.unpack_from(endian + saved_fmt, data, data_offset)
        results.extend(result)
        data_offset += struct.calcsize(endian + saved_fmt)
    return results, data_offset - offset

import os
def parse_log_file(fname):
    data = open(fname).read()
    header_fmt = '<IIHBHBII'
    if struct.calcsize(header_fmt) > len(data):
        if DEBUG:
            print 'incomplete data. ignore this file %s' % (fname)
        return []
    (t, sz) = struct_unpack(header_fmt, data, 0)
    soft_length = t[7]
    data_fmt = '<IBBBIZZZIZZIZZBIII'
    offset = sz
    # soft_length == 30
    # print soft_length
    afs = []
    for i in range(soft_length):
        (t, sz) = struct_unpack(data_fmt, data, offset)
        offset += sz
        af = AppFact()
        af.processed = 0
        af.ads = ''
        af.type = 'ios'
        af.markets = ['apple']
        af.bundleId = t[5]
        af.versions = [t[6]]
        af.urls = [t[7]]
        af.title = t[9]
        af.category = t[12]
        # af.compose_key()
        afs.append(af)
    assert(offset == len(data))
    return afs

def read_afs(date):
    get_response_files(date)
    dir_prefix = dir_prefix_format % date
    afs = []
    for i in range(len(generals)):
        g = generals[i]
        ds = details[i]
        for d in ds:
            rank = 0
            for pg in range(page_num):
                f = '%s/%s-%s-%d.log' % (dir_prefix, g, d, pg)
                afs0 = parse_log_file(f)
                for af in afs0:
                    af.general = g
                    af.rank = rank
                    rank += 1
                afs.extend(afs0)
    return afs

def test():
    date = '20151028'
    get_response_files(date)
    afs = read_afs(date)
    for af in afs[:10]:
        print af.rank, af.title, af.category, af.bundleId

if __name__ == '__main__':
    test()
