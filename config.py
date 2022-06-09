import os
from dotenv import load_dotenv
from arcgis.gis import GIS

class Config(object):
    load_dotenv()

    PORTAL_URL = os.environ.get('PORTAL_URL')
    PORTAL_USER = os.environ.get("PORTAL_USER")
    PORTAL_PASSWORD = os.environ.get("PORTAL_PASSWORD")
    SERVER_URL = os.environ.get('SERVER_URL')

    ARCGIS_ID = os.environ.get("ARCGIS_ID")
    ARCGIS_SECRET = os.environ.get("ARCGIS_SECRET")

if __name__ == "__main__":
    import requests
    import json

    assert(Config.PORTAL_URL)
    assert(Config.PORTAL_USER)
    assert(Config.PORTAL_PASSWORD)
    assert(Config.SERVER_URL)

    # Test a connection via normal auth
    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
    print(gis)

    # Test a connection via a token
    url = '/sharing/rest/generateToken'
    payload = {'username': Config.PORTAL_USER,
           'password': Config.PORTAL_PASSWORD,
           'client':'ip', 'ip':'10.10.4.68', 
           'f': 'json'}
    r = requests.post(Config.PORTAL_URL+url, payload)
    j=json.loads(r.text)
    token = j['token']
#    gis = GIS(Config.PORTAL_URL,api_key=token)
#    print(gis)
    q = '*'
    list_of_maps = gis.content.search(
        q, item_type='web map', outside_org=False, max_items=5000)
    print("Maps found %d" % len(list_of_maps))

    d = os.environ
    for k in d:
        print("%s : %s" % (k, d[k]))
#    print("PYTHONPATH=", os.environ.get("PYTHONPATH"))
