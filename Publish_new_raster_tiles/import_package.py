"""
    Import a tile package into an existing tile cache.

    https://developers.arcgis.com/rest/services-reference/import-tiles.htm
"""
import os
from os.path import splitext
from arcgis.gis import GIS
import arcgis.mapping as MAPPING
from config import Config
from utils import find_item_by_title

def import_tiles(gis, tpkx_item, map_url):

    m = MAPPING.MapImageLayerManager(map_url, gis)
    d = m.import_tiles(tpkx_item, merge=True, replace=True)

    # The dictionary returned is the description of the map.
    # I wonder how I find the error messages.
    # My idea is that it SHOULD be returning jobId so I could track it.

    return d


if __name__ == "__main__":
    from datetime import datetime
    import json
    datestamp = datetime.now().strftime("%m/%d/%Y %H:%M")

    test_package = "testfile.txt"
    test_tile_cache = "Astoria Base Map RASTER TILES"
    thumbnail = "map.png"

    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
    try:
        tpkx_item = find_item_by_title(gis, test_package)
        print(tpkx_item)
    except FileNotFoundError:
        print("Try running file_upload.py to create %s" % test_package)

    try:
        dest_item = find_item_by_title(gis, test_tile_cache)
        print(dest_item)
        dest_url = dest_item.url
    except FileNotFoundError:
        print("I can't find the map cache.")

    try:
        d = import_tiles(gis, tpkx_item, dest_url)
        print(json.dumps(d, sort_keys=True,indent=4))

    except Exception as e:
        print(e)
        
    exit(0)

