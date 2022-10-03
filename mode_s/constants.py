from typing import NamedTuple, List
import os

class ENGINE_CONSTANTS:
    PLOTS = ["occurrence", "bar_ivv", "filtered", "interval", "std", "location", "heat_map"]
    MAX_NUMBER_THREADS_ENGINE: int = 20
    KDE_BANDWIDTH = 0.5
    MEDIAN_N = 1
    
class DB_CONSTANTS:
    VALID_DB_COLUMNS = ["id", "timestamp", "address", "bds", "altitude", "latitude", "longitude", "ground_speed", "identification",
                        "category", "roll_angle", "true_track_angle", "track_angle_rate", "true_airspeed", "magnetic_heading", "indicated_airspeed", "mach", "barometric_altitude_rate", "inertial_vertical_velocity"]

    USED_COLUMNS = ["identification", "address", "timestamp",
                     "latitude", "longitude",  "bar", "ivv"]

    # Old
    # HOSTNAME = "airdata.skysquitter.com"
    # DATABASE_NAME = "db_airdata"
    # USER_NAME = "tubs"
    # PASSWORD = "ue73f5dn"
    # TABLE_NAME = "tbl_mode_s"

    # New
    HOSTNAME = "tubs.skysquitter.com"
    DATABASE_NAME = "db_airdata"
    USER_NAME = "tubs"
    PASSWORD = "DILAB-2022"
    TABLE_NAME = "tbl_tubs"

    # For Local Use Only
    # HOSTNAME = None
    # DATABASE_NAME = "local_mode_s"
    # USER_NAME = "root"
    # PASSWORD = "BisbiDb2022?"
    # TABLE_NAME = "tbl_mode_s"

    CONNECTIONS_TOTAL = 0

    MAX_ROW_BEFORE_LONG_DURATION = 200000
    PREFERRED_NUMBER_THREADS = 20
    MAX_NUMBER_THREADS = 40
    MIN_NUMBER_THREADS = 10
    
    NO_IDENTIFICATION = "Unknown"
    EMPTY_FILTER = "WHERE"
    
class MODE_S_CONSTANTS:
    APP_DATA_PATH: str = os.path.join(os.path.expanduser("~"), ".mode_s")
    if not os.path.exists(APP_DATA_PATH):
        os.mkdir(APP_DATA_PATH)
    
    APP_DUMP_PATH: str = os.path.join(APP_DATA_PATH, "dump")
    if not os.path.exists(APP_DUMP_PATH):
        os.mkdir(APP_DUMP_PATH)

    STD_SERIES: str           = "std"
    EXCEEDS_SERIES: str       = "exceeds"
    HEATMAP_SERIES: str       = "heatmap"
    BAR_IVV_SERIES: str       = "bar_ivv"
    INTERVAL_SERIES: str      = "interval"
    FILTERED_SERIES: str      = "filtered"
    LOCATION_SERIES: str      = "location"
    TURBULENCE_SERIES: str    = "turbulence"
    OCCURRENCE_SERIES: str    = "occurrence"
    KDE_EXCEEDS_SERIES: str   = "kde_exceeds"
    ALL_SERIES: List[str] = [STD_SERIES, EXCEEDS_SERIES, HEATMAP_SERIES, BAR_IVV_SERIES, INTERVAL_SERIES,
                             FILTERED_SERIES, LOCATION_SERIES, TURBULENCE_SERIES, OCCURRENCE_SERIES, KDE_EXCEEDS_SERIES]

    STD_DUMP: str           = os.path.join(APP_DUMP_PATH, "std.dump.json")
    EXCEEDS_DUMP: str       = os.path.join(APP_DUMP_PATH, "exceeds.dump.json")
    HEATMAP_DUMP: str       = os.path.join(APP_DUMP_PATH, "heatmap.dump.json")
    BAR_IVV_DUMP: str       = os.path.join(APP_DUMP_PATH, "bar_ivv.dump.json")
    INTERVAL_DUMP: str      = os.path.join(APP_DUMP_PATH, "interval.dump.json")
    FILTERED_DUMP: str      = os.path.join(APP_DUMP_PATH, "filtered.dump.json")
    LOCATION_DUMP: str      = os.path.join(APP_DUMP_PATH, "location.dump.json")
    DATABASE_DUMP: str      = os.path.join(APP_DUMP_PATH, "database.dump.json")
    INDENT_MAPPING: str     = os.path.join(APP_DUMP_PATH, "addresses.dump.json")
    TURBULENCE_DUMP: str    = os.path.join(APP_DUMP_PATH, "turbulence.dump.json")
    OCCURRENCE_DUMP: str    = os.path.join(APP_DUMP_PATH, "occurrence.dump.json")
    KDE_EXCEEDS_DUMP: str   = os.path.join(APP_DUMP_PATH, "kde_exceeds.dump.json")


class LOGGER_CONSTANTS:
    ENGINE:str              = "ID_EGN"
    MODE_S:str              = "ID_MDS"
    DATABASE:str            = "ID_DTB"
    PLOT:str                = "ID_PLT"
    KDE_EXCEED:str          = "ID_KDX"
    LOCATION: str           = "ID_LOC"
    TURBULENT: str          = "ID_TRB"
    KDE: str                = "ID_KDE"
    PROGRESS_BAR:str        = "[==>]"
    END_PROGRESS_BAR:str    = "[==|]"

class GUI_CONSTANTS:
    DE_MIN_LATITUDE = 46
    DE_MAX_LATITUDE = 56
    DE_MIN_LONGITUDE = 4
    DE_MAX_LONGITUDE = 16


class DATA(NamedTuple):
    time: float  # in Seconds
    bar: float
    ivv: float


class WINDOW_POINT(NamedTuple):
    window: float
    point: float

class WINDOW_DATA(NamedTuple):
    window: float
    bar: float
    ivv: float


class LOCATION_DATA(NamedTuple):
    time: float
    longitude: float
    latitude: float
