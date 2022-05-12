# This Python file uses the following encoding: utf-8
import os
from pathlib import Path
import sys
import argparse

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
import PySide6.QtCore as qtcore

sys.path.append("D:\\BA\\ba_mode-s_analysis")
import qml.qrc_qml

# Initialize argparse
def init_argparse():
    parser = argparse.ArgumentParser(
        description="Framework for automatic Mode-S data tranfer and turbulence prediction."
    )    
    parser.add_argument("-t", "--terminal",
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
    qtcore.qDebug(str(args))
    
    app = QGuiApplication(sys.argv)
    engine = QQmlApplicationEngine()
    engine.load(qtcore.QUrl("qrc://qml/main.qml"))
    if not engine.rootObjects():
        sys.exit(-1)
    sys.exit(app.exec())
