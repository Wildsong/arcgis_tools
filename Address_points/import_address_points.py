"""
Yesterday I had to work with a table and convert it to a point layer, 
today we got new data from GeoComm and it's a shapefile. This project
gets easier and easier.

All this script is doing right now is
copying e911 data into feature classes

Input is a shapefile.

Output will be
1. a feature class in local projection in the EGDB
2. a hosted feature layer in Delta. 
"""
import os
import sys
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

egdb = 'C:/Users/bwilson/AppData/Roaming/Esri/ArcGISPro/Favorites/Clatsop_WinAuth.sde'
fgdb = "K:/e911/e911.gdb"
datestamp = datetime.now().strftime("%Y%m%d_%H%M")
ssap = "K:/e911/From_Geosolve/2021-04-23/ssap.shp"


def write_fc(df, pathname):
    print("Writing %d points to \"%s\"." % (len(df), pathname))
    df.spatial.to_featureclass(pathname, sanitize_columns=False)

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

# ----------------------------------------------------------------------------------------------

if __name__ == '__main__':

    # NOTE, SSAP data arrives in Web Mercator.
    sdf = GeoAccessor.from_featureclass(ssap)

    #https://pro.arcgis.com/en/pro-app/latest/arcpy/classes/spatialreference.htm
    #sref = arcpy.SpatialReference()
    #rval = sref.loadFromString('EPSG:2913')
    
    print(len(sdf))
    print(sdf.columns)
    print(sdf.dtypes)

    # Clean!

    # Change float64 columns to strings, removing the stupid ".0" endings.
    df1 = sdf.apply(fixid, axis=1)

    # Columns that we're keeping
    # There are a bunch ignored including COUNTY STATE COUNTRY
    # and specialize ones that probably only matter to GeoComm like rSrcId
    # There are two GlobalId fields, huh. That's annoying. I keep only 1.

    df1 = df1[['SHAPE', 
        'srcFullAdr', # "1234 1/2 SOUTHWEST VISTA DEL MAR DRIVE"
        'gcLgFlAdr',  # "197 N MARION AVE" -- shortened with abbreviations

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

    d_aliases = { 
        'srcFullAdr': 'Full Address Long',
        'gcLgFlAdr':  'Full Address',
        'addNum': 'Address Number',
        'addNumSuf': 'Address Number Suffix',
        'preMod': 'Pre modifier',
        'preDir': 'Pre directional',
        'preType': 'Pre type',
        'preTypeSep': 'Pretype Separator',
        'strName': 'Street Name',
        'postType': 'Post type',
        'postDir': 'Post directional',
        'postMod': 'Post modifier',
        'unit': 'Unit',
        'unitDesc': 'Unit descriptor',
        'unitNo': 'Unit number',
        'incMuni': 'Municipal area',
        'msagComm': 'MSAG community',
        'postComm': 'Postal community',
        'zipCode': 'Zip Code', 
        'long': 'Longitude',
        'lat': 'Latitude',
        'srcLastEdt': 'Edit Date',
        'EditDate': 'Upload Date',
        'gcConfiden': 'Confidence',
        'GlobalID_2': 'GUID',
        'taxlotID': 'Taxlot ID'
    }

    print("We have %d points." % len(df1))
    print(df1.head(5))
    print(df1.columns)
    print(df1.dtypes)

    try:
        wm_fc = fgdb + '/address_pts_wm_' + datestamp
        write_fc(df1, wm_fc)
        set_aliases(wm_fc, d_aliases)
    except Exception as e:
        print("Write to %s failed, " % wm_fc, e)
        rval = False

    # Reproject web mercator points to local.

    local_fc = fgdb + '/address_pts_local_' + datestamp

    # This gets published internally to the EGDB
    # THIS DOES NOT WORK -- it spins forever
    # if you remove the transform it works but generates bad data
#    local_df = df1.copy()
#    rval = local_df.spatial.project(2913, 'NAD_1983_HARN_To_WGS_1984_2')
#    print("LOCAL", df1.spatial.sr, local_df.spatial.sr, rval)
#    write_fc(local_df, local_fc)

    # I got this from a Model export
    # Using a transform string just seems to cause the process to lock up
    # and this sref string apparently includes the transform.
    sref = """PROJCS['NAD_1983_HARN_StatePlane_Oregon_North_FIPS_3601_Feet_Intl',GEOGCS['GCS_North_American_1983_HARN',DATUM['D_North_American_1983_HARN',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',8202099.737532808],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-120.5],PARAMETER['Standard_Parallel_1',44.33333333333334],PARAMETER['Standard_Parallel_2',46.0],PARAMETER['Latitude_Of_Origin',43.66666666666666],UNIT['Foot',0.3048]]", transform_method=["NAD_1983_HARN_To_WGS_1984_2"], in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"""
    print("Reprojecting to \"%s\"." % local_fc)
    try:
        #https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/project.htm
        arcpy.management.Project(wm_fc, local_fc,
            out_coor_system=sref, 
            #transform_method='NAD_1983_HARN_To_WGS_1984_2'
        )
        set_aliases(local_fc, d_aliases)
    except Exception as e:
        print("Write to %s failed, " % local_fc, e)
        rval = False

    print("..and we're done!")
# That's all!

