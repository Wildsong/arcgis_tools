import os
import sys
import arcpy

from datetime import datetime
datestamp = datetime.now().strftime("%Y%m%d_%H%M")

def create_domain(workspace):
    try:
        rval = arcpy.management.CreateDomain(in_workspace=workspace, 
            domain_name="address_source", 
            domain_description="Source of situs data", 
            field_type="TEXT", domain_type="CODED", split_policy="DEFAULT", merge_policy="DEFAULT")
    except Exception as e:
        print("create_domain said: ", e)
        #return
    try:
        rval = arcpy.management.AddCodedValueToDomain(in_workspace=workspace, domain_name="address_source", code="AT", code_description="Accessment and Taxation taxlot data")
        rval = arcpy.management.AddCodedValueToDomain(in_workspace=workspace, domain_name="address_source", code="GE", code_description="Geocoded (Esri)")
        rval = arcpy.management.AddCodedValueToDomain(in_workspace=workspace, domain_name="address_source", code="M", code_description="Manual")
    except Exception as e:
        print("create_domain said: ", e)


def build_address_points(source, target, keep_fields):
    arcpy.env.overwriteOutput = True

    if arcpy.Exists(target):
        arcpy.management.Delete(target)

    selected_features = "in_memory/selected_taxlots"
    if arcpy.Exists(selected_features):
        arcpy.management.Delete(selected_features)

    selection_sql = "NOT (OrTaxLot LIKE %ROADS OR OrTaxLot LIKE %WATER OR OrTaxLot LIKE %NONTL)"
    arcpy.management.MakeFeatureLayer(in_features=source, out_layer=selected_features, where_clause=selection_sql)
    rval = arcpy.management.DeleteField(in_table=selected_features, drop_field=delete_these_fields)

    arcpy.management.FeatureToPoint(in_features=selected_features, out_feature_class=target, point_location="CENTROID")

    rval = arcpy.management.EnableEditorTracking(in_dataset=target, 
        creator_field="created_by", creation_date_field="created_date", 
        last_editor_field="edit_by", last_edit_date_field="edit_date", 
        add_fields="ADD_FIELDS", record_dates_in="DATABASE_TIME")


    rval = arcpy.management.AddFields(in_table=target, 
        field_description=[
            ["source", "TEXT", "", "2", 
                "AT", "address_source"]
        ])

#    Output_Feature_Class = "K:\\Social_Services\\NearMe\\NearMe.gdb\\address_pt_ReverseGeocode"
#    arcpy.geocoding.ReverseGeocode(in_features=address_pt_2_, in_address_locator="", out_feature_class=Output_Feature_Class, address_type="ADDRESS", search_distance="100 Meters", feature_type="", location_type="")

if __name__ == '__main__':
    workspace = "K:/Social_Services/NearMe/NearMe.gdb"
    with arcpy.EnvManager(scratchWorkspace=workspace, workspace=workspace):
        create_domain(workspace)

    # Okay so basically there's a boatload of attributes to get rid of,
    # which means I am starting with the wrong feature class.
    # Use the stripped down one and add ownership etc later if I need it, avoid duplication

        build_address_points("K:/Social_Services/NearMe/Clatsop_WinAuth.sde/taxlots_fd/taxlots",
            "address_pt_" + datestamp, 
            ['OrTaxLot', 'MapTaxlot']
        )

