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

class report_project_workpackage(osv.osv):
    _name = "report.project.workpackage"
    _description = "Workpackage by project"
    _auto = False
    _columns = {
        'name': fields.char('Name', size=128, readonly=True),
        'project_id': fields.many2one('project.project', 'Project', readonly=True),
        'phase_id': fields.many2one('project.phase', 'Phase', readonly=True),
        'nbr': fields.integer('# of workpackage', readonly=True),
        'no_of_days': fields.integer('# of Days', size=128, readonly=True),
        'delay_endings_days': fields.integer('Overpassed Deadline', size=128, readonly=True),
        'average_progress': fields.float('Average progress', readonly=True,group_operator="avg"),
        'state': fields.selection([('draft', 'Draft'), ('open', 'In Progress'), ('pending', 'Pending'), ('cancelled', 'Cancelled'), ('done', 'Done')],'Status', readonly=True),
    }

    def init(self, cr):
        tools.sql.drop_view_if_exists(cr, 'report_project_workpackage')
        cr.execute("""
            CREATE view report_project_workpackage as
                SELECT id, project_id,phase_id, 1 as nbr, name,state,
                    cast(to_char(date_trunc('day',date_deadline) - date_trunc('day',date_start),'DD') as int) as no_of_days, 
                    cast(to_char(date_trunc('day',date_deadline) - date_trunc('day',date_end),'DD') as int) as delay_endings_days, 
                    progress_rate as average_progress
                FROM project_pmi_wbs_item
                WHERE type = 'work_package'
                GROUP BY id

        """)

report_project_workpackage()

