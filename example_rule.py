import ruleBackend
import time

host="localhost"
port=1883
user = ""
password = ""
ruleBackend.init(host,port,user,password)
# if you need authentication change user and password accordingly

#######################################################
# Which states do you want to be available?
someBool1 = ruleBackend.State("modbus/sth/state")
someInt1 = ruleBackend.State("modbus/int/state")
# Attention: type of the states is always string
# One word on timing: If a rule and a state have the same topic,
# make sure you initialize the state before you initialize the rule
# (in this example line 11 and 12 before lines 46 to 50). Otherwise
# the state will be updated after the rule has been executed.

#######################################################
# Define the rules here:

# a global variable
zaehler = 1

def rule1(payload,topic):
    global zaehler
    print(topic+": "+payload)
    print("Calling rule 1")
    print("..for the "+str(zaehler)+" time")
    zaehler = zaehler + 1

def rule2(payload,topic):
    print("Calling rule 2")
    print(topic+": "+payload)
    if zaehler > 4:
        print("1. rule has been called "+zaehler+"times!")

def rule3(payload,topic):
    print("Calling rule 3")
    print(topic+": "+payload)


#######################################################
# set topics the rules will trigger on

#is triggered when the value changes
ruleBackend.topics.append(ruleBackend.Topic(rule1,"device/someCrap1/state","on_change"))
#is triggered whenever a new message arrives on the topic
ruleBackend.topics.append(ruleBackend.Topic(rule2,"device/someCrap2/state","on_message"))
#is triggered when the message payload is '1234'
ruleBackend.topics.append(ruleBackend.Topic(rule3,"device/someCrap3/state","on_payload:1234"))

#######################################################

ruleBackend.start()

#main loop
while ruleBackend.connected:
    time.sleep(1)

#how to use states 
    print("State sth: "+someBool1.state)
    print("State int: "+someInt1.state)
#how to send a message
    ruleBackend.publisher.send("device/dog/bark","True")
