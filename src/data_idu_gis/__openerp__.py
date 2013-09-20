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
  'name': 'Módulo para crear datos GIS del IDU',
  'version': '01',
  'category': 'Urban GIS/Others',
  'description': "Modulo para cargar datos GIS usados en el IDU",
  'author': 'Andres Ignacio Baez Alba',
  'website': 'http://www.idu.gov.co',
  'depends': ['base'],
  'init_xml': ['district_bogota.xml',
               #'sub_district_bogota.xml',
               #'neighborhood_bogota.xml',
               #'micro_seismicity.xml',
               #'cadastral_zone.xml',
               #'geological_zone.xml',
               #'road_hierarchy_bogota.xml',
  ],
  'update_xml': [],
  'installable': True,
}

