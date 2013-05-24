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
# INSTITUTO DE DESARROLLO URBANO - BOGOTA (COLOMBIA)
#
# Customization developed by:
# ANGEL MARIA FONSECA CORREA - CIO
# ANDRES IGNACIO BAEZ ALBA - Engineer of Development
# CINXGLER MARIACA MINDA - Engineer of Development - Architect
#
###############################################################################

from osv import fields,osv
from base_geoengine import geo_model

class urban_bridge_bridge(geo_model.GeoModel):
    """ 
    Bridge Infraestructure Data
    """
    _name="urban_bridge.bridge"
    _columns = {
        'shape':fields.geo_multi_polygon('Coordinate'),
        'code':fields.char('Bridge Code: ',size=128),
        'name':fields.char('Identifier: ',size=128),
        'category':fields.selection([(1,'PPC'),(2,'PPE'),(3,'PVC'),(4,'PVE')],'Bridge Classification'),
        'structure_type':fields.many2one('urban_bridge.structure_type','Bridge Type',required=True),
        'address':fields.char('Bridge Address',size=256),
        'last_address':fields.char('Last Address',size=256),
        'construction_date':fields.datetime('Construction Date'),
        'length':fields.float('Total Length'),
        'width':fields.float('Total Width'),
        'superstructure_area':fields.float('Bridge SuperStructure Area:'),
        'gauge':fields.float('Gauge'),
        'photo':fields.binary('Photo'),
    }
urban_bridge_bridge()

class urban_bridge_structure_type(osv.osv):
    """
        Structure Type Main Classification
    """
    _name="urban_bridge.structure_type"
    _columns={
        'code':fields.integer('Code','Code - Value equivalent Domain'),
        'name':fields.char('Name :',size=256),
    }
urban_bridge_structure_type()


