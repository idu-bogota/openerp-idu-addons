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
from openerp.osv import osv, fields
from openerp.osv.osv import except_osv
from shapely.wkt import dumps, loads
from tools.translate import _

class urban_bridge_wizard_update_shape(osv.osv_memory):
    _name="urban_bridge.wizard.update_shape"
    _columns={
        'bridge_id':fields.many2one('urban_bridge.bridge','Bridge',required=True),
        'wkt':fields.text('WKT Text',required=True),
        'srid':fields.integer('SRID',required=True)
    }

    def default_get(self,cr, uid, fields, context=None):
        """
        Fields View Get method :- generate the new view and display the survey pages of selected survey.
        """
        res = super(urban_bridge_wizard_update_shape, self).default_get(cr, uid, fields, context=context)
        bridge_id = context['active_id']
        res["bridge_id"]=bridge_id
        if bridge_id is not False:
            spatial_ref_sys = self.pool.get('ir.config_parameter').get_param(cr, uid, 'urban_bridge.local_spatial_reference', default='', context=context) 
            query = """
            SELECT  ST_ASTEXT(ST_TRANSFORM(SHAPE,%s)) FROM URBAN_BRIDGE_BRIDGE WHERE ID = %s
            """
            cr.execute(query,(spatial_ref_sys,bridge_id))
            for row in cr.fetchall():
                shape = row[0]
                if shape is not False:
                    res["wkt"]=shape
                    res["srid"]=int(spatial_ref_sys)
        return res
    
    
    def create(self, cr, uid, vals, context=None):
        """
        This method si called when every action at wizard
        """
        try:
            id_val = super(urban_bridge_wizard_update_shape,self).create(cr, uid, vals, context=context)
            #3. Captura de Dato desde un WKT
            wkt = vals["wkt"]
            spatial_ref_sys = self.pool.get('ir.config_parameter').get_param(cr, uid, 'urban_bridge.local_spatial_reference', default='', context=context)
            bridge_id = context["bridge_id"]
            if ((wkt is not None) or (wkt is not False)):
                #Transform coordinates first
                query = """
                Select ST_ASTEXT(ST_TRANSFORM(ST_GEOMFROMTEXT(%s,
                %s),900913))
                """
                cr.execute(query,(wkt,spatial_ref_sys))
                for row in cr.fetchall():
                    if (row[0] is not False):
                        shape = dumps(loads(row[0]))
                        self.pool.get('urban_bridge.bridge').write(cr,uid,bridge_id,{'shape':shape})
            return id_val
        except Exception:
            raise except_osv(_('Geometry wizard Load Fail'), str("Geometry bad definition"))
    def elem_create (self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}

urban_bridge_wizard_update_shape()
