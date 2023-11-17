# Address_points tools

## Goals

1. Create address points feature class for general use.
2. Build Locator service. It will integrate e911 address points, roads, taxlots, and points of interest.

## History

2023-11-07 
There are some points missing, (I have taxlots without points)
so I reactivated the script to pull data from taxlots, and merged it.

Either I need t

2023-10-13
 1. I used a model instead of this script.
 2. They did not give us hydrants so I left the "hydrants" feature class untouched

2022-08-23 updated 
I switched from trying to create points based on taxlot centroids
to using e911 data so some code here was made obsolete 
but works fine.

2021-10 or so created, based on taxlot centroids

## Notes on Locator

"Roles" in the locator:
1. Street Address
2. Parcel
3. POI

Refer to either the toolbox model "Build Locator Service"
or the  script make_locator.py for things like field mappings.

There are about 100 other fields I am not using yet.
For example, POI could use an URL field. It can have
a phone number. It can have a full address.

## Workflows

### Importing GeoComm data

There is a model "Import SSAP" that processes the data from the
GeoComm provided e911 FGDB and generates a new address point
feature class in our EGDB. It will be in our projection EPSG:2913.

The model also can process hydrant data, should they provide it.

I wrote a script that can do all this, too. Your choice.
e911_import.py imports the e911 address points and hydrants to the project FGDB


### Merging GeoComm and Taxlots Situs data

#### Fields for the Locator

I have listed some fields that would be good to have even though we don't support them yet.
I left out many more fields that seem totally irrelevant to me.
I need examples of what each should look like, else I end up with salads like "1234 North N Wahanna Rd Road" in the results.

Some fields get guessed incorrectly, so if you use the Esri geoprocessing tool then be careful! For example
taxlots will match the city name instead of Situs City and that's WRONG. "State" will have the same problem.
Better to leave it out than use the wrong one.

Probably best to have City, State, Country attributes attached to every feature.

''Point Address'' = Address Points

https://pro.arcgis.com/en/pro-app/3.1/help/data/geocoding/introduction-to-locator-roles.htm#GUID-C7BE5282-A351-4449-B09E-541313C7B7F0

There's code to deal with multiple addresses stacked with the same geometry. I am not willing to think about it right now.
Likewise "subaddresses" which means apartments or condos.

* Feature ID
* *Street Name 
* Full Street Name
* City
* County
* State
* Country
* Unit
* Unit Type
* House Number
* Prefix Direction
* Suffix Direction
* Building Name

''Parcel'' = Taxlots w accounts

https://pro.arcgis.com/en/pro-app/3.1/help/data/geocoding/introduction-to-locator-roles.htm#ESRI_SECTION1_D00AD43A248E49BC939616E570CC66B9

"Feature ID" should be a field that's unique to a location, for example if you have 5 stacked polygons at
the same place, you should have one Feature ID for all 5. 

House Number is not used if you use "From" and "To" fields. In this case if you have a single house you put the
number in both the From and To fields and leave House Number blank. I might try to do this.

* Feature ID
* *Parcel Name
* House Number
* House Number From
* House Number To
* Prefix Direction
* Suffix Direction
* Full Street Name
* Preferred Street Name
* City
* County
* State

''Street Address'' = Roads

* Feature ID
* *Left House Number From
* *Left House Number To
* *Right House Number From
* *Right House Number To
* *Street Name
* Full Street Name
* Prefix Direction
* Suffix Direction
* Left City (no really, left and right? I suppose it makes sense, never thought about it.)
* Right City

''POI'' = Points_of_interest "Boat Ramp in Astoria"

POI can have the whole address field set but we don't have anything like that at this time.

* Feature ID
* *Place Name
* Place Category - "waterfall", "boat ramp", "park"...
* Place Subcategory
* Building Name
* Phone
* Url

''Distance Marker'' = Mileposts

* *

''Postal'' = Zip codes

### Importing GNIS

Don't do this, it's done already. EGDB "Points of interest" is now
maintained by hand and this would wipe out all my hard work.

gnis_import.py imports the Oregon GNIS data for Clatsop County

### Building Locator service

#### Initial set up

Assuming the E911 and point of interest data are already loaded.

1. e911_import.py to create address and hydrant data in local fgdb
2. process_poi.py to create poi fc in local FGDB
3. make_locator.py to create a locator and publish it

#### Maintenance 

You only have to run make_locator.py

It creates a local copy of the data,
turns it into a locator,
and then publishes it to the server.

#### Share a locator on Portal

'''NOTE make_locator.py does this now, too.'''

https://pro.arcgis.com/en/pro-app/latest/help/sharing/overview/share-a-locator.htm#GUID-0E990A85-7CA9-46B9-8163-87AEA3B23924

In ArcGIS Pro,

"Share" tab -> "Share As" group -> "Locator" use "Share Locator" or "Overwrite Locator" in dropdown

With "Overwrite", you will need to select the one in the Locator_services folder
and use the LOC file created by "make_locator.py", usually that's clatsop_county.loc.

There are lots of options left to explore in this step.

