# -*- coding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
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
#
#
#
#     Autor: Andres Ignacio Báez Alba
#
#
##############################################################################


class campo():
    def __init__(self):
        self.nombre=""
        self.valor=""

class registro():
    def __init__(self):
        self.listaCampos=[]
    def set_modelName(self,modelName):
        self._model_name = modelName
    def get_modelName (self):
        return self._model_name
    def set_key(self,key):
        self._key = self._model_name+"_"+key
    def get_key(self):
        return self._key

class xml_datalayer:
    """
    Sirve para generar fichero xml para cargue de datos en openerp
    """
    def __init__(self):
        self._listaRegistros=[]
        self.model=""
        self._xml=""
        
    def add_registro(self,registro,key):#La clave es valor de un codigo llave primaria listo!
        registro.set_modelName(self.model)
        registro.set_key(key)
        self._listaRegistros.append(registro)
        
    def obtener_registro(self,key):
        r_key = self.model+"_"+key
        for reg in self._listaRegistros:
            if (reg.get_key() == r_key):
                return reg
        return {}

    def generarXML(self):
        st = '<?xml version="1.0" encoding="UTF-8"?>\
        \n<openerp>\
        \n<data>\n'
        i=0
        for reg in self._listaRegistros:
            i=i+1
            st = st + "    <record model='"+self.model+"' id='"+str(reg.get_key())+"'>\n"
            for camp in reg.listaCampos:
                st = st + "        <field name='"+camp.nombre+"'>"+str(camp.valor)+"</field>\n" #<field name='name'>2</field> 
            st = st + "    </record>\n"
        st = st + "</data>\n</openerp>"
        self._xml = st
        return self._xml
    
    def obtenerXML(self):
        return self._xml
    
