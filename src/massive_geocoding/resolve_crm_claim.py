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
#    para la clase crm_claim

from geocode import geo_CodeAddress
import psycopg2
import sys
import json


ws_url = "http://gi03cc01/ArcGIS/rest/services/GeocodeIDU/GeocodeServer/findAddressCandidates?"
con = None

def GeoCode(_database,_user,_password,_host):
    try: 
        con = psycopg2.connect(database=_database, user=_user, password = _password, host=_host) 
        cur = con.cursor()
        cur.execute('select id,claim_address from crm_claim where geo_point is null and claim_address is not null')              
        rows = cur.fetchall()
        for row in rows:
            idx = row[0]
            addr = row [1]
            jsonpoint = geo_CodeAddress(addr, srid = "other.extra:900913", uri = ws_url, zone = 1100100 )
            if jsonpoint is not False:
                puntos = json.loads(jsonpoint)["coordinates"]
                x = puntos[0]
                y = puntos[1]
                wkt = "POINT (%10.12f %10.12f)" % (x,y)
                updateQuery = "UPDATE crm_claim SET geo_point = st_geomfromtext('{1}',900913) where id = {0}".format(idx,wkt)
                cur.execute(updateQuery)
                print 'Actualizado ID {0}, Addr {1}'.format(idx,addr) 
        con.commit()
    except psycopg2.DatabaseError, e:
        print 'Error %s' % e
        if con:
            con.rollback()
    finally:
        if con:
            con.close()

#Ejecucion del probrama

x_dataBase = raw_input('Ingrese el nombre de la base de Datos de OpenErp:')
x_user = raw_input('Ingrese el usuario de conexión a la base de datos:')
x_password = raw_input('Ingrese el password de conexión a dicha base de datos')
x_host = raw_input('Ingrese el nombre de host o direccion IP')
GeoCode(x_dataBase,x_user,x_password,x_host)
sys.exit(1)
