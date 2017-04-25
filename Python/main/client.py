# -*- coding: utf-8 -*-
import sys, urllib, urllib2, json
import base64
url = 'http://localhost:8000'

data = {}


file_object = open('/home/haop/code/ReceiptOCR/test/6.jpg','rb')
try:
     tmp = file_object.read( )
finally:
     file_object.close( )

data['type']='text'
data['image'] = base64.b64encode(tmp)
data['text']='251901141001,10011820,69551628,1383'

decoded_data = urllib.urlencode(data)
req = urllib2.Request(url, data = decoded_data)


resp = urllib2.urlopen(req)
content = resp.read()
if(content):
    print(content)