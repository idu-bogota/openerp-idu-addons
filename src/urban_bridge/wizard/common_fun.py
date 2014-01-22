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
#    Creado Por: Andres Ignacio Baez Alba
#
#
##############################################################################
from shapely.wkt import dumps, loads 
###
# Transform input wkt geometry in web mercator (900913) to user defined spatial_ref_sys 
###
def transform_from_web_mercator_to_source_coordinates(cr,input_wkt,spatial_ref_sys):
        try:
            ret_val = None
            if (input_wkt is not False):
                query = """
                    SELECT ST_ASTEXT(ST_TRANSFORM(ST_GEOMFROMTEXT(%s,
                    900913),%s))
                """
                cr.execute(query,(input_wkt,spatial_ref_sys))
                for row in cr.fetchall():
                    if row[0] is not False:
                        ret_val = row[0]
            return ret_val
        except Exception as e:
            raise e

###
# Transform input wkt geometry in user defined spatial ref sys to web mercator (900913) 
# by database 
###
def transform_source_geometry_to_web_mercator(cr,input_wkt,spatial_ref_sys):
        if input_wkt == False:
            return False
        else:
            try:
                shape = dumps(loads(input_wkt))
                query = """
                SELECT ST_ASTEXT(ST_TRANSFORM(ST_GEOMFROMTEXT(%s,
                %s),900913))
                """
                cr.execute(query,(shape,spatial_ref_sys))
                for row in cr.fetchall():
                    if (row[0] is not False):
                        return dumps(loads(row[0]))
                return False
            except Exception as e:
                raise e

