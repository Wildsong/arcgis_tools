import os
import json
from arcgis.gis import GIS
from config import Config
from file_upload import upload
from import_package import import_tiles
from utils import find_item_by_title

from datetime import datetime
datestamp = datetime.now().strftime("%m/%d/%Y %H:%M")

packagepathname = "C:/temp/astoria_update.tpkx"
folder = "TESTING_Brian" # Storage for the package file on the server
thumbnail = "tiles.png"
cache = "Astoria Base Map RASTER TILES"

type = "Compact Tile Package"

def tile_upload(gis):
    item = None
    try:
        item = upload(gis, packagepathname, folder, type, thumbnail=thumbnail, 
            description="File uploaded %s" % datestamp, snippet="Different colors")
        print("Your upload is here: %s/home/item.html?id=%s" % (Config.PORTAL_URL, item.id))
        
    except Exception as e:
        print(e)
    return item

def tile_import(gis, pkg_item):
    dest_url = ''
    try:
        dest_item = find_item_by_title(gis, cache)
        print(dest_item)
        dest_url = dest_item.url
    except FileNotFoundError:
        print("I can't find the map cache.")

    d = import_tiles(gis, pkg_item, dest_url)
    print(json.dumps(d, sort_keys=True,indent=4))

gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)

pkg_item = tile_upload(gis)
tile_import(gis, pkg_item)

exit(0)