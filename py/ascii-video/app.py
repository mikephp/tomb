#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import web
import util
from PIL import Image

urls = ('/upload', 'upload',
        '/.*', 'home')

app = web.application(urls, globals())

home_html = open('home.html').read()
class home:
    def GET(self):
        return home_html

import cgi
"""
web input

file_content_type = image/png
file_size = 3625446
file_path = /tmp/nginx_upload/0000000022
file_md5 = 1f7e1395ccc314e684eb4f46f4112308
"""
output_html = open('output.html').read()
redirect_html = open('redirect.html').read()
TEST = True
CACHE = False
import os
class upload:
    def GET(self):
        return self.POST()

    def POST(self):
        if not TEST:
            winput = web.input()
            path = winput['imgfile_path']
            ctype = winput['imgfile_content_type']
            fsize = int(winput['imgfile_size'])
            fmd5 = winput['imgfile_md5']
        else:
            path = './sample.jpg'
            ctype = 'image/jpeg'
            fsize = 135 * 1024
            fmd5 = 'md5-of-sample-jpg'
        if not ctype.startswith('image') or fsize > 8 * 1024 * 1024:
            return "Not image or image file is too large(<8MB)"
        image_html_file = '%s.html' % (fmd5)
        image_html_path = '/tmp/ascii_image_output/%s' % (image_html_file)
        # if cached.
        if CACHE and os.path.exists(image_html_path): return redirect_html % (locals())
        # resize image.
        rim = Image.open(path).convert('RGB')
        W = 120
        im = rim.resize((W, int(rim.size[1] * W / rim.size[0])))
        # write html file.
        image_html = util.image2html(im, constrast = True, font_color = True)
        with open(image_html_path, 'w') as fh: fh.write(output_html % (locals()))
        return redirect_html % (locals())

wsgiapp = app.wsgifunc()

if __name__ == "__main__":
   app.run()
