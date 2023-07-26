"""

For each app, 

1. Copy the standard BasemapGallery config into the app.

2. Edit the app config.json file to make it 
have the same BasemapGallery widget referenced.

"""
import os
from glob import glob
from utils import load_json, save_json


def getConfigs(baseFolder="\\\\cc-gis\\C$\\inetpub\\wwwroot\\apps") -> list:
    """ Returns a list of full paths for each app config.json file. """
    return  glob(os.path.join(baseFolder, '*/config.json'))

def getWidget(widgetName:str, configFile:str)->dict:
    """ Search the config.json file for a widget and return its obj. """
    rval = None
    config = load_json(configFile)
    for w in config['widgetPool']['widgets']:
        #print(w)
        if w['name'] == widgetName:
            rval = w
            break
    return rval


if __name__ == "__main__":

    replacement = "widgets_ClatsopCounty_BasemapGallery"

    for item in getConfigs():
        (p,f) = os.path.split(item)
        (base, appName) = os.path.split(p)
        print(f"Checking \"{appName}\"..")
        widge = getWidget("BasemapGallery", item)
        if widge:
            if widge['id'] == replacement:
                already_fixed += 1
            else:
                print(f"  My sad widget is called \"{widge['id']}\"")
                fixed += 1
        else:
            print("  This little app had none.")

    print(f"All done! I fixed {fixed} apps. Already okay={already_fixed}")
