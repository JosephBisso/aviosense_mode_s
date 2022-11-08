from PySide2 import QtSql
from PySide2.QtCore import QDateTime

import numpy as np
from sklearn.neighbors import KernelDensity

from typing import List, Dict, Union

from constants import DB_CONSTANTS, DATA, LOCATION_DATA, WINDOW_DATA

def query(queries: List[str], elements: List[str] = [], knownIdents: Dict[str,str]={}, query_id:int = 0, login: Dict[str, str] = {}) -> List[Dict[str, Union[int, str]]]:
    name = "db_process_" + str(query_id)

    db = QtSql.QSqlDatabase.addDatabase("QMYSQL", name)
    db.setDatabaseName(login["db_name"])
    db.setUserName(login["user_name"])
    db.setPassword(login["password"])
    if login.get("host_name"):
        db.setHostName(login["host_name"])
    if login.get("db_port"):
        db.setPort(login["db_port"])

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
                    
            if entry.get("identification") is None:
                if knownIdents and knownIdents.get(entry["address"]):
                    entry["identification"] = knownIdents[entry["address"]]
                else:
                    entry["identification"] = DB_CONSTANTS.NO_IDENTIFICATION

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


def getAllAddressSeriesMap(allSeriesMap, allAddressSeriesMap, allSeries):
    for series in allSeries:
        for addressSeries in allSeriesMap[series]:
            address = addressSeries["address"]
            if allAddressSeriesMap.get(str(address)) is None:
                allAddressSeriesMap[str(address)] = {series: None for series in allSeries}
            allAddressSeriesMap[str(address)][series] = addressSeries
            
    return allAddressSeriesMap


def getKDEExceeds(kdeZones: List[Dict[str, Union[float, List[Dict[str, float]]]]], slidingIntervallForStd: List[Dict[str, Union[str, List[WINDOW_DATA]]]] = [], bandwidth = 1) -> Dict[str, Dict[str, Union[str, List[float]]]]:
    lineSeriesKDEExceeds = {}

    for i in range(len(kdeZones)):
        kdeZone = kdeZones[i]
        zoneData = kdeZone["zoneData"]
        zoneID = kdeZone["zoneID"]

        zoneAddresses = list(zoneData.keys())
        
        maxX = 1000

        allExceedingData = []
        
            
        zoneAddressesDataRead = {address: False for address in zoneAddresses}
        for addressData in slidingIntervallForStd:
            if all(list(zoneAddressesDataRead.values())): break
            
            if addressData["address"] not in zoneAddresses: continue

            exceedingData: Dict[str, Union[str, Dict[int, int]]] = {
                "address": addressData["address"],
                "identification": addressData.get("identification"),
                "start": zoneData[addressData["address"]]["start"],
                "end": zoneData[addressData["address"]]["end"],
                "smoothed": [],
                "series": []
            }

            threshold = addressData["threshold"]

            if threshold == 0:
                continue

            actualAddress = addressData["address"]

            allDiffs = [point.bar - point.ivv for point in addressData["points"] if zoneData[actualAddress]["start"] <= point.window <= zoneData[actualAddress]["end"]]

            if not allDiffs:
                continue
            
            exceeds = [100*(diff - threshold)/threshold for diff in allDiffs if diff >= threshold]

            if not exceeds:
                continue
            
            exceedingPercentageGroup = []
            sizeRatio = 10

            for exceedingPercentage in exceeds:
                percentage = next((dist for dist in [0,10,20,30,40,50,60,70,80,90,100] if dist <= exceedingPercentage < dist + 10), 100)
                exceedingPercentageGroup.append(percentage/sizeRatio)

            exceedsShape = np.array(exceedingPercentageGroup).reshape(-1, 1)
            Xs = np.linspace(0, 100/sizeRatio, num=maxX).reshape(-1, 1)

            kde = KernelDensity(kernel="gaussian",bandwidth=bandwidth).fit(exceedsShape)
            density = np.exp(kde.score_samples(Xs))
            norm = np.linalg.norm(density)

            exceedingData["smoothed"] = density.tolist()
            kdeZone["exceedsPerAddress"].append(exceedingData)

            allExceedingData.append({"densities": (density/norm).tolist(), "norm": float(norm)})

        globalDensity = [sum(component["densities"][i] * component["norm"] for component in allExceedingData) for i in range(maxX)]

        kdeZone["kde"] = globalDensity
        lineSeriesKDEExceeds[zoneID] = kdeZone

    return lineSeriesKDEExceeds
