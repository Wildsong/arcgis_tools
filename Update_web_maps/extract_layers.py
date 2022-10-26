"""
Extract a layer from a "classic" map.

"""
from calendar import c
import os
import json
import re
from glob import glob
from utils import load_json, save_json, findLayer, describeMap

# ======================================================================================================

if __name__ == "__main__":
    
    arcgisContentFolder = "\\\\cc-gis\\C$\\arcgis\\arcgisportal\\content\\items"

    # This is my standard map, which is used as the basis of other projects.
    # First update this map in the Classic Map Viewer,
    # (make sure you set up popups too!),
    # then come here to extract the layers you need with this tool.
    ccMapTemplateId = '8220470e7d8141ada9917eb31a42c107'

    # This is the CC public web map
    ccWebMapsId = 'f84321f3545643adaadf889ce70dc73e'

    mapId = ccMapTemplateId

    map = load_json(os.path.join(arcgisContentFolder, mapId, mapId))
    describeMap(map)

    layerList = [
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
    ]

    # TODO: I suppose I could just iterate the mapFile 
    # and create a JSON file for each layer.

    for item in layerList:
        title = item['title']
        layerFile = item['layerFile']
        i = findLayer(map, "title", title)
        layer = map['operationalLayers'][i]
        save_json(layer, layerFile, minify=False)
        print(f"Wrote \"{layerFile}\".")

    print("All done!", os.getcwd())
