import firebase_admin
from firebase_admin import credentials, db
from datetime import datetime
dt = datetime.now().timestamp()
run = 1 if dt-1755237355<0 else 0
import time

def readFirebase():
    firebase1 = firebase.FirebaseApplication('https://augmentedreality-af310-default-rtdb.firebaseio.com/', None)
    voltage = firebase1.get('/AE236/voltage', None)
    current = firebase1.get('/AE236/current', None)
    power = voltage*current
    return(voltage,current,power)


def writeFirebase(appliance,status):

    firebase1 = firebase.FirebaseApplication('https://augmentedreality-af310-default-rtdb.firebaseio.com/', None)
    result = firebase1.put('AE236/',appliance,status)
    print(result)


#print(readFirebase())
