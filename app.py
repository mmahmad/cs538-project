from flask import Flask, request, jsonify, abort
import json
import requests
import random
import math
import geocoder
import sys
import click

app = Flask(__name__)

current_location = None # set in main() from cmd-line arg
targets = {}

# IPs=[
#     'http://34.204.74.243:5000/forward', # east-1: N. Virginia
#     'http://13.58.203.246:5000/forward', # east-2: Ohio
#     'http://54.215.188.3:5000/forward', # west-1: N. California
    
#     'http://35.166.131.254:5000/forward', # Oregon
#     'http://13.232.9.79:5000/forward', # Mumbai
#     'http://13.125.255.243:5000/forward', # Seoul
#     'http://54.255.237.155:5000/forward', # Singapore
#     'http://54.252.137.172:5000/forward', # Sydney
#     'http://13.114.92.252:5000/forward', # Tokyo
#     'http://35.183.35.149:5000/forward', # Central Canada
#     'http://18.197.144.127:5000/forward', # Frankfurt
#     'http://34.244.33.202:5000/forward', # Ireland
#     'http://35.178.94.52:5000/forward', # London
#     'http://52.47.145.82:5000/forward', # Paris
#     'http://13.53.38.55:5000/forward', # Stockholm
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
    "nvirg": (37.9821704,-81.7696267),
    "ncali": (38.8120855,-124.5556146),
    "ohio": (40.3436035,-84.9124752),
    "oregon": (44.1234992,-122.8263855),
    "mumbai": (19.0821978,72.7410999),
    "seoul": (37.5650172,126.8494656),
    "singapore": (1.3139961,103.7041632),
    "sydney": (-33.847927,150.6517866),
    "tokyo": (35.5040536,138.6486313),
    "canada": (50.8325132,-130.1073912),
    "frankfurt": (50.1211277,8.4964811),
    "ireland": (53.3942356,-10.1983315),
    "london": (51.5285582,-0.2416811),
    "paris": (48.8588377,2.2770203),
    "stockholm": (59.3260668,17.8419713)
}

def getTargets():

    # using the current_location, get coords of all other locations
    coords = [v for k,v in coordinateMapping.items() if k != current_location]
    print("coords:") 
    print(coords)

    # for each coords, add {coord: ip} in targets
    for coord in coords:
        # get ip from ipTable
        ip = IpTable[coord]
        targets[coord] = ip

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
    # targets={(37.926868, -78.024902): IPs[0], (40.358615, -82.706838): IPs[1], (37.279518, -121.867905): IPs[2]} #map from coordinates to contact addresses
    # if current_location == 'ohio':
    #     targets={(37.926868, -78.024902): IPs[0], (37.279518, -121.867905): IPs[2]} #map from coordinates to contact addresses
    # elif current_location == 'ncali':
    #     targets={(37.926868, -78.024902): IPs[0], (40.358615, -82.706838): IPs[1]} #map from coordinates to contact addresses
    # elif current_location == 'nvirg':
    #     targets={(40.358615, -82.706838): IPs[1], (37.279518, -121.867905): IPs[2]} #map from coordinates to contact addresses

    bestkey=mycoordinate
    for key in targets.keys():
        if distance(key,destination)<distance(bestkey,destination):
            bestkey=key
    if bestkey!=mycoordinate:
        return targets[bestkey]
    else:
        return destip

def get_next_hop_ip(dest_coord, dest_IP):
    mycoordinate = geocoder.ip('me')
    return picktarget(tuple(mycoordinate.latlng), dest_coord, dest_IP)

def make_success_response(message):
    return json.dumps({
        'statusCode': 200,
        'body': message
    })


@app.route('/')
def index():
    return "Hello World!"

@app.route('/forward', methods=['POST'])
def forward():
    data = {}
    data['hop_number'] = int(request.args.get('hop_number'))
    data['body'] = request.args.get('body')
    data['dest_IP'] = request.args.get('dest_IP')
    data['dest_coord_lat'] = float(request.args.get('dest_coord_lat'))
    data['dest_coord_lng'] = float(request.args.get('dest_coord_lng'))
    data['timestamp'] = float(request.args.get('timestamp'))

    if(data['hop_number'] == 1):
        print("hop_number=1")
        sendToDestination(data)

    else:
        # decrement hop_number. When hop_number equals 0, send to destination
        data['hop_number'] = int(request.args.get('hop_number')) - 1 # decrement data
        IP=get_next_hop_ip(tuple((data['dest_coord_lat'], data['dest_coord_lng'])), data['dest_IP'])

        '''
        If the current node is closest to the destination, send message to dest directly instead of sending
        to a relay node.
        Else, send to closest node.
        '''
        if IP == data['dest_IP']:
            sendToDestination(data)
        else:
            print('sending to: ', IP)
            r = requests.post(IP, params=data)
        
    return make_success_response('success')

'''
GET request to destination server
'''
def sendToDestination(data):
    print("sending message to destination: ", data['dest_IP'])
    r = requests.get(data['dest_IP'], params=data)
    print(r)

if __name__ == '__main__':

    cities = [k for k,v in coordinateMapping.items()]

    if len(sys.argv) == 1 or sys.argv[1] not in cities:
        print("Exiting. Location required as command line arg:")
        print(cities)
        sys.exit()

    current_location = sys.argv[1]
    getTargets() # set targets array
    app.debug = False
    app.run(host='0.0.0.0', port=5000)
