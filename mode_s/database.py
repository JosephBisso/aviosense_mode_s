from PySide6 import QtSql
from PySide6.QtCore import QDateTime

import json
import os
import concurrent.futures
from typing import List, Dict, Union

from pyparsing import Any


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
               

        self.data: List[Dict[str, Union[str, int]]] = []  
        
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
        q.setForwardOnly(True)
        if not q.exec(query):
            self.logger.critical(
                "Could not execute query: " + q.lastQuery() + " on " + name + "ERROR:: " + q.lastError().text(), ConnectionError)

        self.logger.debug("Executed following query: " + q.lastQuery() + " :: on :: " + name)
        self.logger.info("Query successfully excecuted")
        db.close()
        return q

    def __getAll(self, query: QtSql.QSqlQuery = QtSql.QSqlQuery(), elements: List[str] = []) -> List[Dict[str, Union[int, str]]]:
        allResults = []
        executor = concurrent.futures.ThreadPoolExecutor()
        while query.next():
            executor.submit(self.__appendEntryToAllResults, allValues={el: query.value(el) for el in elements}, elements=elements, allResults=allResults)
        
        executor.shutdown(wait=True)
        self.logger.debug("Finish getting all data from query: " + query.lastQuery())
        return allResults
    
    def __appendEntryToAllResults(self,  allValues: List[Dict[str, Any]], elements: List[str], allResults : List[Dict[str, Union[int, str]]]):
        entry = {}
        for el in elements:
            if isinstance(allValues[el], str):
                entry[el] = allValues[el].strip()
            elif isinstance(allValues[el], QDateTime):
                entry[el] = allValues[el].toMSecsSinceEpoch() * 10**6
            else:
                entry[el] = allValues[el]
                
        entry.update({abs: None for abs in (set(DB_CONSTANTS.USED_COLUMNS) - set(elements))})
        allResults.append(entry)

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
        
    def __getLattestDBTimeStamp(self):
        time = self.getFromDB( ["timestamp"], options = {"not_null_values": ["timestamp"], "limit": 1})
        lastDBUpdate = QDateTime.fromMSecsSinceEpoch(int(time[0]["timestamp"]) / 10**6).toString()
        self.lattestDBUpdate = lastDBUpdate
        
        self.logger.info("Lattest database db_airdata update: " + lastDBUpdate)

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
               
        return self.__getAll(self.__query(query), attributes)

    def actualizeData(self) -> bool:
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                id_address__future = executor.submit(self.getFromDB, ["identification", "address"], options={
                                                     "select_distinct": True, "not_null_values": ["identification", "address"]})

                lat_lon__future = executor.submit(self.getFromDB, ["id", "address", "timestamp", "bds", "altitude", "latitude", "longitude"], options={
                                                  "not_null_values": ["bds", "altitude"], "limit": int(int(self.limit) / 2)})

                bar_ivv__future = executor.submit(self.getFromDB, ["id", "address", "timestamp", "bds", "altitude", "bar", "ivv"], options={
                                                  "not_null_values": ["bds60_barometric_altitude_rate", "bds60_inertial_vertical_velocity"], "limit": int(int(self.limit) / 2)})

                executor.submit(self.__actualizeKnownAddresses, id_address__future.result())
                
                self.data = bar_ivv__future.result()
                self.data.extend(lat_lon__future.result())

            self.logger.info("Data actualized. Size: " + str(len(self.data)))

            return True

        except ConnectionError:
            self.logger.warning("Could not actualize Addresses")
            return False
