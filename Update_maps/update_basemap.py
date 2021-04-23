"""
    In this context "basemap" means the map image layer for Clatsop County.
    Find the old basemap and remove it.
    Put the new one in the same place.
"""
import os

from arcgis.gis import GIS
from arcgis.gis import server as SERVER
from arcgis.mapping import WebMap as WEBMAP
from arcgis.gis import Item as ITEM
from arcgis.mapping import MapImageLayerManager

from watermark import watermark
from config import Config

VERSION = '1.0'
path,exe = os.path.split(__file__)
myname = exe + ' ' + VERSION

from datetime import datetime
now = datetime.now()
datestamp = now.strftime("%Y-%m-%d %H:%M") # for comments
datestring = now.strftime("%Y%m%d_%H%M") # for filenames

def update_maps(q, old_id, new_layer):
# for each map on the server,
    # Find a reference to the new layer
    # In the map,
    #   Find the old layer
    #   Remove it
    #   Insert the new layer in the same place

    count = 0
    msg = ''
    maps = gis.content.search(q, max_items=1000, sort_field="title", sort_order="asc", outside_org=False, item_type="Web Map")
    print("Found %d maps." % len(maps))

    for map in maps: 
        i_did_update = False

        map_info = "%s (%s) %s" % (map.title, map.owner, map.type)
        #display(web_map)
        count += 1

        web_map = WEBMAP(map)
        for layer in web_map.layers:

    # I dont care about labels right now because i use a different workflow.
    # They can be directly replaced in Portal.
    #        if layer.layerType == 'VectorTileLayer' and layer.title == old_label_name:
    #           # I see you, old labels.
    #           print("county labels updated")
    #          i_did_update = True
    #           web_map.remove_layer(layer)
                #web_map.add_layer(new_label)

            try:
                layerId = layer.itemId
                layerType = layer.layerType
            except AttributeError:
                layerId = ''
                layerType = ''
            
            if layerType == 'ArcGISTiledMapServiceLayer' and layerId == old_id:
                msg += map_info + "\n" 
                msg += "\ttitle:\"%s\" id:%s itemId:%s\n" % (layer.title, layer.id, layerId)

                print("new layer", new_id)


# ALAS ALAS
# this puts the "added" layer at the TOP of the layer list.
# making this script, well, useless


                web_map.remove_layer(layer)
                web_map.add_layer(new_layer, options={
                    "title": "Clatsop County"
                })
                i_did_update = True
            else:
                print("32%s \"%s\" %s" % (layerId, layer.title, layerType))
            pass

        if i_did_update:

            # "update" will save changes made to the web map
            # alternatively "save" will create a new copy of the map.
            # Thumbnail can be a local file (to upload) or a URL.

            # UPDATE
            web_map.update()
            comment = "%s updated by \"%s\"" % (datestamp, myname)
            item = ITEM(gis, web_map.item.id)
            item.add_comment(comment)

            """
            # SAVE
            old_title = web_map.item.title

            # I need to grab the existing thumbnail from Portal
            #watermarked_thumbnail = "thumbnail_" + datestring + ".jpg" 
            #watermark("thumbnail.jpg", watermarked_thumbnail, old_title, (0,200,200,128))
            
            # comment indicates new map created
            comment = "%s created from \"%s\" by \"%s\"" % (datestamp, web_map.item.title, myname)

            item = web_map.save(item_properties={
                # These are REQUIRED
                    "title":   "CHANGED " +  old_title + ' ' + datestamp, 
                    "snippet": web_map.item.snippet, 
                    "tags":    web_map.item.tags
                },
                #thumbnail = watermarked_thumbnail,
#                folder = "TESTING_Brian"
            )
            item.add_comment(comment)
            """

    print(msg)
    return count

def test_mil():
  
    tile_name  = 'Clatsop_County_cached_tiles'
    tile_layers = gis.content.search('title:' + tile_name,
                                    item_type = 'Map Image Layer')
    if not tile_layers or len(tile_layers) > 1:
        raise Exception("Can't find \"%s\"." % tile_name)
    tile_layer = tile_layers[0]
    print("tile layer", tile_layer)

    map_service = "https://delta.co.clatsop.or.us/server/rest/admin/services/Hosted/Clatsop_County_cached_tiles/MapServer"

    mil = MapImageLayerManager(url=map_service, gis=gis)
    d = mil.update_tiles(levels = [9])


if __name__ == "__main__":     

    print("Connecting to ", Config.PORTAL_URL)
    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD, 
            verify_cert=False)

    old_id = "38eb0a5b3ab1468f8465c76a01c6375f"
    new_id = "6868cf24b52c4230bc97dc9815d4caa5"

    milq = "id:" + new_id
    new_mil = gis.content.search(milq, outside_org=False)[0]
    print("New layer: \"%s\", type=\"%s\"" % (new_mil.title, new_mil.type))

    # For query definition, refer to http://bitly.com/1fJ8q31
    q = ""
    q = "title:Tester for Clatsop County Basemap, owner:bwilson@CLATSOP"
    count = update_maps(q, old_id, new_mil)

    print("----")
    print("Processed %d maps on this server." % count)

# That's all!
