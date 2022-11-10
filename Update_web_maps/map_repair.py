"""
        This used to lookup maps in apps and only repair those.
        Now it finds every map on the Portal and repairs all of them.

"""
import os
from deepdiff import DeepDiff
from glob import glob
import datetime
from arcgis.gis import GIS
from arcgis.gis import Item as ITEM
from config import Config
from utils import portalContentFolder, load_json, save_json, findObjects, findLayer, findMaps, getItemUrl

VERSION = '1.0'
path, exe = os.path.split(__file__)
myname = exe + ' ' + VERSION


def repairBasemapWidget(app_folder:str, dryrun=False) -> None:

    # First off let's extract the JSON for the widget we want, (which is in the PlanningApp)

    widget_name = 'BasemapGallery'
    paths = glob(os.path.join(app_folder, 'configs', widget_name, 'config*.json'))
    if len(paths)!=1:
        raise Exception("This is the wrong answer.")
    config = load_json(paths[0])
    print(config)
    save_json(config, 'basemap_gallery.json', minify=False)

    return

def repairQueryWidget(app_folder:str, template_file:str, dryrun=False):
    widget_name = 'Query'
    template = load_json(template_file)
    template_name = template['name']
    #e.g. template_name = 'Find Road'
    app_config = load_json(os.path.join(app_folder, 'config.json'))

    # Search around in this app's config to find the name of the widget's config file.
    widgets = app_config['widgetPool']['widgets']
    matches = findObjects(l=widgets, field='name', pattern=widget_name)
    count = len(matches)
    if count != 1:
        raise Exception(f"Found {count} matching widget, which is surprising.")

    widget_config_file = os.path.join(app_folder, matches[0]["config"])
    widget_config = load_json(widget_config_file)
    unchanged_config = dict(widget_config)

    inx = 0
    f_inx = None
    for item in widget_config['queries']:  # FIXME!!
        print(f"{inx}: {item['name']}")
        if item['name'] == template_name or item['name'] == template_name+'s':
            print("  Found")
            f_inx = inx
            # Extract to file; it will be the new template.
#            save_json(item, template_file, minify=False)
        inx += 1

    if f_inx:
        # This widget already has this template, so make sure it's not a duplicate
        diff = DeepDiff(template, widget_config['queries'][f_inx], view="tree")
        print(diff.pretty())
        print(diff.get_stats())
        # If nothing changed then don't write a new file!
        # Replace
        widget_config['queries'][f_inx] = template
    else:
        # Otherwise, add it at the end.
        widget_config['queries'].append(template)
    if widget_config == unchanged_config:
        print("These appear the same to me?")
    (p,f) = os.path.split(widget_config_file)
    (f,e) = os.path.splitext(f)
    backup = "C:/temp/" + f + datestamp + e
    print(f"Saving backup file {backup}")
    save_json(unchanged_config, backup)
    save_json(widget_config, widget_config_file)
    return


def repairLayers(mapLayers:dict, replacements:list) -> bool:
    """    
    input:  dict of layers, can be operational or basemap
            replacements = list of repairs to perform
    returns: layer list if changed else None
    """

    # Make a new copy of the list so we can change it without changing the source (map)
    new_layers = list(mapLayers)
    rval = None

    # March through the list of things we are updating.
    for item in replacements:
        field = item['key']
        re_pattern = item[field]

        # I can't just extract the new layer name from the replacement file, because
        # Esri changes them all the time, it's just another frustrating thing about them.
        # So I have to be more flexible and search different fields for different things
        i = findLayer(mapLayers, field, re_pattern)
        if i != None:
            nfname = item['layerFile']
            newLayer = load_json(nfname)
            assert newLayer != None

            new_layers[i] = newLayer
            rval = new_layers

    return rval


def test_layers(cm:object, layers:list) -> list:
    """ Test the layers in this map and return a list of broken ones. """
    broken = list()
    for l in layers:
        if 'itemId' in l: # Some layers don't have an itemId, for example WMS services.
            id = l['itemId']
            title = l['title']
            layer = cm.get(id)
            if not layer:
                print(f"Broken layer \"{title}\" {getItemUrl(id)}")
                broken.append(title)
    return broken

def addComment(gis, id, txt:str) -> None:
    try:
        item = ITEM(gis, id)
        item.add_comment(txt)
    except Exception as e:
        print("Could not make a comment.", e)
    return

# ======================================================================================================

if __name__ == "__main__":

    backup_folder = 'C:\\Temp'
    now = datetime.datetime.now()
    datestamp = '-' + now.strftime("%Y%m%d_%H%M")
    fancydatestamp = now.strftime("%H:%M %m-%d-%y")

    try:
        gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
        print(f"Logged in as \"{gis.properties.user.username}\".")
    except Exception as e:
        print(f"Could not connect to portal. {e}")
        print("Make sure the environment variables are set correctly.")
        exit(-1)

    # This is why we have a map called TEST MAP
    addComment(gis, "2effce16fc1742ecba05c255ea6d7b54", f"{fancydatestamp} -- Tested addComment in {myname}.") # Newlines and markup don't work.
    # https://delta.co.clatsop.or.us/portal/home/item.html?id=2effce16fc1742ecba05c255ea6d7b54

    # First, update this map, then use it to repair the others.
    # The canonical source for all good things
    ccMapTemplateId = '8220470e7d8141ada9917eb31a42c107'

    # Query widget template that will be updated or added to each app.
    find_roads_file = "query_find_roads.json"

    allLayers = [
        { # This one only shows up in the template, I think.
            "key": "title",
            "title": "^County Aerial Photos \\(brief\\)$", # remember these are regex strings
            "layerFile": "layers/county_aerials_brief.json", 
        },
        {
            "key": "title",
            "title": "^County(-wide)? [Aa]erial( [Pp]hotos)?$",
            "layerFile": "layers/county_aerials.json", 
        },
        {
            "key": "title",
            "title": "Roads",
            "layerFile": "layers/roads.json", 
        },
    ]
    briefLayers = [
        {
            "key": "title",
            "title": "^County aerial photos$", # remember these are regex strings
            "layerFile": "layers/county_aerials_brief.json", 
        },
        {
            "key": "title",
            "title": "Roads",
            "layerFile": "layers/roads.json", 
        },
    ]

    # Let's fix the broken layers in every single map

    basemapFile = "layers/basemap.json"

    replacement_layers = [
        {
            "key": "title",
            "title": "^Tsunami [Ee]vacuation [Zz]ones?", # remember these are regex strings
            "layerFile": 'layers/tsunami_evacuation_zones.json'
        },
        #{
        #    "key": "title",
        #    "title": "^Tsunami [Ss]afe [Zz]ones?", # remember these are regex strings
        #    "layerFile": 'layers/tsunami_safe_zones.json'
        #},
        {
            "key": "title",
            "title": "^Contours?", # remember these are regex strings
            "layerFile": 'layers/contours_40.json'
        },
        {
            "key": "title",
            "title": "^City [Aa]erial [Pp]hotos", # remember these are regex strings
            "layerFile": 'layers/city_aerials.json'
        }, 
        {
            "key": "title",
            "title": "Roads",
            "layerFile": "layers/roads.json", 
        },
        { # This one is used in public facing webmaps
            "key": "url",
            "url": "county-aerials-brief/wms$",
            "layerFile": "layers/county_aerials_brief.json", 
        },
        { # This one is used in internal webmaps
            "key": "url",
            "url": "county-aerials/wms$",
            "layerFile": "layers/county_aerials.json", 
        },
        {
            "key": "title",
            "title": "^Clatsop County [Ll]abels$",
            "layerFile": "layers/clatsop_county_labels.json"
        },
        {
            "key": "title",
            "title": "^Clatsop County$", # Normal case
            "layerFile": "layers/clatsop_county_basemap.json"
        },
        {
            "key": "title",
            "title": "^Clatsop County unlabeled",  # Weird one off case
            "layerFile": "layers/clatsop_county_basemap.json"
        },

         # Hillshades
        {
            "key": "title",
            "title": "^Hillshades and slope$",
            "layerFile": "layers/lidar_hillshades.json"
        },
        {
            "key": "title",
            "title": "^LiDAR hillshades$",
            "layerFile": "layers/lidar_hillshades.json"
        },
        {
            "key": "title",
            "title": "^Hillshades from DOGAMI LiDAR$",
            "layerFile": "layers/lidar_hillshades.json"
        },

        {
            "key": "title",
            "title": "^PLSS$",
            "layerFile": "layers/plss.json"
        },
        {
            "key": "title",
            "title": "^Empty Basemap$",
            "layerFile": "layers/empty_basemap.json"
        }
    ]

    maps = findMaps(gis)
    total = len(maps)
    print(f"Checking all {total} maps..")
    repaired = list()
    dryrun = False # SHOW TIME!!
    i = 0
    for thisMap in maps:
        mapId = thisMap.id
        print(f"Checking map {i}/{total}: \"{thisMap.title}\" Owner: {thisMap.owner} URL: {getItemUrl(mapId)}")
        i += 1
        mapFile = os.path.join(portalContentFolder, mapId, mapId)
        backupFile = os.path.join(portalContentFolder, mapId, mapId + datestamp + ".json")
        original_map = load_json(mapFile) # Make a backup
        if not original_map:
            # This could mean the mapfile could not be found or it's not valid JSON
            print(f"  Unreadable map.")
            continue

        # Flag all broken layers
        cm = gis.content
#        test_layers(cm, original_map["operationalLayers"])
#        test_layers(cm, original_map["baseMap"]['baseMapLayers'])
        
        print("  Checking ops layers")
        ops = repairLayers(original_map['operationalLayers'], replacement_layers)
        print("  Checking basemap layers")
        bml = repairLayers(original_map['baseMap']['baseMapLayers'], replacement_layers)

        # If the map did not change then the repair operation was probably already done.
        if ops or bml:
            new_map = dict(original_map)
            broken_ops = list()
            broken_bm  = list()
            if ops: 
                broken_ops = test_layers(cm, ops)
                if len(broken_ops)>0:  # Everything should be fixed now!!!
                    print(f"There are still {len(broken_ops)} broken OPS layers. :-(")
                new_map['operationalLayers'] = ops
            if bml: 
                broken_bm = test_layers(cm, bml)
                if len(broken_bm)>0:  # Everything should be fixed now!!!
                    print(f"There are still {len(broken_bm)} broken basemap layers. :-(")
                new_map['baseMap']['baseMapLayers'] = bml
            print("REPAIRED.")
            repaired.append(mapId)
            #print(DeepDiff(t1=original_map, t2=map).pretty())
            if not dryrun:
                # Make a backup file
                save_json(original_map, backupFile, minify=False)
                save_json(new_map, mapFile) ## OVERWRITE ORIGINAL
                msg = f"Repaired by {myname}. Wrote backup to {backupFile}."
                print(msg)
                if len(broken_ops):
                    b = ' '.join(broken_ops)
                    addComment(gis, mapId, f"BROKEN LAYERS: {b}")
                if len(broken_bm):
                    b = ' '.join(broken_bm)
                    addComment(gis, mapId, f"BROKEN BASEMAP LAYERS: {b}")
                addComment(gis, mapId, msg) # Newlines and markup don't work.
            else:
                mapFile = os.path.join("C:\\Temp", mapId + '.json')
                save_json(new_map, mapFile, minify=False) 
        print("----")
    print(f"Repaired {len(repaired)} maps.")
    exit(0)

    appsBase = "\\\\cc-gis\\C$\\inetpub\\wwwroot\\apps"
    apps = [
        ('PublicWorksApp', allLayers), 
        ('PlanningApp', allLayers), 
        ('ATApp', allLayers), 
        ('ClatsopCounty', briefLayers),
    ]

    repairBasemapWidget(os.path.join(appsBase, 'PlanningApp'))
    exit(0)

# We must update the nice template map now because
# We edited the layer files by hand after pulling them out of the template
# so now we need to repair the template before extracting the layers again!!

    # FIXME: REST CALL??
    mapFile = os.path.join(portalContentFolder, ccMapTemplateId, ccMapTemplateId)
    backup = os.path.join(backup_folder, ccMapTemplateId + datestamp + ".json")
    original_map = load_json(mapFile)
    if repairMap(mapFile, allLayers):
        # Repair was successful so save a backup.
        save_json(original_map, backup, minify=False)
        print(f"Wrote backup of \"{mapFile}\" to \"{backup}\".")

    for (app, layers) in apps:
        print(f"Repairing app \"{app}\".")
        appFolder = os.path.join(appsBase, app)

        continue

        # Examine the query widget in each app and make sure it has "Find Road"
        repairQueryWidget(appFolder, find_roads_file)

        # Find the map in this app
        app_config = load_json(os.path.join(appFolder, 'config.json'))
        mapId = app_config['map']['itemId']
        # FIXME: REST CALL??
        mapFile = os.path.join(portalContentFolder, mapId, mapId)        
        backup = os.path.join(backup_folder, mapId + datestamp + ".json")
        original_map = load_json(mapFile)
        if repairMap(mapFile, layers, dryrun=True):
            # Repair was successful so save a backup.
            #save_json(original_map, backup, minify=False)
            print(f"Wrote backup to \"{backup}\".")

    print("All done!")
