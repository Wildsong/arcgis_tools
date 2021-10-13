# arcgis_tools
Python tools automating day-to-day tasks with ArcGIS Enterprise

My intention is to collect tools that I am writing here.

## Set up

Currently I am developing the code in Visual Studio Code,
which allows me to specify a conda environment as a setting.

I am trying to live without arcpy right now because conda cannot install it.
It gripes about the Python version and I can't find the right setting.

```bash
conda create --name=arcgis_tools --file=requirements.txt -c esri -c conda-forge
```

Notes:
* The opencv and pillow packages are currently only needed to generate thumbnails.
* Currently, arcgis and arcpy will force python to be version 3.7.x 

## Publish new raster tiles

Go read its README.md to see what it does. It will have changed by now.

## Transit_update

Updates the (hosted) transit layer(s) on cc-gis.

