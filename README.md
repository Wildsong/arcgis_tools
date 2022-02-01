# arcgis_tools
Python tools automating day-to-day tasks with ArcGIS Enterprise

My intention is to collect the tools that I am writing here in this repository.

## Set up

Currently I am developing the code in Visual Studio Code,
which allows me to specify a conda environment as a setting.

Tell it you want the package 'arcgis' and then let conda dependencies install everything else,
selecting the version of python, pandas, etc that it wants. This way everything will work
together.

You need python-dotenv to run from command line, and autopep8 to keep VS Code happy.

```bash
conda create -n arcgis_tools -c esri -c conda-forge autopep8 python-dotenv arcgis 
```

Notes:
* The opencv and pillow packages are currently only needed to generate thumbnails.
* Currently, arcgis and arcpy will force python to be version 3.7.x 

Optionally, install these:

```bash
conda install -n arcgis_tools -c esri python arcpy
conda install -n arcgis_tools opencv pillow
```

On a server there is a different package for arcgpy, see https://enterprise.arcgis.com/en/server/latest/develop/linux/scripting-service-publishing-with-arcpy.htm
Refer to that page for the very limited list of things you can do with arcpy on a server. Probably not worth the bother
but here is how to install:

```bash
conda install -n arcgis_tools arcpy-server=10.9 -c esri
```

## Publish new raster tiles

Go read its README.md to see what it does. It will have changed by now.

## Transit_update

Updates the (hosted) transit layer(s) on cc-gis.

