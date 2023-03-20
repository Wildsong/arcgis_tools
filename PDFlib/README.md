# PDFlib

Check for missing PDFlib files
to avoid having broken links in webmaps.

1. Build a list of needed files from taxlots GIS layer
2. See if the referenced taxmap files exist
3. List any that are missing

## Deployment

I run this once a week as a cronjob
and so its output is automatically emailed to me.

The environment is supported via conda, so refer to
~/.conda/envs/arcgis_tools/etc/conda/activate.d/env_vars.sh
for PORTAL_* and SERVER_URL.

Credentials for the file server are handled through
the automounter, so refer to /etc/creds/
