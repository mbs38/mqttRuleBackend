import time
import paho.mqtt.client as mqtt
import signal
import sys

topics=[]
publisher=None
subscriber=None

host=""
port=0

def init(h,p):
    global host
    global port
    host = h
    port = p
    
    global publisher
    publisher = Publisher(host,port)
    global subscriber
    subscriber = Subscriber(host,port)


def start():
    subscriber.connect()

class Subscriber:
    def __init__(self,host,port):
        self.clientid=None
        self.mqc=None
        self.host=host
        self.port=port
        self.topics=[]
        self.handlers=[]
        self.clientid="mqttRuleBackend-subscriber-"+ str(time.time())

    def addTopic(self,topic,handler):
        self.topics.append((topic,1))
        self.handlers.append((topic,handler))
    
    def connect(self):
        self.mqc=mqtt.Client(client_id=self.clientid)
        self.mqc.on_connect=self.connecthandler
        self.mqc.on_message=self.messagehandler
        self.mqc.on_log=self.on_log
        self.mqc.disconnected = True
        self.mqc.connect(self.host,self.port,60)
        self.mqc.loop_start()
        print("New client: "+self.clientid)
    
    def messagehandler(self,mqc,userdata,msg):
        payload=str(msg.payload.decode("utf-8"))
        topic=str(msg.topic)
        for t in self.handlers:
            if t[0] == topic:
                t[1](topic,payload)

    def connecthandler(self,mqc,userdata,flags,rc):
        self.mqc.subscribe(self.topics)
        print("Subscribing to: "+self.topics)

    def on_log(client, userdata, level, buff):
        print("log: ",buff)

class Publisher:
    def __init__(self,host,port):
        self.host=host
        self.port=port
        self.clientid="mqttRuleBackend-publisher-"+ str(time.time())
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

class Topic:
    def __init__(self,rule,topic,react_on):
        self.topic=topic
        self.react_on=react_on
        self.oldPayload=None
        global host
        global port
        self.host=host
        self.port=port
        self.rule=rule

        subscriber.addTopic(self.topic,self.messagehandler)

    def messagehandler(self,topic,payload):
        if self.react_on == "on_message":
            self.executeRule(payload,topic)
        else:
            if self.react_on.startswith("on_payload:"):
                stripped=self.react_on.lstrip("on_payload:")
                if payload == stripped:
                    self.executeRule(payload,topic)
            else:
                if self.react_on == "on_change":
                    if self.oldPayload is not None:
                        if self.oldPayload != payload:
                            self.executeRule(payload,topic)
                        self.oldPayload=payload
                    else:
                        self.oldPayload=payload
        
    def executeRule(self,payload,topic):
        try:
            self.rule(payload,topic)
        except Exception as e:
            print("Error when executing rule: "+str(e))


class State:
    def __init__(self,topic):
        self.topic=topic
        self.state=""

        subscriber.addTopic(self.topic,self.messagehandler)
        
    def messagehandler(self,topic,payload):
        self.state=payload

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


 
