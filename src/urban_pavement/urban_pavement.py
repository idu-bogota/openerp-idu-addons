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

class urban_pavement_severity(osv.osv):
    """
        Structure Type Main severity
    """
    _name="urban_pavement.severity"
    _columns={
        'code':fields.integer('Code'),
        'name':fields.char('Name',size=200),
    }

class urban_pavement_display(osv.osv):
    """
        Structure Type Main Classification
    """
    _name="urban_pavement.display"
    _columns={
        'code':fields.integer('Code'),
        'name':fields.char('Name',size=200),
    }

class urban_pavement_damage(osv.osv):
    """
        Structure Type Main Classification
    """
    _name="urban_pavement.damage"
    _columns={
        'code':fields.integer('Code'),
        'name':fields.char('Name',size=200),
    }


class urban_pavement_evaluator(osv.osv):
    """
        Structure Type Main Classification
    """
    _name="urban_pavement.evaluator"
    _columns={
        'name':fields.char('Name',size=256),
        'identification':fields.char('Identification',size=20),
    }

urban_pavement_evaluator()



class urban_pavement_evaluation(geo_model.GeoModel):

    def search_civ(self, cr, uid, ids,civ):
        print "Hello World" 

    def calculate_pci(self, cr, uid, ids,pci):
        v={}
        evaluations = self.browse(cr,uid,ids)
        for evaluation in evaluations:
            pci = pci+1
            components = evaluation.component_id
            for component in components:
                damage_id = component.damage_id
                extension = component.extension_id
            v['pci'] = pci
        res = {'value':v}
        return res

    _name="urban_pavement.evaluation"
    _columns={
        'civ': fields.char('CIV',size = 20),
        'pci': fields.integer('PCI'),
        'unit_display_id': fields.many2one('urban_pavement.display',"Display",required = True),
        'number_slabs': fields.integer('Number Slabs'),
        'eval_date': fields.date('Date Evaluation'),
        'evaluator_id': fields.many2one('urban_pavement.evaluator',"Evaluator",required = True),
        'photo':fields.binary('Photo'),
        'component_id':fields.one2many('urban_pavement.component','component_id',required = True),
        'shape':fields.function('Shape'),
    }
    
   
urban_pavement_evaluation()

class urban_pavement_component(osv.osv):
    """
        Structure Type Main Classification
    """
    _name="urban_pavement.component"
    _columns={
        'damage_id':fields.many2one('urban_pavement.damage',"Damage",required = True),
        'extension':fields.integer('Extension',required = True),
        'severity_id':fields.many2one('urban_pavement.severity',"Severity",required = True),
        'component_id':fields.integer('component_id'),
    }
 
urban_pavement_component()



