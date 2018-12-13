import ruleLib
import time

#clientid=None
#mqc=None
host="localhost"
port=1883
ruleLib.init(host,port)

#######################################################
# Welche states sollen zusätzlich verfügbar sein?
someBool1 = ruleLib.State("modbus/sth/state")
someInt1 = ruleLib.State("modbus/int/state")
# Achtung! Die types von den States sind immer String.

#######################################################
# Hier die Regeln definieren.

#eine globale Variable
zaehler = 1

def rule1(payload):
    global zaehler
    print("Rufe Regel 1 auf.")
    print("..und zwar zum "+str(zaehler)+" Mal!")
    zaehler = zaehler + 1

def rule2(paylpad):
    print("Rufe Regel 2 auf.")
    if zaehler > 4:
        print("1. Regel wurde schon mehr als 3 mal aufgerufen! Frechheit!")

def rule3(payload):
    print("Rufe Regel 3 auf.")


#######################################################
# Auf welche Topic soll welche Regel unter welchen
# Umständen reagieren?

#löst aus, wenn sich der Wert ändert
ruleLib.topics.append(ruleLib.Topic(rule1,"device/someCrap1/state","on_change"))
#löst aus, wenn irgendwas kommt auf der Topic
ruleLib.topics.append(ruleLib.Topic(rule2,"device/someCrap2/state","on_message"))
#löst aus, wenn eine Message kommt deren Payload 1234 ist.
ruleLib.topics.append(ruleLib.Topic(rule3,"device/someCrap3/state","on_payload:1234"))

#######################################################
# Zugreifen auf states:
while True:
    time.sleep(1)
    print("State sth"+someBool1.state)
    print("State int"+someInt1.state)
    ruleLib.publisher.send("modbus/blah/fasel","True")
