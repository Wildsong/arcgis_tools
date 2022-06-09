"""
    Run some tests on a GeocodeServer
"""
import os
import arcgis
from arcgis.gis import GIS
from arcgis.geocoding import geocode
from config import Config

if __name__ == "__main__":

    serviceName = Config.SERVER_URL + \
        "/rest/services/clatsop_county_no_parcels/GeocodeServer"
    gis = GIS(Config.PORTAL_URL, Config.PORTAL_USER, Config.PORTAL_PASSWORD)
    print(gis)
    gc = arcgis.geocoding.get_geocoders(gis)[0]

    tests = [
        "McClure Park, Astoria",
        "Capt. Robert Gray School, Astoria",

        "1830, Astoria",
        "1830",
        "1831 5th Street, Astoria",
        "1830 5th Street, Astoria",
        "1830 5th St., Astoria",
        "1830 5th St, Astoria",
        "1830 5th, Astoria",
        "1830 5th St.",
        "1830 5th St",
        "5th Street, Astoria",
        "5th Street",
        "5th St., Astoria",
        "5th St.",
        "5th",
        "5"
    ]

    for item in tests:
        print("%s -----" % item)
        r = geocode(item)
        for result in r:
            print("  %5.2f %s" % (result['attributes']['Score'], result['address']))
