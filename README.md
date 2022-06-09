# arcgis_tools
Python tools automating day-to-day tasks with ArcGIS Enterprise

My intention is to collect the tools that I am writing here in this repository.

## Set up

Currently I am developing the code in Visual Studio Code,
which allows me to specify a Conda environment as a setting.

My approach is to tell Conda I want 'arcgis' and then let conda dependencies install everything else,
selecting the version of python, pandas, etc that it wants. This way everything will work together.

I am relying on features in version 2.x of arcgis.

You need python-dotenv to run from command line, and autopep8 to keep VS Code happy.

```bash
conda create -n arcgis_tools -c esri -c conda-forge autopep8 python-dotenv arcgis 
```

I hate cloning the old ArcGIS Pro environment because then it's painful to upgrade
and I end up with it being always out of date. But this is how it could be done.

```bash
conda create -n arcgis_tools --clone arcgispro-py3
conda activate arcgis_tools
conda install autopep8 python-dotenv
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

## PDFlib

Checks for missing taxmaps

## Transit_update

Updates the (hosted) transit layer(s) on cc-gis.

