import threading

class IPCMemory:

    #MotionDetector
    START_LEARNING = 'startLearning'
    START_RECOGNIZING = 'startRecognizing'

    #MotionListener
    RESET_ROTATION_SUM = 'resetRotationSum'
    
    #General
    SHUTDOWN = 'shutdown'
    NEW_MOTION = 'newMotion'

    __memory = []
    __lock = threading.Lock()

    def __init__(self):
        pass

    def put(self, cmd):
        self.__lock.acquire()
        self.__memory.append(cmd)
        self.__lock.release()

    def get(self, index):
        result = None
        self.__lock.acquire()
        result = self.__memory[index]
        self.__lock.release()
        return result

    def getLast(self):
        return self.get(self.getSize()-1)

    def getSize(self):
        result = None
        self.__lock.acquire()
        result = len(self.__memory)
        self.__lock.release()
        return result

    def clear(self):
        self.__lock.acquire()
        self.__memory = []
        self.__lock.release()
