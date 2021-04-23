# Update a layer
# or layers
# or something
#
# Anyway, replace some stuff with some other stuff.
#
# Maps are JSON this should be easy.
#
import sys
import os
import re
from config import Config

from arcgis.gis import GIS
from arcgis.gis import server as SERVER
from arcgis.mapping import WebMap as WEBMAP
from arcgis.gis import Item as ITEM
from arcgis.mapping import MapImageLayerManager

from IPython.display import display
from watermark import watermark

VERSION = '0.1'
path,exe = os.path.split(__file__)
myname = exe + ' ' + VERSION


def find_maps(map_query, layer_query=None, url_query=None):
    maps = gis.content.search(map_query, max_items=1000, sort_field="title", sort_order="asc", outside_org=False, item_type="Web Map")
    found_maps = {}
    if layer_query: re_layer = re.compile(layer_query)
    if url_query: re_url   = re.compile(url_query)
    for map in maps: 
        map_info = "%s (%s) %s" % (map.title, map.owner, map.type)
        web_map = WEBMAP(map)
        #display(web_map) # This loads the map in an iPython window.

        k = "%s : %s" % (map.id, map.title)
        found_maps[k] = []
        for layer in web_map.layers:
            if layer_query:
                mo = re_layer.search(layer.title)
                if mo: 
                    found_maps[k].append(layer)
                    continue

            if url_query:
                try:
                    mo = re_url.search(layer.url)
                    if mo:
                        found_maps[map.title].append(layer)
                        continue
                except Exception as e:
                    continue

    #        if layer.layerType == 'VectorTileLayer' and layer.title == old_label_name:
                
                # I see you, old labels.
    #           print("county labels updated")
    #          i_did_update = True

    #           web_map.remove_layer(layer)
                #web_map.add_layer(new_label)

#            if layer.layerType == 'ArcGISTiledMapServiceLayer':
#                try:
#                    layerId = layer.itemId
#                except AttributeError:
#                    layerId = None
#                if layerId != current_id:
#                    if "Clatsop County" in layer.title:
#                        msg += map_info + "\n" 
#                        msg += "\ttitle:\"%s\" id:%s itemId:%s\n" % (layer.title, layer.id, layerId)

                    #print("new layer", new_basemap)
                    #web_map.remove_layer(layer)
                    #web_map.add_layer(new_basemap)
                    #i_did_update = True
 #               else:
 #                   print(map.title, "is CURRENT")
    for map,layers in found_maps.items():
        if len(layers)>0:
            print(map)
            for layer in layers:
                print("   %s: \"%s\"" % (layer.id, layer.title))
            print()
    return

def test_mil():
    # Collect the information we'll put in a comment string.
    from datetime import datetime
    now = datetime.now()
    datestamp = now.strftime("%Y-%m-%d %H:%M") # for comments
    datestring = now.strftime("%Y%m%d_%H%M") # for filenames

    # I dont care about labels right now because i use a different workflow.

    label_name        = 'Clatsop County labels'
    old_label_name    = 'Clatsop County labels'
    
    tile_name  = 'Clatsop_County_cached_tiles'

    #new_labels  = gis.content.search('title:' + label_name, item_type = 'Vector Tile Layer')
    #if not new_labels or len(new_labels)>1:
    #    raise Exception("Can't find new labels.")
    #print("label layer", new_labels)
    #new_label_item = new_labels[0]

    tile_layers = gis.content.search('title:' + tile_name,
                                    item_type = 'Map Image Layer')
    if not tile_layers or len(tile_layers) > 1:
        raise Exception("Can't find \"%s\"." % tile_name)
    tile_layer = tile_layers[0]
    print("tile layer", tile_layer)

    map_service = "https://delta.co.clatsop.or.us/server/rest/admin/services/Hosted/Clatsop_County_cached_tiles/MapServer"

    mil = MapImageLayerManager(url=map_service, gis=gis)
    d = mil.update_tiles(levels = [9])

    print(d)

if __name__ == "__main__":     

    print("Connecting to ", Config.PORTAL)
    gis = GIS(url=Config.PORTAL, 
            username=Config.USER, 
            password=Config.PASSWORD, verify_cert=False)

    # For query definition, refer to http://bitly.com/1fJ8q31
    map_query = ""
    #map_query = "owner:bwilson@CLATSOP"
    #find_maps(map_query, url_query='.*oda.state.*')
    find_maps(map_query, layer_query='^OCMP .*')

    print("----")
    #print("I found %d maps on this server." % count)

# That's all!
