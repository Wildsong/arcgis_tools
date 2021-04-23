import os

def find_item_by_title(gis, title):
    q = title
    items = gis.content.search(q, outside_org=False)
    if len(items)==1:
        return items[0]

    # Matching more than one is just as bad as matching none.
    if len(items)>1:
        msg = "More than one match found."
    else:
        msg = "No matches found."
    raise FileNotFoundError(msg)

if __name__ == "__main__":
    from config import Config
    from arcgis.gis import GIS
    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)

    try:
        item = find_item_by_title(gis, "testfile.txt")
        print(item.id)
    except Exception as e:
        print(e)

    try:
        item = find_item_by_title(gis, "Astoria Base Map RASTER TILES")
        print(item.id)
    except Exception as e:
        print(e)

        