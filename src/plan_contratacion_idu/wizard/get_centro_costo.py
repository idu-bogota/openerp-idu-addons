# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Instituto de Desarrollo Urbano (<http://www.idu.gov.co>).
#     All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#    Realizado por: Andrés Ignacio Báez Alba andresignaciob@gmail.com
#
#
#    Febrero de 2014
#
##############################################################################
from openerp.osv import osv, fields
from stone_erp_idu import stone_client_ws


class plan_contratacion_idu_wizard_get_centro_costo(osv.osv_memory):
    """
    Wizard para importar centro de costo con el resto de información desde stone
    """
    _name = "plan_contratacion_idu.wizard.get_centro_costo"
    _description = "Optiene Centro de Costo"
    
    def _get_centro_costo(self,cr,uid,context=None):
        wsdl = self.pool.get('ir.config_parameter').get_param(cr,uid,'stone_idu.webservice.wsdl',default=False,context=context)
        if (wsdl == False):
            return [('0','Sin conexión a stone')]
        res = stone_client_ws.obtener_centros_costo(wsdl)
        var = [(r,str(r) + ' : ' +res[r]) for r in res]
        return var
    def on_change_centro_costo(self,cr,uid,ids,centro_costo,context=None):
        wsdl = self.pool.get('ir.config_parameter').get_param(cr,uid,'stone_idu.webservice.wsdl',default=False,context=context)
        if (wsdl == False):
            return {}
        res = stone_client_ws.completar_datos_centro_costo(wsdl, centro_costo)
        return {'value':res}
    
    def create (self,cr,uid,vals,context=None):
        wsdl = self.pool.get('ir.config_parameter').get_param(cr,uid,'stone_idu.webservice.wsdl',default=False,context=context)
        res = stone_client_ws.completar_datos_centro_costo(wsdl, vals['centro_costo'])
        res['centro_costo']=vals['centro_costo']
        id_val = super(plan_contratacion_idu_wizard_get_centro_costo,self).create(cr,uid,res,context=context)
        return id_val
    
    def action_create(self, cr, uid, ids, context=None):
        return {'type': 'ir.actions.act_window_close'}
         
    _columns={
            'centro_costo':fields.selection(_get_centro_costo,'Centro Costo'),
            'proyecto_idu_id':fields.integer('Codigo Proyecto IDU',readonly = True),
            'proyecto_idu':fields.char('Proyecto Idu',size=1024,readonly=True),
            'punto_inversion_id':fields.integer('Codigo Punto de Inversión',size=2048,readonly=True),
            'punto_inversion':fields.char('Punto Inversión',size=2048,readonly=True),
    }
plan_contratacion_idu_wizard_get_centro_costo()
