from typing import NamedTuple

class ENGINE_CONSTANTS:
    PLOTS = ["occurrence", "bar_ivv", "filtered", "interval", "std", "location", "heat_map"]
    
class DB_CONSTANTS:
    VALID_DB_COLUMNS = ["id", "timestamp", "frame_hex_chars", "address", "downlink_format", "bds", "on_ground", "adsb_version", "altitude", "altitude_is_barometric", "nuc_p", "latitude", "longitude", "nuc_r", "true_track", "groundspeed", "vertical_rate", "gnss_height_diff_from_baro_alt", "identification",
                        "category", "bds17_common_usage_gicb_capability_report", "bds50_roll_angle", "bds50_true_track_angle", "bds50_ground_speed", "bds50_track_angle_rate", "bds50_true_airspeed", "bds60_magnetic_heading", "bds60_indicated_airspeed", "bds60_mach", "bds60_barometric_altitude_rate", "bds60_inertial_vertical_velocity"]

    USED_COLUMNS = ["identification", "address", "timestamp",
                     "latitude", "longitude",  "bar", "ivv"]

    HOSTNAME = "airdata.skysquitter.com"
    DATABASE_NAME = "db_airdata"
    USER_NAME = "tubs"
    PASSWORD = "ue73f5dn"

    CONNECTIONS_TOTAL = 0

    MAX_ROW_BEFORE_LONG_DURATION = 200000

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
