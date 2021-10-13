"""
    List the apps on this server
"""
import os

from arcgis.gis import GIS
from arcgis.gis import server as SERVER

from config import Config

VERSION = '1.0'
path,exe = os.path.split(__file__)
myname = exe + ' ' + VERSION

if __name__ == "__main__":

    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD, verify_cert=False)

    # See arcgis.gis.ContentManager
    # For query definition, refer to http://bitly.com/1fJ8q31
    #q = "title:Clatsop County Template"
    #q = "owner:bwilson@CLATSOP"

    # NB, the outside_org options fails.
    q = "NOT (owner:esri_nav OR owner:esri_apps OR owner:esri)"
    items = gis.content.search(q, outside_org=False, max_items=5000)

#    print("Items found %d" % len(items))

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
            dtype[item.type][item.title] = item

    for itype,items in dtype.items():
        print('<h2>%s</h2>' % itype)
        count = 0
        for title in items.keys():
            count += 1
            item = items[title]

            url = item.url
            if url:
                if url[0:2] == '//':
                    url = "https:" + url
                url = '<a href="%s" target="_app">URL</a> ' % url
            else:
                url = 'no url'
            
            homepage = '<a href="%s" target="_details">item details</a> ' % item.homepage

            print('<p>')
            print('{0:3n},{2},{3},"{1}"<br />'.format(count, item.title, item.owner, item.access))
            print(homepage, ' ', url, '<br />')
            print('keywords:', ', '.join(item.typeKeywords))
            print('<br />')
            print('</p>')
            print("<hr>")
            print()

#    print(dtype)

# That's all!
