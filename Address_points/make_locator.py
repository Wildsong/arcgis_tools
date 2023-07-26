"""
Creates a locator
"""
import os
import pprint
import arcpy
from arcgis.gis import GIS
from arcgis.gis import Item as ITEM
from config import Config

from datetime import datetime
now = datetime.now()
datestamp = now.strftime("%Y-%m-%d %H:%M")  # for comments
datestring = now.strftime("%Y%m%d_%H%M")  # for filenames

VERSION = '1.0'
path, exe = os.path.split(__file__)
myname = exe + ' ' + VERSION


def create_locator(locator_file):
    """ Generates output in workspace """

    msg = "Created locator \"%s\"." % locator_file
    if arcpy.Exists(locator_file):
        msg = "Overwrote locator \"%s\"." % locator_file

    # IMPORT ALL THE DATA -- always pull the data, it needs to be fresh
    # ONLY pull attributes we need, it just burns up extra memory in the locator to copy everything

    thesql = "K:\\e911\\cc-thesql.sde\\"
    Clatsop_DBO_roads = thesql + "Clatsop.DBO.roads"
    Clatsop_DBO_taxlot_accounts = thesql + "Clatsop.DBO.taxlot_accounts"
    Clatsop_DBO_address_points = thesql + "Clatsop.DBO.address_points"
    Clatsop_DBO_points_of_interest = thesql + "Clatsop.DBO.points_of_interest"

    # Select a version!!

    workspace = arcpy.env.workspace

    print("Loading roads into workspace")
    roads = arcpy.conversion.FeatureClassToFeatureClass(in_features=Clatsop_DBO_roads, out_path=workspace, out_name="roads", where_clause="",
            field_mapping="ToRight \"ToRight\" true true false 4 Long 0 10,First,#,Clatsop.DBO.roads,ToRight,-1,-1;FromRight \"FromRight\" true true false 4 Long 0 10,First,#,Clatsop.DBO.roads,FromRight,-1,-1;Street \"Street\" true true false 72 Text 0 0,First,#,Clatsop.DBO.roads,Street,0,72;FunctionalClass \"FunctionalClass\" true true false 15 Text 0 0,First,#,Clatsop.DBO.roads,FunctionalClass,0,15;FunClassD \"FunctionalClassD\" true true false 254 Text 0 0,First,#,Clatsop.DBO.roads,FunClassD,0,254;FunClassN \"FunctionalClassN\" true true false 2 Short 0 5,First,#,Clatsop.DBO.roads,FunClassN,-1,-1;FunClassM \"FunctionalClassM\" true true false 254 Text 0 0,First,#,Clatsop.DBO.roads,FunClassM,0,254;City \"City\" true true false 12 Text 0 0,First,#,Clatsop.DBO.roads,City,0,12;Name \"Name\" true true false 30 Text 0 0,First,#,Clatsop.DBO.roads,Name,0,30;FromAddressRight \"FromAddressRight\" true true false 5 Text 0 0,First,#,Clatsop.DBO.roads,FromAddressRight,0,5;ToAddressLeft \"ToAddressLeft\" true true false 5 Text 0 0,First,#,Clatsop.DBO.roads,ToAddressLeft,0,5;FromLeft \"FromLeft\" true true false 4 Long 0 10,First,#,Clatsop.DBO.roads,FromLeft,-1,-1;ToAddressRight \"ToAddressRight\" true true false 5 Text 0 0,First,#,Clatsop.DBO.roads,ToAddressRight,0,5;Owner \"Owner\" true true false 12 Text 0 0,First,#,Clatsop.DBO.roads,Owner,0,12;FromAddressLeft \"FromAddressLeft\" true true false 5 Text 0 0,First,#,Clatsop.DBO.roads,FromAddressLeft,0,5;Type \"Type\" true true false 2 Text 0 0,First,#,Clatsop.DBO.roads,Type,0,2;ToLeft \"ToLeft\" true true false 4 Long 0 10,First,#,Clatsop.DBO.roads,ToLeft,-1,-1;StreetName \"StreetName\" true true false 38 Text 0 0,First,#,Clatsop.DBO.roads,StreetName,0,38", config_keyword="")[0]

    print("Loading parcels into workspace")
    parcels = arcpy.conversion.FeatureClassToFeatureClass(in_features=Clatsop_DBO_taxlot_accounts, out_path=workspace, out_name="parcels", where_clause="",
            field_mapping="MapTaxlot \"MapTaxlot\" true true false 25 Text 0 0,First,#,K:\\ORMAP_CONVERSION\\Clatsop_WinAuth.sde\\Clatsop.DBO.taxlot_accounts,MapTaxlot,0,25;SITUS_ADDR \"SITUS_ADDR\" true true false 40 Text 0 0,First,#,K:\\ORMAP_CONVERSION\\Clatsop_WinAuth.sde\\Clatsop.DBO.taxlot_accounts,SITUS_ADDR,0,40;SITUS_CITY \"SITUS_CITY\" true true false 20 Text 0 0,First,#,K:\\ORMAP_CONVERSION\\Clatsop_WinAuth.sde\\Clatsop.DBO.taxlot_accounts,SITUS_CITY,0,20", config_keyword="")[0]

    print("Loading address points into workspace")
    address_points = arcpy.conversion.FeatureClassToFeatureClass(in_features=Clatsop_DBO_address_points, out_path=workspace, out_name="address_points", where_clause="",
            field_mapping="gcLgFlAdr \"Full Address\" true true false 62 Text 0 0,First,#,Clatsop.DBO.address_points,gcLgFlAdr,0,62;gcLgFlName \"Street Name\" true true false 50 Text 0 0,First,#,Clatsop.DBO.address_points,gcLgFlName,0,50;gcFullName \"Full Street Name\" true true false 56 Text 0 0,First,#,Clatsop.DBO.address_points,gcFullName,0,56;addNum \"House Number\" true true false 10 Text 0 0,First,#,Clatsop.DBO.address_points,addNum,0,10;addNumSuf \"Address Number Suffix\" true true false 6 Text 0 0,First,#,Clatsop.DBO.address_points,addNumSuf,0,6;preMod \"Prefix Modifier\" true true false 18 Text 0 0,First,#,Clatsop.DBO.address_points,preMod,0,18;preDir \"Prefix Direction\" true true false 18 Text 0 0,First,#,Clatsop.DBO.address_points,preDir,0,18;preType \"Prefix type\" true true false 14 Text 0 0,First,#,Clatsop.DBO.address_points,preType,0,14;preTypeSep \"Prefix Type Separator\" true true false 6 Text 0 0,First,#,Clatsop.DBO.address_points,preTypeSep,0,6;strName \"Street\" true true false 50 Text 0 0,First,#,Clatsop.DBO.address_points,strName,0,50;postType \"Postfix Type\" true true false 18 Text 0 0,First,#,Clatsop.DBO.address_points,postType,0,18;postDir \"Postfix Direction\" true true false 10 Text 0 0,First,#,Clatsop.DBO.address_points,postDir,0,10;postMod \"Postfix Modifier\" true true false 16 Text 0 0,First,#,Clatsop.DBO.address_points,postMod,0,16;unit \"Unit\" true true false 22 Text 0 0,First,#,Clatsop.DBO.address_points,unit,0,22;unitDesc \"Unit Description\" true true false 18 Text 0 0,First,#,Clatsop.DBO.address_points,unitDesc,0,18;unitNo \"Unit Number\" true true false 10 Text 0 0,First,#,Clatsop.DBO.address_points,unitNo,0,10;incMuni \"City\" true true false 28 Text 0 0,First,#,Clatsop.DBO.address_points,incMuni,0,28;msagComm \"MSAG Community\" true true false 24 Text 0 0,First,#,Clatsop.DBO.address_points,msagComm,0,24;postComm \"Postal Community\" true true false 26 Text 0 0,First,#,Clatsop.DBO.address_points,postComm,0,26;zipCode \"ZIP\" true true false 10 Text 0 0,First,#,Clatsop.DBO.address_points,zipCode,0,10;long \"Longitude\" true true false 8 Double 8 38,First,#,Clatsop.DBO.address_points,long,-1,-1;lat \"Latitude\" true true false 8 Double 8 38,First,#,Clatsop.DBO.address_points,lat,-1,-1;srcLastEdt \"Edit Date\" true true false 8 Date 0 0,First,#,Clatsop.DBO.address_points,srcLastEdt,-1,-1;EditDate \"Upload Date\" true true false 8 Date 0 0,First,#,Clatsop.DBO.address_points,EditDate,-1,-1;gcConfiden \"Confidence\" true true false 4 Long 0 10,First,#,Clatsop.DBO.address_points,gcConfiden,-1,-1;GlobalID_2 \"GUID\" true true false 72 Text 0 0,First,#,Clatsop.DBO.address_points,GlobalID_2,0,72;taxlotID \"Taxlot ID\" true true false 28 Text 0 0,First,#,Clatsop.DBO.address_points,taxlotID,0,28", config_keyword="")[0]

    print("Loading points of interest into workspace")
    POI = arcpy.conversion.FeatureClassToFeatureClass(in_features=Clatsop_DBO_points_of_interest, out_path=workspace, out_name="POI", where_clause="",
            field_mapping="name \"name\" true true false 160 Text 0 0,First,#,Clatsop.DBO.points_of_interest,name,0,160;category \"category\" true true false 38 Text 0 0,First,#,Clatsop.DBO.points_of_interest,category,0,38;subcategory \"subcategory\" true true false 28 Text 0 0,First,#,Clatsop.DBO.points_of_interest,subcategory,0,28;locale \"locale\" true true false 24 Text 0 0,First,#,Clatsop.DBO.points_of_interest,locale,0,24;FEATURE_ID \"id\" true true false 8 Double 8 38,First,#,Clatsop.DBO.points_of_interest,FEATURE_ID,-1,-1", config_keyword="")[0]

    print("Creating locator definition.")
    try:
        arcpy.geocoding.CreateLocator(country_code="USA",
            primary_reference_data=[[roads, "StreetAddress"], [
                parcels, "Parcel"], [address_points, "PointAddress"], [POI, "POI"]
            ],
            field_mapping=[
                "StreetAddress.HOUSE_NUMBER_FROM_LEFT roads.FromLeft", "StreetAddress.HOUSE_NUMBER_TO_LEFT roads.ToLeft", "StreetAddress.HOUSE_NUMBER_FROM_RIGHT roads.FromRight", "StreetAddress.HOUSE_NUMBER_TO_RIGHT roads.ToRight", "StreetAddress.STREET_NAME roads.Street", "StreetAddress.FULL_STREET_NAME roads.StreetName",
                "Parcel.PARCEL_NAME parcels.MapTaxlot", "Parcel.FULL_STREET_NAME parcels.SITUS_ADDR", "Parcel.CITY parcels.SITUS_CITY",
                "PointAddress.FEATURE_ID address_points.GlobalID_2", "PointAddress.HOUSE_NUMBER address_points.addNum", "PointAddress.STREET_PREFIX_DIR address_points.preDir", "PointAddress.STREET_PREFIX_TYPE address_points.preType", "PointAddress.STREET_NAME address_points.gcLgFlName", "PointAddress.FULL_STREET_NAME address_points.gcFullName", "PointAddress.SUB_ADDRESS_UNIT address_points.unit", "PointAddress.CITY address_points.incMuni", "PointAddress.POSTAL address_points.zipCode",
                "POI.FEATURE_ID POI.FEATURE_ID", "POI.PLACE_NAME POI.name", "POI.CATEGORY POI.category", "POI.SUBCATEGORY POI.subcategory"
            ],
            out_locator=locator_file,
            language_code="ENG", alternatename_tables=[], alternate_field_mapping=[], custom_output_fields=[], precision_type="GLOBAL_HIGH"
        )
    except Exception as e:
        print(e)

    return

def publish_locator(locator_file, service_name):
    """
    This will either overwrite or create a new locator service.
    """
    portal = arcpy.GetActivePortalURL()
    arcpy.SignInToPortal(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)

    sddraft_file = "C:\\Temp\locator.sddraft"
    sd_file = "C:\\Temp\\locator.sd"

    folderName = "Locator_services"
    summary = "Locator based on E911 address points, points of interest, parcels, and roads"
    tags = "Clatsop County, address, locator, geocode"
    
    # The URL of the federated server you are publishing to
    server = Config.SERVER_URL + "/rest/services/"

    print("Analyzing...")
    analyze_messages = arcpy.CreateGeocodeSDDraft(
        locator_file, sddraft_file, 
        service_name,
        copy_data_to_server=True,
        folder_name = folderName,
        summary=summary, tags=tags, max_result_size=10,
        max_batch_size=500, suggested_batch_size=150,
        overwrite_existing_service=True
    )

    if analyze_messages['warnings'] != {}:
        print("Warning messages")
        pprint.pprint(analyze_messages['warnings'], indent=2)

    # Stage and upload the service if the sddraft analysis did not contain errors
    if analyze_messages['errors'] == {}:
        try:
            print("Staging to", sd_file)

            results = arcpy.server.StageService(sddraft_file, sd_file)
            messages = results.getMessages()
            pprint.pprint(messages, indent=2)

            results = arcpy.server.UploadServiceDefinition(in_sd_file=sd_file, in_server=server, 
                in_folder_type = "EXISTING", in_folder = folderName,
                in_my_contents="SHARE_ONLINE", in_public="PUBLIC"
            )
            messages = results.getMessages()
            print("The geocode service was successfully published.")
            pprint.pprint(messages, indent=2)
            return True

        except arcpy.ExecuteError:
            print("An error occurred")
            print(arcpy.GetMessages(2))

    else:
        # If the sddraft analysis contained errors, display them

        print("Error were returned when creating service definition draft")
        pprint.pprint(analyze_messages['errors'], indent=2)

    return False


if __name__ == "__main__":

    arcpy.env.overwriteOutput = True

    suffix = '_' + datestring # for debug and development
    locator_file = "c:\\Temp\\locator" + suffix
    service_name = "Clatsop_County_Locator"  # No spaces or special characters here

    # I have already created this service,
    # and I know its id and I really don't want to create a new one,
    # but if I do, well then okay
    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD,
              verify_cert=False)
    print("Connected to ", Config.PORTAL_URL)
    itemId = 'b87919419f6c4cd4a1580085f58b0c8f'
#    q = f"title:{service_name}, owner:bwilson@CLATSOP"
#    locators = gis.content.search(q, max_items=10, sort_field="title",
#                              sort_order="asc", outside_org=False, item_type="Geocoding Service")
#    print("Found %d locators." % len(locators))
    item = None
    try:
        item = ITEM(gis, itemId)
        locatorUrl = Config.PORTAL_URL + '/home/item.html?id=' + item.id
        print("Current service", locatorUrl)
    except:
        print("The old service is gone so I will make a new one.")

    with arcpy.EnvManager(scratchWorkspace="in_memory", workspace="in_memory"):
        # This creates .loc and .loz files that contain a copy of all the data,
        # so once that is done the in_memory copies are no longer needed.

        # You can comment this out if you want, to test only publishing...
        rval = create_locator(locator_file)

        # for testing, update the date, uncomment.
        # locator_file = "C:\\Temp\\locator_20220824_1124"
        #locator_file = "K:\\e911\\clatsop_county_20220824_1124"
        publish_locator(locator_file, service_name)

        if item:
            comment = "%s updated by \"%s\"" % (datestamp, myname)
            item.add_comment(comment)

# That's all!

