#!/bin/bash

conda activate arcgis_tools

# Esri throws a warning message about our self-signed certificate
# fortunately on STDERR so we just ignore STDERR output.

python /home/gis/bin/check_pdflib.py 2> /dev/null

