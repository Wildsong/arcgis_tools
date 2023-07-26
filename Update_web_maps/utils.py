import os
import re
import json
from glob import glob
from regex import D
import xml.etree.ElementTree as ET
from rocketchat.api import RocketChatAPI as rc
from config import Config

myname="utils"
portalContentFolder = "\\\\cc-gis\\C$\\arcgis\\arcgisportal\\content\\items"
rocket = rc(settings={
    "username":Config.CHAT_USER,
    "password":Config.CHAT_PASSWORD,
    "domain":Config.CHAT_SERVER}) 

def sendMessage(message="your message here", recipient='bwilson'):
    id = "aGzdHtfSpEjknA9cN" # Brian
    #id = "zRKXNZdASMeMuKQLd" # GIS
    rocket.send_message(message=message, room_id=id)
    return

def load_json(fname:str) -> dict:
    # There are lots of empty JSON files in Esri land!!
    d = None
    if os.path.exists(fname) and os.stat(fname).st_size:
        with open(fname, 'r', encoding='latin-1') as fp:
            d = json.load(fp)
    return d

def load_info(fname:str) -> dict:
    d = dict()
    if os.stat(fname).st_size:
        with open(fname, 'r', encoding='utf8') as fp:
            d = ET.parse(fp)
    return d

def scrub_unicode(raw:str) -> str:
    """ Scrub out the stupid unicode characters from a string """

    # C2 is circumflex A
    # A0 is nonbreak space

    # This replaces actual honest to god unicode characters
    cleaner = raw.replace('\u00c2','').replace('\u00a0',' ')

    # This replaces the string representation of unicode, huh? Well yeah.
    # No really, I just repair what is broken without asking how it got that way.
    cleaned = cleaner.replace('\\u00c2','').replace('\\u00a0',' ')

    return cleaned 

def save_json(d:dict, fname:str, minify=True, repair=True) -> None:
    with open(fname, "w", encoding='utf-8') as fp:
        if minify:
            raw = json.dumps(d, indent=None, separators=(',', ':'))
        else:
            raw = json.dumps(d, indent=2)

        if repair:
            repaired = scrub_unicode(raw)
            
            if repaired == raw:
                print("  File did not contain any unicode.")
                
            fp.write(repaired)
        else:
            fp.write(raw)

    return

def findObjects(l:list, field:str, pattern:str):
    """
    List "l" is a list of dicts, 
    search item["field"] for a match with 'pattern',
    return a list of matches.
    """
    matches = list()
    for item in l:
        value = item[field]
        #print(inx, value) # uncomment if you are stumped
        mo =  re.search(pattern, value)
        if mo:
            matches.append(item)
    return matches

def findLayer(layers:list, field:str, pattern:str) -> int:
    """
    Search for a layer based on an attribute field.
    Return the index of the last matching layer or None.
    Throws an error if your expression matches more than one layer.
    """
    inx = 0
    found = None
    for item in layers:
        if item and field in item:
            value = item[field]
            #print(value)
            mo =  re.search(pattern, value)
            if mo:
                print(f"    [{inx}] \"{value}\".")
                if found:
                    raise Exception("FindLayers matched > 1.")
                found = inx
        inx += 1
    return found

def describeLayer(l:dict) -> None:
    print(f"id={l['id']} title=\"{l['title']}\"")
#    pprint(l)
    return

def findMaps(gis:object) -> list:
    """ 
    Return a list of all the maps
    """
    # There should never be >500 maps on this server,
    # if this comes back 500 then we got external content from Esri
    MAX = 500
    cm = gis.content
    q=""
    maps = cm.search(q, item_type="Web Map",
                     outside_org=False, max_items=MAX)
    count = len(maps)
    if count >= MAX:
        raise Exception("Too many maps. Did I find external content?")
    return maps

def describeMap(map:str) -> None:
    version = map['version']
    basemap = map['baseMap']
    print(f"version: {version}  basemap: \"{basemap['title']}\"")
    print("Operational layers:")
    for l in map['operationalLayers']:
        describeLayer(l)
    return


def getItemUrl(id):
    return Config.PORTAL_URL + '/home/item.html?id=' + id
    
# unit tests, if you please.

if __name__ == "__main__":

    raw = '{"title":"NAIP\u00a0\u00c21995\u00a0\u00c21m\u00a0BW\u00a0DOQ"}'
    repaired = scrub_unicode(raw)
    print(f"raw      \"{raw}\"")
    print(f"repaired \"{repaired}\"")
    print("Same?", raw==repaired)

    # Just read the file, which can be anywhere..
    map = load_json("test_map.json")
    assert map
    describeMap(map)
    print()

    save_json(map, "C:/temp/test_map_min.json")
    save_json(map, "C:/temp/test_map.json", minify=False)

    from arcgis.gis import GIS
    from pprint import pprint
    from config import Config
    try:
        gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
        print(f"Logged in as \"{gis.properties.user.username}\".")
    except Exception as e:
        print(f"Could not connect to portal. {e}")
        print("Make sure the environment variables are set correctly.")
        exit(-1)

    maps = findMaps(gis)
    print(f"Number of maps found: {len(maps)}")
    i = 0
    cm = gis.content
    for item in maps:
        print(f"Map: \"{i} {item.title}\" Owner: {item.owner} URL: {getItemUrl(item.id)}")
        jmap = item.get_data(True)
        ops = jmap["operationalLayers"]
        for op in ops:
            if 'itemId' in op:
                id = op['itemId']
                layer = cm.get(id)
                if not layer:
                    print(f"Broken? layer \"{op['title']}\" {getItemUrl(id)}")
#        pprint(jmap)
        i += 1

    #m = f"Greetings from a Python script called \"{myname}\"."
    #sendMessage(m)

#    # Access a single map via REST
#    ccMapTemplateId = '8220470e7d8141ada9917eb31a42c107'
#    portal_map = gis.content.get(ccMapTemplateId)
#    assert portal_map.type == 'Web Map'
#    #describeMap(portal_map) FIXME

    #print(maps)


    layers = map['operationalLayers']
    matches = findObjects(layers, "id", "Roads_")
    for item in matches:
        print(f'id:{item["id"]}')
    assert len(matches) == 1
    print()

    layers = map['operationalLayers']
    matches = findObjects(layers, "id", "Taxlots")
    for item in matches:
        print(f'id:{item["id"]}')
    assert len(matches) == 3
    print()

    i = findLayer(layers, "id", "^wms_53\d+")
    print(f"Layer title: {layers[i]['title']}")
    assert i == 1

    i = findLayer(layers, "id", "^wms_\d+")
    assert i == 7
    print(f"Layer title: {layers[i]['title']}")

    i = findLayer(layers, "id", "^nomatch")
    print("id=", i)
    assert i == None

