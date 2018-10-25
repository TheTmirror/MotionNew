import threading
import sys
sys.path.insert(0, '/home/pi/Desktop/Reworked Project/manager')

from flask import Flask

from deviceManager import device_api
from motionManager import motion_api
from restHandler import device_handler_api


class RestServer(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.app = Flask(__name__)
        self.app.register_blueprint(device_api)
        self.app.register_blueprint(motion_api)
        self.app.register_blueprint(device_handler_api)

    def run(self):
        self.app.run(host='0.0.0.0')
