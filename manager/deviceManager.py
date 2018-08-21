# -*- coding: utf-8 -*-
from flask import Blueprint, jsonify, request
import threading

device_api = Blueprint('device_api', __name__)

class DeviceManager:

    __devices = dict()
    __lock = threading.Lock()

    def __init__(self):
        pass

    #Ggf. automatisiert möglich?
    def initDevices(self):
        #Hier alle Devices intitialisieren
        device = PhillipsHueLightBulb()
        device.connect()
        self.__lock.acquire()
        self.__devices[device.getName()] = device
        self.__lock.release()

        device = Door()
        device.connect()
        self.__lock.acquire()
        self.__devices[device.getName()] = device
        self.__lock.release()

    def getAllDevices(self):
        return self.__devices

    def getDevice(self, key):
        device = None
        self.__lock.acquire()
        device = self.__devices[key]
        self.__lock.release()
        return device

class Device:

    def __init__(self, name):
        self.setName(name)

    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

class PhillipsHueLightBulb(Device):

    def __init__(self):
        Device.__init__(self, type(self).__name__)
        self.setStatus('off')
        self.connectioNEstablished = False

    def getStatus(self):
        return self.status

    def setStatus(self, status):
        self.status = status

    def switch(self):
        if self.getStatus() == 'off':
            self.setStatus('on')
        else:
            self.setStauts('off')

    def isConnected(self):
        return self.connectionEstablished

    def connect(self):
        self.connectionEstablished = True

    def disconnect(self):
        self.connectionEstablished = False

    def getAllControllFunctions(self):
        functions = [self.switch.__name__]
        return functions

class Door(Device):

    def __init__(self):
        Device.__init__(self, type(self).__name__)
        self.setStatus('closed')
        self.connectionEstablished = False

    def getStatus(self):
        return self.status

    def setStatus(self, status):
        self.status = status

    def open(self):
        self.setStatus('open')

    def close(self):
        self.setStatus('closed')

    def isConnected(self):
        return self.connectionEstablished

    def connect(self):
        self.connectionEstablished = True

    def disconnect(self):
        self.connectionEstablished = False

    def getAllControllFunctions(self):
        functions = [self.open.__name__, self.close.__name__]
        return functions

@device_api.route("/init", methods = ['GET'])
def init():
    dm = DeviceManager()
    dm.initDevices()
    return "Devices wurden erfolgreich initialisiert"

@device_api.route("/devices", methods = ['GET'])
def restGetAllDevices():
    dm = DeviceManager()
    devices = dm.getAllDevices()
    dic = {'devices' : []}
    for deviceName in devices:
        deviceDic = dict()
        device = dm.getDevice(deviceName)
        deviceDic['name'] = device.getName()
        deviceDic['functions'] = device.getAllControllFunctions()
        dic['devices'].append(deviceDic)

    return jsonify(dic)

@device_api.route("/functions", methods = ['GET'])
def getFunctionsOfDevice():
    dm = DeviceManager()
    deviceName = request.args.get('deviceName')
    print("Device Name: {}".format(deviceName))
    device = dm.getDevice(deviceName)
    functions = device.getAllControllFunctions()
    result = {'functions':functions}
    return jsonify(result)
