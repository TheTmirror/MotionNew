# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '/home/pi/Desktop/Updated Project/math')
from myMath import Interpolator, Calculator

from motion import Motion
from events import BaseEvent, RotationEvent, ButtonEvent, TouchEvent
from events import EVENT_BASE, EVENT_ROTATE, EVENT_BUTTON, EVENT_TOUCH

from decimal import Decimal, getcontext
getcontext().prec = 15

class MotionTransformer:

    def __init__(self):
        self.recordedRotations = []
        self.recordedButtons = []
        #self.recordedTouches = []
        self.touches = dict()

    def transformMotion(self, signals):
        self.signals = signals
        interpolator = Interpolator()
        n = 64

        startTime = None
        endTime = None
        
        for event in self.signals:
            if startTime == None:
                startTime = event.getTime()
            elif startTime > event.getTime():
                startTime = event.getTime()

            if endTime == None:
                endTime = event.getTime()
            elif endTime < event.getTime():
                endTime = event.getTime()
            
            
            if isinstance(event, RotationEvent):
                self.recordedRotations.append(event)
            elif isinstance(event, ButtonEvent):
                self.recordedButtons.append(event)
            elif isinstance(event, TouchEvent):
                #self.recordedTouches.append(event)

                if event.getLocation is None:
                    raise NameError('Hier ist ein Fehler aufgetreten')

                #Sort Touches by Locations
                if event.getLocation() not in self.touches:
                    self.touches[event.getLocation()] = []

                self.touches[event.getLocation()].append(event)
                
            else:
                pass

        if startTime is None or endTime is None:
            raise NotEnoughSignals()

        #Construct Motion
        transformedMotion = Motion()
        transformedMotion.setStartTime(startTime)
        transformedMotion.setEndTime(endTime)

        self.addNeutralValues(startTime, endTime)

        #print('ROTATIONS')
        #print(self.recordedRotations)
        #print('BUTTONS')
        #print(self.recordedButtons)
        #print('TOUCHES ARRAY')
        #print(self.recordedTouches)
        #print('TOUCHES DIC')
        #print(self.touches)
        #return
        
        #Rotation Part of Motion
        if len(self.recordedRotations) > 0:
            result = interpolator.linearInterpolation(self.recordedRotations, n)

            transformedTime = result[0]
            transformedSum = result[1]

            for i in range(len(transformedTime)):
                event = RotationEvent(transformedTime[i], None, transformedSum[i])
                transformedMotion.addEvent(event)
        else:
            print('Es wurde keine Rotation hinzugefügt')

        #Button Part of Motion
        if len(self.recordedButtons) > 0:
            result = interpolator.linearInterpolation(self.recordedButtons, n)

            transformedTime = result[0]
            transformedValue = result[1]
                    
            for i in range(len(transformedTime)):
                event = ButtonEvent(transformedTime[i], transformedValue[i])
                transformedMotion.addEvent(event)
        else:
            print('Es wurde kein Button hinzugefügt')
                
        #Touch Part of Motion
        for location in self.touches:
            touchEvents = self.touches[location]
            result = interpolator.linearInterpolation(touchEvents, n)

            transformedTime = result[0]
            transformedValue = result[1]

            for i in range(len(transformedTime)):
                event = TouchEvent(transformedTime[i], location, transformedValue[i])
                transformedMotion.addEvent(event)

        #Scaling and adjustment
        self.scaleMotion(transformedMotion)
        self.adjustValues(transformedMotion)
        
        return transformedMotion

    #Needed for alignment of time
    def addNeutralValues(self, startTime, endTime):
        if len(self.recordedRotations) > 0:
            if self.recordedRotations[0].getTime() != startTime:
                newEvent = RotationEvent(startTime, Decimal('0'), Decimal('0'))
                self.recordedRotations.insert(0, newEvent)
            if self.recordedRotations[len(self.recordedRotations)-1].getTime() != endTime:
                lastEvent = self.recordedRotations[len(self.recordedRotations)-1]
                newEvent = RotationEvent(endTime, (Decimal('-1') * lastEvent.getValue()).normalize(), Decimal('0'))
                self.recordedRotations.append(newEvent)

        if len(self.recordedButtons) > 0:
            if self.recordedButtons[0].getTime() != startTime:
                newEvent = ButtonEvent(startTime, Decimal('0'))
                self.recordedButtons.insert(0, newEvent)
            if self.recordedButtons[len(self.recordedButtons)-1].getTime() != endTime:
                newEvent = ButtonEvent(endTime, Decimal('0'))
                self.recordedButtons.append(newEvent)
                
        for location in self.touches:
            touchEvents = self.touches[location]
            if touchEvents[0].getTime() != startTime:
                newEvent = TouchEvent(startTime, location, Decimal('0'))
                touchEvents.insert(0, newEvent)
            if touchEvents[len(touchEvents)-1].getTime() != endTime:
                newEvent = TouchEvent(endTime, location, Decimal('0'))
                touchEvents.append(newEvent)

    #Die Rotation muss skaliert werden, da man sonst keine Basis
    #hat durch die man teilen kann. Siehe in den Notizen zu Vor- und
    #Nachteile der Skalierung
    def scaleMotion(self, motion):
        #Find Max RotationValue
        maxValue = None
        for event in motion.getEvents():
            if isinstance(event, RotationEvent):
                if maxValue == None:
                    maxValue = abs(event.getSum())
                elif maxValue < abs(event.getSum()):
                    maxValue = abs(event.getSum())

        #Wenn keine Rotation vorhanden war, dann muss/kann nicht
        #skaliert werden, da eh alle Werte = 0 sind.
        if maxValue is None:
            return
        else:
            for event in motion.getEvents():
                if isinstance(event, RotationEvent):
                    event.sum = event.sum * (Decimal('400') / maxValue)
                    event.sum = event.sum.normalize()

    #Zur Korrektur der Differenz der einzelnen Summen der Rotation
    #Nachdem diese Transformiert wurden
    def adjustValues(self, motion):
        rotationEvents = []
        
        for event in motion.getEvents():
            if isinstance(event, RotationEvent):
                rotationEvents.append(event)

        for i in range(len(rotationEvents)):
            if i == 0:
                rotationEvents[i].value = rotationEvents[i].getSum()
                rotationEvents[i].value = rotationEvents[i].value.normalize()
            else:
                rotationEvents[i].value = rotationEvents[i].getSum() - rotationEvents[i-1].getSum()
                rotationEvents[i].value = rotationEvents[i].value.normalize()

class NotEnoughSignals(Exception):
    pass
