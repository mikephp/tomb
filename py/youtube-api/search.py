#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

# 返回结果见
# https://developers.google.com/youtube/v3/docs/search

# 参数传入见
# https://developers.google.com/youtube/v3/docs/search/list

# refers to https://developers.google.com/youtube/v3/code_samples/python#search_by_keyword

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.tools import argparser

# Set DEVELOPER_KEY to the API key value from the APIs & auth > Registered apps
# tab of
#   https://cloud.google.com/console
# Please ensure that you have enabled the YouTube Data API for your project.

DEVELOPER_KEY = "AIzaSyBglP9GAV_zOD3LGhPoIWTAfsEzgAOJ4yU"
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def create_youtube_instance():
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,
        developerKey=DEVELOPER_KEY)
    return youtube

def youtube_search(options):
    youtube = options.youtube
    # Call the search.list method to retrieve results matching the specified
    # query term.
    search_response = youtube.search().list(
      q=options.q,
      part="id,snippet",
      videoDuration = options.videoDuration,
      # maxResults=options.max_results
      maxResults = 25,
      pageToken = options.pageToken,
      **{'type': 'video'}
    ).execute()

    # videos = []
    # channels = []
    # playlists = []

    # Add each result to the appropriate list, and then display the lists of
    # matching videos, channels, and playlists.
    # for search_result in search_response.get("items", []):
      # if search_result["id"]["kind"] == "youtube#video":
      #   videos.append("%s (%s)" % (search_result["snippet"]["title"],
      #                              search_result["id"]["videoId"]))
      # elif search_result["id"]["kind"] == "youtube#channel":
      #   channels.append("%s (%s)" % (search_result["snippet"]["title"],
      #                                search_result["id"]["channelId"]))
      # elif search_result["id"]["kind"] == "youtube#playlist":
      #   playlists.append("%s (%s)" % (search_result["snippet"]["title"],
      #                                 search_result["id"]["playlistId"]))



    # print "Videos:\n", "\n".join(videos), "\n"
    # print "Channels:\n", "\n".join(channels), "\n"
    # print "Playlists:\n", "\n".join(playlists), "\n"
    return (search_response.get('items', []), search_response['pageInfo']['totalResults'], search_response['nextPageToken'])

def youtube_search_all(options):
    options.videoDuration = 'short'
    options.pageToken = ''
    options.youtube = create_youtube_instance()

    n = options.max_results
    count = 0
    while count < n:
        (items, totalNumber, nextPageToken) = youtube_search(options)
        print 'totalNumber : ', totalNumber
        print "Videos: \n", "\n".join(map(lambda x: x['snippet']['title'], items))
        options.pageToken = nextPageToken
        count += len(items)

if __name__ == "__main__":
  argparser.add_argument("--q", help="Search term", default="Google")
  argparser.add_argument("--max-results", help="Max results", default=100)
  args = argparser.parse_args()

  try:
      # youtube_search(args)
      youtube_search_all(args)
  except HttpError, e:
      print "An HTTP error %d occurred:\n%s" % (e.resp.status, e.content)
