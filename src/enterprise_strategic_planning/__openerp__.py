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
    'name': 'Strategic Planning',
    'version': '1.0',
    'category': 'Planning',
    'description': """
This module adds the Strategic Planning support for the entiire company
====================================================================
Elements in the module are taken from Business Motivation Model (BMM) http://www.omg.org/spec/BMM/
                """,
    'author': 'Instituto De Desarrollo Urbano',
    'website': 'http://www.idu.gov.co',
    'depends': [
        'base_setup',
        'base_status',
    ],
    'data': [
        'enterprise_strategic_planning_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
