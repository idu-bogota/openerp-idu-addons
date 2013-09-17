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
from shapely.geometry import asShape
from shapely.geometry import MultiPolygon
from datetime import datetime

class urban_bridge_bridge(geo_model.GeoModel):
    """ 
    Bridge Infraestructure Data
    """

    def _get_district(self,cr,uid,ids,fieldname,arg,context=None):
        res = {}
        for bridge in self.browse(cr, uid, ids, context = context):
            geom = bridge.shape
            districts=""
            if geom != False:
                query = "SELECT name FROM base_map_district WHERE st_intersects(shape,st_geomfromtext('{0}',4326)) = true".format(geom)
                cr.execute(query)
                for row in cr.fetchall():
                    districts = row[0] + ","+districts
            res[bridge.id] = districts
        return res
    
    def _get_sub_district(self,cr,uid,ids,fieldname,arg,context=None):
        res = {}
        for bridge in self.browse(cr, uid, ids, context = context):
            geom = bridge.shape
            sub_districts=""
            if geom != False:
                query = "SELECT name FROM base_map_sub_district WHERE st_intersects(shape,st_geomfromtext('{0}',4326)) = true".format(geom)
                cr.execute(query)
                for row in cr.fetchall():
                    sub_districts = row[0] + ","+sub_districts
            res[bridge.id] = sub_districts
        return res
        
    def _get_cadastral_zone(self,cr,uid,ids,fieldname,arg,context=None):
        res = {}
        for bridge in self.browse(cr, uid, ids, context = context):
            cad_zone=""
            geom = bridge.shape
            if geom != False:
                query = "SELECT name FROM base_map_cadastral_zone WHERE st_intersects(shape,st_geomfromtext('{0}',4326)) = true".format(geom)
                cr.execute(query)
                for row in cr.fetchall():
                    cad_zone = row[0] + ","+cad_zone
            res[bridge.id] = cad_zone
        return res
    
    def _get_micro_seismicity(self,cr,uid,ids,fieldname,arg,context=None):
        res = {}
        for bridge in self.browse(cr, uid, ids, context = context):
            micr_seism=""
            geom = bridge.shape
            if geom !=False:
                query = "SELECT zone_name,micr_measure1 FROM base_map_micro_seismicity WHERE st_intersects(shape,st_geomfromtext('{0}',4326)) = true".format(geom)
                cr.execute(query)
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
            select st_transform(shape,96873) as pmagna from urban_bridge_bridge where id = %s
            ) as t1
            """
            cr.execute(query,str(bridge_id))
            area=0.0
            for row in cr.fetchall():
                #Crear un diccionario para almacenar areas por
                if row[0]!=None:
                    area = float(row[0])
                res[bridge.id] = area
        return res
    
    def _get_perimeter(self,cr,uid,ids,fieldname,arg,context=None):
        res = {}
        for bridge in self.browse(cr, uid, ids, context = context):
            bridge_id = bridge.id
            query = """
            select st_perimeter(pmagna) as area from (
            select st_transform(shape,96873) as pmagna from urban_bridge_bridge where id = %s
            ) as t1
            """
            cr.execute(query,str(bridge_id))
            perimeter = 0.0
            for row in cr.fetchall():
                #Crear un diccionario para almacenar areas por
                if row[0]!=None:
                    perimeter = float(row[0])
                res[bridge.id] = perimeter
        return res
    
    def web_service_save (self,cr,uid,data,context=None):
        #1.Check Geography Type-- and translate to multipoly
        #Geography come in geojsCheckliston
        try :
            jgeometry = data["shape"]
            geography=asShape(jgeometry)
            shape=""
            if geography.geom_type =="Polygon":
                mpoly=MultiPolygon([geography])
                shape=mpoly.wkt
            else :
                shape=geography.wkt
            data["shape"] = shape
            #Check date
            if (data.has_key("construction_date")):
                construction_date = datetime.strptime(data["construction_date"],"%Y-%m-%d %H:%M:%S")
                data["contruction_date"]=str(construction_date.date())
        except Exception as e:
            print e
        #2. Read Category Type
        if (data.has_key("structure_type")):
            structure_type_ids = self.pool.get("urban_bridge.structure_type").search(cr,uid,[('code','=',data["structure_type"])])
        if structure_type_ids.__len__() == 0:
            return {'result':'Error, Structure Type Code Not defined!'}
        else :
            data["structure_type"]=structure_type_ids[0]
        #3. Check if bridge_code Exist if does not exist then create, if exist update from code --
        search_result_ids=[]
        if data.has_key("code"):
            search_result_ids = self.search(cr,uid,[('code','=',data["code"])])
        try :
            if search_result_ids.__len__() == 0:
                #Create
                id_bridge = self.create(cr,uid,data)
                return {"result":"Insertion success ","id":id_bridge}
            else :
                #If Update, only update Geography
                self.write(cr,uid,search_result_ids[0],{"shape":data["shape"]})
                return {"result":"Geometry Update success! attributes does not modified!","id":search_result_ids[0]}
        except Exception as e:
            print e 
            return {"result":"Save Failed!"}
    _name="urban_bridge.bridge"
    _columns = {
        'shape':fields.geo_multi_polygon('Shape',help="Shape",srid=4326),
        'code':fields.char('Bridge Code',size=128,help="Bridge Code"),
        'name':fields.char('Identifier',size=128,help ="Identifier"),
        'classification':fields.selection([('PPC','PPC'),('PPE','PPE'),('PVC','PVC'),('PVE','PVE')],'Bridge Classification'),
        'structure_type':fields.many2one('urban_bridge.structure_type','Bridge Type',required=True),
        'address':fields.char('Bridge Address',size=256),
        'last_address':fields.char('Last Address',size=256),
        'construction_date':fields.date('Construction Date'),
        'length':fields.float('Total Length'),
        'width':fields.float('Total Width'),
        'superstructure_area':fields.float('Bridge Super-Structure Area'),
        'vertical_gauge':fields.float('Vertical Gauge'),
        'horizontal_gauge':fields.float('Horizontal Gauge'),
        'design_load_capacity':fields.float('Design Load Capacity'),
        'level':fields.selection([('-2','-2'),('-1','-1'),('0','0'),('1','1'),('2','2'),('3','3'),('4','4')],'Bridge Level'),
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
        'elements':fields.one2many('urban_bridge.structure_element','bridge_id','Elements'),
        'survey_id':fields.one2many('urban_bridge.inspection_survey','bridge_id','Inspection Survey')
    }
    
    _sql_contraints = [
        ('cc_bridge_code_unique','unique(code)','¡Bridge Code must be unique!'),
    ]


urban_bridge_bridge()

class urban_bridge_structure_type(osv.osv):
    """
        Structure Type Main Classification
    """
    _name="urban_bridge.structure_type"
    _columns={
        'code':fields.integer('Code','Code - Value equivalent Domain'),
        'name':fields.char('Name',size=256,required=True),
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
        'sub_classification':fields.selection([('SS','Super Structure'),('IS','Infrastructure'),('FP','Foundation'),('SE','Structure Element'),('FE','Functional Elements'),('IN','Instrumentation')],'SubClassification',required=True),
        'attributes':fields.one2many('urban_bridge.structure_element_attribute','element_type_id'),
        'alias':fields.char('Alias',size=3,required=True)
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
        'data_type':fields.selection([('integer','Integer'),('text','Text'),('datetime',' Date Time'),('date','Date'),('float','Float'),('boolean','Boolean'),('char','Char'),('selection','Selection'),('binary','Photo'),('geo_point','Geographic Point'),('geo_line','Geographic Line'),('geo_polygon','Geographic Polygon')],'Data Type',required=True),
        'element_type_id':fields.many2one('urban_bridge.structure_element_type','Element ID'),
        'selection_text':fields.char('Selection',size=1024,help='If Data type : selection then selection text contain the dictionary'),
    }
    _defaults={
        'is_required': lambda *args: True,
        'is_enabled': lambda *args: True,
    }
    
urban_bridge_structure_element_attribute()
class urban_bridge_structure_element_value(geo_model.GeoModel):
    """
    EAV Value Definition for elements of Structure
    """
    _name="urban_bridge.structure_element_value"
    _columns={
        'element_id':fields.many2one('urban_bridge.structure_element','Element',ondelete="cascade"),
        'element_attribute_id':fields.many2one('urban_bridge.structure_element_attribute','Attribute'),
        'value_integer':fields.integer('Integer'),
        'value_char':fields.char('Char',size=256),
        'value_date':fields.date('Date'),
        'value_datetime':fields.datetime('Date Time'),
        'value_text':fields.text('Text'),
        'value_float':fields.float('Float'),
        'value_bool':fields.boolean('Boolean'),
        'value_binary':fields.binary('Photo'),
        'value_selection':fields.char('Selection',size=10),
        'value_point':fields.geo_point('Shape Point',srid=4326),
        'value_line':fields.geo_line('Shape Line',srid=4326),
        'value_polygon':fields.geo_polygon('Shape Line',srid=4326),
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
        'values':fields.one2many('urban_bridge.structure_element_value','element_id','Values',ondelete="cascade"),
        'bridge_id':fields.many2one('urban_bridge.bridge','Bridge',ondelete="cascade"),
        }
urban_bridge_structure_element()

############################### Inspection Use Case Implementation #################################

class urban_bridge_inspection_survey(osv.osv):
    """
    Survey Inspections
    """
    _rec_name = 'methodology_id'
    _name = "urban_bridge.inspection_survey"
    _order = 'inspection_date desc'
    _columns = {
        'inspection_date':fields.date('Inspection Date'),
        'score':fields.float('Inspection '),
        'bridge_id':fields.float('Bridge'),
        'methodology_id':fields.many2one('urban_bridge.methodology','Methodology'),
        'state':fields.selection([('draft', 'New'),('open', 'In Progress'),('cancel', 'Cancelled'),('done', 'Closed')],'State'),
        'values':fields.one2many('urban_bridge.inspection_value','inspection_id','Values',ondelete="cascade"),
        'comment':fields.text('Comment'),
    }

urban_bridge_inspection_survey()

class urban_bridge_methodology(osv.osv):
    """
    Define the Inspection Methodology to apply survey's to the bridges and its elements 
    """
    _name="urban_bridge.methodology"
    _columns={
        'name':fields.char('Methodology Name',size=128,required=True),
        'expression':fields.text('Expression'),
        'entity_id':fields.one2many('urban_bridge.inspection_entity','methodology_id','Inspection Issues'),
    }

class urban_bridge_inspection_entity(osv.osv):
    """
    Inspection Entity Definition 
    """
    _name="urban_bridge.inspection_entity"
    _columns = {
        'name':fields.char('Name',size=128,required=True),
        'methodology_id':fields.many2one('urban_bridge.methodology','Methodology'),
        'expression':fields.text('Expression'),
        'attribute_id':fields.one2many('urban_bridge.inspection_attribute','inspection_entity_id','Attributes'),
        'alias':fields.char('Alias:',size=1,required=True,help="This field is to identify the field at methodology expression"),
    }

class urban_bridge_inspection_attribute(osv.osv):
    """
    EAV for Inspection attribute definition
    """
    _name ="urban_bridge.inspection_attribute"
    _columns = {
        'name':fields.char('Name',size=128),
        'data_type':fields.selection([('integer','Integer'),('text','Text'),('datetime',' Date Time'),('date','Date'),('float','Float'),('boolean','Boolean'),('char','Char'),('selection','Selection')],'Data Type',required=True),
        'selection_text':fields.char('Selection',size=1024,help='If Data type : selection then selection text contain the dictionary'),
        'is_required':fields.boolean('Is Required'),
        'is_enabled':fields.boolean('Is Enabled'),
        'is_general':fields.boolean('This field applies to all the Bridge in general?'),
        'alias':fields.char('Alias:',size=1,required=True,help="This field is to identify the field at methodology expression"),
        'inspection_entity_id':fields.many2one('urban_bridge.inspection_entity','Entity'),
        'structure_element_type':fields.many2many('urban_bridge.structure_element_type','urban_bridge_struct_elem_type_insp_entity_rel','inspection_attribute_id','element_type_id','Element to Inspect:')
    }
    _defaults={
        'is_required': lambda *args: True,
        'is_enabled': lambda *args: True,
    }

class urban_bridge_inspection_value(osv.osv):
    """
    EAV for inspection value measured or calculated
    """
    _name = "urban_bridge.inspection_value"
    _columns = {
        'value_photo':fields.binary('Photo'),
        'value_integer':fields.integer('Integer'),
        'value_char':fields.char('Char',size=256),
        'value_date':fields.date('Date'),
        'value_datetime':fields.datetime('Date Time'),
        'value_text':fields.text('Text'),
        'value_float':fields.float('Float'),
        'value_bool':fields.boolean('Boolean'),
        'value_selection':fields.char('Selection',size=10),
        'bridge_id':fields.many2one('urban_bridge.bridge','Bridge'),
        'element_id':fields.many2one('urban_bridge.structure_element','Structure Element'),
        'inspection_id':fields.many2one('urban_bridge.inspection_survey','Inspection',ondelete="cascade"),
        'inspect_attribute_id':fields.many2one('urban_bridge.inspection_attribute','Inspection Attribute'),
    }
