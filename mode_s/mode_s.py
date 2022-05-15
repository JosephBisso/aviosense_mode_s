# This Python file uses the following encoding: utf-8
import os
import sys
import argparse
from typing import Dict

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QUrl, QCoreApplication
from PySide6.QtWidgets import QApplication


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
    parser.add_argument("-it", "--interactive",
                        action="store_true", help="Whether the app should run interactively on the terminal", default=False)
    parser.add_argument("-v", "--verbose",
                        action="store_true", help="Whether the app should run only on the terminal", default=False)
    parser.add_argument("-la", "--latitude-minimal", metavar="latitude_minimal",
                        help="The desired minimal latitude. If not set, all available latitudes are evaluated")
    parser.add_argument("-LA", "--latitude-maximal",
                        help="The desired maximal latitude. If not set, all available latitudes are evaluated")
    parser.add_argument("-lo", "--longitude-minimal", metavar="longitude_minimal",
                        help="The desired minimal longitude. If not set, all available longitudes are evaluated")
    parser.add_argument("-LO", "--longitude-maximal",
                        help="The desired maximal longitude. If not set, all available longitudes are evaluated")
    parser.add_argument("-bd", "--bds",
                        help="The desired bds. If not set, all available bds are evaluated")
    parser.add_argument("-id", "--id-minimal", metavar="id_minimal",
                        help="The desired minimal id. If not set, all available ids are evaluated")
    parser.add_argument("-ID", "--id-maximal",
                        help="The desired maximal id. If not set, all available ids are evaluated")
    parser.add_argument("-l", "--limit",
                        help="The desired limit for the sql commmands. (default = 50000)", default=50000)
    parser.add_argument("-p", "--plots", nargs='*',
                        help="The desired plots. POSSIBLE VALUES: data_occurrences, bar_ivv, median_filtered, data_interval")

    return parser

def get_allArgs(args : Dict[str, str]) -> Dict[str, str]:
    params = {}
    
    for key in ["limit", "id_minimal", "id_maximal", "latitude_minimal", "latitude_maximal", "longitude_maximal", "longitude_minimal", "bds"]:
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
    
    # app = QGuiApplication(sys.argv) if not args.terminal else QCoreApplication(sys.argv)
    app = QApplication(sys.argv)
    
    logger = Logger(args.terminal, args.verbose)
    logger.debug(args)
    
    db = Database(logger)
    
    modes_engine = ModeSEngine.Engine(logger=logger)
        
    if not args.terminal:
        engine = QQmlApplicationEngine()
        engine.load(QUrl("qrc://qml/main.qml"))
        if not engine.rootObjects():
            sys.exit(-1)
        sys.exit(app.exec())
    else:
        db.setDefaultFilter(get_allArgs(args))
        db.actualizeData()
        modes_engine.setDataSet(db.getData())
        modes_engine.updateOccurrencesForAddresses(plot=True)
        sys.exit(0)
