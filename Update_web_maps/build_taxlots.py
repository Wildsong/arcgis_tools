


# Templates for operational layers

field_template = {
    "fieldName": "OBJECTID",
    "label": "OBJECTID",
    "isEditable": False,
    "tooltip": "",
    "visible": False,
    "stringFieldOption": "textbox"
}
expressionInfo_template = {
    "name": "", # Name of this expression
    "title": "", # Title, not really used anywhere
    "expression": "", # An expression in Arcade
    "returnType": "string", # Always "string" AFAIK 
}
popupInfo_template = {
    "title": "Taxlot:{TAXLOTKEY}", # Typically has a variable name in it.
    "fieldInfos": [], # A list of field definitions
    "description": "", # HTML for popup
    "showAttachments": True,
    "expressionInfos": []
}

# A "Map Service Layer" lives in the Server at a URL
# and has one or more layers
# Each layer can have a popup.

mapServiceLayer_template =     {
      "id": "Zoning_8752",
      "layerType": "ArcGISMapServiceLayer",
      "url": "https://delta.co.clatsop.or.us/server/rest/services/Zoning/MapServer",
      "visibility": False,
      "opacity": 1,
      "title": "Zoning",
      "itemId": "42f8e83a1449452c8da8c9f71ca638de",
      "layers": [
        {
          "id": 0,
          "name": "Zoning",
          "showLabels": true,
          "popupInfo": {
            "title": "Zoning, County:",
            "fieldInfos": [], # A list containing fields (see field_template)
            "description": "", # HTML
            "showAttachments": False,
            "mediaInfos": []
          }
        },
        {
          "id": 1,
          "name": "Zoning, Astoria",
          "showLabels": true,
          "popupInfo": popupInfo_template, 
          }
        },

# A Feature Layer has only one data source
# It can have a popup defined in the actual service, designed in ArcGIS Pro
# but if there is one here it overrides that one.
#
# They have to go at the top of the stack.

featureLayer_template = {
    "id": "Taxlots_2409", # Be careful defining this, it's referenced in widgets sometimes
    "layerType": "ArcGISFeatureLayer", # Not defined for WMS service layer
    "url": "https://delta.co.clatsop.or.us/server/rest/services/Taxlots/FeatureServer/1",
    "visibility": 'true',
    "opacity": 1,
    "mode": 1,
    "title": "Taxlots",
    "itemId": "4946b9334ae64e518c081829d53c561e",
    "layerDefinition": {
    "drawingInfo": {
        "renderer": {
        "type": "simple",
        "label": "",
        "description": "",
        "symbol": {
            "color": [
            0,
            0,
            0,
            0
            ],
            "outline": {
            "color": [
                168,
                168,
                0,
                255
            ],
            "width": 0.75,
            "type": "esriSLS",
            "style": "esriSLSSolid"
            },
            "type": "esriSFS",
            "style": "esriSFSSolid"
        }
        }
    },
    "popupInfo": popupInfo_template,
    "mediaInfos": [], # Attachments maybe???
} 