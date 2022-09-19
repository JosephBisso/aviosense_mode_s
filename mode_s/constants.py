from typing import NamedTuple, List
import os

class ENGINE_CONSTANTS:
    PLOTS = ["occurrence", "bar_ivv", "filtered", "interval", "std", "location", "heat_map"]
    MAX_NUMBER_THREADS_ENGINE: int = 20
    KDE_BANDWIDTH = 0.5
    MEDIAN_N = 1
    
class DB_CONSTANTS:
    VALID_DB_COLUMNS = ["id", "timestamp", "frame_hex_chars", "address", "downlink_format", "bds", "on_ground", "adsb_version", "altitude", "altitude_is_barometric", "nuc_p", "latitude", "longitude", "nuc_r", "true_track", "groundspeed", "vertical_rate", "gnss_height_diff_from_baro_alt", "identification",
                        "category", "bds17_common_usage_gicb_capability_report", "bds50_roll_angle", "bds50_true_track_angle", "bds50_ground_speed", "bds50_track_angle_rate", "bds50_true_airspeed", "bds60_magnetic_heading", "bds60_indicated_airspeed", "bds60_mach", "bds60_barometric_altitude_rate", "bds60_inertial_vertical_velocity"]

    USED_COLUMNS = ["identification", "address", "timestamp",
                     "latitude", "longitude",  "bar", "ivv"]

    # HOSTNAME = "airdata.skysquitter.com"
    # DATABASE_NAME = "db_airdata"
    # USER_NAME = "tubs"
    # PASSWORD = "ue73f5dn"

    HOSTNAME = None
    DATABASE_NAME = "local_mode_s"
    USER_NAME = "root"
    PASSWORD = "BisbiDb2022?"

    CONNECTIONS_TOTAL = 0

    MAX_ROW_BEFORE_LONG_DURATION = 250000
    PREFERRED_NUMBER_THREADS = 4
    MAX_NUMBER_THREADS = 6
    MIN_NUMBER_THREADS = 2
    
    
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
