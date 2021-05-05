"""
Publish services to Portal and EGDB

Currently this just creates a locator but does no publishing!
"""
import arcpy
from arcgis.geometry import Geometry, Point
from arcgis.features import GeoAccessor, Table
from arcgis.gis import GIS
from datetime import datetime
from pandas.core.frame import DataFrame
from config import Config


def publish_service():
    gis = GIS(url=Config.PORTAL_URL, 
        username=Config.PORTAL_USER, password=Config.PORTAL_PASSWORD, 
        #token=access_token # token takes precedence over username/password
    )
    print(gis)

    content = gis.content.search("Change", item_type="Feature Layer")
    print(content)

def import_database():
  
    return

if __name__ == "__main__":
    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True
    egdb = 'C:/Users/bwilson/AppData/Roaming/Esri/ArcGISPro/Favorites/Clatsop_WinAuth.sde'
    fgdb = "K:/e911/e911.gdb"
    datestamp = datetime.now().strftime("%Y%m%d_%H%M")
    
# That's all!
