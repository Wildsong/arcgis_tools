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

def create_locator(fgdb, locator_file):

    # These feature classes have to be in the FGDB
    address_points = "address_pts_wm_20210428_1453"
    roads = "roads"
    poi = 'points_of_interest'

    data = [
        [address_points, "PointAddress"],
        [poi, 'POI'],
        [roads, "StreetAddress"],
    ]
    field_map = [
        "PointAddress.HOUSE_NUMBER " + address_points + ".addNum", 
#        "PointAddress.STREET_PREFIX_DIR " + address_points + ".preDir", 
#        "PointAddress.STREET_PREFIX_TYPE " + address_points + ".preMod", 
        "PointAddress.STREET_NAME " + address_points + ".gcLgFlName",
#        "PointAddress.STREET_SUFFIX_TYPE " + address_points + ".postMod", 
#        "PointAddress.STREET_SUFFIX_DIR " + address_points + ".postDir", 
#        "PointAddress.SUB_ADDRESS_UNIT " + address_points + ".unit", 
        "PointAddress.PARCEL_JOIN_ID " + address_points + ".taxlotID", 
        "PointAddress.CITY " + address_points + ".msagComm", 
        "PointAddress.POSTAL " + address_points + ".zipCode", 
        #"PointAddress.DISPLAY_X long", "PointAddress.DISPLAY_Y lat",

        "POI.PLACE_NAME points_of_interest.Name", 
        "POI.CATEGORY points_of_interest.Type",
        
        "StreetAddress.HOUSE_NUMBER_FROM_LEFT " + roads + ".FromLeft", 
        "StreetAddress.HOUSE_NUMBER_TO_LEFT " + roads + ".ToLeft", 
        "StreetAddress.HOUSE_NUMBER_FROM_RIGHT " + roads + ".FromRight", 
        "StreetAddress.HOUSE_NUMBER_TO_RIGHT " + roads + ".ToRight", 
        "StreetAddress.STREET_NAME " + roads + ".Street", 
        "StreetAddress.FULL_STREET_NAME " + roads + ".StreetName",
    ]

    with arcpy.EnvManager(workspace = fgdb):
        try:
            rval = arcpy.geocoding.CreateLocator(country_code="USA", 
                primary_reference_data = data, 
                field_mapping = field_map,
                out_locator = locator_file, 
                language_code="ENG", 
                alternatename_tables = [], alternate_field_mapping = [], 
                custom_output_fields = [],
                precision_type="LOCAL_EXTRA_HIGH")
            print("Wrote locator called \"%s\"." % locator_file)
            rval = True
        except Exception as e:
            print("Fail. \"%s\"" % e)
            rval = False

    return rval

if __name__ == "__main__":
    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True
    egdb = 'C:/Users/bwilson/AppData/Roaming/Esri/ArcGISPro/Favorites/Clatsop_WinAuth.sde'
    fgdb = "K:/e911/e911.gdb"
    datestamp = datetime.now().strftime("%Y%m%d_%H%M")

    locator_file = "k:\\e911\\clatsop_county_" + datestamp
    create_locator(fgdb, locator_file)
    
# That's all!
