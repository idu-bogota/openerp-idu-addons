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

{
    'name': 'Project Report IDU',
    'version': '1.1',
    'author': 'OpenERP SA',
    'website': 'http://www.openerp.com',
    'category': 'Project Management',
    'sequence': 8,
    'summary': 'Projects, Reports',
    'images': [
        'images/gantt.png',
        'images/project_dashboard.jpeg',
        'images/project_task_tree.jpeg',
        'images/project_task.jpeg',
        'images/project.jpeg',
        'images/task_analysis.jpeg',
        'images/project_kanban.jpeg',
        'images/task_kanban.jpeg',
        'images/task_stages.jpeg'
    ],
    'depends': [
        'base_setup',
        'base_status',
        'product',
        'analytic',
        'board',
        'mail',
        'resource',
        'web_kanban'
    ],
    'description': """
Report Project IDU
=====================================================

This application allows display reports
    """,
    'data': [
        'project_report_idu_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
