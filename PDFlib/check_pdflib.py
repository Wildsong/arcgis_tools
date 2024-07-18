#!/usr/bin/env -S conda run -n arcgis_tools --no-capture-output python
# Remember to set credentials etc in the .conda/envs/arcgis_tools/etc/conda/activate.d/ files.
"""
    Check for missing taxmap PDF files. 
    Use the -v option to get output even when nothing is missing. 
    Default is to be quiet for running from crontab.

    This script is part of arcgis_tools.
"""
import sys
import os
from arcgis.gis import GIS
import arcgis.features
import pandas as pd
from glob import glob

# Normally we want to be quiet when running from crontab.
verbose = False
try:
    verbose = sys.argv[1] == '-v' 
except:
    pass


class Config(object):
    PORTAL_URL = os.environ.get('PORTAL_URL')
    SERVER_URL = os.environ.get('SERVER_URL')
    PDFLIB = os.environ.get("PDFLIB")

if __name__ == '__main__':

    assert(Config.PORTAL_URL)
    assert(Config.SERVER_URL)
    assert(Config.PDFLIB)
    assert(os.path.exists(Config.PDFLIB))
        
    try:
        # They stupidly throw a warning message about verify_cert
        # so I have to wrap this script in a shell script to catch it.
        gis = GIS(profile=os.environ.get('USERNAME'))
    except Exception as e:
        print("Can't sign in!",e)
        exit(1)

    try:
        # Get a dataframe of all the taxlots
        url = f"{Config.SERVER_URL}/rest/services/Taxlots/FeatureServer/1"
        layer = arcgis.features.FeatureLayer(url,gis)
    except Exception as e:
        print(e)
        print(url)
        exit(1)
    
    taxlotkey = "TAXLOTKEY"
    taxmapnum = "TAXMAPNUM"

    fields = [taxlotkey, taxmapnum]
    try:
        df = layer.query(where="1=1", out_fields=fields, as_df=True)
    except Exception as e:
        print("Can't query layer.",e, f"url={url}")
        exit(1)

    # Get a list of all the existing PDF files
    os.chdir(Config.PDFLIB)
    files = glob('*.pdf')
    if verbose:
        print(f"Count of PDF files in {Config.PDFLIB}: {len(files)}")

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
