import os
import arcpy

url="https://delta.co.clatsop.or.us/server/rest/services/Hosted/Astoria_Base_Map/MapServer",
map = "GIS Servers/portal on delta.co.clatsop.or.us (admin)/Hosted/Astoria_Base_Map.MapServer"
map = "GIS Servers/server on delta.co.clatsop.or.us (publisher)/Hosted/Astoria_Base_Map"
tpk="C:/temp/astoria_update.tpk"
tpk="misteltoe_update.tpkx"

if not os.path.exists(tpk):
    print("I need a package of tiles, my friend, and you have given me NOTHING.")
    exit(0)

try:
    arcpy.ImportMapServerCache_server(
        input_service=map,
        source_cache_type="TILE_PACKAGE",
        source_tile_package=tpk
    )
    print("I love it when you silently fail.")
except Exception as e:
    print("Cryptic error message:", e)

pass