import sys, urllib.request, urllib.error
try:
    urllib.request.urlopen("http://127.0.0.1:8000/")
except urllib.error.HTTPError as e:
    print(e.read().decode("utf-8"))
