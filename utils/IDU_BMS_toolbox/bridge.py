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
#
###############################################################################

import xmlrpclib
import arcpy


class BridgeCollection():
    def __init__(self):
        self._bridges=[]
        self.isLoggedIn=False
    def add_bridge(self,Bridge):
        self._bridges.append(Bridge)
            
    def export_to_openerp(self,user,pwd,dbname,openerp_server):               
        if not self.isLoggedIn:
            uid=0
            arcpy.AddMessage("Loggin into Openerp")            
            sock_login = xmlrpclib.ServerProxy(openerp_server+"common")
            uid = sock_login.login(dbname,user,pwd)
            if not uid == 0:
                self.isLoggedIn = True
            else:                
                raise Exception("Could not loggin in Openerp")
        for Bridge in self._bridges:
            elem_to_send = {}
            #Prevent to send null parameters
            arcpy.AddMessage("Checking values to send...")
            for elem in Bridge.get_values():
                value = str(Bridge.get_values()[elem])
                if not ((value == "") or (value =="None")):
                    #arcpy.AddMessage("Value :"+value)
                    elem_to_send[elem]=Bridge.get_values()[elem]                    
            sock = xmlrpclib.ServerProxy(openerp_server+"object")
            arcpy.AddMessage("Sending Bridge "+str(Bridge.get_local_id()) +" to Openerp WS ..")
            retVal = sock.execute(dbname, uid, pwd, 'urban_bridge.bridge','web_service_save', elem_to_send)                        
            for val in retVal:
                arcpy.AddMessage(str(val)+" : "+str(retVal[val]))                
        return 0


class Bridge():
    def __init__(self,
                 SHAPE,
                 CODE=None,
                 NAME=None,
                 CATEGORY=None,
                 STRUCTURE_TYPE=None,
                 ADDRESS=None,
                 LAST_ADDRESS=None,
                 CONSTRUCTION_DATE=None,
                 LENGTH=None,
                 WIDTH=None,
                 SUPERSTRUCTURE_AREA=None,                 
                 VERTICAL_GAUGE=None,
                 HORIZONTAL_GAUGE=None,
                 DESIGN_LOAD_CAPACITY=None,
                 LEVEL=None,
                 STRUCTURE_MATERIAL=None,
                 DESIGN_LOAD_CODE=None):                
        self.set_values(SHAPE,
                 CODE,
                 NAME,
                 CATEGORY,
                 STRUCTURE_TYPE,
                 ADDRESS,
                 LAST_ADDRESS,
                 CONSTRUCTION_DATE,
                 LENGTH,
                 WIDTH,
                 SUPERSTRUCTURE_AREA,                 
                 VERTICAL_GAUGE,
                 HORIZONTAL_GAUGE,
                 DESIGN_LOAD_CAPACITY,
                 LEVEL,
                 STRUCTURE_MATERIAL,
                 DESIGN_LOAD_CODE)
        self.isLoggedIn=False
        
    def set_values(self,
                 SHAPE,
                 CODE=None,
                 NAME=None,
                 CATEGORY=None,
                 STRUCTURE_TYPE=None,
                 ADDRESS=None,
                 LAST_ADDRESS=None,
                 CONSTRUCTION_DATE=None,
                 LENGTH=None,
                 WIDTH=None,
                 SUPERSTRUCTURE_AREA=None,                 
                 VERTICAL_GAUGE=None,
                 HORIZONTAL_GAUGE=None,
                 DESIGN_LOAD_CAPACITY=None,
                 LEVEL=None,
                 STRUCTURE_MATERIAL=None,
                 DESIGN_LOAD_CODE=None):
        b_category = ""
        if CATEGORY == 1:
            b_category = "PVE"
        elif CATEGORY == 2:
            b_category = "PPE"
        elif CATEGORY == 3:
            b_category = "PVC"
        else:
            b_category = "PPC"
        stype = None
        try :
            stype = int(STRUCTURE_TYPE)            
        except Exception as e:
            print e
            stype = 0
        if STRUCTURE_TYPE == None or STRUCTURE_TYPE == "":
            STRUCTURE_TYPE="0"
        self.__values = {            
            "shape":SHAPE,
            "code":CODE,
            "name":NAME,
            "category":b_category,
            "structure_type":str(stype),
            "address":ADDRESS,
            "last_address":LAST_ADDRESS,
            "construction_date":str(CONSTRUCTION_DATE),
            "length":LENGTH,
            "width":WIDTH,
            "superstructure_area":SUPERSTRUCTURE_AREA,
            "vertical_gauge":VERTICAL_GAUGE,
            "horizontal_gauge":HORIZONTAL_GAUGE,
            "design_load_capacity":DESIGN_LOAD_CAPACITY,
            "level":str(LEVEL),
            "structure_material":STRUCTURE_MATERIAL,
            "design_load_code":DESIGN_LOAD_CODE,    
        }  
    def get_values(self):
        return self.__values

    def print_features(self):
        val = ""
        for feat in self.__values:
            val = val + str(feat)+ " : "+str(self.__values[feat]) +"\n"
        return val
    def get_bridge_name_and_code(self):
        bridge = "Name : "
        if self.__values.has_key("name"):
            bridge = bridge +str(self.__values["name"])
        else :
            bridge = bridge + "Not defined"
        bridge = bridge + " Code : "        
        if self.__values.has_key("code"):
            bridge = bridge + str(self.__values["code"])
        else :
            bridge = bridge + "Not defined"        
        return bridge 
    def set_local_id(self,ID):
        self._local_id = ID
    def get_local_id(self):
        return self._local_id


