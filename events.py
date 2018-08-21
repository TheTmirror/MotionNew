#System
import sys
#Systempaths
sys.path.insert(0, '/home/pi/Desktop/Griffin')
#Project
from pypowermate import powermate
#Scriptsetup
EVENT_BASE = 'base'
EVENT_ROTATE = powermate.Powermate.EVENT_ROTATE
EVENT_BUTTON = powermate.Powermate.EVENT_BUTTON
EVENT_TOUCH = 'touchEvent'
EVENT_ABOART = 'aboartEvent'

class BaseEvent:

    def __init__(self, time):
        global EVENT_BASE
        self.time = time
        self.event = EVENT_BASE

    def getTime(self):
        return self.time

    def getEvent(self):
        return self.event

    def __repr__(self):
        global EVENT_BASE
        return "Time: {}\nEvent: {}".format(self.time, EVENT_BASE)

class AboartEvent(BaseEvent):

    def __init__(self, time):
        global EVENT_ABOART
        BaseEvent.__init__(self, time)
        self.event = EVENT_ABOART

    def __repr__(self):
        global EVENT_ABOART
        return "Time: {}\nEvent: {}".format(self.time, EVENT_ABOART)

class TouchEvent(BaseEvent):

    def __init__(self, time, location, value):
        global EVENT_TOUCH
        BaseEvent.__init__(self, time)
        self.event = EVENT_TOUCH
        self.location = location
        self.value = value

    def getValue(self):
        return self.value

    def getLocation(self):
        return self.location

    def __repr__(self):
        return "Time: {}\nEvent: {}\nLocation: {}\nValue: {}".format(self.time, self.event, self.location, self.value)

class RotationEvent(BaseEvent):

    def __init__(self, time, value, sum):
        global EVENT_ROTATE
        BaseEvent.__init__(self, time)
        self.event = EVENT_ROTATE
        self.value = value
        self.sum = sum

    def getValue(self):
        return self.value

    def getSum(self):
        return self.sum

    def __repr__(self):
        return "Time: {}\nEvent: {}\nValue: {}\nSum: {}".format(self.time, self.event, self.value, self.sum)

class ButtonEvent(BaseEvent):

    def __init__(self, time, value):
        global EVENT_BUTTON
        BaseEvent.__init__(self, time)
        self.event = EVENT_BUTTON
        self.value = value

    def getValue(self):
        return self.value

    def __repr__(self):
        return "Time: {}\nEvent: {}\nValue: {}".format(self.time, self.event, self.value)
