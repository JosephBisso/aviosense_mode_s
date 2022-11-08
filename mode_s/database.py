from PySide2.QtCore import QDateTime
from PySide2 import QtSql

import multiprocessing
import concurrent.futures
from typing import List, Dict, Union

import process
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
    
    data: List[Dict[str, Union[str, int]]] = []  
    executors: List[concurrent.futures.ThreadPoolExecutor] = []
    pExecutor: concurrent.futures.ProcessPoolExecutor = None
    
    addresses: List[int] = []
    usedAddresses: List[int] = []
    knownIdents: Dict[str, int] = {}

    strFilter: str = DB_CONSTANTS.EMPTY_FILTER
    filterOn: bool = False 
    filterDictList: List[str] = []
    
    backgroundFutures: List[concurrent.futures.Future] = []
    
    data:List[Dict[str, Union[str, float]]] = []
    
    login: Dict[str, str] = {
        "host_name": None,
        "db_port": None,
        "db_name": None,
        "user_name": None,
        "table_name": None,
        "password": None
    }
    
    validDBColumns: Dict[str, str] = {
        "bar": "bds60_barometric_altitude_rate",
        "ivv": "bds60_inertial_vertical_velocity",
    }
    
    def __init__(self, logger: Logger):        
        self.logger: Logger = logger
    
    def start(self) -> bool:
        self.logger.info("Starting database")
        self.logger.progress(LOGGER_CONSTANTS.DATABASE, "Starting Database Connector")
        started = True
        executor = self.__executor()
        try:
            rowCount__future = executor.submit(self.__getDBInformation)
            rowCount__future.add_done_callback(self.__backgroundWorkFinished)
            self.backgroundFutures.append(rowCount__future)
            self.mapAddressIndent()
        except DatabaseError as de:
            self.logger.critical(str(de))
            started = False

        executor.shutdown()
        return started
    
    def setProcessExecutor(self, ex: concurrent.futures.ProcessPoolExecutor):
        self.pExecutor = ex
        
    def getData(self) -> List[Dict[str, Union[str, int]]]:
        return self.data
    
    def getMapping(self, addresses:List[int]) -> Dict[int, str]:
        mapping = {}
        unknownIdents = []
        for address in addresses:
            if self.knownIdents.get(address):
                mapping[str(address)] = self.knownIdents[address]
            else:
                mapping[str(address)] = DB_CONSTANTS.NO_IDENTIFICATION
                unknownIdents.append(address)

        if unknownIdents: self.logger.warning("No identification found for: ", unknownIdents)
        return mapping 
    
    def cancel(self) -> True:
        for ex in self.executors:
            ex.shutdown(wait=False)
        return True
    
    def waitUntilReady(self) -> bool:
        concurrent.futures.wait(self.backgroundFutures)
        return True
    
    def setLogin(self, **loginData) -> bool:
        Done = True
        for el in loginData:
            self.login[el] = loginData[el]
            
        try:
            self.__testDBConnection()
            self.logger.log("Login Info")
            for el in loginData:
                self.logger.log(f"{el}  \t: {self.login[el]}")
        except DatabaseError:
            Done = False
        finally:
            QtSql.QSqlDatabase.removeDatabase("testDB")
            return Done
        
    def setValidDBColumnsNames(self, **dbColumnsName) -> bool:
        for el in dbColumnsName:
            self.login[el] = dbColumnsName[el]
        
        self.logger.log(f"Using Following Columns Name")
        for el in dbColumnsName:
            self.logger.log(f"{el}  \t-> {self.login[el]}")
            
    def setDatabaseParameters(self, **params):
        self.waitUntilReady()
        self.logger.info("Setting Database Parameters")
        self.__resetFilter()
        
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
            self.strFilter = self.__addFilter(f"{self.login['table_name']}.timestamp >= '{lastPossibleTimestamp}'", attribute="timestamp")
            self.logger.debug("Last possible timestamp  " + lastPossibleTimestamp)

        if params.get("latitude_min"):
            self.strFilter = self.__addFilter(f"{self.login['table_name']}.latitude >= {params['latitude_min']}", attribute="latitude")
            self.logger.log("Setting minimal latitude to", params["latitude_min"])
        if params.get("latitude_max"):
            self.strFilter = self.__addFilter(f"{self.login['table_name']}.latitude <= {params['latitude_max']}", attribute="latitude")
            self.logger.log("Setting maximal latitude to", params["latitude_max"])
        if params.get("longitude_min"):
            self.strFilter = self.__addFilter(f"{self.login['table_name']}.longitude >= {params['longitude_min']}", attribute="longitude")
            self.logger.log("Setting minimal longitude to", params["longitude_min"])
        if params.get("longitude_max"):
            self.strFilter = self.__addFilter(f"{self.login['table_name']}.longitude <= {params['longitude_max']}", attribute="longitude")
            self.logger.log("Setting maximal longitude to", params["longitude_max"])
        if params.get("id_min"):
            self.strFilter = self.__addFilter(f"{self.login['table_name']}.id >= {params['id_min']}", attribute="id")
            self.logger.log("Setting minimal  to", params["id_min"])
        if params.get("id_max"):
            self.strFilter = self.__addFilter(f"{self.login['table_name']}.id <=  {params['id_max']}", attribute="id")
            self.logger.log("Setting maximal  to", params["id_max"])
            
        self.logger.info("Setting query filter to: " + self.strFilter)

    def resetFilter(self):
        self.filterOn = False
        
    def getFromDB(self, attributes: List[str] = [], options: Dict[str, str] = {"default_filter_on": False, "select_distinct": False, "not_null_values": []}) -> List[Dict[str, Union[int, str]]]:
        # option={..., "limit":50000}
        self.logger.debug("Getting attributes", ", ".join(attrib for attrib in attributes), "from Database")
        allResults = []
        dbName = None
        try:
            queries = self.__generateQueries(attributes, options) 
            threadedQueries = []
            maxProcesses = min(len(queries), multiprocessing.cpu_count() + 1) or 1
            queriesPerProcess = int(len(queries) / maxProcesses)
            for i in range(maxProcesses):
                DB_CONSTANTS.CONNECTIONS_TOTAL += 1
                startIndex = i*queriesPerProcess
                endIndex = None if i == maxProcesses - 1 else startIndex + queriesPerProcess
                pack = queries[startIndex : endIndex]
                if not pack:
                    continue
                connectionTotal = DB_CONSTANTS.CONNECTIONS_TOTAL
                threadedQueries.append(self.pExecutor.submit(process.query, pack, attributes, self.knownIdents, connectionTotal, self.login))
                
            for completedQuery in concurrent.futures.as_completed(threadedQueries):
                try:
                    results, dbName = completedQuery.result()
                except ConnectionError as de:
                    self.logger.critical("Error occurred while getting attributes " + str(attributes))
                    self.logger.critical(str(de))
                except Exception as esc:
                    self.logger.warning("Error occurred while getting attributes " + str(attributes) + "\nERROR: " + str(esc))
                else:
                    allResults.extend(results)
                finally:
                    if dbName:
                        QtSql.QSqlDatabase.removeDatabase(dbName)

            limit = options.get("limit") or self.limit
                    
            if len(allResults) < int(limit): self.logger.warning("Query executed. Results lower than expected (" + str(len(allResults)) + " < " + str(limit) + ")")
            else: self.logger.success("Query successfully executed.")

        except DatabaseError as de:
            self.logger.critical(str(de))
            return []
        # finally:
        #     self.pExecutor.shutdown()
            
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
        except ConnectionError as dbe:
            self.logger.critical("Error occurred while actualizing known addresses")
            self.logger.critical(str(dbe))
            valid =  False
        except Exception as esc:
            self.logger.warning("Error occurred while actualizing known addresses \nERROR: " + str(esc))
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
                "not_null_values": [self.validDBColumns["bar"], self.validDBColumns["ivv"]], "limit": int(int(self.limit) / 2)})
            
            self.logger.progress(LOGGER_CONSTANTS.DATABASE, "Actualizing Database [1/2]")
            
            self.__updatedUsedAddresses(barAndIvv)

            latAndlon__future = executor.submit(self.getFromDB, ["address", "timestamp", "latitude", "longitude"], options={
                "not_null_values": ["latitude", "longitude"], "limit": int(int(self.limit) / 2)})

            self.data = barAndIvv
            self.data.extend(latAndlon__future.result())

            self.logger.progress(LOGGER_CONSTANTS.DATABASE, "Actualizing Database [2/2]")
            self.logger.success(f"Data actualized. Size: {len(self.data)}")

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
        db.setDatabaseName(self.login["db_name"])
        db.setUserName(self.login["user_name"])
        db.setPassword(self.login["password"])
        if self.login.get("host_name"):
            db.setHostName(self.login["host_name"])
        if self.login.get("db_port"):
            db.setPort(self.login["db_port"])

    def __getDBRowCount(self):
        count, dbName = self.__query(f"SELECT COUNT(*) AS rowCount FROM {self.login['table_name']}", ["rowCount"])
        self.ROW_COUNT = count[0]["rowCount"]

        if self.ROW_COUNT == 0:
            raise DatabaseError(f"Row count of Table {self.login['table_name']} should not be 0 !")
        self.logger.log(f"Row Count for table {self.login['table_name']}: " + str(self.ROW_COUNT))

        QtSql.QSqlDatabase.removeDatabase(dbName)

    def __query(self, query: str, elements: List[str] = []) -> List[Dict[str, Union[int, str]]]:
        DB_CONSTANTS.CONNECTIONS_TOTAL += 1
        name = "db_thread_" + str(DB_CONSTANTS.CONNECTIONS_TOTAL)
        db = QtSql.QSqlDatabase.addDatabase("QMYSQL", name)
        self.__setUp(db)
        if not db.open():
            raise DatabaseError("Database " + name +
                                " not accessible. ERROR:: " + db.lastError().text())

        # self.logger.debug("New database connection: " + name)

        q = QtSql.QSqlQuery(db)
        q.setForwardOnly(True)
        if not q.exec_(query):
            raise DatabaseError(
                "Could not execute query: " + q.lastQuery() + " on " + name + " ERROR:: " + q.lastError().text())

        # self.logger.debug("Executed query :: on :: " + name)

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

        # self.logger.debug(len(allResults),"entries for query", str(q.lastQuery()))
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
                selectStr += f"{self.validDBColumns['bar']} AS bar"
            elif attrib == "ivv":
                selectStr += f"{self.validDBColumns['ivv']} AS ivv"
            else:
                selectStr += attrib
            selectStr += ", " if index < (len(attributes) - 1) else " "

        whereStr = DB_CONSTANTS.EMPTY_FILTER
        if options.get("default_filter_on") is not None or self.filterOn:
            whereStr = self.__adaptDefaultFilter(*attributes)
        
        ident_run = False
        if options.get("not_null_values") is not None and len(options["not_null_values"]) > 0:
            if "identification" in options["not_null_values"] and "address" in options["not_null_values"]:
                ident_run = True
                whereStr = DB_CONSTANTS.EMPTY_FILTER
            
            for index, attrib in enumerate(options["not_null_values"]):
                whereStr = self.__addFilter(f"{attrib} IS NOT NULL", attribute=attrib, target=whereStr)

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

        self.logger.log(str(len(offsetStr))  + " sub queries for attributes", ", ".join(attrib for attrib in attributes))

        allUsedAddressFilter = []
        if self.usedAddresses and len(self.usedAddresses) >= numThread:
            numAddressPerQuery = int(len(self.usedAddresses)/numThread)
            for i in range(numThread):
                startIndex = i*numAddressPerQuery
                endIndex = None if i == numThread - 1 else startIndex + numAddressPerQuery
                partialAddressList = self.usedAddresses[startIndex: endIndex]
                addressFilter = self.__addFilter(" address IN (" + ",".join(
                    str(address) for address in partialAddressList) + ") ", target=whereStr)

                allUsedAddressFilter.append(addressFilter)
                offsetStr = f" LIMIT {int(limit / 2)}" # Same Limit for all
                
                if endIndex is None and rest > 0:
                    allUsedAddressFilter.append(addressFilter) #Adding duplicate
    
        if allUsedAddressFilter:
            queries = [(selectStr + f" FROM {self.login['table_name']} " + usedAddressFilter + orderStr + offsetStr) for usedAddressFilter in allUsedAddressFilter]
        else:
            queries = [(selectStr + f" FROM {self.login['table_name']} " + whereStr + orderStr + offset) for offset in offsetStr]

        # queries = [(selectStr + f" FROM {self.login['table_name']} " + whereStr + orderStr + offset) for offset in offsetStr]

        for query in queries:
            self.logger.debug(query)

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
            
        if not self.usedAddresses:
            self.logger.warning("No address to update")
            return
        
        # self.strFilter = self.__addFilter(" address IN (" + ",".join(str(address)
        #                  for address in self.usedAddresses) + ") ", attribute="address")
            
        self.logger.log("Updated database filter")
        self.logger.debug(f"New filter is: {self.strFilter}")

    def __getLattestDBTimeStamp(self):
        time = self.getFromDB( ["timestamp"], options = {"not_null_values": ["timestamp"], "limit": 1})
        if time:
            self.LAST_DB_UPDATE = QDateTime.fromMSecsSinceEpoch(int(time[0]["timestamp"]) / 10**6)
            self.logger.log(f"Latest database {self.login['db_name']} update: " + self.LAST_DB_UPDATE.toString("yyyy-MM-dd hh:mm:ss"))
        else:
            self.logger.warning("Could not fetch latest database update. Using current date as latest update")

    def __getDBInformation(self):
        self.__getDBRowCount()
        self.__getLattestDBTimeStamp()

    def __backgroundWorkFinished(self, future: concurrent.futures.Future):
        future.result()
        self.logger.progress(LOGGER_CONSTANTS.DATABASE, LOGGER_CONSTANTS.END_PROGRESS_BAR)

    def __addFilter(self, filter, attribute=None, target=None):
        if target is None:
            self.filterOn = True
            target = self.strFilter
            self.filterDictList.append({"attribute": attribute, "filter": filter})

        if target != DB_CONSTANTS.EMPTY_FILTER:
            target += " AND "

        target += f" {filter} "
        
        self.logger.debug(f"Adding filter for attribute {attribute}: {filter}")
        
        return target
            
    def __resetFilter(self):
        self.strFilter = DB_CONSTANTS.EMPTY_FILTER
        self.filterOn = False

    def __adaptDefaultFilter(self, *attributes) -> str:
        adaptedFilter = DB_CONSTANTS.EMPTY_FILTER
        for filterDict in self.filterDictList:
            if filterDict["attribute"] in attributes:
                adaptedFilter = self.__addFilter(filter=filterDict["filter"], target=adaptedFilter, attribute=filterDict["attribute"])
        if adaptedFilter == DB_CONSTANTS.EMPTY_FILTER:
            self.logger.debug("No adapted filter")
        
        self.logger.debug(f"Using this adapted filter: {adaptedFilter}")
        return adaptedFilter
        