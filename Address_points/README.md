# Address_points tools

2022-08-23 updated 
2021-10 or so created

I switched from trying to create points based on taxlot centroids to using e911 data
so lots of code here was made obsolete but works fine

e911_import.py imports the e911 address points and hydrants to the project FGDB

gnis_import.py imports the Oregon GNIS data for Clatsop County

## Initial set up

The E911 and point of interest data are already loaded.

1. e911_import.py to create address and hydrant data in local fgdb
2. process_poi.py to create poi fc in local FGDB
3. make_locator.py to create a locator and publish it

## Maintenance 

You only have to run make_locator.py

It creates a local copy of the data,
turns it into a locator,
and then publishes it to the server.
## Share a locator on Portal

'''NOTE make_locator.py does this now, too.'''

https://pro.arcgis.com/en/pro-app/latest/help/sharing/overview/share-a-locator.htm#GUID-0E990A85-7CA9-46B9-8163-87AEA3B23924

In ArcGIS Pro,

"Share" tab -> "Share As" group -> "Locator" use "Share Locator" or "Overwrite Locator" in dropdown

With "Overwrite", you will need to select the one in the Locator_services folder
and use the LOC file created by "make_locator.py", usually that's clatsop_county.loc.

There are lots of options left to explore in this step.

