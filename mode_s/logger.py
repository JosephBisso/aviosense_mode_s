import os
from datetime import datetime

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

class Logger:
    def __init__(self, terminal = True, verbose = False, debug = False):
        self.terminal = terminal
        self.verbose = verbose
        self.debugging = debug
        self.outputFile = os.path.join(os.getcwd(), "mode_s.log")
        
        if os.path.exists(self.outputFile):
                os.remove(self.outputFile)
        with open(self.outputFile, "w") as output:
            output.write(str(datetime.now()) + ":: Starting MODE_S\n")
            
    
    def debug(self, msg):
        time = datetime.now()
        with open(self.outputFile, "a") as output:
            output.write(str(datetime.now()) + ":: DEBUG\t::\t" + str(msg) + "\n")
            
        if self.debugging:
            print(colors.VIOLET + "DEBUG\t:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: " + colors.ENDC + str(msg))
    
    def log(self, msg):
        time = datetime.now()
        with open(self.outputFile, "a") as output:
            output.write(str(datetime.now()) + ":: LOG\t::\t" + str(msg) + "\n")
            
        if self.terminal or self.verbose or self.debugging:
            print(colors.BLUE + "LOG\t:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: " + colors.ENDC + str(msg))

    def success(self, msg):
        time = datetime.now()
        with open(self.outputFile, "a") as output:
            output.write(str(datetime.now()) + ":: SUCCESS::\t" + str(msg) + "\n")
            
        if self.terminal:
            print(colors.GREEN + "SUCCESS\t:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: " + str(msg) + colors.ENDC)
            
    def info(self, msg):
        time = datetime.now()
        with open(self.outputFile, "a") as output:
            output.write(str(datetime.now()) + ":: INFO\t::\t" + str(msg) + "\n")

        if self.terminal:
            print(colors.CYAN + "INFO\t:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: " + str(msg) + colors.ENDC)
            
    def warning(self, msg):
        time = datetime.now()
        with open(self.outputFile, "a") as output:
            output.write(str(datetime.now()) + ":: WARNING::\t" + str(msg) + "\n")

        if self.terminal:
            print(colors.YELLOW + "WARNING\t:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: " + str(msg) + colors.ENDC)
            
    def critical(self, msg, exception = Exception):
        time = datetime.now()
        with open(self.outputFile, "a") as output:
            output.write(str(datetime.now()) + ":: CRITICAL::\t" + str(msg) + "\n")

        if self.terminal:
            print(colors.RED + "CRITICAL:: " + str(time.hour) + ":" + str(time.minute) + ":" + str(time.second) + " :: " + str(msg) + colors.ENDC)
            
        raise exception(msg)
                
        
