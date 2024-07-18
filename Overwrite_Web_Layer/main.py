import os, sys
import json
from urllib.request import urlopen
from urllib.parse import urlencode
import arcpy
from arcgis.gis import GIS
from config import Config

# Read
# https://pro.arcgis.com/en/pro-app/latest/arcpy/sharing/introduction-to-arcpy-sharing.htm

prjPath = "K:/webmaps/basemap/basemap.aprx"

"""
# Normally we'd use these...
title = "Clatsop County"
# Set sharing options
shrOrg = True
shrEveryone = True
shrGroups = "CC Gallery"
"""

# ...but when testing we don't want to break things
# also we want a small test data set!
webmap_name = 'Test map for Clatsop County data'
title = 'Map for testing scripts, do not delete.'
service_name = 'TEST_fc'
# Set sharing options
shrOrg = False
shrEveryone = False
shrGroups = ""

folder = "TESTING_Brian"
# Speedier to use the SSD to hold the sddraft and sd files.

#tmpPath, name = os.path.split(prjPath)
tmpPath = 'C:/temp'

def create_sd_file(aprx_map, sd_file, folder=""):
    """ 
        Using a map from ArcGIS Pro project, 
        create a new SDDraft file
        use the SDDraft file to create a new SD file.

        Input:  aprx_map is a map object from an APRX project
                sd_file is the service definition name
                folder (optional) destination folder on the server
        Output: files: a service draft and a service definition

        Returns: True or False
    """
    path, name = os.path.split(sd_file)
    service_name, ext = os.path.splitext(name)
    sddraft_filename = os.path.join(path, service_name + ".sddraft")

    arcpy.env.overwriteOutput = True

    # You can include a list of layers here, and then you can omit services or add some that aren't in the AGP map.
    sddraft = aprx_map.getWebLayerSharingDraft('HOSTING_SERVER', 'FEATURE', service_name)
    sddraft.federatedServerUrl = Config.SERVER_URL # required!

    # FAIL: You can't write a MAP_IMAGE to a HOSTING_SERVER
    #sddraft = aprx_map.getWebLayerSharingDraft('HOSTING_SERVER', 'TILE', service_name)
    #sddraft.portalUrl = Config.PORTAL_URL # required!

    # All these are optiona;
    sddraft.portalFolder = folder
    sddraft.serverFolder = folder
    sddraft.summary = ''
    sddraft.tags = 'TEST'
    sddraft.credits = ''
    sddraft.description = ''
    sddraft.copyDataToServer = True
    sddraft.overwriteExistingService = True
    #sddraft.offline = False
    #sddraft.useLimitations = False

    # In theory this writes the XML file we're looking for.
    sddraft.exportToSDDraft(sddraft_filename)

    """deprecated version
    try:
        print("Creating draft in \"%s\"." % sddraft_filename)
        arcpy.mp.CreateWebLayerSDDraft(aprx_map, sddraft_filename, service_name, 
            server_type='HOSTING_SERVER', service_type="MAP_SERVICE", folder_name=folder, 
            overwrite_existing_service=True, copy_data_to_server=True, allow_exporting=False, 
            summary=title, tags="TEST", description="TEST",credits="")
    """

    # Can I do an "Analyze" step here??

    try:
        print("Converting XML sddraft to sdfile \"%s\"." % sd_file)
        arcpy.StageService_server(sddraft_filename, sd_file)
    except Exception as e:
        print("Staging failed:", e)
        return False

    return True

def update_service_definition(sd_file, sdItem, service_name):

    try:
        sdItem.update(data=sd_file)
    except Exception as e:
        print("Could not update service definition.", e)
        return None

    try:
        print("Overwriting service…")
        fs = sdItem.publish(overwrite=True)
    except Exception as e:
        print("Could not overwrite.", e)
        return None

    try:
        if shrOrg or shrEveryone or shrGroups:
            print("Setting sharing options…")
            fs.share(org=shrOrg, everyone=shrEveryone, groups=shrGroups)
    except Exception as e:
        print("Could set sharing for \"%s\"." % service_name, e)
        return None

    print("Finished updating: {} – ID: {}".format(fs.title, fs.id))
    return fs.title

def fetch_tile(service_url, output_file):

    # Get a token
    token_url = Config.PORTAL_URL + '/sharing/rest/generateToken'
    referer = Config.SERVER_URL + '/rest/services'
    query_dict1 = {
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
    #overwrite = True # Force creation of a new SD file
    sd_file = os.path.join(tmpPath, service_name + ".sd")
    if overwrite or not os.path.exists(sd_file):
        assert create_sd_file(map, sd_file, folder)
    
    # First I try to update an existing definition.
    # If that fails then I create a new one...

    username = os.environ.get('USERNAME')
    gis = GIS(profile=username)

    print("Searching for an existing SD \"%s\" on portal…" % service_name)
    query = f"{service_name} AND owner:{username}*"
    try:
        sdItem = gis.content.search(query, item_type="Service Definition")[0]
        print("Found SD: {}, ID: {} Uploading and overwriting…".format(
            sdItem.title, sdItem.id))
        if update_service_definition(sd_file, sdItem, service_name):
            print("Service definition has been updated.")
    except Exception as e:
        print("Service does not exist, attempting to create it.", e)
        sdItem = None

    if not sdItem:
        print("Uploading new definition.")

        # Upload the service definition to SERVER 
        # In theory everything needed to publish the service is already in the SD file.
        # https://pro.arcgis.com/en/pro-app/latest/tool-reference/server/upload-service-definition.htm
        # You can override permissions, ownership, groups here too.
        try:
            rval = arcpy.SignInToPortal(Config.PORTAL_URL)
            rval = arcpy.server.UploadServiceDefinition(in_sd_file=sd_file, in_server="My Hosted Services", in_startupType="STARTED")
        except Exception as e:
            print("Upload failed.", e)

# Test by trying to grab a tile from the service.

    service = Config.SERVER_URL + '/rest/services/' 
    if folder:
        service += folder + "/"
    service += service_name + '/MapServer'
    print("Map Image published successfully - ", service)


    fetch_tile(service, "C:/temp/output.png")
