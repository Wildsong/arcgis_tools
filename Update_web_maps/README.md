# Update_web_maps

Use case: I need to replace existing layers with new ones.

## Set up

On my desktop I am using an existing conda environment called "arc-vscode" cloned
from "arcgispro-py3-vscode"
should already have what I need in it. Namely, "arcgis.py".

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

### find_map_layers.py

This will look for all the maps in Portal and list them.
You can set various queries and filters.

It generates a python list that you can paste into other scripts,
for example, repair_maps.py

### repair_maps.py

Find all the maps using
the old services or whatever, and replace it with the new.

## Resources 

There are samples in the arcgis.py repo, start there.
See "05_content_publishers/using_and_updating_GIS_content"

