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

class project(osv.osv):
    _name = "project.project"
    _inherit = "project.project"

    _columns = {
        'etapa_id': fields.many2one('project_idu.etapa','Etapa', select=True),
        #Punto de inversion
        #Centro de costo
        #Fuente de Financiacion
    }

project()

class task(osv.osv):
    _name = "project.task"
    _inherit = "project.task"

    _columns = {
        'etapa_id': fields.related(
            'project_id',
            'etapa_id',
            type="many2one",
            relation="project_idu.etapa",
            string="Etapa del Proyecto",
            store=True)
    }

task()

class project_idu_etapa(osv.osv):
    _name = "project_idu.etapa"

    _columns = {
        'name': fields.char('Name', size=255, required=True, select=True),
    }

project_idu_etapa()

class project_pmi_wbs_item(osv.osv):
    _name = "project_pmi.wbs_item"
    _inherit = "project_pmi.wbs_item"

    def _get_wbs_item_and_parents(self, cr, uid, ids, context=None):
        return super(project_pmi_wbs_item, self)._get_wbs_item_and_parents(cr, uid, ids, context=context)

    def _opportunity_evaluation(self, cr, uid, ids, prop, unknow_none, context=None):
        res = {}
        if isinstance(ids, (list, tuple)) and not len(ids):
            return res
        if isinstance(ids, (long, int)):
            ids = [ids]
        reads = self.read(cr, uid, ids, ['date_deadline','date_end'], context=context)
        res = {}
        for record in reads:
            opportunity = '';
            if record['date_deadline']:
                today = datetime.datetime.now().date()
                date_deadline = datetime.datetime.strptime(record['date_deadline'], '%Y-%m-%d').date()
                if record['date_end']:
                    date_end = datetime.datetime.strptime(record['date_end'], '%Y-%m-%d').date()
                    if date_end <= date_deadline:
                        opportunity = 'is_on_time'
                    elif date_end > date_deadline:
                        opportunity = 'is_late'
                elif today >= date_deadline:
                    opportunity = 'is_not_finished'
            res[record['id']] = opportunity
        return res

    _columns = {
        'opportunity_evaluation': fields.function(_opportunity_evaluation, type="char", translate=True, string='is late, on time, not finished?',store = {
                'project_pmi.wbs_item': (_get_wbs_item_and_parents, ['date_end','date_deadline'], 10),
        }),
    }

project_pmi_wbs_item()
