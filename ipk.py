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
        return checkForRequestGET(toarray)
    elif toarray[0] == 'POST':
        checkForRequestPOST(toarray)
        return string
        # return checkForRequestPOST(toarray)
    else:
        # Method Not Allowed
        return '405 Method Not Allowed\r\n\r\n'.encode()


def checkForRequestPOST(toarray):
    newArray = toarray[13:]
    print(newArray)


def checkForRequestGET(toarray):
    if re.match(r"/resolve\?name=(\S)*&type=A\s*$", toarray[1]):
        cutted = re.search(r'/resolve\?name=(.*?)&type=A\s*$', toarray[1]).group(1)
        return findIP(cutted)
    else:
        # BAD REQUEST
        return '400 Bad Request\r\n\r\n'.encode()


def findIP(string):
    cntrl = controlURL(string)
    if cntrl == 200:
        getIP = socket.gethostbyname(string)
        getIP = string + ':A=' + getIP + "\n"
        return str.encode(getIP)
    else:
        return cntrl.encode()


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
        self.request.sendall(editRequestedString(self.data))


def StartServer():
    host, port = "localhost", 8080
    print("starting server on port {}!".format(port))
    with tcps((host, port), HandleTCP) as server:
        server.serve_forever()


#################################
#                               #
#          MAIN PROGRAM         #
#                               #
#################################
StartServer()
