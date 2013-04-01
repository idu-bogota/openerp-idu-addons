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
import math
from pyproj import Proj
from pyproj import transform
import re, json
import logging

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
    #return '{"type":"Point","coordinates":[-8246435.141098299995065,512561.201248599973042]}';
    try:
        addr = addr.encode('utf8')
        url = "{0}Street={1}&Zone={2}&outSR={3}&f=pjson".format(uri,addr,zone,4326) #Because to Geocoder Bug, first we need to get information in Geographic coordinate system 
        jsonstr = urllib.urlopen(url).read()
        vals = json.loads(jsonstr)
        if (len(vals) >= 2):
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
    except Exception as e:
        logging.getLogger(__name__).error(str(e))
        return False
    return False

def is_bogota_address_valid(address):
    """ This function checks if the parameter fits Bogotá D.C. address schema.

    >>> print is_bogota_address_valid('KR 102 10 30')
    True
    >>> print is_bogota_address_valid('KR 102 10 30 INT 2 AP 1023')
    True
    >>> print is_bogota_address_valid('KR 102 10 30 INT 2')
    True
    >>> print is_bogota_address_valid('KR 102 10 30 AP 1123')
    True
    >>> print is_bogota_address_valid('KR 102 A 10 A 30')
    True
    >>> print is_bogota_address_valid('KR 102 A 10 A 30 INT 3 AP 12')
    True
    >>> print is_bogota_address_valid('KR 102 A 10 A BIS 30')
    True
    >>> print is_bogota_address_valid('KR 102 A 10 A BIS Z 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS 10 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS 10 30 AP 12')
    True
    >>> print is_bogota_address_valid('KR 102 BIS 10 A 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS 10 BIS 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS 10 BIS Z 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS 10 A BIS 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS 10 A BIS Z 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS 10 A BIS Z 30 INT 3 LOC 4')
    True
    >>> print is_bogota_address_valid('KR 102 BIS A 10 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS A 10 30 E')
    True
    >>> print is_bogota_address_valid('KR 102 BIS A 10 A 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS A 10 A BIS 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS A 10 A BIS A 30')
    True
    >>> print is_bogota_address_valid('KR 102 BIS A 10 A BIS A 30 LOC 5')
    True
    >>> print is_bogota_address_valid('KR 102 BIS A 10 BIS Z 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS 10 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS 10 A 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS 10 A BIS 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS 10 A BIS A 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS 10 BIS Z 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS Z 10 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS Z 10 30 SE')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS Z 10 A 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS Z 10 A BIS 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS Z 10 A BIS A 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS Z 10 BIS Z 30')
    True
    >>> print is_bogota_address_valid('KR 102 A BIS Z 10 BIS Z 30 N')
    True
    >>> print is_bogota_address_valid('TV 34 F 45 B BIS Z 32 MZ 32 INT 5 TO 23 AP 123 S')
    True
    >>> print is_bogota_address_valid('CL 22 A 52 07 TO C AP 1102')
    True
    """
    st_type = '(CL|AC|DG|KR|AK|TV|CA|CT|PS)'
    st_number = '[0-9]+'
    st_suffix = '(\s[A-Z])?((\sBIS)|(\sBIS\s[A-Z]))?'
    st_horizontal = '(\s(AP|OF|CON|PEN|LOC|DEP|GJ)\s[0-9]+)?'
    st_interior = '(\s((INT|BQ|TO|CA)\s[0-9A-Z]+))?'
    st_manzana = '(\s((MZ|LO|ET)\s[A-Z0-9]+))?'
    st_sector = '(\s(N|E|S|O|NE|SE|SO|NO))?'
    regex = "^{0}\s{1}{2}\s{1}{2}\s{1}{6}{6}{3}{3}{4}{5}$".format(st_type, st_number, st_suffix, st_interior, st_horizontal, st_sector, st_manzana);
    #print regex
    if re.match(regex, address) != None:
        return True
    else:
        return False


if __name__ == "__main__":
    import doctest
    doctest.testmod()
