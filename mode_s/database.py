from PySide6 import QtSql
from PySide6.QtCore import QDateTime

import json
import os
import concurrent.futures
from typing import List, Dict, Union


from logger import Logger

class DB_CONSTANTS:
    VALID_DB_COLUMNS = ["id", "timestamp", "frame_hex_chars", "address", "downlink_format", "bds", "on_ground", "adsb_version", "altitude", "altitude_is_barometric", "nuc_p", "latitude", "longitude", "nuc_r", "true_track", "groundspeed", "vertical_rate", "gnss_height_diff_from_baro_alt", "identification",
                        "category", "bds17_common_usage_gicb_capability_report", "bds50_roll_angle", "bds50_true_track_angle", "bds50_ground_speed", "bds50_track_angle_rate", "bds50_true_airspeed", "bds60_magnetic_heading", "bds60_indicated_airspeed", "bds60_mach", "bds60_barometric_altitude_rate", "bds60_inertial_vertical_velocity"]

    USED_COLUMNS = ["id", "identification", "address", "timestamp",
                    "bds", "altitude", "latitude", "longitude",  "bar", "ivv"]

    HOSTNAME = "airdata.skysquitter.com"
    DATABASE_NAME = "db_airdata"
    USER_NAME = "tubs"
    PASSWORD = "ue73f5dn"

    CONNECTIONS_TOTAL = 0


class Database:
    def __init__(self, logger: Logger):        
        db = QtSql.QSqlDatabase.addDatabase("QMYSQL")
        self.__setUp(db)
        self.filterOn: bool = False 
        self.logger: Logger = logger
        if db.open():
            self.logger.info("Database accessible")
            db.close()
            self.__getLattestDBTimeStamp()
        else:
            self.logger.critical("Database not accessible")
               
        database_loader = concurrent.futures.ThreadPoolExecutor()
        self.databaseLoadingTask = database_loader.submit(self.__loadDumpedDatabase)

        self.data: List[Dict[str, Union[str, int]]] = self.databaseLoadingTask.result() if self.databaseLoadingTask.done() else []  
        
    def __setUp(self, db: QtSql.QSqlDatabase):
        db.setHostName(DB_CONSTANTS.HOSTNAME)
        db.setDatabaseName(DB_CONSTANTS.DATABASE_NAME)
        db.setUserName(DB_CONSTANTS.USER_NAME)
        db.setPassword(DB_CONSTANTS.PASSWORD)

    def __query(self, query: str) -> QtSql.QSqlQuery:
        DB_CONSTANTS.CONNECTIONS_TOTAL += 1
        name = "db_thread_" + str(DB_CONSTANTS.CONNECTIONS_TOTAL)
        db = QtSql.QSqlDatabase.addDatabase("QMYSQL", name)
        self.__setUp(db)
        if not db.open():
            self.logger.critical("Database " + name +
                                 "not accessible", ConnectionError)

        self.logger.debug("New database connection: " + name)

        q = QtSql.QSqlQuery(db)
        if not q.exec(query):
            self.logger.critical(
                "Could not execute query from database " + name, ConnectionError)

        db.close()
        return q

    def __getAll(self, query: QtSql.QSqlQuery = QtSql.QSqlQuery(), elements: List[str] = []) -> List[Dict[str, Union[int, str]]]:
        allResults = []
        while query.next():
            entry = {}
            for el in elements:
                value = query.value(el)
                if isinstance(value, str):
                    entry[el] = value.strip()
                elif isinstance(value, QDateTime):
                    entry[el] = value.toMSecsSinceEpoch() * 10**6
                else:
                    entry[el] = value
            for abs in DB_CONSTANTS.USED_COLUMNS:
                if not abs in elements:
                    entry[abs] = None
            allResults.append(entry)
        return allResults

    def __isEmpty(self, entry: Dict[str, Union[int, str]] = {}) -> bool:
        for el in entry.keys():
            if not str(entry[el]).isalnum():
                return False
        return True

    def __generateQuery(self, attributes: List[str], options: Dict[str, str]) -> str:
        selectStr = "SELECT "
        try:
            if options["select_distinct"]:
                selectStr += "DISTINCT "
        except KeyError:
            pass

        for index, attrib in enumerate(attributes):
            if attrib == "bar":
                selectStr += "bds60_barometric_altitude_rate AS bar"
            elif attrib == "ivv":
                selectStr += "bds60_inertial_vertical_velocity AS ivv"
            else:
                if not attrib in DB_CONSTANTS.VALID_DB_COLUMNS:
                    self.logger.critical(
                        "Attribute: " + attrib + "not valid", ValueError)
                selectStr += attrib
            selectStr += ", " if index < (len(attributes) - 1) else " "

        whereStr = "WHERE"
        try:
            if options["default_filter_on"]:
                whereStr += self.strFilter + " "
        except KeyError:
            if self.filterOn:
                whereStr += self.strFilter + " "
        
        ident_run = False
        try:
            if len(options["not_null_values"]) > 0:
                if "identification" in options["not_null_values"] and "address" in options["not_null_values"]:
                    ident_run = True
                    whereStr = " WHERE "
                else:
                    whereStr += " AND " if not whereStr == "WHERE" else " "

                for index, attrib in enumerate(options["not_null_values"]):
                    whereStr += attrib + " IS NOT NULL"
                    whereStr += " AND " if index < (
                        len(options["not_null_values"]) - 1) else " "
        except KeyError:
            pass

        try:
            limit = options["limit"]
        except KeyError:
            limit = self.limit
        limitStr = "LIMIT " + str(limit) if not ident_run else ""

        query = selectStr + " FROM tbl_mode_s " + whereStr + (" ORDER BY timestamp DESC " if not ident_run else "") + limitStr
        return query

    def __actualizeKnownAddresses(self, id_address: List[Dict[str, Union[int, str]]] = []):
        self.addresses = []
        self.known_idents = {}
        skipped_addresses = []
        for el in id_address:
            address = el["address"]
            if address in self.addresses and not el["identification"].isalnum():
                skipped_addresses.append(address)
                continue
            self.addresses.append(address)
            self.known_idents[address] = el["identification"]

        self.logger.warning("Skipping following addresses: " + str(skipped_addresses) + " :: Already added or invalid identification")
        self.logger.debug("Known Addresses: " + str(len(self.addresses)))

    def __loadDumpedDatabase(self) -> List[Dict[str, Union[str, int]]]:
        if not os.path.exists("database"): return []
        
        database_path = "database\\database_dump.json"

        if not os.path.exists(database_path): return []
        
        with open(database_path, 'r') as database:
            data = json.load(database)
            
        lastUpdate = QDateTime.fromMSecsSinceEpoch(int(data[0]["timestamp"]) / 10**6).toString()
        self.lastDumpUpdate = lastUpdate
        
        self.logger.info("Loaded dumped database. Size: " + str(len(data)) + ". Lasttest entry: " + lastUpdate)

        return data

    def __dumpDatabase(self):
        if not os.path.exists("database"):
            os.mkdir("database")

        database_path = "database\\database_dump.json"

        if not os.path.exists(database_path):
            with open(database_path, 'w') as database:
                json.dump(self.data, database, indent="\t")

            self.logger.info("Successfully dumped data base")
            return

        with open(database_path, 'r') as database:
            data: List[Dict[int, Union[str, int]]] = json.load(database)

        for el in self.data: data.append(el)
        data.sort(key=lambda item: item.get("timestamp"), reverse=True)
        os.remove(database_path)

        with open(database_path, 'w') as database:
            json.dump(data, database, indent="\t")

        self.logger.info("Successfully dumped data base")
        
    def __getLattestDBTimeStamp(self):
        time = self.getFromDB( ["timestamp"], options = {"not_null_values": ["timestamp"], "limit": 1})
        lastDBUpdate = QDateTime.fromMSecsSinceEpoch(int(time[0]["timestamp"]) / 10**6).toString()
        self.lattestDBUpdate = lastDBUpdate
        
        self.logger.info("Lattest database db_airdata update: " + lastDBUpdate)


    def isOpen(self) -> bool:
        return self.open

    def getData(self) -> List[Dict[str, Union[str, int]]]:
        return self.data

    def setDefaultFilter(self, params: Dict[str, str] = {}):
        strFilter = " "
        for index, el in enumerate(params.keys()):
            if el == "limit":
                self.limit = params["limit"]
                self.logger.debug(
                    "Setting global query row limit to: " + self.limit)
                continue
            elif "minimal" in el:
                if "latitude" in el: strFilter += "latitude > " + params[el]
                elif "longitude" in el: strFilter += "longitude > " + params[el]
                elif "id" in el: strFilter += "id > " + params[el]
            elif "maximal" in el:
                if "latitude" in el: strFilter += "latitude < " + params[el]
                elif "longitude" in el: strFilter += "longitude < " + params[el]
                elif "id" in el: strFilter += "id < " + params[el]
            else: strFilter += el + " = " + params[el]
            
            strFilter += " AND " if index < len(params.keys()) - 1 else " "

        self.filterOn = len(params.keys()) > 1
        self.logger.debug("Setting engine filter to: " + strFilter)
        self.strFilter = strFilter

    def resetFilter(self):
        self.filterOn = False
        
    def getFromDB(self, attributes: List[str] = [], options: Dict[str, str] = {"default_filter_on": False, "select_distinct": False, "not_null_values": []}) -> List[Dict[str, Union[int, str]]]:
        # option={..., "limit":50000}
        query = self.__generateQuery(attributes, options)

        self.logger.debug("Executing following query: " + query)

        try:
            results = self.__query(query)
        except ConnectionError:
            self.logger.critical("Could not run query " + query)

        self.logger.info("Query successfully excecuted")
        return self.__getAll(results, attributes)

    def actualizeData(self) -> bool:
        try:
            lat_lon = bar_ivv = []

            with concurrent.futures.ThreadPoolExecutor() as executor:
                id_address__future = executor.submit(self.getFromDB, ["identification", "address"], options={
                                                     "select_distinct": True, "not_null_values": ["identification", "address"]})

                lat_lon__future = executor.submit(self.getFromDB, ["id", "address", "timestamp", "bds", "altitude", "latitude", "longitude"], options={
                                                  "not_null_values": ["bds", "altitude"], "limit": int(int(self.limit) / 2)})

                bar_ivv__future = executor.submit(self.getFromDB, ["id", "address", "timestamp", "bds", "altitude", "bar", "ivv"], options={
                                                  "not_null_values": ["bds60_barometric_altitude_rate", "bds60_inertial_vertical_velocity"], "limit": int(int(self.limit) / 2)})

                id_address = id_address__future.result()
                executor.submit(self.__actualizeKnownAddresses, id_address)

                lat_lon = lat_lon__future.result()
                bar_ivv = bar_ivv__future.result()
                all_data_raw = lat_lon + bar_ivv

            skipped = 0

            self.data = self.databaseLoadingTask.result()
            for i in range(len(all_data_raw)):
                address = all_data_raw[i]["address"]
                if address in self.addresses:
                    all_data_raw[i]["identification"] = self.known_idents[address]
                else:
                    skipped += 1
                    continue
                
                self.data.append(all_data_raw[i])

            if skipped > 0:
                self.logger.warning(
                    "Skipped " + str(skipped) + " entries. Identification(s) unknown")

            self.logger.info("Data actualized. Size: " + str(len(self.data)))

            databaseDump_executor = concurrent.futures.ThreadPoolExecutor()
            databaseDump_executor.submit(self.__dumpDatabase)
            
            return True

        except ConnectionError:
            self.logger.warning("Could not actualize Addresses")
            return False
