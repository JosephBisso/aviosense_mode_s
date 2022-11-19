# Bachelor Thesis

[[_TOC_]]
# Presentation of the project
## Task of this project

Quantitative analysis of MODE-S information on the possible turbulence assessment of commercial aircraft

## Idea

Processed data from many MODE-S receivers are available. These data comprise a large number of parameters in a high frequency. Using these data, statements on turbulence are to be made with the help of different approaches. Due to the very different aircraft characteristics, a normalized approach has to be used. In a first step, the approach ``1`` shall be implemented in the following

## Problems

- Turbulence are dynamic in spatial and temporal dimensions

- Lack of observation to understand the process

- The resolution of the turbulence model is larger than the range that applies to the effect of an aircraft

## Relevant work aspects of this project

- [x] Automated procedure for data transfer and calculation of approach ``1``. Increasing the temporal and spatial scale of the example data set.

- [x] Problem of the size of the database. So far, the data is stored in MySQL. 
Research on more efficient storage of data in other database formats.

- [ ] Problem of unevenly distributed time series ("unevenly distributed time series").  Research methods to ensure the quality of the analysis.

- [ ] Matching with weather data (Prefer "AMDAR" data - availability to be checked).

- [ ] Evaluation and integration of DILAB data after first measurement flights including the directly calculated "Eddy Dissipation Rate".

# Installation

## Get the code

Get the source code with the following commands. First you will need [**git**](https://git-scm.com/download/win), [**python**](https://www.python.org/downloads/release/python-377/) and [**pip**](https://pip.pypa.io/en/stable/installation/) install to your pc:

```powershell
git clone https://git.rz.tu-bs.de/j.bisso-bi-ela/ba_mode-s_analysis.git
cd ba_mode-s_analysis

# Install the Dependencies and setup the app
pip install -r .\requirements.txt
pip install .
```
## Dependencies

Following packaged are required to run the development version of the app. They are **automatically installed** during the previous installations processes:

- PySide6==6.3.0
- numpy==1.21.6
- matplotlib==3.5.2
- scipy==1.7.3

# Usage

## General usage
Run the app using the `run.ps1` script

```powershell
$ .\run.ps1 -h
usage: mode_s.py [-h] [-t] [-it] [-v] [-d] [--local] [-la latitude_minimal]
                 [-LA LATITUDE_MAXIMAL] [-lo longitude_minimal]
                 [-LO LONGITUDE_MAXIMAL] [-bd BDS] [-id id_minimal]
                 [-ID ID_MAXIMAL] [-l LIMIT] [-dl DURATION_LIMIT]
                 [-n MEDIAN_N] [-p [PLOTS [PLOTS ...]]]
                 [-pa [PLOT_ADDRESSES [PLOT_ADDRESSES ...]]]

Framework for automatic Mode-S data tranfer and turbulence prediction.

optional arguments:
  -h, --help            show this help message and exit
  -t, --terminal        Whether the app should run only on the terminal
  -it, --interactive    Whether the app should run interactively on the
                        terminal
  -v, --verbose         Whether the app should run only on the terminal
  -d, --debug           Whether the app should run only on debug mode
  --local               Whether the app should should connect to local
                        database
  -la latitude_minimal, --latitude-minimal latitude_minimal
                        The desired minimal latitude. If not set, all
                        available latitudes are evaluated
  -LA LATITUDE_MAXIMAL, --latitude-maximal LATITUDE_MAXIMAL
                        The desired maximal latitude. If not set, all
                        available latitudes are evaluated
  -lo longitude_minimal, --longitude-minimal longitude_minimal
                        The desired minimal longitude. If not set, all
                        available longitudes are evaluated
  -LO LONGITUDE_MAXIMAL, --longitude-maximal LONGITUDE_MAXIMAL
                        The desired maximal longitude. If not set, all
                        available longitudes are evaluated
  -bd BDS, --bds BDS    The desired bds. If not set, all available bds are
                        evaluated
  -id id_minimal, --id-minimal id_minimal
                        The desired minimal id. If not set, all available ids
                        are evaluated
  -ID ID_MAXIMAL, --id-maximal ID_MAXIMAL
                        The desired maximal id. If not set, all available ids
                        are evaluated
  -l LIMIT, --limit LIMIT
                        The desired limit for the mysql commmands. (default =
                        50000)
  -dl DURATION_LIMIT, --duration-limit DURATION_LIMIT
                        The desired flight duration limit in seconds for the
                        analysis. (default = None)
  -n MEDIAN_N, --median-n MEDIAN_N
                        The desired n for the median filtering. MUST BE ODD.
                        (default: n=3)
  -p [PLOTS [PLOTS ...]], --plots [PLOTS [PLOTS ...]]
                        The desired plots. POSSIBLE VALUES: ['occurrence',
                        'bar_ivv', 'filtered', 'interval', 'std']
  -pa [PLOT_ADDRESSES [PLOT_ADDRESSES ...]], --plot-addresses [PLOT_ADDRESSES [PLOT_ADDRESSES ...]]
                        The addresses of the desired plots.
```

## Example Usage

In the following example, we run the app in terminal mode and pass some relevant arguments, such as `-l 2000000` for the query limit, `-p filtered std` for the plots we want the app to do, and `-n 3` for the kernel size of the median filter.

```powershell
$ .\run.ps1 -t --local -l 2000000 -p filtered std -n 3
Starting the app...
INFO    :: 1:0:24 :: Framework for automatic Mode-S data tranfer and turbulence prediction.
SUCCESS :: 1:0:24 :: Database accessible
INFO    :: 1:0:30 :: Row Count for table tbl_mode_s: 7160557
LOG     :: 1:0:30 :: 1 threads for attributes ['timestamp']
SUCCESS :: 1:0:36 :: Query successfully executed. Attributes were: ['timestamp']
INFO    :: 1:0:36 :: Lattest database db_airdata update: Tue Jul 6 14:08:06 2021
LOG     :: 1:0:36 :: Engine plot status : {'occurrence': False, 'bar_ivv': False, 'filtered': True, 'interval': False, 'std': True}
LOG     :: 1:0:36 :: Setting global query row limit to: 2000000
LOG     :: 1:0:36 :: Setting query filter to:
LOG     :: 1:0:36 :: 1 threads for attributes ['identification', 'address']
LOG     :: 1:0:36 :: 5 threads for attributes ['id', 'address', 'timestamp', 'bds', 'altitude', 'latitude', 'longitude']
LOG     :: 1:0:36 :: 5 threads for attributes ['id', 'address', 'timestamp', 'bds', 'altitude', 'bar', 'ivv']
WARNING :: 1:1:9 :: Query executed. Results lower than expected (2078 < 2000000). Attributes were: ['identification', 'address']
WARNING :: 1:1:9 :: Skipping following addresses: [4661099] :: Already added or invalid identification
INFO    :: 1:1:9 :: Known Addresses: 2077
SUCCESS :: 1:3:44 :: Query successfully executed. Attributes were: ['id', 'address', 'timestamp', 'bds', 'altitude', 'bar', 'ivv']
SUCCESS :: 1:3:47 :: Query successfully executed. Attributes were: ['id', 'address', 'timestamp', 'bds', 'altitude', 'latitude', 'longitude']
INFO    :: 1:3:47 :: Data actualized. Size: 2000000
LOG     :: 1:3:49 :: Plotting for following addresses: [4502584, 4966467, 4223733, 5262923]
LOG     :: 1:3:52 :: Filtering data with n set to: 3
INFO    :: 1:3:53 :: Plotting filtered data and standard deviations
SUCCESS :: 1:5:46 :: Successfully plotted
App existed normally.
```

The result of the previous command look as follow:

![MODE-S___FILTERED___STD_-_BAR___IVV](/uploads/8d5610ab5f2326f9e2fad86674cb4a6a/MODE-S___FILTERED___STD_-_BAR___IVV_2_.png)
