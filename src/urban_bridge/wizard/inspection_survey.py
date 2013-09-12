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
        inspection_id = context['inspection_id']
        xml = etree.fromstring(result['arch'])
        #Generar un xml para insertar al final del ciclo
        maingroup = etree.Element("group",colspan="4",col="4")
        notebook = etree.SubElement(maingroup,"notebook")
        page_gral_data = etree.SubElement(notebook,"page",string="General Data")
        #1. Mostrar de acuerdo a la metodología escogida los datos que son generales        
        methodology =methodology_obj.browse(cr,uid,methodology_id)
        for entity in methodology.entity_id:
            for attribute in entity.attribute_id:
                if (attribute.is_general):
                    new_id = str(entity.id)+"_"+str(attribute.id)+'_'+str(inspection_id)
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
                        etree.SubElement(page_gral_data,"field",required=is_required,name=new_id)
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
                        etree.SubElement(page_gral_data,"field",required=is_required,name=new_id)
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
                        etree.SubElement(page_gral_data,"field",required=is_required,name=new_id)
        #2. De acuerdo al inventario existente para cada elemento de infraestructura, se muestra los aspectos que 
        #se deben evaluar
        bridge = bridge_obj.browse(cr,uid,bridge_id)
        
        pgInd=0#Reference to page index group
        page_group = []
        for elem_if in bridge.elements:
            page_group.append(etree.SubElement(notebook,"page",string=str(elem_if.name)))
            etree.SubElement(page_group[pgInd],"separator",colspan="4",string="Inspection "+str(elem_if.element_type_id.name) +" : "+str(elem_if.name))
            #xml.insert(xml_index,etree.Element("separator",colspan="4",string="Inspection "+str(elem_if.element_type_id.name) +" : "+str(elem_if.name)))
            for entity in methodology.entity_id:
                for attribute in entity.attribute_id:
                    this_attribute_applies = False
                    for str_elem_type in attribute.structure_element_type:
                        if (attribute.is_general == False and str_elem_type.id == elem_if.element_type_id.id):
                            this_attribute_applies = True
                    if (this_attribute_applies):
                        #xml_index=xml_index+1
                        new_id=str(entity.id)+"_"+str(attribute.id)+'_'+str(inspection_id)+"_"+str(elem_if.id)
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
                            etree.SubElement(page_group[pgInd],"field",required=is_required,name=new_id)
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
                            etree.SubElement(page_group[pgInd],"field",required=is_required,name=new_id)
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
                            etree.SubElement(page_group[pgInd],"field",required=is_required,name=new_id)
            pgInd=pgInd+1
        xml.insert(1,maingroup)
        result['arch'] = etree.tostring(xml)
        return result


    def default_get(self,cr, uid, fields, context=None):
        """
        Fields View Get method :- generate the new view and display the survey pages of selected survey.
        """
        res = super(urban_bridge_wizard_inspection_survey, self).default_get(cr, uid, fields, context=context)
        active_id = False
        for k in context:
            if k == 'active_id':
                active_id = context[k]
        if active_id == False:
            return res
        inspection_survey = self.pool.get('urban_bridge.inspection_survey').browse(cr,uid,active_id)
        res.update({'bridge_id':inspection_survey.bridge_id})
        for value in inspection_survey.values:
            field_id = ""
            if (value.inspect_attribute_id.is_general):
                #field = str(entity.id)+"_"+str(attribute.id)+'_'+str(inspection_id)
                field_id = str(value.inspect_attribute_id.inspection_entity_id.id)+"_"+str(value.inspect_attribute_id.id)+"_"+str(value.inspection_id.id)
            else:
                field_id = str(value.inspect_attribute_id.inspection_entity_id.id)+"_"+str(value.inspect_attribute_id.id)+"_"+str(value.inspection_id.id)+"_"+str(value.element_id.id)
            data_type = value.inspect_attribute_id.data_type
            if (data_type=='integer'):
                res.update({field_id:value.value_integer})
            elif (data_type=='text'):
                res.update({field_id:value.value_text})
            elif (data_type=='datetime'):
                res.update({field_id:value.value_datetime})
            elif (data_type=='float'):
                res.update({field_id:value.value_float})
            elif (data_type=='boolean'):
                res.update({field_id:value.value_bool})
            elif(data_type=='char'):
                res.update({field_id:value.value_char})
            elif(data_type=='date'):
                res.update({field_id:value.value_date})
            elif(data_type=='selection'):
                res.update({field_id:value.value_selection})
            elif(data_type=='binary'):
                res.update({field_id:value.value_binary})
        return res



    def elem_create (self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}
    
    def create(self, cr, uid, vals, context=None):
        """
        Create the wizard and set the values for structure element in EAV model 
        """
        #El metodo escribe los valores ingresados por el usuario en la base de Datos
        super(urban_bridge_wizard_inspection_survey,self).create(cr, uid, {'bridge_id':context['bridge_id']}, context=context)
        inspection_id=context['active_id']
        inspection_survey=self.pool.get('urban_bridge.inspection_survey')
        inspection_attribute_obj=self.pool.get('urban_bridge.inspection_attribute')
        inspection_obj=self.pool.get('urban_bridge.inspection_value')
        inspection=inspection_survey.browse(cr,uid,inspection_id)
        for value_form in vals:
            if not (str(value_form).startswith("n") or str(value_form).startswith("e")):#Values aren't name or structure_elem
                s = value_form.split('_')
                inspec_attribute_id=int(s[1])
                ins_survey_vals={}
                ins_survey_vals['inspection_id']=inspection_id
                ins_survey_vals['bridge_id']=context['bridge_id']
                ins_survey_vals['inspect_attribute_id']=inspec_attribute_id
                inspection_attribute=inspection_attribute_obj.browse(cr,uid,inspec_attribute_id)
                if (not inspection_attribute.is_general):
                    ins_survey_vals['element_id'] = int(s[3])
                if (inspection_attribute.data_type=='integer'):
                    ins_survey_vals['value_integer']=vals[value_form]
                elif (inspection_attribute.data_type=='text'):
                    ins_survey_vals['value_text']=vals[value_form]
                elif (inspection_attribute.data_type=='datetime'):
                    ins_survey_vals['value_datetime']=vals[value_form]
                elif (inspection_attribute.data_type=='float'):
                    ins_survey_vals['value_float']=vals[value_form]
                elif (inspection_attribute.data_type=='boolean'):
                    ins_survey_vals['value_bool']=vals[value_form]
                elif(inspection_attribute.data_type=='char'):
                    ins_survey_vals['value_char']=vals[value_form]
                elif(inspection_attribute.data_type=='date'):
                    ins_survey_vals['value_date']=vals[value_form]
                elif(inspection_attribute.data_type=='selection'):
                    ins_survey_vals['value_selection']=vals[value_form]
                elif(inspection_attribute.data_type=='binary'):
                    ins_survey_vals['value_binary']=vals[value_form]
                isnew=True
                id_value=0
                for inspection_value in inspection.values:
                    if (int(inspection_value.inspect_attribute_id) == inspec_attribute_id):
                        id_value=inspection_value.id
                        isnew=False
                if (not isnew):
                    #Write
                    inspection_obj.write(cr,uid,id_value,ins_survey_vals)
                else:
                    #Create
                    inspection_obj.create(cr,uid,ins_survey_vals)
        return 1
urban_bridge_wizard_inspection_survey()