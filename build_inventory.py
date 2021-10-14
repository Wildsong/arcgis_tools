"""
    Create an inventory of content on an ArcGIS Portal
"""
import os

from arcgis.gis import GIS
from arcgis.mapping import WebMap
#from arcgis.gis import server as SERVER
from config import Config

VERSION = '1.0'
path,exe = os.path.split(__file__)
myname = exe + ' ' + VERSION

def get_apps(items):
    dtype = {} # A dictionary of all item types
    applications = [
        'Application',
        'Code Attachment',
        'Dashboard',
        'Desktop Application Template',
        'Desktop Application',
        'Web Experience', 
        'Web Mapping Application',
    ]
    for item in items: 
        if item.type in applications:
    #        if not ('zhunt' in item.owner or "@CLATSOP" in item.owner):
            if not item.type in dtype:
                dtype[item.type] = {}
            dtype[item.type][item.title] = item
    return dtype

def get_maps(items):
    dtype = {} # A dictionary of all item types
    for item in items: 
        if not item.type in dtype:
            dtype[item.type] = {}
        dtype[item.type][item.title] = item
    return dtype

def generate_html(dtype):
    for itype,items in dtype.items():
        print('<h2>%s</h2>' % itype)
        count = 0
        print("<table>")
        for title in items.keys():
            count += 1
            item = items[title]

            url = item.url
            if url:
                if url[0:2] == '//':
                    url = "https:" + url
                url = '<a href="%s" target="_app">URL</a> ' % url
            else:
                url = 'no url'
            
            homepage = '<a href="%s" target="_details">%s</a>' % (item.homepage, str(item.title))

            print('<tr><td>{0:3n}</td><td>{1}</td><td>{2}</td><td>{3}</td></tr>'.format(count, homepage, item.owner, item.access))
#            keywords = str(', '.join(item.typeKeywords))
#            print('keywords:', keywords)
        print('</table>')
        print()

    return

if __name__ == "__main__":

    # Weird stuff happens if these are not defined.
    assert(Config.PORTAL_URL)
    assert(Config.PORTAL_USER)
    assert(Config.PORTAL_PASSWORD)

    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)

    # See arcgis.gis.ContentManager
    # For query definition, refer to http://bitly.com/1fJ8q31
    #q = "title:Clatsop County Template"
    #q = "owner:bwilson@CLATSOP"

    q = '*'
    list_of_maps = gis.content.search(q, item_type='web map', outside_org=False, max_items=5000)
    print("Maps found %d" % len(list_of_maps))
    
    # Build a dictionary with each layer as the index
    # and a list of the maps that the layer participates in
    layer_dict = {}

    for item in list_of_maps:
        # Look up the layers.
        wm = WebMap(item)
        mapId = wm.item.id
        for l in wm.layers:
            try:
                layerId = l.itemId
#                print(itemId, l.layerType, l.title)
                if layerId not in layer_dict:
                    layer_dict[layerId] = []
                layer_dict[layerId].append(mapId)
                pass
            except Exception as e:
                #print(e)
#                print('??', l.id, l.layerType, l.title)
                layerId = l.id
                if layerId not in layer_dict:
                    layer_dict[layerId] = []
                layer_dict[layerId].append(mapId)
                pass

    print(layer_dict)

    # figure out which maps have these layers in them
    # broken layers
    unlabeled_tiles = 'ad55cfca21034537890cae6a2a9e61cf'
    labels = '9ea1b5b29a534549ade3e4f43630333f'
    labeled_tiles = '01d7aec6e83e43f190bb543b5860647d'
    baddies = [ unlabeled_tiles, labeled_tiles, labels ]

    for layerId in baddies:
        if layerId in layer_dict:
            print(layerId, "-----> ", layer_dict[layerId])

    dtype = get_maps(list_of_maps)
#    print(dtype)

    generate_html(dtype)

    q = "NOT owner:esri_apps"
    items = gis.content.search(q, outside_org=False, max_items=5000)
    print("Items found %d" % len(items))
    dtype = get_apps(items)
#    print(dtype)
    generate_html(dtype)

# That's all!
