import json
import requests
import random
import math


IPs=[
    'https://4zjoii2pzf.execute-api.us-east-1.amazonaws.com/default/relay_node',
    'https://b9tmd8ucbf.execute-api.us-east-2.amazonaws.com/default/relay_node',
    'https://puit2a7od4.execute-api.us-west-1.amazonaws.com/default/relay_node',
]

deg deg2rad(degrees):
    return (degrees*math.pi)/180
def distance(p1,p2): #(latitude,longitude) tuples
    earthradius=6371
    deglat=(p2[0]-p1[0])
    deglong=(p2[1]-p1[1])
    p1=deg2rad(p1[0])
    p2=deg2rad(p2[0])
    a=(math.sin(deglat/2)**2)+((math.sin(deglong/2)**2)*math.cos(p1[0])*math.cos(p2[0]))
    c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))
    return earthradius*c
def picktarget(mycoordinate,destination,destip):
    targets={(37.926868, -78.024902):'https://4zjoii2pzf.execute-api.us-east-1.amazonaws.com/default/relay_node',(40.358615, -82.706838):'https://b9tmd8ucbf.execute-api.us-east-2.amazonaws.com/default/relay_node',(37.279518, -121.867905):'https://puit2a7od4.execute-api.us-west-1.amazonaws.com/default/relay_node'} #map from coordinates to contact addresses
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
        'body': json.dumps(message),
    }


# In: event
# Out: Dict containing: hop_number, message
def get_data_from_event(event):
    print("event: ", event)
    # ev=event['queryStringParameters']
    ev=event
    return {'hop_number':ev['hop_number'],'message':ev['message'], 'dest_IP':ev['dest_IP']}

def lambda_handler(event, context):
    data = get_data_from_event(event)
    
    if data['hop_number']==1:
        print("sending message to destination: ", data['dest_IP'])
        #r=requests.get("http://172.22.148.144:8000")
        r = requests.get(data['dest_IP'], data=data)
        print("returned from requests.post")
        return make_success_response('success')

    # decrement hop_number. When hop_number equals 0, send to destination
    data['hop_number']-=1
    IP=get_next_hop_ip()
    print('sending to: ', IP)
    r = requests.post(IP, data=data)
    
    return make_success_response('success')




# import math
# deg deg2rad(degrees):
#     return (degrees*math.pi)/180
# def distance(p1,p2): #(latitude,longitude) tuples
#     earthradius=6371
#     deglat=(p2[0]-p1[0])
#     deglong=(p2[1]-p1[1])
#     p1=deg2rad(p1[0])
#     p2=deg2rad(p2[0])
#     a=(math.sin(deglat/2)**2)+((math.sin(deglong/2)**2)*math.cos(p1[0])*math.cos(p2[0]))
#     c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))
#     return earthradius*c
# def picktarget(mycoordinate):
#     targets={} #map from coordinates to contact addresses
#     #bestkey=firsttarget
#     for key in targets.keys():
#         if distance(mycoordinate,key)<distance(mycoordinate,bestkey):
#             bestkey=key
#     return targets[bestkey]

