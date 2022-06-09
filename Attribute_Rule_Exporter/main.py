from cmath import exp
import arcpy
import os

gdb = r"C:\data\gis.sde"
aaPath = r"C:\data\AttributeRules"
gdb = "attr_rule_test.gdb"
aaPath = r'C:\temp'


def export_attributes(item, ruleFile):
    attRules = arcpy.Describe(item).attributeRules
    if len(attRules) == 0:
        print("No rules found in %s" % item)
        return True # Nothing to do

    try:
        arcpy.management.ExportAttributeRules(item, ruleFile)
    except Exception as e:
        arcpy.AddMessage("FAILED to create %s, %s" % (ruleFile, e))
        return False
    
    arcpy.AddMessage("SUCCESSFULLY created %s" % ruleFile)
    return True

if not arcpy.Exists(gdb): 
    print("Could not open database.")
    exit(-1)
arcpy.env.workspace = gdb
arcpy.env.overwriteOutput = True

if not os.path.exists(aaPath): os.makedirs(aaPath)

for ds in arcpy.ListDatasets("*"):
    for fc in arcpy.ListFeatureClasses("*", feature_dataset=ds):
        fcPath = os.path.join(ds, fc)
        rules = os.path.join(aaPath, fc+'_AA.csv')
        export_attributes(fcPath, rules)

for fc in arcpy.ListFeatureClasses("*"):
    rules = os.path.join(aaPath, fc+'_AA.csv')
    export_attributes(fc, rules)

for table in arcpy.ListTables("*"):
    rules = os.path.join(aaPath, table+'_AA.csv')
    export_attributes(table, rules)
