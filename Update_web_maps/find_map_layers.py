#
#  Search our server finding maps and then look for maps that have layers we're interested in.
#
import os
from collections import defaultdict
from xml.dom.minidom import Attr
import requests

from arcgis.gis import GIS
from arcgis.gis import server as SERVER
from arcgis.mapping import WebMap as WEBMAP
from arcgis.gis import Item as ITEM

from config import Config

VERSION = '1.0'
path,exe = os.path.split(__file__)
myname = exe + ' ' + VERSION

def find_interesting_maps(gis, q="", interesting_layer_titles=list(), interesting_layer_id=None) -> list:
    """
        Search for all maps matching a query
        and optionally with a layer matching one of the 'interesting_layer_titles' or 'interesting_layer_id'.
        Return a list of the maps.
    """
    # There should never be >500 maps on this server,
    # if this comes back 500 then we got external content from Esri!!
    MAX = 500
    cm = gis.content
    maps = cm.search(q, item_type="Web Map",
                     outside_org=False, max_items=MAX)
    print("Number of maps matching query '%s': %d" % (q, len(maps)))

    interesting_maps = list()

    broken_layers = defaultdict(list)
    deprecated_layers = defaultdict(list)
    basemaps = defaultdict(list)
    totalmaps = len(maps)
    thismap = 0
    for map in maps:
        thismap += 1 
        print("Examining %d of %d \"%s\"" % (thismap, totalmaps, map.title))

        try:
            web_map = WEBMAP(map)
        except Exception as e:
            print("This map is total broken!", map, e)
            continue

        for basemap in web_map.basemap.baseMapLayers:
            try:
                id = basemap.itemId
            except AttributeError:
                # External map, like National Geographic or Esri Grey.
                id = basemap.id
            basemaps[id].append(basemap)
            if interesting_layer_id and id == interesting_layer_id:
                interesting_maps.append(map.id)

        #print("Map: %s \"%s\"" % (map.id, map.title))
        try:
            layers = web_map.layers
        except KeyError:
            print("ERROR: No layers?", type(web_map))
            continue

        msg = ''
        for layer in layers:
            try:
                ttl = layer.title
                pass
            except AttributeError:
                ttl = 'untitled layer'

            try:
                t = layer.layerType
            except AttributeError:
                t = "???"          

            try:
                id = layer.itemId
            except AttributeError:
                id = layer.id
            layer_info = cm.get(id)

            url = None
            if t == 'VectorTileLayer':
                try:
                    url = layer_info.homepage
                except AttributeError as e:
                    print("no layerinfo on this VTL!!", map.title, ttl)
            else:
                url = layer.url

            # Can I open this layer? (Does it exist and can I read it)
            if url:
                try:
                    response = requests.get(url)
                except Exception as e:
                    print(e, map, ttl, url)

                if response.status_code != 200:
                    msg += "Broken layer (response %d). type=%s(%s) %s\n" % (response.status_code, t, id, ttl)
                    broken_layers[id].append(map.id)
            else:
                if not layer_info:
                    msg += "Broken layer. type=%s(%s) %s\n" % (t, id, ttl)
                    broken_layers[id].append(map.id)
                    pass
                else:
                    # Is this layer deprecated??
                    # { "" | "org_authoritative" | "deprecated" }
                    if layer_info.content_status == 'deprecated':
                        deprecated_layers[id].append(map.id)

            if ttl in interesting_layer_titles:
                interesting_maps.append(map.id)
        #                msg += "%s: \"%s\" (%s)" % (id, ttl, t)

            if interesting_layer_id and id == interesting_layer_id:
                interesting_maps.append(map.id)
        #                msg += "%s(%s) %s: \"%s\" (%s)\n" % (id, ttl, t)
                pass


        if msg:
            print()
            print("%s(%s)" % (map.title, map.id))
            print(msg)

    print("I saw a total of %d maps and %d basemaps." % (len(maps), len(basemaps)))
    print("I saw %d broken layer(s) in %d map(s)." % (len(broken_layers), len(maps)))
    print("There are %d deprecated layer(s) in use." % len(deprecated_layers))

  #  for (basemap, maps) in basemaps.items():
  #      print("basemap %s is in %d maps." % (basemap, len(maps)))

    return interesting_maps


if __name__ == '__main__':
    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER,
              Config.PORTAL_PASSWORD, verify_cert=False)

    # Find maps with the layer we're interested in -- search by ID or title or something else

    # For query definition, refer to http://bitly.com/1fJ8q31
    q = ""
#    q = "title:A&T map"
    #q = "id:ba5d38a16a4841d9a85eec770fa79040" # Public Works road map
    #q = "title:Clatsop County Template"
    #q = "owner:bwilson@CLATSOP"
    title = None

    id = None
#    id = "4eeb630bba2d44598f8af15c44621fd7" # The current empty basemap
#    id = "VectorTile_7105" # PLSS
#    id = "8ac30154d2f44822bbe23a78f496ccdb" # broken Roads layer
    interesting_maps = []

#    id = "be645e399add4c4db2bbe36ba754bb30" # Roads layer that I broke on 10/10/22

#    id = "" # broken Roads layer
#    id = "8ac30154d2f44822bbe23a78f496ccdb" # broken Roads layer

    # Tsunami Evacuation Zones (KH edition)
    # MIL and layer 0
    id = "fcc3492b35b648bf8750ea69a6163022"

    interesting_maps += find_interesting_maps(gis, q=q, 
#        interesting_layer_titles=['County Bridges', 'Waterway Inventory'], 
        interesting_layer_id=id)

    """
    id = "8a244c8ba3f4416e842971fafdb316f4" # DOGAMI SLIDO4
    interesting_maps += find_interesting_maps(gis, q=q, 
#        interesting_layer_titles=['County Bridges', 'Waterway Inventory'], 
        interesting_layer_id=id)

    id = "4de2046661b0469aa3b14216ff6f9f01"  # DOGAMI Landslide Susceptibility
    interesting_maps += find_interesting_maps(gis, q=q,
#        interesting_layer_titles=['County Bridges', 'Waterway Inventory'], 
        interesting_layer_id=id)
    """
    
    print("%d matching maps." % len(interesting_maps))
    cm = gis.content
    print("maps = [")
    for id in interesting_maps:
        map = cm.get(id)
        print('    ("%s", "%s"),' % (map.id, map.title))
    print("]")

    # Via API -- Can I read the JSON file, edit it, and write it back to server?

# That's all!

# new Roads = 17209289b3f642ebaa545ef3ab5a5f66
# cc webmaps f84321f3545643adaadf889ce70dc73e
#maps = [
#    ("ba5d38a16a4841d9a85eec770fa79040", "Clatsop County Public Works Road Map - Web Map"),
#    ("3858169ab451482c9460d897e05e696c", "A&T map"),
#    ("bb5debcf14db4c48bbd4c54fc0fc207f", "Planning Map"),
#]