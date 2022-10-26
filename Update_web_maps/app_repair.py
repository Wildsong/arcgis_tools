import os
from deepdiff import DeepDiff
from glob import glob
from datetime import datetime
from utils import load_json, save_json, findObject, findLayer, describeMap


def replaceLayer(map:dict, field:str, re_pattern:str, newLayer:dict) -> dict:
    """
    Find an old layer using a hard-coded layer name, 
    replace it with a new layer, 
    Return the new map
    """

    newmap = dict(map)

    # I can't just extract the new layer name from the replacement file, because
    # Esri changes them all the time, it's just another frustrating thing about them.
    i = findLayer(map, field, re_pattern)
    if i != None:
        # Make a new copy of the list so we can change it without changing the source (map)
        opLayers = list(map['operationalLayers'])
        opLayers[i] = newLayer
        newmap['operationalLayers'] = opLayers

    return newmap


def repairQueryWidget(app_folder:str, template_file:str, dryrun=False):
    
    widget_name = 'Query'

    template = load_json(template_file)
    template_name = template['name']
    #e.g. template_name = 'Find Road'

    app_config = load_json(os.path.join(app_folder, 'config.json'))

    # Search around in this app's config to find the name of the widget's config file.
    widgets = app_config['widgetPool']['widgets']
    matches = findObject(l=widgets, field='name', pattern=widget_name)
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
            print("  Found it!")
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

    (p,f) = os.path.split(widget_config_file)
    (f,e) = os.path.splitext(f)
    backup = "C:/temp/" + f + datestamp + e

    print(f"Saving backup file {backup}")
    save_json(unchanged_config, backup)

    save_json(widget_config, widget_config_file)

    return


def repairMap(mapFile:str, layers:list, dryrun=False) -> bool:
    """
    I rewrite the mapFile.
    It's all up to you to back up the file before calling me.
    
    input:  mapFile
            list of repairs to perform
            dryrun = True then don't really overwrite the mapFile.
    returns: True if map is rewritten
    """
    original_map = map = load_json(mapFile)
    for item in layers:
        newLayer = load_json(item['layerFile'])
        map = replaceLayer(map, "title", item['title'], newLayer)

    # FIXME: I should check the map and make sure it is valid JSON, but I don't.

    # If the map did not change then the repair operation was probably already done.
    if original_map == map:
        print(f"Nothing changed in \"{mapFile}\".")
        status = False
    else:
        print(f"REPAIRED \"{mapFile}\".")
        print(DeepDiff(t1=original_map, t2=map).pretty())
        if not dryrun:
            save_json(map, mapFile)
        status = True

    return status

# ======================================================================================================

if __name__ == "__main__":

    datestamp = '-' + datetime.now().strftime("%Y%m%d_%H%M")

    source_folder = "\\\\cc-gis\\C$\\arcgis\\arcgisportal\\content\\items"
    backup_folder = 'C:\\Temp'

    # First, update this map, then use it to repair the others.
    # The canonical source for all good things
    ccMapTemplateId = '8220470e7d8141ada9917eb31a42c107'

    # Query widget template that will be updated or added to each app.
    find_roads_file = "query_find_roads.json"

    allLayers = [
        { # This one only shows up in the template, I think.
            "title": "^County Aerial Photos \\(brief\\)$", # remember these are regex strings
            "layerFile": "layers/county_aerials_brief.json", 
        },
        {
            "title": "^County(-wide)? [Aa]erial [Pp]hotos$",
            "layerFile": "layers/county_aerials.json", 
        },
        {
            "title": "Roads",
            "layerFile": "layers/roads.json", 
        },
    ]
    briefLayers = [
        {
            "title": "^County aerial photos$", # remember these are regex strings
            "layerFile": "layers/county_aerials_brief.json", 
        },
        {
            "title": "Roads",
            "layerFile": "layers/roads.json", 
        },
    ]

    appsBase = "\\\\cc-gis\\C$\\inetpub\\wwwroot\\apps"
    apps = [
        ('PublicWorksApp', allLayers), 
        ('PlanningApp', allLayers), 
        ('ATApp', allLayers), 
        ('ClatsopCounty', briefLayers),
    ]

# We must update the nice template map now because
# We edited the layer files by hand after pulling them out of the template
# so now we need to repair the template before extracting the layers again!!

    # FIXME: REST CALL??
    mapFile = os.path.join(source_folder, ccMapTemplateId, ccMapTemplateId)
    backup = os.path.join(backup_folder, ccMapTemplateId + datestamp + ".json")
    original_map = load_json(mapFile)
    if repairMap(mapFile, allLayers):
        # Repair was successful so save a backup.
        save_json(original_map, backup, minify=False)
        print(f"Wrote backup of \"{mapFile}\" to \"{backup}\".")

    for (app, layers) in apps:
        print(f"Repairing app \"{app}\".")
        appFolder = os.path.join(appsBase, app)

        # Examine the query widget in each app and make sure it has "Find Road"
        repairQueryWidget(appFolder, find_roads_file)

        continue

        # Find the map in this app
        app_config = load_json(os.path.join(appFolder, 'config.json'))
        mapId = app_config['map']['itemId']
        # FIXME: REST CALL??
        mapFile = os.path.join(source_folder, mapId, mapId)        
        backup = os.path.join(backup_folder, mapId + datestamp + ".json")
        original_map = load_json(mapFile)
        if repairMap(mapFile, layers, dryrun=False):
            # Repair was successful so save a backup.
            save_json(original_map, backup, minify=False)
            print(f"Wrote backup to \"{backup}\".")

    print("All done!")
