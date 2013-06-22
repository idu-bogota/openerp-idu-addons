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
        'elem_id':fields.many2one('urban_bridge.structure_element','structure_elem')
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
        #1. Se obtiene el ID del combo box con los tipos de elementos de infraestructura
        xml = etree.fromstring(result['arch'])
        elem_types_id=[]
        elem_types_id.append(context['element_type_id'])
        
        #2. Para cada elemento de infraestructura del combo, se obtienen la lista de atributos para construir un diccionario
        
        for elem_inf in struct_elem_obj.browse(cr,uid,elem_types_id):
            xml.insert(1,etree.Element("separator",colspan="4",string=elem_inf.name))
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
                xml.insert(2,etree.Element("field",name=new_id)) #attrs="{'invisible':[('elem_type','=','"+elem_string+"')]}"
        result['arch']=etree.tostring(xml)
        return result

    def default_get(self,cr, uid, fields, context=None):
        """
        Fields View Get method :- generate the new view and display the survey pages of selected survey.
        """
        str_element = self.pool.get('urban_bridge.structure_element').browse(cr, uid, context['active_id'], context=None);
        res = super(urban_bridge_wizard_structure_elem, self).default_get(cr, uid, fields, context=context)
        res.update({'elem_id':str_element.id})
        return res

    def on_change_structure_elem_type(self,cr,uid,ids,elem_type,context=None):
        """
        Set Visible only the fields defined by Structure Element Type
        """
#        res = {}
#        elem_type_obj=self.pool.get('urban_bridge.structure_element_type') 
#        for elem_type in elem_type_obj.browse(cr,uid,elem_type):
#            for attr in elem_type.attributes:
#                field_id = elem_type.id+"_"+attr.id
#                res[field_id]
        #res = super(urban_bridge_wizard_structure_elem, self).default_get(cr, uid, fields, context=context)
        
        
#        elem_type=res.elem_type
#        attr = elem_type.attributes
#        for att in elem_type:
#            att_name = att.name
#            att_datatype = att.datatype
        return []

    def elem_create (self, cr, uid, ids, context=None):
#        wsdl_url = self.pool.get('ir.config_parameter').get_param(cr, uid, 'orfeo.ws.url', default='', context=context)
#        client = Client(wsdl_url)
#
#        current_user = self.pool.get('res.users').browse(cr, uid, uid, context=context)
#        claim_ids = context and context.get('active_ids', False)
#        claim_table = self.pool.get('crm.claim')
#
#        form_object = self.browse(cr, uid, form_object_id, context=context)
#        asunto = form_object.description.strip()
#        if(len(asunto) > 300):
#            raise osv.except_osv('Error de validación','El texto a ser radicado es demasiado largo, por favor resumalo')
#        dependenciaDestino = form_object.dependencia_id.code
#
#        usuarioLogin = current_user.login
#        tipoRadicacion = 2 #Radicados de entrada
#        municipio = 1 # Bogotá
#        departamento = 11 # Distrito Capital
#        pais = 170 # Colomba
#        continente = 1 # América
         form_object_id = ids and ids[0] or False
         form_object = self.browse(cr, uid, form_object_id, context=context)
         return {'type': 'ir.actions.act_window_close'}


    def create(self, cr, uid, vals, context=None):
        """
        Create the Answer of survey and store in survey.response object, and if set validation of question then check the value of question if value is wrong then raise the exception.
        """
        if context is None: context = {}
        #1. Se obtiene el valor de elem_id
        elem_id = context['active_id'] 
        
        
        #2. Se crea el registro de que se hizo un inventario
        urban_bridge_wizard_structure_elem_id = super(urban_bridge_wizard_structure_elem,self).create(cr, uid, {'elem_id': elem_id}, context=context)
        #3. Se ejemplifica el objeto structure_elem que se invocó y se miran los valores que tiene con el fin de asignarles un valor que se va 
        #a actualizar.
        structure_elem_obj=self.pool.get('urban_bridge.structure_element')
        structure_elem = structure_elem_obj.browse(cr,uid,elem_id)
        id = structure_elem.id
        bridge_id = structure_elem.bridge_id
        structure_elem_value_obj=self.pool.get('urban_bridge.structure_element_value')
        #Se itera sobre los elementos recibidos
        #Si no existen se crean
        for value_form in vals:
            if not (str(value_form).startswith("n") or str(value_form).startswith("e")):#Values aren't name or structure_elem
                s = value_form.split('_')
                struct_elem_attribute_id = s[1]
                attribute = self.pool.get('urban_bridge.structure_element_attribute').browse(cr,uid,struct_elem_attribute_id)
                if attribute is False:
                    break
                
                
                data_type = attribute.data_type
                #4. Se arma el diccionario que se va a pasar al metodo
                str_elem_val_vals={}
                str_elem_val_vals['element_attribute_id']=struct_elem_attribute_id
                str_elem_val_vals['element_id']=elem_id
                if (data_type=='integer'):
                    str_elem_val_vals['value_integer']=vals[value_form]
                elif (data_type=='text'):
                    str_elem_val_vals['value_text']=vals[value_form]
                elif (data_type=='datetime'):
                    str_elem_val_vals['value_datetime']=vals[value_form]
                elif (data_type=='float'):
                    str_elem_val_vals['value_float']=vals[value_form]
                elif (data_type=='boolean'):
                    str_elem_val_vals['value_bool']=vals[value_form]
                elif(data_type=='char'):
                    str_elem_val_vals['value_char']=vals[value_form]
                elif(data_type=='date'):
                    str_elem_val_vals['value_date']=vals[value_form]
                isnew=True
                id_value=0 
                for struc_elem_value in structure_elem.values:
                    if (struc_elem_value.element_attribute_id == struct_elem_attribute_id):
                        id_value=struc_elem_value.id
                        isnew=False
                if(isnew):
                    #Write
                    structure_elem_value_obj.write(cr,uid,id_value,str_elem_val_vals)
                else:
                    #Create
                    structure_elem_value_obj.create(cr,uid,str_elem_val_vals)
        return urban_bridge_wizard_structure_elem_id

urban_bridge_wizard_structure_elem()
