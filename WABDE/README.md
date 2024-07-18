# WABDE tools

## Inventory tools

Look in each server/apps/ folder (eg 2.29/server/apps/) for each numbered app folder.
Read the config.json file and show the "title" property.

Look in server/db/apps which is a JSON file.

## Upgrading to a new WABDE release

I am trying to upgrade to 2.29 using the official script, I tried following
the simple instructions (step 3 below) but it failed on many apps.

My improved workflow:

1. Unzip the new version into its version numbered folder (eg 2.29/)

At this point, there is no server/db/ folder. It won't be created until step 6

2. Copy the modified and extra widgets into client/stemapp/widgets.
Note there is no PopupPanel or SaveSession by default. Add them.
See also the ones that start with CC_

3. Do the update.
Do this only one time. Each time you run it, it will create more copies of the apps.

    cd server/
    node upgrade.js ../../2.24

Glory in the fact that after installing the widgets and running the upgrade,
**there were no error messages!**

4. Run an inventory to see if you can tell what it did.

There are now 14 apps in 2.29

5. Consider the server/db/apps json file. It must be telling us something.

6. Launch wabde container, see if it worked.

    Edit the bind mount in "compose.yaml" to point at 2.29
    docker compose up -d

Yesterday's results were less encouraging. Before, 14 apps; after? 6 :-(
Also there wer about a dozen broken ones.

It looks like it skipped every app that had a custom widget.
Which is all of the important ones.

This is the inventory from 2.24 before I did the upgrade.
The * mark problems reported in the update

32  Clatsop County Webmaps App * PopupPanel 2.17, SaveSession.211
33  Planning App * PopupPanel 2.17, SaveSession 2.11
35  Recology App * SaveSession 2.11
20  Assessment and Taxation Webmaps App * PopupPanel 2.17 
22  Public Works Road App
31  Clatsop Affordable Housing Web App (zhunt)
30  Clatsop Affordable Housing Inventory | Web Map
25  Resiliency App
24  Public Works Road App
15  app-Planning-County_Properties
8  Tsunami Signs App

The 2.29 folder now has this

2.29
  33 "Tsunami Signs App"
  31 "Resiliency App"
  28 Clatsop County Public Works Road App
  32 "Clatsop County Planning"
  30 "Clatsop Affordable Housing Inventory"
  29 "Clatsop Affordable Housing Web App"

It's referencing outdated content somehow in the web ui,
how? Running the updater must create that table.

It looks like it used older PopupPanel and SaveSession widgets.
I suspect it downloaded them from Esri since they were not in the ZIP file.

PopupPanel 2.13 --> 2.17
SaveSession 2.7 --> 2.11

Version 2.7 is "official":
https://github.com/softwhere/SaveSession-Widget/blob/master/README.md

See Simo Xu version here:
https://community.esri.com/t5/web-appbuilder-custom-widgets-documents/savesession-that-supports-heavy-map-layers-and/ta-p/913976

Download from https://community.esri.com/ccqpr47374/attachments/ccqpr47374/web-appbuilder-custom-widgetstkb-board/4546/1/SaveSession.zip
