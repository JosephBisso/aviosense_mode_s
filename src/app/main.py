import os
import sys
import argparse
import multiprocessing
import concurrent.futures

from PySide2.QtQml import QQmlApplicationEngine, QQmlDebuggingEnabler
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QIcon
from PySide2.QtCore import *
from typing import Dict, NamedTuple, Union

sys.path.append(os.getcwd())

import mode_s.engine as ModeSEngine
from mode_s.constants import *
from mode_s.database import Database
from mode_s.logger import Logger
from mode_s.mode_s import Mode_S


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


if __name__ == "__main__":
    multiprocessing.freeze_support()
    know_args = init_argparse().parse_known_args()
    args = know_args[0]
    if args.interactive:
        args.terminal = True

    if not args.terminal:
        import gui.qrc_gui

    sys.argv += ['--style', 'Fusion']
    app = QApplication(sys.argv)
    app.setOrganizationName("TU Braunschweig")
    app.setOrganizationDomain("tu-braunschweig.de")
    app.setApplicationName("Mode_S Analysis")
    app.setWindowIcon(QIcon(":/img/mode_s.png"))

    appSettings = QSettings()

    db_login: Dict[str, Union[str, int]] = {
        "host_name": appSettings.value("parameters/host_name", "tubs.skysquitter.com"),
        "db_port": appSettings.value("parameters/db_port", 3307),
        "db_name": appSettings.value("parameters/db_name", "db_airdata"),
        "user_name": appSettings.value("parameters/user_name", "tubs"),
        "table_name": appSettings.value("parameters/table_name", "DILAB-2022"),
        "password": appSettings.value("parameters/password", "tbl_tubs")
    }

    db_column_names = None

    if args.local:
        #For Local Use only
        db_login["host_name"] = None
        db_login["db_port"] = None
        db_login["db_name"] = "local_mode_s"
        db_login["user_name"] = "root"
        db_login["table_name"] = "tbl_mode_s"
        db_login["password"] = "BisbiDb2022?"

        db_column_names = {
            "column_bar": "barometric_altitude_rate",
            "column_ivv": "inertial_vertical_velocity"
        }

    if db_login["db_port"] is not None and isinstance(db_login["db_port"], str) and db_login["db_port"].isdigit():
        db_login["db_port"] = int(db_login["db_port"])
    else:
        db_login["db_port"] = None

    if args.debug:
        debugger = QQmlDebuggingEnabler()
        # debugger.startTcpDebugServer(6969, mode=QQmlDebuggingEnabler.StartMode.WaitForClient)

    logger = Logger(args.terminal, args.verbose, args.debug)
    logger.info(
        "Framework for automatic Mode-S data transfer & turbulence prediction")
    logger.debug(args)

    processPoolExecutor = concurrent.futures.ProcessPoolExecutor(
        max_workers=multiprocessing.cpu_count() + 1
    )

    db = Database(logger=logger)
    db.setLogin(**db_login)
    if db_column_names:
        db.setValidDBColumnsNames(**db_column_names)

    modeSEngine = ModeSEngine.Engine(logger=logger)

    db.setProcessExecutor(processPoolExecutor)
    modeSEngine.setProcessExecutor(processPoolExecutor)

    qInstallMessageHandler(qt_message_handler)

    if not args.terminal:
        engine = QQmlApplicationEngine()
        mode_s = Mode_S(db, modeSEngine, logger)
        mode_s.setProcessExecutor(processPoolExecutor)
        engine.rootContext().setContextProperty("__mode_s", mode_s)
        engine.load(QUrl("qrc:/qml/main.qml"))
        try:
            import pyi_splash
            pyi_splash.close()
        except:
            pass
        if not engine.rootObjects():
            logger.warning("Could not start application Engine")
            sys.exit(-1)
        sys.exit(app.exec_())
    else:
        dbWorking = db.start()
        db.setDatabaseParameters(**dict(args._get_kwargs()))
        if dbWorking:
            dbWorking = db.actualizeData()
        if not dbWorking:
            sys.exit(-1)
        modeSEngine.setDataSet(db.getData())
        modeSEngine.activatePlot(plots=args.plots)
        modeSEngine.setEngineParameters(
            plotAddresses=args.plot_addresses, plotAll=args.plot_all, medianN=args.median_n)
        for plot in modeSEngine.compute():
            pass
        sys.exit(0)
