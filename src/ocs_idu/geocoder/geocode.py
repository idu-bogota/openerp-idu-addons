# -*- coding: utf-8 -*-
#######################################################################
#    INSTITUTO DE DESARROLLO URBANO IDU
#    Copyright (C)
#    PLAN DE DESARROLLO 
#    BOGOTA HUMANA 2012-2016
#    Alcalde Mayor: Gustavo Petro Urrego
#    Director IDU: Maria Fernanda Rojas
#    Director STRT: Angel María Fonseca Correa
#    Arquitecto: Cinxgler Mariaca Minda
#    Programador: Andres Ignacio Báez Alba
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
import urllib
import json, math
from pyproj import Proj
from pyproj import transform

def geo_code_address(addr, 
                srid, 
                uri = '',
                zone = 1100100): #Default = Bogota
    """
    Resolve geo - location from address with REST web service technique
    Parameters :
    addr = Address to Geocode
    srid = Spatial Reference System ID. in this format ie "epsg:4326" or "other.extra:900913"
    uri = Geocoder Web Service addr, for idu = http://gi03cc01/ArcGIS/rest/services/GeocodeIDU/GeocodeServer/findAddressCandidates?
    zone = City or town code for example Bogota = 1100100
    REST POST Example http://gi03cc01/ArcGIS/rest/services/GeocodeIDU/GeocodeServer/findAddressCandidates?Street=cra+82+a+6+37&Zone=Bogot%C3%A1+D.C.&outFields=&outSR=&f=html
    """
    try:
        addr = addr.encode('utf8')
        url = "{0}Street={1}&Zone={2}&outSR={3}&f=pjson".format(uri,addr,zone,4326) #Because to Geocoder Bug, firstable we need to get information in Geographic coordinate system 
        jsonstr = urllib.urlopen(url).read()
        vals = json.loads(jsonstr)       
        if (dict.__len__ >= 2):           
            candidates = vals['candidates'] 
            for candidate in candidates :
                location = candidate['location']
                x = location['x']
                y = location['y']
                if (not (math.isnan(x) or math.isnan(y))):
                    if (srid is "epsg:4326"):
                        x1 = x
                        y1 = y
                    else :
                        pGeographic = Proj(init="epsg:4326")
                        pOtherRefSys = Proj(init=srid)
                        x1,y1 = transform(pGeographic,pOtherRefSys,x,y)    
                        #format :   {"type": "Point", "coordinates": [746676.106813609, 5865349.7175855]}            
                        return '{"type": "Point", "coordinates":[%10.12f, %10.12f]}' % (x1,y1)
    except Exception :
        return False
    return False