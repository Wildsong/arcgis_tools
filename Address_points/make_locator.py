"""

    Creates a locator and uploads it to our portal.

"""
import sys
import os
import pprint
import arcpy
from arcgis.gis import GIS
from arcgis.gis import Item as PORTAL_ITEM
from datetime import datetime

# Add the parent directory so we can find files up one level
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))
from portal import PortalContent
from config import Config

now = datetime.now()
datestamp = now.strftime("%Y-%m-%d %H:%M")  # for comments
datestring = now.strftime("%Y%m%d_%H%M")  # for filenames

VERSION = "1.4"
path, exe = os.path.split(__file__)
myname = exe + " " + VERSION

def printmessages(m):
    try:
        for msg in m.getAllMessages():
            print('  ', msg[2])
    except Exception as e:
        pprint.pprint(m, indent=2)
    return

def create_locator(locator: dict):
    """Generates output in workspace"""

# TODO -- 
# If you were to put the LOC files onto a file share
# that the Server could access, then the copy would not
# have to take place in the publish stage.

    msg = '  Created locator files "%s".' % locator['file']
    if os.path.exists(locator['file'] + '.loc'):
        print(f"  Deleting loc file for \"{locator['file']}\".")
        os.unlink(locator['file'] + '.loc')
    if os.path.exists(locator['file'] + '.loz'):
        print(f"  Deleting loz file for \"{locator['file']}\".")
        os.unlink(locator['file'] + '.loz')

    # I used to copy all the data here
    # but there's not much point in doing that
    # since it gets loaded into the locator anyway.

    print(f"Creating locator definition for '{locator['servicename']}'.")
    # I ran the standard tool in Pro. I went to history, right clicked and did "copy python"
    # Then I pasted that here and edited it.

    try:
        arcpy.geocoding.CreateLocator(
            country_code="USA",
            primary_reference_data=locator['reference_data'],
            field_mapping=locator['fieldmap'],
            out_locator=locator['file'],
            language_code="ENG",
            alternatename_tables=[], alternate_field_mapping=[], custom_output_fields=[], # I wonder what this is
            precision_type="GLOBAL_HIGH",
        )
    except Exception as e:
        # If you get a 99999 error here try removing
        # POI from the list to isolate?? or postal??? Those are troublesome.
        print(e)
        pass

    return msg


def publish_locator(locator_file: str, service_name: str) -> bool:
    """
    This will either overwrite or create a new locator service.

    Return item
    """
    sddraft_file = "C:\\Temp\locator.sddraft"
    sd_file = "C:\\Temp\\locator.sd"

    summary = (
        "Locator based on E911 address points, points of interest, parcels, and roads"
    )
    tags = "Clatsop County, address, locator, geocode"

    # The URL of the federated server you are publishing to
    server = Config.SERVER_URL + "/rest/services/"

    status = False

    print("Analyzing...")
    analyze_messages = arcpy.CreateGeocodeSDDraft(
        locator_file,
        sddraft_file,
        service_name,
        copy_data_to_server=True,
        summary=summary,
        tags=tags,
        max_result_size=10,
        max_batch_size=500,
        suggested_batch_size=150,
        overwrite_existing_service=True,
    )

    if analyze_messages["warnings"] != {}:
        printmessages(analyze_messages)

    # Stage and upload the service if the sddraft analysis did not contain errors
    if analyze_messages["errors"] == {}:
        try:
            print("Staging to", sd_file)

            rval = arcpy.server.StageService(sddraft_file, sd_file)
            printmessages(rval)

            print("Uploading to", server)

# This results in a warning message, I am not sure what I need here
#   'WARNING 086222: Output directory in service definition is not set or is invalid. Using default output directory.'
#   Referring to https://github.com/Esri/arcgis-powershell-dsc/issues/157
#   It looks like it has to do with a server folder, but note the folder has to exist, so create it before using it.
#   It might be fixed iun 3.1 so give it a try.

            results = arcpy.server.UploadServiceDefinition(
                in_sd_file=sd_file,
                in_server=server,
                in_folder_type="EXISTING",
                in_my_contents="SHARE_ONLINE",
                in_public="PUBLIC",
            )
            print("The geocode service was successfully published.")
            printmessages(results)

            status = True

        except arcpy.ExecuteError:
            print("An error occurred")
            print(arcpy.GetMessages(2))

    else:
        # If the sddraft analysis contained errors, display them

        print("Error were returned when creating service definition draft")
        printmessages(analyze_messages)

    return status


def set_sharing(item: PORTAL_ITEM, groups: list) -> bool:
    try:
        item.share(everyone=True, groups=groups)
    except Exception as e:
        print("Could not set sharing.", e)
        return False
    return True


if __name__ == "__main__":

    arcpy.env.overwriteOutput = True

#    scratch_workspace = "in_memory"
    scratch_workspace = "C:\\Temp\\scratch.gdb"
    workspace = Config.SDE_FILE

    assert os.path.exists(Config.SDE_FILE)

    portal = arcpy.GetActivePortalURL()  # I wonder where it finds this.
    result = arcpy.SignInToPortal(portal)

    gis = GIS(profile=os.environ.get('USERNAME'))
    print("Connected to ", portal)
    pcm = PortalContent(gis)
    groups = gis.groups.search("GIS Team")

    # data to be used in the locators
    points_of_interest = "Clatsop.DBO.points_of_interest"
    address_points = "Clatsop.DBO.address_points"
    taxlots = "Clatsop.DBO.taxlots_accounts_join"
    zipcodes = "Clatsop.DBO.zipcodes"
    roads = "Clatsop.DBO.roads"

    map_postal = [
        "Postal.POSTAL 'Clatsop.DBO.zipcodes'.ZIP_CODE",
        "Postal.CITY 'Clatsop.DBO.zipcodes'.NAME",
        "Postal.REGION 'Clatsop.DBO.zipcodes'.STATE",
    ]

    suffix = ''
    #suffix = "_" + datestring  # for debug and development
    basename = "C:\\Temp\\" 

    locators = [
        {
            'servicename': 'Clatsop_County_Parcel_Point_Address_Locator',
            'reference_data': [[taxlots, 'PointAddress']],
            'fieldmap': [
                # Don't we have stupid awkward field names
                "PointAddress.HOUSE_NUMBER 'Clatsop.DBO.taxlots_accounts_join'.Clatsop_dbo_AT_taxlot_accoun_70",
                "PointAddress.STREET_PREFIX_DIR 'Clatsop.DBO.taxlots_accounts_join'.Clatsop_dbo_AT_taxlot_accoun_73",
                "PointAddress.STREET_NAME 'Clatsop.DBO.taxlots_accounts_join'.Clatsop_dbo_AT_taxlot_accoun_71",
                "PointAddress.SUB_ADDRESS_UNIT 'Clatsop.DBO.taxlots_accounts_join'.Clatsop_dbo_AT_taxlot_accoun_75",
                "PointAddress.CITY 'Clatsop.DBO.taxlots_accounts_join'.Clatsop_dbo_AT_taxlot_accoun_61",
                #"Parcel.SUBREGION 'Clatsop.DBO.taxlots_accounts_join'.County", # This field has 4 or NULL in it.
                #"Parcel.REGION 'Clatsop.DBO.taxlots_accounts_join'.STATE", # This field is always wrong
                "PointAddress.POSTAL 'Clatsop.DBO.taxlots_accounts_join'.Clatsop_dbo_AT_taxlot_accoun_74",
            ],
            'file': basename + 'parcel_point_address' + suffix,
        },        {
            'servicename': 'Clatsop_County_Parcel_Locator',
            'reference_data': [[taxlots, 'Parcel']],
            'fieldmap': [
                # Don't we have stupid field names
                "Parcel.PARCEL_NAME 'Clatsop.DBO.taxlots_accounts_join'.Clatsop_dbo_AT_taxlot_accoun_66", 
                "PointAddress.HOUSE_NUMBER 'Clatsop.DBO.taxlots_accounts_join'.Clatsop_dbo_AT_taxlot_accoun_70",
                "Parcel.STREET_PREFIX_DIR 'Clatsop.DBO.taxlots_accounts_join'.Clatsop_dbo_AT_taxlot_accoun_73",
                "Parcel.STREET_NAME 'Clatsop.DBO.taxlots_accounts_join'.Clatsop_dbo_AT_taxlot_accoun_71",
                "Parcel.SUB_ADDRESS_UNIT 'Clatsop.DBO.taxlots_accounts_join'.Clatsop_dbo_AT_taxlot_accoun_75",
                "Parcel.CITY 'Clatsop.DBO.taxlots_accounts_join'.Clatsop_dbo_AT_taxlot_accoun_61",
                #"Parcel.SUBREGION 'Clatsop.DBO.taxlots_accounts_join'.County", # This field has 4 or NULL in it.
                #"Parcel.REGION 'Clatsop.DBO.taxlots_accounts_join'.STATE", # This field is always wrong
                "Parcel.POSTAL 'Clatsop.DBO.taxlots_accounts_join'.Clatsop_dbo_AT_taxlot_accoun_74",
            ],
            'file': basename + 'parcel' + suffix,
        },
        {
            'servicename': 'Clatsop_County_E911_Address_Locator',
            'reference_data': [[address_points, 'PointAddress']],
            'fieldmap': [
                "PointAddress.HOUSE_NUMBER 'Clatsop.DBO.address_points'.addNum",
                "PointAddress.STREET_PREFIX_DIR 'Clatsop.DBO.address_points'.preDir",
                "PointAddress.STREET_PREFIX_TYPE 'Clatsop.DBO.address_points'.preType",
                "PointAddress.STREET_NAME 'Clatsop.DBO.address_points'.gcLgFlName",
                "PointAddress.STREET_SUFFIX_TYPE 'Clatsop.DBO.address_points'.postType",
                "PointAddress.STREET_SUFFIX_DIR 'Clatsop.DBO.address_points'.postDir",
                "PointAddress.FULL_STREET_NAME 'Clatsop.DBO.address_points'.gcFullName",
                "PointAddress.SUB_ADDRESS_UNIT 'Clatsop.DBO.address_points'.unit",
                "PointAddress.CITY 'Clatsop.DBO.address_points'.incMuni",
                "PointAddress.POSTAL 'Clatsop.DBO.address_points'.zipCode",
            ],
            'file': basename + 'e911Address' + suffix,
        },
        {
            'servicename': 'Clatsop_County_Street_Address_Locator',
            'reference_data': [[roads, 'StreetAddress']],
            'fieldmap': [
                "StreetAddress.HOUSE_NUMBER_FROM_LEFT 'Clatsop.DBO.roads'.FromAddressLeft",
                "StreetAddress.HOUSE_NUMBER_TO_LEFT 'Clatsop.DBO.roads'.ToAddressLeft",
                "StreetAddress.HOUSE_NUMBER_FROM_RIGHT 'Clatsop.DBO.roads'.ToAddressRight",
                "StreetAddress.HOUSE_NUMBER_TO_RIGHT 'Clatsop.DBO.roads'.ToAddressRight",
                "StreetAddress.STREET_PREFIX_DIR 'Clatsop.DBO.roads'.Prefix",
                "StreetAddress.STREET_NAME 'Clatsop.DBO.roads'.Street",
                "StreetAddress.FULL_STREET_NAME 'Clatsop.DBO.roads'.StreetName"
            ],
            'file': basename + 'roads' + suffix,
        },
        {
            'servicename': 'Clatsop_County_Point_of_Interest_Locator',
            'reference_data': [[points_of_interest, 'POI']],
            'fieldmap': [
                "POI.FEATURE_ID 'Clatsop.DBO.points_of_interest'.FEATURE_ID",
                "POI.PLACE_NAME 'Clatsop.DBO.points_of_interest'.name",
                "POI.CATEGORY 'Clatsop.DBO.points_of_interest'.category",
                "POI.SUBCATEGORY 'Clatsop.DBO.points_of_interest'.subcategory",
            ],
            'file': basename + 'poi' + suffix,
        },
    ]

    with arcpy.EnvManager(scratchWorkspace=scratch_workspace, workspace=workspace):
        # This creates .loc and .loz files that contain a copy of all the data,
        # so once that is done the in_memory copies are no longer needed.

        composite_service_name = "Clatsop_County_Locator"  # No spaces or special characters here

        for locator in locators:
            msg = create_locator(locator)
            print(msg)

            continue

            # for testing, update the date, uncomment.
            # locator_file = "C:\\Temp\\locator_20220824_1124"
            # locator_file = "K:\\e911\\clatsop_county_20220824_1124"
            status = publish_locator(locator)
            if status:
                newItem = pcm.findItem(title = service_name)
                if not newItem:
                    print("The service was not found.")
                else:
                    print("Setting sharing options…")
                    try:
                        comment = '%s updated by "%s"' % (datestamp, myname)
                        set_sharing(newItem, groups)
                        newItem.add_comment(comment)
            
                    except Exception as e:
                        print("Could not find the new service, weird huh?", e)
                        pass

# That's all!
