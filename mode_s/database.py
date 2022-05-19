from re import L
from PySide6 import QtSql
from PySide6.QtCore import QDateTime

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
    ROW_COUNT = 0

    CONNECTIONS_TOTAL = 0
    
    MAX_ROW_BEFORE_LONG_DURATION = 100000
    MIN_NUMBER_THREADS = 20
    

class Database:
    def __init__(self, logger: Logger):        
        db = QtSql.QSqlDatabase.addDatabase("QMYSQL")
        self.__setUp(db)
        self.filterOn: bool = False 
        self.logger: Logger = logger
        self.data: List[Dict[str, Union[str, int]]] = []  

        executor = concurrent.futures.ThreadPoolExecutor()
        if db.open():
            self.logger.info("Database accessible")
            db.close()
            rowCount__future = executor.submit(self.__getDBRowCount)
        else:
            self.logger.critical("Database not accessible")

        rowCount__future.result()
        f = executor.submit(self.__getLattestDBTimeStamp)
        f.result()
        
    def __setUp(self, db: QtSql.QSqlDatabase):
        db.setHostName(DB_CONSTANTS.HOSTNAME)
        db.setDatabaseName(DB_CONSTANTS.DATABASE_NAME)
        db.setUserName(DB_CONSTANTS.USER_NAME)
        db.setPassword(DB_CONSTANTS.PASSWORD)

    def __getDBRowCount(self):
        q = self.__query("SELECT COUNT(*) FROM tbl_mode_s")
        while q.next():
            DB_CONSTANTS.ROW_COUNT = q.value(0)   
        q.finish()
        self.logger.info("Row Count for table tbl_mode_s: " + str(DB_CONSTANTS.ROW_COUNT))

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
        q.setForwardOnly(True)
        if not q.exec(query):
            self.logger.critical(
                "Could not execute query: " + q.lastQuery() + " on " + name + " ERROR:: " + q.lastError().text(), ConnectionError)

        self.logger.debug("Executed following query: " + q.lastQuery() + " :: on :: " + name)
        db.close()
        return q

    def __getAll(self, query: QtSql.QSqlQuery, elements: List[str] = []) -> List[Dict[str, Union[int, str]]]:
        allResults = []
        
        absentColumns =  []
        for el in DB_CONSTANTS.USED_COLUMNS:
            if not el in elements: absentColumns.append(el)
            
        while query.next():
            entry = {abs: None for abs in absentColumns}
            for el in elements:
                value = query.value(el)
                if isinstance(value, str):
                    entry[el] = value.strip()
                elif isinstance(value, QDateTime):
                    entry[el] = value.toMSecsSinceEpoch() * 10**6
                else:
                    entry[el] = value

            allResults.append(entry)

        query.finish()
        return allResults
    
    def __generateQueries(self, attributes: List[str], options: Dict[str, str]) -> List[str]:
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
                    whereStr += " AND " if index < (len(options["not_null_values"]) - 1) else " "
        except KeyError:
            pass

        try:
            limit = options["limit"] if int(options["limit"]) <= DB_CONSTANTS.ROW_COUNT else DB_CONSTANTS.ROW_COUNT
        except KeyError:
            limit = self.limit
        
        dividing = int(limit) > DB_CONSTANTS.MAX_ROW_BEFORE_LONG_DURATION
        numThread = max(int(int(limit) / DB_CONSTANTS.MAX_ROW_BEFORE_LONG_DURATION), DB_CONSTANTS.MIN_NUMBER_THREADS) if dividing else DB_CONSTANTS.MIN_NUMBER_THREADS

        limitPerThread = int(int(limit)/numThread)
        if limitPerThread == 0: 
            limitPerThread = int(limit)
            numThread = 1
        
        rest = int(limit) % numThread

        if not ident_run:
            offsetStr = [(" LIMIT " + str(limitPerThread) + " OFFSET " + str(i * limitPerThread)) for i in range(numThread) ]
            if rest : offsetStr.append(" LIMIT " + str(rest) + " OFFSET " + str(numThread * limitPerThread))
        else:
            offsetStr = [""] 

        self.logger.log(str(len(offsetStr))  + " threads for attributes " + str(attributes))
        queries = [(selectStr + " FROM tbl_mode_s " + whereStr + (" ORDER BY timestamp DESC " if not ident_run else "") + offset) for offset in offsetStr]
        return queries

    def __actualizeKnownAddresses(self, id_address: List[Dict[str, Union[int, str]]] = []):
        self.addresses = []
        self.knownIdents = {}
        skippedAddresses = []
        for el in id_address:
            address = el["address"]
            if address in self.addresses and not el["identification"].isalnum():
                skippedAddresses.append(address)
                continue
            self.addresses.append(address)
            self.knownIdents[address] = el["identification"]

        if len(skippedAddresses) > 0:
            self.logger.warning("Skipping following addresses: " + str(skippedAddresses) + " :: Already added or invalid identification")
        self.logger.info("Known Addresses: " + str(len(self.addresses)))
        
    def __getLattestDBTimeStamp(self):
        time = self.getFromDB( ["timestamp"], options = {"not_null_values": ["timestamp"], "limit": 1})
        lastDBUpdate = QDateTime.fromMSecsSinceEpoch(int(time[0]["timestamp"]) / 10**6).toString()
        self.logger.info("Lattest database db_airdata update: " + lastDBUpdate)

    def getData(self) -> List[Dict[str, Union[str, int]]]:
        return self.data

    def setDefaultFilter(self, params: Dict[str, str] = {}):
        strFilter = " "
        for index, el in enumerate(params.keys()):
            if el == "limit":
                if int(params["limit"]) <= DB_CONSTANTS.ROW_COUNT:
                    self.limit = params["limit"]
                    self.logger.log("Setting global query row limit to: " + str(self.limit))
                else:
                    self.limit = DB_CONSTANTS.ROW_COUNT
                    self.logger.warning("Setting global query row limit to: " + str(DB_CONSTANTS.ROW_COUNT) + ". (Total row count of table)")
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
        self.logger.log("Setting query filter to: " + strFilter)
        self.strFilter = strFilter

    def resetFilter(self):
        self.filterOn = False
        
    def getFromDB(self, attributes: List[str] = [], options: Dict[str, str] = {"default_filter_on": False, "select_distinct": False, "not_null_values": []}) -> List[Dict[str, Union[int, str]]]:
        # option={..., "limit":50000}
        queries = self.__generateQueries(attributes, options) 
            
        queryExecutor = concurrent.futures.ThreadPoolExecutor()
        threadedQueries = [queryExecutor.submit(self.__query, query) for query in queries]

        allResults = []
        for completedQuery in concurrent.futures.as_completed(threadedQueries):
            try:
                query = completedQuery.result()
            except Exception as esc:
                self.logger.warning("Error occurred while getting attributes " + str(attributes) + "\nERROR: " + str(esc))
            else:
                allResults.extend(self.__getAll(query, attributes))
        
        self.logger.info("Query successfully excecuted. Attributes were: " + str(attributes))
        return allResults
    
    def actualizeData(self) -> bool:
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                idAndAddress__future = executor.submit(self.getFromDB, ["identification", "address"], options={
                                                     "select_distinct": True, "not_null_values": ["identification", "address"]})

                latAndlon__future = executor.submit(self.getFromDB, ["id", "address", "timestamp", "bds", "altitude", "latitude", "longitude"], options={
                                                  "not_null_values": ["bds", "altitude"], "limit": int(int(self.limit) / 2)})

                barAndivv__future = executor.submit(self.getFromDB, ["id", "address", "timestamp", "bds", "altitude", "bar", "ivv"], options={
                                                  "not_null_values": ["bds60_barometric_altitude_rate", "bds60_inertial_vertical_velocity"], "limit": int(int(self.limit) / 2)})

                executor.submit(self.__actualizeKnownAddresses, idAndAddress__future.result())
                
                for completedTask in concurrent.futures.as_completed([latAndlon__future, barAndivv__future]):
                    try:
                        halfResult = completedTask.result()
                    except Exception as esc:
                        self.logger.warning(
                            "Error occurred while getting results \nERROR: " + str(esc))
                    else:
                        self.data.extend(halfResult)

            self.logger.info("Data actualized. Size: " + str(len(self.data)))

            return True

        except ConnectionError:
            self.logger.warning("Could not actualize Addresses")
            return False
