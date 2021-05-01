"""
This script cleans and copies GNIS data into feature classes.

Output will be 
* points of interest for Clatsop County

I am assuming that we don't want a separate hosted data layer for this, 
that we'll read data directly from SQL because I think we'll want to 
edit it!

That also means I only need to project it into FIPS 3601.
"""
import arcpy
from arcgis.features import GeoAccessor
from arcgis.features.geo._io.fileops import _sanitize_column_names
import pandas as pd
from datetime import datetime
from pandas.core.frame import DataFrame
from numpy import logical_not

def set_aliases(fc, d):
    """ Use the dictionary to set aliases for each field. """
    for (field, alias) in d.items():
        arcpy.management.AlterField(in_table=fc, field=field, new_field_alias=alias)
    return


def process_cc_poi(feature_class, datestamp, output_location):
    # For some reason the CC poi data was stored in Web Mercator.
    sdf = GeoAccessor.from_featureclass(feature_class)
    
    print(sdf.head(5))
    print("Rows:", len(sdf))
    print("Columns: ", sdf.columns)
    print("Types:", sdf.dtypes)

    # Clean!

    # Columns that we're keeping
    # There are a bunch ignored including COUNTY STATE COUNTRY
    # and specialize ones that probably only matter to GeoComm like rSrcId
    # There are two GlobalId fields, huh. That's annoying. I keep only 1.

    sdf = sdf[['SHAPE', 
        'Name',
        'Type', 
        "Type2",
        'Creator',
        'Created',
        "Editor",
        "Last_Edit",
        "Alias",
        ]]

    # Rename
    sdf.rename(columns={
        'Type' : 'Category',
        'Type2' : 'Subcategory',
    })

    # Create aliases
    # The original column names are left untouched,
    # but I assign more readable aliases here.
    # NB some of these names are chosen to match up with the Esri point_address locator.
    # NB It turns out assigning some them in the locator makes the locator results icky.
    d_aliases = { 
    }

    print("We have %d points." % len(sdf))
    print(sdf.head(5))
    print(sdf.columns)
    print(sdf.dtypes)

    wm_fc = output_location + '/' + 'poi_wm_' + datestamp
    sdf.spatial.to_featureclass(wm_fc, sanitize_columns=False)
    set_aliases(wm_fc, d_aliases)
    print("Wrote %d points to \"%s\"." % (len(sdf), wm_fc))

    local_fc = output_location + '/poi_local_' + datestamp
    sref = """PROJCS['NAD_1983_HARN_StatePlane_Oregon_North_FIPS_3601_Feet_Intl',GEOGCS['GCS_North_American_1983_HARN',DATUM['D_North_American_1983_HARN',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',8202099.737532808],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-120.5],PARAMETER['Standard_Parallel_1',44.33333333333334],PARAMETER['Standard_Parallel_2',46.0],PARAMETER['Latitude_Of_Origin',43.66666666666666],UNIT['Foot',0.3048]]", transform_method=["NAD_1983_HARN_To_WGS_1984_2"], in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"""
    print("Reprojecting to \"%s\"." % local_fc)
    #https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/project.htm
    arcpy.management.Project(wm_fc, local_fc,
        out_coor_system=sref, 
        #transform_method='NAD_1983_HARN_To_WGS_1984_2'
    )
    set_aliases(local_fc, d_aliases)

    return local_fc


def process_gnis_points(feature_class, datestamp, output_location):
    # State GNIS data arrives in OGIC projection

    # Filter on Clatsop County
    or_df = GeoAccessor.from_featureclass(feature_class)
    sdf = or_df[or_df.COUNTY_NAME == "Clatsop"]

    #https://pro.arcgis.com/en/pro-app/latest/arcpy/classes/spatialreference.htm
    #sref = arcpy.SpatialReference()
    #rval = sref.loadFromString('EPSG:2913')
    
    pd.set_option('display.max_columns', None)

    print(sdf.head(5))
    print("Rows:", len(sdf))
    print("Columns: ", sdf.columns)
    print("Types:", sdf.dtypes)

    # Clean!

    # Change float64 columns to strings, removing the stupid ".0" endings.
    #sdf[['DATE_EDITED']] = sdf[['DATE_EDITED']].astype("datetime64[ns]")
    sdf[['FEATURE_ID']]  = sdf[['FEATURE_ID']].astype("int64")

    # Columns that we're keeping
    # There are a bunch ignored including COUNTY STATE COUNTRY
    # and specialize ones that probably only matter to GeoComm like rSrcId
    # There are two GlobalId fields, huh. That's annoying. I keep only 1.

    sdf = sdf[['SHAPE', 
        'FEATURE_ID',    # a long int
        'FEATURE_NAME',  # 
        "FEATURE_CLASS", # Make the domain from this
        'ELEV_IN_FT',
        'MAP_NAME',      # Quad?? "Warrenton", "Tillamook Head"...
        "DATE_CREATED",
        "DATE_EDITED",
        "Elevation_Source", # "GNIS", "LIDAR DEM", "10m DEM", ...
        ]]

    # Rename some fields
    sdf.rename(columns={
        'FEATURE_CLASS' : 'Category',
        'DATE_CREATED' : 'Created',
        'DATE_EDITED' : 'Last_Edit',
    })

    # Add some fields and set defaults on them.
    sdf.loc[:, 'Creator'] = 'GNIS'
    sdf.loc[:, 'Editor'] = ''

    # Create aliases
    # The original column names are left untouched,
    # but I assign more readable aliases here.
    # NB some of these names are chosen to match up with the Esri point_address locator.
    # NB It turns out assigning some them in the locator makes the locator results icky.
    d_aliases = { 
        'FEATURE_ID' : 'ID', 
        'FEATURE_NAME': "Name",
        'FEATURE_CLASS' : 'Category',
        'ELEV_IN_FT' : 'Elevation', 
        'MAP_NAME': 'Quad Name',
        'Elevation_Source': 'Elevation Source'
    }

    print("We have %d points." % len(sdf))
    print(sdf.head(5))
    print(sdf.columns)
    print(sdf.dtypes)

    fc = output_location + '/' + 'gnis_ogic_' + datestamp
    sdf.spatial.to_featureclass(fc, sanitize_columns=False)
    set_aliases(fc, d_aliases)
    print("Wrote %d points to \"%s\"." % (len(sdf), fc))

    # Reproject web mercator points to local.

    local_fc = output_location + '/' + 'gnis_local_' + datestamp

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
    arcpy.management.Project(fc, local_fc,
        out_coor_system=sref, 
        #transform_method='NAD_1983_HARN_To_WGS_1984_2'
    )
    set_aliases(local_fc, d_aliases)

    return local_fc

# ----------------------------------------------------------------------------------------------
if __name__ == '__main__':

    fgdb = "K:/e911/e911.gdb"
    datestamp = datetime.now().strftime("%Y%m%d_%H%M")

    # Input data
    cc_points = fgdb + "/" + "points_of_interest"
    assert arcpy.Exists(cc_points)

    gnis_points = "K:/State Data/GNIS_2014/GNIS_OR.gdb/GNIS_OR.gdb/GNIS_OR_Buffer"
    assert arcpy.Exists(gnis_points)

    pd.set_option('display.max_columns', None)

    poi_fc = process_cc_poi(cc_points, datestamp, fgdb)
    gnis_fc = process_gnis_points(gnis_points, datestamp, fgdb)

    # Cat them together

    df1 = GeoAccessor.from_featureclass(poi_fc)
    df2 = GeoAccessor.from_featureclass(gnis_fc)

    fc = fgdb + '/' + 'points_combined_' + datestamp
    df  = pd.concat(df1, df2)
    # FIXME -- Add a locality, quad or city or something, to make for better Locator results
    df.to_featureclass(fc, sanitize_columns = False)

    print("..and we're done!")

# That's all!
