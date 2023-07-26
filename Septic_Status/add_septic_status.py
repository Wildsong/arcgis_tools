import arcpy
from glob import glob

septic_path = 'X:/Images/Health/Septic'
workspace = 'K:/ORMAP_CONVERSION/cc-thesql_WinAuth.sde'
fc = 'taxlot_accounts'

# If the short integer field "septic_status" does not exist, you must add it yourself.

fields = ['OID@', 'taxlotkey', 'septic_status']
arcpy.env.workspace = workspace
with arcpy.da.Editor(workspace) as edit:
    with arcpy.da.UpdateCursor(fc, fields) as cursor:
        for row in cursor:
            taxlotkey = row[1]
            # If it has septic file(s), record how many there are 
            filelist = glob(septic_path + f'/{taxlotkey}*.pdf')
            count = len(filelist)
            if count>0:
                row[2] = count 
                cursor.updateRow(row)

