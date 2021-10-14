import os
from dotenv import load_dotenv

class Config(object):
    load_dotenv()

    PORTAL_URL = os.environ.get('PORTAL_URL')
    PORTAL_USER = os.environ.get("PORTAL_USER")
    PORTAL_PASSWORD = os.environ.get("PORTAL_PASSWORD")

    ARCGIS_ID = os.environ.get("ARCGIS_ID")
    ARCGIS_SECRET = os.environ.get("ARCGIS_SECRET")

if __name__ == "__main__":
    assert(Config.PORTAL_URL)
    assert(Config.PORTAL_USER)
    assert(Config.PORTAL_PASSWORD)
