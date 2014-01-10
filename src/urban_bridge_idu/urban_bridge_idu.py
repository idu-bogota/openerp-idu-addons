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
# INSTITUTO DE DESARROLLO URBANO - BOGOTA (COLOMBIA)
#
# Customization developed by:
# ANGEL MARIA FONSECA CORREA - CIO
# ANDRES IGNACIO BAEZ ALBA - Engineer of Development
# CINXGLER MARIACA MINDA - Engineer of Development - Architect
#
###############################################################################
from osv import fields,osv
from base_geoengine import geo_model
from tools.translate import _
from tools.translate import translate

class urban_bridge_bridge(geo_model.GeoModel):
    """ 
    Bridge Infraestructure Data
    """

    def get_ddl_module(self,cr,uid,context=None):
        """
        Web Service que sirve para enviar la definición de datos (DDL) en formato JSON, esto sirve para crear una geodatabase a partir de los datos
        y luego realizar una exportación masiva de los mismos
        
        Estructura de los datos en JSON que se va a retornar:
        {
            objeto o feature class:{campo1:{nombre:"nombre(español)", nom_pres:"Nombre de Presentación del Objeto",tipo_dato:"Tipo Dato",}, campo2:{}.....
        }
        ejemplo:
        {
            puente:{id:{"nombre":"id","nom_pres":identificador,"tipo_dato":"integer"},
                    width:{"nombre":"ancho","nom_pres":"Ancho","tipo_dato":"float"}
            ...
            }
            riostra:{id:{"nombre":"id","nom_pres":identificador,"tipo_dato":"integer"},
            }
        }
        
        """
        res={}
        #1. Se envian la lista de los campos que estan involucrados en el objeto puentes
        puente={}
        fields = self.fields_get(cr,uid,context)
        for field in fields:
            campo = translate(cr,"addons/urban_bridge/urban_bridge.py","code","es_CO",field)
            nombre_presentacion = translate(cr,"urban_bridge.bridge,"+field,"field","es_CO",fields[field]["string"])
            if (nombre_presentacion==False):
                nombre_presentacion = fields[field]["string"]
            tipo_dato = fields[field]["type"]
            if (campo == False):
                raise Exception("Campo :'"+field+"' no se encuentra definido en fichero de traduccion es_CO.po, verifique que se encuentre el campo en el fichero\
                y actualice el módulo")
            if (tipo_dato=="selection"):
                puente[field] = {'nom_pres':nombre_presentacion,"tipo_dato":tipo_dato,"nombre":campo,"selection":str(fields[field]["selection"])}
            #Convertir los elementos many 2 one en un dominio tipo selection
            elif (tipo_dato == "many2one"):
                objeto_rel = self.pool.get(fields[field]["relation"])
                try:
                    objetos_rel_ids = objeto_rel.search(cr,uid,[('id','>','0')])
                    campos_seleccion = []
                    for code_value_obj in objeto_rel.browse(cr,uid,objetos_rel_ids):
                        campos_seleccion.append((str(code_value_obj.code),str(code_value_obj.name)))
                    puente[field] = {'nom_pres':nombre_presentacion,"tipo_dato":"selection","nombre":campo,"selection":str(campos_seleccion)}
                except Exception as e:
                    print str(e)
            else:
                puente[field] = {'nom_pres':nombre_presentacion,"tipo_dato":tipo_dato,"nombre":campo}
        res["puente"] = puente
        #2, Definición de datos de cada uno de los elementos de infraestructura
        #2.1 Campos comunes que se encuentran definidos de manera general en el elemento de infraestructura
        struct_elem = self.pool.get('urban_bridge.structure_element')
        elem_fields = struct_elem.fields_get(cr,uid,context)
        common_fields={}
        for elem_field in elem_fields:
            campo = translate(cr,"addons/urban_bridge/urban_bridge.py","code","es_CO",elem_field)
            #Nombre con el cual se ve el campo en la pantalla
            nombre_presentacion = translate(cr,"urban_bridge.structure_element,"+elem_field,"field","es_CO",elem_fields[elem_field]["string"])
            if (nombre_presentacion==False):
                nombre_presentacion = elem_fields[elem_field]["string"]
            
            if (campo == False):
                raise Exception("Campo :'"+elem_field+"' no se encuentra definido en fichero de traduccion es_CO.po, verifique que se encuentre el campo en el fichero\
                y actualice el módulo")
            
            tipo_dato = elem_fields[elem_field]["type"]
            if (tipo_dato=="selection"):
                common_fields[elem_field] = {'nom_pres':nombre_presentacion,"tipo_dato":tipo_dato,"nombre":campo,"selection":str(fields[field]["selection"])}
            elif (tipo_dato=="many2one"):
                common_fields[elem_field] = {'nom_pres':nombre_presentacion,"tipo_dato":"integer","nombre":campo}
            else:
                common_fields[elem_field] = {'nom_pres':nombre_presentacion,"tipo_dato":tipo_dato,"nombre":campo}
        #2.2 Campos definidos de manera particular para cada campo
        struct_elem_type_obj = self.pool.get('urban_bridge.structure_element_type')
        struct_elem_type_ids = struct_elem_type_obj.search(cr,uid,[('id','>','0')])
            #Estructura de datos para los elementos de infraestructura que se definen dinamicamente
        for struct_elem_type in struct_elem_type_obj.browse(cr,uid,struct_elem_type_ids):
            objeto = struct_elem_type.alias
            objeto_dict = {}
            for comfield in common_fields:
                objeto_dict[comfield]=common_fields[comfield]
            for attribute in struct_elem_type.attributes:
                if (attribute.data_type=="selection"):
                    objeto_dict[attribute.alias]={"nombre":str(attribute.alias),'nom_pres':str(attribute.name),"tipo_dato":str(attribute.data_type), "selection":str(attribute.selection_text)}
                else:
                    objeto_dict[attribute.alias]={"nombre":str(attribute.alias),'nom_pres':str(attribute.name),"tipo_dato":str(attribute.data_type)}
            #Agregar campo al diccionario
            res[objeto]=objeto_dict
        return res
    
    def get_data_module(self,cr,uid,bridge_id = None, context=None):
        """
        Web Service que devuelve todos los datos de los puentes junto con los elementos de infraestructura
        Modo de trabajo:
        
        Consulta cada puente y llena un diccionario con cada uno de los elementos de acuerdo a los nombres 
        que se implementaron en el método anterior
        ejemplo:
        {
        puente:{id:1,galibo:2,ancho:2.5 .....},
        riostra:{id:5,id_puente:1,ancho:2.5 .....} (depende de los datos de la base de datos)
        }
        """
        res = {}
        if (bridge_id == None):
            return res
        bridge_obj = self.pool.get('urban_bridge.bridge')
        bridge_dict = bridge_obj.read(cr,uid,bridge_id)
        puente = {}
        #1. Mandar el diccionario de valores para el objeto puente con los campos traducidos al español
        for attribute in bridge_dict:
            att_name = translate(cr,"addons/urban_bridge/urban_bridge.py","code","es_CO",attribute)
            if (att_name == False):
                att_name=attribute
            puente[att_name] = bridge_dict[attribute]
        res["puente"]=puente
        #2. Mandar un diccionario por cada objeto de infraestructura
        structure_element_obj = self.pool.get("urban_bridge.structure_element")
         
        bridge = bridge_obj.browse(cr,uid,bridge_id)
        for element in bridge.elements:
            element_dict = {}
            elem_type = element.element_type_id.alias
            elem_base = structure_element_obj.read(cr,uid,element.id)
            for elem_base_att in elem_base:
                base_att = translate(cr,"addons/urban_bridge/urban_bridge.py","code","es_CO",elem_base_att)
                if (base_att == False):
                    base_att = elem_base_att
                element_dict[base_att]=elem_base[elem_base_att]

            for values in element.values:
                attribute = values.element_attribute_id.alias
                data_type = values.element_attribute_id.data_type
                value=None
                if (data_type=="integer"):
                    value = values.value_integer
                elif (data_type=="text"):
                    value = values.value_text
                elif (data_type=="datetime"):
                    value = values.value_datetime
                elif (data_type== "date"):
                    value = values.value_datetime
                elif (data_type == "float"):
                    value = values.value_float
                elif (data_type=="boolean"):
                    value = values.value_boolean
                elif (data_type == "char"):
                    value = values.value_char
                elif (data_type == "selection"):
                    value = values.value_selection
                elif (data_type == "binary"):
                    value = values.value_photo
                elif (data_type == "geo_point"):
                    value = values.value_point.wkt
                elif (data_type == "geo_polygon"):
                    value = values.value_polygon.wkt
                elif (data_type == "geo_line"):
                    value = values.value_line.wkt
                element_dict[attribute]=value
            res[elem_type]=element_dict
        return res

    _name="urban_bridge.bridge"
    _inherit="urban_bridge.bridge"
    _columns={
        'civ':fields.integer('CIV',help="Codigo de Identificacion Vial"),
    }
