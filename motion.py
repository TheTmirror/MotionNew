# -*- coding: utf-8 -*-
from events import BaseEvent, RotationEvent, ButtonEvent

class Motion:

    def __init__(self):
        self.events = None
        self.startTime = None
        self.endTime = None
        self.name = None
        self.assignedDevice = None
        self.assignedFunction = None

    #Wird dies überhaupt gebraucht?
    def isEmpty(self):
        if events != None and len(events) > 0:
            return False
        else:
            return True

    def setStartTime(self, time):
        self.startTime = time

    def getStartTime(self):
        return self.startTime

    def setEndTime(self, time):
        self.endTime = time

    def getEndTime(self):
        return self.endTime

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

    def setEvents(self, events):
        self.events = events

    def addEvent(self, event):
        if self.events == None:
            self.events = []

        self.events.append(event)

    def getEvents(self):
        return self.events

    def assignDevice(self, device):
        self.assignedDevice = device

    def isDeviceAssigned(self):
        return self.assignedDevice != None

    def getAssignedDevice(self):
        return self.assignedDevice

    def assignFunction(self, function):
        #Hier fehlt ein Check ob das zugeordnete Device
        #überhaupt die Funktion zur Verfügung stellt
        self.assignedFunction = function

    def isFunctionAssigned(self):
        return self.assignedFunction != None

    def getAssignedFunction(self):
        return self.assignedFunction

    #Wird diese überhaupt gebraucht?
    def equals(self, motion):
        eventsToCompare = motion.getEvents()

        if len(self.events) != len(eventsToCompare):
            return False

        for i in range(len(self.events)):
            if(self.events[i].getTime() != eventsToCompare[i].getTime()):
                return False
            if type (self.events[i]) != type(eventsToCompare[i]):
                return False
            if isinstance(self.events[i], BaseEvent):
                break
            if isinstance(self.events[i], RotationEvent):
                if self.events[i].getValue() != eventsToCompare[i].getValue():
                    return False
                if self.events[i].getSum() != eventsToCompare[i].getSum():
                    return False
            if isinstance(self.events[i], ButtonEvent):
                if self.events[i].getValue() != eventsToCompare[i].getValue():
                    return False

        return True

    def __repr__(self):
        return "Dies ist Motion {}".format(self.getName())
