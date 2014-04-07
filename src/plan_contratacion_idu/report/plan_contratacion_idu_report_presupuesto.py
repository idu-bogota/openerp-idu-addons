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

from openerp.osv import fields,osv
from openerp import tools

class plan_contratacion_idu_report_presupuesto_programados(osv.osv):
    _name = "plan_contratacion_idu.report.presupuesto_programados"
    _table = 'plan_contr_idu_report_presupuesto_programados'
    _description = "Proyección Flujo Financiero CRP según Vigencia"
    _auto = False
    _columns = {
        'presupuesto': fields.float ('Presupuesto', obj="res.currency"),
        'plan_item_id': fields.many2one('plan_contratacion_idu.item', 'item Plan Contratacion'),
        'dependencia_id': fields.many2one('hr.department','Dependencia'),
        'plan_id': fields.many2one('plan_contratacion_idu.plan','Plan Contratacion'),
    }
    _order = 'plan_id'

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'plan_contr_idu_report_presupuesto_programados')
        cr.execute("""
            CREATE view plan_contr_idu_report_presupuesto_programados as
              SELECT
                  p.id,
                  SUM(p.presupuesto) AS presupuesto,
                  p.dependencia_id,
                  pl.id as plan_id
            FROM plan_contratacion_idu_item p 
            LEFT JOIN plan_contratacion_idu_plan pl ON p.plan_id = pl.id
            WHERE p.state NOT IN ('solicitud_cambio', 'no_realizado') AND pl.active = True
            GROUP BY p.dependencia_id, p.id, pl.id
        """)

plan_contratacion_idu_report_presupuesto_programados()

