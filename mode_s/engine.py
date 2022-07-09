
import sys
import statistics
import numpy as np
import seaborn as sb
import geopandas as gpd
import concurrent.futures
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from scipy.signal import medfilt
from collections import Counter, namedtuple
from typing import List, Dict, NamedTuple, Union

from logger import Logger
from constants import ENGINE_CONSTANTS
from constants import DB_CONSTANTS
from constants import GUI_CONSTANTS

class DATA(NamedTuple):
    time: float # in Seconds
    bar: float
    ivv: float
    
class WINDOW_POINT(NamedTuple):
    window: float 
    point: float

class WINDOW_DATA(NamedTuple):
    window: float 
    bar: float
    ivv: float

class LOCATION_DATA(NamedTuple):
    time: float 
    longitude: float
    latitude: float

class EngineError(BaseException):
    pass

class Engine:
    def __init__(self, logger: Logger, plots: List[str] = [], plotAddresses: List[str] = [], medianN: int = 1, durationLimit:int = None, plotAll = False):
        self.logger = logger
        self.plots: Dict[str, bool] = self.__activatePlot(plots)
        self.plotAddresses = [int(address) for address in plotAddresses]
        self.plotAll = plotAll
        self.medianN = int(medianN) if int(medianN) % 2 == 1 else int(medianN) + 1
        self.durationLimit = float(durationLimit) if durationLimit else None
        self.executors = []
    
    def __executor(self) -> concurrent.futures.ThreadPoolExecutor:
        ex = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="engine_workerThread", max_workers=ENGINE_CONSTANTS.MAX_NUMBER_THREADS_ENGINE)
        self.executors.append(ex)
        return ex

    def __activatePlot(self, plots:List[str]):
        plotsInsensitive = [plot.lower() for plot in plots]
        plots = {plot: plot in plotsInsensitive for plot in ENGINE_CONSTANTS.PLOTS}

        abs = []
        for plot in plotsInsensitive:
            if not plot in ENGINE_CONSTANTS.PLOTS: abs.append(plot)
        if len(abs) > 0 : self.logger.warning("Following Plots are unknown. May be a Typo? : " + str(abs))
        
        self.logger.log("Engine plot status : " + str(plots))
        return plots

    def __getDataForAddress(self, address: int) -> Dict[str, Union[str, List[DATA]]]:
        addressData: Dict[str, Union[str, List[int]]] = {
            "address": address,
            "points": []
        }

        bars = []
        ivvs = []
        times = []

        startIndex = None
        for index, data in enumerate(self.data):
            if data["address"] != address: continue
            startIndex = index
            break

        if not startIndex:
            raise EngineError("Skipping address " + str(address) + " : Cannot be found")

        for index in range(startIndex, len(self.data)):
            if self.data[index]["bar"] is None or self.data[index]["ivv"] is None:
                continue
            if self.data[index]["address"] != address:
                break
            bars.append(self.data[index]["bar"])
            ivvs.append(self.data[index]["ivv"])
            times.append(self.data[index]["timestamp"])
        
        if not times:
            raise EngineError("Skipping address " + str(address) + " : No valid entry")

        startTime = min(times)
        addressData["points"] = [DATA((times[i] - startTime)*10**-9, bars[i], ivvs[i]) for i in range(len(times))]
        addressData["points"].sort(key=lambda el: el.time)
        
        if self.durationLimit:  
            startIndexForOverDuration = None
            for index, point in enumerate(addressData["points"]):
                if point.time < self.durationLimit: continue
                startIndexForOverDuration = index
                break 
            if startIndexForOverDuration:
                self.logger.log("Filtering data for address " + str(address)+ " with max flight duration time = " + str(self.durationLimit))
                del(addressData["points"][startIndexForOverDuration: len(addressData["points"])])
        
        # self.logger.debug("Valid results for sliding interval for address " + str(
        #     address) + ". Points Count: " + str(len(addressData["points"])))

        return addressData

    def __applyMedianFilter(self, addressData: Dict[str, Union[str, List[DATA]]]) -> None:
        bars = [point.bar for point in addressData["points"]]
        ivvs = [point.ivv for point in addressData["points"]]
        times = [point.time for point in addressData["points"]]

        if not bars or not ivvs or not times:
            raise EngineError("Skipping address " + str(addressData["address"]) + " : Invalid bar or ivv for median filter")
        
        maxMedianFilter = len(bars) if len(bars) % 2 == 1 else len(bars) - 1
        nFilter = min(self.medianN, maxMedianFilter)

        filteredBars: np.ndarray = medfilt(bars, nFilter)
        filteredIvvs: np.ndarray = medfilt(ivvs, nFilter)

        addressData["filteredPoints"] = [
            DATA(times[i], filteredBars[i], filteredIvvs[i]) for i in range(len(filteredBars))
        ]
        
        # self.logger.debug("Valid results for apply median filter for address " + str(
        #     addressData["address"]) + ". Points Count: " + str(len(addressData["filteredPoints"])))


    def __getSlidingIntervalForAddress(self, addressData: Dict[str, Union[str, List[DATA]]]) -> Dict[str, Union[str, List[WINDOW_POINT]]]:
        times = [point.time for point in addressData["points"]]
        if not times: 
            raise EngineError("Skipping address " + str(addressData["address"]) + " : Invalid time for sliding interval")
        
        slidingWindows = [duration * 60 for duration in range(int(max(times) / 60))]
        
        slidingIntervals:Dict[str, Union[str, List[WINDOW_POINT]]]  = {"address": addressData["address"], "points":[]}
        actualIndex = 0
        for windowIndex in range(len(slidingWindows)):
            dataPoints = 0
            for dataIndex in range(actualIndex, len(addressData["points"])):
                if addressData["points"][dataIndex].time > slidingWindows[windowIndex]: 
                    actualIndex = dataIndex
                    break
                dataPoints += 1
            
            slidingIntervals["points"].append(WINDOW_POINT(slidingWindows[windowIndex]/60, dataPoints))
        
        # self.logger.debug("Valid results for sliding interval for address " + str(
        #     addressData["address"]) + ". Points Count: " + str(len(slidingIntervals["points"])))
        
        return slidingIntervals

    def __getSlidingIntervalForStdPerAddress(self, addressData: Dict[str, Union[str, List[DATA]]]) -> Dict[str, Union[str, List[WINDOW_DATA], float]]:
        slidingIntervalsForStd: Dict[str, Union[str, List[WINDOW_POINT]]] = {
            "address": addressData["address"],
            "points": [],
            "threshold": 0
        }
        
        times = [point.time for point in addressData["points"]]
        
        try:
            addressData["filteredPoints"]
        except KeyError:
            raise EngineError("Skipping address " + str(addressData["address"]) + " : No filtered points for sliding interval per std")
            
        slidingWindows = [duration *60 for duration in range(int(max(times) / 60))]
        
        barStds = []
        ivvStds = []

        actualIndex = 0
        for windowIndex in range(len(slidingWindows)):
            bars = []
            ivvs = []
            for dataIndex in range(actualIndex, len(addressData["filteredPoints"])):
                if addressData["filteredPoints"][dataIndex].time > slidingWindows[windowIndex]:
                    actualIndex = dataIndex
                    break
                bars.append(addressData["filteredPoints"][dataIndex].bar)
                ivvs.append(addressData["filteredPoints"][dataIndex].ivv)

            if not bars or not ivvs:
                bars = [0,0]
                ivvs = [0,0]
            
            if len(bars) == 1 :
                bars.append(bars[0])
                ivvs.append(ivvs[0])
            
            barStd = statistics.stdev(bars)
            ivvStd = statistics.stdev(ivvs)
            
            slidingIntervalsForStd["points"].append(WINDOW_DATA(
                slidingWindows[windowIndex]/60, barStd, ivvStd))

            barStds.append(barStd)
            ivvStds.append(ivvStd)
            
        if not barStds or not ivvStds: 
            barStds = [0, 0]
            ivvStds = [0, 0]
            
        arrayBarStds = np.array(barStds)
        arrayIvvStds = np.array(ivvStds)
        diffStds = arrayBarStds - arrayIvvStds
        
        ddof = 1 if len(diffStds) > 1 else 0
        threshold = np.average(diffStds) + 1.2 * np.std(diffStds, ddof=ddof)
        slidingIntervalsForStd["threshold"] = threshold
        
        # self.logger.debug("Valid results for sliding interval for std for address " + str(
        #     addressData["address"]) + ". Points Count: " + str(len(slidingIntervalsForStd["points"])))

        return slidingIntervalsForStd

    def __getHeatPointsForAddress(self, addressData: Dict[str, Union[str, List[WINDOW_DATA], float]] = {}) -> Dict[str, Union[str,List[LOCATION_DATA]]]:
        heatPointsForAddress: List[str, List[LOCATION_DATA]] = []
        
        turbulentSlidingWindows = [point.window for point in addressData["points"] if point.bar - point.ivv > addressData["threshold"]]
        turbulentSlidingWindows.sort()
        
        # self.logger.debug("Heat Points for address " + str(
        #     addressData["address"]) + ". Address Data windows Count: " + str(len(addressData["points"])) + 
        #     ". Turbulent sliding windows: " + str(len(turbulentSlidingWindows)))

        times = []

        startIndex = None
        for index, data in enumerate(self.data):
            if data["address"] != addressData["address"]: continue
            startIndex = index
            break

        if not startIndex:
            raise EngineError("Skipping address " + str(addressData["address"]) + " : Invalid bar or ivv stds for heat map")

        for index in range(startIndex, len(self.data)):
            if self.data[index]["address"] != addressData["address"]:
                break
            times.append(self.data[index]["timestamp"])
                    
        startTime = min(times)

        foundLongitude = False
        foundWindow = False
        closestTimes = []
        allTimes = []
        for index in range(startIndex, len(self.data)):
            if self.data[index]["longitude"] is None or self.data[index]["latitude"] is None:
                continue
            if self.data[index]["address"] != addressData["address"]:
                break

            foundLongitude = True

            rawTime = self.data[index]["timestamp"]
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
            
            longitude = self.data[index]["longitude"]
            latitude = self.data[index]["latitude"]
            
            heatPointsForAddress.append(
                LOCATION_DATA(rawTime, longitude, latitude)
            )
            
        if allTimes: closestTimes.insert(0, min(allTimes))
        
        if len(heatPointsForAddress) < len(turbulentSlidingWindows):
            self.logger.debug("Doubtful results for Heat Points for address " + str(
                addressData["address"]) + ". Points Count: " + str(len(heatPointsForAddress)) + "| Found longitude and latitude data? " + str(foundLongitude) + 
                " | Found window? " + str(foundWindow) + " | turbulent sliding windows: " + str(turbulentSlidingWindows) + " | closest Times: " + str(closestTimes))

        # else:
        #     self.logger.debug("Valid results for Heat Points for address " + str(
        #         addressData["address"]) + ". Points Count: " + str(len(heatPointsForAddress)))

        return {"address": addressData["address"], "points": heatPointsForAddress}

    def updateParameters(self, plotAddresses: List[str] = [], medianN: int = 1, durationLimit: int = None):
        self.gui = True
        self.plots = self.__activatePlot([""])
        self.plotAddresses = [int(address) for address in plotAddresses]
        self.medianN = int(medianN) if int(medianN) % 2 == 1 else int(medianN) + 1
        self.durationLimit = float(durationLimit) if durationLimit else None

        self.logger.log("Minimum number of threads : " + str(DB_CONSTANTS.MIN_NUMBER_THREADS))
        self.logger.log("Setting median Filter to : " + str(self.medianN))
        self.logger.log("Watching following address(es) : " + str(self.plotAddresses))
        self.logger.log("Setting duration limit to : " + str(self.durationLimit))


    def setDataSet(self, dataset: List[Dict[str, Union[str, int]]]):
        self.data = sorted(dataset, key=lambda el: el["address"])
        
        # import json
        # with open("engine.dump.json", "w") as dbd:
        #     json.dump(self.data, dbd)

                      
    def compute(self, usePlotter=True) -> None:
        if usePlotter and not any(self.plots.values()) : return
        
        activePlots = self.plots
        
        if not usePlotter:
            activePlots = {plot: True for plot in ENGINE_CONSTANTS.PLOTS}
                
        plotted = []
        
        if activePlots["occurrence"]:
            dataPoints = self.prepareOccurrencesForAddresses()
            if usePlotter:
                self.logger.info("Plotting occurrence on addresses")
                plotted.append(Plotter.plotDataPointOccurrences(occurrences=dataPoints))
            else:
                lineSeriesOccurrence = self.getLineSeriesDataPointOccurrences(dataPoints)
                yield lineSeriesOccurrence

        allAddresses = self.prepareOccurrencesForAddresses("addresses")
        mostPointAddresses = allAddresses[:4]
        if self.plotAddresses:
            addressesToPlot = self.plotAddresses
        elif self.plotAll:
            addressesToPlot = allAddresses
        else:
            addressesToPlot = mostPointAddresses
            
        if len(addressesToPlot) < 5: self.logger.log("Computing for following addresses: " + str(addressesToPlot))
        else: self.logger.log("Computing for " + str(len(addressesToPlot)) + " addresses")
            
        data = self.prepareBarAndIvvAndTime(addressesToPlot)
        
        if activePlots["bar_ivv"]:
            if usePlotter:
                self.logger.info("Plotting bar and ivv on time")
                plotted.append(Plotter.plotBarAndIvv(data))
            else:
                lineSeriesBarIvv = self.getLineSeriesBarAndIvv(data)
                yield lineSeriesBarIvv
            
        if activePlots["filtered"] and not activePlots["std"]:
            self.prepareMedianFilter(data)
            if usePlotter:
                self.logger.info("Plotting filtered bar and ivv on time")
                plotted.append(Plotter.plotFilteredBarAndIvv(data))
            else:
                lineSeriesFiltered = self.getLineSeriesFilteredBarAndIvv(data)
                yield lineSeriesFiltered

        if activePlots["interval"]:
            slidingIntervals = self.prepareSlidingInterval(data)
            if usePlotter:
                self.logger.info("Plotting sliding Intervals")
                plotted.append(Plotter.plotSlidingInterval(slidingIntervals))
            else:
                lineSeriesInterval = self.getLineSeriesSlidingInterval(slidingIntervals)
                yield lineSeriesInterval
        
        if activePlots["std"]: 
            self.prepareMedianFilter(data)
            slidingIntervalForStd = self.prepareSlidingIntervalForStd(data) 
            if usePlotter:
                if activePlots["filtered"]: 
                    self.logger.info("Plotting filtered data and standard deviations")
                    plotted.append(Plotter.plotFilteredAndStd(filteredData=data, stdData=slidingIntervalForStd))
                else:
                    self.logger.info("Plotting standard deviations")
                    plotted.append(Plotter.plotSlidingIntervalForStd(slidingIntervalForStd))
            else:
                lineSeriesStd = self.getLineSeriesSlidingIntervalForStd(slidingIntervalForStd)
                yield lineSeriesStd
        
        if activePlots["location"]:
            location = self.prepareLocation()
            if usePlotter:
                self.logger.info("Plotting location")
                plotted.append(Plotter.plotLocation(location))
            else:
                lineSeriesLocation = self.getLineSeriesLocation(location)
                yield lineSeriesLocation

        if activePlots["heat_map"]:
            if not activePlots["filtered"] and not activePlots["std"]:
                self.prepareMedianFilter(data)
            if not activePlots["std"]:
                slidingIntervalForStd = self.prepareSlidingIntervalForStd(data)
            if not activePlots["location"]:
                location = self.prepareLocation()
            heatMap = self.prepareHeatMap(slidingIntervalForStd)
            if usePlotter:
                self.logger.info("Plotting heat map")
                plotted.append(Plotter.plotHeatMap(heatMap=heatMap, rawLocation=location))
            else:
                lineSeriesHeatMap = self.getLineSeriesHeatMap(heatMap)
                yield lineSeriesHeatMap
                
        if all(plotted): self.logger.success("Successfully plotted")
        else: self.logger.warning("Error while plotting")
        
    def prepareOccurrencesForAddresses(self, returnValue="datapoint") -> Union[List[Union[int, str]], List[int]]:
        self.logger.log("Computing Occurrences for Addresses")
        dataPointsCounter = Counter([entry["address"] for entry in self.data])
        if returnValue != "datapoint": return [mostCommonAddress[0] for mostCommonAddress in dataPointsCounter.most_common() if mostCommonAddress[1] > 1]

        dataPoint = list(dataPointsCounter.values())
        dataPoint.sort(reverse=True)
        return dataPoint

    def prepareBarAndIvvAndTime(self, addresses:List[int] = []) -> List[Dict[str, Union[str, List[DATA]]]]:
        self.logger.log("Computing bar, ivv and time")
        plotData = []
        executor = self.__executor()
        addressData__futures = [executor.submit(self.__getDataForAddress, address) for address in addresses]

        for completedThread in concurrent.futures.as_completed(addressData__futures):
            try:
                addressData = completedThread.result()
            except EngineError as e:
                self.logger.warning(str(e))
            except Exception as esc:
                type, value, traceback = sys.exc_info()
                self.logger.warning(
                    "Error occurred while computing data for addresses\n" + str(type) + "::" + str(value))
            else:
                plotData.append(addressData)
        
        executor.shutdown()
        return plotData

    def prepareMedianFilter(self, data: List[Dict[str, Union[str, List[DATA]]]]) -> None:
        self.logger.log("Filtering data with n set to: " + str(self.medianN))
        executor = self.__executor()
        filteredAddressData__futures = [executor.submit(
            self.__applyMedianFilter, addressData) for addressData in data]

        for completedThread in concurrent.futures.as_completed(filteredAddressData__futures):
            try:
                completedThread.result()
            except EngineError as e:
                self.logger.warning(str(e))
            except Exception as esc:
                type, value, traceback = sys.exc_info()
                self.logger.warning(
                    "Error occurred while filtering data for addresses\n" + str(type) + "::" + str(value))

        executor.shutdown()

    def prepareSlidingInterval(self, data: List[Dict[str, Union[str, List[DATA]]]]) -> List[Dict[str, Union[str, List[WINDOW_POINT]]]]:
        self.logger.log("Computing sliding intervals")
        slidingIntervals = []
        executor = self.__executor()
        slidingInterval__futures = [executor.submit(
            self.__getSlidingIntervalForAddress, addressData) for addressData in data]

        for completedThread in concurrent.futures.as_completed(slidingInterval__futures):
            try:
                slidingIntervalForAddress = completedThread.result()
            except EngineError as e:
                self.logger.warning(str(e))
            except Exception as esc:
                type, value, traceback = sys.exc_info()
                self.logger.warning(
                    "Error occurred while preparing sliding intervals for addresses\n" + str(type) + "::" + str(value))
            else:
                if slidingIntervalForAddress: slidingIntervals.append(slidingIntervalForAddress)
                
        executor.shutdown()
        return slidingIntervals
    
    def prepareSlidingIntervalForStd(self, data: List[Dict[str, Union[str, List[DATA]]]]) -> List[Dict[str, Union[str, List[WINDOW_DATA], float]]]:
        self.logger.log("Computing sliding intervals for std")
        slidingIntervalForStd = []
        executor = self.__executor()
        slidingInterval__futures = [executor.submit(
            self.__getSlidingIntervalForStdPerAddress, addressData) for addressData in data]

        for completedThread in concurrent.futures.as_completed(slidingInterval__futures):
            try:
                slidingIntervalForStdPerAddress = completedThread.result()
            except EngineError as e:
                self.logger.warning(str(e))
            except Exception as esc:
                type, value, traceback = sys.exc_info()
                self.logger.warning(
                    "Error occurred while preparing sliding interval for std per addresses\n" + str(type) + "::" + str(value))
            else:
                if slidingIntervalForStdPerAddress: slidingIntervalForStd.append(slidingIntervalForStdPerAddress)

        executor.shutdown()
        return slidingIntervalForStd

    def prepareLocation(self) -> List[Dict[str, Union[str, List[LOCATION_DATA]]]]:
        self.logger.log("Computing locations")
        allLocationData = []
        
        addressPoints: List[LOCATION_DATA] = []
         
        for index in range(len(self.data)):
            time = self.data[index]["timestamp"]
            longitude = self.data[index]["longitude"]
            latitude = self.data[index]["latitude"]
            
            if longitude is None or latitude is None : continue

            addressPoints.append(LOCATION_DATA(time, longitude, latitude))

            if index == len(self.data) - 1 or self.data[index]["address"] != self.data[index + 1]["address"]:
                addressPoints.sort(key=lambda el: el.time)

                allLocationData.append({
                    "address": self.data[index]["address"],
                    "points": addressPoints
                })
                
                addressPoints = []
        
        return allLocationData
    
    def prepareHeatMap(self, slidingIntervallForStd: List[Dict[str, Union[str, List[WINDOW_DATA], float]]] = []) -> List[Dict[str, Union[str, List[LOCATION_DATA]]]]:
        self.logger.log("Computing heat map")
        heatPoints: List[Dict[str, Union[str, List[LOCATION_DATA]]]] = []
        executor = self.__executor()
        heatPoints__future = [executor.submit(
            self.__getHeatPointsForAddress, addressData) for addressData in slidingIntervallForStd]
        for completedThread in concurrent.futures.as_completed(heatPoints__future):
            try:
                heatPointsPerAddress = completedThread.result()
            except EngineError as e:
                self.logger.warning(str(e))
            except Exception as esc:
                type, value, traceback = sys.exc_info()
                self.logger.warning(
                    "Error occurred while preparing heatmap per addresses\n" + str(type) + "::" + str(value))
            else:
                heatPoints.append(heatPointsPerAddress)
                
        executor.shutdown()
        return heatPoints


    def getLineSeriesDataPointOccurrences(self, occurrences: List[Union[str, int]]) -> List[int]:
        self.logger.info("Getting lineSeries for  occurrence on addresses")
        return occurrences 

    def getLineSeriesBarAndIvv(self,  plotData: List[Dict[str, Union[str, List[DATA]]]]) -> List[Dict[str, List[int]]]:
        self.logger.info("Getting lineSeries for raw bar & ivv")
        lineSeries = []
        for index in range(len(plotData)):
            addressSeries = {"address": plotData[index]["address"], "bar":[], "ivv": [], "time": []}

            time = list(map(lambda el: el/60, [point.time for point in plotData[index]["points"]]))
            bar = [point.bar for point in plotData[index]["points"]]
            ivv = [point.ivv for point in plotData[index]["points"]]

            addressSeries["bar"] = bar
            addressSeries["ivv"] = ivv
            addressSeries["time"] = time
            
            lineSeries.append(addressSeries)
            
        return lineSeries

    def getLineSeriesFilteredBarAndIvv(self, plotData: List[Dict[str, Union[str, List[DATA]]]]) -> List[Dict[str, List[int]]]:
        self.logger.info("Getting line series for filtered bar and ivv on time")
        
        lineSeries = []
        for index in range(len(plotData)):
            addressSeries = {
                "address": plotData[index]["address"],
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

    def getLineSeriesSlidingInterval(self, plotData: List[Dict[str, Union[str, List[WINDOW_POINT]]]]) -> List[Dict[str, List[int]]]:
        self.logger.info("Getting lineSeries for sliding interval")
        lineSeries = []
        for index in range(len(plotData)):
            addressSeries = {
                "address": plotData[index]["address"],
                "points": [],
                "windows": []
            }

            windows = [point.window for point in plotData[index]["points"]]
            points = [point.point for point in plotData[index]["points"]]

            addressSeries["points"] = points
            addressSeries["windows"] = windows

            lineSeries.append(addressSeries)

        return lineSeries

    def getLineSeriesSlidingIntervalForStd(self, plotData: List[Dict[str, Union[str, List[WINDOW_DATA]]]]) -> List[Dict[str, List[int]]]:
        self.logger.info("Getting lineSeries for sliding interval for Std")
        lineSeries = []
        for index in range(len(plotData)):
            addressSeries = {
                "address": plotData[index]["address"],
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

    def getLineSeriesLocation(self, location: List[Dict[str, Union[str, List[LOCATION_DATA]]]]) -> List[Dict[str, List[int]]]:
        pass

    def getLineSeriesHeatMap(self, heatMap: List[Dict[str, Union[str, List[LOCATION_DATA]]]]) -> List[Dict[str, List[int]]]:
        pass

class Plotter:
    def plotDataPointOccurrences(occurrences: List[Union[str, int]]) -> bool:
        plt.subplots(num="MODE-S @ Data Points Occurrence")
        plt.plot(range(1, len(occurrences) + 1), occurrences, marker='o', color='b', linestyle='None', ms=1.75)
        plt.xlabel("Number of addresses")
        plt.ylabel("Number of datapoints")
        plt.title("Datapoints over addresses")
        plt.show()
        
        return True
    
    def plotBarAndIvv(plotData: List[Dict[str, Union[str, List[DATA]]]]) -> bool:
        nCol = int(round((len(plotData)/4) * 16/9))
        nRow = int(round(len(plotData) / nCol))
        
        plt.subplots(num="MODE-S @ BAR & IVV")
        for index in range(len(plotData)):
            address = plotData[index]["address"]
            time = list(map(lambda el: el/60, [point.time for point in plotData[index]["points"]]))
            bar = [point.bar for point in plotData[index]["points"]]
            ivv = [point.ivv for point in plotData[index]["points"]]
            
            plt.subplot(nRow, nCol, index + 1)
            plt.subplots_adjust(wspace=0.5, hspace=0.5)
            plt.plot(time, bar, marker=',', color='b', linestyle='-', ms=0.25, label="BAR")
            plt.plot(time, ivv, marker=',', color='r', linestyle='-', ms=0.25, label="IVV")
            plt.grid()

            plt.xlabel("min")
            plt.ylabel("v ft/min")
            plt.legend()
            plt.title("Address " + str(address) + " (" + str(len(plotData[index]["points"]))+ " points)")
                        
        plt.suptitle("IVV & BAR for addresses", fontsize=20)
        plt.show()
        
        return True
    
    def plotFilteredBarAndIvv(plotData: List[Dict[str, Union[str, List[DATA]]]]) -> bool:
        nCol = len(plotData)
        nRow = 2
        
        plt.subplots(num="MODE-S @ Filtered BAR & IVV")

        for index in range(len(plotData)):
            address = plotData[index]["address"]
            time = list(map(lambda el: el/60, [point.time for point in plotData[index]["points"]]))
            bar = [point.bar for point in plotData[index]["points"]]
            ivv = [point.ivv for point in plotData[index]["points"]]
            
            filteredBar = [point.bar for point in plotData[index]["filteredPoints"]]
            filteredIvv = [point.ivv for point in plotData[index]["filteredPoints"]]
            
            plt.subplot(nRow, nCol, index + 1)
            plt.subplots_adjust(wspace=0.5, hspace=0.5)
            plt.plot(time, bar, marker=',', color='r', linestyle='-', ms=0.25, label="Raw BAR")
            plt.plot(time, filteredBar, marker=',', color='#4287f5', linestyle='-', ms=0.25, label="Filtered BAR")
            plt.grid()
            plt.title("BAR :: Address " + str(address) + " (" + str(len(plotData[index]["points"]))+ " points)")
            plt.xlabel("min")
            plt.ylabel("v ft/min")
            plt.legend()

            plt.subplot(nRow, nCol, index + 1 + nCol)
            plt.subplots_adjust(wspace=0.5, hspace=0.5)
            plt.plot(time, ivv, marker=',', color='r', linestyle='-', ms=0.25, label="Raw IVV")
            plt.plot(time, filteredIvv, marker=',', color='#3ccf9b', linestyle='-', ms=0.25, label="Filtered IVV")
            plt.grid()
            plt.title("IVV :: Address " + str(address) + " (" + str(len(plotData[index]["points"]))+ " points)")
            plt.xlabel("min")
            plt.ylabel("v ft/min")
            plt.legend()
            
        plt.suptitle("IVV & BAR, Raw and Filtered with n = " + str(self.medianN) + " for addresses", fontsize=20)
        plt.show()
        
        return True
        
    def plotSlidingInterval(plotData: List[Dict[str, Union[str, List[WINDOW_POINT]]]]) -> bool:
        nCol = int(round((len(plotData)/4) * 16/9))
        nRow = int(round(len(plotData) / nCol))
        
        plt.subplots(num="MODE-S @ Sliding Intervals")
        for index in range(len(plotData)):
            address = plotData[index]["address"]
            windows = [point.window for point in plotData[index]["points"]]
            points = [point.point for point in plotData[index]["points"]]

            plt.subplot(nRow, nCol, index + 1)
            plt.subplots_adjust(wspace=0.5, hspace=0.5)
            plt.step(windows, points, where="mid", marker=',', color='b', linestyle='-', linewidth=2)
            plt.grid()

            plt.xlabel("sliding window [min]")
            plt.ylabel("number of points [1]")
            plt.title("Address " + str(address))
                        
        plt.autoscale(enable=True, axis="x", tight=True)
        plt.suptitle("Sliding Intervals for addresses", fontsize=20)
        plt.show()
        
        return True
    
    def plotSlidingIntervalForStd(plotData: List[Dict[str, Union[str, List[WINDOW_DATA]]]]) -> bool:
        nCol = len(plotData)
        nRow = 2
        
        plt.subplots(num="MODE-S @ STD BAR & IVV")

        for index in range(len(plotData)):
            address = plotData[index]["address"]
            windows = [point.window for point in plotData[index]["points"]]
            barsStd = [point.bar for point in plotData[index]["points"]]
            ivvsStd = [point.ivv for point in plotData[index]["points"]]
            diffStd = [barsStd[i] - ivvsStd[i] for i in range(len(barsStd))]

            threshold = plotData[index]["threshold"]

            plt.subplot(nRow, nCol, index + 1)
            plt.subplots_adjust(wspace=0.3, hspace=0.3)
            plt.plot(windows, barsStd, marker='o', color='b', linestyle='-', ms=3, label="Std BAR")
            plt.plot(windows, ivvsStd, marker='o', color='m', linestyle='-', ms=3, label="Std IVV")
            plt.grid()
            plt.legend()
            plt.title("BAR & IVV :: Address " + str(address))
            plt.xlabel("min")
            plt.ylabel("std v ft/min")
            
            plt.subplot(nRow, nCol, index + 1 + nCol)
            plt.subplots_adjust(wspace=0.3, hspace=0.3)
            plt.stem(windows, diffStd, linefmt="g-", markerfmt="k.",basefmt="k-")
            plt.plot([0, len(windows)-1], [threshold, threshold], color="#f20707", linestyle="--", label="Threshold")
            plt.grid()
            plt.legend()
            plt.title("DIFF :: Address " + str(address) + " (T ~ " + str(round(threshold)) + ")")
            plt.xlabel("min")
            plt.ylabel("delta std v ft/min")
            
        plt.suptitle("Standard deviation (Std) of IVV & BAR. Data filtered with n = " + str(self.medianN) + " for addresses", fontsize=20)
        plt.show()
        
        return True

    def plotFilteredAndStd(filteredData: List[Dict[str, Union[str, List[DATA]]]], stdData: List[Dict[str, Union[str, List[WINDOW_DATA]]]]) -> bool:
        nCol = len(stdData)
        nRow = 3
        
        plt.subplots(num="MODE-S @ FILTERED & STD -> BAR & IVV")

        for index in range(len(stdData)):
            address = stdData[index]["address"]
            windows = [point.window for point in stdData[index]["points"]]
            barsStd = [point.bar for point in stdData[index]["points"]]
            ivvsStd = [point.ivv for point in stdData[index]["points"]]
            diffStd = [barsStd[i] - ivvsStd[i] for i in range(len(barsStd))]

            threshold = stdData[index]["threshold"]
            
            time = list(map(lambda el: el/60, [point.time for point in filteredData[index]["filteredPoints"]]))
            filteredBar = [point.bar for point in filteredData[index]["filteredPoints"]]
            filteredIvv = [point.ivv for point in filteredData[index]["filteredPoints"]]
            
            plt.subplot(nRow, nCol, index + 1)
            plt.subplots_adjust(wspace=0.5, hspace=0.5)
            plt.plot(time, filteredBar, marker=',', color='b', linestyle='-', ms=0.25, label="BAR")
            plt.plot(time, filteredIvv, marker=',', color='m', linestyle='-', ms=0.25, label="IVV")
            plt.grid()
            plt.legend()
            plt.xlabel("min")
            plt.ylabel("v ft/min")
            plt.title("Filtered :: Address " + str(address))

            plt.subplot(nRow, nCol, index + 1 + nCol)
            plt.subplots_adjust(wspace=0.5, hspace=0.5)
            plt.plot(windows, barsStd, marker='o', color='b', linestyle='-', ms=3, label="BAR")
            plt.plot(windows, ivvsStd, marker='o', color='m', linestyle='-', ms=3, label="IVV")
            plt.grid()
            plt.legend()
            plt.title("STD :: Address " + str(address))
            plt.xlabel("min")
            plt.ylabel("std v ft/min")
            
            plt.subplot(nRow, nCol, index + 1 + 2*nCol)
            plt.subplots_adjust(wspace=0.5, hspace=0.5)
            plt.stem(windows, diffStd, linefmt="g-", markerfmt="k.",basefmt="k-")
            plt.plot([0, len(windows)-1], [threshold, threshold], color="#f20707", linestyle="--", label="Threshold")
            plt.grid()
            plt.legend()
            plt.title("DIFF :: Address " + str(address) + " (T ~ " + str(round(threshold)) + ")")
            plt.xlabel("min")
            plt.ylabel("delta std v ft/min")
            
        plt.suptitle("Filtered Data & Standard deviation (Std) of IVV & BAR. Filtered with n = " + str(self.medianN) + " for addresses", fontsize=20)
        plt.show()
        
        return True
        
    def plotLocation(plotData: List[Dict[str, Union[str, List[LOCATION_DATA]]]]) -> bool:
        import gui.scripts.world as w
        
        worldMap = gpd.GeoDataFrame.from_features(w.WORLD["features"])
        fig, ax = plt.subplots(num="MODE-S @ LOCATION")
        worldMap.boundary.plot(ax=ax, edgecolor="black")
        ax.set_xlim(GUI_CONSTANTS.DE_MIN_LONGITUDE, GUI_CONSTANTS.DE_MAX_LONGITUDE)
        ax.set_ylim(GUI_CONSTANTS.DE_MIN_LATITUDE, GUI_CONSTANTS.DE_MAX_LATITUDE)
        ax.set(aspect=1.78)
        
        r = 1
        g = 0
        b = 0
        maxColor= 255 / 255
        minColor= 0 
        for index in range(len(plotData)):
            longitude = [point.longitude for point in plotData[index]["points"]]
            latitude = [point.latitude for point in plotData[index]["points"]]
            
            if index >= 18 and index < 36:
                maxColor = 250 / 255 
                minColor = 112 / 255
            elif index >= 36 and index < 54:
                maxColor = 240 / 255
                minColor = 168 / 255
            else:
                maxColor = 255 / 255
                minColor = 0
                
            if r < minColor: r = minColor         
            if g < minColor: g = minColor         
            if b < minColor: b = minColor
            if r > maxColor: r = maxColor         
            if g > maxColor: g = maxColor         
            if b > maxColor: b = maxColor

            label = str(plotData[index]["address"]) + "(" + str(len(plotData[index]["points"]))+ ")"
            plt.plot(longitude, latitude, color=(r, g, b), marker=".", ms=1, linestyle="none", label=label)

            colorRatio = 85/255
            if r == maxColor and b == minColor and g != maxColor: g += colorRatio
            elif g == maxColor and b == minColor and r != minColor: r -= colorRatio
            elif g == maxColor and r == minColor and b != maxColor: b += colorRatio
            elif b == maxColor and r == minColor and g != minColor: g -= colorRatio
            elif b == maxColor and g == minColor and r != maxColor: r += colorRatio
            elif r == maxColor and g == minColor and b != minColor: b -= colorRatio
            
        fig.tight_layout()
        
        plt.suptitle("Data of the addresses with the most points (" + str(len(plotData)) + "), mercator proj" )
        plt.legend(bbox_to_anchor=(1,1), loc="upper left", title="Addresses (number points)", ncol=3)
        plt.show()        
        return True

    def plotHeatMap(heatMap: List[Dict[str, Union[str, List[LOCATION_DATA]]]] = [], rawLocation: List[Dict[str, Union[str, List[LOCATION_DATA]]]] = []) -> bool:
        import gui.scripts.world as w
        
        fig = plt.figure(num="MODE-S @ HEAT MAP")
        
        ax1 = fig.add_subplot(1, 2, 1)
        
        worldMap = gpd.GeoDataFrame.from_features(w.WORLD["features"])
        worldMap.boundary.plot(ax=ax1, edgecolor="black")
        
        ax1.set_xlim(GUI_CONSTANTS.DE_MIN_LONGITUDE, GUI_CONSTANTS.DE_MAX_LONGITUDE)
        ax1.set_ylim(GUI_CONSTANTS.DE_MIN_LATITUDE, GUI_CONSTANTS.DE_MAX_LATITUDE)
        ax1.set(aspect=1.78)
        
        allTurbulentLongitude = []
        allTurbulentLatitude = []
        
        legendHandles = []
        legendLabels = []
        
        for location in rawLocation:
            longitude = [point.longitude for point in location["points"]]
            latitude = [point.latitude for point in location["points"]]
            ax1.plot(longitude, latitude, color=(0.6, 0.6, 0.6, 0.1), marker=",", ms=1, linestyle="none")

        for turbulentLocation in heatMap:
            longitude = [point.longitude for point in turbulentLocation["points"]]
            latitude = [point.latitude for point in turbulentLocation["points"]]
            
            if len(turbulentLocation["points"]) > 0 :
                label = str(turbulentLocation["address"]) + "(" + str(len(turbulentLocation["points"]))+ ")"
                
                allTurbulentLongitude += longitude
                allTurbulentLatitude += latitude

                # self.logger.debug("Turbulent address: " + str(turbulentLocation["address"]) + ". Longitudes:" + str(
                # longitude) + ":: Latitudes:" + str(latitude))

                points = ax1.plot(longitude, latitude, color="red", marker=".", ms=1, linestyle="none", label=label)                

                legendHandles += points
                legendLabels += label
        
        ax2 = fig.add_subplot(1, 2, 2)
        
        worldMap.boundary.plot(ax=ax2, edgecolor="black")
        
        ax2.set_xlim(GUI_CONSTANTS.DE_MIN_LONGITUDE, GUI_CONSTANTS.DE_MAX_LONGITUDE)
        ax2.set_ylim(GUI_CONSTANTS.DE_MIN_LATITUDE, GUI_CONSTANTS.DE_MAX_LATITUDE)
        ax2.set(aspect=1.78)

        sb.histplot(x=allTurbulentLongitude, y=allTurbulentLatitude, ax=ax2, kde=True, cmap=ListedColormap(["orange", "red", "maroon"]))

        # fig.legend(legendHandles, legendLabels, bbox_to_anchor=(0,0), loc="upper left", title="Addresses (number points)", ncol=3)
        plt.suptitle("Turbulence Areas (from " + str(len(legendLabels)) + " addresses), mercator proj")
        plt.show()        
        return True
