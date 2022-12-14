import sys
import json
import concurrent.futures
from collections import namedtuple
from typing import Any, Dict, NamedTuple, List, Union

import mode_s.engine as ModeSEngine
from mode_s.constants import *
from mode_s.database import Database, DatabaseError
from mode_s.logger import Logger
import mode_s.process as process

from PySide2.QtCore import *


class Mode_S(QObject):
    
    logged              = Signal(str, arguments=['log'])
    progressed          = Signal(str, str, arguments=['id', 'msg'])

    dbFilterUpdated     = Signal()
    engineFilterUpdated = Signal()
    computingStarted    = Signal()
    computingFinished   = Signal()

    readyToPlot         = Signal()
    identificationMapped= Signal()
    plotOccurrenceReady = Signal()
    plotRawReady        = Signal()
    plotFilteredReady   = Signal()
    plotIntervalReady   = Signal()
    plotStdReady        = Signal()
    plotExceedsReady    = Signal()
    plotLocationReady   = Signal()
    plotTurbulentReady  = Signal()
    plotHeatMapReady    = Signal()
    allMapPlotsReady    = Signal()
    plotKDEExceedsReady = Signal()

    executor: concurrent.futures.ThreadPoolExecutor = None
    pExecutor: concurrent.futures.ProcessPoolExecutor = None
    backgroundFutures: List[concurrent.futures.Future] = []
    
    __occurrenceSeries        = []
    __identMap                = {}
    __rawSeries               = []
    __intervalSeries          = []
    __filteredSeries          = []
    __stdSeries               = []
    __exceedsSeries           = []
    __kdeExceedsSeries        = {}
    __locationSeries          = []
    __turbulentLocationSeries = []
    __heatMapSeries           = []
    
    __addressRawSeries        = []
    __addressIntervalSeries   = []
    __addressFilteredSeries   = []
    __addressStdSeries        = []
    __addressExceedsSeries    = []

    __zoneKdeExceedsSeries    = {}
    
    __partialLocationSeries   = []
    __partialTurbulentSeries  = []
    __partialHeatMapSeries    = []
    
    allAddressSeriesMap       = {}
    allPlotSeriesMap          = {}
    allMapPlotSeriesMap       = {}
    


    def __init__(self, db: Database, msEngine: ModeSEngine.Engine, logger: Logger):
        super(Mode_S, self).__init__(None)
        self.db = db
        self.engine = msEngine
        self.logger = logger
        logger.logged.connect(self.__log)
        logger.progressed.connect(self.__progress)
        self.dbFilterUpdated.connect(self.actualizeDB)
        self.engineFilterUpdated.connect(self.compute)
        self.readyToPlot.connect(self.plot)
        self.executor = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="modeS_workerThread", max_workers=10)

        self.plot(fromDump=True)

    def setProcessExecutor(self, ex: concurrent.futures.ProcessPoolExecutor):
        self.pExecutor = ex

    @Slot()
    def printFullLogPath(self):
        self.logger.printLogFullPath()
        
    @Slot(str, result=None)
    def updateDBFilter(self, dbJson: str): 
        self.computingStarted.emit()
        data: Dict[str, str] = self.__checkParam(dbJson)
        
        future = self.executor.submit(self.__setDbParameters, data)
        future.add_done_callback(self.__backgroundThreadFinished)
        self.backgroundFutures.append(future)
    
    def __setDbParameters(self, data):
        self.db.setDatabaseParameters(**data)
        self.dbFilterUpdated.emit()

    @Slot(str, result=None)
    def updateEngineFilter(self, engineJson: str): 
        self.computingStarted.emit()
        data: Dict[str, str] = self.__checkParam(engineJson)
                                
        self.engine.setEngineParameters(**data)
        self.engineFilterUpdated.emit()

    @Slot(str)
    def updateLoginData(self, loginJson: str): 
        data: Dict[str, str] = self.__checkParam(loginJson)
                                
        if not self.db.setLogin(**data):
            self.logger.critical("Cannot connect to Database with following login data:", data)

    @Slot(str)
    def updateDBColumnsName(self, columnsNameJson: str): 
        data: Dict[str, str] = self.__checkParam(columnsNameJson)
                                
        self.db.setValidDBColumnsNames(**data)
    
    @Slot()
    def actualizeDB(self):
        future = self.executor.submit(self.__actualizeDB)
        future.add_done_callback(self.__computingFinished)
        
    @Slot()
    def compute(self):
        future = self.executor.submit(self.__prepareEngine)
        future.add_done_callback(self.__backgroundThreadFinished)

    @Slot()
    def startDatabase(self):
        future = self.executor.submit(self.db.start)
        future.add_done_callback(self.__backgroundThreadFinished)

    @Slot()
    def plot(self, **params): 
        future = self.executor.submit(self.__plotting, **params)
        future.add_done_callback(self.__computingFinished)

    @Slot()
    def cancel(self): 
        self.db.cancel()
        self.engine.cancel()
        self.executor.shutdown(wait=False)
        self.executor = concurrent.futures.ThreadPoolExecutor(thread_name_prefix="modeS_workerThread")
        self.computingFinished.emit()

    @Slot(str)
    def prepareAddress(self, address): 
        future = self.executor.submit(self.__updateAddressPlots, address)
        future.add_done_callback(self.__backgroundThreadFinished)

    @Slot(str)
    def prepareKDEZone(self, zoneID): 
        future = self.executor.submit(self.__updateKDEZonePlots, zoneID)
        future.add_done_callback(self.__backgroundThreadFinished)

    @Slot(str, int, int, result=int)
    def preparePartialSeries(self, locationType, counter, maxLength): 
        ms = MODE_S_CONSTANTS
        endSlice = 0
        partialList = []
        stop = False
        progressID = LOGGER_CONSTANTS.LOCATION
        setter = self.__setPartialLocationSeries
        try:
            series = []
            actualSegmentLength = 0
            
            if locationType in [ms.LOCATION_SERIES, ms.TURBULENCE_SERIES]:
                if locationType == ms.TURBULENCE_SERIES:
                    progressID = LOGGER_CONSTANTS.TURBULENT
                    setter = self.__setPartialTurbulentSeries
                    
                series = self.allMapPlotSeriesMap[locationType]
                if len(series) == 0:
                    raise AssertionError(f"Skipping Loading of {locationType} Series because it is empty.")

                actualSegmentLength = len(series[counter]["segments"])
                endSlice = counter + 1
                
                while(endSlice < len(series) and actualSegmentLength + len(series[endSlice]["segments"]) < maxLength):
                    actualSegmentLength += len(series[endSlice]["segments"])
                    endSlice += 1
                    
                partialList = series[counter:endSlice]
                
            elif locationType == "kde":
                progressID = LOGGER_CONSTANTS.KDE
                setter = self.__setPartialHeatMapSeries
                series = self.allMapPlotSeriesMap[ms.HEATMAP_SERIES]
                if len(series) == 0:
                    raise AssertionError(f"Skipping {locationType} Series because it is empty.")

                actualSegmentLength = maxLength
                endSlice = counter + maxLength
                
                partialList = series[counter:endSlice]

            else:
                raise AssertionError (f"Cannot prepare Partial Series for unknown location type {locationType}")

            self.logger.progress(progressID, f"Loading {locationType} Data [{counter}/{len(series) - 1}]")
            self.logger.debug(f"Loading {actualSegmentLength} {locationType} elements")
            
            stop = endSlice >= len(series) - 1

        except AssertionError as ae:
            self.logger.warning(str(ae))
            stop = True
            
        except Exception as ecx:
            type, value, traceback = sys.exc_info()
            self.logger.warning(
                f"Error Occurred: Mode_s prepare partial series for type {locationType}::\n" + str(type) + "::" + str(value))
            self.logger.warning("Error raised at Frame:", traceback.tb_frame)

            stop = True
            
        finally:
            if stop:
                self.logger.progress(progressID, LOGGER_CONSTANTS.END_PROGRESS_BAR)
                endSlice = -1
            else:
                setter(partialList)
                
            return endSlice
            
        
    @Slot(str)
    def __log(self, log: str):
        self.logged.emit(log)

    @Slot(str, str)
    def __progress(self, id: str, msg: str):
        self.progressed.emit(id, msg)
        
    def __checkParam(self, strJson):
        data: Dict[str, str] = json.loads(strJson)

        for key in data:
            if data[key].isdigit():
                data[key] = int(data[key])
            else:
                try:
                    data[key] = float(data[key])
                except ValueError:
                    if data[key].lower() == "none" or data[key].lower() == "all" or data[key].lower() == "auto":
                        data[key] = None                    

        return data

    def __computingFinished(self, future: concurrent.futures.Future):
        future.result()
        self.computingFinished.emit()

    def __backgroundThreadFinished(self, future: concurrent.futures.Future):
        future.result()

    def __prepareEngine(self):
        self.waitUntilReady()
        self.engine.setDataSet(self.db.getData())
        self.readyToPlot.emit()

        
    def __actualizeDB(self):
        self.db.actualizeData()

    def waitUntilReady(self) -> bool:
        concurrent.futures.wait(self.backgroundFutures)
        return True

    def __plotting(self, **params):
        try: 
            self.logger.progress(LOGGER_CONSTANTS.MODE_S, "Sending data [0/2]")
            if params.get("fromDump"):
                results = self.engine.loadDump()
            else:
                results = self.engine.compute(usePlotter=False)

            self.__occurrenceSeries = next(results)

            computedAddresses = next(results)
            self.__identMap = computedAddresses if params.get("fromDump") else self.db.getMapping(computedAddresses)
            self.identificationMapped.emit()
            self.allAddressSeriesMap = {str(address): {} for address in computedAddresses}
            self.logger.progress(LOGGER_CONSTANTS.MODE_S, "Sending data [1/2]")

            self.plotOccurrenceReady.emit()
            self.logger.progress(LOGGER_CONSTANTS.MODE_S, LOGGER_CONSTANTS.END_PROGRESS_BAR)

            self.__rawSeries = next(results)
            self.__intervalSeries = next(results)
            self.__filteredSeries = next(results)
            self.__stdSeries = next(results)
            self.__exceedsSeries = next(results)
            self.__updateAllPlotSeriesMap()

            self.logger.progress(LOGGER_CONSTANTS.PLOT, "Getting all Addresses series Map")
            allAddressSeriesMap__future = self.pExecutor.submit(process.getAllAddressSeriesMap, self.allPlotSeriesMap, 
                self.allAddressSeriesMap,[
                    MODE_S_CONSTANTS.BAR_IVV_SERIES, MODE_S_CONSTANTS.INTERVAL_SERIES, 
                    MODE_S_CONSTANTS.FILTERED_SERIES,MODE_S_CONSTANTS.STD_SERIES, MODE_S_CONSTANTS.EXCEEDS_SERIES
                ]
            )
            allAddressSeriesMap__future.add_done_callback(self.__updateAllAddressSeriesMap)
            self.backgroundFutures.append(allAddressSeriesMap__future)

            self.__locationSeries = next(results)
            self.__turbulentLocationSeries = next(results)
            self.__heatMapSeries = next(results)
            self.__updateAllLocationSeriesMap()
            
            self.__kdeExceedsSeries = next(results)
            
            self.logger.success("Done plotting")
            
            while next(results, None) is not None:
                pass
            
            if params.get("fromDump") is None:
                self.__dumpAll()

        except ModeSEngine.EngineError as err:
            self.logger.warning("Engine Error Occurred: Mode_s plotting::", str(err))
        except Exception as esc:
            type, value, traceback = sys.exc_info()
            self.logger.critical(
                "Error Occurred: Mode_s plotting::\n" + str(type) + "::" + str(value))
            self.logger.critical("Error raised at Frame:", traceback.tb_frame)
        finally:
            self.logger.progress(LOGGER_CONSTANTS.MODE_S, LOGGER_CONSTANTS.END_PROGRESS_BAR)

    def __updateAllAddressSeriesMap(self, future: concurrent.futures.Future, displayAddress = None):
        allAddressSeriesMap = {}
        try:
            allAddressSeriesMap = future.result()
            self.logger.debug("Length of allAddressSeriesMap: ", len(allAddressSeriesMap))
        except Exception as esc:
            type, value, traceback = sys.exc_info()
            self.logger.critical(
                "Error Occurred while updating all addresses series map:: \n" + str(type) + "::" + str(value))
        else:
            self.allAddressSeriesMap = allAddressSeriesMap
            if displayAddress:
                self.__updateAddressPlots(displayAddress)
        finally:
            self.logger.progress(LOGGER_CONSTANTS.PLOT, LOGGER_CONSTANTS.END_PROGRESS_BAR)
            

    def __updateAddressPlots(self, address):
        self.waitUntilReady()
        if self.allAddressSeriesMap.get(address) is None:
            self.logger.warning(f"Cannot update address {address}. Cannot find it")
            return
        try:
            self.logger.progress(LOGGER_CONSTANTS.PLOT, f"Preparing address {address} [0/5]")
            self.__setAddressRaw(self.allAddressSeriesMap[address][MODE_S_CONSTANTS.BAR_IVV_SERIES])

            self.logger.progress(LOGGER_CONSTANTS.PLOT, f"Preparing address {address} [1/5]")
            self.__setAddressFiltered(self.allAddressSeriesMap[address][MODE_S_CONSTANTS.FILTERED_SERIES])

            self.logger.progress(LOGGER_CONSTANTS.PLOT, f"Preparing address {address} [2/5]")
            self.__setAddressInterval(self.allAddressSeriesMap[address][MODE_S_CONSTANTS.INTERVAL_SERIES])

            self.logger.progress(LOGGER_CONSTANTS.PLOT, f"Preparing address {address} [3/5]")
            self.__setAddressStd(self.allAddressSeriesMap[address][MODE_S_CONSTANTS.STD_SERIES])
            
            self.logger.progress(LOGGER_CONSTANTS.PLOT, f"Preparing address {address} [4/5]")
            self.__setAddressExceeds(self.allAddressSeriesMap[address][MODE_S_CONSTANTS.EXCEEDS_SERIES])
        except KeyError as ke:
            self.logger.warning("Error while updating address plots::", str(ke))
        finally:
            self.logger.progress(LOGGER_CONSTANTS.PLOT, LOGGER_CONSTANTS.END_PROGRESS_BAR)

    def __updateKDEZonePlots(self, zoneID):
        if self.__kdeExceedsSeries.get(zoneID) is None:
            self.logger.warning(f"Cannot update kde zone {zoneID}. Cannot find it")
            return
        self.logger.progress(LOGGER_CONSTANTS.KDE_EXCEED, f"Preparing kdeZone {zoneID}")
        self.__setZoneKdeExceedsSeries(self.__kdeExceedsSeries[zoneID])
        self.logger.progress(LOGGER_CONSTANTS.KDE_EXCEED, LOGGER_CONSTANTS.END_PROGRESS_BAR)
        
    def __dumpAll(self):

        ms = MODE_S_CONSTANTS
        
        toDump = [self.__occurrenceSeries, self.__identMap, self.__rawSeries, self.__intervalSeries,
                  self.__filteredSeries, self.__stdSeries, self.__exceedsSeries, self.__locationSeries, self.__turbulentLocationSeries, self.__heatMapSeries, self.__kdeExceedsSeries]
        toDumpName = [ms.OCCURRENCE_DUMP, ms.INDENT_MAPPING, ms.BAR_IVV_DUMP, ms.INTERVAL_DUMP,
                        ms.FILTERED_DUMP, ms.STD_DUMP, ms.EXCEEDS_DUMP, ms.LOCATION_DUMP, ms.TURBULENCE_DUMP, ms.HEATMAP_DUMP, ms.KDE_EXCEEDS_DUMP]
        for index in range(len(toDump)):
            self.logger.progress(LOGGER_CONSTANTS.MODE_S, f"Saving series [{index}/{len(toDump)}]")
            if not toDump[index]:
                continue
            self.__dumpData(toDump[index], toDumpName[index])
        
        if self.db.data:
            self.logger.progress(LOGGER_CONSTANTS.MODE_S, "Saving database")
            self.__dumpData(self.db.data, ms.DATABASE_DUMP)
            self.db.data.clear() 
        if self.engine.data:
            self.logger.progress(LOGGER_CONSTANTS.MODE_S, "Clearing engine data")
            self.engine.data.clear() 
        

    def __dumpData(self, data: List[Any], name: str):
        self.logger.debug("Dumping and freeing memory for", name)
        with open(name, "w") as dumpF:
            json.dump(data, dumpF, indent = 2, default=lambda coord: {"longitude":coord.longitude() ,"latitude": coord.latitude()})
    
    def __updateAllPlotSeriesMap(self):
        self.allPlotSeriesMap = {
            MODE_S_CONSTANTS.STD_SERIES:        self.__stdSeries,
            MODE_S_CONSTANTS.EXCEEDS_SERIES:    self.__exceedsSeries,
            MODE_S_CONSTANTS.BAR_IVV_SERIES:    self.__rawSeries,
            MODE_S_CONSTANTS.INTERVAL_SERIES:   self.__intervalSeries,
            MODE_S_CONSTANTS.FILTERED_SERIES:   self.__filteredSeries,
        }
        
    def __updateAllLocationSeriesMap(self):
        self.allMapPlotSeriesMap = {
            MODE_S_CONSTANTS.LOCATION_SERIES:       self.__locationSeries,
            MODE_S_CONSTANTS.TURBULENCE_SERIES:     self.__turbulentLocationSeries,
            MODE_S_CONSTANTS.HEATMAP_SERIES:        self.__heatMapSeries
        }
        self.allMapPlotsReady.emit()
        
    def __identMapping(self):
        return self.__identMap
    def __occurrence(self):
        return self.__occurrenceSeries
    def __raw(self):
        return self.__addressRawSeries
    def __filtered(self):
        return self.__addressFilteredSeries
    def __interval(self):
        return self.__addressIntervalSeries
    def __std(self):
        return self.__addressStdSeries
    def __exceeds(self):
        return self.__addressExceedsSeries
    def __location(self):
        return self.__partialLocationSeries
    def __turbulentLocation(self):
        return self.__partialTurbulentSeries
    def __heatMap(self):
        return self.__partialHeatMapSeries
    def __kdeExceeds(self):
        return self.__zoneKdeExceedsSeries
    
    def __setAddressRaw(self, addressData):
        self.__addressRawSeries = addressData
        self.plotRawReady.emit()
    def __setAddressFiltered(self, addressData):
        self.__addressFilteredSeries = addressData
        self.plotFilteredReady.emit()
    def __setAddressInterval(self, addressData):
        self.__addressIntervalSeries = addressData
        self.plotIntervalReady.emit()
    def __setAddressStd(self, addressData):
        self.__addressStdSeries = addressData
        self.plotStdReady.emit()
    def __setAddressExceeds(self, addressData):
        self.__addressExceedsSeries = addressData
        self.plotExceedsReady.emit()

    def __setZoneKdeExceedsSeries(self, zoneData):
        self.__zoneKdeExceedsSeries = zoneData
        self.plotKDEExceedsReady.emit()

    def __setPartialLocationSeries(self, locationData):
        self.__partialLocationSeries = locationData
        self.plotLocationReady.emit()
    def __setPartialTurbulentSeries(self, locationData):
        self.__partialTurbulentSeries = locationData
        self.plotTurbulentReady.emit()
    def __setPartialHeatMapSeries(self, heatMapData):
        self.__partialHeatMapSeries = heatMapData
        self.plotHeatMapReady.emit()
        
    
    identMap                = Property("QVariantMap" , __identMapping,       notify = identificationMapped)
    occurrenceSeries        = Property("QVariantList", __occurrence,         notify = plotOccurrenceReady)
    addressRawSeries        = Property("QVariantMap" , __raw,                notify = plotRawReady)
    addressStdSeries        = Property("QVariantMap" , __std,                notify = plotStdReady)
    addressExceedSeries     = Property("QVariantMap" , __exceeds,            notify = plotExceedsReady)
    addressFilteredSeries   = Property("QVariantMap" , __filtered,           notify = plotFilteredReady)
    addressIntervalSeries   = Property("QVariantMap" , __interval,           notify = plotIntervalReady)
    partialLocationSeries   = Property("QVariantList", __location,           notify = plotLocationReady)
    partialTurbulentSeries  = Property("QVariantList", __turbulentLocation,  notify = plotTurbulentReady)
    partialHeatMapSeries    = Property("QVariantList", __heatMap,            notify = plotHeatMapReady)
    zoneKdeExceedSeries     = Property("QVariantMap" , __kdeExceeds,         notify = plotKDEExceedsReady)
