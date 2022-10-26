import os
import re
import json


def load_json(fname:str) -> dict:
    with open(fname, "r") as fp:
        d = json.load(fp)
    return d

def save_json(d:dict, fname:str, minify=True) -> None:
    with open(fname, "w") as fp:
        i = 2
        if minify:
            i = 0
        json.dump(d, fp, indent=i)
    return

def findObject(l:list, field:str, pattern:str):
    """
    List "l" is a list of dicts, 
    search item "name" for a match with 'pattern',
    return a list of matches.
    """
    matches = list()
    inx = 0
    for item in l:
        value = item[field]
        #print(inx, value) # uncomment if you are stumped
        mo =  re.search(pattern, value)
        if mo:
            matches.append(item)
        inx += 1
    return matches

def findLayer(map:dict, field:str, pattern:str) -> dict:
    """
    Search for a layer in a map based on its title.
    Return the index of the last matching layer or None.
    """
    matches = list()
    found = None
    inx = 0
    for item in map['operationalLayers']:
        if field in item: 
            value = item[field]
            #print(inx, value) # uncomment if you are stumped
            mo =  re.search(pattern, value)
            if mo:
                matches.append(item)
                found = inx
                print(f"Found {inx} \"{value}\".")
        inx += 1
    return found

def describeLayer(l:dict) -> None:
    print(f"id={l['id']} title=\"{l['title']}\"")
#    pprint(l)
    return

def describeMap(map:str) -> None:
    version = map['version']
    basemap = map['baseMap']
    print(f"version: {version}  basemap: \"{basemap['title']}\"")
    print("Operational layers:")
    for l in map['operationalLayers']:
        describeLayer(l)
    return


# unit tests, if you please.

if __name__ == "__main__":

    map = load_json("test_map.json")
    assert map
    describeMap(map)
    print()

    save_json(map, "C:/temp/test_map_min.json")
    save_json(map, "C:/temp/test_map.json", minify=False)

    layers = map['operationalLayers']
    matches = findObject(layers, "id", "Roads_")
    for item in matches:
        print(f'id:{item["id"]}')
    assert len(matches) == 1
    print()

    layers = map['operationalLayers']
    matches = findObject(layers, "id", "Taxlots")
    for item in matches:
        print(f'id:{item["id"]}')
    assert len(matches) == 3
    print()

    i = findLayer(map, "id", "^wms_53\d+")
    print(f"Layer title: {layers[i]['title']}")
    assert i == 1

    i = findLayer(map, "id", "^wms_\d+")
    assert i == 7
    print(f"Layer title: {layers[i]['title']}")

    i = findLayer(map, "id", "^nomatch")
    print("id=", i)
    assert i == None