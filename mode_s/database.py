from PySide6 import QtSql
from PySide6.QtCore import QDateTime
from collections import namedtuple
import concurrent.futures

class DB_CONSTANTS:
    VALID_DB_COLUMNS = ["id", "timestamp", "frame_hex_chars", "address", "downlink_format", "bds", "on_ground", "adsb_version", "altitude", "altitude_is_barometric", "nuc_p", "latitude", "longitude", "nuc_r", "true_track", "groundspeed", "vertical_rate", "gnss_height_diff_from_baro_alt", "identification",
                        "category", "bds17_common_usage_gicb_capability_report", "bds50_roll_angle", "bds50_true_track_angle", "bds50_ground_speed", "bds50_track_angle_rate", "bds50_true_airspeed", "bds60_magnetic_heading", "bds60_indicated_airspeed", "bds60_mach", "bds60_barometric_altitude_rate", "bds60_inertial_vertical_velocity"]

    USED_COLUMNS = ["id", "identification", "address", "timestamp",
                    "bds", "altitude", "latitude", "longitude",  "bar", "ivv"]

    ROW = namedtuple("DB_ROW", USED_COLUMNS)
    
    HOSTNAME = "airdata.skysquitter.com"
    DATABASE_NAME = "db_airdata"
    USER_NAME = "tubs"
    PASSWORD = "ue73f5dn"
    
    CONNECTIONS_TOTAL = 0
class Database:
    def __init__(self, logger):        
        db = QtSql.QSqlDatabase.addDatabase("QMYSQL")
        self.__setUp(db)
        self.logger = logger
        self.filter = False
        self.data = []
        
        if db.open():
            self.logger.info("Database accessible")
            db.close()
        else: self.logger.critical("Database not accessible")
        
    def __setUp(self, db):
        db.setHostName(DB_CONSTANTS.HOSTNAME)
        db.setDatabaseName(DB_CONSTANTS.DATABASE_NAME)
        db.setUserName(DB_CONSTANTS.USER_NAME)
        db.setPassword(DB_CONSTANTS.PASSWORD)
        
    def __query(self, query):
        DB_CONSTANTS.CONNECTIONS_TOTAL += 1
        name = "db_thread_" + str(DB_CONSTANTS.CONNECTIONS_TOTAL)
        db = QtSql.QSqlDatabase.addDatabase("QMYSQL", name)
        self.__setUp(db)
        if not db.open() : 
            self.logger.critical("Database " + name + "not accessible", ConnectionError)
        
        self.logger.debug("New database connection with the name " + name)
        
        q = QtSql.QSqlQuery(db)
        if not q.exec(query):
            self.logger.critical("Could not execute query from database "+ name, ConnectionError)
        
        db.close()
        return q

    def __getAll(self, query = QtSql.QSqlQuery(), elements=[]):
        allResults = []
        while query.next():
            entry = {}
            for el in elements:
                value = query.value(el)
                if isinstance(value, str): entry[el] = value.strip()
                elif isinstance(value, QDateTime): entry[el] = value.toMSecsSinceEpoch() * 10**6
                else: entry[el] = value
            for abs in DB_CONSTANTS.USED_COLUMNS:
                if not abs in elements:
                    entry[abs] = None
            allResults.append(entry)
        return allResults
    
    def __isEmpty(self, entry={}):
        for el in entry.keys():
            if not str(entry[el]).isalnum():
                return False
        return True
    
    def __generateQuery(self, attributes, options):
        selectStr = "SELECT "
        try:
            if options["select_distinct"]:
                selectStr += "DISTINCT "
        except KeyError:
            pass

        for index, attrib in enumerate(attributes):
            if attrib == "bar": selectStr += "bds60_barometric_altitude_rate AS bar"
            elif attrib == "ivv": selectStr += "bds60_inertial_vertical_velocity AS ivv"
            else:
                if not attrib in DB_CONSTANTS.VALID_DB_COLUMNS:
                    self.logger.critical("Attribute: " + attrib + "not valid", ValueError)
                selectStr += attrib
            selectStr += ", " if index < (len(attributes) - 1) else " "

        self.logger.debug("Using following select string: " + selectStr)

        whereStr = "WHERE"
        try:
            if options["default_filter_on"]:
                whereStr += self.strFilter + " "
        except KeyError:
            pass
        try:
            if len(options["not_null_values"]) > 0:
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
        limitStr = "LIMIT " + str(limit)

        return selectStr + " FROM tbl_mode_s " + whereStr + limitStr

    def __actualizeKnownAddresses(self, id_address=[]):
        addresses = []
        self.known_idents = {}

        for el in id_address:
            address = el["address"]
            if address in addresses and not el["identification"].isalnum(): continue
            addresses.append(address)
            self.known_idents[address] = el["identification"]
            
        self.addresses = set(addresses)
        self.logger.debug("Kown Addresses: " + str(len(self.addresses)))

    def isOpen(self):
        return self.open


    def getData(self):
        return self.data
            
    def setFilter(self, params={}):
        self.filter = True
        strFilter = " "
        for index, el in enumerate(params.keys()):
            if el == "limit":
                self.limit = params["limit"]
                self.logger.debug(
                    "Setting engine default query limit to: " + self.limit)
                continue
            strFilter += el + " = " + params[el]
            strFilter += " AND " if index < (len(params.keys()) - 1) else " "

        self.logger.debug("Setting engine filter to: " + strFilter)
        self.strFilter = strFilter

    def getFromDB(self, attributes=[], options={"default_filter_on": False, "select_distinct": False, "not_null_values": []}):
    # option={..., "limit":50000}
        query = self.__generateQuery(attributes, options)

        self.logger.debug("Executing following querry: " + query)

        try:
            results = self.__query(query)
        except ConnectionError:
            self.logger.warning("Could not run query " + query)
            
        self.logger.info("Query successfully excecuted")
        return self.__getAll(results, attributes)
        

    def actualizeData(self):
        try:
            lat_lon = bar_ivv = []
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                id_address__future = executor.submit(self.getFromDB, ["identification", "address"], options={
                                                     "select_distinct": True, "not_null_values": ["identification", "address"]})

                lat_lon__future = executor.submit(self.getFromDB, ["id", "address", "timestamp", "bds", "altitude", "latitude", "longitude"], options={
                                                  "not_null_values": ["bds", "altitude"]})

                bar_ivv__future = executor.submit(self.getFromDB, ["id", "address", "timestamp", "bds", "altitude", "bar", "ivv"], options={
                                                  "not_null_values": ["bds60_barometric_altitude_rate", "bds60_inertial_vertical_velocity"]})

                id_address = id_address__future.result()
                actualizing__thread = executor.submit(self.__actualizeKnownAddresses, id_address)

                lat_lon = lat_lon__future.result()
                bar_ivv = bar_ivv__future.result() 
                all_data_raw = lat_lon + bar_ivv
                
            
            skipped = 0
            for i in range(len(all_data_raw)):
                address = all_data_raw[i]["address"]
                if address in self.addresses:
                    all_data_raw[i]["identification"] = self.known_idents[address]
                else: 
                    skipped += 1
                    continue
                self.data.append(DB_CONSTANTS.ROW(**all_data_raw[i]))
            
            if skipped > 0: self.logger.warning("Skipped " + str(skipped) + " entries. Identification(s) unknown")

            self.logger.info("Data actualized. Size: " + str(len(self.data)))
            return True
        
                
        except ConnectionError:
            self.logger.warning("Could not actualize Addresses")
            return False
