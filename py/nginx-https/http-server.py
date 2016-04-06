#!/usr/bin/env python
# coding:utf-8
# Copyright (C) dirlt

import BaseHTTPServer


class Handler(BaseHTTPServer.BaseHTTPRequestHandler):

    def do_GET(self):
        print '===================='
        print self.headers
        content = 'OK'
        self.send_response(200)
        self.send_header('Content-Length', len(content))
        self.end_headers()
        self.wfile.write(content)

import sys
def run(server_class=BaseHTTPServer.HTTPServer,
        handler_class=BaseHTTPServer.BaseHTTPRequestHandler):
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

run(handler_class=Handler)
