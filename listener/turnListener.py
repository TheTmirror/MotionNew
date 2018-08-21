# -*- coding: utf-8 -*-
#System
import threading
import sys
#Systempaths
sys.path.insert(0, '/home/pi/Desktop/Griffin')
sys.path.insert(0, '/home/pi/Desktop/Reworked Project')

#Project
from ipc import IPCMemory
from pypowermate import powermate
from decimal import Decimal, getcontext
from events import BaseEvent, RotationEvent, ButtonEvent
from events import EVENT_BASE, EVENT_ROTATE, EVENT_BUTTON

#Scriptsetup
getcontext().prec = 15
devicePath = '/dev/input/by-id/usb-Griffin_Technology__Inc._Griffin_PowerMate-event-if00'

class TurnListener(threading.Thread):
    
    def __init__(self, bareSignals, bareSignalsLock):
        threading.Thread.__init__(self)
        
        self.bareSignals = bareSignals
        self.bareSignalsLock = bareSignalsLock
        
        self.sm = IPCMemory()
        self.smCounter = 0
        
        self.knob = powermate.Powermate(devicePath)
    
    def run(self):
        print('Starting Listening Thread')
        self.startListening()
    
    def startListening(self):
        self.sum = 0
        
        while True:
            self.checkSharedMemory()

            pollResult = self.knob.read_event(0)
            if pollResult is None:
                continue
            
            (time, event, val) = pollResult
            time = Decimal('{}'.format(time)).normalize()
            val = Decimal('{}'.format(val)).normalize()

            if event == EVENT_ROTATE:
                self.sum = Decimal(self.sum) + val
                event = RotationEvent(time, val, self.sum)
            elif event == EVENT_BUTTON:
                event = ButtonEvent(time, val)

            self.bareSignalsLock.acquire()
            self.bareSignals.append(event)
            self.bareSignalsLock.release()

        self.cleanUp()

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
            elif message == IPCMemory.NEW_MOTION:
                self.sum = 0

    def cleanUp(self):
        print('McListener wird beendet')
