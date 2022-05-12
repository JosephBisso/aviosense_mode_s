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

# Initialize argparse
def init_argparse():
    parser = argparse.ArgumentParser(
        description="Framework for automatic Mode-S data tranfer and turbulence prediction."
    )    
    parser.add_argument("-t", "--terminal",
                        action="store_true", help="Whether the app should run only on the terminal", default=True)
    parser.add_argument("-v", "--verbose",
                        action="store_true", help="Whether the app should run only on the terminal", default=False)
    parser.add_argument("-la", "--latitude",
                        help="The desired latitude. If not set, all available latitudes are evaluated")
    parser.add_argument("-lo", "--longitude",
                        help="The desired longitude. If not set, all available longitudes are evaluated")
    parser.add_argument("-bd", "--bds",
                        help="The desired bds. If not set, all available bds are evaluated")

    return parser


if __name__ == "__main__":
    args = init_argparse().parse_args()
    logger = Logger(args.terminal, args.verbose)
    logger.debug(args)
    
    app = QGuiApplication(sys.argv)
    
    db = Database()
    logger.info("Database connected") if db.isOpen() else logger.info("Database NOT connected")
    q = db.query("SELECT id, address, bds, altitude, latitude, longitude FROM tbl_mode_s WHERE latitude IS NOT NULL AND latitude IS NOT NULL LIMIT 10")
    if not q:
        logger.warning("Could not run query")
    else:
        result = db.getAll(["id", "address", "bds", "altitude", "latitude", "longitude"])
        logger.debug(result)
        
    if not args.terminal:
        engine = QQmlApplicationEngine()
        engine.load(qtcore.QUrl("qrc://qml/main.qml"))
        if not engine.rootObjects():
            sys.exit(-1)
        sys.exit(app.exec())
    else:
        sys.exit(0)
