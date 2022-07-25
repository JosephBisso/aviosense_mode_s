from typing import List, Dict, NamedTuple, Union

import seaborn as sb
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap

from constants import GUI_CONSTANTS
from constants import DATA, WINDOW_POINT, WINDOW_DATA, LOCATION_DATA

class Plotter:
    USED_MEDIAN_FILTER: int = 0
    KDE_BAND_WIDTH: int = 0.5
    
    def updateUsedMedianFilter(medianN:int = 0):
        Plotter.USED_MEDIAN_FILTER = medianN

    def setKDEBandwidth(bandwidth:int = 0.5):
        Plotter.KDE_BAND_WIDTH = bandwidth
    
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
            
        plt.suptitle("IVV & BAR, Raw and Filtered with n = " + str(Plotter.USED_MEDIAN_FILTER) + " for addresses", fontsize=20)
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
            
        plt.suptitle("Standard deviation (Std) of IVV & BAR. Data filtered with n = " + str(Plotter.USED_MEDIAN_FILTER) + " for addresses", fontsize=20)
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
            
        plt.suptitle("Filtered Data & Standard deviation (Std) of IVV & BAR. Filtered with n = " + str(Plotter.USED_MEDIAN_FILTER) + " for addresses", fontsize=20)
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
        
        for index in range(len(plotData)):
            longitude = [point.longitude for point in plotData[index]["points"]]
            latitude = [point.latitude for point in plotData[index]["points"]]

            label = str(plotData[index]["address"]) + "(" + str(len(plotData[index]["points"]))+ ")"
            plt.plot(longitude, latitude, marker=".", ms=1, linestyle="none", label=label)
            
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
        
        numShownAddresses = 0
        
        for location in rawLocation:
            longitude = [point.longitude for point in location["points"]]
            latitude = [point.latitude for point in location["points"]]
            ax1.plot(longitude, latitude, color=(0.6, 0.6, 0.6, 0.1), marker=",", ms=1, linestyle="none")

        for turbulentLocation in heatMap:
            longitude = [point.longitude for point in turbulentLocation["points"]]
            latitude = [point.latitude for point in turbulentLocation["points"]]
            
            if len(turbulentLocation["points"]) > 0 :
                label = str(turbulentLocation["address"]) + "(" + str(len(turbulentLocation["points"]))+ ")"
                
                numShownAddresses += 1

                allTurbulentLongitude += longitude
                allTurbulentLatitude += latitude

                points = ax1.plot(longitude, latitude, color="red", marker=".", ms=1, linestyle="none", label=label)                

        ax2 = fig.add_subplot(1, 2, 2)
        
        worldMap.boundary.plot(ax=ax2, edgecolor="black")
        
        ax2.set_xlim(GUI_CONSTANTS.DE_MIN_LONGITUDE, GUI_CONSTANTS.DE_MAX_LONGITUDE)
        ax2.set_ylim(GUI_CONSTANTS.DE_MIN_LATITUDE, GUI_CONSTANTS.DE_MAX_LATITUDE)
        ax2.set(aspect=1.78)

        sb.histplot(x=allTurbulentLongitude, y=allTurbulentLatitude, ax=ax2, kde=True, kde_kws={"bw_adjust":Plotter.KDE_BAND_WIDTH}, cmap=ListedColormap(["orange", "red", "maroon"]))

        # fig.legend(legendHandles, legendLabels, bbox_to_anchor=(0,0), loc="upper left", title="Addresses (number points)", ncol=3)
        plt.suptitle("Turbulence Areas (from " + str(numShownAddresses) + " addresses), mercator proj")
        plt.show()        
        return True
