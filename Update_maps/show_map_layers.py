# Just show the layers in a map
#
import os

from arcgis.gis import GIS
from arcgis.gis import server as SERVER
from arcgis.mapping import WebMap as WEBMAP
from arcgis.gis import Item as ITEM

from config import Config

VERSION = '1.0'
path,exe = os.path.split(__file__)
myname = exe + ' ' + VERSION

gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD, verify_cert=False)

# For query definition, refer to http://bitly.com/1fJ8q31
#q = "title:Clatsop County Template"
#q = "owner:bwilson@CLATSOP"
q = ""
maps = gis.content.search(q, item_type="Web Map")
print("Maps found %d" % len(maps))
for map in maps: 
    web_map = WEBMAP(map)

    basemap = web_map.basemap.baseMapLayers[0]
    try:
        t = basemap.layerType
        pass
    except AttributeError:
        t = basemap.type
    try:
        ttl = basemap.title
        pass
    except AttributeError:
        ttl = basemap.id
#    print("basemap: %s (%s)" % (ttl, t))

    old_id = "38eb0a5b3ab1468f8465c76a01c6375f"
    new_id = "6868cf24b52c4230bc97dc9815d4caa5"

    for layer in web_map.layers:
        try:
            if layer.title == "Clatsop_County":
                print('"%s" : %s : %s' % (map.title, map.owner, map.tags))
                print('%s "%s" "%s"' % (layer.id, layer.title, layer.layerType), layer.itemId)
        except AttributeError:
            pass

# That's all!
