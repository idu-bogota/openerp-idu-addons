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
        "name" : "Office of Citizen Service - Orfeo Integration",
        "version" : "openerp6.1-rev2013080800",
        "author" : "Angel María Fonseca, Andres Ignacio Baez Alba and Cinxgler Mariaca Minda",
        "website" : "www.idu.gov.co",
        "category" : "Social Management",
        "description": """For Public Organizations, useful to receive claims from Citizens and create a document in the Document Management System Orfeo - http://orfeogpl.org
This requires ladonize installed (http://ladonize.org/index.php/Python_install) and you need to set the wsdl url at settings > Customization > Low Level Objects > System Parameters and create a new parameter using key: orfeo.ws.url and value: http://orfeo_url?wsdl
        """,
        "depends" : ['base',
                     'ocs',
                    ],
        "init_xml" : [
                       'security/ir.model.access.csv',
                     ],
        "demo_xml" : [],
        "update_xml" : [
                        'wizard/radicar_view.xml',
                        'ocs_orfeo_view.xml',
                       ],
        "installable": True
}
