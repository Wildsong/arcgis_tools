"""
    Update all the maps in an APRX project
    so that the databases are correct.
"""
import os
from arcgis.gis import Datastore
import arcpy
from config import Config

oldserver = 'cc-gis'
newserver = 'cc-thesql'

old_sde_password = 'CCgis97103'
new_sde_user     = 'sde'
new_sde_password = 'Clatsop.97103'

olddatabase = 'Clatsop'
newdatabase = 'gis-sandbox'


def dump_layer(item):
    try:
        print("Layer: \"%s\"" % item.name)
    except Exception as e:
        pass

    try:
        sublayers = item.listLayers()
        if len(sublayers):
            print("--- sublayers (%d) ---" % len(sublayers))
            for layer in sublayers:
                dump_layer(layer)
            pass
    except Exception as e:
        pass

    if item.isWebLayer:
        print("   web layer")
        return
    if item.isGroupLayer:
        print("  group layer")
        return
    if item.isBasemapLayer:
        print("  basemap")
        return

    try:
        props = item.connectionProperties
        #cim = item.getDefinition('V2')
        if props:
            print("  ", props)            

    except Exception as e:
        print(e)
        pass

    return


def updateTable(item):
    fixed = 0

    try:
        print("Table: \"%s\"" % item.name)
    except Exception as e:
        pass
        
    try:
        props = item.connectionProperties
        #cim = item.getDefinition('V2')
        if props:
            connection = props['connection_info']

        if 'db_connection_properties' in connection and connection['db_connection_properties'] == oldserver:
            print('updating table')
            new_props = {
                'connection_info': {
                    'db_connection_properties': newserver,
                    'server': newserver,
                    'instance': f'sde:sqlserver:{newserver}',
                    'database': newdatabase,
                }
            }
            if connection['authentication_mode'] == 'DBMS':
#                new_props['connection_info']['authentication_mode'] = 'DBMS'
                new_props['connection_info']['user'] = new_sde_user
                new_props['connection_info']['password'] = new_sde_password

            item.updateConnectionProperties(props, new_props, validate=False, ignore_case=False)
            fixed += 1

    except Exception as e:
        print(e)
        pass

    return fixed

def updateLayer(item):
    fixed = 0

    try:
        print("Layer: \"%s\"" % item.name)
    except Exception as e:
        pass

    try:
        sublayers = item.listLayers()
        if len(sublayers):
            print("--- sublayers (%d) ---" % len(sublayers))
            for layer in sublayers:
                fixed += updateLayer(layer)
            pass
    except Exception as e:
        pass

    if item.isWebLayer:
        print("   web layer")
        return fixed
    if item.isGroupLayer:
        print("  group layer")
        return fixed
    if item.isBasemapLayer:
        print("  basemap")
        return fixed

    try:
        props = item.connectionProperties
        #cim = item.getDefinition('V2')
        if props:
            connection = props['connection_info']
            print("  ", props['dataset'])

        if 'db_connection_properties' in connection and connection['db_connection_properties'] == oldserver:
            print('updating layer')

            # In theory you only want to put the properties that are changing here.
            # props is how we find the right layer, new_props is what we change
            new_props = {
                'connection_info': {
#                    'authentication_mode': 'OSA',
                    'db_connection_properties': newserver,
                    'server': newserver,
                    'instance': f'sde:sqlserver:{newserver}',
                    'database': newdatabase,
                }
            }
            
            if connection['authentication_mode'] == 'DBMS':
 #               new_props['connection_info']['authentication_mode'] = 'DBMS'
                new_props['connection_info']['user'] = new_sde_user
                new_props['connection_info']['password'] = new_sde_password

            print(props)
            print(new_props)

            # Check also for joins and relates here.

            item.updateConnectionProperties(props, new_props, validate=False, ignore_case=False)
            fixed += 1

    except Exception as e:
        print(e)
        pass

    return fixed


def dump_aprx(aprx):
    for map in aprx.listMaps():
        print("===== Map \"%s\" =====" % map.name)
        for layer in map.listLayers():
            dump_layer(layer)
    print("EOF")
    print("")

def update_aprx(aprx):
 
    
    oldsde = "cc-gis-Clatsop.sde"
    newsde = "cc-thesql-gis-sandbox.sde"

    oldsde_osa = "cc-gis-Clatsop-OSA.sde"
    newsde_osa = "cc-thesql-gis-sandbox-OSA.sde"

    if True:
        assert(os.path.exists(oldsde))
        assert(os.path.exists(newsde))
        assert(os.path.exists(oldsde_osa))
        assert(os.path.exists(newsde_osa))

        aprx.updateConnectionProperties(oldsde, newsde, validate=False)
        dump_aprx(aprx)

        aprx.updateConnectionProperties(oldsde_osa, newsde_osa, validate=False)
        dump_aprx(aprx)

        fixed = 1
    else:
        fixed = 0
        for map in aprx.listMaps():
            print("-----------------------------------Map: %s------------------------------" % map.name)
            for layer in map.listLayers():
                fixed += updateLayer(layer)
            for table in map.listTables():
                fixed += updateTable(table)
            print()

    return fixed

# --------------------------------------------------------------------------------------------

if __name__ == "__main__":

    print(os.getcwd())

    os.chdir('Update_desktop_projects/sample_pro')

    aprxpathname = "MyProject1.aprx"
    #aprxpathname = "K:/webmaps/basemap/basemap.aprx"

    aprx = arcpy.mp.ArcGISProject(aprxpathname)
    print("APRX:", aprxpathname)
    dump_aprx(aprx)

    path, file  = os.path.split(aprxpathname)
    f,e = os.path.splitext(file)
    aprxnew = os.path.join(path, f + '_' + newserver + e)
    if os.path.exists(aprxnew): 
        try:
            os.unlink(aprxnew)
        except Exception as e:
            print("You probably have the APRX file open in Pro, right?", e)
            exit(1)


    fixed = update_aprx(aprx)

    if fixed > 0:
        aprx.saveACopy(aprxnew)

