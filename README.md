# Aviosense MODE_S
Quantitative analysis of MODE-S information on the possible turbulence assessment of commercial aircraft <br><br>
[![GitHub release](https://img.shields.io/github/v/release/Josephbisso/aviosense_mode_s.svg)](https://github.com/JosephBisso/aviosense_mode_s/releases) 
## Description

Processed data from many MODE-S receivers are available. These data comprise a large number of parameters in a high frequency. Using these data, statements on turbulence are to be made with the help of different approaches. Due to the very different aircraft characteristics, a normalized approach has to be used.

**Aviosense MODE_S** aims to make statements on turbulence using available data from MODE-S receiversn thanks a automated procedure for data transfer and calculation of the given approach while increasing the temporal and spatial scale of the data set used for the calculation 

<div align="center">
  <img src="https://github.com/JosephBisso/aviosense_mode_s/blob/develop/.github/readme/main%20view.png" width="600">
  <img src="https://github.com/JosephBisso/aviosense_mode_s/blob/develop/.github/readme/map%20view.png"  width="500">
  <img src="https://github.com/JosephBisso/aviosense_mode_s/blob/develop/.github/readme/raw%20view.png" width="500">
  <img src="https://github.com/JosephBisso/aviosense_mode_s/blob/develop/.github/readme/kde%20view.png" width="500">
</div>

## First steps
### Prerequisite
#### Python
**Aviosense MODE_S** is a python project. To run the app you must have [**Python 3.7.7**](https://www.python.org/downloads/) installed. Newer version of Python have not been tested. You could also simply download the standalone [**mode_s binaries**]().

### Dependencies
The list of all dependencies can be found in ``.\requirements.txt``. Those will be automatically installed during the setup. See [**setup**](#install)

## Install
### From Binaries
Download the [**mode_s binaries**]() and unzip it. Easy

### From Source
#### Manually
To install **Aviosense MODE_S** via the source follow the following step (or copy [**the commands below**](#Commands))
  1. Clone the repo locally
  2. Enter the cloned repo
  3. Start powershell
  4. Run the ``setup.ps1`` script

#### Commands
Copy the command below in the CMD with **admin rigths**:

```cmd
git clone https://github.com/JosephBisso/aviosense_mode_s.git aviosense_mode_s
cd aviosense_mode_s
powershell -NoProfile -ExecutionPolicy Bypass -Command ".\setup.ps1"
```

**Note:** The ``setup.ps1`` script will install all the requirements inside ``.\requirements`` and copy the sqldrivers stored ``.\lib`` into the sqldrivers path of the PySide2 python package *(Recommanded)*. If you don't want this, you could run instead (in powershell):

```powershell
.\setup.ps1 --venv
```

A virtual python environment will be automatically created. All packages and the sql drivers will be udpated there.

## Run the app
### From Binaries
Start the app with a double click. Should be easy

### From Source
Run the app in **powershell** using the ``run.ps1`` script:
- The **default mode** is the [**GUI Mode**](https://github.com/JosephBisso/aviosense_mode_s/blob/develop/.github/readme/map%20view.png)
- The log file of the app can be found in ``src/mode_s.log``
- To run the app in loop, run with the parameter ``--loop``
- You can see all other parameter by looking into the helper with the following command:

```powershell
.\run.ps1 -h
```
 <details><summary><b> MODE-S Helper </b></summary>
 
```
usage: main.py [-h] [-t] [-it] [-v] [-d] [--local] [-la latitude_minimal]
               [-LA LATITUDE_MAXIMAL] [-lo longitude_minimal]
               [-LO LONGITUDE_MAXIMAL] [-bd BDS] [-id id_minimal]
               [-ID ID_MAXIMAL] [-l LIMIT] [-dl DURATION_LIMIT] [-n MEDIAN_N]
               [-p [PLOTS [PLOTS ...]]]
               [-pa [PLOT_ADDRESSES [PLOT_ADDRESSES ...]]] [--plot-all]

Framework for automatic Mode-S data transfer and turbulence prediction.

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
                        The desired limit for the mysql commands. (default =
                        500000)
  -dl DURATION_LIMIT, --duration-limit DURATION_LIMIT
                        The desired flight duration limit in minutes for the
                        analysis. (default = 10)
  -n MEDIAN_N, --median-n MEDIAN_N
                        The desired n for the median filtering. MUST BE ODD.
                        (default: n=3)
  -p [PLOTS [PLOTS ...]], --plots [PLOTS [PLOTS ...]]
                        The desired plots. POSSIBLE VALUES: ['occurrence',
                        'bar_ivv', 'filtered', 'interval', 'std', 'location',
                        'heat_map']
  -pa [PLOT_ADDRESSES [PLOT_ADDRESSES ...]], --plot-addresses [PLOT_ADDRESSES [PLOT_ADDRESSES ...]]
                        The addresses of the desired plots.
  --plot-all            Plot all addresses for the desired plots.
```

</details>

## Use the App

## Build the binairies from Source

If needed, you can build the binary from Source. You can use the `build.ps1` script or whatever tool you want.<br>
You would need to install **pyinstaller** if you want to use the `build.ps1` script. Install it with the following command:

```cmd
pip install pyinstaller
```

## Bugs and issues


