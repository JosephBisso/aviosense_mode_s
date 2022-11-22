from PySide2.QtCore import QDateTime

from mysql.connector.connection import MySQLConnection

import numpy as np
from sklearn.neighbors import KernelDensity

from typing import List, Dict, Union
from datetime import datetime

from mode_s.constants import DB_CONSTANTS, DATA, LOCATION_DATA, WINDOW_DATA

def query(queries: List[str], elements: List[str] = [], knownIdents: Dict[str,str]={}, query_id:int = 0, login: Dict[str, str] = {}) -> List[Dict[str, Union[int, str]]]:
    name = "db_process_" + str(query_id)
    last_query = None
    try:
        db = MySQLConnection(
            user=login.get("user_name"),
            password=login.get("password"),
            host=login.get("host_name", "127.0.0.1"),
            port=login.get("db_port", 3306),
            database=login.get("db_name")
        )

        if not db.is_connected():
            raise ConnectionError("Database " + name +" not accessible.")

        allQueriesResults = []

        q = db.cursor(dictionary=True)
        absentColumns = [column for column in DB_CONSTANTS.USED_COLUMNS if column not in elements]

        for query in queries:
            q.execute(query)
            last_query = query

            for row in q:
                entry = {abs: None for abs in absentColumns}
                for el in elements:
                    value = row.get(el)
                    if isinstance(value, str):
                        entry[el] = value.strip()
                    elif isinstance(value, datetime):
                        entry[el] = QDateTime(value).toMSecsSinceEpoch() * 10**6
                    else:
                        entry[el] = value
                        
                if entry.get("identification") is None:
                    if knownIdents and knownIdents.get(entry["address"]):
                        entry["identification"] = knownIdents[entry["address"]]
                    else:
                        entry["identification"] = DB_CONSTANTS.NO_IDENTIFICATION

                allQueriesResults.append(entry)

        q.close()
        db.close()
        
    except Exception as ex:
        raise ConnectionError(
            f"Error (Exception: {ex}) occured while running following query: {last_query}")

    return allQueriesResults

def getRawData(addresses: List[int], data: List[Dict[str, Union[str, float]]] = []) -> List[Dict[str, Union[str, List[DATA]]]]:
    results = []
    startIndexes = {address:False for address in addresses}
    lenStartIndexes = len(startIndexes)
    counterAllIndexes = 0

    for index in range(len(data)):
        addressInList = startIndexes.get(data[index]["address"]) 
        if addressInList is not None and addressInList is False:
            startIndexes[data[index]["address"]] = index
            counterAllIndexes += 1

        if counterAllIndexes == lenStartIndexes:
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

        if startIndex is False:
            raise AssertionError("Skipping address " +
                                str(address) + " : Cannot be found")

        identification = data[startIndex].get("identification")

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
    startIndexes = {address: {"startIndex": False, "times": []} for address in [addressData["address"] for addressData in addressDataList]}

    for index in range(len(data)):
        address = data[index]["address"]
        addressInList = startIndexes.get(address)
        if addressInList is not None:
            if addressInList["startIndex"] is False:
                startIndexes[address]["startIndex"] = index
            
            startIndexes[address]["times"].append(data[index]["timestamp"])


    for addressData in addressDataList:
        heatPointsForAddress: List[str, List[LOCATION_DATA]] = []
        
        turbulentSlidingWindows = [point.window for point in addressData["points"] if point.bar - point.ivv > addressData["threshold"]]
        turbulentSlidingWindows.sort()
        
        startIndex = startIndexes[addressData["address"]]["startIndex"]

        if startIndex is False:
            raise AssertionError("Skipping address " + str(addressData["address"]) + " : Invalid bar or ivv stds for heat map")

        times = startIndexes[addressData["address"]]["times"]
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

            windowStart = None
            windowEnd = None
            for point in addressData["points"]:
                if windowStart is not None and windowEnd is not None:
                    break
                if point.window <= zoneData[actualAddress]["start"]: 
                    windowStart = point.window if windowStart is None else max(point.window, windowStart)
                if point.window >= zoneData[actualAddress]["end"]: 
                    windowEnd = point.window if windowEnd is None else min(point.window, windowEnd)
                    
            if windowStart is None or windowEnd is None:
                continue
            
            allDiffs = [point.bar - point.ivv for point in addressData["points"] if windowStart <= point.window <= windowEnd]

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
