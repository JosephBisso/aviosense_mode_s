
import concurrent.futures
from typing import List, Dict, Union
from collections import Counter

import numpy as np
import matplotlib.pyplot as plt

from logger import Logger

class ENGINE_CONSTANTS:
    PLOTS = ["occurrence", "bar_ivv", "filtered", "interval"]

class Engine:
    def __init__(self, logger: Logger, dataset: List[Dict[str, Union[str, int]]] = [], plots: List[str] = []):
        self.data: List[Dict[str, Union[str, int]]] = sorted(dataset, key=lambda el: el["address"])
        self.logger = logger
        self.plots: Dict[str, bool] = self.__activatePlot(plots)
        
    def __activatePlot(self, plots:List[str]):
        plots_insensitive = [plot.lower() for plot in plots]
        plots = {plot: plot in plots_insensitive for plot in ENGINE_CONSTANTS.PLOTS}
        self.logger.log("Status of Plots: " + str(plots))
        return plots
        
    def __plotResult(self, computed: concurrent.futures.Future, plot:str):
        if plot == "occurrence": 
            return self.plotDataPointOccurrences(occurrences=computed.result())
        elif plot == "bar_ivv":
            return self.plotDataPointOccurrences(occurrences=computed.result())
        elif plot == "filtered":
            return self.plotDataPointOccurrences(occurrences=computed.result())
        elif plot == "interval":
            return self.plotDataPointOccurrences(occurrences=computed.result())
        
    def setDataSet(self, dataset: List[Dict[str, Union[str, int]]]):
        self.data = sorted(dataset, key=lambda el: el["address"])
        
        if len(self.plots) < 1 : return
        
        executor = concurrent.futures.ThreadPoolExecutor()
        
        if "occurrence" in self.plots.keys():
            plot = "occurrence"
            computing = executor.submit(self.updateOccurrencesForAddresses)
        elif "bar_ivv" in self.plots.keys():
            plot = "bar_ivv"
            computing = executor.submit(self.updateOccurrencesForAddresses)
        elif "filtered" in self.plots.keys():
            plot = "filtered"
            computing = executor.submit(self.updateOccurrencesForAddresses)
        elif "interval" in self.plots.keys():
            plot = "interval"
            computing = executor.submit(self.updateOccurrencesForAddresses)
            
        plotted = self.__plotResult(computing, plot)
        
        if plotted: self.logger.info("Successfully plotted plot:" + "plot")
        else: self.logger.warning("Could not plot occurrence on addresses")
        
    def updateOccurrencesForAddresses(self):
        dataPoints_counter = Counter([entry["address"] for entry in self.data])
        dataPoint = list(dataPoints_counter.values())
        dataPoint.sort(reverse=True)
        return dataPoint
        
    def plotDataPointOccurrences(self, occurrences: List[Union[str, int]]) -> True:
        self.logger.info("Plotting occurrence on addresses")
        
        plt.plot(range(1, len(occurrences) + 1), occurrences, marker='o', color='b', linestyle='None', ms=1.75)
        plt.xlabel("Number of addresses")
        plt.ylabel("Number of datapoints")
        plt.title("Datapoints over addresses")
        plt.show()
        
        return True
