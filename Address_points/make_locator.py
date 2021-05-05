"""
Creates a locator
"""
import arcpy
from arcgis.geometry import Geometry, Point
from arcgis.features import GeoAccessor, Table
from arcgis.gis import GIS
from datetime import datetime
from pandas.core.frame import DataFrame
from config import Config

def create_locator(addresses, roads, poi, parcels, locator_file):
    data_list = [
        [addresses, "PointAddress"],
        [poi, 'POI'],
        [roads, "StreetAddress"],
        [parcels, "Parcel"]
    ]
    field_map = [
        "PointAddress.HOUSE_NUMBER " + addresses + ".addNum", 
#        "PointAddress.STREET_PREFIX_DIR " + addresses + ".preDir", 
#        "PointAddress.STREET_PREFIX_TYPE " + addresses + ".preMod", 
        "PointAddress.STREET_NAME " + addresses + ".gcLgFlName",
#        "PointAddress.STREET_SUFFIX_TYPE " + addresses + ".postMod", 
#        "PointAddress.STREET_SUFFIX_DIR " + addresses + ".postDir", 
#        "PointAddress.SUB_ADDRESS_UNIT " + addresses + ".unit", 
        "PointAddress.PARCEL_JOIN_ID " + addresses + ".taxlotID", 
        "PointAddress.CITY " + addresses + ".msagComm", 
        "PointAddress.POSTAL " + addresses + ".zipCode", 
        #"PointAddress.DISPLAY_X long", "PointAddress.DISPLAY_Y lat",
        # "Address Join Id" could link to subunit addresses at the same location

        "Parcel.PARCEL_NAME parcels.MapTaxlot", 
        #"Parcel.REGION parcels.STATE",
        #"Parcel.JoinID parcels.points_address_join"

        "POI.PLACE_NAME "  + poi + ".name", 
        "POI.CATEGORY "    + poi + ".category",
        "POI.SUBCATEGORY " + poi + ".subcategory",
        "POI.CITY "        + poi + ".locale",
        # Use a Place Join ID field here to join to an alternative name table
        
        "StreetAddress.HOUSE_NUMBER_FROM_LEFT " + roads + ".FromLeft", 
        "StreetAddress.HOUSE_NUMBER_TO_LEFT " + roads + ".ToLeft", 
        "StreetAddress.HOUSE_NUMBER_FROM_RIGHT " + roads + ".FromRight", 
        "StreetAddress.HOUSE_NUMBER_TO_RIGHT " + roads + ".ToRight", 
        "StreetAddress.STREET_NAME " + roads + ".Street", 
        "StreetAddress.FULL_STREET_NAME " + roads + ".StreetName",
    ]

    try:
        rval = arcpy.geocoding.CreateLocator(country_code="USA", 
            primary_reference_data = data_list, 
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
        # These feature classes have to be in the FGDB

    with arcpy.EnvManager(workspace=fgdb):
        addresses = "address_pts_wm_20210428_1453"
        roads = "roads"
        poi = 'places_20210504_1505'
        parcels = 'parcels'
        assert arcpy.Exists(addresses)
        assert arcpy.Exists(roads)
        assert arcpy.Exists(poi)
        create_locator(addresses, roads, poi, parcels, locator_file)
    
# That's all!
g