# PDFlib

Check for missing PDFlib files
to avoid having broken links in webmaps.

1. Build a list of needed files from taxlots GIS layer
2. See if the referenced taxmap files exist
3. List any that are missing

## Deployment

I run this once a week as a cronjob
and so its output is automatically emailed to me.

The .env file has to be written as a shell file in
~/.conda/env
