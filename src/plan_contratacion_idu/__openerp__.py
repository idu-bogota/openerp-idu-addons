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
    'name': 'Gestión y seguimiento del plan de contratación del IDU',
    'version': '1.0',
    'category': 'Contract Management',
    'description': """
    Este módulo permite hacer el registro y seguimiento al plan de contratación del IDU
""",
    'author': 'Instituto De Desarrollo Urbano',
    'website': 'http://www.idu.gov.co',
    'depends': [
        'base','hr','contrato_idu','stone_erp_idu','base_map'
    ],
    'data': [
        'security/plan_contratacion_idu_security.xml',
        'plan_contratacion_idu_data.xml',
        'wizard/solicitar_cambio_view.xml',
        'plan_contratacion_idu_view.xml',
        'wizard/reporte_excel_view.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'auto_install': False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: