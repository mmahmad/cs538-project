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

ec2_instance_ips = [
    '1.1.1.1',
    '2.2.2.2',
    '3.3.3.3'
]

DESTINATION_ADDRESS = '34.219.21.138:8000'

def getFirstHop():
    return ec2_instance_ips[random.randint(0, len(ec2_instance_ips)-1)]

def sendMessage(message):
    firstHop = getFirstHop()
    # getRequestParamURL = '?hop_count=2' + '&' + 'dest=' + message['dest'] + '&' + 'body=' + message['body']
    m = DESTINATION_ADDRESS + '/?' + urllib.parse.urlencode(message)
    print(m)
    contents = urllib.request.urlopen(m).read()
    print(contents)
    # r = requests.post(DESTINATION, data=message)



if __name__ == "__main__":
    message = {}
    message['hop_count'] = 2
    message['dest'] = DESTINATION_ADDRESS
    message['body'] = 'Hello World!'

    sendMessage(message)

