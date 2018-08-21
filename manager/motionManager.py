# -*- coding: utf-8 -*-
#System
import os
import sys

#Syspaths
sys.path.insert(0, '/home/Desktop/Reworked Project')

#Project
from dataManager import DataManager
from motion import Motion
from flask import Blueprint, jsonify, request

#Scriptsetup
motion_api = Blueprint('motion_api', __name__)

class MotionManager:

    TEMPLATES_PATH = '/home/pi/Desktop/Reworked Project/templates/'
    __motions = dict()
    __motionFiles = dict()

    def __init__(self):
        pass

    #Ggf. automatisiert möglich?
    def initMotions(self):
        dm = DataManager()
        #Hier alle Devices intitialisieren
        oldPath = os.getcwd()
        try:
            os.chdir(self.TEMPLATES_PATH)
        except FileNotFoundError:
            print("Could not load Motions")
            return

        #For jede Geste
        for file in sorted(os.listdir()):
            filePath = os.getcwd() + "/" + file
            if os.path.isdir(filePath):
                continue

            motion = dm.getMotion(filePath)
            self.__motions[motion.getName()] = motion
            self.__motionFiles[motion.getName()] = file

        os.chdir(oldPath)

    def saveOrUpdateMotions(self, motions):
        for motion in motions:
            self.saveOrUpdateMotion(motion)

    def saveOrUpdateMotion(self, motion):
        dm = DataManager()

        #Prüfen ob die Motion existiert
        #Sie existiert wenn es eine MotionFile mit passendem
        #Namen gibt
        path = None
        if motion.getName() in self.getAllMotionFiles():
            path = self.TEMPLATES_PATH + self.getMotionFile(motion.getName())
        else:
            i = 0
            plainPath = self.TEMPLATES_PATH + 'template'
            while os.path.exists(plainPath + "%s.txt" % i):
                i = i + 1
            else:
                plainPath = plainPath + "%s.txt" % i

            if not os.path.exists(os.path.dirname(self.TEMPLATES_PATH)):
                os.makedirs(os.path.dirname(self.TEMPLATES_PATH))

            path = plainPath

        dm.saveMotion(motion, path)
        if motion.getName() not in __motions:
            __motions[motion.getName()] = motion
            __motionFiles[motion.getName()] = path

        print('Motion Saved or Updated')

    def getAllMotions(self):
        return self.__motions

    def getMotion(self, key):
        return self.__motions[key]

    def getAllMotionFiles(self):
        return self.__motionFiles

    def getMotionFile(self, key):
        return self.__motionFiles[key]

@motion_api.route('/motions', methods=['GET'])
def restGetAllMotions():
    mm = MotionManager()
    motions = mm.getAllMotions()
    dic = {'motions' : []}
    for motionName in motions:
        motionDic = dict()
        motion = mm.getMotion(motionName)
        motionDic['name'] = motion.getName()
        dic['motions'].append(motionDic)

    return jsonify(dic)
