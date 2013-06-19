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
#from suds.client import Client

class urban_bridge_wizard_structure_elem(osv.osv_memory):
    _name="urban_bridge.wizard.structure_elem"
    _description="Fill Bridge Properties"
    _columns={
        'name':fields.char('Name',size=128),
        'elem_type':fields.many2one('urban_bridge.structure_element_type','Type'),
        'bridge_id':fields.many2one('urban_bridge.bridge')
    }
    
    def default_get(self,cr, uid, fields, context=None):
        bridge = self.pool.get('urban_bridge.bridge').browse(cr, uid, context['active_id'], context=None);
        res = super(urban_bridge_wizard_structure_elem, self).default_get(cr, uid, fields, context=context)
        res.update({'bridge_id': bridge.id})
        return res 
    
    def on_change_structure_elem_type(self,cr,uid,fields,context=None):
        #res = super(urban_bridge_wizard_structure_elem, self).default_get(cr, uid, fields, context=context)
        elem_type=self.pool.get('')
        
#        elem_type=res.elem_type
#        attr = elem_type.attributes
#        for att in elem_type:
#            att_name = att.name
#            att_datatype = att.datatype
        return []


urban_bridge_wizard_structure_elem()
