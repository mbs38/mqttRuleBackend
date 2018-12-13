import time
import paho.mqtt.client as mqtt
import signal
import sys

topics=[]
publisher=None

host=""
port=0

def init(h,p):
    global host
    global port
    host = h
    port = p
    
    global publisher
    publisher = Publisher(host,port)

class Publisher:
    def __init__(self,host,port):
        self.host=host
        self.port=port
        self.clientid="Publisher-"+ str(time.time())
        print("New client: "+self.clientid)
        self.mqc=mqtt.Client(client_id=self.clientid)
        self.mqc.on_log=self.on_log
        self.mqc.disconnected = True
        self.mqc.connect(self.host,self.port,60)
        self.mqc.loop_start()    

    def on_log(client, userdata, level, buff):
        print("log: ",buff)

    def send(self,topic,payload):
        self.mqc.publish(topic,payload,qos=1,retain=False)
## I know that there is no need to create a new client for every subscription,
# but I'm too lazy to change it now... you can do so if you like to :D

class Topic:
    def __init__(self,rule,topic,react_on):
        self.topic=topic
        self.react_on=react_on
        self.clientid=None
        self.mqc=None
        self.oldPayload=None
        global host
        global port
        self.host=host
        self.port=port
        self.rule=rule

        self.clientid=self.topic+"-"+ str(time.time())
        print("New client: "+self.clientid)
        self.mqc=mqtt.Client(client_id=self.clientid)
        self.mqc.on_connect=self.connecthandler
        self.mqc.on_message=self.messagehandler
        self.mqc.on_log=self.on_log
        self.mqc.disconnected = True
        self.mqc.connect(self.host,self.port,60)
        self.mqc.loop_start()

    def messagehandler(self,mqc,userdata,msg):
        payload=str(msg.payload.decode("utf-8"))
        if self.react_on == "on_message":
            self.executeRule(payload)
        else:
            if self.react_on.startswith("on_payload:"):
                stripped=self.react_on.lstrip("on_payload:")
                if payload == stripped:
                    self.executeRule(payload)
            else:
                if self.react_on == "on_change":
                    if self.oldPayload is not None:
                        if self.oldPayload != payload:
                            self.executeRule(payload)
                        self.oldPayload=payload
                    else:
                        self.oldPayload=payload
        
    def connecthandler(self,mqc,userdata,flags,rc):
        print(self.topic)
        self.mqc.subscribe(self.topic)
        print("Subscribing to: "+self.topic)

    def on_log(client, userdata, level, buff):
        print("log: ",buff)

    def executeRule(self,payload):
        try:
            self.rule(payload)
        except Exception as e:
            print("Error when executing rule: "+str(e))


class State:
    def __init__(self,topic):
        self.topic=topic
        self.clientid=None
        self.mqc=None
        self.oldPayload=None
        global host
        global port
        self.host=host
        self.port=port
        self.state=""

        self.clientid="state_of"+"-"+self.topic+"-"+ str(time.time())
        print("New client: "+self.clientid)
        self.mqc=mqtt.Client(client_id=self.clientid)
        self.mqc.on_connect=self.connecthandler
        self.mqc.on_message=self.messagehandler
        self.mqc.on_log=self.on_log
        self.mqc.disconnected = True
        self.mqc.connect(self.host,self.port,60)
        self.mqc.loop_start()

    def messagehandler(self,mqc,userdata,msg):
        payload=str(msg.payload.decode("utf-8"))
        self.state=payload

    def connecthandler(self,mqc,userdata,flags,rc):
        print(self.topic)
        self.mqc.subscribe(self.topic)
        print("Subscribing to: "+self.topic)

    def on_log(client, userdata, level, buff):
        print("log: ",buff)

control=None

class Control:
    def __init__(self):
        self.runLoop = True
    def stopLoop(self):
        self.runLoop = False

def signal_handler(signal, frame):
        control.stopLoop()
        print('Exiting ' + sys.argv[0])
signal.signal(signal.SIGINT, signal_handler)

def run():
    global control
    control = Control()
    while control.runLoop:
        time.sleep(1)
    sys.exit(1)


 
