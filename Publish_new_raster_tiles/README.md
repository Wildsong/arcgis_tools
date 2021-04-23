# Publish new raster tiles

This tool is intended for updating our Clatsop County "map image layer" aka a map service on the Portal.

We build a cache from the MIL. 
Rebuilding the whole cache takes less than 2 hours, but that two hours
makes the server crawl, so it's better when possible to build tiles only
for the areas that have changed.

## The process

I think that you need to update and then push an "sddraft" file up to the server,
that file is a package that contains a file geodatabase with all the data to be hosted on the server.

Once the "service definition" has been updated, then you can send a command to the server
to tell it to update all or some of the associated tiles.

## The details

There aren't any yet since I just started work on it.

## Set up

This tool uses an ArcGIS Pro project for input so it needs to run on a desktop with ArcGIS Pro 2.7 or higher installed.
It uses the Python for ArcGIS API too but I think that's normally always installed with AGP.

There needs to be a .env file with credentials in it. Copy sample.env to .env and edit it.

## Running it

Currently I only run it in VS Code. I need to change that so that normal people can run it.

Since it is only designed to update "Clatsop County" MIL there is no more config to do.
I will make it less specific when I need to, and at that point "config.py" will change.

The entry point is "main.py".

## TO DO

TODO- write the wrapper.
TODO- wrap it in a python toolbox so that I can run it inside ArcGISPro.
TODO- Generate a thumbnail from the data?


## References

"Automate Publishing of Web Layers Using ArcPy" https://www.esri.com/content/dam/esrisites/en-us/about/events/media/UC-2019/technical-workshops/tw-7108-919.pdf

Blog "Updating your hosted feature services with ArcGIS Pro..." https://www.esri.com/arcgis-blog/products/analytics/analytics/updating-your-hosted-feature-services-with-arcgis-pro-and-the-arcgis-api-for-python/

ArcGIS Server "Map servce caches" https://enterprise.arcgis.com/en/server/latest/publish-services/windows/what-is-map-caching-.htm

ArcGIS Pro 2.7 Mapping module (arcpy.mp) https://pro.arcgis.com/en/pro-app/latest/arcpy/mapping/introduction-to-arcpy-mp.htm

ArcGIS Pro 2.7 Sharing module (arcpy.sharing) https://pro.arcgis.com/en/pro-app/latest/arcpy/sharing/introduction-to-arcpy-sharing.htm

ArcGIS Pro 2.7 Upload Service Definition https://pro.arcgis.com/en/pro-app/latest/tool-reference/server/upload-service-definition.htm

Community.Esri.com

Automate overwrite web layer, feature class https://community.esri.com/t5/python-questions/automate-overwrite-web-layer-feature-class/td-p/20067

ArcGIS API reference https://developers.arcgis.com/python/api-reference
