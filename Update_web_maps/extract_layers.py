"""

    Extract JSON files for layers from a "classic" map.
    The extracted files can then be used to repair other maps.

"""
from calendar import c
import os
import json
import re
from glob import glob
from utils import load_json, save_json, findLayer, describeMap, portalContentFolder


# ======================================================================================================

if __name__ == "__main__":
    
    cwd = os.getcwd()

    # Adjust this for your own workspace.
    os.chdir(r'c:/Users/bwilson/Documents/source/arcgis_tools/')

    # This is a template map, sometimes used as the source to create new maps.
    # First update this map in the Classic Map Viewer, 
    # (make sure you set up popups too!),
    # then come here to extract the layers you need with this tool.
    ccMapTemplateId = '8220470e7d8141ada9917eb31a42c107'

    # This is the CC public web map
    ccWebMapsId = 'f84321f3545643adaadf889ce70dc73e'

    # pick one
    #mapId = ccWebMapsId 
    mapId = ccMapTemplateId

    map = load_json(os.path.join(portalContentFolder, mapId, mapId))
    describeMap(map)

    layerList = [
        {
            "title": "^Taxlots$", # remember these are regex strings
            "layerFile": "layers/taxlots.json", 
        },
        {
            "title": "^Taxlots Labels$", # remember these are regex strings
            "layerFile": "layers/taxlots_labels.json", 
        },
        {
            "title": "^Surveys$", # remember these are regex strings
            "layerFile": "layers/surveys.json", 
        },
        {
            "title": "^County Aerial Photos \\(brief\\)$", # remember these are regex strings
            "layerFile": "layers/county_aerials_brief.json", 
        },
        {
            "title": "^County Aerial Photos$",
            "layerFile": "layers/county_aerials.json", 
        },
        {
            "title": "Roads",
            "layerFile": "layers/roads.json", 
        },
        {
            "title": "Taxmap Layers",
            "layerFile": "layers/taxmap_layers.json", 
        },
    ]

    # TODO: I suppose I could just iterate the mapFile 
    # and create a JSON file for every layer.

    for item in layerList:
        title = item['title']
        layerFile = item['layerFile']
        try:
            opLayers = map['operationalLayers']
            i = findLayer(opLayers, "title", title)
            layer = opLayers[i]
            save_json(layer, layerFile, minify=False)
            print(f"Wrote \"{layerFile}\".")
        except Exception as e:
            print("Failed,", e)

        #exit(0)

    print("All done!", os.getcwd())
