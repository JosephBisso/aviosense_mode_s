# This Python file uses the following encoding: utf-8
import os
import sys
import argparse

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
import PySide6.QtCore as qtcore

sys.path.append(os.getcwd())
import qml.qrc_qml

from logger import Logger
from database import Database
import engine as ModeSEngine

# Initialize argparse
def init_argparse():
    parser = argparse.ArgumentParser(
        description="Framework for automatic Mode-S data tranfer and turbulence prediction."
    )    
    parser.add_argument("-t", "--terminal",
                        action="store_true", help="Whether the app should run only on the terminal", default=False)
    parser.add_argument("-i", "--interactive",
                        action="store_true", help="Whether the app should run interactively on the terminal", default=False)
    parser.add_argument("-v", "--verbose",
                        action="store_true", help="Whether the app should run only on the terminal", default=False)
    parser.add_argument("-la", "--latitude",
                        help="The desired latitude. If not set, all available latitudes are evaluated")
    parser.add_argument("-lo", "--longitude",
                        help="The desired longitude. If not set, all available longitudes are evaluated")
    parser.add_argument("-bd", "--bds",
                        help="The desired bds. If not set, all available bds are evaluated")
    parser.add_argument("-l", "--limit",
                        help="The desired limit for the sql commmands. (default = 50000)", default=50000)

    return parser

def get_allArgs(args):
    params = {}
    
    for key in ["latitude", "longitude", "bds", "limit"]:
        if not args.interactive:
            if not getattr(args, key): continue
            params[key] = getattr(args, key)
        elif not getattr(args, key):
            userInput = input("Enter desired " + key + "(-1 for none):")
            if userInput == -1: continue
            params[key] = userInput
            
    return params

if __name__ == "__main__":
    args = init_argparse().parse_args()
    if args.interactive: args.terminal = True
    
    app = QGuiApplication(sys.argv)
    
    logger = Logger(args.terminal, args.verbose)
    logger.debug(args)
    
    db = Database(logger)
    
    modes_engine = ModeSEngine.Engine()
        
    if not args.terminal:
        engine = QQmlApplicationEngine()
        engine.load(qtcore.QUrl("qrc://qml/main.qml"))
        if not engine.rootObjects():
            sys.exit(-1)
        sys.exit(app.exec())
    else:
        db.setFilter(get_allArgs(args))
        db.actualizeData()
        sys.exit(0)
