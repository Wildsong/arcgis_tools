# Update_web_maps

Use case: I need to replace existing layers with new ones.

## Set up

On my desktop I am using an existing conda environment called "arcgis_tools"
which should already have what I need in it. Namely, "arcgis.py".

(See also the arctic repo.)
```bash
conda activate arcgis-tools
```

Create the .env file, and don't check it in.
```bash
PORTAL=yourportal
USER=
PASSWORD=
```

## The scripts

### extract_layer.py

Extracts the layers we need to update from the CC Map Template.

Currently the files extracted are

* layer_county_aerials_brief.json
* layer_county_aerials.json
* layer_roads.json

I can edit these files by hand.
Then I feed them back into the template map using "map_repair"!

### map_repair.py

Writes JSON layer files into the mapfiles.
The mapfiles are the ones in a list of apps.
Also it will repair the template (see extract_layer.py).

### old_map_repair.py

Clumsy version that will find all the maps using
the old services or whatever, and replace it with the new.
### find_map_layers.py

This will look for all the maps in Portal and list them.
You can set various queries and filters.

It generates a python list that you can paste into other scripts,
for example, repair_maps.py


## Resources 

There are samples in the arcgis.py repo, start there.
See "05_content_publishers/using_and_updating_GIS_content"

