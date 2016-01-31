#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

from PIL import ImageFont, ImageDraw, Image

def image2ascii_color(im): # simply output text. should come with colored output
    code = open(__file__).read().replace('\n', ' ').replace(' ', '')
    ss = []
    idx = 0
    for y in range(0,im.size[1]):
        s = ''.join([code[(idx + i) % len(code)] for i in range(im.size[0])])
        idx += im.size[0]
        ss.append(s)
    return ss

def ascii2image(ss, im, constrast = True, font_size = 4, delta = 1):
    # fnt = ImageFont.truetype('Courier_New.ttf', size = font_size)
    # fnt = ImageFont.truetype('Consolas.ttf', size = font_size)
    fnt = ImageFont.load_default()
    (sw, sh) = fnt.getsize(ss[0][0])
    (ew, eh) = im.size
    # print ew, eh, len(ss[0]), len(ss)
    assert(ew == len(ss[0]) and eh == len(ss))
    w = (sw + delta) * len(ss[0])
    h = (sh + delta) * len(ss)
    # print ew, eh, w, h
    (dx, dy) = (0, 0)
    if (ew * 1.0 / eh) > (w * 1.0 / h):
        nw = int(ew * 1.0 * h / eh)
        dx = (nw - w) * 0.5
        w = nw
    else:
        nh = int(eh * 1.0 * w / ew)
        dy = (nh - h) * 0.5
        h = nh
    # print dx, dy, w, h
    txt = Image.new('RGB', (w, h), (0, 0, 0) if constrast else (255, 255, 255))
    d = ImageDraw.Draw(txt)
    for (idx , s) in enumerate(ss):
        y = dy + idx * (sh + delta) + delta * 0.5
        x = dx + delta * 0.5
        for (idx2, s2) in enumerate(s):
            pixel = im.getpixel((idx2, idx))
            d.text((x, y), s2, font = fnt, fill = pixel if constrast else (0, 0, 0))
            x += (sw + delta)
    return txt

def mosaic_effect(im, box, scale = 0.2):
    im2 = im.crop(box)
    sz = im2.size
    im2 = im2.resize((int(im2.size[0] * scale), int(im2.size[1] * scale)), Image.NEAREST)
    im2 = im2.resize(sz)
    im3 = im.copy()
    im3.paste(im2, box)
    return im3

def test_image():
    fnames = ['sample.jpg', 'sample.png']
    constrast = True
    # decrease original image size and font size can reduce runtime.
    font_size = 12
    delta = 4
    for fname in fnames:
        rim = Image.open(fname).convert('RGB')
        im = rim
        ss = image2ascii_color(im)
        im2 = ascii2image(ss, im, constrast = constrast, font_size = font_size, delta = delta)
        im2.save('ascii-%s' % (fname))
        sz = rim.size
        im3 = mosaic_effect(rim, (sz[0] / 4, sz[1] / 4, sz[1] * 3 / 4, sz[1] * 3 / 4) , 0.05)
        im3.save('mosaic-%s' % (fname))

from moviepy.editor import *
import numpy
import time
def process_clip(clip_name):
    clip = VideoFileClip(clip_name)
    timer = [0, 0]
    def make_frame(t):
        f = clip.get_frame(t)
        (h, w, _) = f.shape
        s = time.time()
        im = Image.fromarray(f)
        timer[0] += (time.time() - s)
        s = time.time()
        im = mosaic_effect(im, (40, 40, 600, 600), scale = 0.05)
        f2 = numpy.asarray(im) # much more efficient than numpy.array(im.getdata())
        timer[1] += (time.time() - s)
        f2 = f2.reshape((im.size[1], im.size[0], 3))
        return f2
    clip2 = VideoClip(make_frame, duration = clip.duration)
    clip2.write_videofile(clip_name + '.mp4', fps = clip.fps)
    print('timer = {}'.format(timer))
    clip = VideoFileClip(clip_name).fx(vfx.mirror_x)
    clip.write_videofile(clip_name + '.mirror.mp4', fps = clip.fps)

# greyscale_10 = " .:-=+*#%@"
# def image2ascii(im, constrast = False):
#     im = im.convert("L") # convert to mono
#     ss = []
#     idx = 0
#     for y in range(0,im.size[1]):
#         s = ''
#         for x in range(0,im.size[0]):
#             p = 255 - im.getpixel((x, y))
#             if constrast: p = 255 - p
#             if p >= 225: c = greyscale_10[-1]
#             else: c = greyscale_10[p / 25]
#             s = s + c
#         ss.append(s)
#     return ss

greyscale_70 = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'.."
def image2ascii(im, constrast = False):
    im = im.convert("L") # convert to mono
    ss = []
    idx = 0
    for y in range(0,im.size[1]):
        s = ''
        for x in range(0,im.size[0]):
            p = im.getpixel((x, y))
            if constrast: p = 255 - p
            if p >= 207: c = greyscale_70[-1]
            else: c = greyscale_70[p / 3]
            s = s + c
        ss.append(s)
    return ss

import cgi
html_template = open('image.html').read()
def image2html(im, constrast = True, font_color = False):
    color = 'white' if constrast else 'black';
    bcolor = 'black' if constrast else 'white';
    ss = image2ascii(im, constrast = constrast)
    if not font_color:
        s = '</br>\n'.join(map(lambda x: cgi.escape(x), ss))
    else:
        (w, h) = im.size
        ys = []
        for y in range(h):
            sp = None
            sp_idx = -1
            xs = []
            for x in range(w):
                p = im.getpixel((x, y))
                if p == sp: continue
                elif sp: xs.append((sp, sp_idx, x))
                sp = p
                sp_idx = x
            if sp: xs.append((sp, sp_idx, w))
            s = ''.join(["<font color=\"#%X%X%X\">%s</font>" % (sp[0], sp[1], sp[2], cgi.escape(ss[y][f:t])) for (sp, f, t) in xs])
            ys.append(s)
        s = '</br>\n'.join(ys)
    image = s
    return html_template % (locals())

def test_image_to_html():
    W = 80
    for fname in ['sample.jpg', 'sample.png']:
        rim = Image.open(fname).convert('RGB')
        im = rim.resize((W, int(rim.size[1] * W / rim.size[0])))
        html = image2html(im, constrast = True, color = True)
        with open('ascii-' + fname + '.html', 'w') as fh:
            fh.write(html)

if __name__ == '__main__':
    # test_image()
    # process_clip('sample.mov')
    test_image_to_html()
