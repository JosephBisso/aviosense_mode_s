
import concurrent.futures
from typing import List, Dict, Union
from collections import Counter

import numpy as np
import matplotlib.pyplot as plt

from logger import Logger

class Engine:
    def __init__(self, logger: Logger, dataset: List[Dict[str, Union[str, int]]] = [], plots: List[str] = []):
        self.data: List[Dict[str, Union[str, int]]] = sorted(dataset, key=lambda el: el["address"])
        self.logger = logger
        self.occurrencePlot: bool = False
        
    def setDataSet(self, dataset: List[Dict[str, Union[str, int]]]):
        self.data = sorted(dataset, key=lambda el: el["address"])
        
    def updateOccurrencesForAddresses(self, plot: bool = False):
        dataPoints_counter = Counter([entry["address"] for entry in self.data])
        dataPoint = list(dataPoints_counter.values())
        dataPoint.sort(reverse=True)
        if plot or self.occurrencePlot: 
            plotted = self.plotDataPointOccurrences(occurrences=dataPoint)
            if plotted: self.logger.info("Successfully plotted occurrence on addresses")
            else: self.logger.warning("Could not plot occurrence on addresses")
        
    def plotDataPointOccurrences(self, occurrences: List[Union[str, int]]) -> True:
        self.logger.info("Plotting occurrence on addresses")
        
        plt.plot(range(1, len(occurrences) + 1), occurrences, marker='o', color='b', linestyle='None', ms=1.75)
        plt.xlabel("Number of addresses")
        plt.ylabel("Number of datapoints")
        plt.title("Datapoints over addresses")
        plt.show()
        
        return True
