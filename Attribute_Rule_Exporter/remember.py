import arcpy
import os

gdb = r"C:\data\gis.sde"
aaPath = r"C:\data\AttributeRules"
gdb = "attr_rule_test.gdb"


def export_attributes(item, ruleFile):
    attRules = arcpy.Describe(item).attributeRules
    if len(attRules) == 0:
        arcpy.AddMessage("No rules found in %s" % item)
        return True  # Nothing to do

    if os.path.exists(ruleFile):
        os.remove(ruleFile)
    try:
        print(ruleFile, len(ruleFile), ruleFile[67:])
        rval = arcpy.management.ExportAttributeRules(item, ruleFile[67:])
        print(rval)
    except Exception as e:
        arcpy.AddMessage("FAILED to create %s, %s" % (ruleFile, e))
        return False

    arcpy.AddMessage("SUCCESSFULLY created %s" % ruleFile)
    return True


arcpy.env.workspace = gdb
arcpy.Describe(gdb)
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
