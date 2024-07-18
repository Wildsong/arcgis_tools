"""
    Create an inventory of content in a geodatabase.
"""
import os
import json
import arcpy
from arcgis.gis import GIS
from config import Config

VERSION = '1.0'
path,exe = os.path.split(__file__)
myname = exe + ' ' + VERSION

def get_content(gdb):
    arcpy.env.workspace = gdb
    datasets = arcpy.ListDatasets("*")
    workspaces = arcpy.ListWorkspaces("*")
    featureclasses = arcpy.ListFeatureClasses("*")
    tables = arcpy.ListTables("*")
    versions = arcpy.ListVersions(gdb)
    return {
        "datasets": datasets,
        "workspaces": workspaces,
        "featureclasses": featureclasses,
        "tables": tables,
        "versions": versions,
    }

def get_portal_content(gis):
    q="NOT owner:esri_*"
    l = gis.content.search(q, max_items=5000, outside_org=False)
    d = dict()
    for item in l:
        if item.type in d:
            d[item.type].append(item)
        else:
            d[item.type] = [item]

if __name__ == "__main__":

    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
    pcd = get_portal_content(gis)
    
    # Generate a CSV of portal content
    for type in sorted(pcd):
        #print(type)
        for item in pcd[type]:
            print("\"%s\",\"%s\",\"%s\"" % (item.type, item.title, item.owner))


    gdb = "K:/webmaps/basemap/cc-thesql.sde"



    d = get_content(gdb)

    # What tables are versioned?
    # Who owns what?
    # What tables are published as registered data in Portal?

    # How many rows are in each table?
    # Is there metadata?

    fcd = list()
    for item in d["featureclasses"]:
        fcd.append(arcpy.Describe(item))

    for item in fcd:
        count = arcpy.management.GetCount(item.name)
        print(item.name, count)

# That's all!
