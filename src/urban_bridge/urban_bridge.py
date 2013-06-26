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
    v={}

        
    def _get_district(self,cr,uid,ids,fieldname,arg,context=None):
        res = {}
        for bridge in self.browse(cr, uid, ids, context = context):
            geom = bridge.shape
            query = "SELECT name FROM base_map_district WHERE st_intersects(shape,st_geomfromtext('{0}',900913)) = true".format(geom)
            cr.execute(query)
            districts=""
            for row in cr.fetchall():
                districts = row[0] + ","+districts
            res[bridge.id] = districts
        return res
    
    def _get_sub_district(self,cr,uid,ids,fieldname,arg,context=None):
        res = {}
        for bridge in self.browse(cr, uid, ids, context = context):
            geom = bridge.shape
            query = "SELECT name FROM base_map_sub_district WHERE st_intersects(shape,st_geomfromtext('{0}',900913)) = true".format(geom)
            cr.execute(query)
            sub_districts=""
            for row in cr.fetchall():
                sub_districts = row[0] + ","+sub_districts
            res[bridge.id] = sub_districts
        return res
        
    def _get_cadastral_zone(self,cr,uid,ids,fieldname,arg,context=None):
        res = {}
        for bridge in self.browse(cr, uid, ids, context = context):
            geom = bridge.shape
            query = "SELECT name FROM base_map_cadastral_zone WHERE st_intersects(shape,st_geomfromtext('{0}',900913)) = true".format(geom)
            cr.execute(query)
            cad_zone=""
            for row in cr.fetchall():
                cad_zone = row[0] + ","+cad_zone
            res[bridge.id] = cad_zone
        return res
    
    def _get_micro_seismicity(self,cr,uid,ids,fieldname,arg,context=None):
        res = {}
        for bridge in self.browse(cr, uid, ids, context = context):
            geom = bridge.shape
            query = "SELECT zone_name,micr_measure1 FROM base_map_micro_seismicity WHERE st_intersects(shape,st_geomfromtext('{0}',900913)) = true".format(geom)
            cr.execute(query)
            micr_seism=""
            for row in cr.fetchall():
                micr_seism = row[0]+"-"+str(row[1])+","+micr_seism
            res[bridge.id] = micr_seism
        return res

    def _get_area(self,cr,uid,ids,fieldname,arg,context=None):
        res = {}
        for bridge in self.browse(cr, uid, ids, context = context):
            bridge_id = bridge.id
            query = """
            select st_area(pmagna) as area from (
            select st_transform(shape,96873) as pmagna from urban_bridge_bridge where id = {0}
            ) as t1
            """.format(bridge_id)
            cr.execute(query)
            area=0.0
            for row in cr.fetchall():
                #Crear un diccionario para almacenar areas por
                area = float(row[0])
                res[bridge.id] = area
        return res
    
    def _get_perimeter(self,cr,uid,ids,fieldname,arg,context=None):
        res = {}
        for bridge in self.browse(cr, uid, ids, context = context):
            bridge_id = bridge.id
            query = """
            select st_perimeter(pmagna) as area from (
            select st_transform(shape,96873) as pmagna from urban_bridge_bridge where id = {0}
            ) as t1
            """.format(bridge_id)
            cr.execute(query)
            area=0.0
            for row in cr.fetchall():
                #Crear un diccionario para almacenar areas por
                perimeter = float(row[0])
                res[bridge.id] = perimeter
        return res
        

    _name="urban_bridge.bridge"
    _columns = {
        'shape':fields.geo_multi_polygon('Shape'),
        'code':fields.char('Bridge Code: ',size=128),
        'name':fields.char('Identifier: ',size=128),
        'category':fields.selection([('PPC','PPC'),('PPE','PPE'),('PVC','PVC'),('PVE','PVE')],'Bridge Classification'),
        'structure_type':fields.many2one('urban_bridge.structure_type','Bridge Type',required=True),
        'address':fields.char('Bridge Address',size=256),
        'last_address':fields.char('Last Address',size=256),
        'construction_date':fields.datetime('Construction Date'),
        'length':fields.float('Total Length'),
        'width':fields.float('Total Width'),
        'superstructure_area':fields.float('Bridge SuperStructure Area:'),
        'vertical_gauge':fields.float('Vertical Gauge'),
        'horizontal_gauge':fields.float('Horizontal Gauge'),
        'design_load_capacity':fields.float('Design Load Capacity'),
        'structure_material':fields.many2one('urban_bridge.structure_material','Structure Materials'),
        'design_load_code':fields.many2one('urban_bridge.design_load_code','Design Load Code'),
        'photo':fields.binary('Photo'),
        'geological_zone':fields.many2one('base_map.geological_zone','Geological Zone'),
        'district':fields.function(_get_district,string='Districts',method=True,type="char"),
        'sub_district':fields.function(_get_sub_district,string='Sub Districts',method=True,type="char"),
        'cadastral_zone':fields.function(_get_cadastral_zone,string="Cadastral Zone",method=True,type="char"),
        'micro_seismicity':fields.function(_get_micro_seismicity,string="Micro-Seismicity",method=True,type="char"),
        'calc_area':fields.function(_get_area,string="Calculated Area",method=True,type="float"),
        'calc_perimeter':fields.function(_get_perimeter,string="Calculated Perimeter",method=True,type="float"),
        'elements':fields.one2many('urban_bridge.structure_element','bridge_id','Element'),
    }
urban_bridge_bridge()

class urban_bridge_structure_type(osv.osv):
    """
        Structure Type Main Classification
    """
    _name="urban_bridge.structure_type"
    _columns={
        'code':fields.integer('Code','Code - Value equivalent Domain'),
        'name':fields.char('Name :',size=256,required=True),
        'description':fields.text('Description'),
        'photo':fields.binary('Photo'),
    }
urban_bridge_structure_type()

class urban_bridge_desgin_load_code(osv.osv):
    """
    Design Load Code
    """
    _name="urban_bridge.design_load_code"
    _columns={
        'code':fields.integer('Code','Unique Identification Code'),
        'name':fields.char('Name',size=128),
    }
urban_bridge_desgin_load_code()

class urban_bridge_structure_material(osv.osv):
    """
    Structure Materials
    """
    _name="urban_bridge.structure_material"
    _columns={
        'code':fields.integer('Code','Material Structure Code'),
        'name':fields.char('Name',help='Material Name',size=256),
    }
urban_bridge_structure_material()

class urban_bridge_structure_element_type(osv.osv):
    """
    EAV Entity Definition for Elements of Bridge Structure
    """
    _name="urban_bridge.structure_element_type"
    _columns={
        'name':fields.char('Name',size=256,required=True),
        'classification':fields.selection([('M','Main Element'),('S','Secondary Element'),('A','Accessory Element')],'Main Classification', required=True),
        'sub_classification':fields.selection([('SS','Super Structure'),('IS','Infrastructure'),('FP','Foundation'),('SE','Structure Element'),('FE','Functional Elements')],'SubClassification',required=True),
        'attributes':fields.one2many('urban_bridge.structure_element_attribute','element_type_id')
    }
urban_bridge_structure_element_type()
class urban_bridge_structure_element_attribute(osv.osv):
    """
    EAV Attribute Definition for Elements of Structure
    """
    _name="urban_bridge.structure_element_attribute"
    _columns={
        'id':fields.integer('Id'),
        'name':fields.char('Name',size=256,required=True),
        'is_required':fields.boolean('Is Required'),
        'is_enabled':fields.boolean('Is Enabled'),
        'data_type':fields.selection([('integer','Integer'),('text','Text'),('datetime',' Date Time'),('date','Date'),('float','Float'),('boolean','Boolean'),('char','Char'),('selection','Selection')],'Data Type',required=True),
        'element_type_id':fields.integer('Element ID'),
        'selection_text':fields.char('Selection',size=1024),
    }
    _defaults={
        'is_required': lambda *args: True,
        'is_enabled': lambda *args: True,
    }
    
urban_bridge_structure_element_attribute()
class urban_bridge_structure_element_value(osv.osv):
    """
    EAV Value Definition for elements of Structure
    """
    _name="urban_bridge.structure_element_value"
    _columns={
        'element_id':fields.integer('Element'),
        'element_attribute_id':fields.many2one('urban_bridge.structure_element_attribute','Attribute'),
        'value_integer':fields.integer('Integer'),
        'value_char':fields.char('Char',size=256),
        'value_date':fields.date('Date'),
        'value_datetime':fields.datetime('Date Time'),
        'value_text':fields.text('Text'),
        'value_float':fields.float('Float'),
        'value_bool':fields.boolean('Boolean'),
        'value_selection':fields.char('Selection',size=10),
        }
urban_bridge_structure_element_value()

class urban_bridge_structure_element(osv.osv):
    """
    EAV Structure Element
    
    """
    _name="urban_bridge.structure_element"
    _order='element_type_id'
    _columns={
        'name':fields.char('Name',size=128,required=True),
        'element_type_id':fields.many2one('urban_bridge.structure_element_type','Element Type',required=True),
        'values':fields.one2many('urban_bridge.structure_element_value','element_id','Values'),
        'bridge_id':fields.integer('Bridge')
        }
urban_bridge_structure_element()