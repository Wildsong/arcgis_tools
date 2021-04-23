import os, sys
import json
from urllib.request import urlopen
from urllib.parse import urlencode
import arcpy
from arcgis.gis import GIS
from config import Config

# Read
#    https://proceedings.esri.com/library/userconf/proc18/tech-workshops/tw_4535-433.pdf



prjPath  = "K:/webmaps/Basemap_PRO/basemap_pro.aprx"
ags_file = "K:/webmaps/Basemap_PRO/server (publisher).ags"

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

def create_service_definition(aprx_map, sdname, folder=""):
    """ 
        Using a map from ArcGIS Pro project, 
        create a new SDDraft
        use the draft to create a new SD file.

        Input:  aprx_map is a map object from an APRX project
                sdname is the service definition name
                folder (optional) destination folder on the server
        Output: files: a service draft and a service definition

        Returns: complete path for SD file or None
    """
    path, name = os.path.split(sdname)
    service_name, ext = os.path.splitext(name)
    sddraft = os.path.join(path, service_name + ".sddraft")

    arcpy.env.overwriteOutput = True

    """Current version."""
    # This call is ONLY for "STANDALONE_SERVER" (no federation allowed!!!)
    """sharing_draft = arcpy.sharing.CreateSharingDraft('STANDALONE_SERVER', 'MAP_SERVICE', service_name, aprx_map)
    sharing_draft.targetServer = ags_file"""
    
    # You can include a list of layers here, and then you can omit services or add some that aren't in the AGP map.
    #sharing_draft = aprx_map.getWebLayerSharingDraft('FEDERATED_SERVER', 'MAP_IMAGE', service_name)
    #sharing_draft.federatedServerUrl = Config.SERVER_URL # required!

    # FAIL: You can't write a MAP_IMAGE to a HOSTING_SERVER
    sharing_draft = aprx_map.getWebLayerSharingDraft('HOSTING_SERVER', 'TILE', service_name)
    sharing_draft.portalUrl = Config.PORTAL_URL # required!

    # All these are optiona;
    sharing_draft.portalFolder = folder
    sharing_draft.serverFolder = folder
    sharing_draft.summary = ''
    sharing_draft.tags = 'TEST'
    sharing_draft.credits = ''
    sharing_draft.description = ''
    sharing_draft.copyDataToServer = True
    sharing_draft.overwriteExistingService = True
    #sharing_draft.offline = False
    #sharing_draft.useLimitations = False

    # In theory this writes the XML file we're looking for.
    sharing_draft.exportToSDDraft(sddraft)

    """deprecated version
    try:
        print("Creating draft in \"%s\"." % sddraft)
        arcpy.mp.CreateWebLayerSDDraft(aprx_map, sddraft, service_name, 
            server_type='HOSTING_SERVER', service_type="MAP_SERVICE", folder_name=folder, 
            overwrite_existing_service=True, copy_data_to_server=True, allow_exporting=False, 
            summary=title, tags="TEST", description="TEST",credits="")
    """

    # Can I do an "Analyze" step here??

    try:
        print("Converting XML sddraft to sdfile \"%s\"." % sdname)
        arcpy.StageService_server(sddraft, sdname)
    except Exception as e:
        print("Staging failed:", e)
        return False

    return True

def update_service_definition(gis, sd, service_name):

    print("Searching for original SD \"%s\" on portal…" % service_name)
    query = "{} AND owner:{}".format(service_name, Config.PORTAL_USER)
    try:
        sdItem = gis.content.search(query, item_type="Service Definition")[0]
    except Exception as e:
        print("Could not find service definition for \"%s\"." % service_name, e)
        return None

    try:
        print("Found SD: {}, ID: {} Uploading and overwriting…".format(sdItem.title, sdItem.id))
        sdItem.update(data=sd)
    except Exception as e:
        print("Could not update service definition.", e)
        return None

    try:
        print("Overwriting service…")
        fs = sdItem.publish(overwrite=True)
    except Exception as e:
        print("Could not overwrite \"%s\"." % sdname, e)
        return None

    try:
        if shrOrg or shrEveryone or shrGroups:
            print("Setting sharing options…")
            fs.share(org=shrOrg, everyone=shrEveryone, groups=shrGroups)
    except Exception as e:
        print("Could set permissions for \"%s\"." % service_name, e)
        return None

    print("Finished updating: {} – ID: {}".format(fs.title, fs.id))
    return fs.title

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
