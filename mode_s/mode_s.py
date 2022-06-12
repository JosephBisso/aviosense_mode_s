# This Python file uses the following encoding: utf-8
import os
import sys
import argparse
import json
import concurrent.futures
from collections import namedtuple
from typing import Dict, NamedTuple


from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import *
from PySide6.QtGui import QGuiApplication


sys.path.append(os.getcwd())

from logger import Logger
from database import Database
from constants import *
import engine as ModeSEngine


# Initialize argparse
def init_argparse():
    parser = argparse.ArgumentParser(
        description="Framework for automatic Mode-S data transfer and turbulence prediction."
    )
    parser.add_argument("-t", "--terminal",
                        action="store_true", help="Whether the app should run only on the terminal", default=False)
    parser.add_argument("-it", "--interactive",
                        action="store_true", help="Whether the app should run interactively on the terminal", default=False)
    parser.add_argument("-v", "--verbose",
                        action="store_true", help="Whether the app should run only on the terminal", default=False)
    parser.add_argument("-d", "--debug",
                        action="store_true", help="Whether the app should run only on debug mode", default=False)
    parser.add_argument("--local",
                        action="store_true", help="Whether the app should should connect to local database", default=False)
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
                        help="The desired limit for the mysql commands. (default = 50000)", default=50000)
    parser.add_argument("-dl", "--duration-limit",
                        help="The desired flight duration limit in seconds for the analysis. (default = None)", default=None)
    parser.add_argument("-n", "--median-n",
                        help="The desired n for the median filtering. MUST BE ODD. (default: n=3)", default=1)
    parser.add_argument("-p", "--plots", nargs='*',
                        help="The desired plots. POSSIBLE VALUES: " + str(ENGINE_CONSTANTS.PLOTS), default=[])
    parser.add_argument("-pa", "--plot-addresses", nargs='*',
                        help="The addresses of the desired plots.", default=[])

    return parser


def getAllArgs(args: NamedTuple) -> Dict[str, str]:
    params = {}
    for key in ["limit", "id_minimal", "id_maximal", "latitude_minimal", "latitude_maximal", "longitude_maximal", "longitude_minimal", "bds"]:
        if not args.interactive:
            if not getattr(args, key):
                continue
            params[key] = getattr(args, key)
        elif not getattr(args, key):
            userInput = input("Enter desired " + key + "(-1 for none):")
            if userInput == -1:
                continue
            params[key] = userInput
    return params

def qt_message_handler(mode, context, message):
    if mode == QtMsgType.QtInfoMsg:
        logger.info(message)
    elif mode == QtMsgType.QtWarningMsg:
        logger.warning(message)
    elif mode == QtMsgType.QtCriticalMsg:
        logger.critical(message)
    elif mode == QtMsgType.QtFatalMsg:
        logger.critical(message)
    else:
        logger.debug(message)


class Mode_S(QObject):
    
    logged = Signal(str, arguments=['log'])
    computingStarted = Signal()
    computingFinished = Signal()
    filterUpdated = Signal()

    def __init__(self, db: Database, msEngine: ModeSEngine.Engine, logger: Logger):
        super(Mode_S, self).__init__(None)
        self.db = db
        self.engine = msEngine
        self.logger = logger
        logger.logged.connect(self.__log)
        self.filterUpdated.connect(self.compute)

    @Slot(str)
    def __log(self, log: str):
        self.logged.emit(log)
    
    def __computingFinished(self, future: concurrent.futures.Future):
        future.result()
        self.computingFinished.emit()

    def __computing(self):
        self.db.actualizeData()
        self.engine.setDataSet(self.db.getData())
    
    @Slot(str, result=None)
    def updateFilter(self, dataJson: str): 
        data: Dict[str, str] = json.loads(dataJson)
        median = 1
        addresses = []
        durationLimit = None
        
        for key in data:
            if data[key].lower() == "none" or data[key].lower() == "all" or data[key].lower() == "auto":
                if key == "threads": 
                    DB_CONSTANTS.MIN_NUMBER_THREADS = 4
                    continue
                data[key]=False
            elif key == "threads":
                DB_CONSTANTS.MIN_NUMBER_THREADS = int(data[key])
            elif key == "address":
                addresses = [address.strip() for address in data[key].split(",")]
            elif key == "median_n":
                median = data[key]
            elif key == "duration_limit":
                durationLimit = data[key]
                        
        data.update({
            "interactive":False,
            "id_minimal": False,
            "id_maximal": False,
        })
        tupledData = namedtuple("ArgsLike", data.keys()) (*data.values())
        dbFilter = getAllArgs(tupledData)
        
        self.db.setDefaultFilter(dbFilter)
        self.engine.updateParameters(plotAddresses=addresses, 
                medianN=median, durationLimit=durationLimit)

        self.filterUpdated.emit()
    
    @Slot()
    def compute(self):
        self.computingStarted.emit()
        executor = concurrent.futures.ThreadPoolExecutor()
        future = executor.submit(self.__computing)
        future.add_done_callback(self.__computingFinished)

    
if __name__ == "__main__":
    args = init_argparse().parse_args()
    if args.interactive:
        args.terminal = True

    if not args.terminal:
        import gui.qrc_gui

    if args.local:
        DB_CONSTANTS.HOSTNAME = False
        DB_CONSTANTS.DATABASE_NAME = "local_mode_s"
        DB_CONSTANTS.USER_NAME = "root"
        DB_CONSTANTS.PASSWORD = "BisbiDb2022?"
    
    sys.argv += ['--style', 'Fusion']
    app = QGuiApplication(sys.argv)
    
    logger = Logger(args.terminal, args.verbose, args.debug)
    logger.info("Framework for automatic Mode-S data transfer and turbulence prediction.")
    logger.debug(args)
    
    db = Database(logger, terminal=args.terminal)
    
    modeSEngine = ModeSEngine.Engine(
        logger=logger, plots=args.plots, plotAddresses=args.plot_addresses, medianN=args.median_n, durationLimit=args.duration_limit
    )

    if not args.terminal:
        qInstallMessageHandler(qt_message_handler)
        engine = QQmlApplicationEngine()
        mode_s = Mode_S(db, modeSEngine, logger)
        engine.rootContext().setContextProperty("__mode_s", mode_s)
        engine.load(QUrl("qrc://gui/qml/main.qml"))
        if not engine.rootObjects():
            sys.exit(-1)
        sys.exit(app.exec())
    else:
        db.setDefaultFilter(getAllArgs(args))
        db.actualizeData()
        modeSEngine.setDataSet(db.getData())
        sys.exit(0)
