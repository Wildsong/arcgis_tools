"""
I am looking for maps that use the old style popups with the photoshow service.
I need to update the references before I can shut down the service.
"""
import os

# Here is a list of maps that contain the "Taxlots" service.
# I generated this by running find_map_layers.py searching for the layer title "Taxlots"
maps = [
    ("47509878f8a048ec848737ba7e3ec5c6", "Planning map - county owned properties-transit"),
    ("34d3d5617ff6444da708e22ba39ce94a", "Planning map - county owned properties- EDIT"),
    ("96f9001036e149eeaa061f89a8a3e399", "Clatsop Affordable Housing Web Map_ARCHIVE"),
    ("636c926661b743e4af86ab68757a8f98", "widget test map"),
    ("28adc44a1f4f45489f6592ce4395cbbb", "Clatsop Housing Development Web Map_ARCHIVE"),
    ("43c4315eac124fc588d433e37bb18e05", "Redistricting WebMap"),
    ("07252886a92749cb9d812d90c76fc5dd", "nh Clatsop County Webmaps-Copy"),
    ("3d43802eade5432ea5b5650a6c2ae6b4", "Map for the Home Page"),
    ("08add94661734a21add21657afbe7768", "A&T map-Copy for testing 2020"),
    ("69cdb271d3d44cda97004f006df8efe2", "Planning map - county owned properties"),
    ("f42ac39d639d484d9ae0174844adabc8", "Affordable Housing Inventory-Backup Copy"),
    ("ba5d38a16a4841d9a85eec770fa79040", "Clatsop County Public Works Road Map - Web Map"),
    ("e9af4d3d0e1c46db9d49a28737898c6a", " Public Works Road App - Web Map"),
    ("3858169ab451482c9460d897e05e696c", "A&T map"),
    ("8220470e7d8141ada9917eb31a42c107", "Clatsop County Map Template"),
    ("8ffcbe43ac8645e383800b1836986189", "Clatsop Housing Development Web Map"),
    ("4decd6e535d64b8797a48052e5091005", "Clatsop Affordable Housing Web Map"),
    ("bb5debcf14db4c48bbd4c54fc0fc207f", "Planning Map"),
    ("f84321f3545643adaadf889ce70dc73e", "Clatsop County Webmaps"),
]

content="//CC-GIS/C$/arcgis/arcgisportal/content/items"

for item in maps:
    #print(f"Testing \"{item[1]}\".")
    path = os.path.join(content, item[0], item[0]) # File and folder, same name!
    if os.path.exists(path):
        with open(path, "r") as fp:
            text = fp.read()
        #print(text)
        if "photoshow" in text:
            print("YAY, we got one.", item[0], item[1])
            continue
    else:
        print(f"ERROR: No content file called \"{item[0]}\" exists.")
        continue

# This resulted in just 2 matches so I hand repaired them in VSCode.

print("That's all!")