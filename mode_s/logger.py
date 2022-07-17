import os
from datetime import datetime
from PySide2.QtCore import *

os.system("color")

class colors:  # for colored print output
    ENDC = '\033[m'
    RED = '\033[31m'
    RED_BACK = '\033[41m'
    GREEN = '\033[92m'
    YELLOW = '\033[33m'
    BLUE = '\033[94m'
    VIOLET = '\033[95m'
    CYAN = '\033[96m'


class Logger(QObject):
    
    logged = Signal(str)
    
    def __init__(self, terminal = True, verbose = False, debug = False):
        super(Logger, self).__init__(None)
        self.terminal = terminal
        self.verbose = verbose
        self.debugging = debug
        self.outputFile = os.path.join(os.getcwd(), "mode_s.log")
        
        if os.path.exists(self.outputFile):
                os.remove(self.outputFile)
        with open(self.outputFile, "w") as output:
            output.write(str(datetime.now()) + ":: Starting MODE_S\n")
            
    
    def debug(self, *args):
        time = datetime.now()
        with open(self.outputFile, "a") as output:
            output.write(str(datetime.now()) + ":: DEBUG\t::\t" + " ".join([str(msg) for msg in args]) + "\n")
            
        if self.debugging:
            print(colors.VIOLET + "DEBUG\t:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: " + colors.ENDC, *args)
            # self.logged.emit("<p style='color:Violet;'>DEBUG\t: : " + str(time.hour) + ": " + str(time.minute) + ": " + str(time.second) + " : : " + " ".join([str(msg) for msg in args]) + "</p>\n")
    
    def log(self, *args):
        time = datetime.now()
        with open(self.outputFile, "a") as output:
            output.write(str(datetime.now()) + ":: LOG\t::\t" + " ".join([str(msg) for msg in args]) + "\n")
            
        if self.terminal or self.verbose or self.debugging:
            print(colors.BLUE + "LOG\t:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: " + colors.ENDC, *args)
        
        self.logged.emit("<p style='color:DodgerBlue;'>LOG\t: : " + str(time.hour) + ": " + str(time.minute) + ": " +
                         str(time.second) + " : : <i style='color:White;'>" + " ".join([str(msg) for msg in args]) + "</i></p>\n")

    def success(self, *args):
        time = datetime.now()
        with open(self.outputFile, "a") as output:
            output.write(str(datetime.now()) + ":: SUCCESS::\t" + " ".join([str(msg) for msg in args]) + "\n")
            
        if self.terminal or self.verbose:
            print(colors.GREEN + "SUCCESS\t:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: ", *args, colors.ENDC)
        
        self.logged.emit("<p style='color:greenyellow;'>SUCCESS: : " + str(time.hour) + ": " + str(time.minute) + ": " + str(time.second) + " : : " + " ".join([str(msg) for msg in args]) + "</p>\n")
            
    def info(self, *args):
        time = datetime.now()
        with open(self.outputFile, "a") as output:
            output.write(str(datetime.now()) + ":: INFO\t::\t" + " ".join([str(msg) for msg in args]) + "\n")

        if self.terminal or self.verbose:
            print(colors.CYAN + "INFO\t:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: ", *args, colors.ENDC)

        self.logged.emit("<p style='color:Cyan;'>INFO\t: : " + str(time.hour) + ": " + str(time.minute) + ": " + str(time.second) + " : : " + " ".join([str(msg) for msg in args]) + "</p>\n")
            
    def warning(self, *args):
        time = datetime.now()
        with open(self.outputFile, "a") as output:
            output.write(str(datetime.now()) + ":: WARNING::\t" + " ".join([str(msg) for msg in args]) + "\n")

        if self.terminal or self.verbose:
            print(colors.YELLOW + "WARNING\t:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: ", *args, colors.ENDC)
        
        self.logged.emit("<p style='color:Orange;'>WARNING: : " + str(time.hour) + ": " + str(time.minute) + ": " + str(time.second) + " : : " + " ".join([str(msg) for msg in args]) + "</p>\n")
        
            
    def critical(self, *args):
        time = datetime.now()
        with open(self.outputFile, "a") as output:
            output.write(str(datetime.now()) + ":: CRITICAL::\t" + " ".join([str(msg) for msg in args]) + "\n")

        if self.terminal or self.verbose:
            print(colors.RED + "CRITICAL:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: ", *args, colors.ENDC)
        
        self.logged.emit("<p style='color:Tomato;'>CRITICAL: : " + str(time.hour) + ": " + str(time.minute) + ": " + str(time.second) + " : : " + " ".join([str(msg) for msg in args]) + "</p>\n")
        