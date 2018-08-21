# -*- coding: utf-8 -*-
#System
import threading
import sys
import serial
import time

#Project
from ipc import IPCMemory
from decimal import Decimal, getcontext
from events import BaseEvent, AboartEvent, TouchEvent
from events import EVENT_BASE, EVENT_ABOART, EVENT_TOUCH

#Scriptsetup
getcontext().prec = 15

class TouchListener(threading.Thread):

    usbPath = '/dev/ttyACM0'
    baudrate = 9600
    
    def __init__(self, bareSignals, bareSignalsLock):
        threading.Thread.__init__(self)
        self.bareSignals = bareSignals
        self.bareSignalsLock = bareSignalsLock

        self.sm = IPCMemory()
        self.smCounter = 0
        
        self.ser = serial.Serial(self.usbPath, self.baudrate)
        self.ser.flush()
    
    def run(self):
        print('TouchListener is running')
        self.startListening()

    def startListening(self):
        while True:
            self.checkSharedMemory()
            if(self.ser.inWaiting() <= 0):
                continue

            event = self.getEvent()

            if event == None:
                continue

            self.bareSignalsLock.acquire()
            self.bareSignals.append(event)
            self.bareSignalsLock.release()

        self.cleanUp()

    def getEvent(self):
        input = self.ser.readline()
        input = self.convertText(input)
            
        event = input[:input.find(';')]
        input = input[input.find(';')+1:]
        location = input[:input.find(';')]
        input = input[input.find(';')+1:]
        val = input[:input.find(';')]
        val = Decimal('{}'.format(val)).normalize()

        t = time.time()
        t = Decimal('{}'.format(t)).normalize()

        if event == EVENT_TOUCH:
            return TouchEvent(t, location, val)
        else:
            return None

    def convertText(self, text = None):
            text = text[:len(text)-2]
            text = text.decode('utf-8')
            return text

    def checkSharedMemory(self):
        import time
        if self.smCounter < self.sm.getSize():
            message = self.sm.get(self.smCounter)
            self.smCounter = self.smCounter + 1

            if message == IPCMemory.SHUTDOWN:
                print('I shall shutdown')
                time.sleep(2)
                self.cleanUp()
                sys.exit()

    def cleanUp(self):
        print('TouchListener wurde beendet')
