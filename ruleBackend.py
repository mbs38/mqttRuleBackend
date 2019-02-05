import time
import paho.mqtt.client as mqtt
import signal
import sys
import threading

topics=[]
publisher=None
subscriber=None
connected=None

def disconnecthandler(mqc,userdata,rc):
    print("Disconnected from broker")
    global connected
    connected = False

def init(host,port,user=None,password=None):
    global publisher
    publisher = Publisher(host,port,user,password)
    global subscriber
    subscriber = Subscriber(host,port,user,password)

def start():
    subscriber.connect()

class Subscriber:
    def __init__(self,host,port,user,pw):
        self.clientid=None
        self.mqc=None
        self.host=host
        self.port=port
        self.user=user
        self.pw=pw
        self.topics=[]
        self.handlers=[]
        self.clientid="mqttRuleBackend-subscriber-"+ str(time.time())

    def addTopic(self,topic,handler):
        self.topics.append((topic,1))
        self.handlers.append((topic,handler))
    
    def connect(self):
        self.mqc=mqtt.Client(client_id=self.clientid)
        if self.user is not None and self.pw is not None:
            self.mqc.username_pw_set(self.user,self.pw)
        self.mqc.on_connect=self.connecthandler
        self.mqc.on_disconnect=disconnecthandler
        self.mqc.on_message=self.messagehandler
        self.mqc.on_log=self.on_log
        self.mqc.disconnected = True
        self.mqc.connect(self.host,self.port,60)
        self.mqc.loop_start()
        global connected
        connected = True
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
    def __init__(self,host,port,user,pw):
        self.host=host
        self.port=port
        self.user=user
        self.pw=pw
        self.clientid="mqttRuleBackend-publisher-"+ str(time.time())
        print("New client: "+self.clientid)
        self.mqc=mqtt.Client(client_id=self.clientid)
        if self.user is not None and self.pw is not None:
            self.mqc.username_pw_set(self.user,self.pw)
        self.mqc.on_log=self.on_log
        self.mqc.disconnected = True
        self.mqc.on_disconnect=disconnecthandler
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
            sbl=threading.Thread(target=self.rule,args=(payload,topic))
            sbl.daemon = True
            sbl.start()
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



def signal_handler(signal, frame):
    print('Exiting ' + sys.argv[0])
    global connected
    connected = False

signal.signal(signal.SIGINT, signal_handler)
