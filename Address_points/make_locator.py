"""
Creates a locator
"""
import os
import arcpy
from arcgis.geometry import Geometry, Point
from arcgis.features import GeoAccessor, Table
from arcgis.gis import GIS
from datetime import datetime
from pandas.core.frame import DataFrame
from config import Config

def create_locator(addresses, roads, poi, parcels, locator_file):
    data_list = [ # layer, name in locator service
        [addresses, "PointAddress"],
        [parcels, "Parcel"],
        [poi, 'POI'],
        [roads, "StreetAddress"],
    ]
    
    address_field_map = [
        'PointAddress.HOUSE_NUMBER ' + addresses + '.addNum', 
#        'PointAddress.STREET_PREFIX_DIR ' + addresses + '.preDir', 
#        'PointAddress.STREET_PREFIX_TYPE ' + addresses + '.preMod', 
        'PointAddress.STREET_NAME ' + addresses + '.gcLgFlName',
#        'PointAddress.STREET_SUFFIX_TYPE ' + addresses + '.postMod', 
#        'PointAddress.STREET_SUFFIX_DIR ' + addresses + '.postDir', 
#        'PointAddress.SUB_ADDRESS_UNIT ' + addresses + '.unit', 
        'PointAddress.PARCEL_JOIN_ID ' + addresses + '.taxlotID', 
        'PointAddress.CITY ' + addresses + '.msagComm', 
        'PointAddress.POSTAL ' + addresses + '.zipCode', 
        #'PointAddress.DISPLAY_X long', 'PointAddress.DISPLAY_Y lat',
        # 'Address Join Id' could link to subunit addresses at the same location
    ]

    poi_field_map = [
        'POI.PLACE_NAME '  + poi + '.name', 
        'POI.CATEGORY '    + poi + '.category',
        'POI.SUBCATEGORY ' + poi + '.subcategory',
        'POI.CITY '        + poi + '.locale',
        # Use a Place Join ID field here to join to an alternative name table
    ]
    street_field_map = [
        'StreetAddress.LEFT_HOUSE_NUMBER_FROM ' + roads + '.FromLeft', 
        'StreetAddress.HOUSE_NUMBER_TO_LEFT ' + roads + '.ToLeft', 
        'StreetAddress.HOUSE_NUMBER_FROM_RIGHT ' + roads + '.FromRight', 
        'StreetAddress.HOUSE_NUMBER_TO_RIGHT ' + roads + '.ToRight', 
        'StreetAddress.STREET_NAME ' + roads + '.Street', 
        'StreetAddress.FULL_STREET_NAME ' + roads + '.StreetName',
    ]

    parcel_field_map = [
        'Parcel.PARCEL_NAME ' + parcels + '.MapTaxlot', 
        'Parcel.STREET_NAME ' + parcels + '.SITUS_ADDR',
        'Parcel.PARCEL_JOIN_ID ' + parcels + '.MapTaxlot',
    ]

    field_map = address_field_map + parcel_field_map + poi_field_map + street_field_map
    #field_map = address_field_map + parcel_field_map + poi_field_map

    msg = "Created locator \"%s\"." % locator_file
    if arcpy.Exists(locator_file):
        msg = "Overwrote locator \"%s\"." % locator_file

    rval = arcpy.geocoding.CreateLocator(country_code="USA", 
        primary_reference_data = data_list, 
        field_mapping = field_map,
        out_locator = locator_file, 
        language_code="ENG", 
        alternatename_tables = [], alternate_field_mapping = [], 
        custom_output_fields = [],
        precision_type="GLOBAL_HIGH")

    print(msg)

    return rval

if __name__ == "__main__":
    # To allow overwriting outputs change overwriteOutput option to True.
    arcpy.env.overwriteOutput = True

    #egdb = 'C:/Users/bwilson/AppData/Roaming/Esri/ArcGISPro/Favorites/Clatsop_WinAuth.sde'
    egdb = 'K:/webmaps/basemap/cc-gis.sde'
    assert os.path.exists(egdb)
    fgdb = "K:/e911/e911.gdb"
    assert os.path.exists(fgdb)

    datestamp = datetime.now().strftime("%Y%m%d_%H%M")
    suffix = '' # '_' + datestamp # for debug and development

    locator_file = "k:\\e911\\clatsop_county" + suffix

    with arcpy.EnvManager(workspace=fgdb):
        # These feature classes have to be in the Enterprise GDB
        # so that I can publish the locator in Portal
        # They are accessed read-only
        #
        # Wait, doesn't it always copy all the data into a table anyway??
        #
        addresses = "address_points"
        roads = "roads"
        poi = 'points_of_interest'
        parcels = 'taxlot_accounts'

        try:
            rval = create_locator(addresses, roads, poi, parcels, locator_file)
        except Exception as e:
            print("Failed on locator. \"%s\"" % e)
            rval = False
  
# That's all!
