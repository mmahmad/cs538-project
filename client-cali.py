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
import numpy as np
from scipy.spatial import KDTree
import os

IPs=[
    # 'http://54.162.60.73:5000/forward', # east-1: N. Virginia
    # 'http://18.218.55.58:5000/forward', # east-2: Ohio
    # 'http://54.67.121.201:5000/forward', # west-1: N. California
    'http://100.24.10.110:5000/forward', # N. Virginia
    'http://3.18.215.129:5000/forward', # Ohio
    'http://54.153.24.72:5000/forward' # N. California
]

DESTINATION_ADDRESS = 'http://34.209.245.219:8000' # AWS Oregon
DESTINATION_COORDINATES = tuple((43.812502, -120.672999)) # Oregon

# Building tree for for client
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
    # my_ip = os.popen('curl -s ifconfig.me').readline()
    # my_ip = 'http://' + my_ip + ':5000/forward'
    # targets = list(IPs) # copy IPs
    # targets.remove(my_ip) # remove my_ip
    # targets.insert(0, my_ip) # insert my IP at the 0th index
    targets=[
        IPs[0], # IP of current_node == N. Virginia
        IPs[1],
        IPs[2]
    # 'https://4zjoii2pzf.execute-api.us-east-1.amazonaws.com/default/relay_node',
    # 'https://b9tmd8ucbf.execute-api.us-east-2.amazonaws.com/default/relay_node',
    # 'https://puit2a7od4.execute-api.us-west-1.amazonaws.com/default/relay_node'
    ] #map from tree indices to contact addresses
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
#     targets={(37.926868, -78.024902): IPs[0], (40.358615, -82.706838): IPs[1], (37.279518, -121.867905): IPs[2]} #map from coordinates to contact addresses
#     bestkey=mycoordinate
#     for key in targets.keys():
#         if distance(key,destination)<distance(bestkey,destination):
#             bestkey=key
#     if bestkey!=mycoordinate:
#         return targets[bestkey]
#     else:
#         return destip

# def get_next_hop_ip():
#     return random.choice(IPs)

def make_success_response(message):
    return {
        'statusCode': 200,
        'body': json.dumps(message)
    }

def getFirstHop():
    # return IPs[random.randint(0, len(IPs)-1)]
    mycoordinate = geocoder.ip('me')
    return picktarget(tuple(mycoordinate.latlng), DESTINATION_COORDINATES, DESTINATION_ADDRESS, tree)

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

    # create tree
    # my_coords = geocoder.ip('me').latlng
    # tree_coords = [my_coords, [37.926868, -78.024902], [40.358615, -82.706838],[37.279518, -121.867905]] # [0] is my_coords, [1] is N. Virginia (local), [2] is Ohio, [3] is N. Cali.
    tree_coords = [[37.926868, -78.024902], [40.358615, -82.706838],[37.279518, -121.867905]] # [0] is my_coords, [1] is N. Virginia (local), [2] is Ohio, [3] is N. Cali.
    tree = build_tree(tree_coords) # [0] is N. Virginia (local), [1] is Ohio, [2] is N. Cali.

    for x in range(0,100):

        message = {}
        message['hop_number'] = 3
        message['dest_IP'] = DESTINATION_ADDRESS
        message['dest_coord_lat'] = DESTINATION_COORDINATES[0]
        message['dest_coord_lng'] = DESTINATION_COORDINATES[1]
        message['body'] = 'This is a message from Haseeb Wajid!'
        message['timestamp'] = float(time.time())
        r = requests.post('http://54.153.24.72:5000/forward', params=message)
        # sendMessage(message)

