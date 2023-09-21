# arcgis_tools
Python tools automating day-to-day tasks with ArcGIS Enterprise

My intention is to collect the tools that I am writing here in this repository.

The apps.code-workspace file here helps me to edit our apps and our maps.


## Set up

Visual Studio Code, which allows me to specify a Conda environment as a setting.

My approach is to tell Conda I want 'arcgis' and then let conda dependencies install everything else, s
electing the version of python, pandas, etc that it wants. This way everything will work together.

I am relying on features in version 2.x of arcgis python api.

You need python-dotenv to run from command line, and autopep8 to keep VS Code happy.

I hate cloning the old ArcGIS Pro environment because then it's painful to upgrade.
Currently, arcgis and arcpy will determine which (out of date) version of python will be selected.
Today it's taking infinite time to 'conda install arcpy' so I am using 'clone'. Sigh.

    conda create -n arcgis_tools --clone arcgispro-py3
    conda activate arcgis_tools
    conda install autopep8 python-dotenv requests

This process gives the warnings about an inconsistent environment but when I am done, everything seems to work okay. 

Note: The opencv package is currently only needed to generate thumbnails.
Not sure what I was doing with Rocket-python... it can send messages to a chat client, 
maybe I wanted to do progress reports, a great idea actually.

Optionally, install these:

    conda activate arcgis_tools
    conda install opencv
    pip install rocket-python

On a server there is a different package for arcgpy, see https://enterprise.arcgis.com/en/server/latest/develop/linux/scripting-service-publishing-with-arcpy.htm
Refer to that page for the very limited list of things you can do with arcpy on a server. Probably not worth the bother
but here is how to install:

    conda install -n arcgis_tools arcpy-server=10.9 -c esri

## PDFlib

Checks for missing taxmaps

## Septic_Status

Updates the "septic y/n" attribute in taxlots_accounts feature class.

## Transit_update

Updates the (hosted) transit layer(s) on cc-gis.

## Update_web_maps

Mostly tools for replacing parts of the map JSON files.
Has its own README.

## Vector tiles and labels

A series of tests to see what I should be doing to publish vector features and labels.

* test.aprx
* test.fgdb contains test data set, currently a small subset of taxmap data.


## Taxmap popup HTML


<a href="{expression/PHOTO}" rel="nofollow" target="_blank"><img src="{expression/THUMBNAIL}"></a>

<table border="0" style="width:100%"><tbody>
<tr>
<td style="width:25%;padding:3px"><font color="#808080">Account</font></td>
<td style="padding:3px"><a href="https://apps.co.clatsop.or.us/property/property_details/?a={ACCOUNT_ID}" rel="nofollow" target="_blank">{ACCOUNT_ID}</a><br>
</td></tr>

<tr>
<td style="padding:3px"><font color="#808080">Taxmap</font></td>
<td style="padding:3px"><a href="https://delta.co.clatsop.or.us/taxmaps/tp{TAXMAPNUM}.pdf" rel="nofollow" target="_blank">{SIMapTax}</a><br></td>
</tr>

<tr>
<td style="vertical-align:top;padding:2px"><font color="#808080">Owners</font></td>
<td style="padding:2px">{expression/OWNERS_3LINE}
</td></tr>

<tr>
<td style="vertical-align:top;padding:3px"><font color="#808080">Mailing</font></td>
<td style="padding:2px">{expression/MAILING_ADDRESS} <br></td></tr>

<tr>
<td style="vertical-align:top;padding:3px"><font color="#808080">Google Map</font></td>
<td style="padding:2px">
<a href="https://www.google.com/maps/place/{expression/GOOGLE_QUERY}" rel="nofollow" target="_blank">{expression/GOOGLE_TXT}</a>
</td></tr>

<tr>
<td style="vertical-align:top;padding:3px"><font color="#808080">Bing Street View</font></td>
<td style="padding:2px">
<a href="https://bing.com/mapspreview?lvl=17&style=x&cp={expression/BING_QUERY}">{expression/BING_TXT}</a>
</td></tr>

</tbody></table>

## Expressions

//GOOGLE_QUERY
var addr=Trim($feature.SITUS_ADDR);
var city=Trim($feature.SITUS_CITY);
if (addr!='' && city!='') {
  var situs=addr + ', ' + city + ', OR';
  return Replace(situs,' ','+');
}
return Round($feature.Y_COORD,4) + ',' + Round($feature.X_COORD,4)

//GOOGLE_TEXT
var addr=Trim($feature.SITUS_ADDR);
if (addr!='') {
  return addr;
}
return Round($feature.Y_COORD,4) + ',' + Round($feature.X_COORD,4)

//BING_STREET_QUERY
//https://learn.microsoft.com/en-us/bingmaps/articles/create-a-custom-map-url
var x=Round($feature.X_COORD,4);
var y=Round($feature.Y_COORD,4);
return y + '~' + x; 

//BING_STREET_TXT
//https://learn.microsoft.com/en-us/bingmaps/articles/create-a-custom-map-url
var x=Round($feature.X_COORD,4);
var y=Round($feature.Y_COORD,4);
return y + ',' + x; 

## Tests

https://www.google.com/maps/place/125+W+Lexington+Ave%2C+Astoria%2C+OR

https://www.google.com/maps/place/46.1799%2C-123.8448

## EGeoDatabase Database Stats

Connect to the database server in SQL Studio Manager and load and run
geodatabase_version_report.sql. 

I copied it from https://support.esri.com/en/technical-article/000017513

