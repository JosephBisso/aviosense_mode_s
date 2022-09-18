from PySide2 import QtSql
from typing import List, Dict, Union
from constants import DB_CONSTANTS
from PySide2.QtCore import QDateTime

def query(queries: List[str], elements: List[str] = [], knownIdents: Dict[str,str]={}, query_id:int = 0) -> List[Dict[str, Union[int, str]]]:
    name = "db_process_" + str(query_id)

    db = QtSql.QSqlDatabase.addDatabase("QMYSQL", name)
    db.setDatabaseName(DB_CONSTANTS.DATABASE_NAME)
    db.setUserName(DB_CONSTANTS.USER_NAME)
    db.setPassword(DB_CONSTANTS.PASSWORD)
    if DB_CONSTANTS.HOSTNAME: 
        db.setHostName(DB_CONSTANTS.HOSTNAME)

    if not db.open():
        raise ConnectionError("Database " + name +
                            " not accessible. ERROR:: " + db.lastError().text())

    allQueriesResults = []

    q = QtSql.QSqlQuery(db)
    q.setForwardOnly(True)
    
    absentColumns = [column for column in DB_CONSTANTS.USED_COLUMNS if column not in elements]
    emptyEntry = {abs: None for abs in absentColumns}

    for query in queries:
        if not q.exec_(query):
            raise ConnectionError(
                "Could not execute query: " + q.lastQuery() + " on " + name + " ERROR:: " + q.lastError().text())

        while q.next():
            entry = emptyEntry
            for el in elements:
                value = q.value(el)
                if isinstance(value, str):
                    entry[el] = value.strip()
                elif isinstance(value, QDateTime):
                    entry[el] = value.toMSecsSinceEpoch() * 10**6
                else:
                    entry[el] = value
            if knownIdents:
                if knownIdents.get(entry["address"]):
                    entry["identification"] = knownIdents[entry["address"]]

            allQueriesResults.append(entry)
        
    q.finish()
    q.clear()

    db.close()

    return allQueriesResults, name
