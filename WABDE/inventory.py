"""

After an upgrade of WABDE, 
the updater renumbered the apps so 
now I am wondering what the heck
which one is which and where are they 
and all that.

I think all I need to do is find each config.json file
and read its title field.

"""
import sys
import os
import json
from glob import glob
import pprint

workspace = '/home/gis/docker/wabde/'

for something in glob(workspace) :
    pprint.pprint(something)

