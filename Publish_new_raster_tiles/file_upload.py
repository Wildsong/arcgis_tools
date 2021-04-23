"""
    Upload a file from the desktop to the server. 
    Return its ID.
"""
import os
from os.path import splitext
from arcgis.gis import GIS
from config import Config
from utils import find_item_by_title


def upload(gis, source, destination, type, thumbnail=None, description="", snippet=""):
    id = None
    (sourcepath, sourcename) = os.path.split(source)
    (sourcetitle, sourceextn) = os.path.splitext(sourcename)

    id = None # Preserve id if we're overwriting existing content.

    overwrite = True
    if overwrite:
        try: 
            match = find_item_by_title(gis, sourcename)
            id = match.id
            print("Exists, overwriting. Old id was %s" % id)
            match.delete()
        except FileNotFoundError:
            print("I don't need to overwrite.")

    item = gis.content.add({

        # Esri best practices suggests filling in these fields
            "title": sourcename,
            "type": type,
            "typeKeywords": "Data", # See https://developers.arcgis.com/rest/users-groups-and-items/items-and-item-types.htm
            "tags": "Clatsop County",
            "snippet": snippet, # shows up on the item details page, to the right of the thumbnail
            "description": description,

            "filename": sourcename,
            #"extent": "xmin,ymin,xmax,ymax", 
            "overwrite": True # THIS OPTION DOES NOT WORK
        }, 
        data=source, # path or URL
        thumbnail=thumbnail, #path or URL
        item_id=id, # in my experience this does not work, it will ignore this and assign a new ID
        folder=destination
    )

    return item


if __name__ == "__main__":
    from datetime import datetime
    datestamp = datetime.now().strftime("%m/%d/%Y %H:%M")
    testfile = "testfile.txt"
    testfolder = "TESTING_Brian"
    thumbnail = "tiles.png"

    # Stupidly Esri does no type checking on uploads
    # also stupidly will not allow transfer of type = "Text Document"
    # also requires a complex string as a value here from some dictionary somewhere
    # So I can for example upload a TXT file and lie and tell it it's a tile package.
    type = "Compact Tile Package"

    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)

    try:
        item = upload(gis, testfile, testfolder, type, thumbnail=thumbnail, description="File uploaded %s" % datestamp, snippet="Just a test")

        # Print a hyperlink to the "item details" page. How cool is that?
        print("Your upload is here: %s/home/item.html?id=%s" % (Config.PORTAL_URL, item.id))

    except Exception as e:
        print(e)
        
    exit(0)



