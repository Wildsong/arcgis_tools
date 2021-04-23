import os
import arcpy
from datetime import datetime
from glob import glob

from GTFSdownloader import GTFSdownloader
from GTFSimport import GTFSimport

from config import Config

def do_download(table, targetdir, aoi):
    print("---Download any missing or outdated files---")
    count = 0
    for d in table:
        agency = d['Transit service']
        assert(agency != '')

        if aoi and not (agency in aoi): continue
        count += 1

        updated = None
        updatestr = d['Last Modified']
        if updatestr :
            updated = datetime.strptime(updatestr, "%Y-%b-%d")
 
        expire = None
        expirestr = d['Valid Until']
        if expirestr:
            expire = datetime.strptime(expirestr, "%Y-%b-%d")

        url = d['Download Link']
        GTFSdownloader.download_zip(url, os.path.join(targetdir, agency), updated)
    return

def unzip_everything(sourcedir):
    print("---Unpacking as needed---")
    for source in glob(sourcedir + '*/*.zip', recursive=False):
        path,name = os.path.split(source)
        print("Unpacking \"%s\"" % name)
        GTFSdownloader.unpack(source)

def do_import(table, workspace, aoi=None, merged_prefix="all"):

    arcpy.env.overwriteOutput = True # I don't believe this is used anywhere.
    
    path,name = os.path.split(workspace)
    if not arcpy.Exists(workspace):
        arcpy.CreateFileGDB_management(out_folder_path=path, out_name=name)
    arcpy.env.workspace = workspace

    # NO DONT TRY TO USE FEATURE DATASETS NO NO THEY SUCK
#    gtfs_fd = 'gtfs_data'
#    gtfs_path = os.path.join(workspace, gtfs_fd)
#    if not arcpy.Exists(gtfs_path):
#        arcpy.CreateFeatureDataset_management(out_dataset_path=workspace, out_name=gtfs_fd,
#            spatial_reference=arcpy.SpatialReference(Config.spatial_ref_file))

    # NOTE if the downloads failed or could not be unpacked
    # then this stage presses on anyway. Missing files won't upset us.

    gtfs = GTFSimport(workspace)
    all_routes   = []
    all_stops    = []
    all_agencies = []
    count = 0
    routes_fm   = arcpy.FieldMappings()
    stops_fm    = arcpy.FieldMappings()
    agencies_fm = arcpy.FieldMappings()

    dataset_count = len(aoi) or len(table)
    for item in table:
        agency = item['Transit service']
        if aoi and not agency in aoi: continue
        count += 1
        print("IMPORTING %d/%d \"%s\"..." % (count, dataset_count, agency))
        fcs = gtfs.do_import(Config.sourcedir, agency)
        if fcs:
            all_routes.append(fcs[0])
            all_stops.append(fcs[1])
            all_agencies.append(fcs[2])

            routes_fm.addTable(fcs[0])
            stops_fm.addTable(fcs[1])
            agencies_fm.addTable(fcs[2])

    print("Merging everything to %s" % workspace)
    # https://pro.arcgis.com/en/pro-app/latest/tool-reference/data-management/merge.htm

    # reminder, output goes to arcgis workspace
    routes_fc    = merged_prefix + "_routes"
    stops_fc     = merged_prefix + "_stops"
    agency_table = merged_prefix + "_agencies"
    arcpy.management.Merge(all_routes, routes_fc, field_mappings=routes_fm, add_source='ADD_SOURCE_INFO')
    arcpy.management.Merge(all_stops, stops_fc, field_mappings=stops_fm, add_source='ADD_SOURCE_INFO')
    arcpy.management.Merge(all_agencies, agency_table, field_mappings=agencies_fm, add_source='ADD_SOURCE_INFO')

    # I regard this as a bug in the conversion process:
    # the feature class agency_id is a TEXT filed
    # the table agency_id is a LONG!!
    # Join the agency table to the feature class
    if arcpy.Exists(routes_fc) and arcpy.Exists(agency_table):
        try:
            arcpy.management.CalculateField(in_table=agency_table, field="agency_fkey", 
                expression="str(!agency_id!)", expression_type="PYTHON3", code_block="", field_type="TEXT")[0]
            arcpy.management.JoinField(in_data=routes_fc, in_field="agency_id", 
                join_table=agency_table, join_field="agency_fkey", 
                fields=[])[0]
        except Exception as e:
            print("Join failed, %s" % e)

if __name__ == '__main__':
    # Process EVERYTHING
    #aoi = None
    #prefix = "all"

    # Limited to this
    aoi = [
        "Benton Area Transit", 
        "Sunset Empire Transportation District - The Bus",
        "NorthWest POINT",
        "Lincoln County Transit"
    ]
    prefix = "Clatsop"

    # Pull this table from the main page of the GTFS site.

    table = GTFSdownloader.get_table(Config.site)
    #j = json.dumps(table, sort_keys=True, indent=4)
    #print(j)

    # Check expiration date on data and delete any that are past the "use by" date.

    do_download(table, Config.sourcedir, aoi)

    # not limited to aoi but it's fast so no biggie to unzip everything
    unzip_everything(Config.sourcedir)

    workspace = os.path.join(Config.sourcedir, "transit.gdb")

    do_import(table, workspace, aoi=aoi, merged_prefix=prefix)
    
    print("All done.")
