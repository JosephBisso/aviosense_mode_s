import os
from datetime import datetime

os.system("color")

class colors:  # for colored print output
    ENDC = '\033[m'
    RED = '\033[31m'
    RED_BACK = '\033[41m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    CYAN = '\033[96m'

class Logger:
    def __init__(self, terminal = True, verbose = False):
        self.terminal = terminal
        self.verbose = verbose
        self.outputFile = os.path.join(os.getcwd(), "mode_s.log")
        
        if os.path.exists(self.outputFile):
                os.remove(self.outputFile)
        with open(self.outputFile, "w") as output:
            output.write(str(datetime.now()) + "\n")
            
    
    def debug(self, msg):
        with open(self.outputFile, "a") as output:
            output.write(str(datetime.now()) + ":: DEBUG\t::\t" + str(msg) + "\n")
            
        if self.verbose:
            print("DEBUG ::\t" + str(msg) + colors.ENDC)
            
    def info(self, msg):
        with open(self.outputFile, "a") as output:
            output.write(str(datetime.now()) + ":: INFO::\t" + str(msg) + "\n")

        if self.terminal:
            print(colors.CYAN + "INFO\t::\t" + str(msg) + colors.ENDC)
            
    def warning(self, msg):
        with open(self.outputFile, "a") as output:
            output.write(str(datetime.now()) + ":: WARNING ::\t" + str(msg) + "\n")

        if self.terminal:
            print(colors.YELLOW + "WARNING\t::\t" + str(msg) + colors.ENDC)
            
    def critical(self, msg, exception = Exception):
        with open(self.outputFile, "a") as output:
            output.write(str(datetime.now()) + ":: CRITICAL ::\t" + str(msg) + "\n")

        if self.terminal:
            print(colors.RED + "CRITICAL\t::\t" + str(msg) + colors.ENDC)
            
        raise exception(msg)
                
        
