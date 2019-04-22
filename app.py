from flask import Flask, request, jsonify, abort
import json
import requests
import random
import math
import geocoder
import sys
import click
import numpy as np
from scipy.spatial import KDTree
import os

app = Flask(__name__)

current_location = None # set in main() from cmd-line arg

IPs=[
    # 'http://54.162.60.73:5000/forward', # east-1: N. Virginia
    # 'http://18.218.55.58:5000/forward', # east-2: Ohio
    # 'http://54.67.121.201:5000/forward', # west-1: N. California
    'http://100.24.10.110:5000/forward', # N. Virginia
    'http://3.18.215.129:5000/forward', # Ohio
    'http://54.153.24.72:5000/forward' # N. California
]

# Building tree for For current_node == N. Virginia
tree = None # set in main()

def sphere2cart(r,phi,theta):
    #x=r sin phi cos theta
    #y= r sin phi sin theta
    #z= r cos phi
    x=r*math.sin(phi)*math.cos(theta)
    y=r*math.sin(phi)*math.sin(theta)
    z=r*math.cos(phi)
    return (x,y,z)
def build_tree(coordinates):
    r=6400 #kilometres
    #latitude is (90 degrees - phi), longitude is theta
    data=np.zeros(shape=(len(coordinates),3),dtype=np.float)
    for i in range(len(coordinates)):
        latitude=coordinates[i][0]
        longitude=coordinates[i][1]
        data[i]=sphere2cart(r,math.radians(90-latitude),math.radians(longitude))
    print(data)
    tree=KDTree(data)
    return tree
def find_nearest(tree,coordinates):
    return tree.query(sphere2cart(6400,math.radians(90-coordinates[0]),math.radians(coordinates[1])))[1]
def picktarget(mycoordinate,destination,destip,tree):
    my_ip = os.popen('curl -s ifconfig.me').readline()
    my_ip = 'http://' + my_ip + ':5000/forward'
    targets = list(IPs) # copy IPs
    targets.remove(my_ip) # remove my_ip
    targets.insert(0, my_ip) # insert my IP at the 0th index
    # targets=[
    #     IPs[0], # IP of current_node == N. Virginia
    #     IPs[1],
    #     IPs[2]
    # # 'https://4zjoii2pzf.execute-api.us-east-1.amazonaws.com/default/relay_node',
    # # 'https://b9tmd8ucbf.execute-api.us-east-2.amazonaws.com/default/relay_node',
    # # 'https://puit2a7od4.execute-api.us-west-1.amazonaws.com/default/relay_node'
    # ] #map from tree indices to contact addresses
    nearest_idx=find_nearest(tree,destination)
    if nearest_idx==0:
        return destip
    else:
        return targets[nearest_idx]

# def deg2rad(degrees):
#     return (degrees*math.pi)/180

# def distance(p1,p2): #(latitude,longitude) tuples
#     earthradius=6371
#     deglat=(p2[0]-p1[0])
#     deglong=(p2[1]-p1[1])
#     a=(math.sin(deglat/2)**2)+((math.sin(deglong/2)**2)*math.cos(p1[0])*math.cos(p2[0]))
#     c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))
#     return earthradius*c

# def picktarget(mycoordinate,destination,destip):
#     # targets={(37.926868, -78.024902): IPs[0], (40.358615, -82.706838): IPs[1], (37.279518, -121.867905): IPs[2]} #map from coordinates to contact addresses
#     if current_location == 'ohio':
#         targets={(37.926868, -78.024902): IPs[0], (37.279518, -121.867905): IPs[2]} #map from coordinates to contact addresses
#     elif current_location == 'ncali':
#         targets={(37.926868, -78.024902): IPs[0], (40.358615, -82.706838): IPs[1]} #map from coordinates to contact addresses
#     elif current_location == 'nvirg':
#         targets={(40.358615, -82.706838): IPs[1], (37.279518, -121.867905): IPs[2]} #map from coordinates to contact addresses

#     bestkey=mycoordinate
#     for key in targets.keys():
#         if distance(key,destination)<distance(bestkey,destination):
#             bestkey=key
#     if bestkey!=mycoordinate:
#         return targets[bestkey]
#     else:
#         return destip

def get_next_hop_ip(dest_coord, dest_IP):
    mycoordinate = geocoder.ip('me')
    return picktarget(tuple(mycoordinate.latlng), dest_coord, dest_IP, tree)

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

    if len(sys.argv) == 1 or not (sys.argv[1] == 'nvirg' or sys.argv[1] == 'ncali' or sys.argv[1] == 'ohio'):
        print("Location required as command line arg (nvirg, ncali, or ohio). Exiting.")
        sys.exit()
    current_location = sys.argv[1]
    
    tree_coords = None # list of latlng coords. [0] must be current node's latlng
    if current_location == 'nvirg':
        tree_coords = [[37.926868, -78.024902], [40.358615, -82.706838],[37.279518, -121.867905]] # [0] is N. Virginia (local), [1] is Ohio, [2] is N. Cali.
    elif current_location == 'ncali':
        tree_coords = [[37.279518, -121.867905], [37.926868, -78.024902], [40.358615, -82.706838]] # [0] is N. Cali (local), [1] is N. Virginia, [2] is Ohio
    elif current_location == 'ohio':
        tree_coords = [[40.358615, -82.706838], [37.279518, -121.867905], [37.926868, -78.024902]] # [0] is Ohio (local), [1] is N. Cali, [2] is N. Virg
    # node_geocoordinates = geocoder.ip('me').latlng # returns [lat, lng] array
    
    tree = build_tree(tree_coords) # [0] is N. Virginia (local), [1] is Ohio, [2] is N. Cali.
    print("t")
    print(t)
    app.debug = False
    app.run(host='0.0.0.0', port=5000)
