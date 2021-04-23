"""
 This is old code 
 I was trying to merge
 taxlot centroids with address data that Krysta created for Elections

 I should probably just throw it away.
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
from pandas.core.frame import DataFramefrom numpy import logical_not

egdb = 'C:/Users/bwilson/AppData/Roaming/Esri/ArcGISPro/Favorites/Clatsop_WinAuth.sde'
fgdb = "K:/e911/e911.gdb"
datestamp = datetime.now().strftime("%Y%m%d_%H%M")

def poly_to_point(s):
    xy = Geometry(s['SHAPE']).centroid # returns a tuple
    sref = s['SHAPE'].spatialReference
    pt = Point({'x':xy[0], 'y':xy[1], 'spatialReference':sref})
    #print(xy, pt)
    s['SHAPE'] = pt
    return s


def make_address_points(points_on_houses, taxlot_polygons_df):
    # There are some features in the points_on_houses that are bogus
    # and you can tell because they x,y attributes are empty.
    try:
        df = GeoAccessor.from_featureclass(points_on_houses, where_clause='X_Coord>0')
        print("Loaded %d addresses" % len(df))
        # Add MapTaxlot as a key by doing an inner join. This should dispose of any address point outside taxlots
        # because we're doing a spatial join.
        # There will be a lodash added at the end of the name when it's tagged (eg 'CITY' -> 'CITY_tl')
        df = df.spatial.join(taxlot_polygons_df, how="inner", op="within", right_tag="tl")
        print("Spatial join results in %d shapes. Columns:" % len(df), df.columns)
    except Exception as e:
        print("Query failed, %s" % e)
        return None
    df['source'] = 'addresses'

    # Note the address points have a CITY field which gets rewritten as CITY_left
    # and the CITY field in taxlots (which gets renamed CITY_tl) is actually the mailing address
    df['OBJECTID'] = df['OBJECTID_left']
    df['CITY']     = df['CITY_left']
    df['ZIP_CODE'] = df['ZIP_CODE_left']
    df['STATE']    = df['STATE_left']

    # keep only the columns I want
    df = df[['OBJECTID', 'SHAPE', 
        'MapTaxlot', 'Taxlot', 'PROPERTY_C', 'STAT_CLASS', # From taxlots
        'ADDR_NON_STD', 
        'HOUSE_NUM', 'HOUSE_SUFFIX', 'PRE_DIRECTION', 'STREET_NAME', 'STREET_TYPE',
        'POST_DIRECTION', 'UNIT_TYPE', 'UNIT_NUM', 
        'CITY', 'STATE', 'ZIP_CODE', 'ZIP_PLUS', 
        'CREATED_DATE', 'MODIFIED_DATE', 
        'X_Coord', 'Y_Coord', # Not sure why I want these right now.
        'source']]
    return df.apply(combine_fields_to_situs, axis=1)

def make_taxlot_points(poly_df):
    try:
        # Make a feature class that has centroids from taxlots, 
        # and remove the ones that are already done in the point feature class
        df = poly_df.apply(poly_to_point, axis=1)
    except Exception as e:
        print("Query failed, %s" % e)
        exit(1)
    df['source'] = 'taxlots'

    # keep only columns I want
    print(df.columns)
    df = df[['OBJECTID', 'SHAPE',
        'MapTaxlot', 'Taxlot', 'PROPERTY_C', 'STAT_CLASS', 'SITUS_ADDR', 'SITUS_CITY', 
        'source']]

    # Break situs out into separate address fields
    situs_df = df.apply(situs_to_fields, axis=1)

    # Remove all "land only" lots that have only outbuildings, which it turns out currently is "none"
    no_house_df = situs_df[logical_not(
        situs_df.PROPERTY_C.str.endswith('01', na=True) & 
        ((situs_df.STAT_CLASS == 200) | (situs_df.STAT_CLASS == 300))
    )]
    print("Without \"improved but only outbuildings\": %d" % len(no_house_df))
    # Remove all 'land only' lots
    final_df = no_house_df[logical_not(
        no_house_df.PROPERTY_C.str.endswith('0', na=True) 
    )]
    print("Without \"land only\": %d" % len(final_df))

    # There are about 100 lots with PROPERTY_C == None that are PROBABLY vacant
    # I should remove those to PROBABLY...

    # TODO - merge in the E911 addresses...

    # Use E911 data to fill as many more addresses as possible; do a join on MaxTaxlot

    # TODO - geocode whatever is left at this point...
    # Finally, are there any left? Reverse geocode! It's better than nothing!

    return final_df


if __name__ == "__main__":

    # Polygons with attributes attached
    taxlot_polygons = egdb + '/' + "Clatsop.DBO.taxlot_accounts"

    # Krysta generated this point layer with points on houses for Elections
    points_on_houses = egdb + '/' + 'Clatsop.DBO.ocvr_res_addresses_08192020_all_points'

    # This will be the collection of points that don't have elections derived addresses
    taxlot_points = fgdb + '/' + 'no_address'

    e911_points = 'K:/e911/From_GeoSolve/OCT19/Clatsop_Addresses.shp'

    e911_hosted_table = "https://delta.co.clatsop.or.us/server/rest/services/Hosted/e911/FeatureServer/0"
    gis = GIS("https://delta.co.clatsop.or.us/portal",username="bwilson@CLATSOP", password=Config.PORTAL_PASSWORD)
    e911_table_df  = Table(e911_hosted_table, gis=gis)
    df = e911_table_df.query(where="1=1").sdf
    # now I have a table but no geometry, so fix that
    sdf = GeoAccessor.from_xy(df, x_column="long", y_column="lat")

    readme_first = fgdb + '/' + 'raw_merge'
    if arcpy.Exists(readme_first):
        address_points_df = GeoAccessor.from_featureclass(readme_first)
        print("Loaded %d points." % len(address_points_df))

    else:
        taxlot_polygons_df = GeoAccessor.from_featureclass(taxlot_polygons)
        print("Loaded %d taxlot polygons." % len(taxlot_polygons_df))


        # Assuming just for the moment that the "points on houses" data is just more work than it's worth,
        # let's ignore it and see what happens.

        if False:
            skipit = fgdb + '/' + 'address_points_joined_taxlots_20210416_1237'
            if arcpy.Exists(skipit):
                points_on_houses_df = GeoAccessor.from_featureclass(skipit)
            else:
                points_on_houses_df = make_address_points(points_on_houses, taxlot_polygons_df)
                # This is intermediate data, written only to help with debugging.
                pathname = fgdb + '/' + 'address_points_joined_taxlots_' + datestamp
                result = points_on_houses_df.spatial.to_featureclass(pathname, sanitize_columns=False)
                print("Wrote %d points to %s." % (len(points_on_houses_df), result))

        taxlot_points_df  = make_taxlot_points(taxlot_polygons_df)
        # This is intermediate data, written only to help with debugging.
        pathname = fgdb + '/' + 'taxlot_points_' + datestamp
        result = taxlot_points_df.spatial.to_featureclass(pathname, sanitize_columns=False)
        print("Wrote %d points to %s." % (len(taxlot_points_df), result))

        print("Merge the data.")

        # FIXME: I need to avoid duplicated points here!!
        # Could check MapTaxlot to remove overlap from taxlot_points_df
 
        #address_points_df = pd.concat([points_on_houses_df, taxlot_points_df])
        #address_points_df.spatial.to_featureclass(readme_first, sanitize_columns=False)

# That's all!
