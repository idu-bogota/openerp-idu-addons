# -*- coding: utf-8 -*-
##############################################################################
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
# INSTITUTO DE DESARROLLO URBANO - BOGOTA (COLOMBIA)
#  Copyright (C) 2013
# Customization developed by:
# ANGEL MARIA FONSECA CORREA - CIO
# ANDRES IGNACIO BAEZ ALBA - Engineer of Development
# CINXGLER MARIACA MINDA - Engineer of Development - Architect
# Load Script
###############################################################################
import arcpy
import bridge
#from shapely.geometry import asShape
########################################################
#1.0 Parameter Definition
########################################################+
#1.1 Parameter 1 Workspace
workspace = arcpy.GetParameterAsText(0)
#workspace="D:\\Users\\cabaezal1\\Documents\\ArcGIS\\SIGIDU_Prod.sde"
arcpy.AddMessage("workspace: "+workspace)
#1.2 Parameter 2. TableName"
tableName = arcpy.GetParameterAsText(1)
#tableName="OW_SIGPROD.SIG_PUENTE_PEATONAL"
#tableName="OW_SIGPROD.SIG_PUENTE_VEHICULAR"
arcpy.AddMessage("tableName: "+tableName)
#1.3 Parameter 3. ObjectID
objectID = arcpy.GetParameterAsText(2)
#objectID=0
arcpy.AddMessage("ObjectID: "+str(objectID))
#1.4 Parameter 4. Server
server = arcpy.GetParameterAsText(3)
#server="I01833"
arcpy.AddMessage("Server: "+server)
#1.5 Parameter 5. Port
port = arcpy.GetParameterAsText(4)
#port = 8069
arcpy.AddMessage("Port: "+str(port))
#1.6 User Name
user_name = arcpy.GetParameterAsText(5)
arcpy.AddMessage("User Name: "+user_name)
#1.7 Password+
password = arcpy.GetParameterAsText(6)
arcpy.AddMessage("Password: "+password)
#1.8 Database Name
database_name=arcpy.GetParameterAsText(7)
#database_name="bms2"
arcpy.AddMessage("Database: "+database_name)
##################################
# Internal Parameter
##################################
coordinateSystem="D:\\Users\\cabaezal1\\Documents\\ArcGIS\\WGS 1984 Web Mercator.prj"
#######################################################
# 2.0 Getting Data from Table
#######################################################
openerp_server_url="http://"+server+":"+str(port)+"/xmlrpc/" 
arcpy.AddMessage("Setting Workspace")
arcpy.env.workspace=workspace
arcpy.Describe(tableName)

arcpy.AddMessage("Searching Bridge..")
arcpy.AddMessage("server : "+openerp_server_url)
try:
    rows = []
    if not ((objectID == "" or objectID == "None") or str(objectID) == "0"):
        search = "OBJECTID = "+str(objectID)
        rows = arcpy.SearchCursor(tableName,search,coordinateSystem)
    else :
        rows = arcpy.SearchCursor(tableName,"",coordinateSystem)
    bc = bridge.BridgeCollection() 
    for row in rows:
        arcpy.AddMessage("Adding Bridge to List "+ str(row.OBJECTID))       
        feat=row.getValue("SHAPE")
        shape=feat.__geo_interface__
#         geo = asShape(shape)
#         print geo.wkt
        current_Bridge = bridge.Bridge(shape,
                                row.PUENTE,
                                str(row.NUMERO)+"_"+str(row.CO_VI)+"_"+str(row.ELEM)+"_"+str(row.CIV),
                                row.TI_PU,
                                row.TIPO,
                                ADDRESS=row.DIRECCION,
                                LAST_ADDRESS=row.DIRECCION_ANTIGUA,
                                CONSTRUCTION_DATE=row.FECHA_CONSTRUCCION,
                                LENGTH=row.LONGITUD,
                                WIDTH=row.ANCHO,
                                SUPERSTRUCTURE_AREA=row.AREA_PUENTE,
                                VERTICAL_GAUGE=row.GALIBO,
                                LEVEL=row.PTE_NIVEL,
                                )
        current_Bridge.set_local_id(row.OBJECTID)                
        bc.add_bridge(current_Bridge)
    arcpy.AddMessage("Exporting Data to Openerp")
    bc.export_to_openerp(user_name,password, database_name, openerp_server_url)
     
except Exception as e:    
    arcpy.AddError(e)
    print e
    raise e
arcpy.AddMessage("Finish Successfully")
