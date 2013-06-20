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


from osv import osv, fields
from lxml import etree
#from suds.client import Client

class urban_bridge_wizard_structure_elem(osv.osv_memory):
    _name="urban_bridge.wizard.structure_elem"
    _description="Fill Bridge Properties"
    _columns={
        'name':fields.char('Name',size=128),
        'elem_type':fields.many2one('urban_bridge.structure_element_type','Type'),
        'bridge_id':fields.many2one('urban_bridge.bridge')
    }

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        """
        Fields View Get method :- generate the new view and display the survey pages of selected survey.
        """
        #attrib_obj = self.pool.get('urban_bridge.structure_element_attribute')
        struct_elem_obj = self.pool.get('urban_bridge.structure_element_type')
        if context is None:
            context = {}
        result = super(urban_bridge_wizard_structure_elem, self).fields_view_get(cr, uid, view_id, \
                                        view_type, context, toolbar,submenu)


        #1. Se obtienen los ID del combo box con los tipos de elementos de infraestructura
        elem_types = result['fields']['elem_type']['selection']
        xml = etree.fromstring(result['arch'])
        elem_types_id = []
        for x in elem_types:
            elem_types_id.append(x[0])
        #2. Para cada elemento de infraestructura del combo, se obtienen la lista de atributos para construir un diccionario
        
        for elem_inf in struct_elem_obj.browse(cr,uid,elem_types_id):
            attributes = elem_inf.attributes
            for att in attributes:
                new_id = str(elem_inf.id)+"_"+str(att.id)
                elem_string = att.name
                data_type=att.data_type
                result['fields'][new_id]={
                        'domain':[],
                        'string':elem_string,
                        'selectable':True,
                        'type':data_type,
                        'string':elem_string,
                        'context':{},
                }
                if (data_type == 'char'):
                    result['fields'][new_id]['size']=256
                xml.insert(5,etree.Element("field",name=new_id))
        result['arch']=etree.tostring(xml)
        return result


    
    def default_get(self,cr, uid, fields, context=None):
        """
        Fields View Get method :- generate the new view and display the survey pages of selected survey.
        """
        bridge = self.pool.get('urban_bridge.bridge').browse(cr, uid, context['active_id'], context=None);
        res = super(urban_bridge_wizard_structure_elem, self).default_get(cr, uid, fields, context=context)
        res.update({'bridge_id': bridge.id})
        return res
    
    def on_change_structure_elem_type(self,cr,uid,fields,context=None):
        #res = super(urban_bridge_wizard_structure_elem, self).default_get(cr, uid, fields, context=context)
        
        
#        elem_type=res.elem_type
#        attr = elem_type.attributes
#        for att in elem_type:
#            att_name = att.name
#            att_datatype = att.datatype
        return []


urban_bridge_wizard_structure_elem()
