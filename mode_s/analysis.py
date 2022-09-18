from cmath import sqrt
from typing import List, Dict, NamedTuple, Union
import statistics
from unicodedata import category

from sklearn.neighbors import KernelDensity
import numpy as np

from PySide2 import QtPositioning

from constants import DATA, WINDOW_POINT, WINDOW_DATA, LOCATION_DATA

class Analysis:
    KDE_BAND_WIDTH: int = 0.5
    POINT_RADIUS = 10000
    
    SLIDING_INTERVAL_PER_STD = []
    KDE_ZONE_EXCEEDS = []

    def setKDEBandwidth(bandwidth:int = 0.5):
        Analysis.KDE_BAND_WIDTH = bandwidth

    def getLineSeriesDataPointOccurrences(occurrences: List[Union[str, int]]) -> List[int]:
        return occurrences 

    def getLineSeriesBarAndIvv(plotData: List[Dict[str, Union[str, List[DATA]]]]) -> List[Dict[str, List[int]]]:
        lineSeries = []
        for index in range(len(plotData)):
            addressSeries = {
                "address": plotData[index]["address"],
                "identification": plotData[index].get("identification"),
                "bar":[], "ivv": [], "time": []
            }

            time = list(map(lambda el: el/60, [point.time for point in plotData[index]["points"]]))
            bar = [point.bar for point in plotData[index]["points"]]
            ivv = [point.ivv for point in plotData[index]["points"]]

            addressSeries["bar"] = bar
            addressSeries["ivv"] = ivv
            addressSeries["time"] = time
            
            lineSeries.append(addressSeries)
            
        return lineSeries

    def getLineSeriesFilteredBarAndIvv(plotData: List[Dict[str, Union[str, List[DATA]]]]) -> List[Dict[str, List[int]]]:
        lineSeries = []
        for index in range(len(plotData)):
            addressSeries = {
                "address": plotData[index]["address"],
                "identification": plotData[index].get("identification"),
                "points": [
                    {
                        "dataSet": "BAR",
                        "raw": [],
                        "filtered": [],
                        "time": []
                    },
                    {
                        "dataSet": "IVV",
                        "raw":[],
                        "filtered":[],
                        "time": []
                    }    
                ]
            }

            time = list(map(lambda el: el/60, [point.time for point in plotData[index]["points"]]))
            bar = [point.bar for point in plotData[index]["points"]]
            ivv = [point.ivv for point in plotData[index]["points"]]
            filteredBar = [float(point.bar) for point in plotData[index]["filteredPoints"]]
            filteredIvv = [float(point.ivv) for point in plotData[index]["filteredPoints"]]

            addressSeries["points"][0]["raw"] = bar
            addressSeries["points"][0]["filtered"] = filteredBar
            addressSeries["points"][1]["raw"] = ivv
            addressSeries["points"][1]["filtered"] = filteredIvv
            addressSeries["points"][0]["time"] = time
            addressSeries["points"][1]["time"] = time
            
            lineSeries.append(addressSeries)
            
        return lineSeries

    def getLineSeriesSlidingInterval(plotData: List[Dict[str, Union[str, List[WINDOW_POINT]]]]) -> List[Dict[str, List[int]]]:
        lineSeries = []
        for index in range(len(plotData)):
            addressSeries = {
                "address": plotData[index]["address"],
                "identification": plotData[index].get("identification"),
                "points": [],
                "windows": []
            }

            windows = [point.window for point in plotData[index]["points"]]
            points = [point.point for point in plotData[index]["points"]]

            addressSeries["points"] = points
            addressSeries["windows"] = windows

            lineSeries.append(addressSeries)

        return lineSeries

    def getLineSeriesSlidingIntervalForStd(plotData: List[Dict[str, Union[str, List[WINDOW_DATA]]]]) -> List[Dict[str, List[int]]]:
        Analysis.SLIDING_INTERVAL_PER_STD = plotData
        Analysis.KDE_ZONE_EXCEEDS = []
        lineSeries = []
        for index in range(len(plotData)):
            addressSeries = {
                "address": plotData[index]["address"],
                "identification": plotData[index].get("identification"),
                "points": [
                    {
                        "dataSet": "STD",
                        "bar": [],
                        "ivv": [],
                        "windows": []
                    },
                    {
                        "dataSet": "DIFF",
                        "diff": [],
                        "threshold": float(plotData[index]["threshold"]),
                        "windows": []
                    }    
                ]
            }

            windows = [point.window for point in plotData[index]["points"]]
            bar = [point.bar for point in plotData[index]["points"]]
            ivv = [point.ivv for point in plotData[index]["points"]]
            diff = [bar[i] - ivv[i] for i in range(len(bar))]

            addressSeries["points"][0]["windows"] = windows
            addressSeries["points"][1]["windows"] = windows
            addressSeries["points"][0]["bar"] = bar
            addressSeries["points"][0]["ivv"] = ivv
            addressSeries["points"][1]["diff"] = diff

            lineSeries.append(addressSeries)

        return lineSeries
    
    def getLineSeriesForExceeds(plotData: List[Dict[str, Union[str, Dict[int, int]]]]) -> List[Dict[str, List[int]]]:
        lineSeries = [addressSeries for addressSeries in plotData]
        return lineSeries

    def getLineSeriesLocation(location: List[Dict[str, Union[str, List[LOCATION_DATA]]]]) -> List[Dict[str, Union[int, List[List[QtPositioning.QGeoCoordinate]]]]]:
        lineSeries = []
        for index in range(len(location)):
            lineSeries.append(Analysis.__getAddressSeries(location[index]))
                    
        return lineSeries

    def getLineSeriesTurbulentLocation(heatMap: List[Dict[str, Union[str, List[LOCATION_DATA]]]]) -> List[Dict[str, List[int]]]:
        lineSeries = []
        
        for turbulentLocation in heatMap:
            if len(turbulentLocation["points"]) > 0 :
                lineSeries.append(Analysis.__getAddressSeries(turbulentLocation))

        return lineSeries

    def getLineSeriesHeatMap(heatMap: List[Dict[str, Union[str, List[LOCATION_DATA]]]]) -> List[Dict[str, List[int]]]:
        lineSeries = []
        
        allLongitudes = []
        allLatitudes = []
        allTurbulentLongitude = []
        allTurbulentLatLon = []
        allTurbulentLatitude = []
        allAddresses = []
        
        for turbulentLocation in heatMap:
            longitude = []
            latitude = []
            latLon = []
            allAddresses.append(turbulentLocation["address"])

            for point in turbulentLocation["points"]:
                longitude.append(point.longitude)
                latitude.append(point.latitude)
                latLon.append({"address": turbulentLocation["address"], "lat":point.latitude, "lon":point.longitude, "time":point.time})

            allLongitudes += longitude
            allLatitudes += latitude
            allTurbulentLatLon += latLon
            if len(turbulentLocation["points"]) > 0 :
                allTurbulentLongitude += longitude
                allTurbulentLatitude += latitude

        if not allTurbulentLatitude: 
            return lineSeries

        mapPoints = np.vstack([allLongitudes, allLatitudes]).T
        turbulentMapPoints = np.vstack([allTurbulentLongitude, allTurbulentLatitude]).T
        
        kde = KernelDensity(kernel="gaussian", bandwidth=Analysis.KDE_BAND_WIDTH).fit(mapPoints)
        density = np.exp(kde.score_samples(turbulentMapPoints))
        normedDensity = density / max(density)
        
        latitude = allTurbulentLatLon[0]["lat"]
        longitude = allTurbulentLatLon[0]["lon"]
        time = allTurbulentLatLon[0]["time"]
        zoneTimes = {allTurbulentLatLon[0]["address"]: {"start": time, "end": time}}
        
        actualSegment: Dict[str, List[Union[QtPositioning.QGeoCoordinate, float]]] = {
            "coordinates": [QtPositioning.QGeoCoordinate(latitude, longitude)],
            "normedKDEs": [float(normedDensity[0])],
            "KDEs": [float(density[0])]
        }
        
        allSegments = []
        
        for pointIndex, point in enumerate(zip(allTurbulentLatLon, normedDensity, density)):
            latitude = point[0]["lat"]
            longitude = point[0]["lon"]

            address = point[0]["address"]
            time = point[0]["time"]
            
            if zoneTimes.get(address) is None: 
                zoneTimes[address] = {"start": time, "end": time}
            else:
                zoneTimes[address]["end"] = max(zoneTimes[address]["end"], time) 
                zoneTimes[address]["start"] = min(zoneTimes[address]["start"], time)

            normedKDE = float(point[1])
            pointKDE = float(point[2])

            actualPoint = QtPositioning.QGeoCoordinate(latitude, longitude)

            if actualSegment["coordinates"][-1].distanceTo(actualPoint) <= Analysis.POINT_RADIUS:
                actualSegment["coordinates"].append(actualPoint)
                actualSegment["normedKDEs"].append(normedKDE)
                actualSegment["KDEs"].append(pointKDE)
            else:
                allSegments.append({
                    "latitude": statistics.mean([coord.latitude() for coord in actualSegment["coordinates"]]),
                    "longitude": statistics.mean([coord.longitude() for coord in actualSegment["coordinates"]]),
                    "normedKDE": statistics.mean(actualSegment["normedKDEs"]),
                    "kde": statistics.mean(actualSegment["KDEs"]),
                    "zoneTimes": zoneTimes,
                    "bandwidth": Analysis.KDE_BAND_WIDTH
                })
                
                actualSegment["coordinates"] = [actualPoint]
                actualSegment["normedKDEs"] = [normedKDE]
                actualSegment["KDEs"] = [pointKDE]
                zoneTimes = {address: {"start": time, "end": time}}

            if pointIndex == len(allTurbulentLatitude) - 1:
                allSegments.append({
                    "latitude": statistics.mean([coord.latitude() for coord in actualSegment["coordinates"]]),
                    "longitude": statistics.mean([coord.longitude() for coord in actualSegment["coordinates"]]),
                    "normedKDE": statistics.mean(actualSegment["normedKDEs"]),
                    "kde": statistics.mean(actualSegment["KDEs"]),
                    "zoneTimes": zoneTimes,
                    "bandwidth": Analysis.KDE_BAND_WIDTH
                })
                
        allSegments.sort(key= lambda el: el["latitude"]**2 + el["longitude"]**2)
        allKDEZones = {"segments": [allSegments[0]], "widthIncrease": [0]}
        usedJIndex = []
        usedIIndex = []
        for i in range(1, len(allSegments)):
            if i in usedJIndex:
                continue

            allKDEZoneCenter = QtPositioning.QGeoCoordinate(
                statistics.mean(segment["latitude"] for segment in allKDEZones["segments"]),
                statistics.mean(segment["longitude"] for segment in allKDEZones["segments"])
            )
            
            for j in range(2, len(allSegments)):
                if j in usedJIndex or j in usedIIndex:
                    continue
                
                actualSegmentCenter = QtPositioning.QGeoCoordinate(
                    allSegments[j]["latitude"],
                    allSegments[j]["longitude"]
                )
                
                mostDistantPossiblePoint = QtPositioning.QGeoCoordinate(
                    allKDEZoneCenter.latitude() + Analysis.KDE_BAND_WIDTH/2 + 0.5 * sum(allKDEZones["widthIncrease"]) ,
                    allKDEZoneCenter.longitude() + Analysis.KDE_BAND_WIDTH/2 + 0.5 * sum(allKDEZones["widthIncrease"]) 
                )

                if allKDEZoneCenter.distanceTo(actualSegmentCenter) <= allKDEZoneCenter.distanceTo(mostDistantPossiblePoint):
                    allKDEZones["segments"].append(allSegments[j])
                    usedJIndex.append(j)

                    widthIncrease = max(
                        abs(allSegments[j]["latitude"] - allKDEZoneCenter.latitude()), 
                        abs(allSegments[j]["longitude"] - allKDEZoneCenter.longitude())
                    )
                    if widthIncrease > 0 and 0.5 * (sum(allKDEZones["widthIncrease"]) + abs(Analysis.KDE_BAND_WIDTH/2 - widthIncrease)) <= Analysis.KDE_BAND_WIDTH/2:
                        allKDEZones["widthIncrease"].append(abs(Analysis.KDE_BAND_WIDTH/2 - widthIncrease))
            
            usedIIndex.append(i)
            
            kdeZone = {
                key: statistics.mean(segment[key] for segment in allKDEZones["segments"]) for key in ["latitude", "longitude", "normedKDE", "kde", "bandwidth"]
            }
            
            kdeZone["bandwidth"] = Analysis.KDE_BAND_WIDTH + sum(allKDEZones["widthIncrease"]) 
            
            kdeZoneTime = {}
            for segment in allKDEZones["segments"]:
                for address in segment["zoneTimes"]:
                    if kdeZoneTime.get(address) is None:
                        kdeZoneTime[address] = segment["zoneTimes"][address]
                    else:
                        kdeZoneTime[address]["start"] = min(kdeZoneTime[address]["start"], segment["zoneTimes"][address]["start"])
                        kdeZoneTime[address]["end"] = max(kdeZoneTime[address]["end"], segment["zoneTimes"][address]["end"])

            
            Analysis.__createKDEZone(lineSeries, kdeZone, kdeZoneTime)
            allKDEZones["segments"] = [allSegments[i]]
            allKDEZones["widthIncrease"] = [0]
            
        return lineSeries
    
    def getLineSeriesKDEExceeds():
        return Analysis.KDE_ZONE_EXCEEDS
    
    def __createKDEZone(target: List[Dict[str, float]], zone: Dict[str, str], zoneData: Dict[int, Dict[str, float]]):
        target.append(zone)
        
        zoneAddresses = list(zoneData.keys())
        kdeZone: Dict[str, Union[float, List[Dict[str, float]]]] = {
            "latitude": zone["latitude"],
            "longitude": zone["longitude"],
            "exceedsPerAddress": [],
            "kde":[]
        }
        
        maxX = 1000
        Xs = np.linspace(0, 100, num=maxX).reshape(-1, 1)

        allExceedingData = []
        
        for addressData in Analysis.SLIDING_INTERVAL_PER_STD:
            if addressData["address"] not in zoneAddresses: continue

            exceedingData: Dict[str, Union[str, Dict[int, int]]] = {
                "address": addressData["address"],
                "identification": addressData.get("identification"),
                "start": zoneData[addressData["address"]]["start"],
                "end": zoneData[addressData["address"]]["end"],
                "smoothed": []
            }

            threshold = addressData["threshold"]

            if threshold == 0:
                continue

            actualAddress = addressData["address"]

            allDiffs = [point.bar - point.ivv for point in addressData["points"] if zoneData[actualAddress]["start"] <= point.window <= zoneData[actualAddress]["end"]]

            if not allDiffs:
                continue
            
            exceeds = [100*(diff - threshold) /
                    threshold for diff in allDiffs if diff >= threshold]

            if not exceeds:
                continue
            
            exceedingPercentageGroup = []

            for exceedingPercentage in exceeds:
                percentage = next((dist for dist in [0,10,20,30,40,50,60,70,80,90,100] if dist <= exceedingPercentage < dist + 10), 100)
                exceedingPercentageGroup.append(percentage)

            exceedsShape = np.array(exceedingPercentageGroup).reshape(-1, 1)

            kde = KernelDensity(kernel="gaussian",bandwidth=Analysis.KDE_BAND_WIDTH).fit(exceedsShape)
            density = np.exp(kde.score_samples(Xs))
            norm = np.linalg.norm(density)

            exceedingData["smoothed"] = density.tolist()
            kdeZone["exceedsPerAddress"].append(exceedingData)

            allExceedingData.append({"densities": (density/norm).tolist(), "norm": float(norm)})



        globalDensity = [sum(component["densities"][i] * component["norm"] for component in allExceedingData) for i in range(maxX)]

        kdeZone["kde"] = globalDensity
        Analysis.KDE_ZONE_EXCEEDS.append(kdeZone)


    def __getAddressSeries(addressLocation: Dict[str, Union[str, List[LOCATION_DATA]]]) -> Dict[str, Union[int, List[List[QtPositioning.QGeoCoordinate]]]]:
        addressSeries: Dict[str, Union[int, List[Dict[float, float]]]] = {
            "address": addressLocation["address"],
            "identification": addressLocation.get("identification"),
            "segments": []
        }
        
        addressLocation["points"].sort(key=lambda point: point.latitude**2 + point.longitude**2)

        latitude = addressLocation["points"][0].latitude
        longitude = addressLocation["points"][0].longitude
        actualSegment: List[QtPositioning.QGeoCoordinate] = [QtPositioning.QGeoCoordinate(latitude, longitude)]

        for pointIndex, point in enumerate(addressLocation["points"]):
            actualPoint = QtPositioning.QGeoCoordinate(point.latitude, point.longitude)
            if actualSegment[-1].distanceTo(actualPoint) <= Analysis.POINT_RADIUS:
                actualSegment.append(actualPoint)
            else:
                addressSeries["segments"].append(actualSegment)
                actualSegment = [actualPoint]
            if pointIndex == len(addressLocation["points"]) - 1:
                addressSeries["segments"].append(actualSegment)
                
        return addressSeries
