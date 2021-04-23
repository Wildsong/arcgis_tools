# Transit_update

GTFS = transit data

## TODO

This version requires "arcpy" which means it has to run on a computer with Pro installed.
I want it on a server, which means I have to ditch arcpy in favor of arcgis or "other".

The only arcpy code I need is the conversion code that reads in the GTFS files
and writes them out as feature classes (and tables.) Reading the files should
be simple since they are just CSV. Then store in memory in Pandas dataframes,
and send the completed dataframes to arcpy for writing to feature classes.

Easy, but not something I have time to work on at the moment.

## Prerequisite

This version, alas, requires arcpy. So for now, I run it on a desktop. 
## How to use it

If you run main.py it does everything,

* check for updates
* download new data if needed
* convert from GTFS to FGDB
* publish to cc-gis (TODO)

Some of the sources don't have any expiration dates,
so they get reprocessed every time main is run.
## Configuration

The file config.py contains:

* sources for downloads
* where to store downloaded files
* lists of what to download and how to rename them.
## Downloader

Reads the table from the GTFS web site, parses it,
downloads any files that are expired or missing.

The code is in GTFSdownloader.py

## Convert

I did a model in K:/Social_Services/NearMe and exported it to Python. Then I polished it. 
See GTFSimport.py. It now implements a class that can be used in other scripts.
## Publish

## References

* [GTFS web site](https://gtfs.org)
* [Oregon GTFS](https://oregon-gtfs.com)
* [Esri public transit tools](https://esri.github.io/public-transit-tools/)

