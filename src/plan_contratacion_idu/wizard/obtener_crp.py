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
from contrato_idu import siac_ws

class  plan_contratacion_idu_wizard_crp(osv.osv_memory):
    _name = 'plan_contratacion_idu.wizard.crp'
    _description = 'lista CRP relacionados al numero de contrato del item'

    def _get_numero_crp(self, cr, uid, context=None):
        res = ()
        if not context or not 'plan_item_id' in context:
            return res
        wsdl_url = self.pool.get('ir.config_parameter').get_param(cr,uid,'siac_idu.webservice.wsdl',default=False,context=context)
        record = self.pool.get('plan_contratacion_idu.item').browse(cr, uid, context['plan_item_id'], context=context)
        if record.numero_contrato:
            datos_contrato = siac_ws.obtener_datos_contrato(wsdl_url, record.numero_contrato)
            if (datos_contrato):
                crp_list = datos_contrato['numero_crp']
            lista_crp = ()
            if isinstance(crp_list, int):
                lista_crp = [(crp_list, crp_list)]
            else:
                for crp in crp_list:
                    lista_crp = lista_crp + ((crp, crp),)
                res = lista_crp
        return res

    _columns = {
        'crps': fields.selection(_get_numero_crp, 'Número de CRP')
    }

    def radicar(self, cr, uid, ids, context=None):
        wizard_obj=self.browse(cr, uid, ids[0], context)
        plan_contratacion_idu_item_obj = self.pool.get('plan_contratacion_idu.item')
        plan_contratacion_idu_item_obj.write(cr, uid, context['plan_item_id'], {'numero_crp':wizard_obj.crps, 'state': 'suscrito' }, context)
        return {'type': 'ir.actions.act_window_close'}


plan_contratacion_idu_wizard_crp()
