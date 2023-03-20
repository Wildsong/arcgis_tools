#!/usr/bin/env -S conda run -n arcgis_tools --no-capture-output python
# Remember to set Portal credentials in the .conda/envs/arcgis_tools/etc/conda/activate.d/ file.
# The CIFS credentials are automounted using credentials from /etc/creds/
"""
    Check for missing taxmap PDF files.
"""
import os
from arcgis.gis import GIS
import arcgis.features
import pandas as pd
from glob import glob

# Normally we want to be quiet when running from crontab.
verbose = True

class Config(object):
    PORTAL_URL = os.environ.get('PORTAL_URL')
    SERVER_URL = os.environ.get('SERVER_URL')
    PORTAL_USER = os.environ.get("PORTAL_USER")
    PORTAL_PASSWORD = os.environ.get("PORTAL_PASSWORD")
    PDFLIB = os.environ.get("PDFLIB")

if __name__ == '__main__':
    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER,
              Config.PORTAL_PASSWORD, verify_cert=False)

    # Get a dataframe of all the taxlots
    url = f"{Config.SERVER_URL}/rest/services/Taxlots/FeatureServer/1"
    layer = arcgis.features.FeatureLayer(url,gis)
    
    taxlotkey = "TAXLOTKEY"
    taxmapnum = "TAXMAPNUM"

    fields = [taxlotkey, taxmapnum]
    df = layer.query(where="1=1", out_fields=fields, as_df=True)

    # Get a list of all the existing PDF files
    os.chdir(Config.PDFLIB)
    files = glob('*.pdf')
    if verbose:
        print(f"PDF files missing in {Config.PDFLIB}: {len(files)}")

    # Look for missing PDF files
    missing = dict()
    for idx, row in df.iterrows():
        taxlot = row[taxlotkey]
        taxmap = 'tp' + row[taxmapnum].lower() + '.pdf'
        if taxmap not in files:
            if taxmap in missing:
                missing[taxmap].append(taxlot)
            else: 
                missing[taxmap] = [taxlot]
    if len(missing):
        print("There are %d missing taxmap PDF files." % len(missing))
        for item in missing:
            print("ERROR:", item, missing[item])
    elif verbose:
        print("There are no missing taxmap PDF files today.")

    exit(0)
