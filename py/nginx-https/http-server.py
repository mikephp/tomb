#!/usr/bin/env python
#coding:utf-8
#Copyright (C) dirlt

import BaseHTTPServer

class Handler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        print '-----'
        print self.headers
        content = 'OK'
        self.send_response(200)
        self.send_header('Content-Length',len(content))
        self.end_headers()
        self.wfile.write(content)


def run(server_class=BaseHTTPServer.HTTPServer,
        handler_class=BaseHTTPServer.BaseHTTPRequestHandler):
    server_address = ('', 8000)
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()

run(handler_class = Handler)
