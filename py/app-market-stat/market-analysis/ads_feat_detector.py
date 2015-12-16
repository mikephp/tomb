#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import os
import subprocess
from gevent.subprocess import Popen
import gevent
import tempfile
import logging
import biplist
import config as CF
import shutil
import traceback
import pprint as PP
import re
from xml.dom.minidom import parse
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

def find_ads(names, t = 'android'):
    ads_feat_mapping = CF.ANDROID_ADS_FEAT_MAPPING if t == 'android' else CF.IOS_ADS_FEAT_MAPPING
    ads = []
    if not names: return ads
    for kind in ads_feat_mapping.keys():
        for sdk_name in ads_feat_mapping[kind].keys():
            class_names = ads_feat_mapping[kind][sdk_name]
            for cls_name in class_names:
                if cls_name in names:
                    ads.append('%s.%s' % (kind, sdk_name))
                    break
    return ads

class IOSAdsFeatureDetector:
    def __init__(self, logger = None):
        self.logger = logging.getLogger('umdecode') if logger is None else logger

    def decode_ipa(self, tmpdir, f):
        args = ['7z', 'e', '-o%s' % tmpdir, f, 'Payload/*.app/Info.plist']
        self.logger.debug('args = %s' % args)
        p = Popen(args)
        code = p.wait()
        if code != 0:
            self.logger.warning('extract info.plist(%s) failed' % (f))
            return None

        plist = biplist.readPlist(os.path.join(tmpdir, 'Info.plist'))
        exe = plist['CFBundleExecutable']
        args = ['7z', 'e', '-o%s' % tmpdir, f, 'Payload/*.app/%s' % exe]
        self.logger.debug('args = %s' % args)
        p = Popen(args)
        code = p.wait()
        if code != 0:
            self.logger.warning('extract executable(%s) failed' % (f))
            return None

        args = ['../util/class-dump-z', '-h','cats', '-h','dogs', '%s/%s' % (tmpdir, exe)]
        self.logger.debug('args = %s' % args)
        outf = os.path.join(tmpdir, 'class-dump-z.out')
        with open(outf, 'w') as fh:
            p = Popen(args, stdout = fh)
            code = None
            for i in range(CF.SUBPROCESS_TIMEOUT):
                code = p.poll()
                if code is not None: break
                gevent.sleep(1)
            if code is None:
                # we have to kill this subprocess
                p.terminate()
                return None
            if code != 0:
                self.logger.warning('run class-dump-z(%s) failed' % (f))
                return None

        with open(outf) as fh:
            lines = fh.readlines()
            names = set()
            for line in lines:
                if line.startswith('@interface') or line.startswith('@protocol'):
                    ss = line.split(' ')
                    x = ss[1]
                    if x.startswith('XXEncryptedClass'): continue
                    names.add(x)
            return names

    def try_decode_ipa(self, f):
        tmpdir = tempfile.mkdtemp(prefix = 'umdecode')
        try:
            data = self.decode_ipa(tmpdir, f)
            if data is None: return 'EDECODE'
            return data
        except Exception as e:
            self.logger.exception(e)
            self.logger.error(traceback.format_exc())
        finally:
            shutil.rmtree(tmpdir)
        return 'EDECODE'

class AndroidAdsFeatureDetector():
    def __init__(self, logger = None):
        self.logger = logging.getLogger('umdecode') if logger is None else logger

    def decode_apk(self, tmpdir, f):
        # 不能添加--no-res, 否则无法解析AndroidManifest.xml
        args = ['java','-jar','../util/apktool_2.0.2.jar','d','-f', '-o',tmpdir,f]
        self.logger.debug('args = %s' % args)
        p = Popen(args)
        code = p.wait()
        if code != 0:
            self.logger.warning('decode apk(%s) failed' % (f))
            return None

        names = set()
        for subdir in ['smali', 'smali_classes', 'smali_classes3']:
            dir_prefix = os.path.join(tmpdir, subdir)
            for root, dirs, files in os.walk(dir_prefix):
                r = root[len(dir_prefix) + 1:]
                for d in dirs:
                    x = os.path.join(r, d)
                    names.add(x)
                # for f in files:
                #     x = os.path.join(r, f)
                #     names.add(x)

        ump = ['', '']
        mf = os.path.join(tmpdir, 'AndroidManifest.xml')
        if os.path.exists(mf):
            try:
                dom = parse(mf)
                es = dom.getElementsByTagName('meta-data')
                for e in es:
                    if e.getAttribute('android:name') == 'UMENG_APPKEY':
                        ump[0] = e.getAttribute('android:value')
                    elif e.getAttribute('android:name') == 'UMENG_CHANNEL':
                        ump[1] = e.getAttribute('android:value')
            except Exception as e:
                self.logger.exception(e)
                self.logger.error(traceback.format_exc())
        return (names, ump)

    def try_decode_apk(self, f):
        tmpdir = tempfile.mkdtemp(prefix = 'umdecode')
        ump = ['','']
        try:
            data = self.decode_apk(tmpdir, f)
            if data is None: return ('EDECODE', ump)
            return data
        except Exception as e:
            self.logger.exception(e)
            self.logger.error(traceback.format_exc())
        finally:
            shutil.rmtree(tmpdir)
        return ('EDECODE', ump)

import zlib
import base64
def compress_names(names):
    if isinstance(names, str):
        assert(names.startswith('E'))
        return names
    s = ':'.join(list(names))
    zs = zlib.compress(s, 9)
    zs2 = 'D' + base64.b64encode(zs)
    return zs2
def decompress_names(zs):
    if zs.startswith('E'): return zs
    s2 = base64.b64decode(zs[1:])
    s = zlib.decompress(s2)
    names = set(s.split(':'))
    return names

def test():
    detector = IOSAdsFeatureDetector()
    ipa_file = '../sample/iqiyi.ipa'
    names = detector.try_decode_ipa(ipa_file)
    zs = compress_names(names)
    print len(str(names)), len(zs)

    detector = AndroidAdsFeatureDetector()
    apk_file = '../sample/iqiyi.apk'
    names = detector.try_decode_apk(apk_file)
    zs = compress_names(names)
    print len(str(names)), len(zs)
    print decompress_names(zs)
    print find_ads(names, 'android')

    # print decompress_names(compress_names('EDECODE'))


if __name__ == '__main__':
    test()
