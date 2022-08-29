from typing import List, Dict, NamedTuple, Union
import statistics

from sklearn.neighbors import KernelDensity
import numpy as np

from PySide2 import QtPositioning

from constants import DATA, WINDOW_POINT, WINDOW_DATA, LOCATION_DATA

class Analysis:
    KDE_BAND_WIDTH: int = 0.5
    POINT_RADIUS = 20000

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
        density = np.exp(kde.score_samples(turbulentMapPoints))
        normedDensity = density / max(density)
        

        latitude = allLatitudes[0]
        longitude = allLongitudes[0]
        actualSegment: Dict[str, List[Union[QtPositioning.QGeoCoordinate, float]]] = {
            "coordinates": [QtPositioning.QGeoCoordinate(latitude, longitude)],
            "normedKDEs": [float(normedDensity[0])],
            "KDEs": [float(density[0])]
        }
        
        for pointIndex, point in enumerate(zip(allTurbulentLatitude, allTurbulentLongitude, normedDensity, density)):
            latitude = point[0]
            longitude = point[1]
            normedKDE = float(point[2])
            pointKDE = float(point[3])
            actualPoint = QtPositioning.QGeoCoordinate(latitude, longitude)
            if actualSegment["coordinates"][-1].distanceTo(actualPoint) <= Analysis.POINT_RADIUS:
                actualSegment["coordinates"].append(actualPoint)
                actualSegment["normedKDEs"].append(normedKDE)
                actualSegment["KDEs"].append(pointKDE)
            else:
                lineSeries.append({
                    "latitude": statistics.mean([coord.latitude() for coord in actualSegment["coordinates"]]),
                    "longitude": statistics.mean([coord.longitude() for coord in actualSegment["coordinates"]]),
                    "normedKDE": max(actualSegment["normedKDEs"]),
                    "kde": max(actualSegment["KDEs"]),
                    "bandwidth": Analysis.KDE_BAND_WIDTH
                })
                
                actualSegment["coordinates"] = [actualPoint]
                actualSegment["normedKDEs"] = [normedKDE]
                actualSegment["KDEs"] = [pointKDE]
            if pointIndex == len(allTurbulentLatitude) - 1:
                lineSeries.append({
                    "latitude": statistics.mean([coord.latitude() for coord in actualSegment["coordinates"]]),
                    "longitude": statistics.mean([coord.longitude() for coord in actualSegment["coordinates"]]),
                    "normedKDE": max(actualSegment["normedKDEs"]),
                    "kde": max(actualSegment["KDEs"]),
                    "bandwidth": Analysis.KDE_BAND_WIDTH
                })

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
            actualPoint = QtPositioning.QGeoCoordinate(point.latitude, point.longitude)
            if actualSegment[-1].distanceTo(actualPoint) <= Analysis.POINT_RADIUS:
                actualSegment.append(actualPoint)
            else:
                addressSeries["segments"].append(actualSegment)
                actualSegment = [actualPoint]
            if pointIndex == len(addressLocation["points"]) - 1:
                addressSeries["segments"].append(actualSegment)
                
        return addressSeries
