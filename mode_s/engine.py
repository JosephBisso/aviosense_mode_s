
import concurrent.futures
import sys
from typing import List, Dict, NamedTuple, Union
from collections import Counter, namedtuple

import math
import matplotlib.pyplot as plt

from logger import Logger

class POINT(NamedTuple):
    time: float
    bar: float
    ivv: float
    
class ENGINE_CONSTANTS:
    PLOTS = ["occurrence", "bar_ivv", "filtered", "interval"]
    
    # START_TIME_NANO = 1625559990537752100 #nanoseconds
    
class Engine:
    def __init__(self, logger: Logger, plots: List[str] = [], plot_addresses: List[str] = []):
        self.logger = logger
        self.plots: Dict[str, bool] = self.__activatePlot(plots)
        self.plot_addresses = [int(address) for address in plot_addresses]
        
    def __activatePlot(self, plots:List[str]):
        plots_insensitive = [plot.lower() for plot in plots]
        plots = {plot: plot in plots_insensitive for plot in ENGINE_CONSTANTS.PLOTS}
        self.logger.log("Engine will compute and plot for : " + str(plots))
        return plots
        
    def setDataSet(self, dataset: List[Dict[str, Union[str, int]]]):
        self.data = sorted(dataset, key=lambda el: el["address"])
        
        if len(self.plots) < 1 : return
        
        executor = concurrent.futures.ThreadPoolExecutor()
        plotted = False
        if self.plots["occurrence"]:
            dataPoint__future = executor.submit(self.prepareOccurrencesForAddresses)
            plotted = self.plotDataPointOccurrences(occurrences=dataPoint__future.result())

        elif self.plots["bar_ivv"]:
            if len(self.plot_addresses) == 0: 
                addresses__future = executor.submit(self.prepareOccurrencesForAddresses, "addresses")
                addresses_to_plot = addresses__future.result()[:9]
            else:
                addresses_to_plot = self.plot_addresses
                
            self.logger.log("Plotting for following addresses: " + str(addresses_to_plot))
            data_bar_ivv_time__future = executor.submit(self.prepareBar_ivv, addresses_to_plot)
            plotted = self.plotBar_ivv(data_bar_ivv_time__future.result())
            
        elif self.plots["filtered"]:
            plotted = "filtered"
        elif self.plots["interval"]:
            plotted = "interval"
        
        if plotted: self.logger.info("Successfully plotted")
        else: self.logger.warning("Nothing to plot")
        
    def prepareOccurrencesForAddresses(self, returnValue="datapoint") -> Union[List[Union[int, str]], List[int]]:
        dataPoints_counter = Counter([entry["address"] for entry in self.data])
        if returnValue != "datapoint": return [most_common_address[0] for most_common_address in (dataPoints_counter.most_common())]

        dataPoint = list(dataPoints_counter.values())
        dataPoint.sort(reverse=True)
        return dataPoint

    def prepareBar_ivv(self, addresses:List[int] = []) -> List[Dict[str, Union[str, List[POINT]]]]:
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

        startTime = min(times)
        addressData["points"] = [POINT((times[i] - startTime)*10**-9, bars[i], ivvs[i]) for i in range(len(times))]
        addressData["points"].sort(key=lambda el: el.time)

        if not alreadyFoundAddress : self.logger.warning("Could not find address " + str(address) + ". May be a Typo?")
        else: self.logger.debug("Address " + str(address) + ":: Plotting " + str(len(addressData["points"])) + " points.")
        return addressData
    
    def plotDataPointOccurrences(self, occurrences: List[Union[str, int]]) -> bool:
        self.logger.info("Plotting occurrence on addresses")
        
        plt.plot(range(1, len(occurrences) + 1), occurrences, marker='o', color='b', linestyle='None', ms=1.75)
        plt.xlabel("Number of addresses")
        plt.ylabel("Number of datapoints")
        plt.title("Datapoints over addresses")
        plt.show()
        
        return True
    
    def plotBar_ivv(self, plotData: List[Dict[str, Union[str, List[POINT]]]]) -> bool:
        self.logger.info("Plotting bar and ivv on time")
        
        if len(plotData) == 1:
            address = plotData[0]["address"]
            time = list(map(lambda el: el/60, [point.time for point in plotData[0]["points"]]))
            bar = [point.bar for point in plotData[0]["points"]]
            ivv = [point.ivv for point in plotData[0]["points"]]

            plt.plot(time, bar, marker='.', color='b', linestyle='-', ms=1)
            plt.plot(time, ivv, marker='.', color='r', linestyle='-', ms=1)
            plt.grid()
            
            plt.xlabel("min")
            plt.ylabel("v ft/min")
            plt.title("ivv & bar(blue) for address " + str(address) + " (" + str(len(plotData[0]["points"]))+ " points)")
            
            plt.show()
            return True
        
        for index in range(len(plotData)):
            address = plotData[index]["address"]
            time = list(map(lambda el: el/60, [point.time for point in plotData[index]["points"]]))
            bar = [point.bar for point in plotData[index]["points"]]
            ivv = [point.ivv for point in plotData[index]["points"]]
            
            height = int(math.sqrt(len(plotData))) % 5
            if height == 0: height = 1
            width = int(len(plotData) / height) % 5
            if width == 0: width = 1
            plt.subplot(width, height, index + 1)
            plt.subplots_adjust(wspace=0.5, hspace=0.5)
            plt.plot(time, bar, marker=',', color='b', linestyle='-', ms=0.25)
            plt.plot(time, ivv, marker=',', color='r', linestyle='-', ms=0.25)
            plt.grid()

            plt.xlabel("min")
            plt.ylabel("v ft/min")
            plt.title("ivv & bar(blue) for address " + str(address) + " (" + str(len(plotData[index]["points"]))+ " points)")
        
        plt.show()
        
        return True
