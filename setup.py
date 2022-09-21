import shutil
import os
import sys
from setuptools import setup

current_path = os.getcwd()
not_installed = ''

# PySide2 [5.15.2]
try:
    import PySide2
    print('PySide2 is found')
    
    mysql_path = shutil.which("mysql")
    if not mysql_path:  
        print ('MySql must be installed and added to PATH')
    else:
        try:    
            from PySide2 import QtSql as qtsql
            qtsql_path = qtsql.__file__
            qtsql_path.replace("\\", "\\") # a\d -> a\\d
            qtpath = os.path.dirname(qtsql_path)
            qtsqldrivers_path = os.path.join(qtpath, "plugins", "sqldrivers")

            if not os.path.exists(os.path.join(qtsqldrivers_path, "qsqlmysql.dll")):
                shutil.copyfile(os.path.join(current_path, "lib", "qsqlmysql.dll"), qtsqldrivers_path)
                shutil.copyfile(os.path.join(current_path, "lib", "qsqlmysqld.dll"), qtsqldrivers_path)
        except:
            print("Error while preparing sqldrivers")

except:
    print('Error : PySide2 must be installed!')
    not_installed = 'PySide2 '

# Numpy [1.21.6]
try:
    import numpy
    print('numpy is found')
except:
    print('Error : numpy must be installed!')
    not_installed = not_installed + 'numpy '

# matplotlib [3.5.2]
try:
    import matplotlib
    print('matplotlib is found')
except:
    print('Error : matplotlib must be installed!')
    not_installed = not_installed + 'matplotlib '

# scipy [1.7.3]
try:
    import scipy
    print('scipy is found')
except:
    print('Error : scipy must be installed!')
    not_installed = not_installed + 'scipy '

# sklearn
try:
    import sklearn
    print('sklearn is found')
except:
    print('Error : sklearn must be installed!')
    not_installed = not_installed + 'sklearn '

# seaborn
try:
    import seaborn
    print('seaborn is found')
except:
    print('Error : seaborn must be installed!')
    not_installed = not_installed + 'seaborn '

if not_installed != '':
    print('########################')
    print('####### WARNING ########')
    print('########################')
    print('Some dependencies are not installed .It causes some problems for mode-s analysis! : \n')
    print(not_installed + '\n\n')
    print('Read this link for more information: \n')
    print('https://git.rz.tu-bs.de/j.bisso-bi-ela/ba_mode-s_analysis/-/blob/main/README.md\n\n')
    sys.exit(1)


DESCRIPTION = 'Quantitative analysis of MODE-S information on the possible turbulence assessment of commercial aircraft'

setup (
    name='mode-s_analysis',
    version='1.0.0',
    license='GPL3',
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    include_package_data=True,
    url='https://git.rz.tu-bs.de/j.bisso-bi-ela/ba_mode-s_analysis',
    author='Joseph Loic Bisso-Bi-Ela',
    author_email='j.bisso-bi-ela@tu-braunschweig.de',
    maintainer='Joseph Loic Bisso-Bi-Ela',
    maintainer_email='j.bisso-bi-ela@tu-braunschweig.de',
    packages=[
        'mode_s', 'mode_s.gui',
        'mode_s.analysis', 'mode_s.gui.qml',
    ]
)
