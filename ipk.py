from socketserver import TCPServer as tcps
from socketserver import BaseRequestHandler as handler
import re
import socket
import urllib.request, urllib.error
from urllib.parse import urlparse


def editRequestedString(string):
    edited = string.decode()
    toarray = edited.split()
    if toarray[0] == 'GET':
        msg, codeandmsg = checkForRequestGET(toarray)
        return msg, codeandmsg.encode()
    elif toarray[0] == 'POST':
        msg, codeandmsg = checkForRequestPOST(toarray)
        return msg, codeandmsg.encode()
    else:
        # Method Not Allowed
        return ''.encode(), '405 Method Not Allowed\r\n'.encode()


def checkForRequestPOST(toarray):
    newArray = toarray[13:]
    toappend = ''
    error = ''
    for item in newArray:
        if re.match(r"^\s*((https?|ftp|smtp)://)?(www\.)?[a-z0-9-.]+\.[a-z]+(/[a-zA-Z0-9#-]+/?)*\s*:\s*A\s*$", item):
            cutted = item.split(':', 1)[0]
            ip = findIP(cutted)
            if ip != '':
                toappend += ip.decode()
            else:
                error = "404 Not Found\r\n"
                if item == newArray[-1] and toappend == '':
                    return ''.encode(), error + "\r\n"
        elif re.match(r"^\s*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s*:\s*PTR\s*$", item):
            cutted = item.split(':', 1)[0]
            ip = checkForPostIP(cutted)
            if ip != '':
                toappend += ip.decode()
            else:
                error = "404 Not Found\r\n"
                if item == newArray[-1] and toappend == '':
                    return ''.encode(), error + "\r\n"
        else:
            if error == '':
                error = '400 Bad Request\r\n'
            if item == newArray[-1] and toappend == '':
                return ''.encode(), error + "\r\n"
            pass

    return toappend.encode(), '200 OK'


def checkForPostIP(ip):
    try:
        getIP = socket.gethostbyaddr(ip)
        print(ip)
        print(getIP)
        getIP = ip + ':PTR=' + getIP[0] + "\r\n"
        return str.encode(getIP)
    except socket.error:
        return ''


def checkForRequestGET(toarray):
    if re.match(r"/resolve\?name=(\S)*&type=A\s*$", toarray[1]) or re.match(r"/resolve\?type=A&name=(\S)*\s*$", toarray[1]):
        cutted = toarray[1].partition('name=')[2].split('&', 1)[0]
        ip = findIP(cutted)
        if ip != '':
            return ip, '200 OK'
        else:
            return ''.encode(), "404 Not Found\r\n"
    else:
        # BAD REQUEST
        return ''.encode(), '400 Bad Request\r\n'


def findIP(string):
    cntrl = controlURL(string)
    if cntrl == 200:
        getIP = socket.gethostbyname(string)
        getIP = string + ':A=' + getIP + "\r\n"
        return str.encode(getIP)
    else:
        return ''


def controlURL(string):
    url = string
    a = urlparse(string)

    if a.netloc == '' and a.scheme == '':
        if string[0:3] != 'www':
            url = "http://www." + string
        else:
            url = "http://" + string
    try:
        urllib.request.urlopen(url)
    except urllib.error.HTTPError as e:
        return "404 Not Found\r\n"
    except urllib.error.URLError as e:
        return "404 Not Found\r\n"
    else:
        return 200


#################################
#                               #
#          LOCAL SERVER         #
#                               #
#################################
class HandleTCP(handler):
    def handle(self):
        self.data = self.request.recv(8192).strip()
        msg, codemsg = editRequestedString(self.data)
        if msg.decode() == '':
            self.request.sendall('HTTP/1.1 '.encode() + codemsg)
        else:
            self.request.sendall('HTTP/1.1 '.encode() + codemsg + '\r\n\r\n'.encode() + msg)


def StartServer():
    host, port = "localhost", 8080
    print("starting server on port {}!".format(port))
    with tcps((host, port), HandleTCP) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.shutdown()


#################################
#                               #
#          MAIN PROGRAM         #
#                               #
#################################
StartServer()
