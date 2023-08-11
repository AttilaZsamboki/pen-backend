from .utils.logs import log
from .utils.minicrm import dijbekero

def pen_dijbekero():
    log("Díjbekérők feltöltése", "INFO", script_name="pen_dijbekero")
    try:
        dijbekero()
        log("Díjbekérők feltöltése sikeres",
            "SUCCESS", script_name="pen_dijbekero")
    except KeyError as e:
        log("Nincsenek számlázási adatok", "FAILED",
            script_name="pen_dijbekero", details=e)
    except Exception as e:
        log("Hiba akadt a díjbekérő feltöltésében", "ERROR",
            script_name="pen_dijbekero", details=e)

