"""
    Create an inventory of content on an ArcGIS Portal


"""
import os
from collections import defaultdict
from arcgis.gis import GIS
from arcgis.gis.server.catalog import ServicesDirectory
from arcgis.mapping import WebMap
from config import Config

VERSION = '1.0'
path,exe = os.path.split(__file__)
myname = exe + ' ' + VERSION

exclude_esri = '-owner:esri -owner:esri_apps'

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
            dtype[item.type][item.id] = item
    return dtype


def generate_html(dtype):
    for itype,items in dtype.items():
        print('<h2>%s</h2>' % itype)
        count = 0
        print("<table>")
        for id in items.keys():
            count += 1
            item = items[id]

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

def inventory_services() -> list:
    """
        Returns a list of every service that relies on data living in the SQL database.
    """
    sd = ServicesDirectory(url=Config.SERVER_URL, username=Config.PORTAL_USER, password=Config.PORTAL_PASSWORD)
    print("Server folders:", sd.folders)

    # This takes 16 seconds in Jupyter Notebook and infinite time here.
    return sd.list()
 

def inventory_maps(gis, query=''):
    q = query + ' ' + exclude_esri
    list_of_maps = gis.content.search(q, item_type='web map', max_items=-1)
    print("Maps found %d" % len(list_of_maps))
    
    # Build a dictionary with each layer as the index
    # and a list of the maps that the layer participates in
    layer_dict = defaultdict(list)

    for item in list_of_maps:
        # Look up the layers.
        wm = WebMap(item)
        mapId = wm.item.id
        for l in wm.layers:
            try:
                layer_dict[l.itemId].append(mapId)
                pass
            except Exception as e:
                layer_dict[l.id].append(mapId)
                pass

    # Each item is indexed by a layer id and contains a list of the maps containing that id.
    print(layer_dict)

    # Now make another dictoinary that is indexed by type.
    dtype = defaultdict(dict)
    for item in list_of_maps: 
        dtype[item.type][item.id] = item

    print(dtype)


if __name__ == "__main__":

    # Weird stuff happens if these are not defined.
    assert(Config.PORTAL_URL)
    assert(Config.PORTAL_USER)
    assert(Config.PORTAL_PASSWORD)
    assert(Config.SERVER_URL)

    services = inventory_services()
    print("Services found %d" % len(services))
    for s in services:
        print(s)
        continue
 
    # See arcgis.gis.ContentManager
    # For query definition, refer to http://bitly.com/1fJ8q31
    #q = "title:Clatsop County Template"
    #q = "owner:bwilson@CLATSOP"
    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
    #inventory_maps(gis)


#    q = "NOT owner:esri_apps"
#    items = gis.content.search(q, outside_org=False, max_items=5000)
#    print("Items found %d" % len(items))
#    dtype = get_apps(items)
#    print(dtype)
#    generate_html(dtype)

# That's all!
