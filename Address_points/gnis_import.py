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
    ]]

    # Rename
    sdf.rename(columns={
        'Name' : 'name',
        'Type' : 'category',
        'Type2' : 'subcategory',
        'Creator': 'created_user',
        'Created': 'created_date',
        'Editor': 'last_edited_user',
        'Last_Edit' : 'last_edited_date',
    }, inplace=True)

    # Change column types
    sdf[['created_date']]  = sdf[['created_date']].astype("datetime64")
    sdf[['last_edited_date']]  = sdf[['last_edited_date']].astype("datetime64")

    # Add some fields and set defaults on them.
    sdf.loc[:, 'source'] = 'clatsop'

    print("We have %d points." % len(sdf))
    print(sdf.head(5))
    print(sdf.columns)
    print(sdf.dtypes)

    wm_fc = output_location + '/' + 'poi_wm_' + datestamp
    sdf.spatial.to_featureclass(wm_fc, sanitize_columns=False)
    print("Wrote %d points to \"%s\"." % (len(sdf), wm_fc))

    local_fc = output_location + '/poi_local_' + datestamp
    sref = """PROJCS['NAD_1983_HARN_StatePlane_Oregon_North_FIPS_3601_Feet_Intl',GEOGCS['GCS_North_American_1983_HARN',DATUM['D_North_American_1983_HARN',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',8202099.737532808],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-120.5],PARAMETER['Standard_Parallel_1',44.33333333333334],PARAMETER['Standard_Parallel_2',46.0],PARAMETER['Latitude_Of_Origin',43.66666666666666],UNIT['Foot',0.3048]]", transform_method=["NAD_1983_HARN_To_WGS_1984_2"], in_coor_system="GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]]"""
    print("Reprojecting to \"%s\"." % local_fc)
    #https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/project.htm
    arcpy.management.Project(wm_fc, local_fc,
        out_coor_system=sref, 
        #transform_method='NAD_1983_HARN_To_WGS_1984_2'
    )

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

    # Columns that we're keeping
    # There are a bunch ignored including COUNTY STATE COUNTRY
    # and specialize ones that probably only matter to GeoComm like rSrcId
    # There are two GlobalId fields, huh. That's annoying. I keep only 1.

    sdf = sdf[['SHAPE', 
        'FEATURE_ID',    # a long int
        'FEATURE_NAME',  # 
        "FEATURE_CLASS", # Make the domain from this
        'ELEV_IN_FT',
#        'MAP_NAME',      # Quad?? "Warrenton", "Tillamook Head"...
        "DATE_CREATED",
        "DATE_EDITED",
        "Elevation_Source", # "GNIS", "LIDAR DEM", "10m DEM", ...
        ]]

    # Rename some fields
    sdf.rename(columns={
        'FEATURE_NAME'  : 'name',
        'FEATURE_CLASS' : 'category',
        'DATE_CREATED'  : 'created_date',
        'DATE_EDITED'   : 'last_edited_date',
    }, inplace=True)

    # Add some fields and set defaults on them.
    sdf.loc[:, 'created_user'] = 'GNIS'
    sdf.loc[:, 'last_edited_user'] = ''
    sdf.loc[:, 'source'] = 'gnis'
    sdf.loc[:, 'subcategory'] = sdf.loc[:, 'category']

    # Change float64 column to string, to remove the stupid ".0" endings.
    sdf[['FEATURE_ID']]  = sdf[['FEATURE_ID']].astype("int64")
    sdf[['created_date']]  = sdf[['created_date']].astype("datetime64")
    sdf[['last_edited_date']]  = sdf[['last_edited_date']].astype("datetime64")

    print("We have %d points." % len(sdf))
    print(sdf.head(5))
    print(sdf.columns)
    print(sdf.dtypes)

    fc = output_location + '/' + 'gnis_ogic_' + datestamp
    sdf.spatial.to_featureclass(fc, sanitize_columns=False)
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

    return local_fc

def fix_category(row):
    # Change some categories
    d_cat = {
        'City Park':  'Park',
        'State Park': 'Park',
        'Wayside':    'Park',

        'Bar':      'Water',
        'Basin':    'Water',
        'Bay':      'Water',
        'Channel':  'Water',
        'Falls':    'Water',
        'Lake':     'Water',
        'Rapids':   'Water',
        'Reservoir':'Water',
        'Spring':   'Water',
        'Stream':   'Water',
        'Swamp':    'Water',

        'Census': 'Populated Place',
        'Civil':  'Populated Place',

        'Christian': 'Church',

#        'Post Office' : 'Government',

        'Public School': 'School', 
        'Pre-School/Kinder': 'School', 
        'Private School': 'School', 
        'Public School': 'School', 
        
        'Deer': 'Wildlife Refuge',
        'Elk': 'Wildlife Refuge',
    }
    for k,v in d_cat.items():
        # select and change them
        if row['category'] == k: row['category'] = v

    if 'County Park' in row['name']:
        row['category'] = 'Park'
        row['subcategory'] = 'County Park'
    elif 'State Park' in row['name']:
        row['category'] = 'Park'
        row['subcategory'] = 'State Park'
    elif 'Boat Ramp' in row['name'] or 'Boat Access' in row['name']:
        row['category'] = 'Boat Ramp'
        row['subcategory'] = ''
    elif 'Church' in row['name']:
        row['category'] = 'Boat Ramp'
        row['subcategory'] = ''
    elif 'City Hall' in row['name']:
        row['category'] = 'Building'
        row['subcategory'] = 'City Hall'
    elif 'Library' in row['name']:
        row['category'] = 'Building'
        row['subcategory'] = 'Library'
    elif 'Lighthouse' in row['name']:
        row['category'] = 'Building'
        row['subcategory'] = 'Lighthouse'
    elif 'Golf' in row['name'] or  'Country Club' in row['name']:
        row['category'] = 'Golf'
        row['subcategory'] = ''
    elif 'Police' in row['name']:
        row['category'] = 'Police'
        row['subcategory'] = ''
    elif 'Fire' in row['name'] or 'Station' in row['name']:
        row['category'] = 'Fire Station'
        row['subcategory'] = ''

    if row['category'] == 'Library': 
        row['operator'] = row['subcategory']
        row['subcategory'] = ''
    elif row['category'] == 'Post Office': 
        row['category'] = 'Building'
        row['subcategory'] = 'Post Office'
    elif row['category'] == 'Beach':
        row['category'] = 'Park'
        row['subcategory'] = 'Beach'
    elif row['category'] == 'Campground':
        row['category'] = 'Park'
        row['subcategory'] = 'Campground'
    elif row['category'] == 'Lighthouse':
        row['category'] = 'Building'
        row['subcategory'] = 'Lighthouse'
    elif row['category'] == 'Public Building':
        row['category'] = 'Building'
        row['subcategory'] = ''
    elif row['category'] == 'View' or row['category'] == 'Photo View':
        row['category'] = 'Viewpoint'
        row['subcategory'] = ''
    elif row['category'] == 'Reserve':
        row['category'] = 'Wildlife Refuge'
        row['subcategory'] = ''
    elif row['category'] == 'Bird' and row['subcategory'] == 'Federal':
        row['category'] = 'Wildlife Refuge'
    elif row['category'] == 'Wreck':
        row['category'] = 'Shipwreck'
        row['subcategory'] = ''

    # A subcategory cannot be in more than one categpry,
    # this is why all these rules are here.
    if row['subcategory'] == 'Astoria' or row['subcategory'] == 'Ast Park':
        row['locale'] = 'Astoria'
        row['subcategory'] = ''
    elif row['subcategory'] == 'ASTPolice':
        row['operator'] = 'City of Astoria'
        row['subcategory'] = ''
    elif row['subcategory'] == 'Oregon':
        row['operator'] = 'State of Oregon'
        row['subcategory'] = ''
    elif row['subcategory'] == 'CB':
        row['locale'] = 'Cannon Beach'
        row['subcategory'] = ''
    elif row['subcategory'] == 'Camp Rilea':
        row['locale'] = 'Camp Rilea'
        row['subcategory'] = ''
    elif row['subcategory'] == 'CCPark': 
        row['operator'] = 'Clatsop County Park'
        row['subcategory'] = ''
    elif row['subcategory'] == 'Federal': 
        row['operator'] = 'Federal'
        row['subcategory'] = ''
    elif row['subcategory'] == 'NATPark':
        row['operator'] = 'National Park Service'
        row['subcategory'] = ''
    elif row['subcategory'] == 'Seaside': 
        row['operator'] = 'City of Seaside'
        row['subcategory'] = ''
    elif row['subcategory'] == 'WAPark': 
        row['operator'] = 'Washington State'
        row['subcategory'] = ''
    elif row['subcategory'] == 'Warrenton': 
        row['locale'] = 'Warrenton'
        row['subcategory'] = ''
    elif row['subcategory'] == 'Wauna': 
        row['locale'] = 'Wauna'
        row['subcategory'] = ''
    elif row['subcategory'] == 'Westport': 
        row['locale'] = 'Westport'
        row['subcategory'] = ''
    elif row['subcategory'] == 'County': 
        row['operator'] = 'Clatsop County'
        row['subcategory'] = ''
    elif row['subcategory'] == 'Gearhart': 
        row['locale'] = 'Gearhart'
        row['operator'] = 'Gearhart'
        row['subcategory'] = ''
    elif row['subcategory'] == 'Jewell': 
        row['locale'] = 'Jewell'
        row['subcategory'] = ''
    elif row['subcategory'] == 'Military': 
        row['subcategory'] = row['category']
        row['category'] = 'Military'

    if row['category'] == row['subcategory']:
        row['subcategory'] = ''

    return row

# ----------------------------------------------------------------------------------------------
if __name__ == '__main__':

    egdb = 'C:/Users/bwilson/AppData/Roaming/Esri/ArcGISPro/Favorites/Clatsop_WinAuth.sde'
    fgdb = "K:/e911/e911.gdb"
    datestamp = datetime.now().strftime("%Y%m%d_%H%M")

    # Input data
    cc_points = fgdb + "/" + "points_of_interest"
    assert arcpy.Exists(cc_points)

    gnis_points = "K:/State Data/GNIS_2014/GNIS_OR.gdb/GNIS_OR.gdb/GNIS_OR_Buffer"
    assert arcpy.Exists(gnis_points)

    pd.set_option('display.max_columns', None)

    places = fgdb + '/' + 'places_20210503_1507'
    if arcpy.Exists(places):
        sdf = GeoAccessor.from_featureclass(places)
    else:
        poi_fc = process_cc_poi(cc_points, datestamp, fgdb)
        gnis_fc = process_gnis_points(gnis_points, datestamp, fgdb)
    # Cat them together
        df1 = GeoAccessor.from_featureclass(poi_fc)
        df2 = GeoAccessor.from_featureclass(gnis_fc)
        sdf  = pd.concat([df1, df2])

    places = fgdb + '/' + 'places_' + datestamp

    # Clean!

    # Add city as an attribute, to make for better Locator results
    # for example, there is more than one "City Park". Where are they?
    cities = egdb + '/' + 'Clatsop.DBO.cities'
    cities_df = GeoAccessor.from_featureclass(cities)[['City', 'SHAPE']]
    cities_df.rename(columns={'City':'locale'}, inplace=True)
    sdf = sdf.spatial.join(cities_df, how='left', op='intersects')

    # Fix up a few category names, like "Christian" should be "Church"
    sdf = sdf.apply(fix_category, axis=1)

    # Add missing fields
    sdf.loc[:, 'operator'] = '' # eg "Clatsop County Park" or "City of Astoria"

    # Change field order, and dump any columns we don't want by not listing them here.
    sdf = sdf[['name',
        'category', 'subcategory', 
        'operator',
        'locale', # Using city but could be an area eg Camp Rilea or Knappa or a park?
        'ELEV_IN_FT', 'Elevation_Source', # I care about this because of summits.
        'source', 
        'FEATURE_ID', 
        'created_user', 'created_date', 'last_edited_user', 'last_edited_date', 
        'SHAPE'
    ]]  
    sdf.spatial.to_featureclass(places, sanitize_columns = False)

    # Create aliases
    # The original column names are left untouched,
    # but I assign more readable aliases here.
    # NB some of these names are chosen to match up with the Esri point_address locator.
    # NB It turns out assigning some them in the locator makes the locator results icky.
    d_aliases = { 
        'FEATURE_ID' : 'id', 
        'ELEV_IN_FT' : 'elevation', 
        #'MAP_NAME': 'quad name',
        'Elevation_Source': 'elevation source'
    }
    set_aliases(places, d_aliases)
    print("Wrote %d points to \"%s\"" % (len(sdf), places))
    print("..and we're done!")

# That's all!
