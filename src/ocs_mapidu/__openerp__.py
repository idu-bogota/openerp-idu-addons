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
        "name" : "Sistema de Gestión de Cartografía Social",
        "version" : "0.1",
        "author" : "Jorge Hernandez",
        "website" : "www.idu.gov.co",
        "category" : "Cartografía Social",
        "description":  """ 
                        Se utiliza en el IDU para registrar asuntos sociales que son insumo para
                        realizar la prefactibiliad de
                        los proyectos de Infraestructura Urbana
                        """,
        "depends" : ['base',
                     'base_geoengine',
                     'base_map',
                     ],
        "init_xml" : [
                      'map_social_idu.xml',
                      ],
        "demo_xml" : [],
        "update_xml" : [
                        'map_social_idu.xml',
                        'security/ocs_mapidu_security.xml',
                        'security/ir.model.access.csv',
                        ],
        "installable": True
}