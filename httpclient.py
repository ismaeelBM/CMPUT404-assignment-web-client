#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, Ismaeel Bin Mohiuddin, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    def get_host_port_path(self,url):
        host = url
        port = 80
        path = "/"
        if url.startswith("http"):
            if "://" in url:
                host = url.split("://")[1]
        
        if "/" in host:
            (host, path) = host.split("/", 1)
            path = "/" + path

        if ":" in host:
            try:
                port = int(host.split(":")[-1])
                host = host.split(":", 1)[0]
            except:
                port = 80

        return (host, port, path)


    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.socket.connect((host, port))
        except:
            self.socket.close()
            return False
        return True

    def get_code(self, data):
        try:
            return int(data.split(" ")[1])
        except:
            return 404

    def get_headers(self,data):
        header = data.split("\r\n\r\n")[0]
        return header

    def get_body(self, data):
        body = data.split("\r\n\r\n")[-1]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return buffer.decode('utf-8')

    def GET(self, url, args=None):
        code = 404
        body = ""
        (host, port, path) = self.get_host_port_path(url)
        payload = f'GET {path} HTTP/1.0\r\nHost: {host}\r\n\r\n'
        if (self.connect(host, port)):
            self.sendall(payload)
            self.socket.shutdown(socket.SHUT_WR)

            data = self.recvall(self.socket)

            header = self.get_headers(data)
            body = self.get_body(data)
            code = self.get_code(header)

            print(data)

            self.close()

            return HTTPResponse(code, body)
        else:
            return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 404
        body = ""
        post_body = ""
        (host, port, path) = self.get_host_port_path(url)
        payload = f'POST {path} HTTP/1.0\r\nHost: {host}\r\n'
        if args != None:
            for key in args.keys():
                post_body += str(key) + "=" + str(args[key]) + "&"
            post_body = post_body[:-1]
            length = len(post_body)
            payload += f"Content-Length: {length}\r\nContent-Type:application/x-www-form-urlencoded \r\n"

        else:
            payload += f"Content-Length: 0\r\nContent-Type:application/x-www-form-urlencoded \r\n"

        payload += "\r\n"
        payload += post_body
        if (self.connect(host, port)):
            self.sendall(payload)
            self.socket.shutdown(socket.SHUT_WR)

            data = self.recvall(self.socket)

            header = self.get_headers(data)
            body = self.get_body(data)
            code = self.get_code(header)

            print(data)

            self.close()

            return HTTPResponse(code, body)
        else:
            return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
