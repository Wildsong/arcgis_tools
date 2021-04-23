import os
import sys
#from arcgis.features import FeatureLayer
#from arcgis.gis import GIS
import requests
import geopandas as gpd
import fiona

# for arcgis
#from utils import connect

from datetime import datetime
datestamp = datetime.now().strftime("%Y%m%d_%H%M")

#    Output_Feature_Class = "K:\\Social_Services\\NearMe\\NearMe.gdb\\address_pt_ReverseGeocode"
#    arcpy.geocoding.ReverseGeocode(in_features=address_pt_2_, in_address_locator="", out_feature_class=Output_Feature_Class, address_type="ADDRESS", search_distance="100 Meters", feature_type="", location_type="")

def drop_untaxables(df):
    """ Drop any taxlots that have a non-numeric Taxlot attribute. """
    # Change all nonnumerics into NaN
    before = len(df)
    df['Taxlot'] = df['Taxlot'].str.extract('(\d+)')
    df = df.dropna(subset=['Taxlot'])
    after = len(df)
    print("before %d after %d" % (before, after))
    #print(df)
    return df

def features_to_points(df):
    """ Return a centroid point for each polygon. """

    # This is a horrible implementation, I hang my head in shame.
    # "Append" creates a new DF on each pass. You fix please.
    points = gpd.GeoDataFrame()
    for index, row in df.iterrows():
        row.geometry = row.geometry.centroid
        points = points.append(row)
    return points

def save_df(sdf,target):
    sdf.spatial.to_featureclass(location=target)
    return 

if __name__ == '__main__':


    fgdb = "K:/Social_Services/NearMe/NearMe.gdb"
#    fgdb = "K:/Social_Services/NearMe/addrpts.gdb"
    taxlots = "taxlots_centroids"

    #serverUrl    = Config.SERVER_URL
    #taxlots_feature_service = serverUrl + '/rest/services/Taxlots/FeatureServer/1'

    try:
        taxlots_df = None

        #whereclause = 'where=1=1'  # get every taxlot.... up to 5000 that is
        #whereclause = 'objectIds=1900267' # get just one, for testing

        # We request the data in web mercator because otherwise it complains
        # about how hard it is to accurately calculate the centroid, and we want the centroid!
#        query_url = taxlots_feature_service + '/query?f=geojson' + '&geometryType=esriGeometryPolygon&outSR=EPSG:3857&' + whereclause
#        data = requests.get(query_url)
#        b = bytes(data.content)
#        with fiona.BytesCollection(b) as fp:
#            crs = fp.crs        
#            taxlots_df = pd.GeoDataFrame.from_features(fp, crs="EPSG:4326")

#        with fiona.open(fgdb, layer=taxlots, mode='r') as fp:
#            print(fp)
        layers = fiona.listlayers(fgdb)
        print(fgdb, layers)
        taxlots_df = gpd.read_file(fgdb, layer=taxlots, rows=5)
        print(taxlots_df)

    except Exception as e:
        print("Could not query taxlots. \"%s\"" % e)

    taxable_df = drop_untaxables(taxlots_df) # This drops ONE point sheesh

#    address_points_df = features_to_points(taxable_df)
#    print(address_points_df)

    # Write the cleaned up data out to address points

    # BE CAREFUL what you write here, it gets WEIRD if you accidentally write a SHAPEFILE (the default)
    # into an GDB directory -- then suddenly ogrinfo will see only the shapefile.
    # https://gis.stackexchange.com/questions/231265/geopandas-write-layer-back-into-geodatabase

    # OpenFileGDB can't WRITE only read so you have to install an extra library,
    # https://gis.stackexchange.com/questions/193288/how-to-add-support-for-filegdb-esri-file-gdb-api-driver-in-fiona

    # How to install FileGDB, follow instructions here
    #    https://glenbambrick.com/2017/03/10/setting-up-gdal-with-filegdb/
    # download https://download.lfd.uci.edu/pythonlibs/w4tscw6k/GDAL-3.2.2-cp37-cp37m-win_amd64.whl
    # pip install the wheel file
    # I had to install the fiona wheel too
    #
    # confirm it loaded
    # python
    # from osgeo import gdal
    # gdal.__version__ should show 3.22
    # cd /k/Social_Services
    # dig the filegdb dll out of the zip and put it into your osgeo folder
    #
    #

    taxable_df.to_file(fgdb, layer='address_pts_' + datestamp, driver="FileGDB", crs="EPSG:4326")
    
    print("Wrote address points.")
