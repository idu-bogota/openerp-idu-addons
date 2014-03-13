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
##############################################################################
from openerp.osv import osv, fields


class plan_contratacion_idu_wizard_solicitar_cambio(osv.osv_memory):
    """
    Wizard para crear una solicitud de cambio a un item del plan de contratación
    """
    _name = "plan_contratacion_idu.wizard.solicitud_cambio"
    _description = "Permite crear una solicitud de cambio de un item del plan"

    def _tipo_options(self,cr,uid,context=None):
        options = [
           ('modificar', 'Modificación del item'),
           ('eliminar', 'Eliminación del item'),
        ]
        if 'plan_item_id' in context:
            return options

        return [('adicionar', 'Creación de un nuevo item')]

    _columns={
            'tipo':fields.selection(_tipo_options,
                'Tipo de solicitud',
                required=True,
            ),
            'plan_item_id': fields.many2one('plan_contratacion_idu.item','Item a cambiar/eliminar',
                 required=False,
                 readonly=True,
             ),
            'plan_id': fields.many2one('plan_contratacion_idu.plan','Plan',
                 required=True,
                 readonly=True,
             ),
    }

    _defaults = {
        'plan_item_id': lambda self, cr, uid, context : context['plan_item_id'] if context and 'plan_item_id' in context else None,
        'plan_id': lambda self, cr, uid, context : context['plan_id'] if context and 'plan_id' in context else None,
    }

    """Crear un registro de tipo Item Solicitud Cambio
    
    Si el tipo es 'modificacion', se crea una copia del objeto plan_item_id para que sea actualizado y se relaciona a la solicitud de cambio
    
    Si el tipo es 'nuevo', se crea un objeto nuevo y se asigna en con el estado 'solicitud_cambio' al plan de contratación
    """
    def action_radicar(self, cr, uid, ids, context=None):
        form_id = ids and ids[0] or False
        form = self.browse(cr, uid, form_id, context=context)
        solicitud_cambio_pool = self.pool.get('plan_contratacion_idu.item_solicitud_cambio')
        plan_item_pool = self.pool.get('plan_contratacion_idu.item')
        vals = {
            'tipo': form.tipo,
            'plan_id': form.plan_id.id,
            'plan_item_id': form.plan_item_id.id,
            'state': 'radicado',
        }

        if form.tipo == 'modificar':
            vals['item_nuevo_id'] = plan_item_pool.copy(cr, uid, form.plan_item_id.id, default={'message_ids':[], 'state': 'solicitud_cambio'}, context=context)
        elif form.tipo == 'adicionar':
            vals['item_nuevo_id'] = plan_item_pool.create(cr, uid, {'plan_id':form.plan_id.id, 'state': 'solicitud_cambio'}, context=context)

        id = solicitud_cambio_pool.create(cr, uid, vals, context=context)

        return self.redirect_to_solicitud_cambio_view(cr, uid, id, context=context)

    def redirect_to_solicitud_cambio_view(self, cr, uid, id, context=None):
        return {
            'name': 'Solicitud de Cambio',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'plan_contratacion_idu.item_solicitud_cambio',
            'res_id': int(id),
            'type': 'ir.actions.act_window',
        }


plan_contratacion_idu_wizard_solicitar_cambio()
