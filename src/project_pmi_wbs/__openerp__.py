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

{
    'name': 'Project Management - Work Breakdown Structure',
    'version': '1.0',
    'category': 'Project Management',
    'description': """
This module adds the WBS support for Projects.
=================================================================================

                """,
    'author': 'Instituto De Desarrollo Urbano',
    'website': 'http://www.idu.gov.co',
    'depends': [
        'project','project_long_term'
    ],
    'data': [
        'wizard/create_wbs.xml',
        'wizard/create_edt_from_file.xml',
        'project_pmi_wbs_view.xml',
        'project_pmi_wbs_sequence.xml',
        'security/security.xml',
        'security/ir.model.access.csv',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
