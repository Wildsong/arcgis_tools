""" 
    List the contents of our custom basemap gallery.
"""
import os
from arcgis.gis import GIS, Group
from config import Config
from pprint import pprint

# =============================================================

if __name__ == '__main__':
    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)

    cm = gis.content
    group = Group(gis, Config.BASEMAP_GALLERY_ID)

    # Find items in the source group

    groups = gis.groups.search("title:CC Basemaps")
    s = groups[0]
    d = groups[1]

    # Find everything that's in the source group.
    # Add the destination group to it.
    for item in s.content():
        #print(item)
        c=cm.advanced_search(query=f"title:\"{item['title']}\" owner:{item['owner']}", as_dict=False)
        thing = c['results'][0]
        #id = rval['id']
        #thing = cm.get(id)
        sw = thing.shared_with
        print(thing['title'], sw['groups'])
        thing.share(everyone=True, org=True, groups=groups)
        sw = thing.shared_with
        print('       ', sw['groups'])
        print()


    # Add the target group to the item

