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
from osv import fields
from base_geoengine import geo_model

class urban_pavement_roadway(geo_model.GeoModel):
    """ 
    Roadway Base Polygon
    """
    _name="urban_pavement.roadway"
    _columns={
        'shape':fields.geo_multi_polygon('Coordinate'),
        'id':fields.integer('Polygon ID'),
        'ric':fields.integer('Rodway Idenfication Code'),#CIV Codigo de Identificacion de la Via
        'create_date':fields.date('Create Date'),
        'adherence':fields.float('Adherence',digits=(12,6)),
    }
urban_pavement_roadway()