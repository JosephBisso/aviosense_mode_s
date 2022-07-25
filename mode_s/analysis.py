from typing import List, Dict, NamedTuple, Union

from sklearn.neighbors import KernelDensity
import numpy as np

from PySide2 import QtPositioning

from constants import DATA, WINDOW_POINT, WINDOW_DATA, LOCATION_DATA

class Analysis:
    KDE_BAND_WIDTH: int = 0.5
    POINT_RADIUS = 10000

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
        allTurbulentLatitude = []
        
        for turbulentLocation in heatMap:
            longitude = [point.longitude for point in turbulentLocation["points"]]
            latitude = [point.latitude for point in turbulentLocation["points"]]

            allLongitudes += longitude
            allLatitudes += latitude
            if len(turbulentLocation["points"]) > 0 :
                allTurbulentLongitude += longitude
                allTurbulentLatitude += latitude

        if not allTurbulentLatitude: 
            return lineSeries

        mapPoints = np.vstack([allLongitudes, allLatitudes]).T
        turbulentMapPoints = np.vstack([allTurbulentLongitude, allTurbulentLatitude]).T
        
        kde = KernelDensity(kernel="gaussian", bandwidth=Analysis.KDE_BAND_WIDTH).fit(mapPoints)
        logDensity = np.exp(kde.score_samples(turbulentMapPoints))

        for index in range(len(heatMap)):
            addressSeries: Dict[str, Union[int, List[Dict[float, float]]]] = {
                "address": heatMap[index]["address"],
                "identification": heatMap[index].get("identification"),
                "points": []
            }
            
            for point in heatMap[index]["points"]:
                addressSeries["points"].append({
                    "latitude": point.latitude,
                    "longitude": point.longitude,
                    "kde":logDensity[index]
                })

            addressSeries["points"].sort(key=lambda el: el["latitude"]**2 + el["longitude"]**2)
            lineSeries.append(addressSeries)

        return lineSeries
    

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
            point = QtPositioning.QGeoCoordinate(point.latitude, point.longitude)
            if actualSegment[-1].distanceTo(point) <= Analysis.POINT_RADIUS:
                actualSegment.append(point)
            else:
                addressSeries["segments"].append(actualSegment)
                actualSegment = [point]
            if pointIndex == len(addressLocation["points"]) - 1:
                addressSeries["segments"].append(actualSegment)
                
        return addressSeries
