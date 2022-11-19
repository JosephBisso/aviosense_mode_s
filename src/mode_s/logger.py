import os
from datetime import datetime
import threading
from PySide2.QtCore import *
from mode_s.constants import LOGGER_CONSTANTS
import queue

os.system("color")

class colors:  # for colored print output
    ENDC = '\033[m'
    RED = '\033[31m'
    RED_BACK = '\033[41m'
    GREEN = '\033[92m'
    YELLOW = '\033[33m'
    BLUE = '\033[94m'
    BLUE_BACK = '\033[44m'
    VIOLET = '\033[95m'
    CYAN = '\033[96m'


class Logger(QObject):
    
    logged      = Signal(str)
    progressed  = Signal(str, str)
    
    def __init__(self, terminal = True, verbose = False, debug = False):
        super(Logger, self).__init__(None)
        self.terminal = terminal
        self.verbose = verbose
        self.debugging = debug     

        self.queue = queue.Queue()
        self.logPath = os.path.join(os.getcwd(), "mode_s.log")
        self.daemon = LoggerDaemon(self.queue, self.logPath)
        self.daemon.start()
        
        
    def printLogFullPath(self):
        self.log("Full Path:", self.logPath)        
    
    def debug(self, *args):
        time = datetime.now()
        msg = str(datetime.now()) + ":: DEBUG\t::\t" + " ".join([str(msg) for msg in args]) + "\n"
        self.queue.put(msg)
            
        if self.debugging:
            print(colors.VIOLET + "DEBUG\t:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: " + colors.ENDC, *args)
            # self.logged.emit("<p style='color:Violet;'>DEBUG\t: : " + str(time.hour) + ": " + str(time.minute) + ": " + str(time.second) + " : : " + " ".join([str(msg) for msg in args]) + "</p>\n")

        self.queue.join()
    
    def log(self, *args):
        time = datetime.now()
        msg = str(datetime.now()) + ":: LOG\t::\t" + " ".join([str(msg) for msg in args]) + "\n"            
        self.queue.put(msg)

        if self.terminal or self.verbose or self.debugging:
            print(colors.BLUE + "LOG\t:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: " + colors.ENDC, *args)
        
        self.logged.emit("<p style='color:DodgerBlue;'>LOG\t: : " + str(time.hour) + ": " + str(time.minute) + ": " +
                         str(time.second) + " : : <i style='color:White;'>" + " ".join([str(msg) for msg in args]) + "</i></p>\n")
        self.queue.join()

    def success(self, *args):
        time = datetime.now()
        msg = str(datetime.now()) + ":: SUCCESS::\t" + " ".join([str(msg) for msg in args]) + "\n"            
        self.queue.put(msg)

        if self.terminal or self.verbose:
            print(colors.GREEN + "SUCCESS\t:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: ", *args, colors.ENDC)
        
        self.logged.emit("<p style='color:greenyellow;'>SUCCESS: : " + str(time.hour) + ": " + str(time.minute) + ": " + str(time.second) + " : : " + " ".join([str(msg) for msg in args]) + "</p>\n")
        self.queue.join()


    def info(self, *args):
        if LOGGER_CONSTANTS.PROGRESS_BAR in args[0]:
            clean_args = args[0].replace(LOGGER_CONSTANTS.PROGRESS_BAR , "")
            self.progress(clean_args)
            return
        
        time = datetime.now()
        msg = str(datetime.now()) + ":: INFO\t::\t" + " ".join([str(msg) for msg in args]) + "\n"
        self.queue.put(msg)

            
        if self.terminal or self.verbose:
            print(colors.CYAN + "INFO\t:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: ", *args, colors.ENDC)

        self.logged.emit("<p style='color:Cyan;'>INFO\t: : " + str(time.hour) + ": " + str(time.minute) + ": " + str(time.second) + " : : " + " ".join([str(msg) for msg in args]) + "</p>\n")
        self.queue.join()


    def progress(self, *args):
        time = datetime.now()
        msg = str(datetime.now()) + ":: PROGRESS::\t" + LOGGER_CONSTANTS.PROGRESS_BAR + " " + " ".join([str(msg) for msg in args]) + "\n"            
        self.queue.put(msg)

        if self.terminal or self.verbose:
            print(colors.BLUE_BACK + "PROGRESS:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " ::", colors.ENDC, LOGGER_CONSTANTS.PROGRESS_BAR, *args)

        # self.logged.emit(f"<p style='background-color:DodgerBlue;'>PROGRESS: : {str(time.hour)}: {str(time.minute)}: {str(time.second)} : : <i style='color:White;'>" + " ".join([str(msg) for msg in args]) + "</i></p>\n")
        id_index = args[0].find("ID_")
        progressID = args[0][id_index:id_index + 6]
        self.progressed.emit(progressID, " ".join([str(msg) for msg in args]))
        self.queue.join()


    def warning(self, *args):
        time = datetime.now()
        msg = str(datetime.now()) + ":: WARNING::\t" + " ".join([str(msg) for msg in args]) + "\n"
        self.queue.put(msg)

        if self.terminal or self.verbose:
            print(colors.YELLOW + "WARNING\t:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: ", *args, colors.ENDC)
        
        self.logged.emit("<p style='color:Orange;'>WARNING: : " + str(time.hour) + ": " + str(time.minute) + ": " + str(time.second) + " : : " + " ".join([str(msg) for msg in args]) + "</p>\n")
        self.queue.join()

    
    def critical(self, *args):
        time = datetime.now()
        msg = str(datetime.now()) + ":: CRITICAL::\t" + " ".join([str(msg) for msg in args]) + "\n"
        self.queue.put(msg)

        if self.terminal or self.verbose:
            print(colors.RED + "CRITICAL:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: ", *args, colors.ENDC)
        
        self.logged.emit("<p style='color:Tomato;'>CRITICAL: : " + str(time.hour) + ": " + str(time.minute) + ": " + str(time.second) + " : : " + " ".join([str(msg) for msg in args]) + "</p>\n")
        self.queue.join()


class LoggerDaemon(threading.Thread):
    def __init__(self, q, logPath):
        threading.Thread.__init__(self, name="LoggerDaemon", daemon=True)
        self.q: queue.Queue = q
        self.outputFile = logPath

        with open(self.outputFile, "w") as output:
            output.write(str(datetime.now()) + ":: Starting MODE_S\n")

    def run(self):
        with open(self.outputFile, "a") as output:
            while True:
                msg = self.q.get()
                output.write(msg)
                output.flush()
                self.q.task_done()
                    