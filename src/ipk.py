from socketserver import TCPServer as tcps
from socketserver import BaseRequestHandler as handler
import re
import sys
import socket
import urllib.request, urllib.error
from urllib.parse import urlparse


def editRequestedString(string):
    edited = string.decode()
    toarray = edited.split()
    if toarray[0] == 'GET':
        msg, codeandmsg = checkForRequestGET(toarray)
        return msg, codeandmsg.encode(), (toarray[2] + " ").encode()
    elif toarray[0] == 'POST':
        if toarray[1] != '/dns-query':
            return ''.encode(), '400 Bad Request\r\n\r\n'.encode(), (toarray[2] + " ").encode()
        toarray2 = ''
        try:
            toarray2 = edited.split("\r\n\r\n", 1)[1].replace(" ", "").split()
        except:
            return ''.encode(), '400 Bad Request\r\n\r\n'.encode(), (toarray[2] + " ").encode()
        msg, codeandmsg = checkForRequestPOST(toarray2)
        return msg, codeandmsg.encode(), (toarray[2] + " ").encode()
    else:
        return ''.encode(), '405 Method Not Allowed\r\n\r\n'.encode(), (toarray[2] + " ").encode()


def checkForRequestPOST(toarray):
    newArray = toarray
    toappend = ''
    error = ''
    for item in newArray:
        if re.match(r"^\s*\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\s*:\s*(PTR|A)\s*$", item):
            if re.match(r"^\s*(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\s*:\s*PTR\s*$", item):
                cutted = item.split(':', 1)[0]
                ip = checkForPostIP(cutted)
                if ip != '':
                    toappend += ip.decode()
                else:
                    if error == '':
                        error = "404 Not Found"
                    if item == newArray[-1] and toappend == '':
                        return ''.encode(), error + "\r\n\r\n"
            else:
                error = '400 Bad Request'
                if item == newArray[-1] and toappend == '':
                    return ''.encode(), error + "\r\n\r\n"
                pass
        elif re.match(r"^\s*(\S)*\s*:\s*A\s*$", item):
            cutted = item.split(':', 1)[0]
            ip = findIP(cutted)
            if ip != '':
                toappend += ip.decode()
            else:
                if error == '':
                    error = "404 Not Found"
                if item == newArray[-1] and toappend == '':
                    return ''.encode(), error + "\r\n\r\n"
        else:
            error = '400 Bad Request'
            if item == newArray[-1] and toappend == '':
                return ''.encode(), error + "\r\n\r\n"
            pass

    return toappend.encode(), '200 OK'


def checkForPostIP(ip):
    try:
        getIP = socket.gethostbyaddr(ip)
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
            return ''.encode(), "404 Not Found\r\n\r\n"
    else:
        # BAD REQUEST
        return ''.encode(), '400 Bad Request\r\n\r\n'


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
        return "404 Not Found\r\n\r\n"
    except urllib.error.URLError as e:
        return "404 Not Found\r\n\r\n"
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
        msg, codemsg, head = editRequestedString(self.data)
        if msg.decode() == '':
            self.request.sendall(head + codemsg)
            self.request.close()
        else:
            self.request.sendall(head + codemsg + '\r\n\r\n'.encode() + msg)
            self.request.close()


def StartServer():
    port = int(parseArgs())
    print("starting server on port {}!".format(port))
    tcps.allow_reuse_address = True
    with tcps(("localhost", port), HandleTCP) as server:
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.shutdown()
            server.server_close()


def parseArgs():
    if 0 <= int(sys.argv[1]) <= 65535:
        return sys.argv[1]
    else:
        sys.stderr.write('BAD PORT!\n')
        exit(1)


#################################
#                               #
#          MAIN PROGRAM         #
#                               #
#################################
StartServer()
