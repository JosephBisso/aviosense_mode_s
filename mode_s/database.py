from PySide2 import QtSql
from PySide2.QtCore import QDateTime

import sys
import concurrent.futures
from typing import List, Dict, Union

from logger import Logger
from constants import DB_CONSTANTS, LOGGER_CONSTANTS


class DatabaseError(BaseException):
    pass

class Database:

    ROW_COUNT: int = 0
    LAST_DB_UPDATE: QDateTime = QDateTime.currentDateTime()

    preferedNumberThreads = DB_CONSTANTS.PREFERRED_NUMBER_THREADS
    maxNumberThreads = DB_CONSTANTS.MAX_NUMBER_THREADS
    minNumberThreads = DB_CONSTANTS.MIN_NUMBER_THREADS
    
    limit: int = ROW_COUNT
    
    filterOn: bool = False 
    data: List[Dict[str, Union[str, int]]] = []  
    executors: List[concurrent.futures.Executor] = []
    
    addresses: List[int] = []
    usedAddresses: List[int] = []
    knownIdents: Dict[str, int] = {}

    strFilter: str = " "
    
    backgroundFutures: List[concurrent.futures.Future] = []
    
    data:List[Dict[str, Union[str, float]]] = []
    
    def __init__(self, logger: Logger):        
        self.logger: Logger = logger
    
    def start(self) -> bool:
        self.logger.info("Starting database")
        started = True
        executor = self.__executor()
        try:
            self.__testDBConnection()
            rowCount__future = executor.submit(self.__getDBInformation)
            self.backgroundFutures.append(rowCount__future)
            self.mapAddressIndent()
        except DatabaseError as de:
            self.logger.critical(str(de))
            started = False
        finally:
            QtSql.QSqlDatabase.removeDatabase("testDB")

        executor.shutdown()
        return started
        
    def getData(self) -> List[Dict[str, Union[str, int]]]:
        return self.data
    
    def getMapping(self, addresses:List[int]) -> Dict[int, str]:
        mapping = {}
        for address in addresses:
            if self.knownIdents.get(address):
                mapping[str(address)] = self.knownIdents[address]
            else:
                self.logger.warning("No identification found for", address)
        return mapping 
    
    def cancel(self) -> True:
        for ex in self.executors:
            ex.shutdown(wait=False)
        return True
    
    def waitUntilReady(self) -> bool:
        concurrent.futures.wait(self.backgroundFutures)
        return True

    def setDatabaseParameters(self, **params):
        self.waitUntilReady()
        self.logger.info("Setting Database Parameters")
        strFilter = " "
        if params.get("limit"):
            if params["limit"] <= self.ROW_COUNT:
                self.limit = params["limit"]
            else:
                self.limit = self.ROW_COUNT
                self.logger.warning("Query limit bigger than row count of table")
        else:
            self.limit = 500000
        
        self.logger.log("Setting global query row limit to:", self.limit)

        if params.get("dbthreads_min"):
            self.minNumberThreads = params["dbthreads_min"]
        else:
            self.minNumberThreads = DB_CONSTANTS.MIN_NUMBER_THREADS
        if params.get("dbthreads_max"):
            self.maxNumberThreads = params["dbthreads_max"]
        else:
            self.maxNumberThreads = DB_CONSTANTS.MAX_NUMBER_THREADS
        if params.get("dbthreads"):
            self.preferedNumberThreads = params["dbthreads"]
        else:
            self.preferedNumberThreads = DB_CONSTANTS.PREFERRED_NUMBER_THREADS

        self.logger.log("Database number of threads || Min:", self.minNumberThreads,
                        "| Max:", self.maxNumberThreads, "| Preferred:", self.preferedNumberThreads, "||")

        if params.get("duration_limit"):
            self.logger.log("Setting duration limit to", params["duration_limit"] ,"minutes")
            lastPossibleTimestamp = self.LAST_DB_UPDATE.addSecs(-params["duration_limit"] * 60).toString("yyyy-MM-dd hh:mm:ss")
            strFilter += "tbl_mode_s.timestamp > '" + lastPossibleTimestamp + "'"
            self.logger.debug("Last possible timestamp  " + lastPossibleTimestamp)
            

        if params.get("bds"):
            strFilter += "tbl_mode_s.bds = " + params["bds"] + "AND"
            self.logger.log("Setting bds to", params["bds"])
        if params.get("latitude_minimal"):
            strFilter += "tbl_mode_s.latitude > " + params["latitude_minimal"] + " AND "
            self.logger.log("Setting minimal latitude to", params["latitude_minimal"])
        if params.get("latitude_maximal"):
            strFilter += "tbl_mode_s.latitude < " + params["latitude_maximal"] + " AND "
            self.logger.log("Setting maximal latitude to", params["latitude_maximal"])
        if params.get("longitude_minimal"):
            strFilter += "tbl_mode_s.longitude > " + params["longitude_minimal"] + " AND "
            self.logger.log("Setting minimal longitude to", params["longitude_minimal"])
        if params.get("longitude_maximal"):
            strFilter += "tbl_mode_s.longitude < " + params["longitude_maximal"] + " AND "
            self.logger.log("Setting maximal longitude to", params["longitude_maximal"])
        if params.get("id_minimal"):
            strFilter += "tbl_mode_s.id > " + params["id_minimal"] + " AND "
            self.logger.log("Setting minimal  to", params["id_minimal"])
        if params.get("id_maximal"):
            strFilter += "tbl_mode_s.id < " + params["id_maximal"] + " AND "
            self.logger.log("Setting maximal  to", params["id_maximal"])
            
        self.filterOn = strFilter != " "
        self.logger.debug("Setting query filter to: " + strFilter)
        self.strFilter = strFilter

    def resetFilter(self):
        self.filterOn = False
        
    def getFromDB(self, attributes: List[str] = [], options: Dict[str, str] = {"default_filter_on": False, "select_distinct": False, "not_null_values": []}) -> List[Dict[str, Union[int, str]]]:
        # option={..., "limit":50000}
        self.logger.debug("Getting attributes", ", ".join(attrib for attrib in attributes), "from Database")
        allResults = []
        executor = self.__executor()
        try:
            queries = self.__generateQueries(attributes, options) 
            threadedQueries = [executor.submit(self.__query, query, attributes) for query in queries]

            for completedQuery in concurrent.futures.as_completed(threadedQueries):
                try:
                    results, dbName = completedQuery.result()
                except DatabaseError as de:
                    self.logger.critical(str(de))
                except Exception as esc:
                    self.logger.warning("Error occurred while getting attributes " + str(attributes) + "\nERROR: " + str(esc))
                else:
                    allResults.extend(results)
                finally:
                    QtSql.QSqlDatabase.removeDatabase(dbName)

            try:
                limit = options["limit"]
            except KeyError:
                limit = self.limit
                    
            if len(allResults) < int(limit): self.logger.warning("Query executed. Results lower than expected (" + str(len(allResults)) + " < " + str(limit) + ")")
            else: self.logger.success("Query successfully executed.")

        except DatabaseError as de:
            self.logger.critical(str(de))
            return []
        finally:
            executor.shutdown()
        
        return allResults
    
    def mapAddressIndent(self) -> bool:
        self.logger.info("Actualizing known addresses")
        executor = self.__executor()
        valid = True
        try:
            idAndAddress__future = executor.submit(self.getFromDB, ["identification", "address"], options={
                                                 "select_distinct": True, "not_null_values": ["identification", "address"]})
            idAndAddress__future.add_done_callback(self.__actualizeKnownAddresses)

            self.backgroundFutures.append(idAndAddress__future)
        except DatabaseError as dbe:
            self.logger.critical(str(dbe))
            valid =  False
        except Exception as esc:
            self.logger.warning(
                "Error occurred while actualizing known addresses \nERROR: " + str(esc))
            valid = False
        finally:
            executor.shutdown()

        return valid
    
    def actualizeData(self) -> bool:
        self.logger.info("Actualizing database")
        self.logger.progress(LOGGER_CONSTANTS.DATABASE, "Actualizing Database [0/2]")
        executor = self.__executor()
        valid = True
        try:
            barAndIvv = self.getFromDB(["address", "timestamp", "bar", "ivv"], options={
                                              "not_null_values": ["bds60_barometric_altitude_rate", "bds60_inertial_vertical_velocity"], "limit": int(int(self.limit) / 2)})
            
            self.logger.progress(LOGGER_CONSTANTS.DATABASE, "Actualizing Database [1/2]")
            
            self.__updatedUsedAddresses(barAndIvv)

            latAndlon__future = executor.submit(self.getFromDB, ["address", "timestamp", "latitude", "longitude"], options={
                                              "not_null_values": ["latitude", "longitude"], "limit": int(int(self.limit) / 2)})
            
            self.data = barAndIvv
            self.data.extend(latAndlon__future.result())

            self.logger.progress(LOGGER_CONSTANTS.DATABASE, "Actualizing Database [2/2]")
            self.logger.success("Data actualized. Size: " + str(len(self.data)))

            # import json 
            # with open("database.dump.json", "w") as dbd:
            #     json.dump(self.data, dbd)

        except DatabaseError as dbe:
            self.logger.critical(str(dbe))
            valid = False
        except Exception as esc:
            self.logger.warning(
                "Error occurred while getting results \nERROR: " + str(esc))
            valid = False
        finally:
            self.logger.progress(LOGGER_CONSTANTS.DATABASE, LOGGER_CONSTANTS.END_PROGRESS_BAR)
            executor.shutdown()

        return valid


    def __executor(self) -> concurrent.futures.ThreadPoolExecutor: 
        ex = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="database_workerThread")
        self.executors.append(ex)
        return ex
    
    def __testDBConnection(self):
        db = QtSql.QSqlDatabase.addDatabase("QMYSQL", "testDB")
        self.__setUp(db)

        if db.open():
            self.logger.success("Database accessible")
            db.close()
        else:
            raise DatabaseError("Database not accessible")
    
    def __setUp(self, db: QtSql.QSqlDatabase):
        db.setDatabaseName(DB_CONSTANTS.DATABASE_NAME)
        db.setUserName(DB_CONSTANTS.USER_NAME)
        db.setPassword(DB_CONSTANTS.PASSWORD)
        if DB_CONSTANTS.HOSTNAME: db.setHostName(DB_CONSTANTS.HOSTNAME)

    def __getDBRowCount(self):
        count, dbName = self.__query("SELECT COUNT(*) AS rowCount FROM tbl_mode_s", ["rowCount"])
        self.ROW_COUNT = count[0]["rowCount"]

        if self.ROW_COUNT == 0:
            raise DatabaseError("Row count of Table tbl_mode_s should not be 0 !")
        self.logger.log("Row Count for table tbl_mode_s: " + str(self.ROW_COUNT))

        QtSql.QSqlDatabase.removeDatabase(dbName)

    def __query(self, query: str, elements: List[str] = []) -> List[Dict[str, Union[int, str]]]:
        DB_CONSTANTS.CONNECTIONS_TOTAL += 1
        name = "db_thread_" + str(DB_CONSTANTS.CONNECTIONS_TOTAL)
        db = QtSql.QSqlDatabase.addDatabase("QMYSQL", name)
        self.__setUp(db)
        if not db.open():
            raise DatabaseError("Database " + name +
                                " not accessible. ERROR:: " + db.lastError().text())

        self.logger.debug("New database connection: " + name)

        q = QtSql.QSqlQuery(db)
        q.setForwardOnly(True)
        if not q.exec_(query):
            raise DatabaseError(
                "Could not execute query: " + q.lastQuery() + " on " + name + " ERROR:: " + q.lastError().text())

        self.logger.debug("Executed query :: on :: " + name)

        allResults = []

        absentColumns = []
        for el in DB_CONSTANTS.USED_COLUMNS:
            if not el in elements:
                absentColumns.append(el)

        while q.next():
            entry = {abs: None for abs in absentColumns}
            for el in elements:
                value = q.value(el)
                if isinstance(value, str):
                    entry[el] = value.strip()
                elif isinstance(value, QDateTime):
                    entry[el] = value.toMSecsSinceEpoch() * 10**6
                else:
                    entry[el] = value
            if self.knownIdents:
                if self.knownIdents.get(entry["address"]):
                    entry["identification"] = self.knownIdents[entry["address"]]
            allResults.append(entry)

        self.logger.debug(len(allResults),"entries for query", str(q.lastQuery()))
        q.finish()
        q.clear()
        db.close()
        
        return allResults, name
    
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
                    raise DatabaseError(
                        "Attribute: " + attrib + "not valid")
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
            limit = options["limit"] if int(options["limit"]) <= self.ROW_COUNT else self.ROW_COUNT
        except KeyError:
            limit = self.limit
        
        dividing = int(limit) > DB_CONSTANTS.MAX_ROW_BEFORE_LONG_DURATION
        numThread = max(int(int(limit) / DB_CONSTANTS.MAX_ROW_BEFORE_LONG_DURATION), self.preferedNumberThreads) if dividing else self.minNumberThreads
        numThread = min(numThread, self.maxNumberThreads)

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
            
        orderStr = ""
        if not ident_run:
            orderStr = " ORDER BY timestamp "
            if len(attributes) == 1 and "timestamp" in attributes:
                orderStr += "DESC "
            else:
                orderStr += "ASC "

        self.logger.log(str(len(offsetStr))  + " threads for query for attributes", ", ".join(attrib for attrib in attributes))
        queries = [(selectStr + " FROM tbl_mode_s " + whereStr + orderStr + offset) for offset in offsetStr]
        return queries

    def __actualizeKnownAddresses(self, future: concurrent.futures.Future):
        id_address: List[Dict[str, Union[int, str]]] = future.result()
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
    
    def __updatedUsedAddresses(self, halfData: List[Dict[str, Union[int, str]]]) -> None:
        self.usedAddresses = []
        for el in halfData:
            if el["address"] in self.usedAddresses: continue
            self.usedAddresses.append(el["address"])
        self.filterOn = True 
        strFilter = " address IN (" + ",".join(str(address) for address in self.usedAddresses) + ") "
        if self.strFilter == " ": 
            self.strFilter = strFilter + " "
        else:
            self.strFilter += " AND " + strFilter + " "
            
        self.logger.log("Updated database filter")
        self.logger.debug("New filter is:" + self.strFilter)

    def __getLattestDBTimeStamp(self):
        time = self.getFromDB( ["timestamp"], options = {"not_null_values": ["timestamp"], "limit": 1})
        self.LAST_DB_UPDATE = QDateTime.fromMSecsSinceEpoch(int(time[0]["timestamp"]) / 10**6)
        self.logger.log("Lattest database db_airdata update: " + self.LAST_DB_UPDATE.toString("yyyy-MM-dd hh:mm:ss"))

    def __getDBInformation(self):
        self.__getDBRowCount()
        self.__getLattestDBTimeStamp()
