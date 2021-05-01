"""
This script cleans and copies e911 data into feature classes.

Output will be 
* address points
* hydrants

For each service, generate
1. a feature class in local projection in the EGDB
2. a hosted feature layer in Delta. 
"""
import arcpy
from arcgis.geometry import Geometry, Point
from arcgis.features import GeoAccessor, Table
from arcgis.features.geo._io.fileops import _sanitize_column_names
from arcgis.gis import GIS
from arcpy.server import GetLayoutTemplatesInfo
import pandas as pd
from datetime import datetime
from pandas.core.frame import DataFrame
from numpy import logical_not


def fixid(row):
    """ The DF has float64 dtypes for some columns
    forcing them to show "123.0" instead of "123". Fix that here. """

    for field in ['addNum', 'zipCode']:
        try:
            row[field] = "%d" % int(row[field])
        except ValueError:
            # usually this is because input is NaN
            row[field] = None
    return row


def set_aliases(fc, d):
    """ Use the dictionary to set aliases for each field. """
    for (field, alias) in d.items():
        arcpy.management.AlterField(in_table=fc, field=field, new_field_alias=alias)
    return


def process_address_points(feature_class, datestamp, output_location):
    # NOTE, Geocomm data arrives in Web Mercator.
    sdf = GeoAccessor.from_featureclass(feature_class)

    #https://pro.arcgis.com/en/pro-app/latest/arcpy/classes/spatialreference.htm
    #sref = arcpy.SpatialReference()
    #rval = sref.loadFromString('EPSG:2913')
    
    print(len(sdf))
    print(sdf.columns)
    print(sdf.dtypes)

    # Clean!

    # Change float64 columns to strings, removing the stupid ".0" endings.
    sdf.loc[:, 'addNum'].astype("int64")
    sdf.loc[:, 'zipCode'].astype("int64")

    # Columns that we're keeping
    # There are a bunch ignored including COUNTY STATE COUNTRY
    # and specialize ones that probably only matter to GeoComm like rSrcId
    # There are two GlobalId fields, huh. That's annoying. I keep only 1.

    sdf = sdf[['SHAPE', 
        'srcFullAdr', # "1234 1/2 SOUTHWEST VISTA DEL MAR DRIVE"
        'gcLgFlAdr',  # "197 N MARION AVE" -- shortened with abbreviations

        'gcLgFlName', # "N MARION AVE"
        'gcFullName', # "NORTH MARION AVENUE"

        #'addNumPre', # At least this year, this field is empty.
        'addNum', 'addNumSuf', # "1020 1/2" or "1020 A" -- addNum is always an integer
        'preMod', # "ALTERNATE" or "OLD" or "VISTA"
        'preDir', # spelled out like SOUTHWEST
        'preType', # 'HIGHWAY'
        'preTypeSep', # "DEL"
        'strName', # "30" as in "ALTERNATE HIGHWAY 30"
        'postType', # "DRIVE"
        'postDir', # "SOUTH"
        'postMod', # "BUSINESS"
        # 'building', 'floor', 'room', 'seat', # These are EMPTY so far
        # 'location', 'landmark', 'placeType', # ALL EMPTY
        'unit', 'unitDesc', 'unitNo', # "UNIT 208|APT 5", "UNIT|SUITE|APARTMENT", "208"
        'incMuni', # City name or "UNINCORPORATED"
        'msagComm', # City or locality such as 'ASTORIA' or 'BIRKENFELD' or 'WESTPORT'
        'postComm', # The post office, for example BIRKENFELD and WESTPORT go to CLATSKANIE
        #'unincComm', 'nbrhdComm', # ALL EMPTY
        'zipCode', 
        # 'zipCode4', # ALL EMPTY
        # 'esn', # THIS IS INFORMATION FOR DISPATCH I DID NOT INCLUDE
        # 'elev', # EMPTY
        # 'milepost', # is EMPTY
        'long', 'lat', 
        'srcLastEdt',
        'EditDate', # I think this corresponds to GeoComm update date
        'gcConfiden', # Confidence, 1 = good 
        'GlobalID_2', 'taxlotID' # GlobalId is null for a few entries so I use "_2"
        ]]

    # Create aliases
    # The original column names are left untouched,
    # but I assign more readable aliases here.
    # NB some of these names are chosen to match up with the Esri point_address locator.
    # NB It turns out assigning some them in the locator makes the locator results icky.

    d_aliases = { 
        'srcFullAdr': 'Full Address Long',
        'gcLgFlAdr':  'Full Address',

        'gcLgFlName': 'Street Name',     
        'gcFullName': 'Full Street Name',

        'addNum': 'House Number',
        'addNumSuf': 'Address Number Suffix',
        'preMod': 'Prefix Modifier',
        'preDir': 'Prefix Direction',
        'preType': 'Prefix type',
        'preTypeSep': 'Prefix Type Separator',
        'strName': 'Street',
        'postType': 'Postfix Type',
        'postDir': 'Postfix Direction',
        'postMod': 'Postfix Modifier',
        'unit': 'Unit',
        'unitDesc': 'Unit Description',
        'unitNo': 'Unit Number',
        'incMuni': 'City',
        'msagComm': 'MSAG Community',
        'postComm': 'Postal Community',
        'zipCode': 'ZIP', 
     
        'long': 'Longitude',
        'lat': 'Latitude',
     
        'srcLastEdt': 'Edit Date',
        'EditDate': 'Upload Date',
     
        'gcConfiden': 'Confidence',
     
        'GlobalID_2': 'GUID',
        'taxlotID': 'Taxlot ID'
    }

    print("We have %d points." % len(sdf))
    print(sdf.head(5))
    print(sdf.columns)
    print(sdf.dtypes)

    wm_fc = output_location + '/address_pts_wm_' + datestamp
    sdf.spatial.to_featureclass(wm_fc, sanitize_columns=False)
    set_aliases(wm_fc, d_aliases)
    print("Wrote %d points to \"%s\"." % (len(sdf), wm_fc))

    # Reproject web mercator points to local.

    local_fc = output_location + '/address_pts_local_' + datestamp

    # THIS METHOD DOES NOT WORK -- it spins forever
    # if you remove the transform it works but generates bad data
#    local_df = sdf.copy()
#    rval = local_df.spatial.project(2913, 'NAD_1983_HARN_To_WGS_1984_2')
#    print("LOCAL", sdf.spatial.sr, local_df.spatial.sr, rval)
#    write_fc(local_df, local_fc)
    # I got this from a Model export
    # Using a transform string just seems to cause the process to lock up
    # and this sref string apparently includes the transform.
    sref = """PROJCS['NAD_1983_HARN_StatePlane_Oregon_North_FIPS_3601_Feet_Intl',GEOGCS['GCS_North_American_1983_HARN',DATUM['D_North_American_1983_HARN',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',8202099.737532808],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-120.5],PARAMETER['Standard_Parallel_1',44.33333333333334],PARAMETER['Standard_Parallel_2',46.0],PARAMETER['Latitude_Of_Origin',43.66666666666666],UNIT['Foot',0.3048]]", transform_method=["NAD_1983_HARN_To_WGS_1984_2"], in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"""
    print("Reprojecting to \"%s\"." % local_fc)
    #https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/project.htm
    arcpy.management.Project(wm_fc, local_fc,
        out_coor_system=sref, 
        #transform_method='NAD_1983_HARN_To_WGS_1984_2'
    )
    set_aliases(local_fc, d_aliases)


def process_hydrants(feature_class, datestamp, output_location):
    # NOTE, Geocomm data arrives in Web Mercator.
    sdf = GeoAccessor.from_featureclass(feature_class)

    #https://pro.arcgis.com/en/pro-app/latest/arcpy/classes/spatialreference.htm
    #sref = arcpy.SpatialReference()
    #rval = sref.loadFromString('EPSG:2913')
    
    print(len(sdf))
    print(sdf.columns)
    print(sdf.dtypes)

    # Clean!

    # Change float64 columns to strings, removing the stupid ".0" endings.
    sdf = sdf
    #sdf = sdf.apply(fixid, axis=1)

    # Columns that we're keeping
    # There are a bunch ignored including COUNTY STATE COUNTRY
    sdf = sdf[['SHAPE', 
        'HYDRANTID',
        'STREET_INT', # "NW CORNER"
        'LOC_DESC',   # 'BIG CREEK HATCHERY'
        'ADDRESS',    # '93011 LABECK RD'
        'AUTHORITY',  # "CITY OF ASTORIA PUBLIC WORKS"
        'COMMUNITY',  # 'ASTORIA'
        'Source',     # 'BURNSIDE WATER ASSN HYDRANTS.DOC'
        ]]

    # Create aliases
    # The original column names are left untouched,
    # but I assign more readable aliases here.

    d_aliases = { 
        'HYDRANTID': 'Hydrant ID',
        'STREET_INT': 'Intersection',
        'LOC_DESC': 'Description',
        'ADDRESS': 'Address',
        'AUTHORITY': 'Authority',
        'COMMUNITY': 'Community',
    }

    print("We have %d points." % len(sdf))
    print(sdf.head(5))
    print(sdf.columns)
    print(sdf.dtypes)

    wm_fc = output_location + '/hydrants_wm_' + datestamp
    sdf.spatial.to_featureclass(wm_fc, sanitize_columns=False)
    set_aliases(wm_fc, d_aliases)
    print("Wrote %d points to \"%s\"." % (len(sdf), wm_fc))

    # Reproject web mercator points to local.

    local_fc = output_location + '/hydrants_local_' + datestamp

    # THIS METHOD DOES NOT WORK -- it spins forever
    # if you remove the transform it works but generates bad data
#    local_df = sdf.copy()
#    rval = local_df.spatial.project(2913, 'NAD_1983_HARN_To_WGS_1984_2')
#    print("LOCAL", sdf.spatial.sr, local_df.spatial.sr, rval)
#    write_fc(local_df, local_fc)
    # I got this from a Model export
    # Using a transform string just seems to cause the process to lock up
    # and this sref string apparently includes the transform.
    sref = """PROJCS['NAD_1983_HARN_StatePlane_Oregon_North_FIPS_3601_Feet_Intl',GEOGCS['GCS_North_American_1983_HARN',DATUM['D_North_American_1983_HARN',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',8202099.737532808],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-120.5],PARAMETER['Standard_Parallel_1',44.33333333333334],PARAMETER['Standard_Parallel_2',46.0],PARAMETER['Latitude_Of_Origin',43.66666666666666],UNIT['Foot',0.3048]]", transform_method=["NAD_1983_HARN_To_WGS_1984_2"], in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"""
    print("Reprojecting to \"%s\"." % local_fc)
    #https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/project.htm
    arcpy.management.Project(wm_fc, local_fc,
        out_coor_system=sref, 
        #transform_method='NAD_1983_HARN_To_WGS_1984_2'
    )
    set_aliases(local_fc, d_aliases)


def publish():
    # Publish to EGDB
    egdb = 'C:/Users/bwilson/AppData/Roaming/Esri/ArcGISPro/Favorites/Clatsop_WinAuth.sde'
    rval = arcpy.conversion.FeatureClassToFeatureClass(in_features=wm_fc, out_path=egdb, out_name="address_points")[0]
    # Publish as hosted feature layer
    # Overwrite existing?
    # or 

# ----------------------------------------------------------------------------------------------
if __name__ == '__main__':

    fgdb = "K:/e911/e911.gdb"
    datestamp = datetime.now().strftime("%Y%m%d_%H%M")

    # Input data
    geocomm_address_points = "K:/e911/From_Geosolve/2021-04-23/ssap.shp"
    geocomm_hydrants = "K:/e911/From_Geosolve/2020-07/Clatsop_Mapdata.gdb/Basemap/HYDRANT"

    process_address_points(geocomm_address_points, datestamp, fgdb)
    process_hydrants(geocomm_hydrants, datestamp, fgdb)
    print("..and we're done!")

# That's all!
