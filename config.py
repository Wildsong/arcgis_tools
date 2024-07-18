import os
from ssl import ALERT_DESCRIPTION_INSUFFICIENT_SECURITY
from arcgis.gis import GIS
from dotenv import load_dotenv

class Config(object):
    load_dotenv()

    PORTAL_URL = os.environ.get('PORTAL_URL')

    BASEMAP_GALLERY = 'CC Basemap Gallery for Web Maps'
    BASEMAP_GALLERY_ID = 'c8249f276d564b9bba0001128bce3787'

    CHAT_USER="bwilson"
    CHAT_PASSWORD = os.environ.get("PORTAL_PASSWORD")
    CHAT_SERVER = "https://chat.clatsopcounty.gov"
    
    HUB_URL = os.environ.get('HUB_URL')
    AGO_URL = os.environ.get('AGO_URL')
    
    SERVER_URL = os.environ.get('SERVER_URL')

    ARCGIS_ID = os.environ.get("ARCGIS_ID")
    ARCGIS_SECRET = os.environ.get("ARCGIS_SECRET")

    SDE_FILE = 'K:\\ORMAP_CONVERSION\\cc-sqlservers_WINAUTH.sde'

def get_token():
    # Get the ip address of my computer
    import socket
    hostname = socket.gethostname()
    ip_address = socket.gethostbyname(hostname) 

    url = Config.PORTAL_URL + '/sharing/rest/generateToken'
    payload = {'username': Config.PORTAL_USER, 'password': Config.PORTAL_PASSWORD,
           'client':'ip', 'ip':ip_address, 'f': 'json'}
#    payload = {'username': Config.PORTAL_USER, 'password': Config.PORTAL_PASSWORD,
#           'client':'referer', 'referer":refererurl, 'f': 'json'}
    # default lifespan is 60 minutes
    r = requests.post(url, payload)
    j=json.loads(r.text)
    return j['token']


def get_pro_token():
    import arcpy
    portalUrl = arcpy.GetActivePortalURL()
    j = arcpy.GetSigninToken()
    return j['token']


if __name__ == "__main__":
    import requests
    import json

    assert(Config.PORTAL_URL)
    assert(Config.PORTAL_USER)
    assert(Config.PORTAL_PASSWORD)

    assert(Config.HUB_URL)

    assert(Config.AGO_URL)
    assert(Config.AGO_USER)
    assert(Config.AGO_PASSWORD)

    assert(Config.SERVER_URL)

    assert os.path.exists(Config.SDE_FILE)

    # Test connection to ArcGIS Online
    gis = GIS(profile="ago")
    print("Logged in as", gis.properties["user"]["fullName"], 'to', gis.properties['name'])

    # Test connection to ArcGIS Hub, whatever that is. This fails
    #hub = GIS(Config.HUB_URL, Config.AGO_USER, Config.AGO_PASSWORD)
    #print("Logged in as", gis.properties["user"]["fullName"], 'to', gis.properties['name'])

    # Test a connection via normal auth
    gis = GIS(profile=os.environ.get('USERNAME'))
    print(gis)

    try:
        # Test a connection via a Pro token
        token = get_pro_token()
        gis = GIS(Config.AGO_URL, api_key=token, verify_cert=False)
        print("Logged in as", gis.properties["user"]["fullName"])
    except Exception as e:
        print("ERROR: Log in failed.", e)

    # Test a connection via a token
# Whelp, this is wrong
#    token = get_token()
#    gis = GIS(token=token, referer=Config.PORTAL_URL, verify_cert=False)
#    print(gis.properties)

    q = '*'
    list_of_maps = gis.content.search(
        q, item_type='web map', outside_org=False, max_items=5000)
    print("Maps found %d" % len(list_of_maps))

#    d = os.environ
#    for k in d:
#        print("%s : %s" % (k, d[k]))
#    print("PYTHONPATH=", os.environ.get("PYTHONPATH"))
