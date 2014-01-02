# -*- encoding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2013 Instituto de Desarrollo Urbano (<http://www.idu.gov.co>). All Rights Reserved
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

from openerp.osv import fields, osv
import time
import datetime

class project_pmi_wbs_item(osv.osv):
    _name = "project_pmi.wbs_item"
    _inherit = ['mail.thread']
    _description = "WBS item part of WBS tree"

    #FIXME: Adicionar los pesos para el calculo del avance correctamente, debe acumularse de acuerdo al peso, 
    #FIXME: actualmente la implementación no cálcula correctamente
    def _progress_rate(self, cr, uid, ids, names, arg, context=None):
        child_parent = self._get_wbs_item_and_children(cr, uid, ids, context)
        # compute planned_hours, total_hours, effective_hours specific to each project
        cr.execute("""
            SELECT
                wbs_item.id, COALESCE(wbs_item.quantity, 0.0), COALESCE(SUM(wr.quantity), 0.0), wbs_item.weight, wbs_item.type
            FROM
                project_pmi_wbs_item wbs_item
                LEFT JOIN project_pmi_wbs_work_record wr ON wr.wbs_item_id = wbs_item.id
            WHERE
                wbs_item.id IN %s AND state <> 'cancelled' AND state <> 'template'
            GROUP BY wbs_item.id
        """, (tuple(child_parent.keys()),))
        # aggregate results into res
        res = dict([(id, {'planned_quantity':0.0,'effective_quantity':0.0}) for id in ids])
        for id, planned, effective, weight, type in cr.fetchall():
            if id in ids:#no calculated using children values
                if(not 'weight' in res[id]):
                    res[id]['weight'] = (weight/100)
                if(not 'type' in res[id]):
                    res[id]['type'] = type
            # add the values specific to id to all parent wbs_items of id in the result
            while id:
                if id in ids:
                    res[id]['planned_quantity'] += planned
                    res[id]['effective_quantity'] += effective
                id = child_parent[id]
        # compute progress rates
        for id in ids:
            if res[id]['planned_quantity']:
                progress_rate = round(100.0 * res[id]['effective_quantity'] / res[id]['planned_quantity'], 2)
                if res[id]['type'] == 'work_package':
                    res[id]['progress_rate'] = progress_rate
                else:
                    res[id]['progress_rate'] = round(progress_rate * res[id]['weight'], 2)
            else:
                res[id]['progress_rate'] = 0.0
        return res

    _columns = {
        'weight': fields.float('Weight'),
    }

    def _check_weight(self, cr, uid, ids, context=None):
        is_valid_data = True
        for obj in self.browse(cr,uid,ids,context=None):
            if obj.state == 'draft' and (obj.weight < 0 or obj.weight > 100):
                is_valid_data = False
                continue
            if obj.state != 'draft' and (obj.weight <= 0 or obj.weight > 100):
                is_valid_data = False
                continue
            if obj.parent_id:
                weight = 0
                for sibling in obj.parent_id.child_ids:
                    if obj.state != 'cancelled':
                        weight += sibling.weight
                if weight > 100:
                    is_valid_data = False
            elif obj.weight != 100:
                is_valid_data = False

        return is_valid_data

    _constraints = [
        (_check_weight, 'Error ! Weight must be between 1 and 100 or must be 100 if it\'s a root deliverable.', ['weight','state']),
    ]

project_pmi_wbs_item()