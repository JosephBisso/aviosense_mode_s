# Bachelor Thesis

[[_TOC_]]
# Task of this project

Quantitative analysis of MODE-S information on the possible turbulence assessment of commercial aircraft

# Idea

Processed data from many MODE-S receivers are available. These data comprise a large number of parameters in a high frequency. Using these data, statements on turbulence are to be made with the help of different approaches. Due to the very different aircraft characteristics, a normalized approach has to be used. In a first step, the approach ``1`` shall be implemented in the following

# Problems

- Turbulence are dynamic in spatial and temporal dimensions

- Lack of observation to understand the process

- The resolution of the turbulence model is larger than the range that applies to the effect of an aircraft

# Relevant work aspects of this project

- [ ] Automated procedure for data transfer and calculation of approach ``1``. Increasing the temporal and spatial scale of the example data set.

- [ ] Problem of the size of the database. So far, the data is stored in MySQL. 
Research on more efficient storage of data in other database formats.

- [ ] Problem of unevenly distributed timeseries ("unevenly distributed timeseries").  Research methods to ensure the quality of the analysis.

- [ ] Matching with weather data (Prefer "AMDAR" data - availability to be checked).

- [ ] Evaluation and integration of DILAB data after first measurement flights including the directly calculated "Eddy Dissipation Rate".
