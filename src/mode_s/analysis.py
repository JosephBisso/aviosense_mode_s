from cmath import sqrt
from typing import List, Dict, NamedTuple, Union
import statistics
from unicodedata import category

from sklearn.neighbors import KernelDensity
import numpy as np

from PySide2 import QtPositioning

from mode_s.constants import DATA, WINDOW_POINT, WINDOW_DATA, LOCATION_DATA

class Analysis:
    KDE_BAND_WIDTH: int = 0.5
    KDE_FIELD_WIDTH = 180*(10**3)
    POINT_RADIUS = 5000
    
    KDE_ZONE_DATA: List[Dict[str, Union[float, List[Dict[str, float]]]]] = []
    KDE_ZONE_IDS = 0

    def setKDEBandwidth(bandwidth:int = 0.5):
        Analysis.KDE_BAND_WIDTH = bandwidth

    def setKDEFieldWidth(fieldWidth:int = 180*(10**3)):
        Analysis.KDE_FIELD_WIDTH = fieldWidth

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
        Analysis.KDE_ZONE_DATA = []
        lineSeries = []
        
        allTurbulentLatLon = []
        
        for turbulentLocation in heatMap:
            allTurbulentLatLon.extend({"address": turbulentLocation["address"], "lat":point.latitude, "lon":point.longitude, "time":point.time} for point in turbulentLocation["points"])

        if not allTurbulentLatLon:
            return lineSeries, Analysis.KDE_ZONE_DATA

        allPoints = allTurbulentLatLon
        allPoints.sort(key=lambda el: el["lat"]**2 + el["lon"]**2)

        actualSegment: List[Union[QtPositioning.QGeoCoordinate, float]] = []
        
        indexToExclude = [] 
        while len(allPoints) > 0:
            for indexOfI, i in enumerate(indexToExclude):
                del allPoints[i - indexOfI] # Because after deleting a object, the index are shifting
                
            indexToExclude = []
            if len(allPoints) == 0: 
                break
            
            basePoint = allPoints[0]
                    
            latitudeR = basePoint["lat"]
            longitudeR = basePoint["lon"]
            addressR = basePoint["address"]
            timeR = basePoint["time"]
            
            refPoint = QtPositioning.QGeoCoordinate(latitudeR, longitudeR)

            actualSegment = [refPoint]
            zoneTimes = {addressR: {"start": timeR, "end": timeR}}
            
            for index, point in enumerate(allPoints):
                latitudeA = point["lat"]
                longitudeA = point["lon"]
                
                actualPoint = QtPositioning.QGeoCoordinate(latitudeA, longitudeA)

                if refPoint.distanceTo(actualPoint) <= (Analysis.KDE_FIELD_WIDTH / 2):
                    indexToExclude.append(index)
                    
                    actualSegment.append(actualPoint)

                    address = point["address"]
                    time = point["time"]
                    
                    if zoneTimes.get(address) is None: 
                        zoneTimes[address] = {"start": time, "end": time}
                    else:
                        zoneTimes[address]["end"] = max(zoneTimes[address]["end"], time) 
                        zoneTimes[address]["start"] = min(zoneTimes[address]["start"], time)
                        
                    
            maxLongitude = maxLatitude = -200
            minLongitude = minLatitude = 200
            for coord in actualSegment:
                minLongitude = min(minLongitude, coord.longitude())
                minLatitude = min(minLatitude, coord.latitude())
                maxLongitude = max(maxLongitude, coord.longitude())
                maxLatitude = max(maxLatitude, coord.latitude())
                
            Analysis.KDE_ZONE_IDS += 1
            segment = {
                "zoneID": Analysis.KDE_ZONE_IDS,
                "latitude": statistics.mean([coord.latitude() for coord in actualSegment]),
                "longitude": statistics.mean([coord.longitude() for coord in actualSegment]),
                "topLeftLon": minLongitude,
                "topLeftLat": maxLatitude,
                "bottomRightLon": maxLongitude,
                "bottomRightLat": minLatitude,
                "kde": 0.25,
                "zoneTimes": zoneTimes,
                "numOfAddresses": len(zoneTimes),
                "normedKDE": 0.25 if len(zoneTimes) <= 5 else (1 if len(zoneTimes) >= 20 else 0.5),
                "fieldWidth": QtPositioning.QGeoCoordinate(0, minLongitude).distanceTo(QtPositioning.QGeoCoordinate(0, maxLongitude)) * (10**-3),
                "bandwidth": Analysis.KDE_BAND_WIDTH
            }

            Analysis.__createKDEZone(lineSeries, segment, zoneTimes)


        return lineSeries, Analysis.KDE_ZONE_DATA
    
    def __createKDEZone(target: List[Dict[str, float]], zone: Dict[str, str], zoneData: Dict[int, Dict[str, float]]):
        target.append(zone)
        
        zoneID = str(zone["zoneID"])

        Analysis.KDE_ZONE_DATA.append({
            "zoneID": zoneID,
            "zoneData": zoneData,
            "latitude": zone["latitude"],
            "longitude": zone["longitude"],
            "exceedsPerAddress": [],
            "kde": []
        })

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

        