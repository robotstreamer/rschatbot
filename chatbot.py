
import os
import asyncio
import websockets
import time
import argparse
import json
import _thread
import traceback
import subprocess
import urllib
import urllib.request


config = json.load(open('config.json'))

userID = "26"
requiredAmount = 3225

chatEndpoint = {'host': '184.72.15.121', 'port': 8765}
parser = argparse.ArgumentParser(description='robotstreamer chat bot')
commandArgs = parser.parse_args()




def jsonResponsePOST(url, jsonObject):

    print("json object to POST", jsonObject)

    params = json.dumps(jsonObject).encode('utf8')
    req = urllib.request.Request(url, data=params,
                             headers={'content-type': 'application/json'})
    response = urllib.request.urlopen(req)

    jsonResponse = json.loads(response.read())
    
    print("response:", jsonResponse)
   
    return jsonResponse
    

async def handleStatusMessagesWithRetry():

    while True:
        await handleStatusMessages()
        time.sleep(1)

    
        
async def handleStatusMessages():

    global mainWebsocket

    print("running handle status messages")

    url = 'ws://%s:%s' % (chatEndpoint['host'], chatEndpoint['port'])
    print("chat url:", url)

    async with websockets.connect(url) as websocket:

        mainWebsocket = websocket
    
        print("connected to service at", url)
        print("chat websocket object:", websocket)

        print("starting websocket.send")
        #await websocket.send(json.dumps({"type":"connect",
        #                                 "robot_id":1,
        #                                 "local_address":"1"}))

        while True:
            time.sleep(1)
        #    message = await websocket.recv()
        #    print("received message:", message)
            


async def handleUpdateMessages():                

    global mainWebsocket
    count = 0
    print("start update")
    while True:
            time.sleep(2)
            print("sending")
            j = jsonResponsePOST("http://robotstreamer.com:6001/v1/get_goal_funbits", {"user_id":userID})
            goalAmount = j['goal_funbits']

            if goalAmount > requiredAmount:
                goalMetText = " Goal met. NICE."
                delay = 59 * 55
            else:
                goalMetText = ""
                delay = 59 * 14

            print("delay:", delay)
                
            m = "RS Project Life " + str(int(goalAmount)) + " of " + str(requiredAmount) + " funbits for today. If we meet this daily, robotstreamer stays alive. " + goalMetText
            if count % 2 == 0:
                m = m + " "
            print("message to send:", m)
            await mainWebsocket.send(json.dumps({"message": m,
                                                                     "token": config['jwt_user_token']}))
            count += 1
            time.sleep(delay)

            

async def handleAdMessage(m, delay):                

    global mainWebsocket
    count = 0
    print("start update")
    while True:
            time.sleep(delay / 50.0)
                
            if count % 2 == 0:
                m = m + " "
            print("message to send:", m)
            await mainWebsocket.send(json.dumps({"message": m,
                                                                     "token": config['jwt_user_token']}))
            count += 1
            time.sleep(delay)
            

            
            
            
def start(fn, params):
        try:
                asyncio.new_event_loop().run_until_complete(fn(*params))
        except:
                print("error")
                traceback.print_exc()


def main():                

    print(commandArgs)
    print("starting threads")
    
    _thread.start_new_thread(start, (handleStatusMessages, ()))
    _thread.start_new_thread(start, (handleUpdateMessages, ()))
    _thread.start_new_thread(start, (handleAdMessage, ("RESCHEDULED HeidiCast! Wednesday April 4 at 7:30PM Pacific Time", 60 * 50)))
    _thread.start_new_thread(start, (handleAdMessage, ("Join us on Discord https://discord.gg/n6B7ymy", 60 * 56)))
    
    # wait forever
    while True:
        time.sleep(5)

                
if __name__ == '__main__':
    main()


