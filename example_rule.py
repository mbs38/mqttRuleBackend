import ruleBackend
import time

#clientid=None
#mqc=None
host="localhost"
port=1883
ruleBackend.init(host,port)

#######################################################
# Welche states sollen zusätzlich verfügbar sein?
someBool1 = ruleBackend.State("modbus/sth/state")
someInt1 = ruleBackend.State("modbus/int/state")
# Achtung! Die types von den States sind immer String.

#######################################################
# Hier die Regeln definieren.

#eine globale Variable
zaehler = 1

def rule1(payload,topic):
    global zaehler
    print(topic+": "+payload)
    print("Rufe Regel 1 auf.")
    print("..und zwar zum "+str(zaehler)+" Mal!")
    zaehler = zaehler + 1

def rule2(payload,topic):
    print("Rufe Regel 2 auf.")
    print(topic+": "+payload)
    if zaehler > 4:
        print("1. Regel wurde schon mehr als 3 mal aufgerufen! Frechheit!")

def rule3(payload,topic):
    print("Rufe Regel 3 auf.")
    print(topic+": "+payload)


#######################################################
# Auf welche Topic soll welche Regel unter welchen
# Umständen reagieren?

#löst aus, wenn sich der Wert ändert
ruleBackend.topics.append(ruleBackend.Topic(rule1,"device/someCrap1/state","on_change"))
#löst aus, wenn irgendwas kommt auf der Topic
ruleBackend.topics.append(ruleBackend.Topic(rule2,"device/someCrap2/state","on_message"))
#löst aus, wenn eine Message kommt deren Payload 1234 ist.
ruleBackend.topics.append(ruleBackend.Topic(rule3,"device/someCrap3/state","on_payload:1234"))

#######################################################
# Zugreifen auf states:
while True:
    time.sleep(1)

    #print("State sth"+someBool1.state)
    #print("State int"+someInt1.state)
    #ruleBackend.publisher.send("modbus/blah/fasel","True")
