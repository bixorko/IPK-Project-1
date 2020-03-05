import urllib.request, urllib.error
from urllib.parse import urlparse


url = 'http://www.stackoverflow.com/questis/1726402/in-pthon-how-do-i-use-urllib-to-see-ia-website-is-404-or-200'
a = urlparse(url)
print('Zadana url: ' + url)
print('NETLOC: ' + a.netloc)
print('PATH: ' + a.path)

if a.netloc == '' and a.scheme == '':
    if url[0:3] != 'www':
        url = "http://www." + url
    else:
        url = "http://" + url


try:
    conn = urllib.request.urlopen(url)
except urllib.error.HTTPError as e:
    print(e.code)
except urllib.error.URLError as e:
    print(e.reason)
else:
    print(conn.code)


