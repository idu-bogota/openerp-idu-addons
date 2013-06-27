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
from osv import fields,osv
from base_geoengine import geo_model

class urban_pavement_evaluator(osv.osv):
    """
        Structure Type Main Classification
    """
    _name="urban_pavement.evaluator"
    _columns={
        'name':fields.char('Name :',size=256),
        'identification':fields.char('Identification :',size=20),
    }

urban_pavement_evaluator()

class urban_pavement_evaluation(geo_model.GeoModel):
    """
        Structure Type Main Classification
    """
    _name="urban_pavement.evaluation"
    _columns={
        'civ': fields.char('CIV',size = 20),
        'pci': fields.integer('PCI'),
        'eval_date': fields.date('Date Evaluation'),
        'evaluator_id': fields.many2one('urban_pavement.evaluator',"Evaluator",required = True),
        'photo':fields.binary('Photo'),
        'component_id':fields.one2many('urban_pavement.component','component_id',required = True),
        'shape':fields.geo_multi_polygon('Shape'),
    }
   
urban_pavement_evaluation()

class urban_pavement_component(osv.osv):
    """
        Structure Type Main Classification
    """
    _name="urban_pavement.component"
    _columns={
        'damage':fields.float('Damage :'),
        'extension':fields.float('Extension :'),
        'severity':fields.integer('Severity :'),
        'component_id':fields.integer('component_id'),
    }
 
urban_pavement_component()



