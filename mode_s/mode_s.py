# This Python file uses the following encoding: utf-8
import os
import sys
import argparse
import json
import concurrent.futures
from collections import namedtuple
from typing import Dict, NamedTuple


from PySide2.QtQml import QQmlApplicationEngine
from PySide2.QtCore import *
from PySide2.QtWidgets import QApplication
from PySide2 import QtCharts

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
    parser.add_argument("-bd", "--bds", type = int,
                        help="The desired bds. If not set, all available bds are evaluated")
    parser.add_argument("-id", "--id-minimal", metavar="id_minimal", type = int,
                        help="The desired minimal id. If not set, all available ids are evaluated")
    parser.add_argument("-ID", "--id-maximal", type = int,
                        help="The desired maximal id. If not set, all available ids are evaluated")
    parser.add_argument("-l", "--limit", type = int,
                        help="The desired limit for the mysql commands. (default = 500000)", default=500000)
    parser.add_argument("-dl", "--duration-limit", type = float,
                        help="The desired flight duration limit in minutes for the analysis. (default = 10)", default=10)
    parser.add_argument("-n", "--median-n", type = int,
                        help="The desired n for the median filtering. MUST BE ODD. (default: n=3)", default=3)
    parser.add_argument("-p", "--plots", nargs='*',
                        help="The desired plots. POSSIBLE VALUES: " + str(ENGINE_CONSTANTS.PLOTS), default=[])
    parser.add_argument("-pa", "--plot-addresses", nargs='*',
                        help="The addresses of the desired plots.", default=[])
    parser.add_argument("--plot-all", action="store_true",
                        help="Plot all addresses for the desired plots.", default=False)
    
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
    
    logged              = Signal(str, arguments=['log'])

    filterUpdated       = Signal()
    computingStarted    = Signal()
    computingFinished   = Signal()

    readyToPlot         = Signal()
    plotOccurrenceReady = Signal(list, arguments=["pointList"])
    plotRawReady        = Signal(list, arguments=["pointList"])
    plotStdReady        = Signal(list, arguments=["pointList"])
    plotFilteredReady   = Signal(list, arguments=["pointList"])
    plotIntervalReady   = Signal(list, arguments=["pointList"])
    plotLocationReady   = Signal(list, arguments=["pointList"])
    plotHeatMapReady    = Signal(list, arguments=["pointList"])

    def __init__(self, db: Database, msEngine: ModeSEngine.Engine, logger: Logger):
        super(Mode_S, self).__init__(None)
        self.db = db
        self.engine = msEngine
        self.logger = logger
        logger.logged.connect(self.__log)
        self.filterUpdated.connect(self.compute)
        self.readyToPlot.connect(self.plot)
        self.executor = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="modeS_workerThread")
    
    @Slot(str, result=None)
    def updateFilter(self, dataJson: str): 
        data: Dict[str, str] = json.loads(dataJson)
        median = 1
        
        for key in data:
            if data[key].isdigit():
                data[key] = int(data[key])
            elif data[key].lower() == "none" or data[key].lower() == "all" or data[key].lower() == "auto":
                data[key]=None
                                
        self.db.setDatabaseParameters(**data)
        self.engine.setEngineParameters(**data)

        self.filterUpdated.emit()
    
    @Slot()
    def compute(self):
        self.computingStarted.emit()
        future = self.executor.submit(self.__computing)
        future.add_done_callback(self.__readyToPlot)
        
    @Slot()
    def startDatabase(self):
        self.executor.submit(self.db.start)
                
    @Slot()
    def plot(self): 
        future = self.executor.submit(self.__plotting)
        future.add_done_callback(self.__computingFinished)
    
    @Slot(str)
    def __log(self, log: str):
        self.logged.emit(log)

    def __computingFinished(self, future: concurrent.futures.Future):
        future.result()
        self.computingFinished.emit()

    def __readyToPlot(self, future: concurrent.futures.Future):
        future.result()
        self.readyToPlot.emit()

    def __computing(self):
        self.db.actualizeData()
        self.engine.setDataSet(self.db.getData())

    def __plotting(self):
        results = self.engine.compute(usePlotter=False)

        occurrenceSeries = next(results)
        rawSeries = next(results)
        intervalSeries = next(results)
        filteredSeries = next(results)
        stdSeries = next(results)
        locationSeries = next(results)
        heatMapSeries = next(results)

        self.plotOccurrenceReady.emit(occurrenceSeries)
        self.plotRawReady.emit(rawSeries)
        self.plotIntervalReady.emit(intervalSeries)
        self.plotFilteredReady.emit(filteredSeries)
        self.plotStdReady.emit(stdSeries)
        self.plotLocationReady.emit(locationSeries)
        self.plotHeatMapReady.emit(heatMapSeries)

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
    app = QApplication(sys.argv)
    
    logger = Logger(args.terminal, args.verbose, args.debug)
    logger.info("Framework for automatic Mode-S data transfer & turbulence prediction")
    logger.debug(args)
    
    db = Database(logger=logger)
    modeSEngine = ModeSEngine.Engine(logger=logger)

    qInstallMessageHandler(qt_message_handler)
    
    if not args.terminal:
        engine = QQmlApplicationEngine()
        mode_s = Mode_S(db, modeSEngine, logger)
        engine.rootContext().setContextProperty("__mode_s", mode_s)
        engine.load(QUrl("qrc:/qml/main.qml"))
        if not engine.rootObjects():
            logger.warning("Could not start application Engine")
            sys.exit(-1)
        sys.exit(app.exec_())
    else:
        dbWorking = db.start()
        db.setDatabaseParameters(**dict(args._get_kwargs()))
        if dbWorking : dbWorking = db.actualizeData()
        if not dbWorking:
            sys.exit(-1)
        modeSEngine.setDataSet(db.getData())
        modeSEngine.activatePlot(plots=args.plots)
        modeSEngine.setEngineParameters(plotAddresses=args.plot_addresses, plotAll=args.plot_all, medianN=args.median_n)
        for plot in modeSEngine.compute():
            pass
        sys.exit(0)
