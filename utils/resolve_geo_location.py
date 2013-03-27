#encoding:UTF-8
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
#    Este script resuelve de forma masiva 
#    la localizacion de las direcciones 
#    para la clase crm_claim y res_partner_address

from geocode import geo_code_address
from optparse import OptionParser
import psycopg2
import sys
import json

ws_url = "http://gi03cc01/ArcGIS/rest/services/GeocodeIDU/GeocodeServer/findAddressCandidates?"
con = None

def geo_code_claim(_database,_user,_password,_host,_port=5432):
    try: 
        con = psycopg2.connect(database=_database, user=_user, password = _password, host=_host) 
        cur = con.cursor()
        cur.execute('select id,claim_address from crm_claim where geo_point is null and claim_address is not null')              
        rows = cur.fetchall()
        for row in rows:
            idx = row[0]
            addr = row [1]
            print '-- ID = {0}, Address = {1}'.format(idx,addr)
            jsonpoint = geo_code_address(addr, srid = "other.extra:900913", uri = ws_url, zone = 1100100 )
            if jsonpoint is not False:
                puntos = json.loads(jsonpoint)["coordinates"]
                x = puntos[0]
                y = puntos[1]
                wkt = "POINT (%10.12f %10.12f)" % (x,y)
                updateQuery = "UPDATE crm_claim SET geo_point = st_geomfromtext('{1}',900913) where id = {0}".format(idx,wkt)
                print updateQuery
                cur.execute(updateQuery)
        con.commit()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        if con:
            con.rollback()
    finally:
        if con:
            con.close()

def geo_code_res_partner_address(_database,_user,_password,_host,_port=5432):
    try: 
        con = psycopg2.connect(database=_database, user=_user, password = _password, host=_host) 
        cur = con.cursor()
        cur.execute('select id,street from res_partner_address where geo_point is null and street is not null')              
        rows = cur.fetchall()
        for row in rows:            
            idx = row[0]
            addr = row [1]
            print "-- Id: {0} , Address: {1}".format(idx,addr)
            jsonpoint = geo_code_address(addr, srid = "other.extra:900913", uri = ws_url, zone = 1100100 )
            if jsonpoint is not False:
                puntos = json.loads(jsonpoint)["coordinates"]
                x = puntos[0]
                y = puntos[1]
                wkt = "POINT (%10.12f %10.12f)" % (x,y)
                updateQuery = "UPDATE res_partner_address SET geo_point = st_geomfromtext('{1}',900913) where id = {0}".format(idx,wkt)
                cur.execute(updateQuery)
                print updateQuery
        con.commit()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        if con:
            con.rollback()
    finally:
        if con:
            con.close()

def main():
    usage = "Resolve geo location in some geo_point feature class\nCall directly to database\nusage: %prog [options]"
    parser = OptionParser(usage)
    parser.add_option("-H", "--host", dest="host", help="OpenERP server host", default="localhost:5432")
    parser.add_option("-n", "--db_name", dest="db_name", help="Database name")
    parser.add_option("-u", "--db_user", dest="db_user", help="Database User Name")
    parser.add_option("-p", "--db_password", dest="db_password", help="Database password")
    parser.add_option("-c", "--classes", dest="classes", help="Comma separated clases ej: crm_claim,res_partner_address")
    
    (options, args) = parser.parse_args()
    #pprint.pprint(options);
    if not options.host:
        parser.error('host not given')
    if not options.db_name:
        parser.error('db_name not given')
    if not options.db_password:
        parser.error('db_password not given')
    if not options.classes:
        parser.error('classes not given')
    if not options.db_user:
        parser.error('Database user not given')
    
    tables = options.classes.split(',')
    conndata = options.host.split(':')
    xhost = conndata[0]
    xport = conndata[1]
    for table in tables :
        print "--Parameters : Database name = {0}, User = {1}, Host = {2}, Port = {3}".format(options.db_name,options.db_user,xhost,xport)
        print "--Table : {0}".format(table)
        if (table == "crm_claim"):
            print "--Start Geocoding"
            geo_code_claim(options.db_name,options.db_user,options.db_password,xhost,xport)
        if (table == "res_partner_address"):
            print "--Start Geocoding"
            geo_code_res_partner_address(options.db_name,options.db_user,options.db_password,xhost,xport)



if __name__ == '__main__':
    main()
    sys.exit(1)