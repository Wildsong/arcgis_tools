import os

class Config(object):

    PORTAL_URL = "https://delta.co.clatsop.or.us/portal"
    SERVER_URL = "https://delta.co.clatsop.or.us/server"
    
    PORTAL_USER = os.environ.get("PORTAL_USER")
    PORTAL_PASSWORD = os.environ.get("PORTAL_PASSWORD")

