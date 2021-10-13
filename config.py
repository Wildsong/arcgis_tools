import os

class Config(object):

    ARCGIS_URL = os.environ.get('ARCGIS_URL')
    ARCGIS_USER = os.environ.get("ARCGIS_USER")
    ARCGIS_PASSWORD = os.environ.get("ARCGIS_PASSWORD")

    ARCGIS_ID = os.environ.get("ARCGIS_ID")
    ARCGIS_SECRET = os.environ.get("ARCGIS_SECRET")



    

