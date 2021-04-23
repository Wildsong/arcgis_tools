# arcgis_update_map



CAVEAT EMPTOR

In the update section, doing "add_layer" puts the new layer at the top of the list
and I don't see any way around that







I need to publish a new raster map as a base layer,
test it, and then update a bunch of existing web apps.

This will look for web maps in Portal, find all the ones using
the old service, and replace it with the new service.

It should work for Portal or ArcGIS Online, I suppose, but
I only care about Portal right now.

Once it's done you can safely delete the old service.

The services have a date stamp in their name, like "basemap_20201103".

## Set up

On my desktop I am using an existing conda environment called "arc-vscode" cloned
from "arcgispro-py3-vscode"
should already have what I need in it. Namely, "arcgis.py".

(See also the arctic repo.)
```bash
conda activate arctic
```

Create the .env file, and don't check it in.
```bash
PORTAL=yourportal
USER=
PASSWORD=
```

## What the script needs to do

There are samples in the arcgis.py repo, start there.
See "05_content_publishers/using_and_updating_GIS_content"

### Find all the maps

### Find all the layers in each map

### Edit each map



