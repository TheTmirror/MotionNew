#System
import threading
import sys

#System Paths
sys.path.insert(0, '/home/pi/Desktop/Reworked Project/manager')

from events import BaseEvent, RotationEvent, ButtonEvent, AboartEvent
from events import EVENT_BASE, EVENT_ROTATE, EVENT_BUTTON, EVENT_ABOART

from ipc import IPCMemory
from transformer import MotionTransformer

from motionManager import MotionManager

class Executioner(threading.Thread):

    def __init__(self, signals, signalsLock):
        threading.Thread.__init__(self)

        self.signals = signals
        self.signalsLock = signalsLock
        self.signalsCounter = 0

        self.sm = IPCMemory()
        self.smCounter = 0;

        self.motionManager = MotionManager()

    def run(self):
        print('Executioner is running')
        #Wenn keine Motions vorhanden sind
        if not self.motionManager.getAllMotions():
            self.startLearning()
        #self.startExecution()

    def startExecution(self):
        while True:
            self.checkSharedMemory()
            self.signalsLock.acquire()
            if not self.signalsCounter < len(self.signals):
                self.signalsLock.release()
                continue

            event = self.signals[self.signalsCounter]
            self.signalsCounter = self.signalsCounter + 1
            self.signalsLock.release()

            if isinstance(event, AboartEvent):
                self.signalsLock.acquire()
                signalsCopy = self.signals[:]
                self.signalsLock.release()

                self.sm.put(IPCMemory.NEW_MOTION)
            else:
                continue

            self.startRecognition()

    def startRecognition(self):
        pass

    def startLearning(self):
        #Send all Signals to reset Inputs
        self.sm.put(IPCMemory.NEW_MOTION)

        while True:
            self.checkSharedMemory()
            self.signalsLock.acquire()
            if not self.signalsCounter < len(self.signals):
                self.signalsLock.release()
                continue

            event = self.signals[self.signalsCounter]
            self.signalsCounter = self.signalsCounter + 1
            self.signalsLock.release()

            if isinstance(event, AboartEvent):
                self.signalsLock.acquire()
                signalsCopy = self.signals[:]
                self.signalsLock.release()

                self.transformAndSafeMotion(signalsCopy)
            else:
                continue

    def transformAndSafeMotion(self, signalsCopy):
        del signalsCopy[len(signalsCopy) - 1]

        transformer = MotionTransformer()
        transformer.transformMotion(signalsCopy)

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
                self.signalsCounter = 0
