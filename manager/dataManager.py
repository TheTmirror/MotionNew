# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, '/home/pi/Desktop/Reworked Project')

from decimal import Decimal, getcontext
getcontext().prec = 15

from events import BaseEvent, RotationEvent, ButtonEvent, TouchEvent
from events import EVENT_BASE, EVENT_ROTATE, EVENT_BUTTON, EVENT_TOUCH

from motion import Motion
from deviceManager import DeviceManager

class DataManager:

    def __init__(self):
        pass

    def saveMotion(self, motion, path):
        f = open(path, 'w')

        f.write("Name:{};\n".format(motion.getName()))
        if motion.isDeviceAssigned():
            f.write("Device:{};\n".format(motion.getAssignedDevice().getName()))
        else:
            f.write("Device:{};\n".format(None))
        if motion.isFunctionAssigned():
            f.write("Function:{};\n".format(motion.getAssignedFunction().__name__))
        else:
            f.write("Function:{};\n".format(None))

        #String must always have form:
        #Time, Event, Location, Value, Sum
        for event in motion.getEvents():
            string = "Time:{};Event:{};".format(event.getTime(), event.getEvent())
            if isinstance(event, RotationEvent):
                string = string + "Location:{};Value:{};Sum:{};".format(None, event.getValue(), event.getSum())
            elif isinstance(event, ButtonEvent):
                string = string + "Location:{};Value:{};Sum:{};".format(None, event.getValue(), None)
            elif isinstance(event, TouchEvent):
                string = string + "Location:{};Value:{};Sum:{};".format(event.getLocation(), event.getValue(), None)
            else:
                raise NameError('Should not happen, just for safty')

            f.write(string + "\n")

        f.close()

    def getMotion(self, path):
        deviceManager = DeviceManager()
        f = open(path, 'r')

        motion = Motion()

        for line in f:
            if line[:len("Name")] == "Name":
                motion.setName(line[len("Name:"):line.find(";")])
                continue
            elif line[:len("Device")] == "Device":
                deviceName = line[len("Device:"):line.find(";")]
                if deviceName == 'None':
                    continue
                device = deviceManager.getDevice(deviceName)
                motion.assignDevice(device)
                continue
            elif line[:len("Function")] == "Function":
                functionName = line[len("Function:"):line.find(";")]
                if functionName == 'None':
                    continue
                device = motion.getAssignedDevice()
                function = getattr(device, functionName)
                motion.assignFunction(function)
                continue;
            
            time = line[line.find("Time:")+len("Time:"):line.find(";")]
            time = Decimal(time)
            line = line[line.find(";")+1:]
            event = line[line.find("Event:")+len("Event:"):line.find(";")]
            line = line[line.find(";")+1:]
            location = line[line.find("Location:")+len("Location:"):line.find(";")]
            line = line[line.find(";")+1:]
            if location == 'None':
                location = None
            value = line[line.find("Value:")+len("Value:"):line.find(";")]
            if value == 'None':
                value = None
            else:
                value = Decimal(value)
            line = line[line.find(";")+1:]
            sum = line[line.find("Sum:")+len("Sum:"):line.find(";")]
            if sum == 'None':
                sum = None
            else:
                sum = Decimal(sum)
            line = line[line.find(";"):]

            if event == EVENT_BASE:
                event = BaseEvent(time)
            elif event == EVENT_ROTATE:
                event = RotationEvent(time, value, sum)
            elif event == EVENT_BUTTON:
                event = ButtonEvent(time, value)
            elif event == EVENT_TOUCH:
                event = TouchEvent(time, location, value)

            motion.addEvent(event)

        return motion
