'''
Client-side application:

1) Choose any of the EC2 instances
2) Send a message that includes:
    - destination
    - hop_count
3) Wait for reply
'''

import random
import json
import urllib
import urllib.request
import requests
import math
import geocoder

IPs = [
    'http://3.80.248.156:5000/forward', # east-1: N. Virginia
    'http://18.191.54.158:5000/forward', # east-2: Ohio
    'http://52.53.226.185:5000/forward', # west-1: N. California
]

DESTINATION_ADDRESS = 'http://34.216.219.153:8000' # AWS Oregon
DESTINATION_COORDINATES = (43.812502, -120.672999) # Oregon

def deg2rad(degrees):
    return (degrees*math.pi)/180

def distance(p1,p2): #(latitude,longitude) tuples
    earthradius=6371
    deglat=(p2[0]-p1[0])
    deglong=(p2[1]-p1[1])
    a=(math.sin(deglat/2)**2)+((math.sin(deglong/2)**2)*math.cos(p1[0])*math.cos(p2[0]))
    c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    return earthradius*c

def picktarget(mycoordinate,destination,destip):
    targets={(37.926868, -78.024902): IPs[0], (40.358615, -82.706838): IPs[1], (37.279518, -121.867905): IPs[2]} #map from coordinates to contact addresses
    bestkey=mycoordinate
    for key in targets.keys():
        if distance(key,destination)<distance(bestkey,destination):
            bestkey=key
    if bestkey!=mycoordinate:
        return targets[bestkey]
    else:
        return destip

def get_next_hop_ip():
    return random.choice(IPs)

def make_success_response(message):
    return {
        'statusCode': 200,
        'body': json.dumps(message)
    }

def getFirstHop():
    # return IPs[random.randint(0, len(IPs)-1)]
    mycoordinate = geocoder.ip('me')
    return picktarget(tuple(mycoordinate.latlng), DESTINATION_COORDINATES, DESTINATION_ADDRESS)

def sendMessage(message):
    firstHop = getFirstHop()
    print("firstHop: ")
    print(firstHop)
    # getRequestParamURL = '?hop_count=2' + '&' + 'dest=' + message['dest'] + '&' + 'body=' + message['body']
    # m = DESTINATION_ADDRESS + '/?' + urllib.parse.urlencode(message)
    # print(m)
    # contents = urllib.request.urlopen(m).read()
    # print(contents)
    r = requests.post(firstHop, data=message)
    print(r)



if __name__ == "__main__":
    message = {}
    message['hop_number'] = 2
    message['dest_IP'] = DESTINATION_ADDRESS
    message['dest_coord'] = DESTINATION_COORDINATES
    message['body'] = 'Hello World!'

    sendMessage(message)

