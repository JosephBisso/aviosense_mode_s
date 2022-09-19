from PySide2 import QtSql
from PySide2.QtCore import QDateTime

from typing import List, Dict, Union

from constants import DB_CONSTANTS, DATA, LOCATION_DATA, WINDOW_DATA

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

    for query in queries:
        if not q.exec_(query):
            raise ConnectionError(
                "Could not execute query: " + q.lastQuery() + " on " + name + " ERROR:: " + q.lastError().text())

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
                    
            if knownIdents and knownIdents.get(entry["address"]):
                entry["identification"] = knownIdents[entry["address"]]

            allQueriesResults.append(entry)
        
    q.finish()
    q.clear()

    db.close()

    return allQueriesResults, name

def getRawData(addresses: List[int], data: List[Dict[str, Union[str, float]]] = []) -> List[Dict[str, Union[str, List[DATA]]]]:
    results = []
    startIndexes = {address:None for address in addresses}

    for index in range(len(data)):
        if data[index]["address"] in startIndexes:
            if startIndexes.get(data[index]["address"]) is None:
                startIndexes[data[index]["address"]] = index

        if not 0 in startIndexes.values() and all(startIndexes.values()):
            break
        elif 0 in startIndexes.values():
            allIndexesFound = True
            for value in startIndexes.values():
                if value is None: 
                    allIndexesFound = False
                    break
            if allIndexesFound:
                break
    
    for address in addresses:
        addressData: Dict[str, Union[str, List[int]]] = {
            "address": address,
            "points": []
        }

        identification = None
        bars = []
        ivvs = []
        times = []

        startIndex = startIndexes[address]

        if startIndex is None:
            raise AssertionError("Skipping address " +
                                str(address) + " : Cannot be found")

        identification = data[index].get("identification")

        for index in range(startIndex, len(data)):
            if data[index]["bar"] is None or data[index]["ivv"] is None:
                continue
            if data[index]["address"] != address:
                break
            bars.append(data[index]["bar"])
            ivvs.append(data[index]["ivv"])
            times.append(data[index]["timestamp"])

        if not times:
            raise AssertionError("Skipping address " +
                                str(address) + " : No valid entry")

        startTime = min(times)
        addressData["points"] = [
            DATA((times[i] - startTime)*10**-9, bars[i], ivvs[i]) for i in range(len(times))]
        addressData["points"].sort(key=lambda el: el.time)
        addressData["identification"] = identification

        results.append(addressData)

    return results


def getHeatPoints(addressDataList: List[Dict[str, Union[str, List[WINDOW_DATA]]]] = [], data: List[Dict[str, Union[str, float]]] = []) -> List[Dict[str, Union[str,List[LOCATION_DATA]]]]:
    results = []
    startIndexes = {address: None for address in [addressData["address"] for addressData in addressDataList]}

    for index in range(len(data)):
        if data[index]["address"] in startIndexes:
            if startIndexes.get(data[index]["address"]) is None:
                startIndexes[data[index]["address"]] = index

        if not 0 in startIndexes.values() and all(startIndexes.values()):
            break
        elif 0 in startIndexes.values():
            allIndexesFound = True
            for value in startIndexes.values():
                if value is None:
                    allIndexesFound = False
                    break
            if allIndexesFound:
                break

    for addressData in addressDataList:
        heatPointsForAddress: List[str, List[LOCATION_DATA]] = []
        
        turbulentSlidingWindows = [point.window for point in addressData["points"] if point.bar - point.ivv > addressData["threshold"]]
        turbulentSlidingWindows.sort()
        
        times = []

        startIndex = startIndexes[addressData["address"]]

        if startIndex is None:
            raise AssertionError("Skipping address " + str(addressData["address"]) + " : Invalid bar or ivv stds for heat map")

        for index in range(startIndex, len(data)):
            if data[index]["address"] != addressData["address"]:
                break
            times.append(data[index]["timestamp"])
            
        if not times:
            raise AssertionError("Skipping address " + str(addressData["address"]) + " : not times for heat map")

        startTime = min(times)

        foundLongitude = False
        foundWindow = False
        closestTimes = []
        allTimes = []
        for index in range(startIndex, len(data)):
            if data[index]["longitude"] is None or data[index]["latitude"] is None:
                continue
            if data[index]["address"] != addressData["address"]:
                break

            foundLongitude = True

            rawTime = data[index]["timestamp"]
            time = (rawTime - startTime)*10**-9
            time /= 60
            allTimes.append(time)

            windows = None
            for window in turbulentSlidingWindows:
                if time > window: continue
                windows = window
                break
            
            if not windows: break
            
            foundWindow = True
            if time < windows - 1: 
                closestTimes.append(time)
                continue
            
            longitude = data[index]["longitude"]
            latitude = data[index]["latitude"]
            
            heatPointsForAddress.append(
                LOCATION_DATA(time, longitude, latitude)
            )
            
        if allTimes: closestTimes.insert(0, min(allTimes))
        

        results.append({"address": addressData["address"], "identification": addressData.get("identification"),  "points": heatPointsForAddress})
        
    return results
