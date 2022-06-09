import os, sys
import json
from urllib.request import urlopen
from urllib.parse import urlencode
import arcpy
from arcgis.gis import GIS
from config import Config

# Read
# https://pro.arcgis.com/en/pro-app/latest/arcpy/sharing/introduction-to-arcpy-sharing.htm


prjPath  = "K:/webmaps/basemap/basemap.aprx"
ags_file = "K:/webmaps/basemap/server (publisher).ags"

"""
# Normally we'd use these...
title = "Clatsop County"
sdname = 'Clatsop_County'
webmap_name = 'Test map for Clatsop County data'
# Set sharing options
shrOrg = True
shrEveryone = True
shrGroups = "CC Gallery"
"""

# ...but when testing we don't want to break things
# also we want a small test data set!
title = 'Astoria Shively McClure District'
service_name = 'Astoria_Shively_McClure_District'
# Set sharing options
shrOrg = False
shrEveryone = False
shrGroups = ""

folder = "TESTING_Brian"
# Speedier to use the SSD to hold the sddraft and sd files.

#tmpPath, name = os.path.split(prjPath)
tmpPath = 'C:/temp'

def fetch_tile(service_url, output_file):

    # Get a token
    token_url = Config.PORTAL_URL + '/sharing/rest/generateToken'
    referer = Config.SERVER_URL + '/rest/services'
    query_dict1 = {
        'username':   Config.PORTAL_USER,
        'password':   Config.PORTAL_PASSWORD,
        'expiration': str(1440),
        'client':     'referer',
        'referer':     referer
    }
    query_string = urlencode(query_dict1)
    token = json.loads(urlopen(token_url + "?f=json", str.encode(query_string)).read().decode('utf-8'))['token']

    # Validation - Save the tile image to local disk
    tile_url = service_url + "/export?bbox=-123.830,46.188,-123.825,46.185&format=png&transparent=false&f=image&token="
    f = open(output_file,'wb')
    data = urlopen(tile_url + token).read()
    print("Exported map from " + tile_url + token + " to " + output_file)
    f.write(data)
    f.close()

if __name__ == '__main__':

    # Find the map we want in the ArcGIS Pro project.
    project = arcpy.mp.ArcGISProject(prjPath)
    maps = project.listMaps()
    map = None
    for item in maps:
        if item.name == title:
            map = item
            break
    if map:
        print("Map matching \"%s\" found in %s." % (title, prjPath))
    else:
        sys.exit("No map \"%s\" found in %s" % (title, prjPath))

    overwrite = False # Faster debugging of publish step...
    overwrite = True # Force creation of a new SD file
    sdname = os.path.join(tmpPath, service_name + ".sd")
    if overwrite or not os.path.exists(sdname):
        assert create_service_definition(map, sdname, folder)

    
    # First I try to update an existing definition.
    # If that fails then I create a new one...

    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
    if update_service_definition(gis, sdname, service_name):
        print("Service definition has been updated.")

    else:
        print("Uploading definition using \"%s\" %s" % (ags_file, folder))

        # Upload the service definition to SERVER 
        # In theory everything needed to publish the service is already in the SD file.
        # https://pro.arcgis.com/en/pro-app/latest/tool-reference/server/upload-service-definition.htm
        # You can override permissions, ownership, groups here too.
        try:
            # In theory ags_file could be Config.SERVER_URL but then where does it get authenticated?
            # arcpy.server.UploadServiceDefinition(sdname, ags_file, in_startupType="STARTED")
            # in_startupType HAS TO BE "STARTED" else no service is started on the SERVER.

            rval = arcpy.SignInToPortal(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
            rval = arcpy.server.UploadServiceDefinition(sdname, Config.SERVER_URL, in_startupType="STARTED")
        except Exception as e:
            print("Upload failed.", e)

    service = Config.SERVER_URL + '/rest/services/' 
    if folder:
        service += folder + "/"
    service += service_name + '/MapServer'
    print("Map Image published successfully - ", service)

    fetch_tile(service, "C:/temp/output.png")
