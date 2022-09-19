
import multiprocessing
import sys
import os
import json
import statistics
import concurrent.futures
from collections import Counter
from typing import Any, List, Dict, Union

import numpy as np
from scipy.signal import medfilt
from sklearn.neighbors import KernelDensity

import process
from logger import Logger
from constants import ENGINE_CONSTANTS, MODE_S_CONSTANTS, LOGGER_CONSTANTS
from constants import DATA, WINDOW_POINT, WINDOW_DATA, LOCATION_DATA


class EngineError(BaseException):
    pass


class Engine:

    maxNumberThreads: int = ENGINE_CONSTANTS.MAX_NUMBER_THREADS_ENGINE

    data: List[Dict[str, Union[str, float]]] = []
    plots: Dict[str, bool] = {}

    executors: List[concurrent.futures.Executor] = []
    pExecutor: concurrent.futures.ProcessPoolExecutor = None

    gui = False
    plotAddresses: List[int] = []
    medianN: int = ENGINE_CONSTANTS.MEDIAN_N
    kdeBW: int = ENGINE_CONSTANTS.KDE_BANDWIDTH
    minDataPoints: int = 1
    plotAll: bool = False

    def __init__(self, logger: Logger):
        self.logger: Logger = logger

    def setProcessExecutor(self, ex: concurrent.futures.ProcessPoolExecutor):
        self.pExecutor = ex

    def cancel(self) -> True:
        for ex in self.executors:
            ex.shutdown(wait=False)
        return True

    def setEngineParameters(self, **params):
        self.logger.info("Setting Engine Parameters")
        self.gui = params.get("gui") or False
        self.plotAll = params.get("plotAll") or False

        if params.get("plotAddresses"):
            self.plotAddresses = [int(address) for address in params["plotAddresses"]]
        else:
            self.plotAddresses = []
        if params.get("median"):
            self.medianN = params["median"] if params["median"] % 2 == 1 else params["median"] + 1
        else:
            self.medianN = ENGINE_CONSTANTS.MEDIAN_N
        if params.get("bandwidth"):
            self.kdeBW = params["bandwidth"]
        else:
            self.kdeBW = ENGINE_CONSTANTS.KDE_BANDWIDTH
        if params.get("enginethreads"):
            self.maxNumberThreads = params["enginethreads"]
        else:
            self.maxNumberThreads = ENGINE_CONSTANTS.MAX_NUMBER_THREADS_ENGINE
        if params.get("mindatapoints"):
            self.minDataPoints = params["mindatapoints"]
        else:
            self.minDataPoints = 1

        self.logger.log("Engines Max number of threads :", str(self.maxNumberThreads))
        self.logger.log("Setting median Filter to :", str(self.medianN))
        self.logger.log("Setting kde bandwidth to :", str(self.kdeBW))
        self.logger.log("Setting minimum data points to:", str(self.minDataPoints))
        if self.plotAll:
            self.logger.log("Watching all Addresses")
        elif self.plotAddresses:
            self.logger.log("Watching following address(es) : " + str(self.plotAddresses))

    def activatePlot(self, plots:List[str]):
        self.logger.info("Activating Engine Plots.")
        plotsInsensitive = [plot.lower() for plot in plots]
        plots = {plot: plot in plotsInsensitive for plot in ENGINE_CONSTANTS.PLOTS}

        abs = []
        for plot in plotsInsensitive:
            if plot not in ENGINE_CONSTANTS.PLOTS:
                abs.append(plot)
        if len(abs) > 0 : self.logger.warning("Following Plots are unknown. May be a Typo? : " + str(abs))

        self.logger.log("Engine plot status : " + str(plots))

        self.plots = plots

    def setDataSet(self, dataset: List[Dict[str, Union[str, int]]]):
        self.data = sorted(dataset, key=lambda el: el["address"])

        # import json
        # with open("engine.dump.json", "w") as dbd:
        #     json.dump(self.data, dbd)

    def compute(self, usePlotter=True) -> None:
        try:
            self.logger.info("Starting Engine")
            self.logger.progress(LOGGER_CONSTANTS.ENGINE, "Computing [0/11]")
            if not self.data:
                self.logger.debug("Using Dump DB")
                dumpDB = self.__loadDBfromDump()
                if not dumpDB: 
                    self.logger.progress(LOGGER_CONSTANTS.ENGINE, LOGGER_CONSTANTS.END_PROGRESS_BAR)
                    raise EngineError("Engine has no data to compute")
                else:
                    self.data = dumpDB
            if usePlotter and not any(self.plots.values()):
                return

            activePlots = self.plots

            if not usePlotter:
                from analysis import Analysis
                Analysis.setKDEBandwidth(self.kdeBW)
                activePlots = {plot: True for plot in ENGINE_CONSTANTS.PLOTS}
            else:
                from plotter import Plotter
                Plotter.updateUsedMedianFilter(self.medianN)
                Plotter.setKDEBandwidth(self.kdeBW)

            plotted = []

            if activePlots["occurrence"]:
                dataPoints = self.prepareOccurrencesForAddresses()
                if usePlotter:
                    self.logger.info("Plotting occurrence on addresses")
                    plotted.append(Plotter.plotDataPointOccurrences(occurrences=dataPoints))
                else:
                    self.logger.info("Getting lineSeries for  occurrence on addresses")
                    lineSeriesOccurrence = Analysis.getLineSeriesDataPointOccurrences(dataPoints)
                    yield lineSeriesOccurrence

            self.logger.progress(LOGGER_CONSTANTS.ENGINE, "Computing [1/11]")

            allAddresses = self.prepareOccurrencesForAddresses("addresses")
            mostPointAddresses = allAddresses[:4]
            if self.plotAddresses:
                addressesToPlot = self.plotAddresses
            elif self.plotAll or not usePlotter:
                addressesToPlot = allAddresses
            else:
                addressesToPlot = mostPointAddresses

            if len(addressesToPlot) < 5: self.logger.info("Working with following addresses: " + str(addressesToPlot))
            else: self.logger.info("Working with " + str(len(addressesToPlot)) + " addresses")

            if not usePlotter:
                yield addressesToPlot
                
            self.logger.progress(LOGGER_CONSTANTS.ENGINE, "Computing [2/11]")
                
            data = self.prepareBarAndIvvAndTime(addressesToPlot)

            if activePlots["bar_ivv"]:
                if usePlotter:
                    self.logger.info("Plotting bar and ivv on time")
                    plotted.append(Plotter.plotBarAndIvv(data))
                else:
                    self.logger.info("Getting lineSeries for raw bar & ivv")
                    lineSeriesBarIvv = Analysis.getLineSeriesBarAndIvv(data)
                    yield lineSeriesBarIvv

            self.logger.progress(LOGGER_CONSTANTS.ENGINE, "Computing [3/11]")

            if usePlotter:
                if activePlots["filtered"] and not activePlots["std"]:
                    self.prepareMedianFilter(data)
                    self.logger.info("Plotting filtered bar and ivv on time")
                    plotted.append(Plotter.plotFilteredBarAndIvv(data))

            if activePlots["interval"]:
                slidingIntervals = self.prepareSlidingInterval(data)
                if usePlotter:
                    self.logger.info("Plotting sliding Intervals")
                    plotted.append(Plotter.plotSlidingInterval(slidingIntervals))
                else:
                    self.logger.info("Getting lineSeries for sliding interval")
                    lineSeriesInterval = Analysis.getLineSeriesSlidingInterval(slidingIntervals)
                    yield lineSeriesInterval

            self.logger.progress(LOGGER_CONSTANTS.ENGINE, "Computing [4/11]")

            if activePlots["std"]:
                self.prepareMedianFilter(data)

                if not usePlotter:
                    self.logger.info("Getting line series for filtered bar and ivv on time")
                    lineSeriesFilteredBarAndIvv = Analysis.getLineSeriesFilteredBarAndIvv(data)
                    yield lineSeriesFilteredBarAndIvv

                self.logger.progress(LOGGER_CONSTANTS.ENGINE, "Computing [5/11]")

                slidingIntervalForStd = self.prepareSlidingIntervalForStd(data) 
                if usePlotter:
                    if activePlots["filtered"]:
                        self.logger.info("Plotting filtered data and standard deviations")
                        plotted.append(Plotter.plotFilteredAndStd(filteredData=data, stdData=slidingIntervalForStd))
                    else:
                        self.logger.info("Plotting standard deviations")
                        plotted.append(Plotter.plotSlidingIntervalForStd(slidingIntervalForStd))
                else:
                    self.logger.info("Getting lineSeries for sliding interval for Std")
                    lineSeriesStd = Analysis.getLineSeriesSlidingIntervalForStd(slidingIntervalForStd)
                    yield lineSeriesStd

                    self.logger.progress(LOGGER_CONSTANTS.ENGINE, "Computing [6/11]")

                    exceedingData = self.prepareExceedingData(slidingIntervalForStd)
                    self.logger.info("Getting lineSeries for Exceeding data")
                    lineSeriesExceeds = Analysis.getLineSeriesForExceeds(exceedingData)
                    yield lineSeriesExceeds
                    

            self.logger.progress(LOGGER_CONSTANTS.ENGINE, "Computing [7/11]")

            if activePlots["location"]:
                location = self.prepareLocation(addressesToPlot)
                if usePlotter:
                    self.logger.info("Plotting location")
                    plotted.append(Plotter.plotLocation(location))
                else:
                    self.logger.info("Getting lineSeries for location")
                    lineSeriesLocation = Analysis.getLineSeriesLocation(location)
                    yield lineSeriesLocation

            self.logger.progress(LOGGER_CONSTANTS.ENGINE, "Computing [8/11]")

            if activePlots["heat_map"]:
                if not activePlots["filtered"] and not activePlots["std"]:
                    self.prepareMedianFilter(data)
                if not activePlots["std"]:
                    slidingIntervalForStd = self.prepareSlidingIntervalForStd(data)
                if not activePlots["location"]:
                    location = self.prepareLocation(addressesToPlot)
                    
                heatMap = self.prepareHeatMap(slidingIntervalForStd)
                
                if usePlotter:
                    self.logger.info("Plotting heat map")
                    plotted.append(Plotter.plotHeatMap(heatMap=heatMap, rawLocation=location))
                else:
                    self.logger.info("Getting lineSeries for turbulent location")
                    lineSeriesTurbulent = Analysis.getLineSeriesTurbulentLocation(heatMap)
                    yield lineSeriesTurbulent
                    
                    self.logger.progress(LOGGER_CONSTANTS.ENGINE, "Computing [9/11]")
                    
                    self.logger.info("Getting lineSeries for heat map")
                    lineSeriesHeatMap, allKdeZoneData = Analysis.getLineSeriesHeatMap(heatMap)
                    yield lineSeriesHeatMap
                    
                    self.logger.progress(LOGGER_CONSTANTS.ENGINE, "Computing [10/11]")

                    lineSeriesKDEExceeds = self.generateKDEZone(allKdeZoneData, slidingIntervalForStd)
                    self.logger.info("Yielding lineSeries for kde exceeds")
                    yield lineSeriesKDEExceeds

            self.logger.progress(LOGGER_CONSTANTS.ENGINE, "Computing [11/11]")

            if not usePlotter:
                self.logger.success("Successfully computed")
            elif all(plotted):
                self.logger.success("Successfully plotted")
            else:
                self.logger.warning("Error while plotting")

        except Exception as exc:
            type, value, traceback = sys.exc_info()
            self.logger.critical("Error Occurred: Engine Compute::\n" + str(type) + "::" + str(value))
            self.logger.critical("Error raised at Frame:", traceback.tb_frame)
            raise EngineError("Computing failed because of the exception:", str(exc))

        finally:
            self.logger.progress(LOGGER_CONSTANTS.ENGINE, LOGGER_CONSTANTS.END_PROGRESS_BAR)
        
    def loadDump(self):
        self.logger.info("Loading Dump")
        ms = MODE_S_CONSTANTS
        
        toLoadDump = [ms.OCCURRENCE_DUMP, ms.INDENT_MAPPING, ms.BAR_IVV_DUMP, ms.INTERVAL_DUMP,
                      ms.FILTERED_DUMP, ms.STD_DUMP, ms.EXCEEDS_DUMP, ms.LOCATION_DUMP, ms.TURBULENCE_DUMP, ms.HEATMAP_DUMP, ms.KDE_EXCEEDS_DUMP]
        for dump in toLoadDump:
            try:
                if not os.path.exists(dump): 
                    yield []
                    continue
                with open(dump, "r") as dumpF:
                    loaded = json.load(dumpF)
                    yield loaded
            except Exception as esc:
                type, value, traceback = sys.exc_info()
                self.logger.warning("Error occurred while loading dump", dump, "::", type, value)
                yield []
    
    def __loadDBfromDump(self) -> List[Dict[str, Union[str, float]]]:
        self.logger.info("Loading DB from dump")
        loadedDB = []
        try:
            with open(MODE_S_CONSTANTS.DATABASE_DUMP, "r") as dumpDB:
                loadedDB = json.load(dumpDB)
        except Exception as esc:
            type, value, traceback = sys.exc_info()
            self.logger.warning("Error occurred while loading dump database::", type, value)
        finally:
            return loadedDB

    def prepareOccurrencesForAddresses(self, returnValue="datapoint") -> Union[List[Union[int, str]], List[int]]:
        self.logger.log("Computing Occurrences for Addresses")
        dataPointsCounter = Counter([entry["address"] for entry in self.data])
        if returnValue != "datapoint":
            return [mostCommonAddress[0] for mostCommonAddress in dataPointsCounter.most_common() if mostCommonAddress[1] > self.minDataPoints]

        dataPoint = list(dataPointsCounter.values())
        dataPoint.sort(reverse=True)
        return dataPoint

    def prepareBarAndIvvAndTime(self, addresses:List[int] = []) -> List[Dict[str, Union[str, List[DATA]]]]:
        self.logger.log("Computing bar, ivv and time")
        plotData = []
        
        addressData__futures = []
        maxProcesses = min(len(addresses), multiprocessing.cpu_count())
        addressesPerProcess = int(len(addresses) / maxProcesses)
        for i in range(maxProcesses):
            startIndex = i*addressesPerProcess
            endIndex = startIndex + addressesPerProcess if i < maxProcesses - 1 else None
            pack = addresses[startIndex : endIndex]
            if not pack:
                continue
            addressData__futures.append(self.pExecutor.submit(process.getRawData, pack, self.data))
            
        for completedThread in concurrent.futures.as_completed(addressData__futures):
            try:
                addressData = completedThread.result()
            except AssertionError as e:
                self.logger.warning(str(e))
            except Exception as esc:
                type, value, traceback = sys.exc_info()
                self.logger.critical(
                    "Error occurred while computing raw data for addresses\n" + str(type) + "::" + str(value))
            else:
                plotData.extend(addressData)
        
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
                self.logger.critical(
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
                self.logger.critical(
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
                self.logger.critical(
                    "Error occurred while preparing sliding interval for std per addresses\n" + str(type) + "::" + str(value))
            else:
                if slidingIntervalForStdPerAddress: slidingIntervalForStd.append(slidingIntervalForStdPerAddress)

        executor.shutdown()
        return slidingIntervalForStd

    def prepareExceedingData(self, data: List[Dict[str, Union[str, List[DATA]]]]) -> List[Dict[str, Union[str, List[WINDOW_DATA], float]]]:
        self.logger.log("Computing exceeding data")
        exceedingData = []
        executor = self.__executor()
        exceedingData__futures = [executor.submit(
            self.__getExceedingDataPerAddress, addressData) for addressData in data]

        for completedThread in concurrent.futures.as_completed(exceedingData__futures):
            try:
                exceedingDataPerAddress = completedThread.result()
            except EngineError as e:
                self.logger.warning(str(e))
            except Exception as esc:
                type, value, traceback = sys.exc_info()
                self.logger.critical(
                    "Error occurred while preparing exceeding data per addresses\n" + str(type) + "::" + str(value))
            else:
                if exceedingDataPerAddress: exceedingData.append(exceedingDataPerAddress)

        executor.shutdown()
        return exceedingData

    def prepareLocation(self, addresses: List[int] = []) -> List[Dict[str, Union[str, List[LOCATION_DATA]]]]:
        self.logger.log("Computing locations")
        allLocationData = []
        
        addressPoints: List[LOCATION_DATA] = []
         
        for index in range(len(self.data)):
            if self.data[index]["address"] not in addresses: continue
            time = self.data[index]["timestamp"]
            longitude = self.data[index]["longitude"]
            latitude = self.data[index]["latitude"]
            
            if longitude is None or latitude is None : continue

            addressPoints.append(LOCATION_DATA(time, longitude, latitude))

            if index == len(self.data) - 1 or self.data[index]["address"] != self.data[index + 1]["address"]:
                addressPoints.sort(key=lambda el: el.time)

                allLocationData.append({
                    "address": self.data[index]["address"],
                    "identification": self.data[index].get("identification"),
                    "points": addressPoints
                })
                
                addressPoints = []
        
        return allLocationData
    
    def prepareHeatMap(self, slidingIntervallForStd: List[Dict[str, Union[str, List[WINDOW_DATA], float]]] = []) -> List[Dict[str, Union[str, List[LOCATION_DATA]]]]:
        self.logger.log("Computing heat map")
        heatPoints: List[Dict[str, Union[str, List[LOCATION_DATA]]]] = []
        
        heatPoints__future = []
        maxProcesses = min(len(slidingIntervallForStd), multiprocessing.cpu_count())
        addressDataPerProcess = int(len(slidingIntervallForStd) / maxProcesses)
        for i in range(maxProcesses):
            startIndex = i*addressDataPerProcess
            endIndex = startIndex + addressDataPerProcess if i < maxProcesses - 1 else None
            pack = slidingIntervallForStd[startIndex : endIndex]
            if not pack:
                continue
            heatPoints__future.append(self.pExecutor.submit(process.getHeatPoints, pack, self.data))

        for completedThread in concurrent.futures.as_completed(heatPoints__future):
            try:
                heatPointsPerAddress = completedThread.result()
            except AssertionError as e:
                self.logger.warning(str(e))
            except Exception as esc:
                type, value, traceback = sys.exc_info()
                self.logger.critical(
                    "Error occurred while preparing heatmap per addresses\n" + str(type) + "::" + str(value))
            else:
                heatPoints.extend(heatPointsPerAddress)
                
        return heatPoints
    
    def generateKDEZone(self, allKdeZone: List[Dict[str, Union[float, List[Dict[str, float]]]]], slidingIntervallForStd: List[Dict[str, Union[str, List[WINDOW_DATA]]]] = []) -> Dict[str, Dict[str, Union[str, List[float]]]]:
        self.logger.log("Generating KDE Zone")
        lineSeriesKDEExceeds = {}
        
        kdeZone__futures = []
        maxProcesses = min(len(allKdeZone), multiprocessing.cpu_count())
        addressesPerProcess = int(len(allKdeZone) / maxProcesses)
        for i in range(maxProcesses):
            startIndex = i*addressesPerProcess
            endIndex = startIndex + addressesPerProcess if i < maxProcesses - 1 else None
            pack = allKdeZone[startIndex: endIndex]
            if not pack:
                continue
            kdeZone__futures.append(self.pExecutor.submit(
                process.getKDEExceeds, pack, slidingIntervallForStd, self.kdeBW))

        for completedThread in concurrent.futures.as_completed(kdeZone__futures):
            try:
                kdeExceedData = completedThread.result()
            except AssertionError as e:
                self.logger.warning(str(e))
            except Exception as esc:
                type, value, traceback = sys.exc_info()
                self.logger.critical(
                    "Error occurred while computing kde zone exceeds\n" + str(type) + "::" + str(value))
            else:
                lineSeriesKDEExceeds.update(kdeExceedData)

        return lineSeriesKDEExceeds

    def __executor(self) -> concurrent.futures.ThreadPoolExecutor:
        ex = concurrent.futures.ThreadPoolExecutor(
            thread_name_prefix="engine_thread", max_workers=self.maxNumberThreads)
        self.executors.append(ex)
        return ex

    def __getDataForAddress(self, address: int) -> Dict[str, Union[str, List[DATA]]]:
        addressData: Dict[str, Union[str, List[int]]] = {
            "address": address,
            "points": []
        }

        identification = None
        bars = []
        ivvs = []
        times = []

        startIndex = None
        for index in range(len(self.data)):
            if self.data[index]["address"] != address: continue
            identification = self.data[index].get("identification")
            startIndex = index
            break

        if startIndex is None:
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
        addressData["identification"] = identification
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
        
        slidingIntervals:Dict[str, Union[str, List[WINDOW_POINT]]]  = {
            "address": addressData["address"], 
            "identification": addressData.get("identification"),
            "points":[]
        }
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
            "identification": addressData.get("identification"),
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
            
        # From Paper
        arrayBarStds = np.array(barStds)
        arrayIvvStds = np.array(ivvStds)
        diffStds = arrayBarStds - arrayIvvStds
        
        ddof = 1 if len(diffStds) > 1 else 0
        threshold = np.average(diffStds) + 1.2 * np.std(diffStds, ddof=ddof)
        slidingIntervalsForStd["threshold"] = threshold
        
        # self.logger.debug("Valid results for sliding interval for std for address " + str(
        #     addressData["address"]) + ". Points Count: " + str(len(slidingIntervalsForStd["points"])))

        return slidingIntervalsForStd

    def __getExceedingDataPerAddress(self, addressData: Dict[str, Union[str, List[WINDOW_DATA]]]) -> Dict[str, Union[str, Dict[int, int]]]:
        exceedingData: Dict[str, Union[str, Dict[int, int]]] = {
            "address": addressData["address"],
            "identification": addressData.get("identification"),
            "distribution": {
                "0": 0, "10": 0, "20": 0, "30": 0, "40": 0, "50": 0, "60": 0, "70": 0, "80": 0, "90": 0, "100": 0
            },
            "smoothed": []
        }
        
        threshold = addressData["threshold"]
        
        if threshold == 0:
            self.logger.warning(f"No Threshold for address {addressData['address']}")
            return exceedingData
        
        allDiffs = [point.bar - point.ivv for point in addressData["points"]]

        exceeds = [100*(diff - threshold)/threshold for diff in allDiffs if diff >= threshold]
        
        if not exceeds:
            return exceedingData
        
        sizeRatio = 10
        
        exceedingPercentageGroup = []

        for exceedingPercentage in exceeds:
            percentage = next((dist for dist in exceedingData["distribution"] if int(dist) <= exceedingPercentage < int(dist) + 10), "100")
            exceedingData["distribution"][percentage] += 1
            exceedingPercentageGroup.append(int(percentage)/sizeRatio)

        exceedsShape = np.array(exceedingPercentageGroup).reshape(-1, 1)
        Xs = np.linspace(0, 100/sizeRatio, num=1000).reshape(-1, 1)
        
        kde = KernelDensity(kernel="gaussian", bandwidth=self.kdeBW).fit(exceedsShape)
        density = np.exp(kde.score_samples(Xs))

        exceedingData["smoothed"] = density.tolist()

        return exceedingData

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

        if startIndex is None:
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
                LOCATION_DATA(time, longitude, latitude)
            )
            
        if allTimes: closestTimes.insert(0, min(allTimes))
        
        # if len(heatPointsForAddress) < len(turbulentSlidingWindows):
        #     self.logger.debug("Doubtful results for Heat Points for address " + str(
        #         addressData["address"]) + ". Points Count: " + str(len(heatPointsForAddress)) + "| Found longitude and latitude data? " + str(foundLongitude) + 
        #         " | Found window? " + str(foundWindow) + " | turbulent sliding windows: " + str(turbulentSlidingWindows) + " | closest Times: " + str(closestTimes))

        # else:
        #     self.logger.debug("Valid results for Heat Points for address " + str(
        #         addressData["address"]) + ". Points Count: " + str(len(heatPointsForAddress)))

        return {"address": addressData["address"], "identification": addressData.get("identification"),  "points": heatPointsForAddress}
