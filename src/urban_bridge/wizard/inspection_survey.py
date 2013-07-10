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
#
#    Creado por Andres Ignacio Baez Alba
#
##############################################################################

from osv import osv, fields
from lxml import etree
from ast import literal_eval
#from suds.client import Client

class urban_bridge_wizard_inspection_survey(osv.osv_memory):
    _name="urban_bridge.wizard.inspection_survey"
    _description="Creates a survey for the Bridge"
    _columns={
        'name':fields.char('Name',size=128),
        'bridge_id':fields.many2one('urban_bridge.bridge','Bridge')
    }
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """
        Fields View Get method :- generate the new view and display the survey pages of selected survey.
        """
        result = super(urban_bridge_wizard_inspection_survey, self).fields_view_get(cr, uid, view_id, view_type, context, toolbar,submenu)
        methodology_obj = self.pool.get('urban_bridge.methodology')
        bridge_obj = self.pool.get('urban_bridge.bridge')
        methodology_id = context['methodology_id']
        bridge_id = context['bridge_id']
        xml = etree.fromstring(result['arch'])
        xml_index=1
        #1. Mostrar de acuerdo a la metodología escogida los datos que son generales
        xml.insert(xml_index,etree.Element("separator",colspan="4",string="General Data"))
        methodology =methodology_obj.browse(cr,uid,methodology_id)
        for entity in methodology.entity_id:
            for attribute in entity.attribute_id:
                if (attribute.is_general):
                    xml_index=xml_index+1
                    new_id = str(entity.id)+"_"+str(attribute.id)
                    elem_string = attribute.name
                    is_required="0"
                    if (attribute.is_required):
                        is_required = "1"
                    data_type = attribute.data_type
                    if (data_type =='char'):
                        result['fields'][new_id] = {
                                                    'domain':[],
                                                    'string':elem_string,
                                                    'selectable':True,
                                                    'type':data_type,
                                                    'string':elem_string,
                                                    'context':{},
                                                    'size':256,
                                                    'required':is_required,
                                                    }
                        xml.insert(xml_index,etree.Element("field",required=is_required,name=new_id))
                    elif (data_type == 'selection'):
                        result['fields'][new_id] = {
                                                    'domain':[],
                                                    'string':elem_string,
                                                    'selectable':True,
                                                    'type':data_type,
                                                    'string':elem_string,
                                                    'context':{},
                                                    'selection':literal_eval(attribute.selection_text),
                                                    'required':is_required,
                                                    }
                        xml.insert(xml_index,etree.Element("field",required=is_required,name=new_id))
                    else:
                        result['fields'][new_id] = {
                                                    'domain':[],
                                                    'string':elem_string,
                                                    'selectable':True,
                                                    'type':data_type,
                                                    'string':elem_string,
                                                    'context':{},
                                                    'required':is_required,
                                                    }
                        xml.insert(xml_index,etree.Element("field",required=is_required,name=new_id))
        #2. De acuerdo al inventario existente para cada elemento de infraestructura, se muestra los aspectos que 
        #se deben evaluar
        bridge = bridge_obj.browse(cr,uid,bridge_id)
        for elem_if in bridge.elements:
            xml_index=xml_index+1
            xml.insert(xml_index,etree.Element("separator",colspan="4",string="Inspection "+str(elem_if.element_type_id.name) +" : "+str(elem_if.name)))
            for entity in methodology.entity_id:
                for attribute in entity.attribute_id:
                    this_attribute_applies = False
                    for str_elem_type in attribute.structure_element_type:
                        if (attribute.is_general == False and str_elem_type.id == elem_if.element_type_id.id):
                            this_attribute_applies = True
                    if (this_attribute_applies):
                        xml_index=xml_index+1
                        new_id=str(elem_if.id)+"_"+str(entity.id)+"_"+str(attribute.id)
                        elem_string = attribute.name
                        is_required="0"
                        if (attribute.is_required):
                            is_required = "1"
                            data_type = attribute.data_type
                        if (data_type =='char'):
                            result['fields'][new_id] = {
                                                        'domain':[],
                                                        'string':elem_string,
                                                        'selectable':True,
                                                        'type':data_type,
                                                        'string':elem_string,
                                                        'context':{},
                                                        'size':256,
                                                        'required':is_required,
                                                        }
                            xml.insert(xml_index,etree.Element("field",required=is_required,name=new_id))
                        elif (data_type == 'selection'):
                            result['fields'][new_id] = {
                                                        'domain':[],
                                                        'string':elem_string,
                                                        'selectable':True,
                                                        'type':data_type,
                                                        'string':elem_string,
                                                        'context':{},
                                                        'selection':literal_eval(attribute.selection_text),
                                                        'required':is_required,
                                                        }
                            xml.insert(xml_index,etree.Element("field",{'required':is_required},name=new_id))
                        else:
                            result['fields'][new_id] = {
                                                        'domain':[],
                                                        'string':elem_string,
                                                        'selectable':True,
                                                        'type':data_type,
                                                        'string':elem_string,
                                                        'context':{},
                                                        'required':is_required,
                                                        }
                            xml.insert(xml_index,etree.Element("field",name=new_id))
        #3. De acuerdo a los valores ingresados por el usuario se manda un vector de datos al interpretador para que muestre 
        #el resultado del diagnostico...
        
        #4. El resultado del diagnostico se debe almacenar en el objeto inspection_survey para obtener la calificacion general
        # del puente de acuerdo con la metodología seleccionada.
        result['arch'] = etree.tostring(xml)
        return result

urban_bridge_wizard_inspection_survey()