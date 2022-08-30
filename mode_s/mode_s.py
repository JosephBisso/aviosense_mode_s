# This Python file uses the following encoding: utf-8
import os
import gc
import sys
import argparse
import json
import concurrent.futures
from collections import namedtuple
from typing import Any, Dict, NamedTuple, List


from PySide2.QtQml import QQmlApplicationEngine, QQmlDebuggingEnabler
from PySide2.QtCore import *
from PySide2.QtWidgets import QApplication

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

    dbFilterUpdated     = Signal()
    engineFilterUpdated = Signal()
    computingStarted    = Signal()
    computingFinished   = Signal()

    readyToPlot         = Signal()
    identificationMapped= Signal("QVariantMap", arguments=["identMap"])
    plotOccurrenceReady = Signal("QVariantList", arguments=["pointList"])
    plotRawReady        = Signal("QVariantList", arguments=["pointList"])
    plotStdReady        = Signal("QVariantList", arguments=["pointList"])
    plotFilteredReady   = Signal("QVariantList", arguments=["pointList"])
    plotIntervalReady   = Signal("QVariantList", arguments=["pointList"])
    plotLocationReady   = Signal("QVariantList", arguments=["pointList"])
    plotTurbulentReady  = Signal("QVariantList", arguments=["pointList"])
    plotHeatMapReady    = Signal("QVariantList", arguments=["pointList"])
    
    backgroundFutures: List[concurrent.futures.Future] = []

    def __init__(self, db: Database, msEngine: ModeSEngine.Engine, logger: Logger):
        super(Mode_S, self).__init__(None)
        self.db = db
        self.engine = msEngine
        self.logger = logger
        logger.logged.connect(self.__log)
        self.dbFilterUpdated.connect(self.actualizeDB)
        self.engineFilterUpdated.connect(self.compute)
        self.readyToPlot.connect(self.plot)
        self.executor = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="modeS_workerThread")

        self.plot(fromDump=True)
    
    @Slot(str, result=None)
    def updateDBFilter(self, dbJson: str): 
        self.computingStarted.emit()
        data: Dict[str, str] = self.__checkParam(dbJson)
        
        future = self.executor.submit(self.__setDbParameters, data)
        self.backgroundFutures.append(future)
    
    def __setDbParameters(self, data):
        self.db.setDatabaseParameters(**data)
        self.dbFilterUpdated.emit()

    @Slot(str, result=None)
    def updateEngineFilter(self, engineJson: str): 
        self.computingStarted.emit()
        data: Dict[str, str] = self.__checkParam(engineJson)
                                
        self.engine.setEngineParameters(**data)
        self.engineFilterUpdated.emit()
    
    @Slot()
    def actualizeDB(self):
        future = self.executor.submit(self.__actualizeDB)
        future.add_done_callback(self.__computingFinished)
        
    @Slot()
    def compute(self):
        self.executor.submit(self.__prepareEngine)
        
    @Slot()
    def startDatabase(self):
        self.executor.submit(self.db.start)
                
    @Slot()
    def plot(self, **params): 
        future = self.executor.submit(self.__plotting, **params)
        future.add_done_callback(self.__computingFinished)

    @Slot()
    def cancel(self): 
        self.db.cancel()
        self.engine.cancel()
        self.executor.shutdown(wait=False)
        self.executor = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="modeS_workerThread")
        self.computingFinished.emit()

    @Slot(str)
    def __log(self, log: str):
        self.logged.emit(log)
        
    def __checkParam(self, strJson):
        data: Dict[str, str] = json.loads(strJson)

        for key in data:
            if data[key].isdigit():
                data[key] = int(data[key])
            else:
                try:
                    data[key] = float(data[key])
                except ValueError:
                    if data[key].lower() == "none" or data[key].lower() == "all" or data[key].lower() == "auto":
                        data[key] = None                    

        return data

    def __computingFinished(self, future: concurrent.futures.Future):
        future.result()
        self.computingFinished.emit()

    def __prepareEngine(self):
        self.waitUntilReady()
        self.engine.setDataSet(self.db.getData())
        self.readyToPlot.emit()

        
    def __actualizeDB(self):
        self.db.actualizeData()

    def waitUntilReady(self) -> bool:
        concurrent.futures.wait(self.backgroundFutures)
        return True

    def __plotting(self, **params):
        try: 
            occurrenceSeries = identMap = rawSeries = intervalSeries = filteredSeries = stdSeries = locationSeries = turbulentLocationSeries = heatMapSeries = 0
            
            if params.get("fromDump"):
                results = self.engine.loadDump()
            else:
                results = self.engine.compute(usePlotter=False)

            occurrenceSeries = next(results)

            computedAddresses = next(results)
            identMap = computedAddresses if params.get("fromDump") else self.db.getMapping(computedAddresses)
            self.identificationMapped.emit(identMap)
            self.plotOccurrenceReady.emit(occurrenceSeries)

            rawSeries = next(results)
            self.plotRawReady.emit(rawSeries)

            intervalSeries = next(results)
            self.plotIntervalReady.emit(intervalSeries)

            filteredSeries = next(results)
            self.plotFilteredReady.emit(filteredSeries)

            stdSeries = next(results)
            self.plotStdReady.emit(stdSeries)

            locationSeries = next(results)
            self.plotLocationReady.emit(locationSeries)

            turbulentLocationSeries = next(results)
            self.plotTurbulentReady.emit(turbulentLocationSeries)

            heatMapSeries = next(results)
            self.plotHeatMapReady.emit(heatMapSeries)

            self.logger.success("Done computing")
            
            next(results, None)

        except ModeSEngine.EngineError as err:
            self.logger.warning("Error Occurred: Mode_s plotting::", str(err))
        finally:
            ms = MODE_S_CONSTANTS
            self.executor.submit(self.__dumpData, self.db.data, ms.DATABASE_DUMP)
            self.db.data = self.engine.data = []
            
            toDump = [occurrenceSeries, identMap, rawSeries, intervalSeries,
                      filteredSeries, stdSeries, locationSeries, turbulentLocationSeries, heatMapSeries]
            toDumpName = [ms.OCCURRENCE_DUMP, ms.INDENT_MAPPING, ms.BAR_IVV_DUMP, ms.INTERVAL_DUMP,
                          ms.FILTERED_DUMP, ms.STD_DUMP, ms.LOCATION_DUMP, ms.TURBULENCE_DUMP, ms.HEATMAP_DUMP]
            for index in range(len(toDump)):
                self.executor.submit(
                    self.__dumpData, toDump[index], toDumpName[index])
                toDump[index] = []

            gc.collect()

    def __dumpData(self, data: List[Any], name: str):
        self.logger.debug("Dumping and freeing memory for", name)
        with open(name, "w") as dumpF:
            json.dump(data, dumpF, indent = 2)

if __name__ == "__main__":
    know_args = init_argparse().parse_known_args()
    args = know_args[0]
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
    app.setOrganizationName("TU Braunschweig")
    app.setOrganizationDomain("tu-braunschweig.de")
    app.setApplicationName("Mode_S Analysis")

    if args.debug:
        debugger = QQmlDebuggingEnabler()
        # debugger.startTcpDebugServer(6969, mode=QQmlDebuggingEnabler.StartMode.WaitForClient)
    
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
