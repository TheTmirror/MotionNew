# -*- coding: utf-8 -*-
#System
import threading
import time

from ipc import IPCMemory
from decimal import Decimal, getcontext

from events import BaseEvent, RotationEvent, ButtonEvent, TouchEvent, AboartEvent
from events import EVENT_BASE, EVENT_ROTATE, EVENT_BUTTON, EVENT_TOUCH, EVENT_ABOART

getcontext().prec = 15

class Verification(threading.Thread):

    def __init__(self, bareSignals, bareSignalsLock, signals, signalsLock):
        threading.Thread.__init__(self)

        self.bareSignals = bareSignals
        self.bareSignalsLock = bareSignalsLock
        self.bareSignalsCounter = 0
        
        self.signals = signals
        self.signalsLock = signalsLock

        self.sm = IPCMemory()
        self.smCounter = 0

        self.currentTouches = 0

        #TouchCheckerStuff
        self.touchEventsMetaInfo = dict()
        self.threshhold = 0.2

        ###
        #Bachelorarbeit
        self.lastButton = None
        self.intTimeout = 0.5
        self.buttonTimeout = Decimal('{}'.format(self.intTimeout)).normalize()
        ###

    def run(self):
        print('Started Verification')
        self.startVerification()

    def startVerification(self):
        while True:
            self.checkSharedMemory()
            ###
            #Bachelorarbeit Auskommentiert!!! Muss wieder rein!!!
            #Braucht erstmal nur Rotation
            #self.updateObservedTouchEvents()
            ###
            #Read bareSignals
            self.bareSignalsLock.acquire()
            if not self.bareSignalsCounter < len(self.bareSignals):
                self.bareSignalsLock.release()
                continue
            
            event = self.bareSignals[self.bareSignalsCounter]
            self.bareSignalsCounter = self.bareSignalsCounter + 1
            self.bareSignalsLock.release()

            #Stromabbruch checken
            ###
            #Bachelorarbeit Auskommentiert!!! Muss wieder rein!!!
            #if isinstance(event, TouchEvent):
            #    self.observeTouchEvent(event)
            ###

            #CheckIfItIsCorrect
            isValid = False
            if isinstance(event, RotationEvent) or isinstance(event, ButtonEvent):# or isinstance(event, TouchEvent):
                isValid = True

            ###
            #Bachelorarbeit
            if isinstance(event, ButtonEvent) and isValid and event.value == 0:
                #print('New Button Event Release')
                if self.lastButton is None:
                    self.lastButton = event.getTime()
                    #print('Erstes Event')
                elif (Decimal('{}'.format(event.getTime())).normalize() - Decimal('{}'.format(self.lastButton)).normalize()) > self.buttonTimeout:
                    self.lastButton = event.getTime()
                    #print('Replaced Event')
                else:
                    #Es handelt sich um ein Doppelklick und ein Aboart Event muss generiert werden
                    #print('Removing')
                    aboartEvent = AboartEvent(time.time())
                    self.signalsLock.acquire()
                    self.signals.append(aboartEvent)
                    #print('Put aboart')
                    #print(self.signals)
                    self.signalsLock.release()
                    self.lastButton = None
                    continue
            ###

            #Put it into queue or delete it
            if isValid:
                self.addEvent(event)

            #GGF in einen eigenen Event Thread? Achtung: Auf die Reihenfolge
            #der Events dann achten. Nicht dass das Aboart Event for dem Touch
            #Event auftritt und das Touch Release Event somit dann verloren geht
            #self.touchedAreasAndAboartEvent(event)

        self.cleanUp()

    def touchedAreasAndAboartEvent(self, event):
        tmpCurrentTouches = self.currentTouches
        if isinstance(event, TouchEvent):
            #print(event.getValue())
            if event.getValue() == 0:
                self.currentTouches = self.currentTouches - 1
                if self.currentTouches == 0:
                    aboartEvent = AboartEvent(time.time())
                    self.signalsLock.acquire()
                    self.signals.append(aboartEvent)
                    self.signalsLock.release()
            else:
                self.currentTouches = self.currentTouches + 1

        if tmpCurrentTouches != self.currentTouches:
            print("Anzahl der berührten Flächen: {}".format(self.currentTouches))

    def addEvent(self, event):
        self.signalsLock.acquire()
        self.signals.append(event)
        self.signalsLock.release()

    def observeTouchEvent(self, event):
        subDic = None
        if event.getLocation() in self.touchEventsMetaInfo:
            subDic = self.touchEventsMetaInfo[event.getLocation()]
        else:
            subDic = {}
            subDic['lastEventValue'] = None
            subDic['event'] = None
            self.touchEventsMetaInfo[event.getLocation()] = subDic

        subDic['event'] = event
        #print('added')
            
    def updateObservedTouchEvents(self):
        for key in self.touchEventsMetaInfo:
            subDic = self.touchEventsMetaInfo[key]
            subDic['timeSinceLastEvent'] = Decimal(time.time()) - subDic['event'].getTime()

        for key in self.touchEventsMetaInfo:
            subDic = self.touchEventsMetaInfo[key]
            if subDic['timeSinceLastEvent'] > self.threshhold:
                if subDic['lastEventValue'] == None or subDic['lastEventValue'] != subDic['event'].getValue():
                    self.addEvent(subDic['event'])
                    self.touchedAreasAndAboartEvent(subDic['event'])
                    #print('finally')
                    subDic['lastEventValue'] = subDic['event'].getValue()
                    
    def checkSharedMemory(self):
        import time
        if self.smCounter < self.sm.getSize():
            message = self.sm.get(self.smCounter)
            self.smCounter = self.smCounter + 1

            if message == IPCMemory.SHUTDOWN:
                print('I shall shutdown')
                time.sleep(2)
                sys.exit()
            elif message == IPCMemory.NEW_MOTION:
                #print('A new Motion appeared')
                self.signalsLock.acquire()
                del self.signals[:]
                self.signalsLock.release()
                self.bareSignalsLock.acquire()
                del self.bareSignals[:]
                self.bareSignalsCounter = 0
                self.bareSignalsLock.release()

    def cleanUp(self):
        print('Verfication finished')

###
#Bachelorarbeit
if __name__ == '__main__':
    bareSignalsLock = threading.Lock()
    signalsLock = threading.Lock()
    bareSignals = []
    signals = []
    
    v = Verification(bareSignals, bareSignalsLock, signals, signalsLock)
    v.start()

    e1 = ButtonEvent(0, 1)
    e2 = ButtonEvent(1.8, 0)
    e3 = ButtonEvent(3.5, 1)
    e4 = ButtonEvent(3.7, 1)

    bareSignalsLock.acquire()
    bareSignals.append(e1)
    bareSignals.append(e2)
    bareSignals.append(e3)
    bareSignals.append(e4)
    bareSignalsLock.release()
###
