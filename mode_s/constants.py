class ENGINE_CONSTANTS:
    PLOTS = ["occurrence", "bar_ivv", "filtered", "interval", "std", "location", "heat_map"]
    MAX_NUMBER_THREADS_ENGINE = 200
    
class DB_CONSTANTS:
    VALID_DB_COLUMNS = ["id", "timestamp", "frame_hex_chars", "address", "downlink_format", "bds", "on_ground", "adsb_version", "altitude", "altitude_is_barometric", "nuc_p", "latitude", "longitude", "nuc_r", "true_track", "groundspeed", "vertical_rate", "gnss_height_diff_from_baro_alt", "identification",
                        "category", "bds17_common_usage_gicb_capability_report", "bds50_roll_angle", "bds50_true_track_angle", "bds50_ground_speed", "bds50_track_angle_rate", "bds50_true_airspeed", "bds60_magnetic_heading", "bds60_indicated_airspeed", "bds60_mach", "bds60_barometric_altitude_rate", "bds60_inertial_vertical_velocity"]

    USED_COLUMNS = ["id", "identification", "address", "timestamp",
                    "bds", "altitude", "latitude", "longitude",  "bar", "ivv"]

    HOSTNAME = "airdata.skysquitter.com"
    DATABASE_NAME = "db_airdata"
    USER_NAME = "tubs"
    PASSWORD = "ue73f5dn"
    ROW_COUNT = 0

    CONNECTIONS_TOTAL = 0

    MAX_ROW_BEFORE_LONG_DURATION = 200000
    MIN_NUMBER_THREADS_LONG_DURATION = 25
    MAX_NUMBER_THREADS_LONG_DURATION = 40
    MIN_NUMBER_THREADS = 10

class GUI_CONSTANTS:
    DE_MIN_LATITUDE = 46
    DE_MAX_LATITUDE = 56
    DE_MIN_LONGITUDE = 4
    DE_MAX_LONGITUDE = 16
