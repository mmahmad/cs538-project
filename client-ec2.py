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
import time

# IPs = [
#     'http://54.162.60.73:5000/forward', # east-1: N. Virginia
#     'http://18.218.55.58:5000/forward', # east-2: Ohio
#     'http://54.67.121.201:5000/forward', # west-1: N. California
# ]

IpTable={
    (36.850947, -76.280997): 'http://3.82.49.118:5000/forward', # east-1: N. Virginia
    (39.961083, -82.998592): 'http://18.191.224.241:5000/forward', # east-2: Ohio
    (38.579675, -121.489587): 'http://13.57.252.78:5000/forward', # west-1: N. California
    
    (45.516595, -122.679850): 'http://34.217.13.95:5000/forward', # Oregon
    (19.082792, 72.883933): 'http://13.232.130.166:5000/forward', # Mumbai
    (37.553507, 126.986781): 'http://52.79.84.130:5000/forward', # Seoul
    (1.352437, 103.860736): 'http://13.229.251.105:5000/forward', # Singapore
    (-33.847927,150.6517866): 'http://13.239.12.200:5000/forward', # Sydney
    (35.5040536,138.6486313): 'http://54.95.11.194:5000/forward', # Tokyo
    (50.8325132,-130.1073912): 'http://99.79.31.193:5000/forward', # Central Canada
    (50.1211277,8.4964811): 'http://52.59.227.219:5000/forward', # Frankfurt
    (53.3942356,-10.1983315): 'http://18.203.161.211:5000/forward', # Ireland
    (51.5285582,-0.2416811): 'http://3.8.1.114:5000/forward', # London
    (48.8588377,2.2770203): 'http://35.180.100.8:5000/forward', # Paris
    (59.3260668,17.8419713): 'http://13.53.216.250:5000/forward', # Stockholm
}

coordinateMapping = {
    "nvirg": (36.850947, -76.280997),
    "ncali": (38.579675, -121.489587),
    "ohio": (39.961083, -82.998592),
    "oregon": (45.516595, -122.679850),
    "mumbai": (19.082792, 72.883933),
    "seoul": (37.553507, 126.986781),
    "singapore": (1.352437, 103.860736),
    "sydney": (-33.847927,150.6517866),
    "tokyo": (35.5040536,138.6486313),
    "canada": (50.8325132,-130.1073912),
    "frankfurt": (50.1211277,8.4964811),
    "ireland": (53.3942356,-10.1983315),
    "london": (51.5285582,-0.2416811),
    "paris": (48.8588377,2.2770203),
    "stockholm": (59.3260668,17.8419713)
}

#map from coordinates to contact addresses, initialized in main()
targets = {}
# targets={
#     (37.9821704,-81.7696267): IpTable[(37.9821704,-81.7696267)], 
#     (40.3436035,-84.9124752): IpTable[((40.3436035,-84.9124752))], 
#     (38.8120855,-124.5556146): IpTable[(38.8120855,-124.5556146)],
#     (44.1234992,-122.8263855): IpTable[(44.1234992,-122.8263855)],
#     (19.0821978,72.7410999): IpTable[(19.0821978,72.7410999)],
#     (37.5650172,126.8494656): IpTable[(37.9821704,-81.7696267)],
#     (1.3139961,103.7041632): IpTable[(37.9821704,-81.7696267)],
#     (-33.847927,150.6517866): IpTable[(37.9821704,-81.7696267)],
#     (35.5040536,138.6486313): IpTable[(37.9821704,-81.7696267)],
#     (50.8325132,-130.1073912): IpTable[(37.9821704,-81.7696267)],
#     (50.1211277,8.4964811): IpTable[(37.9821704,-81.7696267)],
#     (53.3942356,-10.1983315): IpTable[(37.9821704,-81.7696267)],
#     (51.5285582,-0.2416811): IpTable[(37.9821704,-81.7696267)],
#     (48.8588377,2.2770203): IpTable[(37.9821704,-81.7696267)],
#     (59.3260668,17.8419713): IpTable[(37.9821704,-81.7696267)]



# } 
# DESTINATION_ADDRESS = 'http://34.217.75.213:8000' # AWS Oregon
# DESTINATION_COORDINATES = tuple((43.812502, -120.672999)) # Oregon

DESTINATION_ADDRESS = 'http://40.74.78.170:8000' # Azure West Japan
DESTINATION_COORDINATES = tuple((35.5040536,138.6486313)) # Azure West Japan

def getTargets():

    # using the current_location, get coords of all other locations
    coords = [v for k,v in coordinateMapping.items()]

    # for each coords, add {coord: ip} in targets
    for coord in coords:
        # get ip from ipTable
        ip = IpTable[coord]
        targets[coord] = ip

def deg2rad(degrees):
    return (degrees*math.pi)/180

def distance(p1,p2): #(latitude,longitude) tuples
    earthradius=6371
    deglat=deg2rad(p2[0]-p1[0])
    deglong=deg2rad(p2[1]-p1[1])
    a=(math.sin(deglat/2)**2)+((math.sin(deglong/2)**2)*math.cos(deg2rad(p1[0]))*math.cos(deg2rad(p2[0])))
    c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    return earthradius*c

def picktarget(mycoordinate,destination,destip):
    # targets={(37.926868, -78.024902): IPs[0], (40.358615, -82.706838): IPs[1], (37.279518, -121.867905): IPs[2]} #map from coordinates to contact addresses
    # bestkey=mycoordinate
    bestkey=list(targets.keys())[0]
    print("my coordinate: ")
    print(mycoordinate)
    for key in targets.keys():
        print("key: " + str(key) + ", name: " + list(coordinateMapping.keys())[list(coordinateMapping.values()).index(key)])
        print("destination: ", destination)
        print("distance(key, destination): ", str(distance(key, destination)))
        # if distance(key,destination)<distance(bestkey,destination):
        #     bestkey=key
        if distance(mycoordinate, key) < distance(mycoordinate, bestkey):
            bestkey = key
    print("selected key: ")
    print(bestkey)
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
    print("my coordinate")
    print(mycoordinate)
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
    r = requests.post(firstHop, params=message)
    print(r)



if __name__ == "__main__":

    # initialize targets
    getTargets()


    # for x in range(0,100):
    message = {}
    message['hop_number'] = 3
    message['dest_IP'] = DESTINATION_ADDRESS
    message['dest_coord_lat'] = DESTINATION_COORDINATES[0]
    message['dest_coord_lng'] = DESTINATION_COORDINATES[1]
    message['body'] = 'This is a message from Haseeb Wajid!'
    message['timestamp'] = float(time.time())

    sendMessage(message)

