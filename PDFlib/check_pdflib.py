import os
from arcgis.gis import GIS
import arcgis.features
import pandas as pd
from config import Config
from glob import glob

PDFLIB="k:/pdf_lib/taxmaps"

if __name__ == '__main__':
    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER,
              Config.PORTAL_PASSWORD, verify_cert=False)

    # Get a dataframe of all the taxlots
    url = "https://delta.co.clatsop.or.us/server/rest/services/Taxlots/FeatureServer/1"
    layer = arcgis.features.FeatureLayer(url,gis)
    fields = ["TAXLOTKEY","TAXMAPNUM"]
    df = layer.query(where="1=1", out_fields=fields, as_df=True)

    # Get a list of all the existing PDF files
    os.chdir(PDFLIB)
    files = glob('*.pdf')

    # Look for missing PDF files
    missing = dict()
    for idx, row in df.iterrows():
        taxmap = 'tp' + row["TAXLOTKEY"].lower() + '.pdf'
        acct = row["TAXMAPKEY"]
        if taxmap not in files:
            if taxmap in missing:
                missing[taxmap].append(acct)
            else: 
                missing[taxmap] = [acct]
    if len(missing):
        print("Missing files:")
        for item in missing:
            print(item, missing[item])
