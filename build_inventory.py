"""
    Create an inventory of content on an ArcGIS Portal


"""
import os
from collections import defaultdict
from arcgis.gis import GIS
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


def inventory_services(gis) -> None:
    interesting_services = list()
    interesting_types = ['Map Service', 'Feature Service']
    urls = list()

    myservers = gis.admin.servers.list()
    for f in myservers[0].services.folders:
        services = myservers[0].services.list(folder=f)
        print("Checking folder=\"%s\"; %d services." % (f, len(services)))
        for s in services:
            properties = s.iteminformation.properties
            try:
                if properties['type'] in interesting_types:
                    interesting_services.append(s)
                else:
                    print(properties['title'], ':', properties['type'])
            except KeyError:
                if 'GPServer' in s.url:
                    continue
                if 'GeometryServer' in s.url:
                    continue
                if 'VectorTileServer' in s.url:
                    continue
                if 'ImageServer' in s.url:
                    continue
                urls.append(s.url)

    # These did not have proprties,
    # look like mostly Hosted
    #print(urls)

    for s in interesting_services:
        properties = s.iteminformation.properties
        if properties['type'] == 'Map Service':
            print(s.url)
            continue
        else:
            print(properties)

if __name__ == "__main__":

    # Weird stuff happens if these are not defined.
    assert(Config.PORTAL_URL)
    assert(Config.PORTAL_USER)
    assert(Config.PORTAL_PASSWORD)
    assert(Config.SERVER_URL)

    # See arcgis.gis.ContentManager
    # For query definition, refer to http://bitly.com/1fJ8q31
    #q = "title:Clatsop County Template"
    #q = "owner:bwilson@CLATSOP"
    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
    #inventory_maps(gis)

    types = [
        'AppBuilder Extension', 
        'Application', 
        'Desktop Application','Desktop Application Template', 
        'Site Application', 
        'Document Link', 
        'Administrative Report',
        'Form', 'Site Page',
        'CSV', 'Microsoft Excel', 'Microsoft Word', 'PDF', 'KML',
        'Map Area', 
        'WMS', 'WMTS',
        'Code Attachment', 'Code Sample',
        'Geoprocessing Service',
        'Dashboard', 'StoryMap', 'StoryMap Theme',
        'Web Experience', 'Web Mapping Application', 
        'Image', 
        'Geometry Service',
        'Feature Service',
        'Shapefile',  
        'Layer Package', 'Tile Package', 
        'SQLite Geodatabase',
        'Vector Tile Service', 'Vector Tile Package', 
        'Web Scene', 'Service Definition', 'Map Service', 
        'Web Map', ]
    cm = gis.content

    q = 'title:EGDB_surveys -owner:esri -owner:esri_apps -owner:esri_nav'

    items = cm.search(q, item_type='Feature Service', max_items=-1)
    print("Feature Services", len(items))
    for item in items:
        print(item.title, item.type)
        try:
            for l in item.layers:
                print(l)
                continue
        except Exception as e:
            pass

    items = cm.search(q, item_type='Map Service', max_items=-1)
    print("Map Services", len(items))
    for item in items:
        print(item.title)
        for layer in item.layers:
            print(layer, layer.source)


    inventory_services(gis)

    print("That's all!")

#    q = "NOT owner:esri_apps"
#    items = gis.content.search(q, outside_org=False, max_items=5000)
#    print("Items found %d" % len(items))
#    dtype = get_apps(items)
#    print(dtype)
#    generate_html(dtype)

# That's all!
