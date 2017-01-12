#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

from flask import Flask, render_template
import flask
from flask_ask import Ask, statement, question, request, session, version, audio
import requests
import logging
import json

app = Flask(__name__)
ask = Ask(app, '/')
log = logging.getLogger()

key = 'd903f3dcdf3f7063ed2c3f4698ea030516c4d98d'

def before_fn():
    print('--------------------\nheaders = {}, body = {}'.format(flask.request.headers, flask.request.data))

app.before_request(before_fn)

def get_feed():
    url = 'http://data.castbox.fm/feed?key=%s' % key
    r = requests.get(url)
    json = r.json()
    return json['data']

def get_track():
    url = 'http://data.castbox.fm/track?key=%s' % key
    r = requests.get(url)
    json = r.json()
    return json['data']

tracks = get_track()

def _play_track(idx):
    print('play track index #%d' % idx)
    t = tracks[idx]
    url = t['urls'][0].replace('http', 'https')
    url = url.replace('s3.castbox.fm', 'd1asnxkov2i2k7.cloudfront.net')
    title = t['title']
    print('url = %s' % url)
    resp = audio('RoboTalk. %s' % title).play(url)
    return resp

_current_idx = {}
def get_current_idx():
    user_id = session.user.userId
    if user_id not in _current_idx: _current_idx[user_id] = 0
    return _current_idx[user_id]

def set_current_idx(idx):
    user_id = session.user.userId
    _current_idx[user_id] = idx

@ask.intent('PlayTrackIntent')
def play_track():
    idx = get_current_idx()
    return _play_track(idx)

@ask.intent('AMAZON.NextIntent')
def next_track():
    idx = get_current_idx()
    if idx == len(tracks):
        return statement('This is the last episode')
    set_current_idx(idx + 1)
    return _play_track(idx + 1)

@ask.intent('AMAZON.PreviousIntent')
def prev_track():
    idx = get_current_idx()
    if idx == 0:
        return statement('This is the first episode')
    set_current_idx(idx - 1)
    return _play_track(idx - 1)

@ask.intent('AMAZON.StartOverIntent')
def start_over():
    set_current_idx(0)
    return _play_track(0)

@ask.intent('AMAZON.PauseIntent')
def on_pause():
    return audio().stop()

@ask.intent('AMAZON.ResumeIntent')
def on_resume():
    return audio().resume()

@ask.on_playback_started
def on_playback_started():
    log.info('playback started')

@ask.on_playback_finished
def on_playback_finished():
    log.info('playback finished')
    next_track()

@ask.on_playback_nearly_finished
def on_playback_nearly_finished():
    log.info('playback nearly finished')

@ask.on_playback_stopped
def on_playback_stopped():
    log.info('playback stopped')

@ask.on_playback_failed
def on_playback_failed():
    log.info('playback failed')

@ask.on_session_started
def new_session():
    log.info('new session started')

@ask.launch
def on_launch():
    return question('Hello. Here is RoboTalk.')

if __name__ == '__main__':
    app.run(debug=True)
