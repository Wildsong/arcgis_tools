# PDFlib

Check for missing PDFlib files
to avoid having broken links in webmaps.

## Backstory:

Cartographers generate taxmaps as PDF files as a matter of public record.
We make them available via hyperlinks from maps. That means from time to time
there is a link that points nowhere.

## How it works

1. Build a list of needed files from taxlots GIS layer
2. See if the referenced taxmap files exist
3. List any that are missing

## Deployment

Copy from the source folder to the user bin folder and then
set it to run as from crontab each morning. Cron will 
automatically email output to me.

The environment is supported via conda, so refer to
~/.conda/envs/arcgis_tools/etc/conda/activate.d/env_vars.sh
for ArcGIS credentials.

The automounter is not working right now, so the file server is
mounted at /media/GIS from /etc/fstab.  That's defined in the same
environment under PDFLIB.