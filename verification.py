#System
import threading

from ipc import IPCMemory

from events import BaseEvent, RotationEvent, ButtonEvent, TouchEvent
from events import EVENT_BASE, EVENT_ROTATE, EVENT_BUTTON, EVENT_TOUCH

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

    def run(self):
        print('Started Verification')
        self.startVerification()

    def startVerification(self):
        while True:
            self.checkSharedMemory()
            #Read bareSignals
            self.bareSignalsLock.acquire()
            if not self.bareSignalsCounter < len(self.bareSignals):
                self.bareSignalsLock.release()
                continue
            
            event = self.bareSignals[self.bareSignalsCounter]
            self.bareSignalsCounter = self.bareSignalsCounter + 1
            self.bareSignalsLock.release()

            #CheckIfItIsCorrect
            isValid = False
            if isinstance(event, RotationEvent) or isinstance(event, ButtonEvent) or isinstance(event, TouchEvent):
                isValid = True

            #Put it into queue or delete it
            if isValid:
                self.signalsLock.acquire()
                self.signals.append(event)
                self.signalsLock.release()

        self.cleanUp()

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
                print('A new Motion appeared')
                self.signalsLock.acquire()
                del self.signals[:]
                self.signalsLock.release()
                self.bareSignalsLock.acquire()
                del self.bareSignals[:]
                self.bareSignalsCounter = 0
                self.bareSignalsLock.release()

    def cleanUp(self):
        print('Verfication finished')
