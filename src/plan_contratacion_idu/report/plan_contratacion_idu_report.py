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

class plan_contratacion_idu_report_pagos_programados(osv.osv):
    _name = "plan_contratacion_idu.report.pagos_programados"
    _description = "Proyección Flujo Financiero CRP según Vigencia"
    _auto = False
    _columns = {
        'mes': fields.selection([(1,'Enero'), (2,'Febrero'), (3,'Marzo'), (4,'Abril'),
            (5,'Mayo'), (6,'Junio'), (7,'Julio'), (8,'Agosto'), (9,'Septiembre'),
            (10,'Octubre'), (11,'Noviembre'), (12,'Diciembre')],'Mes', required=True),
        'valor': fields.float('Valor', select=True, obj="res.currency"),
        'plan_item_id': fields.many2one('plan_contratacion_idu.item', 'item Plan Contratacion'),
        'dependencia_id': fields.many2one('hr.department','Dependencia'),
        'plan_id': fields.many2one('plan_contratacion_idu.plan','Plan Contratacion'),
    }
    _order = 'plan_id, plan_item_id'

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'plan_contratacion_idu_report_pagos_programados')
        cr.execute("""
            CREATE view plan_contratacion_idu_report_pagos_programados as
              SELECT 
                p.id,
                p.mes,
                p.valor,
                p.plan_contratacion_item_id AS plan_item_id,
                i.dependencia_id,
                pl.id AS plan_id
            FROM plan_contratacion_idu_plan_pagos_item p 
            LEFT JOIN plan_contratacion_idu_item i ON p.plan_contratacion_item_id = i.id
            LEFT JOIN plan_contratacion_idu_plan pl ON i.plan_id = pl.id
            WHERE 
                i.state NOT IN ('solicitud_cambio', 'no_realizado') 
                AND pl.active = True
        """)

plan_contratacion_idu_report_pagos_programados()

