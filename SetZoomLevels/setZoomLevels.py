"""
@date:   8/1/2018 4:21:18 PM
@author: bwilson
"""
import os
import sys
import logging
import arcpy

scale_ranges = [
    (     0,    1129), #zoom 19
    (  1130,    2258), #zoom 18
    (  2259,    4515), #zoom 17
    (  4516,    9029), #zoom 16
    (  9030,   18057), #zoom 15
    ( 18058,   36113), #zoom 14
    ( 36114,   72225), #zoom 13
    ( 72226,  144449), #zoom 12
    (144450,  288897), #zoom 11
    (288898,  577792), #zoom 10
    (577793, 1155580), #zoom 9
    ]

def set_zoom_levels(df):
    for layer in arcpy.mapping.ListLayers(mxd, "Zoom *", df):
        scale = layer.name[5:7]
        i = 19 - int(scale)
        print("%s Scale = %s index=%d" % (layer.name, scale, i))
        (max,min) = scale_ranges[i]
        layer.minScale = min
        layer.maxScale = max
        print(min,max)
    arcpy.RefreshActiveView()

# ===================================================================================
mxd = arcpy.mapping.MapDocument("CURRENT")
df = mxd.activeDataFrame

if __name__ == "__main__":

    import config

    MYNAME  = os.path.splitext(os.path.split(__file__)[1])[0]
    LOGFILE = MYNAME + ".log"
    logging.basicConfig(filename=LOGFILE, level=logging.DEBUG, format=config.LOGFORMAT)
    print("Writing log to %s" % LOGFILE)

# That's all!
