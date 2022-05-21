
import concurrent.futures
import sys
from typing import List, Dict, NamedTuple, Union
from collections import Counter, namedtuple

import math
import numpy as np
from scipy.signal import medfilt
import matplotlib.pyplot as plt

from logger import Logger

class POINT(NamedTuple):
    time: float # in Seconds
    bar: float
    ivv: float
    
class WINDOW_POINT(NamedTuple):
    window: float 
    points: int
    
class ENGINE_CONSTANTS:
    PLOTS = ["occurrence", "bar_ivv", "filtered", "interval"]
    
class Engine:
    def __init__(self, logger: Logger, plots: List[str] = [], plotAddresses: List[str] = [], medianN: int = 1, durationLimit:int = None):
        self.logger = logger
        self.plots: Dict[str, bool] = self.__activatePlot(plots)
        self.plotAddresses = [int(address) for address in plotAddresses]
        self.medianN = int(medianN)
        self.durationLimit = float(durationLimit) if durationLimit else None
        
    def __activatePlot(self, plots:List[str]):
        plotsInsensitive = [plot.lower() for plot in plots]
        plots = {plot: plot in plotsInsensitive for plot in ENGINE_CONSTANTS.PLOTS}

        abs = []
        for plot in plotsInsensitive:
            if not plot in ENGINE_CONSTANTS.PLOTS: abs.append(plot)
        if len(abs) > 0 : self.logger.warning("Following Plots are unknown. May be a Typo? : " + str(abs))
        
        self.logger.log("Engine plot status : " + str(plots))
        return plots
         
    def __getDataForAddress(self, address: int) -> Dict[str, Union[str, List[POINT]]]:
        addressData: Dict[str, Union[str, List[int]]] = {
            "address": address,
            "points": []
        }

        bars = []
        ivvs = []
        times = []
        
        alreadyFoundAddress = False
        for entry in self.data:
            if not entry["address"] == address: 
                if alreadyFoundAddress: break 
                else: continue
                
            alreadyFoundAddress = True
            if not entry["bar"] or not entry["ivv"]: continue
            
            bars.append(entry["bar"])
            ivvs.append(entry["ivv"])
            times.append(entry["timestamp"])

        if not alreadyFoundAddress : self.logger.critical("Could not find address " + str(address) + ". May be a Typo?", NameError)

        startTime = min(times)
        addressData["points"] = [POINT((times[i] - startTime)*10**-9, bars[i], ivvs[i]) for i in range(len(times))]
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

        
        self.logger.debug("Address " + str(address) + ":: Plotting " + str(len(addressData["points"])) + " points.")
        return addressData

    def __applyMedianFilter(self, addressData: Dict[str, Union[str, List[POINT]]]) -> None:
        bars = [point.bar for point in addressData["points"]]
        ivvs = [point.ivv for point in addressData["points"]]
        times = [point.time for point in addressData["points"]]

        filteredBars: np.ndarray = medfilt(bars, self.medianN)
        filteredIvvs: np.ndarray = medfilt(ivvs, self.medianN)

        addressData["filteredPoints"] = [
            POINT(times[i], filteredBars[i], filteredIvvs[i]) for i in range(len(filteredBars))]

    def __getSlidingIntervalForAddress(self, addressData: Dict[str, Union[str, List[POINT]]]) -> Dict[str, Union[str, List[WINDOW_POINT]]]:
        times = [point.time for point in addressData["points"]]
        slidingWindows = [duration * 60 for duration in range(int(max(times) / 60))]
        
        allData:Dict[str, Union[str, List[WINDOW_POINT]]]  = {"address": addressData["address"], "points":[]}
        actualIndex = 0
        for windowIndex in range(len(slidingWindows)):
            dataPoints = 0
            for dataIndex in range(actualIndex, len(addressData["points"])):
                if addressData["points"][dataIndex].time > slidingWindows[windowIndex]: 
                    actualIndex = dataIndex
                    break
                dataPoints += 1
            
            allData["points"].append(WINDOW_POINT(slidingWindows[windowIndex]/60, dataPoints))
        
        return allData

    def setDataSet(self, dataset: List[Dict[str, Union[str, int]]]):
        self.data = sorted(dataset, key=lambda el: el["address"])
        
        if not any(self.plots.values()) : return
        
        executor = concurrent.futures.ThreadPoolExecutor()
        plotted = False
        
        if self.plots["occurrence"]:
            dataPoint__future = executor.submit(self.prepareOccurrencesForAddresses)
            plotted = self.plotDataPointOccurrences(occurrences=dataPoint__future.result())

        
        addresses__future = executor.submit(self.prepareOccurrencesForAddresses, "addresses")
        addressesToPlot = addresses__future.result()[:4] if len(self.plotAddresses) == 0 else self.plotAddresses
        self.logger.log("Plotting for following addresses: " + str(addressesToPlot))
            
        barAndIvvAndTime__future = executor.submit(self.prepareBarAndIvvAndTime, addressesToPlot)
        data = barAndIvvAndTime__future.result()
        if self.plots["bar_ivv"]:
            plotted = self.plotBarAndIvv(data)
            
        if self.plots["filtered"]:
            self.prepareMedianFilter(data)
            plotted = self.plotFilteredBarAndIvv(data)

        if self.plots["interval"]:
            slidingIntervals = self.prepareSlidingInterval(data)
            plotted = self.plotSlidingInterval(slidingIntervals)
        
        if plotted: self.logger.info("Successfully plotted")
        else: self.logger.warning("Nothing to plot")
        
    def prepareOccurrencesForAddresses(self, returnValue="datapoint") -> Union[List[Union[int, str]], List[int]]:
        dataPointsCounter = Counter([entry["address"] for entry in self.data])
        if returnValue != "datapoint": return [mostCommonAddress[0] for mostCommonAddress in (dataPointsCounter.most_common())]

        dataPoint = list(dataPointsCounter.values())
        dataPoint.sort(reverse=True)
        return dataPoint

    def prepareBarAndIvvAndTime(self, addresses:List[int] = []) -> List[Dict[str, Union[str, List[POINT]]]]:
        plotData = []
        executor = concurrent.futures.ThreadPoolExecutor()
        addressData__futures = [executor.submit(self.__getDataForAddress, address) for address in addresses]

        for completedThread in concurrent.futures.as_completed(addressData__futures):
            try:
                addressData = completedThread.result()
            except Exception as esc:
                type, value, traceback = sys.exc_info()
                self.logger.warning(
                    "Error occurred while computing data for addresses\n" + str(type) + "::" + str(value))
            else:
                plotData.append(addressData)
                
        return plotData

    def prepareMedianFilter(self, data: List[Dict[str, Union[str, List[POINT]]]]) -> None:
        self.logger.log("Filtering data with n set to: " + str(self.medianN))
        executor = concurrent.futures.ThreadPoolExecutor()
        filteredAddressData__futures = [executor.submit(
            self.__applyMedianFilter, addressData) for addressData in data]

        for completedThread in concurrent.futures.as_completed(filteredAddressData__futures):
            try:
                completedThread.result()
            except Exception as esc:
                type, value, traceback = sys.exc_info()
                self.logger.warning(
                    "Error occurred while filtering data for addresses\n" + str(type) + "::" + str(value))
                
    def prepareSlidingInterval(self, data: List[Dict[str, Union[str, List[POINT]]]]) -> None:
        slidingIntervals = []
        executor = concurrent.futures.ThreadPoolExecutor()
        slidingInterval__futures = [executor.submit(
            self.__getSlidingIntervalForAddress, addressData) for addressData in data]

        for completedThread in concurrent.futures.as_completed(slidingInterval__futures):
            try:
                slidingIntervalForAddress = completedThread.result()
            except Exception as esc:
                type, value, traceback = sys.exc_info()
                self.logger.warning(
                    "Error occurred while filtering data for addresses\n" + str(type) + "::" + str(value))
            else:
                slidingIntervals.append(slidingIntervalForAddress)
                
        return slidingIntervals
    
    def plotDataPointOccurrences(self, occurrences: List[Union[str, int]]) -> bool:
        self.logger.info("Plotting occurrence on addresses")
        
        plt.subplots(num="MODE-S @ Data Points Occurrence")
        plt.plot(range(1, len(occurrences) + 1), occurrences, marker='o', color='b', linestyle='None', ms=1.75)
        plt.xlabel("Number of addresses")
        plt.ylabel("Number of datapoints")
        plt.title("Datapoints over addresses")
        plt.show()
        
        return True
    
    def plotBarAndIvv(self, plotData: List[Dict[str, Union[str, List[POINT]]]]) -> bool:
        self.logger.info("Plotting bar and ivv on time")
        
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
            plt.legend(loc="upper right")
            plt.title("Address " + str(address) + " (" + str(len(plotData[index]["points"]))+ " points)")
                        
        plt.tight_layout()
        plt.suptitle("IVV & BAR for addresses", fontsize=20)
        plt.show()
        
        return True
        

    def plotFilteredBarAndIvv(self, plotData: List[Dict[str, Union[str, List[POINT]]]]) -> bool:
        self.logger.info("Plotting filtered bar and ivv on time")
        
        nCol = len(plotData)
        nRow = 2
        if nRow == 0: nRow = 1
        
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
            plt.legend(loc="upper right")

            plt.subplot(nRow, nCol, index + 1 + nCol)
            plt.subplots_adjust(wspace=0.5, hspace=0.5)
            plt.plot(time, ivv, marker=',', color='r', linestyle='-', ms=0.25, label="Raw IVV")
            plt.plot(time, filteredIvv, marker=',', color='#3ccf9b', linestyle='-', ms=0.25, label="Filtered IVV")
            plt.grid()
            plt.title("IVV :: Address " + str(address) + " (" + str(len(plotData[index]["points"]))+ " points)")
            plt.xlabel("min")
            plt.ylabel("v ft/min")
            plt.legend(loc="upper right")
            
        plt.tight_layout()
        plt.suptitle("IVV & BAR, Raw and Filtered with n = " + str(self.medianN) + " for addresses", fontsize=20)
        plt.show()
        
        return True
        
    def plotSlidingInterval(self, plotData: List[Dict[str, Union[str, List[WINDOW_POINT]]]]) -> bool:
        self.logger.info("Plotting sliding Intervals")
        
        nCol = int(round((len(plotData)/4) * 16/9))
        nRow = int(round(len(plotData) / nCol))
        
        plt.subplots(num="MODE-S @ Sliding Intervals")
        for index in range(len(plotData)):
            address = plotData[index]["address"]
            windows = [point.window for point in plotData[index]["points"]]
            points = [point.points for point in plotData[index]["points"]]

            plt.subplot(nRow, nCol, index + 1)
            plt.subplots_adjust(wspace=0.5, hspace=0.5)
            plt.step(windows, points, where="mid", marker=',', color='b', linestyle='-', linewidth=2)
            plt.grid()

            plt.xlabel("sliding window [min]")
            plt.ylabel("number of points [1]")
            plt.title("Address " + str(address))
                        
        plt.tight_layout()
        plt.autoscale(enable=True, axis="x", tight=True)
        plt.suptitle("Sliding Intervals for addresses", fontsize=20)
        plt.show()
        
        return True
        
