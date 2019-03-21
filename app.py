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

IPs=[
    'http://3.80.248.156:5000/forward', # east-1: N. Virginia
    'http://18.191.54.158:5000/forward', # east-2: Ohio
    'http://52.53.226.185:5000/forward', # west-1: N. California
]

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
    if current_location == 'ohio':
        targets={(37.926868, -78.024902): IPs[0], (37.279518, -121.867905): IPs[2]} #map from coordinates to contact addresses
    elif current_location == 'ncali':
        targets={(37.926868, -78.024902): IPs[0], (40.358615, -82.706838): IPs[1]} #map from coordinates to contact addresses
    elif current_location == 'nvirg':
        targets={(40.358615, -82.706838): IPs[1], (37.279518, -121.867905): IPs[2]} #map from coordinates to contact addresses

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
    data['hop_number'] = int(request.form.get('hop_number'))
    data['body'] = request.form.get('body')
    data['dest_IP'] = request.form.get('dest_IP')
    data['dest_coord_lat'] = float(request.form.get('dest_coord_lat'))
    data['dest_coord_lng'] = float(request.form.get('dest_coord_lng'))

    if(data['hop_number'] == 1):
        # return "Will forward to EC2"
        print("sending message to destination: ", data['dest_IP'])
        #r=requests.get("http://172.22.148.144:8000")
        r = requests.get(data['dest_IP'], data=data)
        print("returned from requests.post")
        return make_success_response('success')

    else:
        # decrement hop_number. When hop_number equals 0, send to destination
        data['hop_number'] = int(request.form.get('hop_number')) - 1 # decrement data
        IP=get_next_hop_ip(tuple((data['dest_coord_lat'], data['dest_coord_lng'])), data['dest_IP'])
        print('sending to: ', IP)
        r = requests.post(IP, data=data)
        
        return make_success_response('success')     

if __name__ == '__main__':

    if len(sys.argv) == 1:
        print("Location required as command line arg. Exiting.")
        sys.exit()

    current_location = sys.argv[1]
    app.debug = False
    app.run(host='0.0.0.0', port=5000)
