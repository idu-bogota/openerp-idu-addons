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
#
#
#
#    Autor: Andres Ignacio Báez Alba
#
#     This module is a base map to execute geoprocessing functions, it not have the better
#     structure, and will be re-factored#
#
#
from osv import fields,osv
#from base_geoengine import geo_model

class base_map_district(osv.osv):
    _name="base_map.district"
    _columns = {
        'name':fields.char('District Name',size=256),
        'code':fields.char('District Code',size=256),
        #'shape':fields.geo_multi_polygon('Shape'),
    }
base_map_district()


class base_map_sub_district(osv.osv):
    _name="base_map.sub_district"
    _columns={
        #'shape':fields.geo_multi_polygon('Shape'),
        'code':fields.char('Code',size=256),
        'name':fields.char('Name',size=256),
        'classification':fields.integer('Classification'),
    }
base_map_sub_district()

class base_map_neighborhood(osv.osv):
    """Contains geographic information about all neighborhoods in the city"""
    _name = 'base_map.neighborhood'
    _order = 'name asc'
    _columns = {
        'code': fields.char('Neighborhood Code',size=30,help='Identify a Neighborhood Code'),
        'name': fields.char('Neighborhood Name', size = 128),
        #'shape':fields.geo_multi_polygon('Geometry'),
    }
base_map_neighborhood()


class base_map_cadastral_zone(osv.osv):
    """
    This layer must be re-factored
    """
    _name="base_map.cadastral_zone"
    _columns={
        'name':fields.char('Name',size=256),
        'code':fields.char('Code',size=128),
        'alt_code':fields.char('Alternative Code',size=128),
        'start_date':fields.date('Create Date'),
        'update_0':fields.date('First Update'),
        'update_1':fields.date('Second Update'),
        'update_2':fields.date('Third Update'),
        'update_3':fields.date('Fourth Update'),
        'zone_code':fields.char('Zone Code', size=128),
        #'shape':fields.geo_multi_polygon('Shape'),
    }
base_map_cadastral_zone()

class base_map_micro_seismicity(osv.osv):
    _name="base_map.micro_seismicity"
    _columns={
        'zone_name':fields.char('Zone Name',size=128),
        'colour':fields.char('Colour', size=128),
        'micr_measure1':fields.float('Measure 1'),
        'micr_measure2':fields.float('Measure 2'),
        #'shape':fields.geo_multi_polygon('Shape'),
    }

class base_map_geological_zone(osv.osv):
    _name="base_map.geological_zone"
    _columns={
        'name':fields.char('Geological Zone',size=256),
        'code':fields.char('Code',size=128),
        #'shape':fields.geo_multi_polygon('Shape'),
    }
base_map_geological_zone()

class base_map_road_section(osv.osv):
    """
    Road section basic data of rodways
    """
    _name="base_map.road_section"
    _columns={
        'rsic':fields.char('Road Section ID Code',size=128),
        'name':fields.char('Road Section Name',size=128),
        'start_edge':fields.char('Start Edge',size=128),
        'end_edge':fields.char('End edge',size=128),
        'road_hierarchy':fields.many2one('base_map.road_hierarchy','Road Hierarchy'),
        #'shape':fields.geo_multi_line('Shape'),
    }
base_map_road_section()

class base_map_road_hierarchy(osv.osv):
    _name="base_map.road_hierarchy"
    _columns={
        'code':fields.integer('Road Hierachy Code',required=True),
        'name':fields.char('Name',size=128,required=True),
    }
base_map_road_hierarchy()
    

